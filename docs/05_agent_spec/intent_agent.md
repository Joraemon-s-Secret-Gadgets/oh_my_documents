# Intent Agent 명세서

> 문서 버전: v1.1
> 문서 상태: Review / Intent Agent 상세 정본
> 작성일: 2026-06-12
> 기준 문서: `05_agent_spec.md`, `langgraph_flow.md`, `candidate_evidence_agent.md`, `user_raw_query_flow.md`, `recommendation_flow.md`, `../07_api_spec/07_api_spec.md`

## 1. 문서 목적

본 문서는 Lovv 추천 Agent의 entry node인 `Intent_Agent` 상세 정본이다.

현재 단계에서 Intent Agent의 핵심 목표는 복잡한 계획을 수행하는 것이 아니라, `candidate_evidence_agent.md`의 입력 계약을 안정적으로 만들어 주는 것이다. 즉, 자연어·UI 입력·온보딩 선호·멀티턴 요약을 읽고 Candidate Evidence Agent가 바로 사용할 수 있는 구조화 JSON을 생성한다.

## 2. 모델 정책

Intent Agent 정본은 특정 LLM 모델 ID를 고정하지 않는다.
모델 호출은 Bedrock Converse API adapter를 통해 수행하며, 실제 모델과 tier는
배포 환경 설정, 비용·지연·품질 평가, 운영 정책에 따라 결정한다.

| 항목 | 기준 |
| --- | --- |
| 호출 방식 | Bedrock Converse API adapter |
| 적용 대상 | `Intent_Agent`, `Festival_Verifier_Agent`의 LLM 판단 구간, `Planner_Agent`, 의미 검증 LLM |
| 제외 | embedding model, deterministic Skill, database query, vector search |
| 고정 금지 | prompt와 output schema는 특정 모델 전용 동작이나 모델 배정 전제를 요구하지 않는다 |

모델 차등 배정 여부는 정본에서 고정하지 않는다. 파싱·검증·생성 구간의 모델 tier는
동일한 입출력 계약을 유지한 상태에서 Evaluations와 운영 지표를 기준으로 교체할 수
있어야 한다.

## 3. 책임 범위

Intent Agent가 담당하는 범위:

| 범위 | 설명 |
| --- | --- |
| 멀티턴 요약 해석 | 최근 사용자 발화와 `conversation_summary`를 현재 턴 조건으로 재증류 |
| UI 입력 병합 | `entryType`, `country`, `travelMonth`, `tripType`, `destinationId`, `themes` 등 명시 입력을 우선 반영 |
| 온보딩 병합 | 장기 선호는 기본값으로 사용하되 현재 자연어 의도가 더 강하면 현재 의도를 우선 |
| Candidate Evidence 입력 생성 | `candidate_evidence_input` JSON 생성 |
| soft/raw query 분리 | 검색용 `cleaned_raw_query`와 분위기용 `soft_preference_query` 생성 |
| unsupported 분리 | 숙박 가격, 예약 가능 여부, 실시간 혼잡도처럼 검색 근거로 쓰면 위험한 조건을 분리 |
| fulfilled matrix 초기화 | `evidence`, `festival`, `planning`의 초기 상태 생성 |
| 추가 질문 판단 | 필수 입력이 부족하면 Candidate Evidence로 넘기지 않고 간단한 질문 생성 |

Intent Agent가 담당하지 않는 범위:

| 비범위 | 담당 |
| --- | --- |
| 도시/장소 검색 | `Candidate_Evidence_Agent` |
| 도시 ranking과 scoring | `Candidate_Evidence_Agent` |
| 축제 날짜 검증 | `Festival_Verifier_Agent` |
| 일정 생성과 설명 | `Planner_Agent` |
| API 응답 패키징 | `Backend_Serving` |

## 4. 입력 계약

Intent Agent 입력:

```json
{
  "messages": [],
  "conversation_summary": null,
  "entryType": "chatbot",
  "country": "KR",
  "travelMonth": 6,
  "travelYear": 2026,
  "destinationId": null,
  "themes": ["sea_coast", "gourmet_retro"],
  "tripType": "2d1n",
  "includeFestivals": false,
  "naturalLanguageQuery": "바다도 보고 오래된 맛집도 가고 싶어. 너무 붐비지 않았으면 좋겠어.",
  "user_location": {
    "latitude": 37.5665,
    "longitude": 126.978
  },
  "onboardingProfile": {},
  "feedbackHistory": []
}
```

입력 우선순위:

1. 명시 UI 입력
2. 현재 턴 자연어
3. 멀티턴 요약
4. 온보딩 선호
5. 피드백 이력

명시 UI 입력과 자연어가 충돌하면 현재 턴 자연어가 더 구체적인 경우에만 override한다. 확신이 낮으면 `needs_clarification=true`를 반환한다.

## 5. 출력 계약

Intent Agent의 핵심 출력은 Candidate Evidence Agent 입력이다.

```json
{
  "needs_clarification": false,
  "clarifying_question": null,
  "extracted_inputs": {
    "country": "KR",
    "travelMonth": 6,
    "travelYear": 2026,
    "tripType": "2d1n",
    "destinationId": null,
    "includeFestivals": false
  },
  "candidate_evidence_input": {
    "country": "KR",
    "travelMonth": 6,
    "travelYear": 2026,
    "tripType": "2d1n",
    "destinationId": null,
    "active_required_themes": ["바다·해안", "미식·노포"],
    "cleaned_raw_query": "바다를 보고 오래된 지역 맛집도 가고 싶다",
    "soft_preference_query": "너무 붐비지 않는 조용한 분위기",
    "unsupported_conditions": [],
    "user_location": {
      "latitude": 37.5665,
      "longitude": 126.978
    },
    "includeFestivals": false
  },
  "active_required_themes": ["바다·해안", "미식·노포"],
  "soft_preferences": ["quiet"],
  "unsupported_conditions": [],
  "fulfilled_matrix": {
    "evidence": "X",
    "festival": "N/A",
    "planning": "X"
  },
  "handoff_notes": []
}
```

`candidate_evidence_input`은 `candidate_evidence_agent.md`의 입력 계약을 우선한다.

향후 `anchor_fixed`와 `festival_selection` 모드를 Candidate Evidence 정본에 완전히 반영하면 아래 필드를 선택 확장으로 추가한다.

```json
{
  "execution_mode": "city_discovery",
  "fixed_city_id": null,
  "city_anchor": null
}
```

## 6. 필드 생성 규칙

| 필드 | 생성 규칙 |
| --- | --- |
| `country` | UI 입력 우선. 자연어만 있을 경우 명확한 국가 표현이 없으면 추가 질문 |
| `travelMonth` | UI 입력 우선. 계절 표현만 있으면 월로 확정하지 말고 필요 시 추가 질문 |
| `travelYear` | 요청값 우선. 없으면 현재 MVP 기본값 2026 |
| `tripType` | UI 입력 우선. 없으면 추가 질문 또는 서비스 기본값 정책에 따름 |
| `destinationId` | 지도 마커/명시 도시 anchor가 있으면 유지 |
| `includeFestivals` | UI 입력 또는 자연어의 축제·행사 의도로 결정 |
| `active_required_themes` | API theme code를 raw theme label로 변환. 최대 3개 기본 |
| `cleaned_raw_query` | 검색 가능한 장소·테마·활동 맥락을 자연어로 보존 |
| `soft_preference_query` | 조용함, 감성, 산책, 전망, 덜 붐빔 같은 분위기 선호 |
| `unsupported_conditions` | 숙소 가격/예약, 실시간 영업, 실시간 혼잡, 보장 불가 조건 |
| `fulfilled_matrix.festival` | `includeFestivals=true`이면 `X`, 아니면 `N/A` |

## 7. 테마 매핑

| API code | Candidate Evidence label |
| --- | --- |
| `sea_coast` | `바다·해안` |
| `nature_trekking` | `자연·트레킹` |
| `gourmet_retro` | `미식·노포` |
| `history_tradition` | `역사·전통` |
| `art_sense` | `예술·감성` |
| `healing_spa` | `온천·휴양` |
| `festival_event` | `축제·이벤트` |

`festival_event`는 장소 검색 테마로 직접 섞기보다 `includeFestivals=true`와 Festival Verifier 경로로 연결한다. 단, 사용자가 축제 자체를 목적지 anchor로 요청한 경우에는 `festival_selection` 후보로 handoff note를 남긴다.

## 8. Prompt Template

현재 단계 기본 프롬프트:

```text
You are Intent_Agent for Lovv, a small-city travel recommendation system.

Your only job is to transform the current user turn, UI fields, onboarding profile, and conversation summary into the input JSON required by Candidate_Evidence_Agent.

Use model behavior suitable for deterministic extraction:
- Do not recommend destinations.
- Do not search.
- Do not score cities or places.
- Do not create itinerary text.
- Do not invent missing country, month, trip type, destination, or theme.
- If required fields are missing or ambiguous, set needs_clarification=true and ask one short Korean question.

Output JSON only.

Candidate_Evidence_Agent input fields:
- country: "KR" or "JP"
- travelMonth: integer 1-12
- travelYear: integer or null; use 2026 as MVP default only when the request does not specify a year
- tripType: "daytrip" | "2d1n" | "3d2n" | "4d3n" | "5d4n"
- destinationId: string or null
- active_required_themes: Korean theme labels
- cleaned_raw_query: Korean sentence preserving searchable travel intent
- soft_preference_query: Korean sentence for mood/preferences, or empty string
- unsupported_conditions: string array
- user_location: object or null
- includeFestivals: boolean

Theme mapping:
- sea_coast -> 바다·해안
- nature_trekking -> 자연·트레킹
- gourmet_retro -> 미식·노포
- history_tradition -> 역사·전통
- art_sense -> 예술·감성
- healing_spa -> 온천·휴양
- festival_event -> 축제·이벤트

Classification rules:
- Required themes are hard constraints for Candidate Evidence.
- Soft preferences are not hard filters; place them in soft_preference_query.
- Lodging price, room availability, real-time crowding, real-time opening status, guaranteed parking, and reservation guarantees are unsupported unless an explicit tool exists. Put them in unsupported_conditions.
- If user asks for festivals, set includeFestivals=true. Do not put festivals into normal place search unless the theme code is explicitly needed for handoff notes.
- Onboarding profile is a default preference. The current user turn overrides it when clear.
- Keep cleaned_raw_query natural and searchable. Remove unsupported conditions but preserve useful travel intent.

Return this JSON shape:
{
  "needs_clarification": boolean,
  "clarifying_question": string | null,
  "extracted_inputs": {...},
  "candidate_evidence_input": {...},
  "active_required_themes": [...],
  "soft_preferences": [...],
  "unsupported_conditions": [...],
  "fulfilled_matrix": {
    "evidence": "X" | "N/A",
    "festival": "X" | "N/A",
    "planning": "X" | "N/A"
  },
  "handoff_notes": [...]
}
```

## 9. Clarification Policy

추가 질문은 Candidate Evidence 입력을 만들 수 없을 때만 생성한다.

질문이 필요한 경우:

- `country`가 없음
- `travelMonth`가 없음
- `tripType`이 없음
- theme가 없고 자연어에서도 추론하기 어려움
- `destinationId`와 자연어의 명시 도시가 충돌
- 축제 중심 요청인데 월 또는 연도가 없어 날짜 검증을 할 수 없음

질문 원칙:

- 한국어 한 문장
- 한 번에 가장 중요한 1개만 질문
- 후보를 2-3개로 좁힐 수 있으면 제안형 질문 사용

예:

```json
{
  "needs_clarification": true,
  "clarifying_question": "여행하실 월을 알려주실 수 있을까요? 축제 포함 여부와 계절 후보를 함께 맞춰볼게요."
}
```

## 10. Validation

Intent Agent 출력은 Supervisor로 넘기기 전에 결정적으로 검증한다.

| 검증 | 기준 |
| --- | --- |
| JSON parse | JSON만 반환 |
| schema | `candidate_evidence_input` 필수 필드 존재 |
| country | `KR` 또는 `JP` |
| month | 1-12 |
| tripType | 허용 enum |
| theme label | canonical label만 사용 |
| unsupported | 숙박·실시간 조건이 검색 query에 섞이지 않음 |
| matrix | `X`, `O`, `△`, `N/A` 외 값 없음 |

검증 실패 시 같은 모델을 1회 재호출하되, 두 번째도 실패하면 안전한 clarification으로 종료한다.

## 11. 테스트 기준

| ID | 유형 | 입력 | 기대 결과 |
| --- | --- | --- | --- |
| IN-N01 | UI 중심 | `themes=["sea_coast"]`, 월/일정 명시 | Candidate Evidence input 정상 생성 |
| IN-N02 | 자연어 soft | “조용하고 덜 붐비는 바다” | `바다·해안`은 required, 조용함은 `soft_preference_query` |
| IN-N03 | 축제 포함 | “10월 축제도 보고 싶어” | `includeFestivals=true`, `festival=X` |
| IN-N04 | 지도 진입 | `entryType=map_marker`, `destinationId` 존재 | anchor 조건 유지 |
| IN-F01 | 월 누락 | 축제 요청 + 월 없음 | clarification |
| IN-F02 | unsupported | “오션뷰 숙소 싸게 예약 가능한 곳” | 숙소 조건은 `unsupported_conditions` |
| IN-F03 | 충돌 | UI는 KR, 자연어는 일본 | clarification 또는 현재 턴 override 근거 note |
| IN-F04 | 테마 과다 | 4개 이상 테마 | 최대 3개로 제한하고 handoff note |

## 12. Open Decisions

| 항목 | 결정 필요 |
| --- | --- |
| 기본 `tripType` | 누락 시 서비스 기본값을 둘지, 항상 질문할지 |
| 계절 표현 매핑 | “가을”, “여름 휴가”를 월로 확정할지 범위로 둘지 |
| `festival_event` 처리 | 축제 선택 모드와 일반 테마 검색의 분리 기준 |
| 온보딩 override threshold | 현재 턴 자연어가 장기 선호를 덮는 확신 기준 |

## 13. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v1.1 | 2026-06-12 | llm | 특정 LLM 모델 고정 문구를 제거하고 Bedrock Converse adapter 기반 모델 비종속 정책으로 정리 |
| v1.0 | 2026-06-12 | llm | Candidate Evidence 입력 생성을 목표로 하는 Intent Agent 상세 정본과 기본 프롬프트 작성 |
