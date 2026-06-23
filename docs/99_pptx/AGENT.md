# Agent Instructions for presentation docs

이 폴더는 로브(Lovv)의 발표 자료 원본과 발표 단계별 하위 문서를 관리한다.

## Primary Document

대표 문서는 `99_pptx.md`다. 발표 자료 폴더의 구조, 발표 단위, 산출물 관리 원칙은 이 파일을 기준으로 관리한다.

## Document Structure

현재 하위 문서는 다음과 같다.

- `99_pptx.md`: 발표 자료 대표 문서
- `midterm_vs_final_presentation_guide.md`: 중간발표와 최종발표 구성 차이 및 재사용 전략 보조 문서
- `01_midterm_presentation/`: 중간발표 대표 Markdown과 페이지별 슬라이드 문서

## Editing Rules

- 발표 내용은 Markdown 원본을 먼저 수정한다.
- 발표 단위가 별도 폴더를 가지면 해당 폴더 안에 대표 Markdown과 `AGENT.md`를 둔다.
- PPTX, HTML 발표본, 캡처 이미지는 산출물로 관리하고, 원본 Markdown과 충돌하지 않게 한다.
- `bak/`는 로컬 백업 전용이며 Git 추적 대상으로 만들지 않는다.
- 대표 문서 이외에 새 `index.md` 파일은 만들지 않는다.
