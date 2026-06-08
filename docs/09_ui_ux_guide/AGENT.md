# Agent Instructions for UI/UX guide

이 폴더는 로브(Lovv) UI/UX 가이드를 관리한다.

## Primary Document

대표 문서는 `09_ui_ux_guide.md`다. 화면 구성, 인터랙션 흐름, 컴포넌트 규칙, 디자인 토큰(색상·타이포·간격), 접근성 기준을 정의한다.

## Dependencies

- 요구사항 기준: `../01_requirements/01_requirements.md`
- 서비스 흐름: `../02_service_flow/02_service_flow.md`
- 기술 명세(프론트엔드 화면·상태): `../06_technical_spec/06_technical_spec.md`
- API 계약: `../07_api_spec/07_api_spec.md`

## Editing Rules

- 화면·컴포넌트는 기술 명세서의 프론트엔드 화면·클라이언트 상태 정의와 모순되지 않게 작성한다.
- 색상·테마 규칙은 저장소 루트 `color-map.md`와 일치시킨다.
- 같은 폴더 안에 보조 Markdown을 추가해 초안·근거를 먼저 작성하고, Agent가 검토해 대표 문서에 반영한다.
- 문서 버전, 문서 상태(Draft/Review/Complete), 기준 문서를 상단 메타데이터에 유지한다.
