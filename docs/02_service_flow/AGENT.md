# Agent Instructions for service flow

이 폴더는 로브 서비스 흐름 명세서를 관리한다.

## Primary Document

대표 문서는 `02_service_flow.md`다. 사용자 진입, 온보딩, 지도 탐색, 챗봇 추천, 결과 확인, 저장·피드백 흐름을 정의한다.

## Dependencies

- 요구사항 기준: `../01_requirements/01_requirements.md`
- API 계약 확인: `../04_api_spec/04_api_spec.md`
- Agent 처리 흐름 확인: `../06_agent_spec/06_agent_spec.md`

## Editing Rules

- 화면 흐름은 사용자 행동, 시스템 처리, 상태 변화가 함께 드러나게 작성한다.
- 서비스 흐름을 바꾸면 관련 요구사항 ID와 API 엔드포인트 영향 여부를 확인한다.
- PoC 대체 흐름과 Production 목표 흐름을 혼동하지 않는다.
- 저장, 피드백, 온보딩 흐름을 수정할 때는 개인정보와 데이터 저장 범위를 함께 확인한다.
