# Candidate Evidence Agent Baseline 비교 설계

> 문서 성격: 보조 Markdown
> 대표 문서: `../05_agent_spec.md`

> 문서 버전: v1.1
> 문서 상태: 검토 중 (Review)  
> 기준 문서: `../05_agent_spec.md`, `candidate_evidence_agent.md`, `../../10_test_plan/supplemental/candidate_evidence_search_test_plan.md`

# 1. 목적

본 문서는 `Candidate_Evidence_Agent`가 단순 RAG Baseline에서 무엇을 유지하고 무엇을 추가했는지 설명한다. 비교의 목적은 Ours를 무조건 우수하다고 선언하는 것이 아니라, 각 추가 요소가 어떤 실패 유형을 줄이려는 설계인지와 현재 실험에서 어디까지 확인됐는지를 분리해 기록하는 것이다.

# 2. 비교 원칙

Baseline과 Ours는 다음 공통 조건을 사용한다.

| 공통 조건 | 적용 내용 |
| --- | --- |
| 입력 | 동일한 `cleaned_raw_query`, 국가, 일정 유형, 필수 테마 |
| 테마 검색 | 필수 테마별 S3 Vector 검색과 동일 metadata filter |
| hard constraint | 필수 테마를 모두 보유한 도시만 생존하는 AND gate |
| 후보 예산 | daytrip `6+4`, 2d1n `10+8`, 3d2n `14+10`, 4d3n 이상 `18+12` |
| 후보 부족 처리 | `full_budget → primary_budget → best_available` fallback |
| 오류 처리 | `ok`, `no_candidate`, `insufficient_candidates`, `error` 상태 기록 |
| 상세 조회 | 최종 선택 도시의 primary 후보만 DynamoDB에서 rehydrate |

따라서 후보 예산, reserve, fallback, 실패 상태는 Ours만의 장점이 아니라 공정 비교를 위한 공통 정책이다.

# 3. Baseline 정의

Baseline은 필수 테마별 raw query 검색 결과만 사용한다.

```text
raw query embedding
→ required theme별 vector search
→ place_id 중복 병합
→ city grouping
→ hard-theme AND gate
→ raw similarity 기반 도시 순위
→ 공통 후보 충분성 fallback
→ raw similarity Top-K primary/reserve
```

Baseline은 다음 요소를 사용하지 않는다.

- `soft_preference_query` 추가 검색
- raw/soft evidence 융합
- 방문객 기반 quiet/vibrant 혼잡도 조정
- 출발지 및 도시 내부 거리 감점
- source quality 점수
- entropy 기반 theme balance
- primary min quota 및 soft max quota

Baseline의 장점은 단순성, 낮은 호출량, 낮은 지연 시간이다. 주요 한계는 도시가 AND gate를 통과했더라도 최종 Top-K가 고유사도 단일 테마로 다시 편중될 수 있다는 점이다.

# 4. Ours에 추가된 설계

| 추가 요소 | 설계 의도 | 줄이려는 실패 |
| --- | --- | --- |
| soft retrieval channel | 분위기·감성 표현을 별도 query로 검색 | raw query에 없는 quiet/vibrant evidence 누락 |
| raw/soft evidence 병합 | 같은 장소의 두 distance를 함께 보존 | 한 채널의 신호가 다른 채널을 덮는 문제 |
| 다요소 place score | raw/soft, theme match, source quality, local distance 반영 | 유사도만 높고 근거가 빈약하거나 동선이 나쁜 장소 우대 |
| 다요소 city score | semantic, coverage, entropy, scale, sufficiency, distance, congestion 반영 | 장소 수가 많은 도시와 단일 테마 도시의 과대평가 |
| entropy theme balance | 필수 테마 후보 비율의 정규화 Shannon entropy 계산 | coverage만 충족하고 실제 분포는 편중되는 문제 |
| min theme quota | 각 필수 테마의 primary 최소 노출 보장 | 최종 primary에서 필수 테마가 사라지는 문제 |
| soft max quota | 한 테마가 primary 절반을 넘지 않게 우선 구성 | 한 테마의 primary 독점 |
| quota relaxation | 상한 때문에 slot이 빌 때만 cap 완화 | 균형을 위해 추천 수 자체가 줄어드는 문제 |
| title 선제 중복 제거 | quota 계산 전에 동일 이름 후보 제거 후 재충전 | 다른 ID의 같은 장소가 quota와 후보 수를 부풀리는 문제 |
| 상세 audit | score, fallback, quota, retrieval, warning 기록 | 결과 차이의 원인을 설명하지 못하는 문제 |

# 5. 선택 알고리즘

도시 ranking은 후보군 전체의 entropy를 포함한 city score로 수행한다. 최종 도시가 정해진 뒤 primary 구성은 별도 단계로 처리한다.

```text
1. place_score 내림차순 정렬
2. title 정규화 후 중복 제거
3. theme_min_quota 우선 배정
4. theme_max_quota 이내에서 점수순 충전
5. primary slot이 비는 경우에만 max quota 완화
6. 미선택 고유 후보를 reserve로 배정
```

```text
theme_min_quota = floor(primary_budget / required_theme_count * 0.6)
theme_max_quota = ceil(primary_budget / 2)
```

복수 theme tag를 가진 후보는 quota 계산에서 하나의 `assigned_theme`에만 배정한다. 상한이 완화되면 `theme_max_quota_relaxed` reason code와 audit를 남긴다.

# 6. 현재 검증에서 확인된 설계 효과

2026년 6월 12일 평가에서 다음을 확인했다.

| 관측 항목 | Baseline | Ours |
| --- | ---: | ---: |
| 24건 중 후보 예산 충족 | 7 | 17 |
| 후보 부족 | 17 | 7 |
| 평균 실행 시간 | 2.28초 | 7.31초 |
| 평균 고유 후보 고려 수 | 93.75 | 165.25 |
| 평균 선택 도시 후보 수 | 12.08 | 19.29 |
| 평균 DynamoDB GetItem 추정 | 7.79 | 29.62 |

복수 테마 20건에서는 11건이 soft max quota를 그대로 지켰고, 9건은 희소 테마 때문에 상한을 완화했다. minimum quota 자체를 채울 수 없었던 케이스는 3건이었다.

통제 fixture 기반 38개 테스트는 모두 통과했다. 이 중 7개 outcome-quality 테스트는 soft channel, congestion, origin distance, entropy, min quota, soft max quota, source quality가 필요한 합성 시나리오에서 외부 utility를 개선하는지 확인한다.

# 7. 해석 경계

현재 결과로 다음은 말할 수 있다.

- Ours는 Baseline보다 더 넓은 evidence pool을 고려한다.
- Ours는 quiet/vibrant 신호와 복수 테마 구성을 결과에 반영할 수 있다.
- min quota와 soft max quota는 최종 primary의 테마 누락과 편중을 줄인다.
- 후보 부족과 AWS 오류는 실행 중단 대신 구조화된 결과로 기록된다.

다음은 아직 말할 수 없다.

- Ours가 모든 실제 사용자 요청에서 항상 더 좋은 도시를 고른다.
- 현재 score weight와 quota 계수가 최적이다.
- 추천 장소의 영업 상태, 계절성, 실제 이동 시간이 검증됐다.
- Candidate Evidence Package의 개선이 최종 Planner 일정 품질로 그대로 이어진다.

# 8. 설계 보완 우선순위

| 우선순위 | 보완 항목 | 이유 |
| --- | --- | --- |
| P0 | theme taxonomy 정제 | 잘못된 태그는 entropy와 quota를 모두 잘못된 방향으로 유도 |
| P0 | 희소 테마 shortfall 정책 | 최소 quota 미달 시 confidence와 Planner 안내 기준 필요 |
| P1 | fallback scoring 재검토 | score winner가 후보 부족으로 교체되는 비율이 `19/24`로 높음 |
| P1 | distance·congestion weight calibration | 출발지 변화에 최종 도시가 반응하지 않거나 혼잡도가 다른 신호를 압도할 수 있음 |
| P1 | retrieval·DynamoDB 비용 절감 | Ours의 평균 지연과 조회 수가 Baseline보다 큼 |
| P2 | itinerary-level 검증 | 장소 후보 품질과 최종 일정 실행 가능성은 별도 문제 |

# 9. 관련 문서

- 상세 Agent 계약: `candidate_evidence_agent.md`
- 전체 Agent 구조: `../05_agent_spec.md`
- 도시·관광지 검색 테스트 계획: `../../10_test_plan/supplemental/candidate_evidence_search_test_plan.md`
- 상세 평가 보고서: `../../10_test_plan/supplemental/candidate_evidence_evaluation_results.md`
