# 4. 현재 우선 운영 항목

| 영역 | 현재 기준 |
| --- | --- |
| 인증·인가 | Cognito Hosted UI/OIDC가 Social Login을 담당하고 Lovv backend는 `/api/v1/auth/cognito/session` bridge로 세션 shape를 구성 |
| 데이터 적재 | KR 상세 데이터는 `TourKoreaDomainData` 기준 |
| 검색 인덱스 | S3 vector index `kr-tour-domain-v1` 구축 기준 수립 |
| 그래프DB | 현재 직접 도입하지 않고 Lambda 기반 관계 탐색 보조 기능으로 유사 기능 구현 예정. Neptune은 승격 기준 충족 시 재검토 |
| 관리자 보안 | `R-ADMIN`/`R-SUPER-ADMIN` role union으로 일반 admin 조회를 허용하고, 고위험 승인·거절 시점에만 최근 5분 TOTP MFA를 요구 |
| 관리자 DB migration | 기본 product schema는 `infra/data-stack/rds/schema.sql`을 단일 기준으로 사용하고, admin 보강 migration은 `002_admin_console_tables.sql` → `003_admin_operations_tables.sql` → `004_admin_high_risk_approvals.sql` 순서로 적용 |
| 문서 배포 | `docs/` Markdown 원본 → `pages/*.html` 생성 |
| PDF 배포 | 대응 Markdown 원본 → `pdf/*.tex`/`pdf/*.pdf` 생성 |

## 4.1 관리자 보안 운영 Runbook

### 최초 Super Admin bootstrap

초기 운영 환경에는 최소 1명의 활성 `R-SUPER-ADMIN`이 있어야 한다. 최초 부여는 일반 콘솔 승인 플로우를 사용할 수 없으므로 BE 저장소의 `scripts/bootstrap_super_admin.py`로 수행한다.

```powershell
python scripts/bootstrap_super_admin.py --user-id <USER_UUID> --reason "initial super admin bootstrap"
```

- 실행자는 운영 승인 기록에 작업자, 대상 사용자, 사유, 실행 시각을 남긴다.
- bootstrap 이후에는 같은 사용자가 MFA 등록을 완료했는지 확인한다.
- 이후 `R-SUPER-ADMIN` 부여·회수는 고위험 변경 요청과 다른 `R-SUPER-ADMIN`의 승인으로만 처리한다.

### 접근 재검토와 권한 조회

분기별 access attestation은 활성 역할·지역 할당 전체를 대상으로 한다. 증적에는 토큰, 쿠키, MFA secret, recovery code, 민감 원문을 포함하지 않는다.

```powershell
python scripts/list_user_authz.py --user-id <USER_UUID>
mysql --execute="source scripts/admin_access_attestation.sql"
```

- 최초 부여자와 다른 최종 확인자가 유지·축소·회수 여부를 승인한다.
- 불필요한 `R-ADMIN`·`R-SUPER-ADMIN`은 1영업일 이내 회수하고 권한 캐시·활성 세션을 무효화한다.
- 마지막 활성 `R-SUPER-ADMIN` 회수는 애플리케이션 트랜잭션에서 거부되어야 한다.

### MFA 장애·잠금 대응

- `ADMIN_MFA_ENROLLMENT_REQUIRED`: 사용자가 MFA 등록을 완료하도록 안내한다.
- `ADMIN_MFA_REQUIRED`: `/admin/security/mfa/verify`로 TOTP 세션을 생성한 뒤 승인·거절을 재시도한다.
- `ADMIN_MFA_TOTP_REQUIRED`: recovery code 세션 또는 5분을 초과한 TOTP 세션이므로 새 TOTP 인증을 요구한다.
- `ADMIN_MFA_LOCKED`: 잠금 만료까지 대기하거나 운영 승인 후 MFA 자격 초기화 절차를 수행한다.
- recovery code는 계정 복구용이며 고위험 승인·거절용 인증 수단이 아니다.

### 고위험 승인 감사와 rollback 기준

고위험 승인 성공 시 대상 변경, 요청 상태 전이, 업무 action 감사 로그는 같은 트랜잭션에서 strict 기록한다. 감사 로그 기록이 실패하면 업무 변경도 롤백한다. 권한 거부, MFA 실패, 상태 충돌, 실행 실패는 원장 변경과 분리해 `denied` 또는 `failed` 감사 행으로 남긴다.

## 4.2 로컬 DB 초기화와 migration 운영

새 로컬 DB 초기화 순서는 다음과 같다.

1. `infra/data-stack/rds/schema.sql`
2. `schema/aurora_mysql/002_admin_console_tables.sql`
3. `schema/aurora_mysql/003_admin_operations_tables.sql`
4. `schema/aurora_mysql/004_admin_high_risk_approvals.sql`

`schema/aurora_mysql/001_product_api_tables.sql`은 삭제 유지 대상이다. 새 초기화나 migration 문서에서 필수 단계로 복구하지 않는다. 기존 운영·공유 DB에는 base schema를 재적용하지 않고 필요한 admin migration만 선택 적용한다. BE 저장소의 `scripts/apply_admin_migration.py`는 적용할 migration 파일을 명시해 사용한다.
