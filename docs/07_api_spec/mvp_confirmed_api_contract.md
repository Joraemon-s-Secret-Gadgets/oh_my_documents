# 로브 (Lovv) MVP 확정 API 구축 명세서

> 문서 버전: v0.1
> 문서 상태: 확정 범위 (MVP Build Contract)
> 기준 문서: API 명세서 v0.2, 기술 명세서 v0.3, Product API 전환 보강 명세서 v0.1
> 대표 문서: [07_api_spec.md](./07_api_spec.md)

# 1. 문서 목적

본 문서는 AWS SAM 백엔드 구현 시 우선 구축할 MVP 확정 API만 분리해 정리한다.
기존 대표 API 명세서인 `07_api_spec.md`를 대체하지 않으며, 기존 문서에 이미 작성된 내용을 수정하지 않고 MVP 구현 범위를 명확히 하기 위한 보조 문서다.

프론트엔드와 백엔드는 이 문서의 endpoint 목록과 request/response 필드를 기준으로 MVP 구현 범위를 맞춘다.
후속 Product 기능은 `product_api_transition_supplement.md`에 후보로 남기고, 구현 확정 시 별도 반영한다.

# 2. 공통 API 기준

| 항목 | 확정 기준 |
| --- | --- |
| Base URL | `/api/v1` |
| Content-Type | `application/json; charset=utf-8` |
| 인증 헤더 | `Authorization: Bearer <accessToken>` |
| 날짜 형식 | ISO 8601 |
| ID 형식 | UUID 권장 |
| JSON 필드 | `camelCase` 사용 |
| 인증 구분 | `Public`, `Optional`, `User` |

공통 오류 응답은 대표 API 명세서의 `error.code`, `error.message`, `error.details` 구조를 따른다.

# 3. AWS SAM Lambda 분리 기준

| 담당 Lambda | API 범위 | 책임 |
| --- | --- | --- |
| `Auth-Function` | `/auth/*`, `/auth/session`, `/me/preferences`, `/me/itineraries`, `/me/feedback` | Google/Kakao 로그인, JWT 발급·검증, 사용자 세션, 선호, 저장 일정, 피드백 |
| `Map-Function` | `/themes/onboarding-options`, `/destinations/*` | 테마 선택지, 지도 마커, 소도시 상세 콘텐츠, DB/S3 기반 읽기 API |
| `AgentCore-Function` | `/recommendations`, `/recommendations/{recommendationId}`, `/agent/answer` | LLM 호출, 추천 생성, 단일 턴 AI 답변, 대화 원문 저장 없는 순수 추론 |

인증·지도 API에는 LangChain, OpenAI SDK, Bedrock SDK 등 무거운 AI 의존성을 포함하지 않는다.
AgentCore API는 사용자 대면 동기 응답 기준으로 29초 내외 완료를 목표로 한다.

# 4. MVP 확정 Endpoint 목록

## 4.1 Auth-Function

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| POST | `/auth/google` | Public | Google 간편 로그인 token 검증 및 서비스 JWT 발급 |
| POST | `/auth/kakao` | Public | Kakao 간편 로그인 token 검증 및 서비스 JWT 발급 |
| POST | `/auth/logout` | User | 현재 세션 로그아웃 |
| GET | `/auth/me` | User | 현재 사용자와 역할 조회 |
| GET | `/auth/session` | User | 로그인 직후 화면 초기화용 세션 요약 조회 |
| GET | `/me/preferences` | User | 사용자 선호 프로필 조회 |
| PUT | `/me/preferences` | User | 온보딩 응답 저장 또는 재설정 |
| GET | `/me/itineraries` | User | 저장 일정 목록 조회 |
| POST | `/me/itineraries` | User | 추천 결과 snapshot 저장 |
| DELETE | `/me/itineraries/{itineraryId}` | User | 저장 일정 삭제 |
| POST | `/me/feedback` | User | 추천 좋아요/싫어요 저장 |

## 4.2 Map-Function

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/themes/onboarding-options` | Public | 온보딩과 필터에서 사용할 canonical theme 선택지 조회 |
| GET | `/destinations/map-markers` | Public | 초기 지도 진입용 소도시 마커 조회 |
| GET | `/destinations/{destinationId}` | Public | 마커 클릭 후 소도시 상세와 콘텐츠 조회 |

## 4.3 AgentCore-Function

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| POST | `/recommendations` | Optional | 지도 선택 또는 챗봇 조건 기반 추천 생성 |
| GET | `/recommendations/{recommendationId}` | Optional | 짧은 수명의 추천 결과 조회 |
| POST | `/agent/answer` | Optional | 대화 원문 저장 없는 단일 턴 AI 답변 생성 |

# 5. Auth-Function API 계약

## 5.1 `POST /auth/google`, `POST /auth/kakao`

**Request**

```json
{
  "providerAccessToken": "oauth-provider-token",
  "redirectUri": "https://lovv.example.com/auth/callback"
}
```

**Response 200**

```json
{
  "accessToken": "service-jwt",
  "tokenType": "Bearer",
  "expiresIn": 3600,
  "user": {
    "userId": "uuid",
    "displayName": "홍길동",
    "roles": ["R-USER"]
  }
}
```

OAuth 공급자 access token은 서버에서만 검증한다.
refresh token을 사용하는 경우 클라이언트 JavaScript 저장소에 두지 않고 HttpOnly cookie 또는 서버 세션 저장소로 관리한다.

## 5.2 `GET /auth/session`

로그인 성공 후 첫 화면 진입 시 사용자 정보, 온보딩 완료 여부, 저장 선호, 저장 일정 요약을 한 번에 반환한다.
저장 일정 상세 본문은 `/me/itineraries`에서 별도로 조회한다.

**Response 200**

```json
{
  "user": {
    "userId": "uuid",
    "displayName": "홍길동",
    "roles": ["R-USER"]
  },
  "preferences": {
    "onboardingCompleted": true,
    "countryTrack": "JP",
    "selectedCityStyle": "KANAZAWA",
    "mappedThemes": ["art_sense", "history_tradition"],
    "updatedAt": "2026-06-08T09:00:00Z"
  },
  "savedItineraries": [
    {
      "itineraryId": "uuid",
      "title": "가나자와 1박 2일 예술 산책",
      "destinationName": "가나자와",
      "country": "JP",
      "updatedAt": "2026-06-08T09:00:00Z"
    }
  ]
}
```

## 5.3 `GET /me/preferences`

**Response 200**

```json
{
  "preferenceId": "uuid",
  "onboardingCompleted": true,
  "countryTrack": "KR",
  "selectedCityStyle": "GYEONGJU",
  "mappedThemes": ["history_tradition"],
  "updatedAt": "2026-06-08T09:00:00Z"
}
```

## 5.4 `PUT /me/preferences`

**Request**

```json
{
  "countryTrack": "KR",
  "selectedCityStyle": "GYEONGJU",
  "mappedThemes": ["history_tradition"]
}
```

**Response 200**

```json
{
  "preferenceId": "uuid",
  "onboardingCompleted": true,
  "countryTrack": "KR",
  "selectedCityStyle": "GYEONGJU",
  "mappedThemes": ["history_tradition"],
  "updatedAt": "2026-06-08T09:00:00Z"
}
```

`mappedThemes`는 `GET /themes/onboarding-options`에서 내려주는 canonical `themeId`를 사용한다.

# 6. Map-Function API 계약

## 6.1 `GET /themes/onboarding-options`

프론트엔드는 이 API의 `themeId`를 온보딩, 지도 필터, 추천 요청, 피드백 저장에 동일하게 사용한다.

**Response 200**

```json
{
  "items": [
    {
      "themeId": "history_tradition",
      "label": "역사·전통",
      "shortLabel": "전통",
      "description": "오래된 거리, 전통 건축, 지역 문화유산을 먼저 봅니다.",
      "displayOrder": 1,
      "isActive": true,
      "sampleDestinations": [
        {
          "destinationId": "uuid",
          "name": "경주",
          "country": "KR",
          "imageUrl": "https://..."
        }
      ]
    }
  ]
}
```

**확정 규칙**

| 항목 | 규칙 |
| --- | --- |
| `themeId` | 백엔드 canonical enum |
| 선택 개수 | 최소 1개, 최대 3개 |
| label 변경 | 프론트 배포 없이 백엔드 데이터로 반영 가능해야 함 |

## 6.2 `GET /destinations/map-markers`

초기 MVP에서는 국가, 월, 테마 기준 필터만 확정한다.
GPS, 지도 bounds, cursor 기반 페이지네이션은 후속 후보로 둔다.

**Query**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `country` | string | No | `KR`, `JP` |
| `month` | number | No | 1~12 |
| `theme` | string | No | canonical `themeId` |

**Response 200**

```json
{
  "items": [
    {
      "destinationId": "uuid",
      "name": "가나자와",
      "country": "JP",
      "region": "이시카와현",
      "latitude": 36.5613,
      "longitude": 136.6562,
      "themes": ["art_sense", "history_tradition"],
      "recommendedMonths": [4, 5, 10, 11]
    }
  ]
}
```

## 6.3 `GET /destinations/{destinationId}`

마커 클릭 시 해당 소도시의 상세 콘텐츠를 조회한다.
API path의 `destinationId`는 DB 구현에서 `cityId` 또는 `city_id`와 매핑될 수 있다.

**Response 200**

```json
{
  "destinationId": "uuid",
  "name": "경주",
  "country": "KR",
  "region": "경상북도",
  "latitude": 35.8562,
  "longitude": 129.2247,
  "summary": "오래된 골목과 전통 산책 리듬이 잘 맞는 소도시입니다.",
  "description": "불국사, 첨성대, 황리단길을 중심으로 전통과 산책 동선을 구성할 수 있습니다.",
  "themes": ["history_tradition"],
  "recommendedMonths": [3, 4, 5, 9, 10, 11],
  "image": {
    "heroImageUrl": "https://...",
    "thumbnailImageUrl": "https://...",
    "gallery": [
      {
        "imageUrl": "https://...",
        "alt": "경주 야경",
        "sourceUrl": "https://..."
      }
    ]
  },
  "routeSeed": ["불국사", "첨성대", "황리단길"],
  "recommendationReasons": [
    "역사·전통 테마 장소가 충분합니다.",
    "대표 장소 간 이동 동선이 단순합니다."
  ],
  "festival": {
    "festivalAvailable": false,
    "festivalIds": []
  },
  "contents": [
    {
      "contentId": "uuid",
      "title": "불국사",
      "contentType": "attraction",
      "themeTags": ["history_tradition"],
      "latitude": 35.7901,
      "longitude": 129.3321,
      "estimatedDurationMinutes": 90,
      "openingHoursSummary": "09:00-18:00",
      "sourceUrl": "https://...",
      "verificationStatus": "verified"
    }
  ]
}
```

# 7. AgentCore-Function API 계약

## 7.1 운영 기준

| 항목 | 기준 |
| --- | --- |
| 대화 저장 | 대화 원문은 영구 저장하지 않음 |
| 추천 저장 | 추천 결과는 사용자가 `/me/itineraries`를 호출할 때만 계정 데이터로 저장 |
| 임시 추천 조회 | `/recommendations/{recommendationId}`는 짧은 TTL의 결과 조회에만 사용 |
| Timeout | 사용자 대면 동기 호출은 29초 내외 완료 목표 |

## 7.2 `POST /recommendations`

지도 마커 선택 후 일정 생성, 또는 챗봇에서 자연어 조건을 받은 뒤 일정 생성을 요청한다.
사용자 위치 필드는 `userLocation`으로 확정한다.

**Request**

```json
{
  "entryType": "map_marker",
  "destinationId": "uuid",
  "country": "KR",
  "travelYear": 2026,
  "travelMonth": 10,
  "tripType": "2d1n",
  "themes": ["history_tradition", "food_local"],
  "includeFestivals": false,
  "naturalLanguageQuery": null,
  "userLocation": {
    "latitude": 37.5665,
    "longitude": 126.978
  }
}
```

**Request 규칙**

| 필드 | 규칙 |
| --- | --- |
| `entryType` | `map_marker`, `chat`, `home_recommendation` 중 하나 |
| `destinationId` | `entryType`이 `map_marker`이면 필수 |
| `themes` | canonical `themeId` 1~3개 |
| `naturalLanguageQuery` | 자연어 조건이 없으면 `null` 또는 생략 가능 |
| `userLocation` | 위치 권한이 없으면 `null` 또는 생략 가능 |

**Response 201**

```json
{
  "recommendationId": "uuid",
  "expiresAt": "2026-06-08T09:30:00Z",
  "destination": {
    "destinationId": "uuid",
    "name": "경주",
    "country": "KR",
    "region": "경상북도"
  },
  "itinerary": {
    "tripType": "2d1n",
    "days": [
      {
        "day": 1,
        "items": [
          {
            "itemId": "uuid",
            "contentId": "uuid",
            "timeOfDay": "morning",
            "sortOrder": 1,
            "title": "불국사 산책",
            "body": "전통 산책 흐름을 먼저 잡습니다.",
            "reason": "선택 테마와 소도시 상세 seed가 맞습니다.",
            "moveMinutes": 18,
            "latitude": 35.7901,
            "longitude": 129.3321
          }
        ]
      }
    ]
  },
  "explainability": {
    "matchedConditions": ["history_tradition", "travelMonth:10"],
    "unsupportedConditions": [],
    "recommendationReasons": [
      "역사·전통 테마 장소가 일정에 충분히 포함됩니다.",
      "10월 계절 적합도와 도보 이동성이 좋습니다."
    ],
    "itineraryFlowReason": "오전에는 대표 유적 산책, 오후에는 근거리 골목 탐색을 배치해 이동 부담을 낮췄습니다.",
    "confidence": 0.86,
    "userNotice": "숙소 가격과 예약 가능 여부는 실시간 확정 정보가 아니므로 검색 링크에서 확인해야 합니다."
  },
  "festivalDateVerifications": [
    {
      "festivalId": "uuid",
      "dateStatus": "confirmed",
      "startDate": "2026-10-10",
      "endDate": "2026-10-12",
      "sourceUrl": "https://example.official.kr",
      "confidence": 0.91
    }
  ],
  "links": {
    "map": "https://maps.google.com/...",
    "staySearch": "https://..."
  }
}
```

## 7.3 `GET /recommendations/{recommendationId}`

짧은 TTL 안에서 추천 결과를 다시 조회한다.
이 API는 대화 기록 저장 API가 아니며, 사용자가 저장한 일정은 `/me/itineraries`에서 관리한다.

**Response 200**

`POST /recommendations`의 Response 201과 동일한 구조를 반환한다.

## 7.4 `POST /agent/answer`

챗봇 화면의 현재 질문에 단일 턴 답변을 생성한다.
서버는 대화 원문을 영구 저장하지 않는다.

**Request**

```json
{
  "message": "가을에 조용한 일본 소도시 추천해줘",
  "context": {
    "country": "JP",
    "travelMonth": 10,
    "themes": ["healing_rest", "art_sense"]
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

# 8. 저장·피드백 API 계약

## 8.1 `GET /me/itineraries`

**Response 200**

```json
{
  "items": [
    {
      "itineraryId": "uuid",
      "sourceRecommendationId": "uuid",
      "title": "경주 1박 2일 전통 산책",
      "destination": {
        "destinationId": "uuid",
        "name": "경주",
        "country": "KR"
      },
      "tripType": "2d1n",
      "themes": ["history_tradition"],
      "createdAt": "2026-06-08T09:00:00Z",
      "updatedAt": "2026-06-08T09:00:00Z"
    }
  ]
}
```

## 8.2 `POST /me/itineraries`

추천 결과를 사용자 계정 데이터로 저장한다.
저장 일정은 추천 결과 snapshot을 보존하므로 원 추천 결과가 만료되어도 마이페이지에서 열 수 있어야 한다.

**Request**

```json
{
  "recommendationId": "uuid",
  "destinationId": "uuid",
  "title": "경주 1박 2일 전통 산책",
  "tripType": "2d1n",
  "themes": ["history_tradition"],
  "days": [
    {
      "day": 1,
      "items": [
        {
          "itemId": "uuid",
          "contentId": "uuid",
          "timeOfDay": "morning",
          "sortOrder": 1,
          "title": "불국사 산책",
          "body": "전통 산책 흐름을 먼저 잡습니다.",
          "reason": "선택 테마와 소도시 상세 seed가 맞습니다.",
          "moveMinutes": 18,
          "latitude": 35.7901,
          "longitude": 129.3321
        }
      ]
    }
  ]
}
```

**Response 201**

```json
{
  "itineraryId": "uuid",
  "sourceRecommendationId": "uuid",
  "createdAt": "2026-06-08T09:00:00Z"
}
```

## 8.3 `DELETE /me/itineraries/{itineraryId}`

**Response 204**

응답 body 없음.

## 8.4 `POST /me/feedback`

**Request**

```json
{
  "recommendationId": "uuid",
  "destinationId": "uuid",
  "feedbackType": "like",
  "themeTags": ["history_tradition"]
}
```

**Response 201**

```json
{
  "feedbackId": "uuid",
  "createdAt": "2026-06-08T09:00:00Z"
}
```

# 9. MVP 제외 항목

다음 항목은 현재 문서에 구현 대상으로 넣지 않는다.

| 항목 | 제외 이유 |
| --- | --- |
| `PATCH /me/itineraries/{itineraryId}` | 드래그앤드랍 일정 수정은 Product 고도화 단계에서 확정 |
| 지도 `bounds`, `radiusKm`, `cursor` query | GPS와 지도 viewport 검색 단계에서 확장 |
| 비동기 Agent job API | 29초 내 동기 응답이 어려워지는 경우 별도 설계 |
| 운영자 데이터 검토 API | MVP 사용자 흐름과 분리 |
| 외부 숙소·검색 링크 전용 API | MVP에서는 추천 응답의 `links`로 우선 처리 |

# 10. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-08 | 로브 기획팀 | AWS SAM 백엔드 구현을 위한 MVP 확정 API 범위, Lambda별 endpoint, 핵심 request/response 계약 정리 |
