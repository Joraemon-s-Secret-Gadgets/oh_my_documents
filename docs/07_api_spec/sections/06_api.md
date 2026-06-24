# 6. 추천 API

| Method | Path | Auth | 담당 Lambda | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/recommendations` | Optional | `AgentCore-Function` | 추천 생성 |
| GET | `/recommendations/{recommendationId}` | Optional | `AgentCore-Function` | 짧은 수명의 추천 결과 조회 |
| POST | `/recommendations/{recommendationId}/alternatives/weather` | Optional | `AgentCore-Function` | 기상 악화 대체 일정 조회 |
| POST | `/agent/answer` | Optional | `AgentCore-Function` | 대화 원문 저장 없는 단일 턴 AI 답변 생성 |

## 6.1 `POST /recommendations`

**Request**

```json
{
  "entryType": "map_marker",
  "country": "JP",
  "travelMonth": 10,
  "travelYear": 2026,
  "destinationId": "uuid",
  "themes": ["art_sense"],
  "tripType": "2d1n",
  "includeFestivals": true,
  "naturalLanguageQuery": "가을에 감성적인 일본 소도시 추천해줘",
  "user_location": {
    "latitude": 35.6812,
    "longitude": 139.7671
  }
}
```

**Response 201**

```json
{
  "recommendationId": "uuid",
  "destination": {
    "destinationId": "uuid",
    "name": "가나자와",
    "country": "JP"
  },
  "itinerary": {
    "tripType": "2d1n",
    "days": [
      {
        "day": 1,
        "items": [
          {
            "timeOfDay": "morning",
            "title": "히가시차야 거리 산책",
            "reason": "도보 이동이 쉽고 예술·감성 선호와 맞습니다."
          }
        ]
      }
    ]
  },
  "explainability": {
    "matchedConditions": ["art_sense", "travelMonth:10"],
    "recommendationReasons": [
      "예술·감성 테마 장소가 일정에 충분히 포함됩니다.",
      "10월 계절 적합도와 도보 이동성이 좋습니다."
    ],
    "itineraryFlowReason": "오전에는 대표 거리 산책, 오후에는 실내 문화 콘텐츠를 배치해 이동 부담을 낮췄습니다.",
    "confidence": 0.86,
    "user_notice": "숙소 가격과 예약 가능 여부는 실시간 확정 정보가 아니므로 검색 링크에서 확인해야 합니다."
  },
  "festivalDateVerifications": [
    {
      "festivalId": "uuid",
      "dateStatus": "confirmed",
      "startDate": "2026-10-10",
      "endDate": "2026-10-12",
      "sourceUrl": "https://example.official.jp",
      "confidence": 0.91
    }
  ],
  "links": {
    "map": "https://maps.google.com/...",
    "staySearch": "https://..."
  }
}
```

추천 API 계약 기준:

| 필드 | 방향 | 설명 |
| --- | --- | --- |
| `naturalLanguageQuery` | Request | 현재 턴 자연어 의도. Agent는 반영 가능한 조건과 `unsupported_conditions`를 분리한다. |
| `user_location` | Request | 거리 기반 1차 필터 기준 좌표. 권한이 없으면 생략 가능하다. |
| `recommendationReasons` | Response | 조건 충족, 도시 특성, 일정 가능성 기준의 추천 근거 배열 |
| `confidence` | Response | 데이터 결측, 검증 상태, 폴백 적용 여부를 반영한 신뢰도 |
| `user_notice` | Response | 숙박 가격·예약 가능 여부처럼 확정 추천 근거로 쓸 수 없는 조건 안내 |
| `festivalDateVerifications` | Response | 일정 배치 또는 후보 축제의 해당 연도 날짜 검증 결과 |

AgentCore API 운영 기준:

| 항목 | 기준 |
| --- | --- |
| 저장 정책 | 대화 원문은 저장하지 않는다. 추천 결과는 사용자가 `/me/itineraries` 저장 API를 호출할 때만 계정 데이터로 저장한다. |
| Timeout | 사용자 대면 동기 호출은 29초 내외 완료를 목표로 한다. 장시간 추론이 필요한 경우 비동기 작업 상태 조회 또는 스트리밍 API로 분리한다. |
| 의존성 | LangChain, OpenAI SDK, Boto3, Bedrock SDK 등 무거운 AI 의존성은 `AgentCore-Function`에만 포함한다. |
| 실패 응답 | 모델 호출 실패, timeout, rate limit은 공통 오류 형식을 사용하되 사용자에게 재시도 가능 여부를 명확히 전달한다. |

## 6.2 `POST /agent/answer`

저장 없는 단일 턴 AI 응답 생성 API다. 챗봇 화면에서 사용자의 현재 질문에 답변을 생성하되, 대화 원문을 서버에 영구 저장하지 않는다.

**Request**

```json
{
  "message": "가을에 조용한 일본 소도시 추천해줘",
  "context": {
    "country": "JP",
    "travelMonth": 10,
    "themes": ["healing", "art_sense"]
  }
}
```

**Response 200**

```json
{
  "answer": "10월에는 가나자와가 잘 맞습니다. 전통 거리와 미술관 콘텐츠가 함께 있고, 대도시보다 이동 동선이 단순합니다.",
  "suggestedActions": [
    {
      "type": "create_recommendation",
      "label": "가나자와 일정 만들기",
      "payload": {
        "destinationId": "uuid"
      }
    }
  ],
  "modelUsage": {
    "latencyMs": 3200
  }
}
```
