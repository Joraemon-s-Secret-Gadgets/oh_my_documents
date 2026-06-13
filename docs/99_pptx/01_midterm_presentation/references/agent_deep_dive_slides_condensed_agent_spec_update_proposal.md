# 에이전트 딥다이브 슬라이드 최신 Agent 설계 반영 제안

> 검토 대상: `agent_deep_dive_slides_condensed.md`
> 반영 기준: `05_agent_spec.md`, `langgraph_flow.md`, `candidate_evidence_agent.md`, `agent_harness_design.md`, `recommendation_flow.md`
> 문서 성격: 원문 미수정 상태의 변경 제안서
> 작성일: 2026-06-11

---

## 1. 결론

현재 압축안의 핵심 메시지인 **"Tool은 계산하고, Agent는 판단한다"**와 **"Ranker는 최적 공식이 아니라 검증 가능한 scoring framework다"**는 유지할 가치가 있다.

다만 최신 `05_agent_spec` 설계를 반영하면 다음 세 가지는 반드시 바뀌어야 한다.

1. `Polymorphic_Retriever_Agent`와 `Ranker_Agent`를 독립 Agent처럼 설명하지 않는다. 두 책임은 현재 `Candidate_Evidence_Agent`에 통합되었고, 검색과 점수 계산은 각각 `Destination Search Tool`, `Scoring Tool`이 담당한다.
2. `Output_Validator_Agent`를 독립 노드로 두지 않는다. `Planner_Agent`는 세부 일정 생성, 일정 소개·동선 설명, 결정적 Validation Skill, 의미 검증을 구조 수준에서 통합 담당한다. **도시 추천 근거는 Candidate Evidence Agent 책임**으로 둔다.
3. 설계, baseline 실험, 통합 구현 완료를 구분한다. 현재 자료로 방어 가능한 것은 **설계 계약과 일부 검색 baseline 실험**이며, 전체 Agent 파이프라인이나 Candidate Evidence Package의 end-to-end 구현 완료를 주장해서는 안 된다.
4. `Candidate_Evidence_Agent` 통합은 영구 고정 구조가 아니다. Production 구현에서 검색과 랭킹의 독립 확장·배포·평가 필요성이 확인되면 동일한 Candidate Evidence Package 계약을 유지한 채 `Retriever + Ranker` 구조로 재분리할 수 있는 진화 경로를 명시한다.
5. Candidate Evidence Agent가 Planner에 반환하는 결과는 모든 단계에서 **최종 1개 도시**로 고정한다. `city_discovery`는 여러 도시를 내부 비교한 뒤 1개를 선정하고, `anchored_place_search`는 지정된 1개 도시를 유지한다.

따라서 B4의 주제를 `RAG + Ranker`라는 구형 Agent 분할이 아니라 다음처럼 바꾸는 것이 가장 안전하다.

```text
B4-1 Candidate Evidence Agent: 검색 결과를 Planner가 쓸 수 있는 근거 패키지로 만든다
B4-2 Deterministic Scoring & Audit: 점수 계산을 Tool로 분리하고 선택 근거를 남긴다
```

발표에서는 현재 구조와 Production 진화 가능성을 다음처럼 함께 표현하는 것이 좋다.

```text
PoC·초기 구현: Candidate Evidence Agent로 계약과 상태를 단순화
Production: 검색·랭킹의 부하와 평가 주기가 달라지면 Retriever + Ranker로 재분리 가능
```

---

## 2. 현재안의 주요 문제

### 2.1 최신 Agent 책임 경계와 충돌

| 현재안 | 최신 설계 | 판정 |
| --- | --- | --- |
| `발견 → Polymorphic Retriever + Ranker` | `Candidate_Evidence_Agent`가 검색, 도시/장소 scoring, primary/reserve 패키징 통합 | 교체 필요 |
| B3의 `검색`과 `선정`을 별도 Agent 단계처럼 표현 | Candidate Evidence Agent 내부에서 Search Tool과 Scoring Tool을 순차 사용 | 하나의 Agent 노드 내부 Tool 단계로 표현 |
| `선정 단계가 추천 근거 생성` | 방향이 맞다. Candidate Evidence Agent가 score breakdown과 장소 evidence를 바탕으로 **도시 추천 근거**를 생성 | 유지하되 출력 계약을 명확히 함 |
| Planner가 도시 추천 이유까지 생성 | Planner는 Candidate Evidence가 만든 도시 추천 근거를 입력으로 받고, 세부 일정·일정 소개·동선 설명을 생성 | 책임 문구 수정 |
| `출력 검증` 독립 노드 | Planner가 일정·일정 설명·Validation Skill·의미 검증 통합 | Planner 내부 검증으로 흡수 |
| `Supplement Mode`를 정식 검색 모드로 설명 | 정본 검색 모드는 `city_discovery`, `anchored_place_search` 두 가지. 후보 부족 시 reserve 사용 후 필요할 때 재호출 | Supplement를 독립 mode로 부르지 않음 |
| `city_rankings`를 Planner 반환 목록처럼 표현 | 여러 도시의 비교 결과는 Candidate Evidence 내부 선정·감사용 데이터이며 Planner에는 최종 1개 도시만 전달 | 단일 도시 출력으로 수정 |

### 2.2 단일 도시 출력 원칙

Candidate Evidence Agent의 두 검색 모드는 검색 시작점이 다르지만 Planner-facing 출력은 동일해야 한다.

| 모드 | 내부 처리 | Planner-facing 출력 |
| --- | --- | --- |
| `city_discovery` | 여러 후보 도시를 검색·점수화하고 내부 순위를 비교 | 최종 선정 도시 1개와 해당 도시의 추천 근거·장소 후보 |
| `anchored_place_search` | 사용자가 지정한 도시 안에서 장소를 검색·점수화 | 지정 도시 1개와 해당 도시의 추천 근거·장소 후보 |

```text
city_discovery       → N개 도시 내부 비교 → selected_city 1개 반환
anchored_place_search → anchor 도시 유지   → selected_city 1개 반환
```

`city_rankings` 전체 목록은 필요하면 trace, audit, 테스트 결과에 보존할 수 있지만 Planner 입력이나 사용자 반환 목록으로 취급하지 않는다. Planner가 받는 안정 계약은 다음과 같다.

```text
selected_city 1개
selected_city_score_breakdown
city_recommendation_reasons
recommended_places / reserve_places
coverage_audit / retrieval_audit
```

이 원칙은 PoC에 한정하지 않고 Production에서도 유지한다. Production에서 Retriever와 Ranker를 재분리하더라도 Ranker가 최종 1개 도시를 확정한 뒤 Candidate Evidence Package를 반환한다.

### 2.3 Candidate Evidence Agent의 Production 진화 경로

현재 통합 구조는 Retriever와 Ranker의 역할 차이를 없앤 것이 아니라, **하나의 내부 계약과 상태 경계 안에 배치한 것**이다. 따라서 Production에서 다음 조건이 실제로 나타나면 두 책임을 다시 분리하는 것이 타당하다.

| 재분리 트리거 | 이유 |
| --- | --- |
| 검색과 scoring의 트래픽·지연 특성이 달라짐 | vector 검색은 I/O와 인덱스 부하 중심이고 scoring은 CPU·규칙 계산 중심이므로 독립 확장이 유리할 수 있음 |
| 검색 인덱스와 점수 공식의 배포 주기가 달라짐 | 검색 모델·인덱스 교체와 가중치·정책 변경을 서로 영향 없이 배포할 필요가 생김 |
| Retriever와 Ranker를 별도 데이터셋·SLA로 평가해야 함 | retrieval recall과 ranking quality를 독립적으로 관측하고 회귀 차단하기 쉬워짐 |
| 후보 수나 국가 범위가 커져 중간 결과 캐시가 필요함 | 검색 후보를 캐시하고 여러 ranking 정책이 재사용할 수 있음 |
| 팀 소유권이나 장애 격리가 필요함 | 검색 장애와 scoring 장애의 blast radius를 나눌 수 있음 |

재분리 시에도 외부 흐름과 Planner 계약은 바꾸지 않는 것이 핵심이다. Ranker 또는 통합 Candidate Evidence Agent가 도시 추천 근거까지 완성해 같은 패키지로 전달한다.

```text
현재
Candidate_Evidence_Agent
  ├─ Destination Search Tool
  └─ Scoring Tool

Production 재분리 가능 구조
Retriever Agent → Candidate Pool
Ranker Agent    → Candidate Evidence Package + 도시 추천 근거
Planner Agent
```

즉, 발표에서 `Retriever + Ranker를 폐기했다`고 말하지 않는다. **현재는 통합 orchestration으로 구현하고, Production에서는 운영 지표에 따라 물리적으로 분리할 수 있다**고 설명한다.

### 2.4 구현 완료로 오해될 표현

다음 표현은 근거 저장소나 실행 결과를 즉시 제시할 수 없다면 발표에서 단정하지 않는 편이 좋다.

| 현재 표현 | 위험 | 권장 표현 |
| --- | --- | --- |
| `PoC 구현·검증` | 설계 문서와 baseline 도구 테스트를 통합 시스템 구현으로 오해할 수 있음 | `검색 baseline 실험 수행`, `통합 구현 예정` |
| `현재 PoC는 RDS로 구현·검증` | 문서 설계와 legacy 의사코드는 있으나 Candidate Evidence Agent 통합 구현 증거와 다름 | `PoC 데이터 집계는 관계형 구조로 검증 가능하며, Production 저장소 계약은 별도 설계` |
| `Targeted는 smoke 수준 검증 중` | 최신 정본의 명칭은 `anchored_place_search`; smoke 결과 링크가 슬라이드에 없음 | 결과가 있으면 수치/산출물 링크 제시, 없으면 `설계 범위`로만 표현 |
| `축제 Top-K만 웹 검증하고 TTL 적용` | 정책 설계는 존재하지만 런타임 구현 여부와 별개 | `구현 정책: Top-K 검증 및 상태별 TTL` |
| `환각 체크` | 환각을 완전히 검출한다는 인상을 줌 | `근거 누락·조건 불일치·미검증 사실을 검사해 위험을 낮춤` |

### 2.5 B4-1의 그래프DB 방어 논리

현재 문서 자체의 §7 판단이 타당하다. Lovv의 현 추천 쿼리는 거리 필터, `city_id + theme` 집계, 특화도, 규모 보정, 콘텐츠 균형처럼 관계형 집계가 중심이다. 3홉 이상의 가변 관계 순회가 핵심 요구가 아니므로 Neptune을 현재 딥다이브의 중심으로 세우면 오버엔지니어링 지적을 방어하기 어렵다.

권장 방향:

```text
현재 핵심: vector 의미 검색 + 정형 원장 grounding
고도화 선택지: 관계 순회 요구가 실제로 생길 때 graph index 검토
```

`Production에서 그래프DB로 전환한다`도 확정 계획처럼 말하지 말고, **승격 조건이 있는 선택지**로 낮춘다.

---

## 3. 권장 슬라이드 구조

## 3.1 B3 에이전트 플로우 교체안

### 화면 카피

```text
Tool은 계산하고, Agent는 근거를 보고 다음 행동을 정한다
```

### 권장 도식

| 단계 | Agent / 계층 | Tool 또는 결정적 처리 | Agent 책임 |
| --- | --- | --- | --- |
| 1 | Intent Agent | 입력 스키마 검증 | 자연어를 필수 테마, soft 선호, 미지원 조건으로 구조화 |
| 2 | Supervisor Router | Matrix Transition Skill | `fulfilled_matrix`를 기준으로 다음 노드와 재시도 결정 |
| 3 | Candidate Evidence Agent | Destination Search Tool, Scoring Tool, Weather Trends Skill | 검색 모드 선택, 최종 1개 도시 선정, 도시 추천 근거와 해당 도시의 primary/reserve 장소 패키징 |
| 4 | Festival Verifier Agent | Catalog Search, Web Search | 출처 충돌을 해석하고 `confirmed/tentative/unknown` 판정 |
| 5 | Planner Agent | Validation Skill, Link Builder Skill | 세부 일정·일정 소개·동선 설명 생성, 구조·의미 검증, reserve 사용 또는 재요청 판단 |
| 6 | Backend Serving / SAM | Output Packaging Skill | 검증 완료 결과를 UI 계약으로 직렬화하고 민감정보 마스킹 |

### 반드시 고칠 책임 문구

- 기존 `최종 소도시 선정 + 추천 근거 생성`은 유지하되, Candidate Evidence Agent가 **도시 추천 근거**를 생성한다고 명확히 쓴다.
- Candidate Evidence Package에는 최종 선정 도시 1개의 score breakdown과 도시 추천 근거를 포함한다.
- 여러 도시의 ranking은 Candidate Evidence Agent 내부 비교·audit 용도로만 사용하고 Planner에는 반환하지 않는다.
- Planner는 도시 추천 근거를 새로 만들지 않는다. 이를 입력으로 받아 장소 배치, 일자별 일정 소개, 동선 이유를 생성한다.
- `출력 검증`을 별도 Agent 노드로 그리지 않고 Planner 내부의 결정적 검증과 의미 검증으로 표시한다.
- Supervisor가 raw 대화나 검색 결과를 직접 해석하는 것처럼 말하지 않는다. Supervisor는 `fulfilled_matrix`와 Matrix Transition Skill 결과를 사용한다.

### 발표 노트

```text
검색과 점수 계산은 재현 가능한 Tool로 분리합니다.
Candidate Evidence Agent는 그 결과를 해석해 도시를 선정하고, 왜 이 도시인지에 대한 추천 근거와 장소 후보 패키지를 함께 만듭니다.
Planner는 이 도시 추천 근거를 유지한 채 세부 일정과 일정 소개·동선 설명을 만들고, 검증 실패 시 reserve 후보를 쓰거나 재검색을 요청합니다.
```

---

## 3.2 B4-1 교체안: Candidate Evidence Package

### 제목

```text
도시를 고른 이유와 일정에 쓸 장소 근거를 함께 넘긴다
```

### 서브 카피

```text
도시 추천 근거와 primary·reserve 장소를 함께 준비해 추천과 일정의 이유가 어긋나지 않게 한다
```

### 화면 도식

```text
사용자 조건
  → [Destination Search Tool] 장소 evidence 검색
  → [Scoring Tool] 도시·장소 점수 계산
  → [Candidate Evidence Agent] coverage 확인 및 후보 패키징
  → Planner

Candidate Evidence Package
  selected_city (항상 1개)
  selected_city_score_breakdown
  city_recommendation_reasons
  recommended_places
  reserve_places
  coverage_audit / retrieval_audit
```

### 이 슬라이드가 설명해야 할 설계 가치

1. 단순 Top-K 장소 목록이 아니라 도시 단위 여행 가능성을 평가한다.
2. 복수 테마 quota로 한 테마 쏠림을 줄인다.
3. primary가 일정 제약으로 탈락해도 reserve를 먼저 사용해 불필요한 재검색을 줄인다.
4. `coverage_audit`와 `retrieval_audit`로 부족한 이유와 사용한 검색 경로를 남긴다.
5. score breakdown과 대표 장소 evidence를 사용자 관점의 **도시 추천 근거**로 변환한다.
6. discovery에서도 여러 도시 목록이 아니라 최종 선정 도시 1개만 Planner에 전달한다.
7. 이 패키지는 내부 계약이며 외부 `/recommendations` 응답 전체가 아니다. Planner가 세부 일정과 일정 소개를 추가한다.

### 도시 추천 근거 출력 제안

도시 추천 근거는 다음과 같은 구조로 표현할 수 있다.

```json
{
  "city_recommendation_reasons": [
    {
      "reason_code": "theme_coverage",
      "summary": "선택한 바다·해안과 미식·노포 테마를 모두 충족합니다.",
      "evidence_place_ids": ["P_001", "P_002"]
    },
    {
      "reason_code": "candidate_sufficiency",
      "summary": "1박 2일 일정을 구성할 primary·reserve 장소가 충분합니다.",
      "evidence_place_ids": ["P_003", "P_004"]
    }
  ]
}
```

추천 근거는 최소한 다음 원칙을 지킨다.

- Scoring Tool의 `score_breakdown`과 실제 `evidence_place_ids`에서 파생한다.
- 도시를 추천한 이유만 설명하고, 일자별 방문 순서나 동선 소개는 만들지 않는다.
- 근거가 없는 분위기·운영 여부·축제 날짜를 보강해서 쓰지 않는다.
- Production에서 Retriever와 Ranker로 분리되면 Ranker가 이 필드를 생성한다.

### 구현 상태 라벨

화면 하단에 다음처럼 작게 표기한다.

```text
현재: 검색 baseline·데이터 분포 검증 / 설계: Candidate Evidence Package 계약 확정 / 후속: LangGraph 통합 구현·E2E 검증
```

`구현 완료` 여부가 실제로 확인되면 그때 라벨만 갱신한다.

### Production 진화 각주

화면 하단 또는 발표자 노트에 다음 한 줄을 추가한다.

```text
운영 단계에서 검색·랭킹의 확장 및 평가 주기가 달라지면, 동일 계약을 유지한 채 Retriever와 Ranker로 재분리할 수 있다.
```

이 문구는 `Production에서는 반드시 분리한다`는 로드맵이 아니라 **분리 조건을 보존한 아키텍처**라는 의미로 사용한다.

---

## 3.3 B4-2 교체안: Scoring Tool & Audit

### 제목

```text
가장 비슷한 장소가 있는 도시와, 실제 여행하기 좋은 도시는 다르다
```

### 서브 카피

```text
점수 계산은 결정적 Tool로 분리하고, Agent는 breakdown과 후보 충분성을 해석한다
```

### 권장 점수 항목

점수 항목은 일단 기존 발표안과 `recommendation_flow.md`의 설명 구조를 유지한다. Candidate Evidence Agent는 이 점수 breakdown과 대표 장소 evidence를 이용해 도시 추천 근거를 생성한다.

| 점수 항목 | 역할 |
| --- | --- |
| 테마 충족도 | 선택한 모든 테마를 만족하는가 (`theme` 컬럼 집계로 확정) |
| 테마 특화도 | 고정 20%가 아니라 전체 평균 대비 강한가 |
| 희소 테마 보정 | 온천처럼 희소한 테마가 데이터량 때문에 과소평가되지 않는가 |
| 도시 규모 보정 | 장소 수를 구간화해 큰 도시의 물량 우위를 제한하는가 |
| soft / raw 적합도 | 분위기와 원문 맥락을 임베딩 유사도로 가산하는가 |
| audit log | 어떤 항목과 대표 장소가 도시 선택에 기여했는지 기록하는가 |

이 여섯 항목은 검증 완료된 최종 가중치가 아니라, 추천 이유를 분해하고 이후 ablation으로 각 항목의 효과를 검증하기 위한 현재 scoring framework다. 향후 `Candidate Evidence Package`의 내부 필드명이 달라지더라도 발표의 사용자 관점 설명은 이 항목을 기준으로 유지할 수 있다.

### 하단 문구

```text
Ranker는 "정답 공식"이 아니라, 추천 이유를 분해해 검증·설명 가능하게 만드는 scoring framework다
```

### 실측 수치 사용법

`미식·노포 43.17%`, `온천·휴양 약 2.8%`, 도시별 최대 440개라는 데이터 불균형은 설계 필요성을 설명하는 근거로 적절하다. 다만 현재안의 `온천 2%`는 반올림이 과하므로 `약 3%` 또는 정확한 `2.8%`로 고친다. `21~440개`의 최솟값 21은 같은 분석 기준에서 산출됐는지 캡션 또는 출처를 확인한 뒤 사용한다.

---

## 4. 방어 논리 검토

| 질문 | 판정 | 권장 답변 |
| --- | --- | --- |
| 왜 Retriever와 Ranker를 합쳤나? | 강한 방어 가능 | `초기 구현에서는 두 단계가 같은 후보 상태와 audit 계약을 공유하므로 하나의 Candidate Evidence Agent로 묶어 상태 전달과 재시도를 단순화했습니다.` |
| Production에서도 계속 통합하나? | 조건부 진화 경로 명시 | `고정하지 않았습니다. 검색과 랭킹의 트래픽, 배포 주기, 평가 SLA가 달라지면 Candidate Evidence Package 계약은 유지한 채 Retriever와 Ranker를 독립 Agent로 재분리할 수 있습니다.` |
| 왜 Candidate Evidence Agent가 필요한가? | 방어 가능 | `Tool 결과를 그대로 넘기지 않고, 도시 단위 coverage와 후보 충분성을 확인해 primary/reserve와 audit을 Planner 계약으로 묶기 위해서입니다.` |
| 도시 추천 근거는 누가 만드나? | 책임 경계 명확화 | `Candidate Evidence Agent가 score breakdown과 실제 장소 evidence를 바탕으로 도시 추천 근거를 만듭니다. Planner는 그 근거를 유지한 채 세부 일정과 일정 소개·동선 설명을 생성합니다.` |
| 검색 모드가 왜 여러 개인가? | 명칭 수정 후 방어 가능 | `목적지 미정이면 city_discovery, 목적지가 정해졌으면 anchored_place_search입니다. 같은 schema를 쓰되 검색 범위와 도시 선택 방식이 달라집니다.` |
| Discovery는 여러 도시를 반환하나? | 단일 도시 원칙 | `아닙니다. 여러 도시는 Candidate Evidence Agent 내부에서만 비교하고, Planner에는 최종 선정 도시 1개와 그 도시의 추천 근거·장소 후보만 전달합니다. Anchored mode도 지정 도시 1개를 반환하므로 두 모드의 출력 계약이 같습니다.` |
| Supplement Mode도 구현됐나? | 현재 답변 부적절 | `독립 mode가 아니라 reserve 우선 사용 후 후보가 모두 부족할 때 Candidate Evidence Agent를 재호출하는 실패 처리입니다.` |
| Ranker가 미검증인데 왜 발표하나? | 논리 적절, 명칭 수정 필요 | `최적 가중치를 주장하는 것이 아니라 결정적 Scoring Tool과 score breakdown 계약을 제시하는 것입니다. 항목별 기여도는 ablation으로 검증할 예정입니다.` |
| 테스트 점수가 낮은데 실패 아닌가? | 조건부로 적절 | `baseline은 단순 유사도 검색의 한계를 측정하기 위한 기준선입니다.` 이후 개선 결과가 없으면 `그래서 설계가 옳다`까지 비약하지 말고 `추가 요소를 검증할 가설을 얻었다`고 끝낸다. |
| Tool이 계산하면 Agent는 왜 필요한가? | 적절 | `Tool은 검색·점수·검증 결과를 만들고, Agent는 충분성·실패 신호·상태를 보고 reserve 사용, 재호출, 다음 노드 진행을 결정합니다.` |
| 왜 graph DB가 필요한가? | 현 상태로는 방어 약함 | `현재 핵심 경로에는 필요하지 않아 관계형 대체 구조를 사용합니다. 3홉 이상 관계 순회가 핵심 기능이 될 때 승격을 검토합니다.` |
| 환각을 막을 수 있나? | 절대 표현 금지 | `원장 재검증, confirmed 축제만 일정 배치, Validation Skill, 근거 부족 시 폴백으로 위험을 낮춥니다. 완전 방지를 보장하지는 않습니다.` |
| 축제 검증은 왜 별도 Agent인가? | 강한 방어 가능 | `단순 조회가 아니라 여러 출처의 우선순위, 날짜 충돌, 해당 연도 유효성, confidence 판단이 필요해 독립적인 evidence lifecycle을 갖기 때문입니다.` |
| Planner가 너무 많은 일을 하지 않나? | 논쟁 여지 있음 | `현재는 일정·설명·검증이 동일 evidence를 참조해야 해 구조 수준에서 통합했습니다. 파싱 정확도나 프롬프트 비대화, 테스트 실패율이 임계치를 넘으면 검증 노드를 다시 분리할 수 있습니다.` |

---

## 5. 삭제 또는 강등할 문장

다음 문장은 원문 반영 시 삭제하거나 노트의 조건부 표현으로 강등한다.

- `① 발견 → Polymorphic Retriever + Ranker`를 현재 구현 구조처럼 단정하는 표현. Production 진화 가능성 또는 내부 역할 설명으로는 유지 가능
- `Ranker / Planner 진행`
- `PoC: RDS JOIN → 최종: 그래프DB(Neptune)`
- `Production 단계에서 그래프DB로 전환한다`
- `현재 PoC는 RDS로 구현·검증했습니다`
- `Targeted는 smoke 수준 검증 중` (검증 결과 링크가 없을 때)
- `Supplement Mode와 Festival retrieval은 후속 검증 범위` 중 Supplement를 독립 mode로 보는 표현
- `Output Validator`를 별도 Agent로 표시하는 모든 도식
- Planner가 도시 추천 근거를 새로 생성하거나 Candidate Evidence의 선정 이유를 임의로 바꾸는 표현

---

## 6. 유지할 문장

다음 논리는 최신 설계에서도 유효하다.

- `Tool은 계산하고, Agent는 판단한다.`
- 필수 테마 충족은 벡터 유사도가 아니라 구조화 필드로 확인한다.
- soft/raw 유사도는 hard filter가 아니라 재랭킹 evidence로 사용한다.
- 단순 장소 수는 큰 도시와 흔한 테마에 유리하므로 규모·분포 보정이 필요하다.
- 점수 공식은 최적 정답이 아니라 audit과 ablation이 가능한 framework다.
- 도시 추천 근거는 Candidate Evidence Agent가 score breakdown과 대표 장소 evidence에서 생성한다.
- Planner는 도시 추천 근거를 받아 세부 일정 소개와 동선 설명을 생성한다.
- 축제는 해당 연도 `confirmed`일 때만 일정에 직접 배치한다.
- 근거가 부족할 때 생성으로 메우지 않고 reserve, 재검색, 조건 완화, 안내로 전환한다.
- `항상 환각을 막는다`가 아니라 `환각 위험을 낮춘다`고 표현한다.

---

## 7. 최종 적용 체크리스트

- [ ] B3를 `Intent → Supervisor → Candidate Evidence → Festival Verifier → Planner → Serving`으로 교체
- [ ] Retriever와 Ranker 독립 Agent 표기를 제거
- [ ] 단, Production에서는 운영 지표와 배포·평가 경계에 따라 `Retriever + Ranker`로 재분리할 수 있음을 각주와 Q&A에 명시
- [ ] 재분리 여부와 무관하게 `Candidate Evidence Package`가 Planner-facing 안정 계약임을 명시
- [ ] 검색·점수화가 Candidate Evidence Agent 내부 Tool 호출임을 표시
- [ ] Candidate Evidence Package는 외부 응답 전체는 아니지만 도시 추천 근거까지 포함하고, Planner는 세부 일정 소개를 담당한다고 표시
- [ ] Candidate Evidence Package의 도시 추천 근거 출력 예시를 `city_recommendation_reasons`로 표시
- [ ] 도시 추천 근거는 Candidate Evidence Agent, 세부 일정·일정 소개·동선 설명은 Planner 책임으로 구분
- [ ] `city_discovery`와 `anchored_place_search` 모두 Planner에 최종 1개 도시만 반환한다고 명시
- [ ] `city_rankings` 전체 목록은 내부 비교·trace·audit 용도로만 두고 Planner-facing 패키지에서 제외
- [ ] Output Validator 독립 노드를 제거하고 Planner 내부 검증으로 이동
- [ ] `Supplement Mode`를 reserve 우선 및 부족 시 재호출 정책으로 교체
- [ ] B4-1을 vector/graph 저장소 설명보다 Candidate Evidence Package 계약 중심으로 재구성
- [ ] Neptune은 확정 전환이 아니라 승격 조건이 있는 고도화 선택지로 강등
- [ ] B4-2 명칭을 `Ranker Agent`가 아니라 `Scoring Tool & Audit`으로 교체
- [ ] 구현 상태를 `baseline 실험 / 설계 확정 / 통합 미구현`으로 분리 표기
- [ ] 실측 수치 `온천 2%`를 `2.8%` 또는 `약 3%`로 수정
- [ ] 모든 Q&A에서 구형 Agent 명칭과 최신 책임 경계를 정합화

---

## 8. 권장 한 문장 요약

```text
Lovv는 Candidate Evidence Agent가 후보를 내부 비교해 최종 1개 도시를 선정하고 그 도시의 추천 근거와 장소 후보 패키지를 만들며, Planner는 그 근거를 바꾸지 않고 세부 일정·일정 소개·동선 설명과 검증을 완성한다. 이 단일 도시 계약은 anchored mode와 Production 재분리 구조에서도 동일하게 유지한다.
```
