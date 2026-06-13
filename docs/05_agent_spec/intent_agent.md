# Intent Agent 명세서

> 문서 버전: v1.7
> 문서 상태: Review / Intent Agent 상세 정본
> 작성일: 2026-06-12
> 기준 문서: `05_agent_spec.md`, `langgraph_flow.md`, `candidate_evidence_agent.md`, `user_raw_query_flow.md`, `recommendation_flow.md`, `../07_api_spec/07_api_spec.md`

## 1. 문서 목적

본 문서는 Lovv 추천 Agent의 entry node인 `Intent_Agent` 상세 정본이다.

현재 단계에서 Intent Agent의 핵심 목표는 복잡한 계획을 수행하는 것이 아니라, `candidate_evidence_agent.md`의 입력 계약을 안정적으로 만들어 주는 것이다. 즉, API structured input을 정본으로 받아 Candidate Evidence Agent가 바로 사용할 수 있는 구조화 JSON으로 정규화하고, `naturalLanguageQuery`에서는 보조 선호·제외 조건·지원 불가 조건·명시적 변경 요청 신호만 추출한다.

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
| 멀티턴 요약 해석 | 최근 사용자 발화와 `conversation_summary`에서 보조 선호, 제외 조건, 변경 요청 신호를 재증류 |
| API structured input 정규화 | `entryType`, `country`, `travelMonth`, `tripType`, `destinationId`, `themes` 등 명시 API 입력을 현재 요청의 정본으로 사용 |
| 온보딩 병합 | 장기 선호는 soft preference 기본값으로만 사용하고 API core field를 덮어쓰지 않음 |
| Candidate Evidence 입력 생성 | `candidate_evidence_input` JSON 생성 |
| soft/raw query 분리 | 검색용 `cleaned_raw_query`와 분위기용 `soft_preference_query` 생성 |
| 입력 충돌 감지 | 자연어가 API core field와 충돌하면 조용히 override하지 않고 clarification 또는 handoff note로 기록 |
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
  "themes": ["sea_coast", "food_local"],
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

### 4.1 API structured input 정본 원칙

현재 Product/API 흐름에서는 `country`, `travelMonth`, `tripType`, canonical travel `themes`가 이미 API structured input으로 전달된다. 이 값들은 자연어에서 다시 추론하거나 재분류할 대상이 아니다.

Core field 정본 기준:

1. API structured input: `entryType`, `country`, `travelMonth`, `travelYear`, `tripType`, `destinationId`, `themes`, `includeFestivals`, `userLocation`.
2. Adapter-normalized legacy fields: 기존 클라이언트가 `user_location` 또는 legacy theme code를 보낸 경우 API adapter 또는 Intent Agent boundary에서 canonical field로 정규화한다.
3. `naturalLanguageQuery`: core field를 새로 파싱하지 않고, soft preference, 제외 조건, unsupported condition, 명시적 변경 요청 신호만 추출한다.
4. `conversation_summary`, `onboardingProfile`, `feedbackHistory`: 현재 API structured input이 비어 있지 않은 core field를 덮어쓰지 않고, 보조 선호와 설명 맥락으로만 사용한다.

자연어가 API structured input과 충돌하면 Intent Agent는 조용히 override하지 않는다. 예를 들어 API는 `country="KR"`인데 자연어에 "일본으로 바꿔줘"가 있거나, API는 `travelMonth=10`인데 "11월로 변경"이 있으면 `needs_clarification=true` 또는 `handoff_notes`에 변경 요청을 기록해 프론트/오케스트레이터가 structured input을 갱신하도록 한다.

API 계약상 축제 포함 여부는 `themes`가 아니라 별도 boolean 필드인 `includeFestivals`로 전달된다. `themes`에는 `/themes/onboarding-options`가 제공하는 canonical travel theme만 들어와야 한다. 과거 UI 또는 legacy adapter가 `festival_event` 같은 값을 `themes`에 넣어 전달한 경우 Intent Agent는 이를 canonical theme으로 취급하지 않고 `includeFestivals=true`로 정규화한 뒤 `themes`/`active_required_themes`에서는 제거한다.

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

`anchored_place_search`는 Candidate Evidence 정본의 공식 고정 도시 mode다. Intent Agent는 API의 `destinationId` 또는 지도 마커 입력이 있으면 아래 필드를 선택 확장으로 전달할 수 있다.

`destinationId`와 `includeFestivals`는 서로 배타적이지 않다. 고정 도시 진입에서도 사용자가 축제 포함을 선택할 수 있으므로, Intent Agent는 `destinationId`가 있다는 이유로 `includeFestivals`를 끄거나 제거하지 않는다.

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
| `country` | API structured input을 정본으로 사용. 자연어에서 재추론하지 않으며, 누락 시 추가 질문 |
| `travelMonth` | API structured input을 정본으로 사용. 자연어 계절 표현으로 월을 확정하지 않으며, 누락 시 추가 질문 |
| `travelYear` | 요청값 우선. 없으면 현재 MVP 기본값 2026 |
| `tripType` | API structured input을 정본으로 사용. 누락 시 추가 질문 또는 서비스 기본값 정책에 따름 |
| `destinationId` | 지도 마커/명시 도시 anchor가 있으면 유지. `includeFestivals=true`와 함께 전달될 수 있음 |
| `includeFestivals` | API `includeFestivals` 입력을 우선 사용. 자연어의 축제·행사 의도는 명시적 변경 요청 신호로 기록하고, legacy `themes=["festival_event"]`가 들어오면 `true`로 정규화 |
| `active_required_themes` | API `themes`의 canonical travel theme code를 Candidate Evidence label로 변환. `festival_event`나 `축제·이벤트`는 포함하지 않음 |
| `cleaned_raw_query` | 검색 가능한 장소·테마·활동 맥락을 자연어로 보존 |
| `soft_preference_query` | 조용함, 감성, 산책, 전망, 덜 붐빔 같은 분위기 선호 |
| `unsupported_conditions` | 숙소 가격/예약, 실시간 영업, 실시간 혼잡, 보장 불가 조건 |
| `fulfilled_matrix.festival` | `includeFestivals=true`이면 `X`, 아니면 `N/A` |

## 7. 테마 매핑

| API code | Candidate Evidence label |
| --- | --- |
| `sea_coast` | `바다·해안` |
| `nature_trekking` | `자연·트레킹` |
| `food_local` | `미식·노포` |
| `history_tradition` | `역사·전통` |
| `art_sense` | `예술·감성` |
| `healing_rest` | `온천·휴양` |

`festival_event`는 현재 API 정본의 canonical travel theme이 아니다. legacy 입력에서 발견되면 `includeFestivals=true`로 정규화하고 `active_required_themes`에는 넣지 않는다. 사용자가 축제 자체를 목적지처럼 요청한 경우에도 별도 축제 선택 mode를 만들지 않고, `includeFestivals` 변경 요청 또는 handoff note로만 남긴다.

## 8. Prompt Template

현재 단계 기본 프롬프트는 한국어로 유지한다. 프롬프트 안에서도 API structured input이 정본이라는 원칙을 반복해, 자연어가 core field를 조용히 덮어쓰지 않도록 한다.

```text
당신은 Lovv 소도시 여행 추천 시스템의 Intent_Agent입니다.

당신의 유일한 역할은 API structured input, naturalLanguageQuery, 온보딩 프로필, 대화 요약을 Candidate_Evidence_Agent가 사용할 입력 JSON으로 정규화하는 것입니다.

가장 중요한 원칙:
- country, travelMonth, travelYear, tripType, destinationId, canonical travel themes, includeFestivals, userLocation은 API structured input을 정본으로 사용합니다.
- naturalLanguageQuery에서 country, travelMonth, tripType, destinationId, canonical travel themes를 새로 추론하거나 덮어쓰지 마세요.
- API structured input에 core field가 없으면 naturalLanguageQuery로 채우지 말고 needs_clarification=true를 반환하세요.
- naturalLanguageQuery는 soft preference, 제외 조건, unsupported condition, 명시적 변경 요청 신호를 추출하는 데만 사용합니다.
- naturalLanguageQuery가 API structured input과 충돌하면 core field를 조용히 override하지 말고 clarification 또는 handoff_notes에 변경 요청으로 기록하세요.

결정적 추출 규칙:
- 목적지를 추천하지 마세요.
- 검색하지 마세요.
- 도시나 장소를 scoring하지 마세요.
- 일정 본문을 생성하지 마세요.
- 출력은 JSON만 반환하세요.
- 필수 structured input이 누락되었거나 충돌이 있으면 한국어 한 문장으로 clarifying_question을 작성하세요.

Candidate_Evidence_Agent 입력 필드:
- country: "KR" 또는 "JP"
- travelMonth: 1-12 정수
- travelYear: 정수 또는 null. 요청에 연도가 없으면 MVP 기본값 2026 사용
- tripType: "daytrip" | "2d1n" | "3d2n" | "4d3n" | "5d4n"
- destinationId: 문자열 또는 null
- active_required_themes: Candidate Evidence가 사용하는 한국어 테마 label 배열
- cleaned_raw_query: 검색 가능한 여행 의도를 보존한 한국어 문장
- soft_preference_query: 분위기·취향 선호를 담은 한국어 문장. 없으면 빈 문자열
- unsupported_conditions: 지원 불가 조건 문자열 배열
- user_location: API userLocation을 내부 snake_case로 정규화한 객체 또는 null
- includeFestivals: API includeFestivals를 기준으로 한 boolean

테마 매핑:
- sea_coast -> 바다·해안
- nature_trekking -> 자연·트레킹
- food_local -> 미식·노포
- history_tradition -> 역사·전통
- art_sense -> 예술·감성
- healing_rest -> 온천·휴양

분류 규칙:
- API themes는 Candidate Evidence의 hard constraint입니다.
- includeFestivals는 themes가 아니라 별도 boolean입니다.
- festival_event 또는 축제·이벤트를 일반 travel theme으로 취급하지 마세요.
- legacy themes에 festival_event가 있으면 includeFestivals=true로 정규화하되 active_required_themes에서는 제거하고 handoff_notes에 남기세요.
- 자연어에서 축제 포함/제외 의도가 보이지만 API includeFestivals와 다르면 값을 덮어쓰지 말고 변경 요청으로 기록하세요.
- soft preference는 hard filter가 아닙니다. soft_preference_query에 넣으세요.
- 숙소 가격, 객실 예약 가능 여부, 실시간 혼잡도, 실시간 영업 여부, 주차 보장, 예약 보장처럼 현재 tool이 없는 조건은 unsupported_conditions에 넣으세요.
- 온보딩 프로필은 기본 soft preference로만 사용합니다. API structured core field를 덮어쓰지 마세요.
- cleaned_raw_query는 자연스럽고 검색 가능한 한국어 문장으로 유지하세요. 지원 불가 조건은 제거하되, 검색 가능한 여행 의도는 보존하세요.

반환 JSON shape:
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

### 8.1 구조화 출력 런타임 정책

프롬프트에 `반환 JSON shape`를 적는 것은 모델을 유도하기 위한 보조 장치다. 운영 구현에서는 문자열 JSON 파싱에 의존하지 않고, Bedrock Structured Outputs를 사용해 출력 구조를 런타임에서 강제한다.

참고: [Amazon Bedrock Structured Outputs](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html)

기본 정책:

1. Intent Agent 호출은 Bedrock Converse API의 `outputConfig.textFormat`에 `json_schema`를 지정한다.
2. schema 이름은 `intent_agent_output`으로 둔다.
3. schema에는 최상위 필수 필드, enum, nullable 필드, 배열 item type, `additionalProperties=false`를 명시한다.
4. Bedrock Structured Outputs가 지원하지 않는 세부 제약은 schema에 억지로 넣지 않고 후단 business rule validation에서 처리한다. 예를 들어 `travelMonth`의 1-12 범위, `themes` 1-3개 제한, canonical theme label 검증은 Validation 단계에서 확인한다.
5. JSON Schema 강제 실패, schema 통과 후 business rule 실패, API structured input과 자연어 충돌은 fallback 대상이다. 단순 JSON parse 실패 fallback은 발생하지 않는 것을 목표로 한다.

Converse API 요청 개념 예시:

```json
{
  "outputConfig": {
    "textFormat": {
      "type": "json_schema",
      "structure": {
        "jsonSchema": {
          "name": "intent_agent_output",
          "description": "Lovv Intent Agent structured output",
          "schema": "{...JSON Schema Draft 2020-12 subset...}"
        }
      }
    }
  }
}
```

`intent_agent_output` schema는 최소한 아래 필드를 required로 둔다.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "needs_clarification",
    "clarifying_question",
    "extracted_inputs",
    "candidate_evidence_input",
    "active_required_themes",
    "soft_preferences",
    "unsupported_conditions",
    "fulfilled_matrix",
    "handoff_notes"
  ],
  "properties": {
    "needs_clarification": { "type": "boolean" },
    "clarifying_question": {
      "anyOf": [
        { "type": "string" },
        { "type": "null" }
      ]
    },
    "extracted_inputs": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "country",
        "travelMonth",
        "travelYear",
        "tripType",
        "destinationId",
        "includeFestivals"
      ],
      "properties": {
        "country": { "type": "string", "enum": ["KR", "JP"] },
        "travelMonth": { "type": "integer" },
        "travelYear": {
          "anyOf": [
            { "type": "integer" },
            { "type": "null" }
          ]
        },
        "tripType": {
          "type": "string",
          "enum": ["daytrip", "2d1n", "3d2n", "4d3n", "5d4n"]
        },
        "destinationId": {
          "anyOf": [
            { "type": "string" },
            { "type": "null" }
          ]
        },
        "includeFestivals": { "type": "boolean" }
      }
    },
    "candidate_evidence_input": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "country",
        "travelMonth",
        "travelYear",
        "tripType",
        "destinationId",
        "active_required_themes",
        "cleaned_raw_query",
        "soft_preference_query",
        "unsupported_conditions",
        "user_location",
        "includeFestivals"
      ],
      "properties": {
        "country": { "type": "string", "enum": ["KR", "JP"] },
        "travelMonth": { "type": "integer" },
        "travelYear": {
          "anyOf": [
            { "type": "integer" },
            { "type": "null" }
          ]
        },
        "tripType": {
          "type": "string",
          "enum": ["daytrip", "2d1n", "3d2n", "4d3n", "5d4n"]
        },
        "destinationId": {
          "anyOf": [
            { "type": "string" },
            { "type": "null" }
          ]
        },
        "active_required_themes": {
          "type": "array",
          "items": { "type": "string" }
        },
        "cleaned_raw_query": { "type": "string" },
        "soft_preference_query": { "type": "string" },
        "unsupported_conditions": {
          "type": "array",
          "items": { "type": "string" }
        },
        "user_location": {
          "anyOf": [
            {
              "type": "object",
              "additionalProperties": false,
              "required": ["latitude", "longitude"],
              "properties": {
                "latitude": { "type": "number" },
                "longitude": { "type": "number" }
              }
            },
            { "type": "null" }
          ]
        },
        "includeFestivals": { "type": "boolean" }
      }
    },
    "active_required_themes": {
      "type": "array",
      "items": { "type": "string" }
    },
    "soft_preferences": {
      "type": "array",
      "items": { "type": "string" }
    },
    "unsupported_conditions": {
      "type": "array",
      "items": { "type": "string" }
    },
    "fulfilled_matrix": {
      "type": "object",
      "additionalProperties": false,
      "required": ["evidence", "festival", "planning"],
      "properties": {
        "evidence": { "type": "string", "enum": ["X", "O", "△", "N/A"] },
        "festival": { "type": "string", "enum": ["X", "O", "△", "N/A"] },
        "planning": { "type": "string", "enum": ["X", "O", "△", "N/A"] }
      }
    },
    "handoff_notes": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

대안으로 tool-call 기반 구현을 선택하는 경우에는 외부 작업을 수행하지 않는 synthetic tool인 `emit_intent_agent_output`을 정의하고, tool definition에 동일한 input schema와 `strict=true`를 부여한다. 다만 Intent Agent는 도구 실행보다 구조화 JSON 생성이 목적이므로 기본값은 `outputConfig.textFormat` 방식이다.

fallback 최소화 원칙:

| 실패 지점 | 처리 |
| --- | --- |
| JSON parse 실패 | Structured Outputs 사용 시 원칙적으로 제거해야 하는 실패 유형 |
| schema compile 또는 schema validation 오류 | 배포 전 schema 검증으로 차단. 런타임에서는 safe clarification 또는 시스템 오류로 기록 |
| business rule validation 실패 | 1회 repair 요청 또는 clarification |
| API structured input 누락 | 자연어로 채우지 않고 clarification |
| API structured input과 자연어 충돌 | core field override 금지. clarification 또는 `handoff_notes`로 변경 요청 기록 |

## 9. Clarification Policy

추가 질문은 Candidate Evidence 입력을 만들 수 없을 때만 생성한다.

질문이 필요한 경우:

- API structured input에 `country`가 없음
- API structured input에 `travelMonth`가 없음
- API structured input에 `tripType`이 없음
- API structured input에 canonical travel `themes`가 없음
- `destinationId`와 자연어의 명시 도시 변경 요청이 충돌
- 자연어가 `country`, `travelMonth`, `tripType`, `themes` 변경을 명시하지만 structured input이 아직 갱신되지 않음
- 축제 중심 요청인데 월 또는 연도가 없어 날짜 검증을 할 수 없음
- legacy `festival_event`만 있고 다른 travel theme이 없으면 축제 seed의 theme pool이 비므로 사용자에게 여행 테마를 추가로 묻는다

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

Intent Agent 출력은 Supervisor로 넘기기 전에 결정적으로 검증한다. 런타임은 Bedrock Structured Outputs schema를 1차 강제 수단으로 사용하고, 아래 검증은 schema가 표현하지 못하는 business rule과 Agent 계약을 확인한다.

| 검증 | 기준 |
| --- | --- |
| structured output | Bedrock `outputConfig.textFormat` schema를 통과한 응답 |
| schema | `intent_agent_output` 필수 필드와 nested object 구조 존재 |
| country | `KR` 또는 `JP` |
| month | 1-12 |
| tripType | 허용 enum |
| theme label | canonical label만 사용 |
| structured source | `country`, `travelMonth`, `tripType`, `active_required_themes`가 자연어 추론이 아니라 API structured input에서 왔는지 확인 |
| unsupported | 숙박·실시간 조건이 검색 query에 섞이지 않음 |
| matrix | `X`, `O`, `△`, `N/A` 외 값 없음 |

schema 이전 단계 실패는 배포 전 schema 검증 또는 시스템 오류로 처리한다. schema 통과 후 business rule validation이 실패하면 같은 모델에 1회 repair 요청을 보내되, 두 번째도 실패하면 안전한 clarification으로 종료한다.

## 11. 테스트 기준

| ID | 유형 | 입력 | 기대 결과 |
| --- | --- | --- | --- |
| IN-N01 | UI 중심 | `themes=["sea_coast"]`, 월/일정 명시 | Candidate Evidence input 정상 생성 |
| IN-N02 | 자연어 soft | `themes=["sea_coast"]` + “조용하고 덜 붐비는 곳” | `바다·해안`은 API theme에서 required로 변환, 조용함은 `soft_preference_query` |
| IN-N03 | 축제 포함 | `travelMonth=10`, `themes=["food_local"]`, `includeFestivals=true` | `active_required_themes=["미식·노포"]`, `includeFestivals=true`, `festival=X` |
| IN-N04 | 지도 진입 | `entryType=map_marker`, `destinationId` 존재 | anchor 조건 유지 |
| IN-N05 | 지도 진입 + 축제 포함 | `destinationId` 존재, `includeFestivals=true` | anchor 조건과 `includeFestivals=true`를 모두 유지 |
| IN-F01 | 월 누락 | 축제 요청 + 월 없음 | clarification |
| IN-F02 | unsupported | “오션뷰 숙소 싸게 예약 가능한 곳” | 숙소 조건은 `unsupported_conditions` |
| IN-F03 | 충돌 | API는 `country="KR"`, 자연어는 “일본으로 바꿔줘” | core field를 조용히 override하지 않고 clarification 또는 변경 요청 handoff note |
| IN-F04 | 테마 과다 | 4개 이상 테마 | 최대 3개로 제한하고 handoff note |
| IN-F05 | legacy 축제 theme 단독 | `themes=["festival_event"]`, `includeFestivals=false` | `includeFestivals=true`로 정규화하되 travel theme 추가 질문 |
| IN-F06 | structured core 누락 | `naturalLanguageQuery="10월에 바다 보러 당일치기"`이나 `travelMonth`, `tripType`, `themes` 누락 | 자연어만으로 core field를 확정하지 않고 structured input 보완 질문 |

## 12. Open Decisions

| 항목 | 결정 필요 |
| --- | --- |
| 기본 `tripType` | 누락 시 서비스 기본값을 둘지, 항상 질문할지 |
| 계절 표현 매핑 | API structured input이 비어 있을 때 자연어 계절 표현을 변경 요청 신호로만 둘지, 별도 UI 보완 질문으로 연결할지 |
| 온보딩 override threshold | 현재 턴 자연어가 장기 soft preference를 덮는 확신 기준 |

## 13. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v1.7 | 2026-06-13 | llm | `destinationId`와 `includeFestivals`가 배타적이지 않음을 명시하고, 고정 도시 진입에서도 축제 포함 값을 유지하도록 테스트 기준 추가 |
| v1.6 | 2026-06-13 | llm | 고정 도시 mode명을 `anchored_place_search`로 통일하고 별도 축제 선택 mode 잔여를 제거 |
| v1.5 | 2026-06-13 | llm | Bedrock Structured Outputs 기반 구조화 출력 강제 정책, JSON Schema 개념 예시, fallback 최소화 원칙 추가 |
| v1.4 | 2026-06-13 | llm | Prompt Template을 한국어로 전환하고 API structured input 정본 원칙, 자연어 충돌 처리, `includeFestivals` 덮어쓰기 금지를 프롬프트 예시에 반영 |
| v1.3 | 2026-06-13 | llm | `country`/`travelMonth`/`tripType`/canonical travel `themes`는 API structured input을 정본으로 사용하고 자연어에서 재파싱하지 않도록 책임 경계 명시 |
| v1.2 | 2026-06-13 | llm | API 계약에 맞춰 축제 포함을 `includeFestivals` 전용 입력으로 정리하고 `festival_event`를 canonical theme mapping에서 제거 |
| v1.1 | 2026-06-12 | llm | 특정 LLM 모델 고정 문구를 제거하고 Bedrock Converse adapter 기반 모델 비종속 정책으로 정리 |
| v1.0 | 2026-06-12 | llm | Candidate Evidence 입력 생성을 목표로 하는 Intent Agent 상세 정본과 기본 프롬프트 작성 |
