# 4. 물리 설계

## 4.1 MySQL 물리 설계 기준

| 기준 | 결정 |
| --- | --- |
| ID | `CHAR(36)` UUID 문자열을 기본으로 한다. |
| 시간 | `created_at`, `saved_at`을 기본 시간 컬럼으로 둔다. |
| 삭제 | 사용자 삭제 가능 데이터는 PoC 단순 모델에서는 hard delete를 우선하고, Production 확장 시 soft delete 컬럼 추가를 검토한다. |
| JSON | 추천 조건 스냅샷, 점수 상세, 일정 경로처럼 유연한 구조는 MySQL `JSON`을 사용한다. |
| 외래키 | 사용자, 소셜 계정, 일정, 일정 항목, 일정 반응 사이에는 FK를 둔다. 대량 로그는 FK 대신 참조 ID 문자열만 둔다. |

## 4.2 주요 인덱스

| 조회 패턴 | 인덱스 후보 |
| --- | --- |
| 현재 사용자 조회 | `users(email)`, `social_accounts(provider, provider_user_id)` |
| 사용자 저장 일정 | `itineraries(user_id, saved_at desc)` |
| 일정 항목 조회 | `itinerary_items(itinerary_id, sort_order)` |
| 사용자 일정 반응 이력 | `plan_reactions(user_id, created_at desc)` |
| 일정별 반응 집계 | `plan_reactions(itinerary_id, reaction_type)` |

## 4.3 DynamoDB 물리 설계 기준

| 기준 | 결정 |
| --- | --- |
| 파티션 분산 | 일자, 이벤트 타입, 해시 사용자 ID를 조합해 hot partition을 피한다. |
| 조회 단위 | 사용자 이벤트 타임라인, Agent run 단건 trace, API 일자별 장애 분석을 기준으로 PK/SK를 설계한다. |
| TTL | 로그성 테이블은 `expires_at`을 필수 속성으로 둔다. 권고·잠정 보존 기간은 5.1절을 따른다(법무·보안 검토로 확정). |
| GSI | `request_id`, `agent_run_id`, `recommendation_request_id`, `event_type` 조회가 필요하면 GSI를 추가한다. |
| Payload | 원문 대신 `payload_summary`, `error_code`, `result_ref`처럼 최소 요약만 저장한다. |

## 4.4 DynamoDB GSI 후보

| GSI | Partition Key | Sort Key | 용도 |
| --- | --- | --- | --- |
| `GSI1RequestLookup` | `request_id` | `created_at` | API 요청 단위 trace 연결 |
| `GSI2AgentRunLookup` | `agent_run_id` | `created_at` | Agent 실행 전체 단계 조회 |
| `GSI3EventTypeDaily` | `event_type#yyyyMMdd` | `created_at` | 이벤트 타입별 일자 분석 |
| `GSI4RecommendationLookup` | `recommendation_request_id` | `created_at` | 추천 요청과 로그 연결 |

## 4.5 S3 vector index 물리 설계 기준

| 기준 | 결정 |
| --- | --- |
| Index layout | 국가 또는 콘텐츠 유형별 prefix 분리를 검토하되 PoC는 단일 S3 vector index로 시작한다. |
| Vector ID | `source_type#source_id#chunk_no` 형식을 사용한다. |
| Metadata filter | `country`, `destination_id`, `city_id`, `content_type`, `theme_tags`, `recommended_months`, `source_type`을 필터로 둔다. |
| 원본 참조 | 각 vector record에는 `raw_s3_uri`, DynamoDB 정규화 문서 ID, 또는 MySQL 일정 ID를 함께 둔다. |
| 개인정보 | 사용자 ID, 대화 전문, 비공개 운영 메모는 metadata에 저장하지 않는다. |

## 4.6 Lambda 관계 탐색 물리 설계 기준

| 기준 | 결정 |
| --- | --- |
| 관계 ID | `city#{city_id}`, `festival#{festival_id}`, `theme#{theme_id}`, `place#{content_id}` 형식을 사용한다. |
| 관계 가중치 | `weight`, `confidence`, `source_id`, `updated_at`을 DynamoDB 인접 리스트와 사전계산 후보 공통 속성으로 둔다. |
| 재생성 기준 | DynamoDB 정규화 문서와 S3 Raw 원본을 기준으로 관계 후보를 배치 재생성할 수 있게 한다. |
| 개인정보 | 사용자 ID, 대화 전문, 비공개 운영 메모는 관계 탐색 입력과 캐시에 저장하지 않는다. |
| 조회 패턴 | 도시 기준 2-hop 이내 테마·축제·장소 확장, 인접 도시 후보 탐색, 축제 일정 관계 검증을 우선한다. |
| 실행 방식 | Lambda가 DynamoDB 인접 리스트, 사전계산 후보 테이블, S3 vector metadata를 읽어 요청 시 후보 확장·재랭킹을 수행한다. |

## 4.7 관리자 MFA 테이블

관리자 Step-up MFA는 로그인 원장과 분리해 관리자 도메인 테이블에 저장한다. TOTP secret은 서버 측 KMS로 암호화하고, 복구 코드는 원문을 저장하지 않는다.

`admin_mfa_credentials`와 `admin_mfa_sessions`의 DDL source of truth는 `schema/aurora_mysql/004_admin_high_risk_approvals.sql`이다. `schema/aurora_mysql/002_admin_console_tables.sql`에는 두 테이블을 중복 정의하지 않는다.

### `admin_mfa_credentials`

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| `user_id` | `CHAR(36)` | `users.id` 참조, 사용자별 MFA 자격 PK |
| `encrypted_secret` | `TEXT` | KMS 암호화 TOTP secret |
| `status` | `VARCHAR(20)` | `pending`, `active`, `revoked` |
| `last_used_counter` | `BIGINT` | TOTP 재사용 방지용 마지막 counter |
| `recovery_codes_json` | `JSON` | scrypt 해시·salt 형태의 복구 코드 목록 |
| `failed_attempts` | `INT` | 연속 실패 횟수 |
| `locked_until` | `DATETIME(3)` | 일시 잠금 만료 시각 |
| `enrolled_at` | `DATETIME(3)` | 등록 시작 시각 |
| `confirmed_at` | `DATETIME(3)` | 등록 확인 시각 |
| `updated_at` | `DATETIME(3)` | 마지막 갱신 시각 |

### `admin_mfa_sessions`

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| `session_id` | `VARCHAR(120)` | 로그인 세션 식별자, MFA 세션 PK |
| `user_id` | `CHAR(36)` | `users.id` 참조 |
| `verified_at` | `DATETIME(3)` | MFA 인증 시각 |
| `expires_at` | `DATETIME(3)` | MFA 인증 만료 시각 |
| `method` | `VARCHAR(30)` | `totp`, `recovery_code` |
| `created_at` | `DATETIME(3)` | 생성 시각 |
| `updated_at` | `DATETIME(3)` | 마지막 갱신 시각 |

주요 조회 인덱스는 `admin_mfa_sessions(user_id, expires_at)`이며, 만료 세션 정리는 운영 배치 또는 주기적 청소 작업에서 수행한다.

## 4.8 관리자 고위험 변경·감사 테이블

### `admin_high_risk_change_requests`

`admin_high_risk_change_requests`의 DDL source of truth는 `schema/aurora_mysql/004_admin_high_risk_approvals.sql`이다. 기본 product tables는 `infra/data-stack/rds/schema.sql`을 단일 기준으로 두며, 삭제된 `schema/aurora_mysql/001_product_api_tables.sql`을 다시 생성하거나 로컬 초기화 순서에 포함하지 않는다.

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| `id` | `CHAR(36)` | 고위험 변경 요청 PK |
| `operation_type` | `VARCHAR(40)` | `role_grant`, `role_revoke`, `region_grant`, `region_revoke`, `bulk_publish` |
| `target_user_id` | `CHAR(36)` | 역할·지역 변경 대상 `users.id`, 대량 게시에서는 `NULL` |
| `payload_json` | `JSON` | 검증·정규화된 작업 입력 |
| `status` | `VARCHAR(20)` | `pending`, `executed`, `rejected` |
| `reason` | `VARCHAR(500)` | 요청 사유 |
| `requested_by` | `CHAR(36)` | 요청자 `users.id` |
| `decided_by` | `CHAR(36)` | 결정한 `R-SUPER-ADMIN`의 `users.id` |
| `decision_reason` | `VARCHAR(500)` | 승인 선택 사유 또는 필수 거절 사유 |
| `requested_at` | `DATETIME(3)` | 요청 시각 |
| `decided_at` | `DATETIME(3)` | 결정 시각 |
| `executed_at` | `DATETIME(3)` | 승인 후 실행 완료 시각 |
| `execution_summary_json` | `JSON` | 변경 건수·게시 반영 작업 수 등 비민감 실행 요약 |
| `updated_at` | `DATETIME(3)` | 마지막 변경 시각 |

조회 인덱스는 `(status, requested_at)`, `(operation_type, requested_at)`, `(target_user_id, requested_at)`, `(requested_by, requested_at)`를 둔다. `decided_by <> requested_by`, 결정·실행 시각이 요청 시각보다 빠르지 않다는 CHECK 제약을 적용한다.

### `admin_audit_logs` C4 기록 계약

`admin_audit_logs`는 `actor_user_id`, `session_id`, 역할·기관·지역 스냅샷, `action`, 리소스 유형·ID, `result`, `reason_code`, `request_id`, 변경 전·후 요약과 비민감 metadata를 저장한다. `result`는 `allowed`, `denied`, `succeeded`, `failed`로 제한한다.

| 고위험 단계 | 필수 `action` | 리소스/결과 |
| --- | --- | --- |
| 요청 생성 | `high_risk_request.create` | `high_risk_request`, `succeeded` 또는 `failed` |
| 승인 결정 | `high_risk_request.approve` | `high_risk_request`, `succeeded` 또는 `failed` |
| 거절 결정 | `high_risk_request.reject` | `high_risk_request`, `succeeded` 또는 `failed` |
| 역할 실행 | `role_grant.execute`, `role_revoke.execute` | 대상 사용자·역할 변경 요약 |
| 지역 실행 | `region_grant.execute`, `region_revoke.execute` | 대상 사용자·지역 변경 요약 |
| 대량 게시 실행 | `bulk_publish.execute` | 게시 건수·반영 작업 건수 요약 |
| 권한·MFA·상태 거부 | 요청 action 또는 보호 API action | `denied`, 표준 `reason_code` |

성공한 고위험 승인에서는 대상 변경, `executed` 상태 전이, 실행 action과 승인 action 감사 행을 동일 트랜잭션에 기록한다. 권한·MFA·상태 검증에서 거부되거나 실행이 롤백된 시도는 원장 변경 트랜잭션과 분리한 `denied`·`failed` 결과 행으로 남긴다. 인덱스는 `(actor_user_id, occurred_at)`, `(resource_type, resource_id, occurred_at)`, `request_id`, `(action, result, occurred_at)`를 둔다.

## 4.9 로컬 DB 초기화와 admin migration 순서

로컬 DB를 새로 초기화할 때는 현재 남아 있는 schema/migration 파일만 사용한다.

1. `infra/data-stack/rds/schema.sql`
2. `schema/aurora_mysql/002_admin_console_tables.sql`
3. `schema/aurora_mysql/003_admin_operations_tables.sql`
4. `schema/aurora_mysql/004_admin_high_risk_approvals.sql`

`schema/aurora_mysql/001_product_api_tables.sql` 삭제는 유지한다. 기존 운영·공유 DB에는 base schema를 재적용하지 않고, 필요한 admin migration만 선택 적용한다. `scripts/apply_admin_migration.py`를 사용할 때는 대상 migration 파일을 명시해 적용 범위를 제한한다.
