# 로브 (Lovv) API 명세서

> 문서 버전: v0.3
> 문서 상태: 기획 단계 (Planning)
> 기준 문서: 요구사항 명세서 v1.7, 서비스 흐름 명세서 v0.2, 데이터베이스 설계 명세서 v0.5, Agent 명세서 v0.4, 기술 명세서 v0.4, 배포·운영 트러블슈팅 v0.2

# 1. 문서 개요

## 1.1 목적

본 문서는 로브 서비스의 프론트엔드, 백엔드, 추천 Agent, 운영 화면이 사용하는 API 계약을 정의한다.
엔드포인트는 Production 기준의 목표 계약이며, PoC에서는 일부를 정적 데이터 또는 로컬 스토리지로 대체할 수 있다.

## 1.2 공통 규칙

| 항목 | 규칙 |
| --- | --- |
| Base URL | `/api/v1` |
| Content-Type | `application/json; charset=utf-8` |
| 인증 | 공개 추천 조회는 선택, 운영·저장·마이페이지는 Cognito JWT 인증 필요 |
| 날짜 형식 | ISO 8601 |
| ID 형식 | UUID 권장 |
| 보안 스킴 | `cognitoBearerAuth` (`Authorization: Bearer <Cognito JWT>`) |

## 1.3 Lambda 라우팅 기준

AWS SAM 기반 배포에서는 API Gateway가 단일 `/api/v1` 진입점을 제공하고, Cognito JWT Authorizer로 인증·인가를 검증한 뒤 요청 성격에 따라 Lambda를 분리해 호출한다.

| 담당 Lambda | API 범위 | 책임 |
| --- | --- | --- |
| `Auth-Function` | `/auth/*`, 초기 `/auth/cognito/session` 세션 조회 | Cognito claims를 Lovv user/session shape로 변환하고, legacy social login API를 유지 |
| `Map-Function` | `/destinations/*` | 지도 마커 목록, 소도시 상세 콘텐츠, DB/S3 기반 읽기 API |
| `AgentCore-Function` | `/recommendations`, `/agent/answer` | LLM 호출, 추천 설명 생성, 대화 원문 저장 없는 순수 AI 추론 |

각 Lambda는 별도 IAM Role과 배포 패키지를 가진다. 인증·지도 API에는 AI SDK와 LangChain 계열 의존성을 포함하지 않고, AgentCore API는 사용자 대면 동기 응답 기준으로 29초 내외 완료를 목표로 한다. 응답 시간이 더 길어질 수 있는 요청은 비동기 작업 또는 스트리밍 API로 별도 설계한다.

# 2. 공통 오류 응답

| HTTP Status | Code | 의미 |
| --- | --- | --- |
| 400 | BAD_REQUEST | 요청 형식 오류 |
| 401 | UNAUTHENTICATED | 인증 필요 |
| 403 | FORBIDDEN | 권한 없음 |
| 404 | NOT_FOUND | 리소스 없음 |
| 409 | CONFLICT | 중복 또는 상태 충돌 |
| 422 | VALIDATION_ERROR | 의미상 유효하지 않은 요청 |
| 422 | AUTH_MAPPING_ERROR | Cognito 필수 claim은 있으나 Lovv 사용자/role 매핑이 불가능 |
| 500 | INTERNAL_ERROR | 서버 오류 |

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "여행 월은 1부터 12 사이여야 합니다.",
    "details": {
      "field": "travelMonth"
    }
  }
}
```

# 3. 인증 API

| Method | Path | Auth | 담당 Lambda | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/auth/cognito/session` | Cognito | `Auth-Function` | Cognito claims를 Lovv user/session 응답으로 변환 |
| POST | `/auth/google` | Public | `Auth-Function` | Legacy. Google provider token 직접 검증 방식 |
| POST | `/auth/kakao` | Public | `Auth-Function` | Legacy. Kakao provider token 직접 검증 방식 |
| POST | `/auth/logout` | User | `Auth-Function` | 로그아웃 |
| GET | `/auth/me` | User | `Auth-Function` | 현재 사용자와 역할 조회 |
| GET | `/auth/session` | User | `Auth-Function` | 로그인 직후 대시보드 진입에 필요한 세션 요약 조회 |

## 3.1 `POST /auth/cognito/session`

Cognito Hosted UI 또는 OIDC IdP 로그인이 끝난 뒤 호출한다. API Gateway JWT Authorizer가 Cognito JWT를 먼저 검증하고, 백엔드는 검증된 claims만 사용해 Lovv 사용자와 세션 응답을 구성한다.

이 경로에서는 Google/Kakao provider token verifier를 호출하지 않는다.

**Request**

본문 없음. 인증 정보는 `Authorization: Bearer <Cognito JWT>` 헤더로 전달한다.

**Claims 입력 기준**

| Claim | 용도 |
| --- | --- |
| `sub` | Cognito 사용자 식별자, Lovv user 조회/생성 기준 |
| `email` | 사용자 이메일 |
| `name` 또는 `preferred_username` | 표시 이름 후보 |
| `cognito:groups` | 큰 권한 그룹 매핑 |

**Response 200**

```json
{
  "authenticated": true,
  "accessToken": "cognito-access-token",
  "tokenType": "Bearer",
  "user": {
    "userId": "uuid",
    "cognitoSub": "cognito-sub",
    "email": "user@example.com",
    "displayName": "홍길동",
    "roles": ["R-USER"]
  },
  "preferences": {
    "countryTrack": "JP",
    "mappedThemes": ["art_sense", "history_tradition"],
    "selectedThemeIds": ["art_sense", "history_tradition"]
  },
  "onboardingCompleted": true,
  "sessionRestored": true
}
```

**오류 기준**

| 상태 | 조건 |
| --- | --- |
| 401 | Cognito claims 없음 또는 JWT Authorizer 미검증 |
| 422 | `sub`, `email` 등 필수 claim 매핑 불가 |
| 500 | DB 초기화·조회 실패 등 인증 이후 내부 오류 |

Repository와 DB client는 claims 검증 이후 lazy init한다. 인증 정보가 없는 요청에서 DB 초기화 실패가 먼저 발생해 500으로 보이면 안 된다.

## 3.2 `POST /auth/google`, `POST /auth/kakao` (Legacy)

이 API는 Cognito 도입 이전의 provider token 직접 검증 방식이다. 신규 프론트 흐름은 Cognito Hosted UI/OIDC 로그인 후 `POST /auth/cognito/session`을 호출한다.

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

공급자 OAuth 토큰은 서버에서 검증하고 클라이언트 저장 대상으로 반환하지 않는다. refresh token을 사용하는 경우 HttpOnly 쿠키 또는 서버 세션 저장소로 관리한다. 단, Cognito 흐름과 동시에 사용하지 않는다.

## 3.3 `GET /auth/session`

기존 프론트 호환용 세션 조회 API다. 신규 Cognito 흐름에서는 `POST /auth/cognito/session` 또는 `GET /auth/me`를 우선 사용한다.

**Response 200**

```json
{
  "user": {
    "userId": "uuid",
    "displayName": "홍길동",
    "roles": ["R-USER"]
  },
  "preferences": {
    "countryTrack": "JP",
    "mappedThemes": ["art_sense", "history_tradition"],
    "selectedThemeIds": ["art_sense", "history_tradition"]
  },
  "savedItineraries": [
    {
      "itineraryId": "uuid",
      "destinationName": "가나자와",
      "country": "JP",
      "updatedAt": "2026-06-08T09:00:00Z"
    }
  ]
}
```

## 3.4 `GET /auth/me`

**Response 200**

```json
{
  "userId": "uuid",
  "displayName": "홍길동",
  "roles": ["R-USER"]
}
```

역할 enum은 `R-USER`, `R-ADMIN`, `R-LOCAL-OPERATOR`, `R-DATA-PROVIDER`를 사용한다. Cognito Group은 큰 권한 구분만 담당하고, 담당 지역·provider 소유권·세부 permission은 Lovv DB와 Backend에서 다시 검증한다.

## 3.5 `POST /auth/logout`

로그아웃은 Lovv logout과 Cognito logout을 분리한다.

| 구분 | 처리 |
| --- | --- |
| Lovv logout | backend session, cookie, local service state 정리 |
| Cognito logout | Cognito Hosted UI logout URL로 redirect |

Cognito access token은 JWT라 이미 발급된 token을 백엔드가 즉시 무효화한다고 표현하지 않는다. 프론트는 필요 시 Cognito logout URL로 이동해 Hosted UI 세션까지 종료한다.

# 4. 온보딩·선호 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/me/preferences` | User | 선호 프로필 조회 |
| PUT | `/me/preferences` | User | 온보딩 응답 저장 또는 재설정 |
| GET | `/themes/onboarding-options` | Public | 대도시 스타일 선택지 조회 |

## 4.1 `PUT /me/preferences`

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
  "mappedThemes": ["history_tradition"],
  "updatedAt": "2026-05-29T09:00:00Z"
}
```

# 5. 지도·목적지 API

| Method | Path | Auth | 담당 Lambda | 설명 |
| --- | --- | --- | --- | --- |
| GET | `/destinations` | Public | `Map-Function` | 소도시 목록 조회 |
| GET | `/destinations/{destinationId}` | Public | `Map-Function` | 소도시 상세 조회 |
| GET | `/destinations/map-markers` | Public | `Map-Function` | 지도 마커 조회 |

## 5.1 `GET /destinations/map-markers`

**Query**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| country | string | No | `KR`, `JP` |
| month | number | No | 1~12 |
| theme | string | No | 테마 코드 |

**Response 200**

```json
{
  "items": [
    {
      "destinationId": "uuid",
      "name": "가나자와",
      "country": "JP",
      "latitude": 36.5613,
      "longitude": 136.6562,
      "themes": ["art_sense", "history_tradition"],
      "recommendedMonths": [4, 5, 10, 11]
    }
  ]
}
```

## 5.2 `GET /destinations/{destinationId}`

마커 클릭 시 해당 소도시의 상세 콘텐츠를 조회한다. API path의 `destinationId`는 DB 구현에서 `city_id`와 매핑될 수 있다.

**Response 200**

```json
{
  "destinationId": "uuid",
  "name": "가나자와",
  "country": "JP",
  "latitude": 36.5613,
  "longitude": 136.6562,
  "summary": "전통 거리와 현대 미술관을 함께 즐길 수 있는 일본 소도시입니다.",
  "themes": ["art_sense", "history_tradition"],
  "contents": [
    {
      "contentId": "uuid",
      "title": "히가시차야 거리",
      "contentType": "attraction",
      "sourceUrl": "https://example.official.jp"
    }
  ]
}
```

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

# 7. 저장·피드백 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/me/itineraries` | User | 저장 일정 목록 |
| POST | `/me/itineraries` | User | 추천 일정 저장 |
| DELETE | `/me/itineraries/{itineraryId}` | User | 저장 일정 삭제 |
| POST | `/me/feedback` | User | 좋아요/싫어요 저장 |

## 7.1 `POST /me/feedback`

**Request**

```json
{
  "recommendationId": "uuid",
  "destinationId": "uuid",
  "feedbackType": "like",
  "themeTags": ["art_sense", "history_tradition"]
}
```

**Response 201**

```json
{
  "feedbackId": "uuid",
  "createdAt": "2026-05-29T09:00:00Z"
}
```

# 8. 외부 정보 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/external/weather/current` | Public | 목적지 현재 날씨 표시 |
| GET | `/external/stay-links` | Public | 숙소 검색 링크 생성 |
| GET | `/external/search-links` | Public | Kakao/Yahoo/Google 탐색 링크 생성 |

WeatherAPI 응답은 추천 스코어링에 사용하지 않고 목적지 상세 표시용으로만 사용한다.

# 9. 운영·검토 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/admin/data-submissions` | Admin/Operator | 데이터 제안 목록 |
| POST | `/admin/data-submissions` | Operator/DataProvider | 데이터 제안 등록 |
| PATCH | `/admin/data-submissions/{submissionId}/review` | Admin | 승인, 반려, 수정 요청 |
| GET | `/admin/audit-logs` | Admin | 검토·승인 이력 조회 |

# 10. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.3 | 2026-06-12 | 로브 기획팀 | Cognito bridge 인증 흐름 추가, Google/Kakao 직접 검증 API legacy 처리, role enum과 logout 책임 경계 반영 |
| v0.2 | 2026-06-08 | 로브 기획팀 | AWS SAM 기반 Auth, Map, AgentCore Lambda별 API 라우팅과 Google/Kakao 인증, 세션, 지도 상세, 저장 없는 Agent 답변 API 추가 |
| v0.1 | 2026-05-29 | 로브 기획팀 | API 명세서 초안 작성 |
