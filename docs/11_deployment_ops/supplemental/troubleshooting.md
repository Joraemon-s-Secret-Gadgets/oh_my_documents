# 로브 (Lovv) 트러블슈팅 문서

> 문서 성격: 보조 Markdown
> 대표 문서: `../11_deployment_ops.md`

> 문서 버전: v0.14
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-12
> 작성자: llm팀
> 기준 문서: `../../04_database_design/04_database_design.md`, `../../04_database_design/supplemental/neptune_alternative.md`, `../../07_api_spec/07_api_spec.md`, `../../08_data_preprocessing/supplemental/korea_data_preprocessing_result_report.md`, `../../08_data_preprocessing/supplemental/s3_vector_index_plan.md`, `../../99_pptx/01_midterm_presentation/01_midterm_presentation.md`
> 문서 목적: 프로젝트 진행 중 발생한 주요 이슈를 원인, 판단, 조치, 재발 방지 기준으로 정리해 발표와 운영 문서에서 함께 사용할 수 있게 한다.

---

# 1. 문서 개요

이 문서는 로브(Lovv) 프로젝트에서 발생했거나 현재 운영 기준상 주의해야 하는 이슈를 트러블슈팅 관점으로 정리한다.

정리 기준은 다음과 같다.

| 기준 | 설명 |
| --- | --- |
| 증상 | 겉으로 드러난 문제 또는 의사결정이 필요했던 지점 |
| 원인 | 기술적·운영적 원인 |
| 판단 | 왜 해당 방향으로 결정했는지 |
| 조치 | 실제로 취한 대응 또는 현재 적용할 대응 |
| 재발 방지 | 같은 문제가 반복되지 않도록 남기는 기준 |

# 2. 요약

| ID | 이슈 | 현재 상태 | 핵심 조치 | 상세 문서 |
| --- | --- | --- | --- | --- |
| TS-01 | Neptune 도입 범위 판단 | Lambda 대체 구현 예정 | 그래프DB 직접 도입 대신 DynamoDB 인접 리스트, 사전계산 후보 테이블, Lambda 인메모리 그래프로 유사 기능 구현 | `troubleshooting/ts-01_neptune_scope_decision.md` |
| TS-02 | S3 vector index 계약 정합성 | 진행 기준 확정 | Titan V2 1024/cosine, 3분절 vector ID, GSI3 export 기준 확정 | `troubleshooting/ts-02_s3_vector_index_contract.md` |
| TS-03 | PDF 산출물 생성·검증 | 대응 완료 | `xelatex` 2회 실행, PDF/TeX 산출물과 `pdf/AGENT.md` 목록 동기화 | `troubleshooting/ts-03_pdf_artifact_generation_verification.md` |
| TS-04 | Cognito / Social Login 책임 경계 충돌 | 기준 확정 | Google/Kakao 직접 검증 API는 legacy로 내리고 Cognito bridge API를 신설 | `troubleshooting/ts-04_cognito_social_login_boundary.md` |
| TS-05 | 식당 데이터 취득 범위 조정 | 기준 확정 | 식당 데이터 직접 취득 대신 Kakao Map API 조회로 대체 | `troubleshooting/ts-05_restaurant_data_scope_decision.md` |
| TS-06 | 일본 데이터 취득 포기 | 기준 확정 | CC BY 4.0 기준으로 처리하려던 일본 데이터 후보를 세부 규약 제한으로 취득 중단 | `troubleshooting/ts-06_japan_data_license_terms_mismatch.md` |

# 3. 상세 문서 인덱스

각 TS 항목의 상세 문제, 원인, 판단, 조치, 재발 방지 내용은 하위 문서에서 관리한다.

| ID | 하위 문서 |
| --- | --- |
| TS-01 | `troubleshooting/ts-01_neptune_scope_decision.md` |
| TS-02 | `troubleshooting/ts-02_s3_vector_index_contract.md` |
| TS-03 | `troubleshooting/ts-03_pdf_artifact_generation_verification.md` |
| TS-04 | `troubleshooting/ts-04_cognito_social_login_boundary.md` |
| TS-05 | `troubleshooting/ts-05_restaurant_data_scope_decision.md` |
| TS-06 | `troubleshooting/ts-06_japan_data_license_terms_mismatch.md` |

# 4. 발표용 트러블슈팅 요약 문구

중간발표에서 한 장으로 설명할 때는 다음 구조로 축약한다.

```text
이슈: 그래프DB가 필요해 보였지만 PoC 관계는 대부분 1~2-hop이었다.
판단: Neptune은 지금 넣으면 비용과 운영 복잡도가 먼저 커진다.
대응: 그래프DB 직접 도입 대신 Lambda로 유사 관계 탐색 기능을 구현한다.
구현: DynamoDB 인접 리스트, 사전계산 후보 테이블, Lambda 인메모리 그래프를 조합한다.
기준: 3-hop 이상 관계 탐색이나 실시간 그래프 쓰기가 병목이 되면 Neptune으로 승격한다.
```

# 5. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.14 | 2026-07-09 | llm팀 | TS-02~TS-05에 공식 문서 및 로컬 대표 문서 기반 출처·근거 섹션 추가 |
| v0.13 | 2026-07-09 | llm팀 | TS-06에 CC BY 4.0, PDL 1.0 및 관련 출처별 라이센스·규약 원문 링크를 첨부 |
| v0.12 | 2026-07-09 | llm팀 | TS-06 요약을 CC BY 4.0 처리 후보가 세부 규약 제한으로 중단된 흐름으로 정정 |
| v0.11 | 2026-07-09 | llm팀 | TS-06 요약에서 일본 데이터 전체를 오픈 라이센스로 일반화하지 않도록 표현 정정 |
| v0.10 | 2026-07-09 | llm팀 | TS-06에 일본 정부·공공 운영 출처의 이용조건 조사 결과를 추가 |
| v0.9 | 2026-07-09 | llm팀 | TS-06에 JATO 공식 사이트와 회원규약 조사 결과를 보강 |
| v0.8 | 2026-07-09 | llm팀 | 일본 데이터 라이센스와 데이터 규약 불일치로 취득을 포기한 사례를 TS-06으로 추가 |
| v0.7 | 2026-07-09 | llm팀 | 개인/작업 방식 이슈였던 기존 TS-03, TS-05를 제거하고 후속 TS 항목을 TS-03~TS-05로 재번호 매김 |
| v0.6 | 2026-07-09 | llm팀 | 개인 로컬 환경 이슈였던 기존 KR 전처리 적재 기준 항목을 제거하고 후속 TS 항목을 재번호 매김 |
| v0.5 | 2026-07-09 | llm팀 | TS 상세 내용을 하위 문서로 분리하고 본 문서를 인덱스 중심으로 재정리 |
| v0.4 | 2026-07-09 | llm팀 | 식당 데이터 취득 범위 조정 이슈를 추가하고 하위 상세 문서 연결 |
| v0.3 | 2026-06-12 | llm팀 | 그래프DB 직접 도입 대신 Lambda 기반 관계 탐색 보조 기능 구현 예정으로 TS-01 방향 명확화 |
| v0.2 | 2026-06-12 | llm팀 | Cognito/Social Login 책임 경계, bridge session API, claims 검증, SAM route, logout, role scope, API 명세 반영 기준 추가 |
| v0.1 | 2026-06-12 | llm팀 | Neptune 도입 판단, KR 전처리, S3 vector index, HTML/PDF 산출물, 발표 HTML 검증 이슈를 트러블슈팅 문서로 초안화 |
