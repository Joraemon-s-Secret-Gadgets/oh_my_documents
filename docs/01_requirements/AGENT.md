# Agent Instructions for requirements

이 폴더는 로브 요구사항 명세서와 요구사항 보조 자료를 관리한다.

## Primary Document

대표 문서는 `01_requirements.md`다. 기능 요구사항, 비기능 요구사항, 데이터 요구사항, 제약사항, 변경 이력은 이 파일을 기준으로 관리한다.
## Representative Document Flow

- `01_requirements.md` is the integrated representative document for this folder.
- `sections/*.md` is the editing source for `01_requirements.md`.
- When changing representative document body content, edit the matching `sections/*.md` file first, then regenerate or update `01_requirements.md` in the same change.
- `supplemental/*.md` stores supporting notes, rationale, drafts, and detailed references for this folder.
- Do not keep supplemental Markdown documents at this folder root.
- Do not create an `index.md` file in this folder.

## Supporting Documents

`supplemental/*.md`의 보조 문서는 요구사항 명세서에 반영할 후보·근거 자료다. 보조 문서의 내용이 확정되면 `sections/*.md`를 먼저 수정하고 `01_requirements.md`에 요구사항 형식으로 통합한다.

## Editing Rules

- 기능 요구사항은 `FR-*`, 비기능 요구사항은 `NFR-*` ID 체계를 유지한다.
- 요구사항을 추가·수정하면 변경 이력에 버전, 날짜, 작성자, 변경 내용을 반영한다.
- 저장 범위, 개인화, API Key, 권한, 데이터 접근 같은 보안·개인정보 관련 내용은 모호하게 두지 않는다.
- `pages/01_requirements.html`은 생성물이다. HTML만 수정하지 말고 대응하는 Markdown 내용을 먼저 확인한다.
- 백업 HTML을 참조해 UI를 복원할 수 있지만, 내용 기준은 현재 `01_requirements.md`다.
