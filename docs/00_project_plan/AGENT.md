# Agent Instructions for project plan

`00_project_plan.md`는 로브 서비스의 상위 기획 문서다. 이 문서는 독립적으로 새로운 요구사항을 만들어내는 문서가 아니라, 다른 상세 문서의 확정 내용을 반영하는 요약·정렬 문서로 관리한다.

## Required Context

이 파일을 수정하기 전에는 다음 문서의 최신 내용을 확인한다. 아래 문서는 읽기 전용 참조이며, 프로젝트 기획서 동기화 작업만으로 수정하지 않는다.

- `../01_requirements/01_requirements.md`
- `../02_service_flow/02_service_flow.md`
- `../03_data_collect_plan/03_data_collect_plan.md`
- `../04_database_design/04_database_design.md`
- `../05_agent_spec/05_agent_spec.md`
- `../06_technical_spec/06_technical_spec.md`
- `../07_api_spec/07_api_spec.md`

## Update Policy

- 요구사항, API, DB, Agent, 서비스 흐름의 세부 결정은 각 상세 문서를 우선한다.
- 프로젝트 목표, 범위, 일정, 성공 기준은 상세 문서의 최신 결정과 모순되지 않게 갱신한다.
- 상세 문서에 없는 새 기능이나 범위를 프로젝트 기획서에 먼저 추가하지 않는다.
- 기획서 문구를 바꿀 때는 어떤 상세 문서의 내용을 반영했는지 추적 가능하게 표현한다.
- 상세 문서는 사용자가 해당 상세 문서 수정을 요청했거나, 상세 문서 자체를 업데이트하는 작업일 때만 Agent가 수정한다.

## Output Rule

기획서를 수정한 뒤에는 `pages/00_project_plan.html` 같은 생성물이 있는지 확인하고, 존재한다면 같은 변경을 반영한다. 현재 생성물이 없으면 `index.html` 링크 구조만 깨지지 않는지 확인한다.

## PDF Rule Reference

프로젝트 기획서 PDF 생성과 스타일 규칙은 `../../pdf/AGENT.md`에서 관리한다.
