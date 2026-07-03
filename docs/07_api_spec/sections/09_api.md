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
