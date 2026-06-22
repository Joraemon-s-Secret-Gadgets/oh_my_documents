# Scoring Tool 실행 명세

> 문서 버전: v0.4
> 문서 상태: Draft / Scoring Tool 세부
> 작성일: 2026-06-13
> 기준 문서: `candidate_evidence_agent.md`, `candidate_evidence_runtime_retrieval.md`
>
> **[PRD 반영 v0.1 — 대화형 빌더]** scoring 가중치를 **context별**로 둔다 — 도시 선정(테마 커버리지 중심) vs 반경 스텝(거리 중심). 기존 거리 페널티를 반경 모드에서 가중. 상세: `../98_prd/interactive_builder_prd.md`.

## 1. 문서 목적

본 문서는 Candidate Evidence 후보 점수화를 담당하는 `ScoringTool`의 실행 세부를 정리한다.

`ScoringTool`은 AWS를 호출하지 않는 순수 Python deterministic scoring engine이다. 이미 검색된 후보의 vector distance와 metadata를 사용해 두 단계 점수를 만든다.

1. `score_place`: 개별 관광지 후보의 점수 계산
2. `score_city`: 도시 후보의 최종 ranking 점수와 breakdown 계산

검색, detail 조회, primary quota 선택은 Scoring Tool의 책임이 아니다.

## 2. 구성 책임

| 구성 요소 | 역할 |
| --- | --- |
| Scoring Tool | `ScoringTool`, `ScoreBreakdown`, `haversine_distance` 책임 |
| Execution orchestration | Baseline/Ours에서 score 호출 순서와 congestion signal 계산 |
| Candidate selection helper | score 이후 primary quota 선택. Scoring Tool 외부 단계 |

## 3. 책임 범위

| 구분 | 내용 |
| --- | --- |
| 책임 | place score 계산, city score 계산, score breakdown 생성 |
| 입력 | 검색된 관광지 후보 dict, searchable place themes, 후보 기준 좌표, 사용자 위치, 혼잡도 index |
| 출력 | `place_score`, `city_score`, `ScoreBreakdown` |
| AWS 호출 | 없음 |
| 사용 데이터 | vector distance, soft distance, metadata, 계산된 congestion signal |

담당하지 않는 범위:

| 비범위 | 담당 |
| --- | --- |
| S3 Vector 검색 | Destination Search Tool |
| 최종 item detail enrichment | DynamoLookupTool |
| 월별 방문자 통계 조회 | 실행 orchestration |
| primary theme quota | Candidate selection helper |
| 후보 수 sufficiency fallback | 실행 orchestration |
| 일정 생성 | Planner Agent |
| restaurant 후보 조회·점수화 | Planner/Backend의 외부 맛집 검색 링크로 대체 |

## 4. 주요 타입

### 4.1 `ScoreBreakdown`

도시 점수 구성 요소를 audit과 평가 리포트에 남기기 위한 dict다.

```python
class ScoreBreakdown(TypedDict):
    semantic_evidence: float
    theme_coverage: float
    theme_balance: float
    scale_correction: float
    candidate_sufficiency: float
    distance_penalty: float
    congestion_penalty: float
```

### 4.2 `haversine_distance`

위도/경도 두 점 사이의 직선 대권거리를 km 단위로 계산한다.

사용 위치:

| 사용처 | 목적 |
| --- | --- |
| `score_place` | 도시 내부 후보군 기준점에서 멀리 떨어진 장소 약한 감점 |
| `score_city` | 사용자 위치와 도시 후보군 평균 좌표 사이 거리 감점 |

실제 이동 시간, 대중교통 소요 시간, 도로 경로 최적화는 계산하지 않는다.

## 5. `score_place`

### 5.1 역할

`score_place(cand, active_themes, reference_location=None)`는 단일 관광지 후보의 점수를 계산한다.
현재 단계에서 `restaurant` 후보는 입력으로 받지 않는다.

공식:

```text
place_score =
    raw_similarity
  + soft_similarity
  + theme_match_score
  + source_quality_score
  - local_distance_penalty
```

최종 점수는 음수가 되지 않도록 `max(score, 0.0)`을 적용한다.

### 5.2 입력

| 입력 | 설명 |
| --- | --- |
| `cand.distance` | raw query channel의 S3 Vector distance |
| `cand.soft_distance` | soft query channel의 S3 Vector distance. 없으면 `None` |
| `cand.metadata.theme_tags` | 테마 일치 여부 |
| `cand.metadata.latitude`, `longitude` | source quality와 거리 penalty |
| `cand.metadata.title` | source quality |
| `cand.metadata.city_id` 또는 `city_name_ko` | source quality |
| `active_themes` | scoring 대상이 되는 `searchable_place_themes`. 현재 `미식·노포`처럼 외부 링크로 처리하는 테마는 제외 |
| `reference_location` | 같은 도시 후보군의 평균 좌표 |

### 5.3 점수 구성 요소

| 요소 | 계산 | 의미 |
| --- | --- | --- |
| `raw_similarity` | `1.0 - distance`, distance 없으면 `0.0` | cleaned raw query와의 의미적 근접도 |
| `soft_similarity` | `1.0 - soft_distance`, 없으면 `0.0` | 분위기/감성 query와의 의미적 근접도 |
| `theme_match_score` | searchable place theme와 후보 `theme_tags`가 겹치면 `+0.2` | 검색 대상 관광 테마 직접 일치 보너스 |
| `source_quality_score` | metadata completeness 최대 `+0.2` | Planner가 쓸 최소 필드가 있는지 |
| `local_distance_penalty` | 기준점에서 1km당 `0.005` 감점 | 도시 내부에서 너무 먼 후보 약한 감점 |

### 5.4 Source quality의 의미

`source_quality_score`는 실제 리뷰 품질, 설명의 풍부함, 영업 정확도를 평가하지 않는다.

현행 규칙은 다음 metadata가 비어 있지 않은지만 본다.

| metadata | 보너스 |
| --- | --- |
| `latitude`와 `longitude` | `+0.05` |
| `title` | `+0.05` |
| `theme_tags` | `+0.05` |
| `city_id` 또는 `city_name_ko` | `+0.05` |

최대 `+0.2`다.

이 점수는 "좋은 콘텐츠" 보너스가 아니라, Planner가 후보를 다루기 위한 최소 metadata completeness guardrail이다.

## 6. `score_city`

### 6.1 역할

`score_city(...)`는 도시 후보의 최종 ranking 점수와 breakdown을 계산한다.

공식:

```text
city_score =
    semantic_evidence
  + theme_coverage
  + theme_balance
  - scale_correction
  + candidate_sufficiency
  - distance_penalty
  - congestion_penalty
```

반환값:

```text
(city_score, breakdown)
```

`city_score`와 breakdown 값은 소수점 4자리로 반올림한다.

### 6.2 입력

| 입력 | 설명 |
| --- | --- |
| `city_id` | 평가 대상 도시 ID |
| `places` | 해당 도시의 후보 목록. 각 후보에는 `place_score`가 있어야 함 |
| `active_themes` | scoring 대상이 되는 `searchable_place_themes` |
| `user_location` | 사용자 출발지 좌표. 없으면 거리 감점 없음 |
| `primary_budget` | tripType에 따른 primary 후보 수 |
| `congestion_index` | 월별 방문자 통계 기반 혼잡도 상대 값 |
| `w_cong` | quiet/vibrant 의도에 따른 혼잡도 가중치 |

### 6.3 Top places 기준

도시 점수는 전체 후보가 아니라 `place_score` 내림차순 상위 `primary_budget`개를 기준으로 계산한다.

```text
sorted_places = places sorted by place_score desc
top_places = sorted_places[:primary_budget]
```

이 정책의 의도:

1. 후보가 많은 도시가 무조건 유리해지는 것을 줄인다.
2. Planner에 실제로 넘길 primary 규모에 가까운 후보 품질을 평가한다.
3. 후보 부족 도시는 `semantic_evidence`에서 자연스럽게 감점된다.

### 6.4 점수 구성 요소

| 요소 | 계산 | 의미 |
| --- | --- | --- |
| `semantic_evidence` | `sum(top place_score) / primary_budget` | 상위 후보들의 의미적 적합도 |
| `theme_coverage` | top places 안에서 커버한 필수 테마 수 / 전체 필수 테마 수 | 필수 테마가 실제 상위 후보에 남았는지 |
| `theme_balance` | Shannon entropy normalized score | 복수 테마가 한쪽으로 치우치지 않았는지 |
| `scale_correction` | `0.02 * log(len(top_places) + 1)` | 후보 수 구조적 이점 약한 보정 |
| `candidate_sufficiency` | `len(top_places) >= 5`이면 `+0.1` | 최소 후보 수 안정성 |
| `distance_penalty` | 사용자 위치와 top places 평균 좌표 거리, 100km당 `0.05` | 출발지 기준 거리 부담 |
| `congestion_penalty` | `congestion_index * w_cong` | 조용함/활기 선호에 따른 혼잡도 반응 |

### 6.5 Theme balance

복수 searchable place theme가 있을 때 `theme_balance`는 Shannon entropy를 사용한다.

의미:

| 값 | 해석 |
| --- | --- |
| `1.0`에 가까움 | 테마 evidence가 비교적 균형적 |
| `0.0`에 가까움 | 한 테마로 쏠림 또는 테마 evidence 없음 |

주의:

1. 한 장소가 여러 theme tag를 가질 수 있으므로 city score의 entropy count에서는 여러 테마에 동시에 기여할 수 있다.
2. 최종 primary quota에서는 Candidate selection helper가 한 장소를 하나의 `_assigned_theme`에 배정한다.
3. 따라서 city score의 `theme_balance`와 `coverage_audit.primary_theme_counts`는 서로 다른 단계의 지표다.

### 6.6 Congestion signal

`ScoringTool`은 방문자 통계를 직접 조회하지 않는다.

상위 orchestration은 다음을 수행한다.

1. DynamoDB에서 도시·월 visitor stats를 조회한다.
2. 도시 간 상대 rank로 `congestion_index`를 만든다.
3. query 문맥이 조용함/활기 중 어디에 가까운지 보고 `w_cong`를 결정한다.
4. `score_city`에 `congestion_index`와 `w_cong`를 넘긴다.

`score_city`는 전달받은 값으로 `congestion_penalty = congestion_index * w_cong`만 계산한다.

## 7. Baseline과 Ours에서의 사용

| 전략 | Scoring Tool 사용 |
| --- | --- |
| Baseline | 현행 비교 기준에서는 다요소 `ScoringTool`을 사용하지 않고 평균 similarity 중심 ranking |
| Ours | `score_place`와 `score_city`를 모두 사용 |

Baseline도 함수 인자로 `scoring_tool`을 받을 수 있지만, 실제 Baseline ranking은 raw similarity 평균을 사용한다.

## 8. Candidate selection과의 경계

`ScoringTool`은 점수를 계산할 뿐, 최종 primary 후보를 직접 고르지 않는다.

점수 이후 흐름:

```text
ScoringTool.score_place()
→ ScoringTool.score_city()
→ city ranking / sufficiency fallback
→ select_primary_with_theme_quotas()
→ reserve 구성
```

Candidate selection helper 담당:

| 기능 | 설명 |
| --- | --- |
| title dedup | 같은 title 반복 후보 제거 |
| min quota | 복수 테마의 최소 evidence 확보 |
| soft max quota | 한 테마가 primary를 과점하지 않게 제한 |
| relaxation | 후보 수가 부족하면 soft max를 완화 |
| `_assigned_theme` | primary audit용 테마 배정 |

따라서 theme quota 결과는 Scoring Tool의 score가 아니라 Candidate Evidence의 primary selection audit로 해석해야 한다.

## 9. Scoring 한계

| 한계 | 설명 |
| --- | --- |
| source quality는 metadata 존재 여부만 봄 | description 길이, 리뷰 품질, 영업 정확도는 평가하지 않음 |
| 거리 penalty는 직선거리 기반 | 실제 도로/대중교통/소요 시간은 반영하지 않음 |
| DynamoDB detail 미사용 | scoring은 vector metadata 기반이며 상세 설명 내용은 직접 평가하지 않음 |
| 실시간 혼잡도 미사용 | visitor stats 기반 상대 index만 사용 |
| Planner 실행 가능성 미검증 | 일정 슬롯 배치와 운영시간 검증은 Planner 단계 |

## 10. Failure와 fallback

Scoring Tool 자체는 예외를 던져 fallback을 결정하는 역할이 아니다.

| 상황 | 처리 |
| --- | --- |
| 후보 없음 | `score_city`는 0점과 0 breakdown 반환 |
| distance 없음 | 해당 similarity를 0으로 처리 |
| soft distance 없음 | soft similarity를 0으로 처리 |
| 좌표 없음 | 거리 penalty를 적용하지 않거나 source quality 보너스 없음 |
| searchable place theme 없음 | theme coverage 0, theme balance 기본값 유지 |

후보 부족, no candidate, AWS 오류 격리는 실행 orchestration과 Candidate Evidence status 계약에서 처리한다.

## 11. Output 예시

도시 score breakdown 예시:

```json
{
  "semantic_evidence": 1.2842,
  "theme_coverage": 1.0,
  "theme_balance": 0.9183,
  "scale_correction": 0.0479,
  "candidate_sufficiency": 0.1,
  "distance_penalty": 0.0,
  "congestion_penalty": 0.125
}
```

이 breakdown은 `city_rankings[].score_breakdown` 또는 평가 리포트에서 도시 선택 이유를 설명하는 audit 자료로 사용된다.

## 12. Change History

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.3 | 2026-06-13 | llm | `restaurant` 후보를 Scoring Tool 입력에서 제외하고, 현재 scoring 대상이 관광지 후보임을 명시 |
| v0.2 | 2026-06-13 | llm | 외부 파일 경로 직접 참조를 제거하고 Scoring Tool의 입력·출력·점수 규칙 중심으로 정리 |
| v0.1 | 2026-06-13 | llm | place score, city score, score breakdown, candidate selection과의 경계 문서화 |
