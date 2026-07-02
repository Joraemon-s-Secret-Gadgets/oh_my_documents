---
작성자: llm팀
상태: 진행후
---

# Backend 문서 전달 대상 조사

## 목적

`03_lovv_BE`에서 생성되었거나 유지 중인 백엔드 문서 중 `00_oh_my_documents`에 보조 문서로 복사해야 할 항목을 선별한다. 대표 문서 본문 통합은 별도 요청 전까지 하지 않고, 우선 원문 보존용 supplemental 문서로 전달하는 것을 기준으로 한다.

## 조사 기준

- 백엔드 구현/운영 사실을 설명하는 문서인가
- `00_oh_my_documents`의 대표 문서에 없는 세부 근거를 보강하는가
- 이미 복사한 TTL 문서와 중복되거나 오래된 판단을 다시 들여오지 않는가
- 대상 폴더 규칙상 `supplemental/` 보조 문서로 둘 수 있는가

## 현재 복사 완료

| BE 원본 | 대상 위치 | 판단 |
| --- | --- | --- |
| `docs/specs/DYNAMODB_TTL_REMEDIATION_EXECUTION_SPEC.md` | `docs/04_database_design/supplemental/backend_dynamodb_ttl_remediation_execution_spec.md` | 복사 완료. TTL writer 구현 상태와 경계 보존용 |
| `reports/dynamodb_ttl_status_review_20260630_ko.md` | `docs/04_database_design/supplemental/backend_dynamodb_ttl_status_review_20260630_ko.md` | 복사 완료. 현재 TTL 적용 상태 보고서 |

## 추가 복사 권장

| 우선순위 | BE 원본 | 권장 대상 위치 | 이유 |
| --- | --- | --- | --- |
| 높음 | `docs/specs/ADMIN_RBAC_SPEC.md` | `docs/07_api_spec/supplemental/backend_admin_rbac_spec.md` | 복사 완료. `oh_my_documents`에는 관리자 RBAC 요구사항과 간단한 API 목록은 있으나, 백엔드 권한 Source of Truth, 토큰 클레임, 오류 계약, 객체 단위 인가, 테스트 요구사항 상세가 부족함 |
| 높음 | `docs/specs/ADMIN_OPERATIONS_RUNBOOK.md` | `docs/11_deployment_ops/supplemental/backend_admin_operations_runbook.md` | 복사 완료. 관리자 콘솔 운영 흐름, 감사 로그, 모니터링 기준을 운영 문서 보조 자료로 보존할 필요가 있음 |
| 높음 | `reports/nat_instance_rds_access_report_20260618_ko.md` | `docs/11_deployment_ops/supplemental/backend_nat_instance_rds_access_report_20260618_ko.md` | 마스킹 후 복사 완료. private RDS를 public으로 열지 않고 SSM port forwarding으로 접근하는 실제 운영 절차와 장애 대응이 담겨 있음 |
| 중간 | `reports/aws_cost_optimization_infra_review_20260630_ko.md` | `docs/11_deployment_ops/supplemental/backend_aws_cost_optimization_infra_review_20260630_ko.md` | 마스킹 후 복사 완료. Terraform이 아니라 CloudFormation Data Stack이 비용 리소스를 소유한다는 판단과 Interface Endpoint/NAT/RDS 비용 절감 근거가 있음 |
| 중간 | `docs/LOCAL_DB_DOCKER.md` | `docs/11_deployment_ops/supplemental/backend_local_db_docker_guide.md` | 복사 완료. 로컬 MySQL 8.0, migration 순서, admin seed, 로컬 핸들러 실행 방법은 개발 운영 가이드로 유용함 |

## 보안 검토 결과

- 라이브 AWS access key, secret access key, bearer token, private key, client secret, RDS password 원문은 발견되지 않았다.
- `backend_nat_instance_rds_access_report_20260618_ko.md`와 `backend_aws_cost_optimization_infra_review_20260630_ko.md`는 AWS account id, EC2/VPC endpoint/security group id, public/private IP, RDS host, RDS username을 마스킹했다.
- `backend_local_db_docker_guide.md`의 `lovvlocal`은 로컬 Docker DB 전용 기본값이며 라이브 자격증명이 아니므로 유지했다.

## 조건부 복사

| BE 원본 | 권장 판단 | 이유 |
| --- | --- | --- |
| `docs/spec/nat_instance_spec.md` | 전체 인프라 설계 근거까지 보존해야 하면 `docs/06_technical_spec/supplemental/backend_nat_instance_spec.md`로 복사 | 운영 절차는 RDS 접속 보고서가 더 직접적이다. 설계 결정 이력까지 필요할 때만 복사 |
| `docs/plan/nat_instance_plan.md` | 실행 이력 보존이 필요하면 `plans/after/backend_nat_instance_plan.md`로 복사 | `oh_my_documents`의 문서 본문 보강보다는 작업 계획 이력 성격이 강함 |
| `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md` | TTL 변경 이력 전체가 필요하면 `docs/04_database_design/supplemental/backend_dynamodb_ttl_write_paths_spec.md`로 복사 | 이미 최신 remediation/status 문서를 복사했다. 오래된 "writer 없음" 상태가 섞여 있어 최신 문서보다 우선하면 안 됨 |
| `reports/dynamodb_ttl_application_write_analysis_20260618_ko.md` | TTL 과거 분석 근거가 필요할 때만 복사 | 최신 status review가 이 문서를 대체한다. 히스토리 보존 외에는 중복 |
| `infra/data-stack/README.md` | Data Stack 명령 모음까지 필요할 때만 `docs/11_deployment_ops/supplemental/backend_data_stack_readme.md`로 복사 | 운영 요약은 NAT/RDS 보고서와 비용 보고서가 더 문서화 가치가 높음 |

## 제외 권장

| 항목 | 제외 이유 |
| --- | --- |
| `infra/data-stack/template.yaml` | IaC 원본이지 `oh_my_documents`로 옮길 설명 문서가 아님 |
| `src/**`, `tests/**` | 백엔드 구현/검증 원본이며 문서 저장소 복사 대상이 아님 |
| `requirements*.txt` | 의존성 파일로 문서 전달 대상이 아님 |

## 작업 체크리스트

- [x] BE 저장소의 Markdown 문서 목록 확인
- [x] 신규/변경 문서와 기존 문서 구분
- [x] `oh_my_documents` 대상 폴더 규칙 확인
- [x] 기존 `oh_my_documents`의 관리자/RBAC, TTL, RDS/NAT, 비용 관련 중복 여부 검색
- [x] 추가 복사 권장 목록 작성
- [x] 사용자가 승인한 범위만 실제 복사
- [x] 복사 후 원본/대상 hash 또는 마스킹 검증
- [ ] 필요 시 대표 문서 통합 계획을 별도 작성

## 검증 방법

복사 단계에서는 다음을 확인한다.

```bash
git status --short
sha256sum <source> <copied-target>
```

대표 문서 본문에 반영할 경우에는 각 폴더의 `sections/*.md`를 먼저 갱신하고 대표 문서를 동기화한다.
