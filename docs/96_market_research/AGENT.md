# Agent Instructions for docs/96_market_research

이 폴더는 로브(Lovv)의 시장조사, 경쟁 서비스 분석, 제품 포지셔닝 근거 문서를 보관한다.

## Primary Document

대표 문서는 `travel_ai_service_market_research.md`다. 트리플·트립닷컴 등 여행 서비스 비교와 LOVV 기능 보완 방향의 기준 문서다.

## Supporting Documents

- `b2g_public_sector_cost_effectiveness_research.md`: B2G 공익 협력과 공공 성과 측정 근거
- `b2g_commercialization_scenario_archive.md`: 영리화 시나리오 검토 아카이브

## Source Rules

- 외부 기사, 공식 뉴스룸, 공개 문서 허브를 근거로 사용하되, 서비스 사용 관찰과 객관 근거를 구분해 작성한다.

## Editing Rules

- 문서 버전, 문서 상태, 작성일, 기준 자료를 상단 메타데이터에 유지한다.
- 이미지 파일과 이미지 Markdown 문법은 넣지 않는다.
- 경쟁 서비스의 기능·수치·시장 근거는 출처 링크를 함께 남긴다.
- LOVV의 기능 판단은 `docs/00_project_plan`, `docs/01_requirements`, `docs/02_service_flow`, `docs/05_agent_spec`의 최신 내용과 충돌하지 않게 정리한다.
- 문서가 추가되거나 대표 문서명이 바뀌면 `scripts/generate_pages.py`의 문서 목록과 GitHub Pages 생성물을 함께 확인한다.
- 보조 문서의 내용이 확정되면 대표 문서나 `docs/00_project_plan/00_project_plan.md`의 시장·비즈니스 요약에 반영할지 판단한다.
