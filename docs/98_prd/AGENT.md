# Agent Instructions for PRD documents

이 폴더는 로브(Lovv) 프로젝트의 제품 요구사항 문서(PRD)를 모아 관리한다.

## Scope

- 서비스 전체 요구사항의 기준은 `../01_requirements/01_requirements.md`다.
- 이 폴더의 PRD는 특정 구축 범위, 파이프라인, 기능 묶음처럼 실행 단위가 분리된 제품 요구사항을 정의한다.
- PRD가 DB, 전처리, API, Agent, 운영 문서의 결정과 충돌하면 각 상세 문서의 최신 결정을 우선 확인하고 PRD에 반영한다.

## Documents

```text
db_build_prd.md          SAM 제외 데이터 스토어 구축 PRD
data_pipeline_prd.md     데이터 파이프라인 한정 PRD
s3_vector_index_prd.md   KR S3 vector index 구축 PRD (CEA 검색 요구 대조 기준. 구현 정본은 02_lovv_data_collect/docs/s3_vector_index_prd.md)
interactive_builder_prd.md  대화형 일정 빌더 + 메모리(단기 AgentCore / 장기 DynamoDB TTL→S3) 전환 PRD
```

## Editing Rules

- 새 PRD는 목적, 범위, 제외 범위, 기능 요구사항, 비기능 요구사항, 수용 기준, 변경 이력을 포함한다.
- PRD 제목에는 대상 범위를 명확히 적고, 제품 전체 PRD인지 범위 한정 PRD인지 상단에 표시한다.
- 구현 범위가 다른 상세 문서와 연결되면 관련 문서 경로를 PRD 안에 명시한다.
- PRD를 이동하거나 이름을 바꾸면 참조 링크와 이 문서의 목록을 함께 갱신한다.
