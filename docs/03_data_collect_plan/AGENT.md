# Agent Instructions for data collect plan

이 폴더는 로브 데이터 수집 계획서를 관리한다.

## Primary Document

대표 문서는 `03_data_collect_plan.md`다.
## Representative Document Flow

- `03_data_collect_plan.md` is the integrated representative document for this folder.
- `sections/*.md` is the editing source for `03_data_collect_plan.md`.
- When changing representative document body content, edit the matching `sections/*.md` file first, then regenerate or update `03_data_collect_plan.md` in the same change.
- `supplemental/*.md` stores supporting notes, rationale, drafts, and detailed references for this folder.
- Do not keep supplemental Markdown documents at this folder root.
- Do not create an `index.md` file in this folder.

## Dependencies

- 요구사항 기준: `../01_requirements/01_requirements.md`
- 기술 명세서: `../06_technical_spec/06_technical_spec.md`

## Editing Rules

- 수집할 데이터 소스, 주기, 포맷, 그리고 보존 정책을 정의한다.
- 실시간 날씨 데이터 수집 및 기상 경향 데이터 가공 방식을 구체적으로 기술한다.
