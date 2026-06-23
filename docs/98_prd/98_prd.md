# 로브 (Lovv) PRD 대표 문서

> 문서 버전: v0.1
> 문서 상태: 검토 중 (Review)
> 작성일: 2026-06-23
> 문서 성격: 대표 Markdown
> 기준 문서: `../00_project_plan/00_project_plan.md`, `../01_requirements/01_requirements.md`, `../02_service_flow/02_service_flow.md`

# 1. 문서 목적

이 문서는 `docs/98_prd/` 하위 PRD의 대표 문서다. 각 PRD는 제품 전체 요구사항을 대체하지 않고, 구현 범위가 분리된 실행 단위의 목적, 범위, 수용 기준, 제외 범위를 정의한다.

서비스 전체 기준은 `../01_requirements/01_requirements.md`와 각 상세 설계 문서에 둔다. PRD가 상세 설계와 충돌하면 최신 상세 문서의 결정을 우선하고, PRD는 해당 결정에 맞게 갱신한다.

# 2. PRD 목록

| PRD | 범위 | 대표 연결 문서 |
| --- | --- | --- |
| `data_pipeline_prd.md` | 한국 관광 데이터 취득 산출물 이후의 S3 Raw 적재, Lambda 전처리, DynamoDB 적재 | `../03_data_collect_plan/03_data_collect_plan.md`, `../08_data_preprocessing/data_preprocessing_plan.md` |
| `db_build_prd.md` | SAM 앱 스택과 분리된 RDS, DynamoDB, S3 데이터 스토어 구축 | `../04_database_design/04_database_design.md`, `../06_technical_spec/06_technical_spec.md` |
| `s3_vector_index_prd.md` | KR S3 Vector Index 구축과 Candidate Evidence Agent 검색 요구 충족 | `../08_data_preprocessing/s3_vector_index_plan.md`, `../05_agent_spec/candidate_evidence_agent.md` |
| `interactive_builder_prd.md` | 대화형 일정 빌더, 메모리·상태 아키텍처, 관측성 전환 | `../05_agent_spec/05_agent_spec.md`, `../04_database_design/04_database_design.md`, `../02_service_flow/02_service_flow.md` |

# 3. 작성 원칙

- PRD 제목과 상단 메타데이터에 범위 한정 여부를 명시한다.
- 제품 전체 PRD가 아니면 `제품 전체 PRD 아님` 또는 동등한 범위 제한 문구를 유지한다.
- 구현 대상과 제외 범위를 표로 분리한다.
- 관련 대표 문서와 충돌 가능성이 있으면 PRD 안에 기준 문서를 명시한다.
- PRD가 확정되어 대표 설계 문서에 반영되면 이 문서의 목록과 상태를 함께 갱신한다.

# 4. 상태 요약

| PRD | 상태 | 비고 |
| --- | --- | --- |
| 데이터 파이프라인 PRD | Draft | 취득 repo를 업스트림으로 두고 Load/Transform/Load 범위 정의 |
| DB 구축 PRD | Draft | SAM 제외 데이터 스토어 구축 범위 정의 |
| S3 Vector Index PRD | Draft | Candidate Evidence Agent 검색 요구와 인덱스 계약 대조 |
| 대화형 일정 빌더 PRD | Draft | HITL 빌더와 AgentCore Memory 전환 범위 정의 |

# 5. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-23 | 로브 기획팀 | PRD 폴더 대표 문서 생성, 실행 단위 PRD 목록과 관리 원칙 정리 |
