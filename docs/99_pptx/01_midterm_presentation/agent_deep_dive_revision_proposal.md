# 중간발표 본론 보강안 — 에이전트 딥다이브 수정 제안

> 작성자: 로브 기획팀  
> 문서 상태: 본론 B3/B4 보강 초안  
> 적용 대상: `body_revision_proposal.md`의 B3 에이전트 플로우, B4 구현 딥다이브  
> 목적: Retriever, Ranker, Planner를 포함한 추천 에이전트 구조에서 “무엇이 핵심이고, 기존 문제를 어떻게 해결했는지”를 발표용 메시지로 명확히 정리한다.

---

## 1. 수정 방향 요약

현재 `body_revision_proposal.md`는 본론 전체 흐름은 잘 잡혀 있다. 다만 B3/B4는 아직 “여러 에이전트가 있다”는 구조 설명에 가깝고, 각 에이전트가 어떤 기존 문제를 해결하는지 충분히 드러나지 않는다.

따라서 본론의 에이전트 설명은 다음 메시지로 재정렬한다.

```text
Lovv는 LLM에게 추천을 상상하게 하지 않는다.
Tool이 검색·계산·검증을 구조화된 절차로 수행하고,
Agent가 그 결과를 해석해 라우팅, fallback, 최종 설명 생성을 담당한다.
```

발표에서 강조할 핵심은 다음 세 가지다.

| 핵심 | 기존 문제 | Lovv의 해결 |
| --- | --- | --- |
| Polymorphic Retriever | 사용자가 목적지를 모르는 경우와 이미 고른 경우가 섞여 일반 검색 하나로 처리하기 어려움 | 진입 맥락에 따라 소도시 후보, 지역 내 장소, 일정 보충 후보를 다르게 검색 |
| Ranker Agent | “비슷한 장소”가 곧 “좋은 여행 도시”는 아님 | 도시별 evidence와 점수 breakdown을 분리해 최종 선정 과정을 audit 가능하게 설계 |
| Planner / Itinerary Writer | 추천 장소 목록만으로는 실제 여행 일정이 되지 않음 | 선택 도시와 evidence를 동선·시간·장소 유형에 맞춰 일정으로 조립 |
| Festival Verifier | 축제는 매년 일정이 바뀌어 RAG 결과를 그대로 믿으면 오배치 위험이 큼 | 해당 연도 개최일과 출처를 검증해 confirmed만 일정에 직접 반영 |

---

## 2. B3 에이전트 플로우 수정안

### 기존 B3 핵심 메시지

```text
단일 LLM이 아니라 — 역할을 나눈 멀티스텝 Agent + 결정적 Skill
```

### 수정 후 핵심 메시지

```text
계산은 Tool이, 판단은 Agent가 — 검색·점수·검증을 근거로 다음 행동을 결정한다
```

또는 화면 카피를 더 짧게 가져가려면:

```text
Tool은 계산하고, Agent는 판단한다
```

### 화면 구성 제안

좌→우 파이프라인은 유지하되, 각 노드를 “Tool이 하는 일”과 “Agent가 판단하는 일”로 나눈다.

| 단계 | Agent / Tool | Tool 로직 | Agent 로직 |
| --- | --- | --- | --- |
| 1 | `Intent_Agent` | 입력값 스키마 검증 | 자연어를 required / soft / unsupported로 구조화 |
| 2 | `Supervisor_Router` | 상태값·완료 플래그 확인 | 다음 노드 선택, 재시도, fallback 라우팅 |
| 3 | `Polymorphic_Retriever` | theme gate, vector search, 후보 추출 | Discovery / Targeted / Supplement 모드 선택, 후보 부족 시 fallback 판단 |
| 4 | `Ranker` | 도시별 score breakdown, tie-break | 최종 소도시 선정, 추천 근거 생성 |
| 5 | `Festival_Verifier` | 축제 날짜·출처 검증 | confirmed / tentative / rejected에 따라 일정 반영 여부 판단 |
| 6 | `Itinerary_Writer` | 장소 후보·동선·유형 제약 확인 | 사용자에게 읽히는 일정, 대체안, 설명 생성 |
| 7 | `Output_Validator` | 조건 충족·근거 누락·환각 체크 | 실패 유형별 재시도 또는 안내문 생성 |

### 발표자 노트

- “LLM이 점수를 상상하거나 없는 장소를 만들어낼 위험을 줄이기 위해, 계산과 검색은 Tool 기반 절차로 분리합니다.”
- “Agent는 Tool 결과를 보고 다음 행동을 정합니다. 후보가 부족하면 조건을 완화하거나 backup theme을 쓰고, 축제가 불확실하면 일정에 직접 넣지 않고 안내로 돌립니다.”
- “이 구조 덕분에 Lovv는 추천 결과뿐 아니라 ‘왜 이 추천이 나왔는지’까지 설명할 수 있습니다.”

---

## 3. Polymorphic Retriever 설명 보강

### 발표에서 바로잡아야 할 지점

`Polymorphic_Retriever`를 단순히 “소도시 후보 검색”으로 설명하면 의미가 좁아진다. 이 에이전트가 polymorphic인 이유는 사용자의 맥락에 따라 검색 대상이 달라지기 때문이다.

### 화면용 정의

```text
Polymorphic Retriever
= 사용자의 진입 맥락에 따라 검색 범위를 바꾸는 다형 검색 에이전트
```

### 3가지 모드

| 모드 | 상황 | 검색 대상 | 핵심 로직 |
| --- | --- | --- | --- |
| Discovery Mode | 사용자가 목적지를 정하지 않음 | 소도시 후보 + 도시별 장소 evidence | 거리·테마 gate 후 raw/soft evidence 검색 |
| Targeted Mode | 지도/링크에서 특정 소도시로 진입 | 해당 소도시 내부 장소 후보 | 도시 scan 생략, 지역 내부 evidence 검색 |
| Supplement Mode | 일정 생성 중 장소가 부족함 | 부족한 테마·시간대·축제 후보 | Planner 요청에 맞춰 보충 후보 검색 |

### 기존 문제와 해결

| 기존 문제 | Retriever 해결 |
| --- | --- |
| 일반 검색은 사용자가 이미 도시를 알고 있다고 가정 | 목적지 미정이면 조건에 맞는 소도시 후보부터 생성 |
| vector search는 유사 장소는 찾지만 도시 단위 필수 테마 충족을 보장하지 않음 | Discovery Mode에서 도시 단위 Theme Gate 적용 |
| 지역이 이미 고정된 경우에도 전국 검색을 반복하면 비효율 | Targeted Mode에서 해당 도시 내부 검색으로 범위 축소 |
| 일정 중 특정 테마 장소가 부족하면 생성 모델이 빈칸을 상상할 위험 | Supplement Mode에서 부족 조건에 맞는 실제 후보를 재검색 |

### Targeted Mode 입력 정리

지도에서 소도시를 먼저 선택하고 들어가는 경우에는 `pre_selected_city_id`가 핵심 입력이다.

```json
{
  "pre_selected_city_id": "Yangyang",
  "city_name": "양양군",
  "country": "KR",
  "duration_days": 2,
  "travel_month": 6,
  "festival_included": true
}
```

이 경우 Retriever는 전국 도시 scan과 도시 간 rank를 수행하지 않는다.

```text
pre_selected_city_id 있음
→ 도시 후보 탐색 생략
→ 해당 소도시 내부 장소만 검색
→ raw/soft query에 맞는 관광지·음식점·축제 후보 생성
→ Planner / Itinerary Writer로 전달
```

지도 진입 후 사용자가 추가로 자연어를 입력하면, 해당 입력은 “도시를 고르기 위한 조건”이 아니라 “그 도시 안에서 어떤 장소와 일정이 필요한지”를 정하는 조건으로 쓰인다.

예시:

```json
{
  "active_required_themes": ["바다·해안", "미식·노포"],
  "cleaned_raw_query": "바다 산책과 지역 맛집을 포함한 일정",
  "soft_query": "조용하고 한적한 해안 산책 분위기",
  "soft_preferences": ["quiet", "walkable", "local"],
  "pre_selected_city_id": "Yangyang"
}
```

사용자 입력이 거의 없고 도시만 선택된 경우에는 도시 대표 테마 기반 기본 코스를 제안하거나, “원하는 분위기나 포함하고 싶은 테마가 있나요?”처럼 추가 질문으로 이어진다.

### 발표용 한 문장

```text
Polymorphic Retriever는 목적지가 없으면 소도시를, 목적지가 있으면 그 안의 장소를, 일정이 비면 보충 후보를 찾는다.
```

### 테스트 결과와 연결하는 말

현재 테스트는 Polymorphic Retriever 전체가 아니라 Discovery Mode를 중심으로 검증했다.

```text
이번 PoC 테스트는 Lovv의 핵심 차별점인 “목적지 미정 상태에서 소도시를 발견하는 흐름”을 우선 검증했다.
Targeted Mode는 지도 선택 진입 흐름으로 설계되어 있으며 현재 smoke 수준으로 검증 중이다.
Supplement Mode와 Festival retrieval은 후속 검증 범위로 둔다.
```

---

## 4. Ranker Agent 설명 보강

### 발표에서 강조할 핵심

Ranker는 단순히 “점수 높은 장소를 고르는 단계”가 아니다. Retriever가 만든 도시별 evidence package를 받아 최종 소도시를 결정하고, 사용자가 납득할 수 있는 추천 근거를 만든다.

다만 중간발표에서는 Ranker의 모든 보정 요소가 성능적으로 검증 완료되었다고 말하지 않는다. 현재 단계에서 Ranker는 “최적 공식”이라기보다, 추천 과정을 분해해 기록하고 검증할 수 있게 만드는 scoring framework로 설명한다.

```text
Ranker의 핵심은 점수 공식 자체를 과시하는 것이 아니라,
왜 이 도시가 선택됐는지 나중에 검증하고 설명할 수 있게 만드는 것이다.
```

### 기존 문제

```text
가장 비슷한 장소가 있는 도시 = 가장 좋은 여행 도시는 아니다.
```

단순 유사도 평균의 한계:

- 장소 수가 많은 도시가 유리해질 수 있음
- 한 테마 evidence가 다른 테마 부족을 덮을 수 있음
- 거리·혼잡도·축제 검증 여부가 반영되지 않음
- 사용자가 말한 분위기 조건이 최종 설명에 연결되지 않음

### Ranker의 해결

| 구성 요소 | 역할 |
| --- | --- |
| raw/soft similarity fusion | 사용자 query와 분위기 조건을 함께 반영 |
| theme anchor aggregation | 선택 테마별 evidence를 따로 확보해 한 테마 쏠림 방지 |
| theme specialization | 도시가 특정 테마에 특화되어 있는지 반영 |
| scale correction | 장소 수 많은 도시의 물량 우위 제한 |
| distance penalty | 여행일수에 따른 접근성 비용 반영 |
| audit log | 최종 추천 이유 생성을 위한 점수 근거 보관 |

### 발표 시 주의할 표현

현재 Ranker는 모든 계수와 보정 항목이 실험적으로 최적화되었다고 주장하기보다, 다음처럼 말하는 것이 안전하다.

```text
현재 PoC에서는 단순 유사도 평균을 baseline으로 두고,
테마 균형·도시 규모·거리·soft preference를 점수 항목으로 분리해
어떤 요소가 최종 추천에 영향을 줬는지 audit 가능하게 설계했습니다.
```

피해야 할 표현:

```text
이 공식이 가장 정확한 추천을 보장합니다.
```

권장 표현:

```text
이 공식은 최종 추천을 설명 가능하게 만들고,
향후 테스트에서 각 보정 항목의 효과를 분리 검증할 수 있게 합니다.
```

### 최종 추천 근거 생성

Ranker Agent는 Scoring Tool의 결과를 그대로 노출하지 않고, 점수 breakdown과 대표 evidence를 사용자 언어로 바꾼다.

예시:

```text
영덕군은 바다·해안 장소와 미식 evidence가 함께 있고,
조용한 해안 산책 분위기와도 맞아 이번 여행 조건에 가장 적합합니다.
```

이 설명은 다음 근거를 기반으로 한다.

```text
theme count
raw/soft similarity
대표 장소 evidence
거리 비용
혼잡도 보정
축제 검증 여부
```

### 발표용 한 문장

```text
Ranker는 “가장 비슷한 장소가 있는 도시”가 아니라, 여행지로 성립하는 도시를 고른다.
```

---

## 5. Planner / Itinerary Writer 설명 보강

### 발표에서 강조할 핵심

Planner는 추천 장소 목록을 그대로 나열하는 단계가 아니다. 선택된 소도시와 evidence를 실제 이동 가능한 일정으로 바꾼다.

### 기존 문제

```text
소도시 정보는 흩어져 있고, 장소를 알아도 하루 일정으로 묶기 어렵다.
```

사용자는 보통 다음을 따로 확인해야 한다.

- 관광지 후보
- 음식점 후보
- 축제 일정
- 날씨
- 지도 동선
- 숙소 검색
- 운영 여부

### Planner의 해결

| 역할 | 설명 |
| --- | --- |
| 일정 조립 | 선택 도시의 evidence를 시간대별 일정으로 구성 |
| 장소 유형 균형 | 관광지·음식점·문화시설·휴식 포인트를 균형 있게 배치 |
| 동선 고려 | 이동 부담이 큰 순서를 피하고 지역 내 흐름을 만든다 |
| 대체 일정 | 날씨·운영정보·사용자 수정 요청에 따라 대체 후보 제안 |
| 설명 생성 | 왜 이 순서인지, 왜 이 장소인지 사용자에게 설명 |

### 발표용 한 문장

```text
Planner는 추천 결과를 “가볼 만한 곳 목록”에서 “실제로 움직일 수 있는 일정”으로 바꾼다.
```

---

## 6. Fallback / Retry 로직 보강

### 왜 필요한가

검색 결과는 항상 충분하지 않다. 특히 소도시는 데이터가 적고, 희소 테마나 축제 조건이 들어오면 후보가 부족할 수 있다.

기존 문제:

```text
후보가 부족한데도 생성 모델이 그럴듯한 장소나 축제를 만들어낼 위험
```

Lovv의 해결:

```text
Tool이 부족·불확실·실패 상태를 감지하고,
Agent가 조건 완화, 재검색, 안내문 생성으로 전환한다.
```

### fallback 판단 예시

| 상황 | Tool이 감지하는 것 | Agent 판단 |
| --- | --- | --- |
| 후보 도시 0건 | theme gate 통과 도시 없음 | backup theme 사용 또는 조건 완화 안내 |
| 특정 테마 evidence 부족 | theme별 Top-N 부족 | Supplement Mode로 추가 검색 |
| 축제 날짜 불확실 | verifier 결과 tentative | 일정 직접 배치 대신 참고 정보로 안내 |
| 근거 부족 | source_url 또는 confidence 부족 | 추천 이유에서 제외하거나 재검색 |
| 출력 검증 실패 | 조건 누락·국가 혼합·환각 의심 | 재시도 또는 fallback 문구 |

### 화면용 도식

```text
Tool 결과
  ├─ 충분함 → Ranker / Planner 진행
  ├─ 후보 부족 → backup theme or 조건 완화
  ├─ 축제 불확실 → tentative 안내
  └─ 검증 실패 → 재시도 or fallback 안내
```

### 발표용 한 문장

```text
Lovv는 실패를 숨기지 않고, 부족하면 조건을 완화하거나 사용자에게 설명한다.
```

발표 시에는 “항상 환각을 막는다”가 아니라 “환각 위험을 줄이기 위해 근거 부족 시 fallback한다”로 표현한다.

---

## 6.5 Festival Verifier 보강 Callout

### 왜 별도 검증이 필요한가

축제는 일반 관광지와 다르다. 장소 자체는 존재해도, 사용자가 여행하는 해당 연도와 날짜에 실제로 열리는지는 매번 달라질 수 있다.

기존 문제:

```text
RAG가 과거 축제 정보를 찾아도, 올해 개최 여부와 날짜가 다르면 일정에 넣을 수 없다.
```

Lovv의 해결:

```text
축제는 Retriever가 일반 장소처럼 바로 일정에 넣지 않고,
Festival Verifier가 해당 연도 개최일과 출처를 확인한 뒤에만 반영한다.
```

### 검증 레일

```text
축제 후보
→ 공식/신뢰 출처 확인
→ 해당 연도 개최일 확인
→ confirmed / tentative / rejected 분류
→ confirmed만 일정 직접 배치
→ tentative는 참고 안내
→ rejected는 제외
```

### 상태별 처리

| 상태 | 의미 | 일정 반영 |
| --- | --- | --- |
| `confirmed` | 해당 연도 개최일과 출처 확인 | 일정에 직접 배치 가능 |
| `tentative` | 축제 정보는 있으나 날짜·출처 불확실 | 참고 정보로만 안내 |
| `rejected` | 조건 불일치 또는 신뢰 불가 | 일정에서 제외 |

### 발표용 한 문장

```text
축제는 RAG 검색 결과를 그대로 믿지 않고, 해당 연도 개최일이 confirmed일 때만 일정에 넣습니다.
```

### B4에 넣는 방식

Festival Verifier를 별도 큰 딥다이브로 만들기보다, B4 하단의 작은 검증 레일 callout으로 넣는 것을 권장한다.

```text
검증 레일: 축제 후보 → 날짜·출처 확인 → confirmed만 일정 반영
```

이렇게 하면 Retriever-Ranker-Planner의 큰 흐름을 유지하면서도, Lovv가 환각과 오배치 위험을 통제한다는 점을 보여줄 수 있다.

---

## 7. B4 딥다이브 교체 제안

현재 B4 후보는 다음이다.

```text
① Explainable RAG = 하이브리드 검색
② Festival Verifier
③ 멀티스텝 통합·단순화
```

발표 목적이 추천 에이전트 구조의 핵심을 보여주는 것이라면, B4는 아래처럼 재구성하는 편이 낫다.

### B4 수정안 — 추천 에이전트 딥다이브

### 핵심 메시지

```text
비슷한 장소 검색에서 끝나지 않고, 도시 후보 → 최종 선정 → 실제 일정으로 이어지게 설계했다
```

### 화면 구성: 3단 문제 해결 도식

| 단계 | 기존 문제 | Lovv Agent 해결 |
| --- | --- | --- |
| 1. Retriever | vector search는 유사 장소는 찾지만 도시 단위 조건을 보장하지 못함 | Polymorphic Retriever가 Discovery/Targeted 맥락을 구분하고 Theme Gate + evidence package 생성 |
| 2. Ranker | 가장 비슷한 장소가 있는 도시가 항상 좋은 여행지는 아님 | 점수 항목을 분리해 최종 소도시 선정 + 추천 근거 생성을 audit 가능하게 설계 |
| 3. Planner | 장소 목록만으로는 실제 여행이 어려움 | 장소 evidence를 동선·시간·대체안이 있는 일정으로 조립 |

### 하단 한 줄

```text
Tool은 계산하고, Agent는 판단한다 — 그래서 추천 결과가 설명 가능하고 재시도 가능하다.
```

### 발표자 노트

- “Retriever는 목적지가 없을 때와 있을 때 검색 범위를 다르게 가져갑니다.”
- “Ranker는 단순 유사도 평균을 baseline으로 두고, 어떤 요소가 최종 선택에 영향을 줬는지 분리해 기록합니다.”
- “Planner는 추천을 장소 목록에서 실제 일정으로 바꿉니다.”
- “그리고 중간에 후보가 부족하거나 검증이 불확실하면 Agent가 fallback 경로를 선택합니다.”
- “축제는 confirmed일 때만 일정에 직접 넣고, 불확실하면 참고 안내로 돌립니다.”

---

## 8. B3/B4에 넣을 최종 발표 문장 모음

발표자가 그대로 사용할 수 있는 문장이다.

```text
Lovv는 단일 LLM이 한 번에 추천을 생성하는 구조가 아닙니다.
검색, 점수 계산, 검증은 Tool 기반 절차로 분리하고,
Agent는 그 결과를 보고 다음 행동을 판단합니다.
```

```text
Polymorphic Retriever는 목적지가 없으면 소도시 후보를 만들고,
목적지가 있으면 그 안의 장소를 찾고,
일정이 비면 부족한 조건에 맞는 보충 후보를 다시 찾습니다.
```

```text
지도에서 소도시를 먼저 선택한 경우에는 도시 추천을 다시 하지 않고,
그 도시 안에서 사용자 취향에 맞는 장소와 일정을 찾습니다.
```

```text
Ranker는 가장 비슷한 장소가 있는 도시를 고르는 것이 아니라,
여행지로 성립하는 도시를 고릅니다.
```

```text
중간발표 단계에서 Ranker는 완성된 최적 공식이라기보다,
추천 근거를 분해해 기록하고 검증할 수 있게 만드는 scoring framework입니다.
```

```text
Planner는 추천 결과를 장소 목록에서 실제로 움직일 수 있는 일정으로 바꿉니다.
```

```text
후보가 부족하거나 검증이 불확실하면, Lovv는 없는 정보를 만들지 않고
조건 완화, 대체 후보, 안내문으로 fallback합니다.
```

```text
축제는 해당 연도 날짜가 confirmed일 때만 일정에 직접 배치합니다.
불확실한 축제는 추천 근거가 아니라 참고 안내로 분리합니다.
```

---

## 9. 예상 질문과 방어 논리

아래 내용은 발표 슬라이드에 모두 넣기보다, 발표자 노트나 질의응답 대비용으로 준비한다.

### Q1. 왜 Retriever가 도시를 먼저 다루나? 사용자는 결국 관광지나 축제를 찾는 것 아닌가?

방어 논리:

```text
Lovv의 최종 산출물은 관광지 목록이 아니라 “소도시 여행 일정”입니다.
그래서 Retriever는 개별 장소를 바로 최종 답으로 고르는 것이 아니라,
여행지로 성립할 수 있는 도시 후보와 그 도시를 뒷받침하는 장소 evidence를 함께 만듭니다.
```

설명 포인트:

- 관광지 하나가 query와 잘 맞아도, 그 도시가 여행 일정으로 성립한다고 볼 수는 없다.
- 소도시 추천에서는 `도시 후보 → 도시 안의 장소 evidence → 최종 도시 선정 → 일정 생성` 순서가 필요하다.
- 따라서 테스트의 city-level 평가는 “최종 장소를 무시한다”는 뜻이 아니라, Lovv의 추천 단위가 소도시 일정이기 때문에 필요한 중간 품질 검증이다.

발표용 짧은 답변:

```text
장소를 찾기 위해서라도 먼저 “여행지로 성립하는 도시 단위 패키지”를 만들어야 합니다.
Lovv의 Retriever는 관광지를 버리는 것이 아니라, 도시별 관광지 evidence를 묶어 Ranker와 Planner가 쓸 수 있게 만듭니다.
```

### Q2. 왜 Polymorphic Retriever라고 부르나? 그냥 검색 조건만 바꾸는 것 아닌가?

방어 논리:

```text
검색 대상 자체가 바뀌기 때문에 polymorphic이라고 부릅니다.
Discovery에서는 소도시 후보를 찾고,
Targeted에서는 이미 선택된 도시 내부 장소를 찾고,
Supplement에서는 일정에서 부족한 조건의 후보를 찾습니다.
```

설명 포인트:

- 같은 vector search를 쓰더라도 입력 상태와 반환 객체가 다르다.
- Discovery Mode의 반환은 `city evidence package`에 가깝다.
- Targeted Mode의 반환은 `selected city 내부 장소 후보`에 가깝다.
- Supplement Mode의 반환은 `Planner가 요청한 부족 슬롯 보충 후보`에 가깝다.

발표용 짧은 답변:

```text
파라미터만 바꾸는 검색기가 아니라, 사용자의 진입 맥락에 따라 검색 단위와 반환 형태가 달라지는 Retriever입니다.
```

### Q3. Targeted Mode와 Supplement Mode는 아직 충분히 테스트되지 않았는데 발표해도 되나?

방어 논리:

```text
발표에서 검증 완료 범위와 설계 범위를 분리해서 말하면 된다.
현재 PoC 테스트는 Lovv의 핵심 진입인 Discovery Mode를 우선 검증했고,
Targeted Mode는 지도 선택 진입 흐름으로 설계되어 smoke 수준 검증 중이며,
Supplement Mode와 Festival retrieval은 후속 검증 범위로 둔다.
```

설명 포인트:

- 중간발표에서는 “완성된 전체 성능”보다 “왜 이런 구조가 필요한가”를 보여주는 것이 목적이다.
- 테스트 결과를 말할 때는 Discovery Mode 중심임을 명시한다.
- Targeted/Supplement는 최종 구현 방향으로 설명하되, 성능 검증 완료처럼 표현하지 않는다.

발표용 짧은 답변:

```text
이번 테스트는 목적지 미정 상태에서 소도시를 발견하는 Discovery 흐름을 우선 검증했습니다.
지도 선택과 일정 보충 모드는 같은 구조 안에서 확장되는 흐름이며, 현재는 후속 검증 범위로 분리해 보고 있습니다.
```

### Q4. Ranker가 아직 검증되지 않았다면 왜 넣나?

방어 논리:

```text
Ranker는 지금 단계에서 “검증 완료된 최적 공식”이 아니라,
추천 결정을 설명 가능하게 만들기 위한 scoring framework입니다.
```

설명 포인트:

- 단순 유사도 평균만 쓰면 왜 해당 도시가 선택됐는지 설명하기 어렵다.
- Ranker는 `raw similarity`, `soft preference`, `theme coverage`, `distance`, `festival verification` 같은 요소를 분리해 기록한다.
- 이 구조가 있어야 나중에 ablation으로 어떤 항목이 성능에 기여했는지 검증할 수 있다.
- 즉, 지금 Ranker의 가치는 “정답 공식”이 아니라 “평가 가능하고 설명 가능한 추천 구조”다.

발표용 짧은 답변:

```text
Ranker는 지금 최적 공식을 주장하기 위한 단계가 아니라, 추천 이유를 분해하고 이후 실험에서 검증할 수 있게 만드는 장치입니다.
```

### Q5. Theme Gate를 넣으면 좋은 후보를 놓칠 위험은 없나?

방어 논리:

```text
있다. 그래서 Theme Gate는 최종 정답을 강제로 고르는 장치가 아니라,
필수 조건을 심하게 위반하는 후보를 줄이는 guardrail로 설명해야 한다.
```

설명 포인트:

- vector search는 query와 비슷한 장소를 찾지만, 도시 단위 필수 테마 충족을 보장하지 않는다.
- Theme Gate는 “좋은 도시를 찾는 모델”이 아니라 “명백히 조건이 맞지 않는 도시를 줄이는 장치”다.
- 희소 테마는 threshold를 낮추고, 후보 부족 시 backup theme 또는 조건 완화로 fallback한다.

발표용 짧은 답변:

```text
Theme Gate는 추천을 확정하는 모델이 아니라 guardrail입니다.
조건을 심하게 벗어난 후보를 줄이고, 후보가 부족하면 완화나 재검색으로 빠지게 설계했습니다.
```

### Q6. Soft preference는 vector similarity만으로 처리하면 안 되나?

방어 논리:

```text
soft preference는 “조용한”, “걷기 좋은”, “현지감 있는”처럼 overview 문장에 직접 드러나지 않는 경우가 많다.
그래서 vector similarity만으로는 약하고, tag나 evidence 기반 보강이 필요하다.
```

설명 포인트:

- 현재 테스트에서도 soft query는 raw query와 다른 후보를 끌어오지만, soft evidence hit는 충분히 높지 않다.
- 이는 soft query가 무의미하다는 뜻이 아니라, soft preference를 별도 tag/evidence로 구조화해야 한다는 근거다.
- 발표에서는 “soft preference를 이미 완벽히 해결했다”가 아니라 “baseline 한계를 확인했고 tag 기반 보강이 필요하다”로 말한다.

발표용 짧은 답변:

```text
soft query는 후보 다양화에는 도움이 되지만, 분위기 조건을 안정적으로 맞추려면 tag/evidence 보강이 필요합니다.
그래서 다음 실험 방향을 soft preference tag로 잡았습니다.
```

### Q7. Tool이 계산한다면 Agent는 왜 필요한가?

방어 논리:

```text
Tool은 한 번의 계산 결과를 만들지만, Agent는 그 결과가 충분한지 판단하고 다음 행동을 선택한다.
```

설명 포인트:

- 후보가 충분하면 Ranker/Planner로 진행한다.
- 후보가 부족하면 theme 완화, backup theme, Supplement Mode로 전환한다.
- 축제가 불확실하면 일정 배치가 아니라 참고 안내로 돌린다.
- 출력 검증 실패 시 재시도 또는 fallback 문구를 생성한다.

발표용 짧은 답변:

```text
Tool은 검색과 계산을 하고, Agent는 그 결과를 보고 계속 진행할지, 재검색할지, 사용자에게 안내할지 결정합니다.
```

### Q8. 축제 검증을 별도 Verifier로 둔 이유는?

방어 논리:

```text
축제는 장소와 달리 “존재 여부”만으로 충분하지 않고,
사용자가 여행하는 해당 연도와 날짜에 실제로 열리는지가 중요하기 때문이다.
```

설명 포인트:

- RAG가 과거 축제 정보를 찾아도 올해 일정과 다르면 일정 오배치가 발생한다.
- confirmed만 일정에 넣고, tentative는 참고 안내, rejected는 제외한다.
- 이 구조는 축제 추천 품질뿐 아니라 생성형 답변의 신뢰성을 지키는 방어선이다.

발표용 짧은 답변:

```text
축제는 매년 날짜가 바뀌기 때문에 일반 관광지처럼 바로 일정에 넣으면 위험합니다.
그래서 해당 연도 날짜와 출처가 confirmed일 때만 일정에 반영합니다.
```

### Q9. 지금 테스트 결과가 낮은데 이것을 어떻게 설명할 것인가?

방어 논리:

```text
낮은 baseline 결과는 실패가 아니라, vector search만으로는 Lovv의 추천 문제를 풀기 어렵다는 근거다.
```

설명 포인트:

- R0 baseline은 “임베딩 유사도만 썼을 때의 한계”를 보기 위한 기준선이다.
- city/theme completeness가 낮다면 Theme Gate, theme-balanced retrieval, soft preference tag가 필요한 이유가 된다.
- 중간발표에서는 “높은 점수”보다 “문제 구조를 확인했고, 그에 맞는 agent/tool 구조를 설계했다”는 흐름으로 설명한다.

발표용 짧은 답변:

```text
baseline 점수가 낮기 때문에 오히려 단순 vector search로는 부족하다는 것이 보였습니다.
그래서 Retriever guardrail, Ranker breakdown, soft preference tag 보강이 필요한 근거로 보고 있습니다.
```

---

## 10. 적용 체크리스트

- [x] B3 제목 또는 서브카피에 “Tool은 계산, Agent는 판단” 문구 추가
- [x] `Polymorphic_Retriever` 설명을 “소도시·관광지·축제 후보 검색”에서 “맥락별 검색 범위 전환”으로 수정
- [x] B3 표에 Tool 로직 / Agent 로직 구분 추가
- [x] B4 딥다이브를 Retriever-Ranker-Planner 3단 문제 해결 구조로 재구성
- [x] fallback/retry 판단 예시를 최소 1개 슬라이드 노트에 포함
- [x] Ranker의 최종 추천 근거 생성 역할을 명시
- [x] Ranker 보정 요소는 “성능 검증 완료”가 아니라 “audit 가능한 scoring framework”로 표현
- [x] Planner가 “장소 목록 → 실제 일정”으로 바꾸는 역할을 명시
- [x] Festival Verifier는 B4 하단 callout으로 `confirmed / tentative / rejected` 검증 레일을 표시
- [x] 예상 질문별 방어 논리를 발표자 노트 수준으로 명시

---

## 11. 최종 요약

본론에서 보여줘야 할 핵심은 “우리가 여러 에이전트를 나눴다”가 아니다.

보여줘야 하는 것은 다음이다.

```text
왜 나눴는가?
기존 검색/생성 방식의 어떤 실패를 막기 위해서인가?
각 Agent가 어떤 판단을 담당하는가?
그 결과 사용자는 왜 더 신뢰할 수 있는 추천과 일정을 받는가?
```

따라서 B3/B4는 단순 파이프라인 설명이 아니라, 다음 메시지로 수렴해야 한다.

```text
Lovv의 추천 에이전트는
도시 후보를 보장하고,
장소 evidence를 모으고,
최종 도시를 설명 가능하게 선택하고,
실제 일정으로 바꾸며,
부족하거나 불확실한 경우 fallback한다.
```
