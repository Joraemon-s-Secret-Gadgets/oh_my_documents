# 로브 (Lovv) 배포·운영 가이드

> 문서 버전: v0.5
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-12
> 작성자: llm팀
> 기준 문서: `../06_technical_spec/06_technical_spec.md`, `../07_api_spec/07_api_spec.md`, `../08_data_preprocessing/data_preprocessing_plan.md`, `../04_database_design/04_database_design.md`, `supplemental/troubleshooting.md`

---

> **[PRD 반영 v0.1 — 대화형 빌더]** 관측: **OTel + AWS X-Ray + CloudWatch Structured JSON Logs**로
> 노드별 토큰·컨텍스트·레이턴시·I/O 트레이싱(정본: `Lovv-agent/docs/specs/LOVV_AGENTCORE_OBSERVABILITY_SPEC.md`).
> CI/CD: 기존 게이트(pytest·compileall·parity·`agentcore validate`/`deploy --dry-run`) + 빌더 게이트
> (무상태 회귀·state serde round-trip·geo-filter·soft floor 폴백·정합성 게이트·interrupt/resume 스모크).
> 상세: `../98_prd/interactive_builder_prd.md`.
# 1. 문서 개요

이 문서는 로브(Lovv) 서비스의 배포와 운영 절차를 정리하는 대표 문서다. 현재는 상세 운영 절차가 확정되기 전 단계이므로, 운영 중 확인해야 할 기준 문서와 트러블슈팅 문서를 연결하는 역할을 한다.
# 2. 운영 문서 구성

| 문서 | 역할 |
| --- | --- |
| `11_deployment_ops.md` | 배포·운영 대표 문서 |
| `supplemental/troubleshooting.md` | 프로젝트 진행 중 발생한 주요 이슈와 대응 기준 |
| `../06_technical_spec/06_technical_spec.md` | 인프라와 기술 선택 근거 |
| `../07_api_spec/07_api_spec.md` | API 계약과 오류 응답 기준 |
| `../04_database_design/04_database_design.md` | schema source of truth와 admin migration 적용 순서 |
| `../08_data_preprocessing/` | 데이터 전처리와 적재 운영 기준 |
# 3. 운영 원칙

- 설계 결정의 "왜"는 기술 명세서에 두고, 이 문서는 "어떻게 배포·운영하는가"에 집중한다.
- 환경 변수와 secret은 실제 값을 문서에 쓰지 않고 관리 방식만 기록한다.
- 장애나 의사결정 이슈는 `supplemental/troubleshooting.md`에 증상, 원인, 판단, 조치, 재발 방지 기준으로 남긴다.
- HTML/PDF 공유 산출물은 원본 Markdown과 함께 검증한 뒤 배포한다.
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
# 5. 검증 명령

HTML 문서 구조 검증:

```powershell
python scripts\generate_pages.py
python scripts\verify_pages_structure.py
```

관리자 보안·로컬 DB 문서 정합성 검증:

```powershell
rg -n "001_product_api_tables|전역 MFA|global MFA|MFA 게이트|MFA gate|admin.*MFA.*필수" docs\01_requirements docs\04_database_design docs\07_api_spec docs\09_ui_ux_guide docs\10_test_plan
git diff --check
```

BE 저장소에서 확인할 관리자 보안 테스트:

```powershell
$env:PYTHONPATH='src'
python -m unittest
python -m unittest tests.test_admin_high_risk_app
python -m unittest tests.test_admin_mfa_app.AdminMfaAppTest.test_admin_read_routes_need_role_only_and_mfa_status_is_accessible
```

admin_web 저장소에서 확인할 프론트 검증:

```powershell
npm.cmd run lint
npm.cmd test
npm.cmd run build
```

opt-in 실DB 통합 테스트는 일반 unittest에서 skip되는 별도 검증이다. 실행하지 않았다면 완료로 표기하지 않는다.

```powershell
$env:RUN_ADMIN_DB_INTEGRATION='1'
$env:RUN_RDS_DATA_API_INTEGRATION='1'
python -m unittest
```

`docker compose config`는 compose 파일이 있는 BE/admin_web 작업 폴더에서 실행한다. 이 문서 저장소에 compose 파일이 없으면 실행 불가로 구분 기록한다.

PDF 문서 검증:

```powershell
cd pdf
xelatex -interaction=nonstopmode -halt-on-error <target>.tex
xelatex -interaction=nonstopmode -halt-on-error <target>.tex
```
# 6. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.5 | 2026-07-02 | Codex | 관리자 Super Admin bootstrap, access attestation, MFA 장애 대응, strict audit rollback, 로컬 DB 초기화·admin migration 순서와 opt-in 실DB 테스트 구분 추가 |
| v0.3 | 2026-06-12 | llm팀 | 그래프DB 직접 도입 대신 Lambda 기반 관계 탐색 보조 기능 구현 예정으로 운영 기준 조정 |
| v0.2 | 2026-06-12 | llm팀 | Cognito/Social Login 운영 기준을 현재 우선 운영 항목에 추가 |
| v0.1 | 2026-06-12 | llm팀 | 배포·운영 대표 문서 초안 작성 및 트러블슈팅 문서 연결 |
