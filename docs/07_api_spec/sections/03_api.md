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
