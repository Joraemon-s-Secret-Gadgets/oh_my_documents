# 로브 (Lovv) API 명세서

> 문서 버전: v0.8
> 문서 상태: 기획 단계 (Planning)
> 기준 문서: 요구사항 명세서 v3.0, 서비스 흐름 명세서 v0.2, 데이터베이스 설계 명세서 v1.0, Agent 명세서 v0.4, 기술 명세서 v0.4, 배포·운영 가이드 v0.5

> **[PRD 반영 v0.1 — 대화형 빌더]** 대화형 빌더용 API 계약 추가 필요: **반경 후보 조회**(anchor+필터→2티어
> 후보), **후보 선택/일정 추가**(interrupt resume), **서브 윈도우 오픈 플래그**, 빌더 상태 재개(thread_id).
> 동선=선택 순서. 상세: `../98_prd/interactive_builder_prd.md`.
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

`/admin/*` 운영·검토 API의 인가 실패는 본 공통 오류 응답 형식을 따르되, 세부 오류 코드는 `9.1 관리자 인가 규칙`의 관리자 인가 오류 코드 표준을 우선 적용한다.

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

역할 enum은 `R-USER`, `R-ADMIN`, `R-SUPER-ADMIN`, `R-LOCAL-OPERATOR`, `R-DATA-PROVIDER`를 사용한다. `R-SUPER-ADMIN`은 기관에 종속되지 않는 전역 역할이며 일반 `R-ADMIN` 권한을 자동 상속하지 않는다. Cognito Group은 큰 권한 구분만 담당하고, 담당 지역·provider 소유권·세부 permission은 Lovv DB와 Backend에서 다시 검증한다.

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
| GET | `/admin/security/mfa/status` | Admin/SuperAdmin | 관리자 MFA 등록·세션 인증 상태 조회 |
| POST | `/admin/security/mfa/enroll` | Admin/SuperAdmin | 관리자 MFA 등록 시작 |
| POST | `/admin/security/mfa/confirm` | Admin/SuperAdmin | TOTP 코드 확인 및 복구 코드 발급 |
| POST | `/admin/security/mfa/verify` | Admin/SuperAdmin | 현재 관리자 세션 MFA 인증 |
| POST | `/admin/security/mfa/recover` | Admin/SuperAdmin | 복구 코드로 현재 관리자 세션 인증 |
| POST | `/admin/high-risk-requests` | Admin/SuperAdmin | 역할·지역·대량 게시 고위험 변경 요청 생성 |
| GET | `/admin/high-risk-requests?status=pending&limit=50` | Admin/SuperAdmin | 고위험 변경 pending 목록 조회 |
| POST | `/admin/high-risk-requests/{requestId}/approve` | SuperAdmin | 다른 요청자의 고위험 변경 승인·실행 |
| POST | `/admin/high-risk-requests/{requestId}/reject` | SuperAdmin | 다른 요청자의 고위험 변경 거절 |

## 9.1 관리자 인가 규칙

모든 `/admin/*` 엔드포인트는 다음 규칙을 서버에서 강제한다. (요구사항 `FR-ADMIN-001`~`FR-ADMIN-003`, `FR-ADMIN-009`)

- 인증 이후에도 요청마다 역할과 리소스 범위를 서버 데이터(서비스 DB의 활성 역할 할당)로 재검증한다. 요청 본문의 `roles`, `regionIds`, `organizationId`, `reviewerId` 등 권한·소유권 필드는 신뢰하지 않는다.
- 관리자 역할(`R-ADMIN`·`R-SUPER-ADMIN`·`R-DATA-PROVIDER`·`R-LOCAL-OPERATOR`) 중 해당 API에 허용된 활성 역할이 하나도 없으면 fail-closed로 거부한다.
- 외부 인증 그룹(Cognito Group 등)은 보조 신호로만 사용하고, 활성 DB 할당이 없거나 정지 상태면 관리자 권한을 부여하지 않는다.
- 복수 역할 사용자의 권한은 역할별 허용 작업의 합집합으로 계산하고, 범위 제한(`Own`/`Assigned`/`All`)은 역할마다 따로 적용한다.
- `require_admin_access` 계층의 일반 관리자 읽기·목록 API는 `R-ADMIN` 또는 `R-SUPER-ADMIN` 활성 역할만 확인한다. MFA 미인증만으로 403을 반환하지 않는다.
- 관리자 MFA는 전역 admin gate가 아니다. MFA 등록·상태·검증 API는 MFA 미인증 상태에서도 접근 가능해야 하며, 고위험 변경 승인·거절 시점에만 최근 5분 이내 TOTP 세션을 요구한다.
- 복구 코드로 만든 MFA 세션은 계정 복구용이다. 고위험 변경 승인·거절에는 사용할 수 없다.

`/admin/*` 인가 실패는 다음 표준 코드로 응답한다.

| HTTP Status | Code | 조건 |
| --- | --- | --- |
| 401 | UNAUTHENTICATED | 인증 정보 없음 |
| 401 | TOKEN_EXPIRED | 액세스 토큰 만료 |
| 403 | ADMIN_ACCESS_REQUIRED | 활성 관리자 역할 없음 |
| 403 | ROLE_FORBIDDEN | 역할은 있으나 해당 작업 권한 없음 |
| 403 | SUPER_ADMIN_REQUIRED | `R-SUPER-ADMIN` 전용 작업을 다른 역할이 시도 |
| 403 | REGION_SCOPE_FORBIDDEN | `R-LOCAL-OPERATOR`의 담당 지역(Assigned) 밖 요청 |
| 403 | ORGANIZATION_SCOPE_FORBIDDEN | `R-DATA-PROVIDER`의 소속 기관(Own) 밖 요청 |
| 403 | SELF_REVIEW_FORBIDDEN | 제안 작성자 본인이 동일 제안을 검토 |
| 404 | NOT_FOUND | 리소스 없음(존재 여부 비노출) |
| 409 | ROLE_ASSIGNMENT_CONFLICT | 역할·지역 할당 충돌 |
| 409 | INVALID_PROPOSAL_STATE | 검토 불가 상태에서의 전이 시도 |

## 9.2 데이터 제안 검토 — `PATCH /admin/data-submissions/{submissionId}/review`

승인·반려·수정 요청 처리 시 서버는 다음을 추가로 검증한다. (요구사항 `FR-ADMIN-006`, `FR-ADMIN-009`, `FR-ADMIN-014`)

- 검토 결정(승인·반려·수정 요청)은 `R-ADMIN`만 수행한다. `R-DATA-PROVIDER`·`R-LOCAL-OPERATOR`는 거부한다.
- 제안 작성자 본인(`createdBy`가 요청자와 동일)이 같은 제안을 검토하면 거부한다(이해충돌 방지).
- 대상 제안이 검토 가능한 상태가 아니면 거부한다.
- 오류 메시지에 타 사용자 ID·기관명·지역 할당·리소스 존재 여부를 노출하지 않는다.

## 9.3 관리자 Step-up MFA

관리자 MFA는 기존 로그인 경로를 바꾸지 않고 고위험 변경 승인·거절 직전에만 step-up으로 적용한다. 일반 admin 읽기·목록 경로와 MFA 상태 조회는 활성 관리자 역할만 있으면 접근 가능하다. (요구사항 `FR-ADMIN-017`)

### 상태 조회 — `GET /admin/security/mfa/status`

응답은 `mfa.enrolled`, `mfa.credentialStatus`, `mfa.sessionVerified`, `mfa.sessionVerifiedAt`, `mfa.sessionExpiresAt`, `mfa.recoveryCodesRemaining`을 포함한다.

### 등록 시작 — `POST /admin/security/mfa/enroll`

서버는 사용자별 TOTP secret을 생성하고 암호화해 `pending` 상태로 저장한다. 응답은 `enrollment.secret`, `enrollment.provisioningUri`를 포함한다.

### 등록 확인 — `POST /admin/security/mfa/confirm`

요청 본문은 `code`를 포함한다. 서버는 TOTP 코드를 검증하고 MFA 자격을 `active`로 전환한 뒤 복구 코드를 1회 표시한다. 응답은 `status`, `recoveryCodes`를 포함한다.

### 세션 인증 — `POST /admin/security/mfa/verify`

요청 본문은 `code`를 포함한다. 서버는 TOTP 재사용을 거부하고 현재 로그인 세션에 관리자 MFA 인증 만료 시각과 인증 방법 `totp`를 기록한다. 고위험 승인·거절은 이 엔드포인트로 만든 최근 5분 이내 TOTP 세션을 별도로 확인하며, approve/reject 본문에는 TOTP code를 넣지 않는다. 응답은 `mfa` 상태를 포함한다.

### 복구 인증 — `POST /admin/security/mfa/recover`

요청 본문은 `recoveryCode`를 포함한다. 서버는 복구 코드를 1회 사용 처리하고 현재 로그인 세션을 복구 인증 상태로 전환한다. 이 세션은 계정 복구용이며 고위험 변경 승인·거절에는 사용할 수 없다. 응답은 `mfa` 상태를 포함한다.

| HTTP Status | Code | 조건 |
| --- | --- | --- |
| 400 | INVALID_ADMIN_MFA_PAYLOAD | 필수 `code` 또는 `recoveryCode` 누락 |
| 403 | ADMIN_MFA_REQUIRED | 고위험 승인·거절 시점에 현재 세션의 MFA 인증 없음 |
| 403 | ADMIN_MFA_ENROLLMENT_REQUIRED | 활성 MFA 자격 없음 |
| 403 | ADMIN_MFA_CODE_INVALID | TOTP 또는 복구 코드 불일치 |
| 403 | ADMIN_MFA_SESSION_REQUIRED | MFA 인증을 기록할 로그인 세션 식별자 없음 |
| 409 | ADMIN_MFA_ALREADY_ENROLLED | 이미 활성 MFA 자격이 있음 |
| 409 | ADMIN_MFA_STATE_CONFLICT | MFA 자격 상태가 요청 전이와 맞지 않음 |
| 409 | ADMIN_MFA_CODE_REUSED | 이미 사용한 TOTP counter 또는 복구 코드 재사용 |
| 429 | ADMIN_MFA_LOCKED | 연속 실패로 MFA 검증 일시 잠금 |
| 500 | ADMIN_MFA_NOT_CONFIGURED | MFA 암호화 키 또는 저장소 설정 누락 |

## 9.4 고위험 변경 요청

역할·지역 할당과 월간 여행지 대량 게시는 직접 변경 API 없이 고위험 요청으로 처리한다. 생성·목록은 `R-ADMIN` 또는 `R-SUPER-ADMIN`, 승인·거절은 `R-SUPER-ADMIN`만 허용한다. `R-SUPER-ADMIN`은 일반 `R-ADMIN` 권한을 자동 상속하지 않지만, 이 절의 생성·목록 API는 두 역할을 모두 허용한다.

### 요청 생성 — `POST /admin/high-risk-requests`

공통 필드는 `operationType`, `reason`이다. 작업별 요청 필드는 다음과 같다.

| `operationType` | 추가 필드 | 검증 규칙 |
| --- | --- | --- |
| `role_grant` | `targetUserId`, `roleCode`, 선택 `organizationId`, `validUntil` | 역할 enum만 허용, `R-SUPER-ADMIN`은 `organizationId` 금지 |
| `role_revoke` | `targetUserId`, `roleCode`, 선택 `organizationId` | 활성 할당 필요, 마지막 활성 `R-SUPER-ADMIN` 회수 금지 |
| `region_grant` | `targetUserId`, `regionId`, 선택 `organizationId`, `validUntil` | 대상 사용자 존재 필요 |
| `region_revoke` | `targetUserId`, `regionId`, 선택 `organizationId` | 활성 할당 필요 |
| `bulk_publish` | `destinationIds` | 중복 제거 후 고유 ID 10~100개 |

**Response 201**

```json
{
  "request": {
    "id": "uuid",
    "operationType": "role_grant",
    "targetUserId": "uuid",
    "payload": {
      "operationType": "role_grant",
      "reason": "운영 담당자 권한 부여",
      "targetUserId": "uuid",
      "roleCode": "R-LOCAL-OPERATOR",
      "organizationId": null,
      "validUntil": null
    },
    "status": "pending",
    "reason": "운영 담당자 권한 부여",
    "requestedBy": "uuid",
    "decidedBy": null,
    "decisionReason": null,
    "requestedAt": "2026-06-30T02:00:00Z",
    "decidedAt": null,
    "executedAt": null,
    "executionSummary": {},
    "updatedAt": "2026-06-30T02:00:00Z"
  }
}
```

### 목록 조회 — `GET /admin/high-risk-requests`

선택 query는 `status`(`pending`, `executed`, `rejected`), `operationType`, `limit`이다. admin_web pending 목록은 `GET /api/v1/admin/high-risk-requests?status=pending&limit=50`을 사용한다. 목록 조회는 MFA가 필요 없고 역할 인증만 필요하다. `limit`은 서버에서 최대 50으로 clamp하며, 50건 초과 여부와 관계없이 현재 응답의 `nextCursor`는 `null`이다.

### 승인·실행 — `POST /admin/high-risk-requests/{requestId}/approve`

요청 본문은 선택 `decisionReason`만 허용하며 TOTP `code`를 포함하지 않는다. 요청자와 다른 `R-SUPER-ADMIN`이 `/admin/security/mfa/verify`로 최근 5분 이내 TOTP 재인증한 경우에만 승인한다. 승인 시 대상 변경과 감사 로그를 같은 트랜잭션에서 실행하고 응답 상태를 `executed`로 반환한다. 복구 코드로 인증한 MFA 세션은 허용하지 않는다.

### 거절 — `POST /admin/high-risk-requests/{requestId}/reject`

요청 본문은 필수 `decisionReason`만 포함하며 TOTP `code`를 포함하지 않는다. 승인과 같은 역할 분리·최근 TOTP 조건을 적용하며, 대상 변경 없이 상태를 `rejected`로 반환한다.

| HTTP Status | Code | 조건 |
| --- | --- | --- |
| 400 | INVALID_HIGH_RISK_PAYLOAD | 생성 본문·작업 유형·필드·대량 게시 건수 오류 |
| 400 | INVALID_HIGH_RISK_FILTER | 목록 필터 오류 |
| 400 | INVALID_HIGH_RISK_DECISION | 결정 본문 또는 필수 거절 사유 오류 |
| 403 | SUPER_ADMIN_REQUIRED | `R-SUPER-ADMIN`이 아닌 사용자의 승인·거절 시도 |
| 403 | ADMIN_MFA_REQUIRED | 현재 세션의 MFA 인증 없음 |
| 403 | ADMIN_MFA_ENROLLMENT_REQUIRED | 활성 MFA 자격 없음 |
| 403 | ADMIN_MFA_TOTP_REQUIRED | 최근 5분 TOTP가 아니거나 복구 코드 인증 세션 |
| 404 | HIGH_RISK_REQUEST_NOT_FOUND | 요청 없음 |
| 404 | USER_NOT_FOUND | 역할·지역 대상 사용자 없음 |
| 404 | MONTHLY_DESTINATION_NOT_FOUND | 대량 게시 대상 중 존재하지 않는 항목이 있음 |
| 409 | SELF_APPROVAL_FORBIDDEN | 요청자가 자신의 요청을 승인·거절 |
| 409 | HIGH_RISK_REQUEST_ALREADY_DECIDED | 이미 실행·거절된 요청 재결정 |
| 409 | HIGH_RISK_REQUEST_STATE_CONFLICT | 동시 결정으로 상태가 변경됨 |
| 409 | ACTIVE_ASSIGNMENT_NOT_FOUND | 회수할 활성 역할·지역 할당 없음 |
| 409 | LAST_SUPER_ADMIN_REQUIRED | 마지막 활성 `R-SUPER-ADMIN` 회수 시도 |
| 409 | MONTHLY_TRANSITION_FORBIDDEN | 게시 가능한 상태가 아닌 월간 여행지 포함 |
| 429 | ADMIN_MFA_LOCKED | 연속 실패로 MFA 검증 일시 잠금 |

## 9.5 관리자 감사 로그 조회 — `GET /admin/audit-logs`

`R-ADMIN` 또는 `R-SUPER-ADMIN`이 조회한다. 선택 query는 `action`, `resourceType`, `result`, `actorUserId`, `limit`이며 응답은 `items`, `nextCursor: null`을 반환한다. 조회에는 MFA를 요구하지 않는다. 고위험 변경에서는 `high_risk_request.create/approve/reject`, `role_grant.execute`, `role_revoke.execute`, `region_grant.execute`, `region_revoke.execute`, `bulk_publish.execute`를 조회할 수 있어야 한다.

감사 항목은 행위자·세션, 역할·기관·지역 스냅샷, action, 리소스, `allowed`/`denied`/`succeeded`/`failed` 결과, 사유 코드, 요청 ID, 비민감 변경 전·후 요약을 포함한다. 토큰, 쿠키, TOTP secret·코드, 복구 코드와 민감 원문은 반환하지 않는다.
# 10. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.8 | 2026-07-02 | Codex | 관리자 MFA 범위를 고위험 승인·거절 시점으로 정정하고 pending 목록 조회, TOTP 별도 검증, 복구 코드 승인 불가, limit 50 clamp 계약 반영 |
| v0.7 | 2026-06-30 | Codex | `R-SUPER-ADMIN` 역할 enum, 고위험 변경 생성·조회·승인·거절 API, 최근 TOTP·자기 결정 금지·오류 코드와 C4 감사 로그 조회 계약 추가 |
| v0.6 | 2026-06-30 | Codex | 관리자 Step-up MFA 상태·등록·확인·인증·복구 API와 오류 코드 추가 |
| v0.5 | 2026-06-30 | Codex | 관리자 운영 API 인가 규칙, 자기검토 금지 오류 코드, `/admin/*` 오류 코드 교차참조 반영 |
| v0.4 | 2026-06-22 | 로브 기획팀 | 대화형 빌더 API placeholder 반영: 반경 후보 조회, 후보 선택·일정 추가, 서브 윈도우 플래그, 빌더 상태 재개 계약 후보 기록 |
| v0.3 | 2026-06-12 | 로브 기획팀 | Cognito bridge 인증 흐름 추가, Google/Kakao 직접 검증 API legacy 처리, role enum과 logout 책임 경계 반영 |
| v0.2 | 2026-06-08 | 로브 기획팀 | AWS SAM 기반 Auth, Map, AgentCore Lambda별 API 라우팅과 Google/Kakao 인증, 세션, 지도 상세, 저장 없는 Agent 답변 API 추가 |
| v0.1 | 2026-05-29 | 로브 기획팀 | API 명세서 초안 작성 |
