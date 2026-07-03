---
작성자: llm팀
상태: 진행후
---

# Data Collect 문서 전달 대상 조사

## 목적

`02_lovv_data_collect`에서 현재 운영 기준으로 확인해야 하는 데이터 수집, 전처리, DynamoDB, S3 Vector, AgentCore 조회 문서를 `00_oh_my_documents/data_collect_documents_20260702/`에 직접 적재한다.

대표 문서 본문 통합은 별도 요청 전까지 하지 않고, 우선 원문 보존용 전달 패키지로 보관하는 것을 기준으로 한다.

## 조사 기준

- 현재 KR V2 운영 상태나 완료 판단을 설명하는 문서인가
- `00_oh_my_documents` 대표 문서에 없는 세부 근거를 보강하는가
- Task 실행 지시서나 agent 운영 규칙처럼 문서 저장소에 복사할 필요가 낮은 파일은 제외한다
- `00_oh_my_documents` repo 바로 아래에서 확인 가능한 독립 전달 패키지로 둘 수 있는가

## 복사 완료

| 원본 | 대상 위치 | 판단 |
| --- | --- | --- |
| `docs/reports/kr_data_acquisition_report_20260629.md` | `data_collect_kr_data_acquisition_report_20260629.md` | KR raw 취득/보정 완료 근거 |
| `docs/reports/kr_20260629_preprocessing_report.md` | `data_collect_kr_20260629_preprocessing_report.md` | 20260629 raw detail 전체 전처리 결과 및 적재 예측 보고 |
| `docs/specs/kr_20260629_preprocessing_redesign_spec.md` | `data_collect_kr_20260629_preprocessing_redesign_spec.md` | 20260629 raw 기반 V2 전처리 설계 근거 |
| `docs/reports/kr_20260630_preprocessing_completion_report.md` | `data_collect_kr_20260630_preprocessing_completion_report.md` | 전처리, DynamoDB V2, Vector V2 완료 보고 |
| `docs/reports/korea_data_preprocessing_result_report.md` | `data_collect_korea_data_preprocessing_result_report.md` | 20260610 KR 상세 Raw JSON 전처리 결과 보고 |
| `docs/reports/preprocessing_report.md` | `data_collect_preprocessing_report.md` | KR 상세 데이터 전처리 완료 보고 |
| `docs/reports/kr_vector_count_discrepancy_analysis_20260630.md` | `data_collect_kr_vector_count_discrepancy_analysis_20260630.md` | Vector count 차이 분석 근거 |
| `docs/reports/kr_vector_metadata_refresh_plan_20260630.md` | `data_collect_kr_vector_metadata_refresh_plan_20260630.md` | Vector metadata refresh 계획 |
| `docs/guides/dynamodb_v2_query_guide.md` | `data_collect_dynamodb_v2_query_guide.md` | `TourKoreaDomainDataV2` 조회 계약 |
| `docs/guides/dynamodb_vector_v2_usage_guide.md` | `data_collect_dynamodb_vector_v2_usage_guide.md` | DynamoDB V2와 S3 Vector V2 연동 계약 |
| `docs/agentcore_v1_dynamodb_query_guide.md` | `data_collect_agentcore_v1_dynamodb_query_guide.md` | AgentCore v1 DynamoDB 조회 보조 자료 |
| `docs/agentcore_v1_vector_guide.md` | `data_collect_agentcore_v1_vector_guide.md` | AgentCore v1 Vector 조회 보조 자료 |
| `docs/guides/vector_search_v2_guide.md` | `data_collect_vector_search_v2_guide.md` | S3 Vector 검색 사용 예시 |
| `docs/reports/kr_lambda_sfn_batch_reset_completion_20260630.md` | `data_collect_kr_lambda_sfn_batch_reset_completion_20260630.md` | Lambda/SFN reset 및 rebuild 운영 완료 보고 |
| `docs/reports/kr_lambda_sfn_batch_reset_next_session_handoff_20260630.md` | `data_collect_kr_lambda_sfn_batch_reset_next_session_handoff_20260630.md` | 다음 세션 운영 handoff |
| `docs/reports/lambda_titan_vector_enrichment_analysis_20260630.md` | `data_collect_lambda_titan_vector_enrichment_analysis_20260630.md` | Titan embedding/vector enrichment 운영 분석 |

## 보안 처리

- 복사본의 12자리 AWS account id는 `<AWS_ACCOUNT_ID>`로 마스킹했다.
- 2026-07-03에 추가 복사한 전처리 보고서들도 동일한 마스킹 규칙을 적용했다.
- `.env`, `.env.local`, 로그, 원천 데이터 파일, 코드 파일은 복사하지 않았다.
- S3 bucket, DynamoDB table, Vector index 이름은 문서의 운영 의미를 유지하기 위해 보존했다.

## 정식 docs 적재 완료

2026-07-03에 루트 전달 패키지의 문서를 현재 `docs/` 폴더 구조에 맞게 아래 위치로 적재했다. 원문 보존용 전달 패키지는 삭제하지 않는다.

| 전달 패키지 파일 | 정식 적재 위치 |
| --- | --- |
| `data_collect_kr_data_acquisition_report_20260629.md` | `docs/03_data_collect_plan/supplemental/kr_data_acquisition_report_20260629.md` |
| `data_collect_dynamodb_v2_query_guide.md` | `docs/04_database_design/supplemental/dynamodb_v2_query_guide.md` |
| `data_collect_dynamodb_vector_v2_usage_guide.md` | `docs/04_database_design/supplemental/dynamodb_vector_v2_usage_guide.md` |
| `data_collect_agentcore_v1_dynamodb_query_guide.md` | `docs/05_agent_spec/supplemental/agentcore_v1_dynamodb_query_guide.md` |
| `data_collect_agentcore_v1_vector_guide.md` | `docs/05_agent_spec/supplemental/agentcore_v1_vector_guide.md` |
| `data_collect_korea_data_preprocessing_result_report.md` | `docs/08_data_preprocessing/supplemental/korea_data_preprocessing_result_report.md` |
| `data_collect_kr_20260629_preprocessing_redesign_spec.md` | `docs/08_data_preprocessing/supplemental/kr_20260629_preprocessing_redesign_spec.md` |
| `data_collect_kr_20260629_preprocessing_report.md` | `docs/08_data_preprocessing/supplemental/kr_20260629_preprocessing_report.md` |
| `data_collect_kr_20260630_preprocessing_completion_report.md` | `docs/08_data_preprocessing/supplemental/kr_20260630_preprocessing_completion_report.md` |
| `data_collect_kr_vector_count_discrepancy_analysis_20260630.md` | `docs/08_data_preprocessing/supplemental/kr_vector_count_discrepancy_analysis_20260630.md` |
| `data_collect_kr_vector_metadata_refresh_plan_20260630.md` | `docs/08_data_preprocessing/supplemental/kr_vector_metadata_refresh_plan_20260630.md` |
| `data_collect_lambda_titan_vector_enrichment_analysis_20260630.md` | `docs/08_data_preprocessing/supplemental/lambda_titan_vector_enrichment_analysis_20260630.md` |
| `data_collect_preprocessing_report.md` | `docs/08_data_preprocessing/supplemental/preprocessing_report.md` |
| `data_collect_vector_search_v2_guide.md` | `docs/08_data_preprocessing/supplemental/vector_search_v2_guide.md` |
| `data_collect_kr_lambda_sfn_batch_reset_completion_20260630.md` | `docs/11_deployment_ops/supplemental/kr_lambda_sfn_batch_reset_completion_20260630.md` |
| `data_collect_kr_lambda_sfn_batch_reset_next_session_handoff_20260630.md` | `docs/11_deployment_ops/supplemental/kr_lambda_sfn_batch_reset_next_session_handoff_20260630.md` |

## 제외

| 항목 | 제외 이유 |
| --- | --- |
| `docs/agents/**`, `AGENTS.md`, `AGENTS.ko.md` | agent 운영 규칙이며 문서 저장소의 제품/운영 문서가 아님 |
| `docs/specs/TASK*_SUBTASKS.md`, `docs/reports/TASK*_COMPLETION.md` | 작업 실행/완료 관리 문서로 대표 문서 보강보다 세션 관리 성격이 강함 |
| `docs/prompts/**` | 대화 프롬프트 템플릿으로 사용자-facing 문서 적재 대상이 아님 |
| `.env`, `logs/**`, `data/**`, `src/**`, `scripts/**` | 환경값, 실행 로그, 원천 데이터, 코드/스크립트로 문서 저장소 복사 대상이 아님 |

## 검증 방법

- `git status --short`로 신규 적재 파일 목록을 확인한다.
- `data_collect_documents_20260702/`에서 12자리 AWS account id, access key, secret access key, private key 패턴이 남아 있지 않은지 확인한다.
