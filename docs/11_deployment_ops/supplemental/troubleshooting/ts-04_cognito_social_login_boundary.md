# TS-04 Cognito / Social Login 책임 경계 충돌

> 문서 성격: 트러블슈팅 하위 Markdown
> 상위 문서: `../troubleshooting.md`

> 문서 버전: v0.2
> 문서 상태: 초안 (Draft)
> 작성일: 2026-07-09
> 작성자: llm팀
> 문서 목적: `TS-04` 이슈의 문제, 원인, 판단, 조치, 재발 방지 기준을 본 문서에서 분리해 상세 관리한다.

---


## 1. 배경

초기 Lovv Auth 구조는 프론트가 Google/Kakao에서 받은 provider token을 백엔드로 전달하고, 백엔드가 직접 검증하는 방식이었다.

```text
POST /api/v1/auth/google
POST /api/v1/auth/kakao
↓
Lovv backend가 Google/Kakao provider token 검증
↓
Lovv user 조회/생성
↓
Lovv access token 발급
↓
refresh session 저장
```

하지만 Cognito를 도입하면 Google/Kakao 인증은 Cognito Hosted UI 또는 OIDC IdP가 담당한다. 백엔드는 provider token을 직접 검증하는 대신 Cognito가 검증한 JWT claims 또는 API Gateway Authorizer claims를 기준으로 Lovv 사용자와 세션 응답을 구성해야 한다.

## 2. 문제 1: 기존 Social Login API와 Cognito 흐름 충돌

| 항목 | 기존 방식 | Cognito 방식 |
| --- | --- | --- |
| Google/Kakao 인증 | Lovv 백엔드가 provider token 직접 검증 | Cognito가 Hosted UI/OIDC IdP로 처리 |
| 백엔드 입력 | provider access token | Cognito JWT claims |
| 백엔드 책임 | provider 검증 + Lovv token 발급 | Lovv user/session shape 변환 |

기존 `/api/v1/auth/google`, `/api/v1/auth/kakao`를 그대로 신규 흐름의 중심으로 두면 인증 책임이 Lovv backend와 Cognito 두 군데로 나뉜다.

### 해결 방향

| API | 상태 | 역할 |
| --- | --- | --- |
| `POST /api/v1/auth/google` | legacy/deprecated | provider token 직접 검증 방식 보존 |
| `POST /api/v1/auth/kakao` | legacy/deprecated | provider token 직접 검증 방식 보존 |
| `POST /api/v1/auth/cognito/session` | 신규 | Cognito claims를 Lovv session 응답으로 변환 |

## 3. 문제 2: Cognito 로그인 후 Lovv 세션 shape 필요

Cognito가 인증을 처리해도 프론트는 Lovv 서비스 상태가 필요하다.

프론트가 필요한 값은 다음과 같다.

| 값 | 용도 |
| --- | --- |
| `user` | 화면 표시와 사용자 식별 |
| `preferences` | 온보딩 취향 복구 |
| `onboardingCompleted` | 온보딩 진입 여부 결정 |
| `roles` | 사용자/운영자/관리자 화면 분기 |
| `accessToken` 또는 인증 상태 | 인증 API 호출 |
| `sessionRestored` | 세션 복구 성공 여부 |

### 해결 방향

`POST /api/v1/auth/cognito/session`은 API Gateway JWT Authorizer가 검증한 Cognito claims를 받아 Lovv user/session shape로 변환한다.

처리 순서:

```text
Cognito JWT Authorizer 검증
↓
sub, email, cognito:groups claims 확인
↓
Lovv user 조회 또는 생성
↓
Lovv 내부 role 정규화
↓
preferences 조회
↓
onboardingCompleted 계산
↓
session response 반환
```

## 4. 문제 3: Provider Verifier 재사용 금지

Cognito bridge endpoint에서 기존 Google/Kakao provider verifier를 재사용하면 안 된다. Cognito 흐름에서는 이미 Cognito가 provider 인증을 완료했기 때문이다.

| 경로 | verifier 사용 |
| --- | --- |
| `/auth/google` | Google provider verifier 사용 |
| `/auth/kakao` | Kakao provider verifier 사용 |
| `/auth/cognito/session` | provider verifier 사용 금지. Cognito claims만 매핑 |

## 5. 문제 4: Cognito claims 누락 시 500 발생 가능

개발 중 missing claims 테스트에서 401이 아니라 500이 발생할 수 있었다.

### 원인

Cognito claims 검증보다 repository 초기화가 먼저 실행되면, 인증 정보가 없는 요청인데 DB/repository 초기화 실패가 먼저 드러나 내부 서버 오류처럼 보인다.

### 해결 방향

- Cognito claims를 먼저 검증한다.
- repository와 DB client는 claims 검증 이후 lazy init한다.
- 인증 실패와 내부 장애를 분리한다.

| 상황 | 기대 응답 |
| --- | --- |
| Cognito claims 없음 | `401 UNAUTHENTICATED` |
| 필수 claim 매핑 불가 | `422 AUTH_MAPPING_ERROR` 또는 명확한 auth mapping error |
| DB 초기화 실패 | claims 검증 이후 `500 INTERNAL_ERROR` |

## 6. 문제 5: Handler route와 SAM template route 불일치

`src/auth/app.py`에 `/api/v1/auth/cognito/session` 처리를 추가해도 `template.yaml`에 API Gateway route가 없으면 실제 배포 API에서는 접근할 수 없다.

### 해결 방향

코드 테스트뿐 아니라 template route 테스트를 추가한다.

확인 기준:

| 확인 항목 | 기준 |
| --- | --- |
| Handler route | `src/auth/app.py`에 `/api/v1/auth/cognito/session` 처리 존재 |
| SAM route | `template.yaml`의 `AuthFunction` event에 동일 path 존재 |
| API 명세 | `docs/07_api_spec/07_api_spec.md`의 path와 일치 |
| Authorizer | Cognito User Pool/JWT Authorizer 연결은 별도 Task로 추적 |

## 7. 문제 6: Logout 의미 분리

Cognito 도입 후 logout을 단순히 백엔드 session 삭제로만 설명하면 부족하다. Cognito access token은 JWT이므로 이미 발급된 token은 만료 전까지 유효할 수 있다.

| 구분 | 설명 |
| --- | --- |
| Lovv logout | Lovv backend session/cookie, 프론트 local service state 정리 |
| Cognito logout | Cognito Hosted UI logout URL로 이동해 Hosted UI 세션 종료 |

백엔드가 Cognito token 자체를 즉시 무효화한다고 표현하지 않는다. 프론트는 필요하면 Cognito logout URL로 redirect한다.

## 8. 문제 7: Role을 Cognito Group만으로 처리하면 복잡해짐

Lovv Admin에는 일반 사용자 외에도 여러 운영 role이 필요하다.

| Role | 의미 |
| --- | --- |
| `R-USER` | 일반 서비스 이용자 |
| `R-ADMIN` | 전체 관리자 |
| `R-LOCAL-OPERATOR` | 담당 지역 데이터와 운영 지표 조회 |
| `R-DATA-PROVIDER` | 관광지, 축제, 체험 데이터 제안 등록 |

### 해결 방향

Cognito Group은 큰 권한 구분만 담당하고, 담당 지역과 provider 소유권 같은 세부 권한은 Lovv DB/backend에서 검증한다.

주의 기준:

- 프론트 route guard만으로 관리자 보안을 처리하지 않는다.
- Lambda/API에서도 role을 검증한다.
- 지역 운영자의 담당 지역 scope는 DB에서 확인한다.

## 9. 문제 8: API 명세 재정리 필요

기존 OpenAPI/API 명세는 custom social login 기준이라 Cognito bridge 흐름을 설명하지 못했다.

반영 기준:

| 항목 | 반영 내용 |
| --- | --- |
| 신규 경로 | `/api/v1/auth/cognito/session` 추가 |
| 기존 경로 | `/api/v1/auth/google`, `/api/v1/auth/kakao` legacy/deprecated 처리 |
| 보안 스킴 | `cognitoBearerAuth` 추가 |
| 세션 응답 | `/auth/me`, `/auth/session`, `/auth/logout` 응답 shape 정리 |
| Preferences | `selectedThemeIds` alias 추가 |
| Role enum | `R-USER`, `R-ADMIN`, `R-LOCAL-OPERATOR`, `R-DATA-PROVIDER` |

## 10. 최종 정리

Cognito 도입의 핵심은 Google/Kakao 로그인을 백엔드가 직접 처리하는 구조에서 벗어나, Cognito가 인증을 담당하고 Lovv 백엔드는 Cognito claims를 서비스 사용자/session shape로 변환하는 것이다.

현재 방향:

- Google/Kakao 직접 로그인 API는 legacy로 유지한다.
- Cognito Hosted UI/OIDC가 Social Login을 담당한다.
- Lovv 백엔드는 `/api/v1/auth/cognito/session`으로 bridge 처리한다.
- API Gateway JWT Authorizer 연결은 후속 Task로 분리한다.
- Role은 Cognito Group과 Lovv DB scope 조합으로 처리한다.
- 프론트는 Cognito token 기반으로 session/me를 호출해 서비스 상태를 복구한다.

## 11. 출처 및 근거

| 출처 | 확인 내용 | TS-04 반영 |
| --- | --- | --- |
| [Amazon Cognito - User pool managed login](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-managed-login.html) | Cognito managed login은 사용자 인증과 JWT 기반 인증 흐름을 제공한다. | Google/Kakao 인증 책임은 Cognito Hosted UI/OIDC로 이동하고, Lovv backend는 검증된 claims를 서비스 session shape로 변환한다. |
| [Amazon Cognito - Using social identity providers with a user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-social-idp.html) | Cognito user pool은 social IdP와 연동해 외부 provider 인증 결과를 user pool 사용자와 연결한다. | 기존 `/auth/google`, `/auth/kakao` provider token 직접 검증 API는 legacy로 두고, 신규 흐름은 Cognito bridge로 분리한다. |
| [Amazon Cognito - Understanding user pool JSON web tokens](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html) | ID token과 access token은 사용자 식별, scope, claims 정보를 포함한다. | 백엔드는 provider token이 아니라 Cognito JWT claims의 `sub`, `email`, `cognito:groups`를 기준으로 사용자/session을 구성한다. |
| [API Gateway - HTTP API JWT authorizer](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html) | API Gateway JWT authorizer는 Cognito 같은 IdP가 발급한 JWT를 검증하고 API 접근을 제어할 수 있다. | `/auth/cognito/session`은 API Gateway/JWT Authorizer가 검증한 claims를 전제로 처리한다. |
| [07_api_spec.md](../../../07_api_spec/07_api_spec.md) | `/auth/cognito/session`, legacy social login, role enum, logout 책임 경계, Cognito bearer auth 기준을 정의한다. | TS-04의 API 경로, 응답 shape, role 처리, logout 의미 분리 기준과 동기화한다. |
| [01_requirements.md](../../../01_requirements/01_requirements.md) | 최종 권한은 Lovv 서비스 DB의 활성 역할 할당을 기준으로 판단하고 Cognito Group은 보조 신호로만 사용한다고 정의한다. | Cognito Group만으로 관리자 권한을 확정하지 않고 Lovv DB scope와 조합해 검증한다. |

## 12. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.2 | 2026-07-09 | llm팀 | Cognito managed login, social IdP, JWT token, API Gateway JWT authorizer 공식 문서와 로컬 API/요구사항 근거 추가 |
| v0.1 | 2026-07-09 | llm팀 | Cognito / Social Login 책임 경계 충돌 이슈 초안 작성 |
