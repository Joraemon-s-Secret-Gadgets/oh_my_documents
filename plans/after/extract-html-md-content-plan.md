---
작성자: llm팀
상태: 진행후
---

# Implementation Plan: HTML 형식 Markdown 원본 추출

## Overview
`docs/*/*.md` 파일 중 실제 내용이 HTML 문서인 파일을 식별하고, HTML 태그와 레이아웃 코드를 제거해 순수 Markdown 문서로 되돌린다. 이 작업은 `docs/`를 원본 Markdown 보관 위치로 유지하고, `pages/`를 공유용 HTML 산출물로 유지하기 위한 정리 작업이다.

## Branch
작업 브랜치: `extract-md-from-html-docs`

`docs/...` 형태의 브랜치명은 Git ref 경로 충돌로 생성할 수 없어, 충돌 없는 브랜치명으로 생성했다.

## Current Context
현재 `docs/01_requirements/*.md`에는 Markdown 확장자를 쓰지만 HTML 전체 문서를 담고 있는 파일과 일반 Markdown/텍스트 파일이 섞여 있다.

| 파일 | 현재 형식 | 처리 방향 |
|---|---|---|
| `docs/01_requirements/01_requirements.md` | HTML fenced block + 전체 HTML 문서 | Markdown 본문으로 변환 |
| `docs/01_requirements/02_overturizim.md` | HTML fenced block + 전체 HTML 문서 | Markdown 본문으로 변환 |
| `docs/01_requirements/03_korea_japan.md` | HTML fenced block + 전체 HTML 문서 | Markdown 본문으로 변환 |
| `docs/01_requirements/04_trip_train.md` | HTML fenced block + 전체 HTML 문서 | Markdown 본문으로 변환 |
| `docs/01_requirements/05_astro_rag_proposal.md` | HTML fenced block + 전체 HTML 문서 | Markdown 본문으로 변환 |
| `docs/01_requirements/06_kdrama-pipeline.md` | HTML fenced block + 전체 HTML 문서 | Markdown 본문으로 변환 |
| `docs/01_requirements/07_animation.md` | 일반 텍스트/Markdown | 변환 제외, 필요 시 Markdown 정리만 검토 |
| `docs/01_requirements/08_japan_add_function.md` | 일반 Markdown | 변환 제외, 필요 시 Markdown 정리만 검토 |

## Target State
- `docs/*/*.md`는 원본 문서 역할에 맞게 사람이 읽고 편집하기 쉬운 Markdown으로 유지한다.
- `pages/*.html`은 공유용 HTML 산출물로 유지한다.
- HTML 문서에서 추출한 제목, 섹션, 표, 리스트, 요구사항 ID, 변경 이력은 Markdown 구조로 보존한다.
- CSS 클래스, 사이드바, 스크립트, 레이아웃용 `div`, `section`, `span` 등 표현 전용 마크업은 제거한다.
- HTML 엔티티, `<br />`, inline code, table structure는 Markdown 문법으로 변환한다.

## Architecture Decisions
- 변환 대상은 `docs/*/*.md` 중 `<!DOCTYPE html>`, `<html`, `<body`, `^```html` 패턴이 있는 파일로 판정한다.
- 변환 제외 파일은 내용 손상을 막기 위해 자동 변환하지 않는다.
- `pages/01_requirements.html` 등 공유용 HTML은 이 작업에서 수정하지 않는다. 필요하면 후속 작업에서 Markdown 원본으로부터 다시 생성한다.
- 원본 보존이 필요하면 변환 전 `git diff`와 현재 커밋 이력을 기준으로 되돌릴 수 있으므로 별도 백업 파일은 만들지 않는다.
- HTML 파싱은 가능하면 구조적 파서 기반으로 수행하고, 단순 정규식 치환은 보조적으로만 사용한다.
- 변환 후에는 각 문서의 첫 줄이 HTML fence가 아니라 Markdown 제목(`# ...`) 또는 일반 본문으로 시작해야 한다.

## Conversion Rules

| HTML 요소 | Markdown 변환 |
|---|---|
| `<h1>` | `#` |
| `<h2>` | `##` |
| `<h3>` | `###` |
| `<p>` | 일반 문단 |
| `<br>` / `<br />` | 줄바꿈 또는 문단 분리 |
| `<ul><li>` | `-` 목록 |
| `<ol><li>` | `1.` 목록 |
| `<table>` | Markdown table |
| `<code>` | inline code |
| `<strong>` / `<b>` | `**bold**` |
| `<em>` / `<i>` | `*italic*` |
| `<a href="...">text</a>` | `[text](url)` |
| 레이아웃용 `div`, `section`, `aside`, `nav`, `script`, `style` | 제거 또는 내부 본문만 추출 |
| HTML 주석 | 제거 |

## Task List

### Phase 1: 대상 식별 및 변환 기준 확정

## Task 1: HTML 형식 `.md` 파일 목록 확정

**Description:** `docs/*/*.md` 전체를 검사해 HTML 전체 문서가 들어 있는 파일과 이미 Markdown인 파일을 분리한다.

**Acceptance criteria:**
- [x] `^```html`, `<!DOCTYPE html>`, `<html`, `<body>` 패턴을 기준으로 HTML 형식 파일이 식별된다.
- [x] 변환 대상 파일과 제외 파일 목록이 플랜 또는 작업 로그에 남는다.
- [x] `07_animation.md`, `08_japan_add_function.md`처럼 이미 Markdown인 파일은 변환 대상에서 제외된다.

**Verification:**
- [x] `Get-ChildItem docs -Recurse -Filter *.md | Select-String -Pattern '<!DOCTYPE html>|<html|<body|^```html'`

**Dependencies:** None

**Files likely touched:**
- None during audit

**Estimated scope:** Small

## Task 2: Markdown 변환 규칙 확정

**Description:** HTML 요소를 Markdown 구조로 바꾸는 규칙을 확정한다. 특히 요구사항 문서에 많은 표, 카드형 목록, note/warn box, 요구사항 ID 셀의 표현 방식을 정한다.

**Acceptance criteria:**
- [x] 제목, 문단, 리스트, 표, 링크, inline code 변환 규칙이 정의된다.
- [x] note/warn box는 `> **Note:**` 또는 일반 소제목+문단 중 하나로 통일된다.
- [x] 요구사항 ID가 포함된 표는 Markdown table로 보존된다.
- [x] 사이드바, CSS, script, decorative markup은 제거 대상으로 정의된다.

**Verification:**
- [x] 샘플 HTML 블록 1개를 수동으로 Markdown 변환해 규칙 누락 여부를 확인한다.

**Dependencies:** Task 1

**Files likely touched:**
- `plans/extract-html-md-content-plan.md`

**Estimated scope:** Small

### Checkpoint: 변환 기준 완료
- [x] 변환 대상과 제외 대상이 명확하다.
- [x] HTML-to-Markdown 변환 규칙이 문서화되어 있다.
- [x] 자동 변환에서 손실되면 안 되는 정보가 식별되어 있다.

### Phase 2: 변환 도구 준비

## Task 3: 변환 스크립트 작성

**Description:** HTML 형식 `.md` 파일을 읽어 본문 내용을 Markdown으로 추출하는 스크립트를 작성한다. 스크립트는 변환 대상 파일만 처리하고, 제외 파일은 건너뛴다.

**Acceptance criteria:**
- [x] `docs/*/*.md`를 순회한다.
- [x] HTML 형식 파일만 변환 대상으로 판정한다.
- [x] HTML fence, doctype, head, sidebar, script, style이 제거된다.
- [x] main/body 내부의 실제 문서 제목, 문단, 표, 리스트가 Markdown으로 변환된다.
- [x] 실행 전 dry-run 또는 preview 모드를 제공한다.

**Verification:**
- [x] 변환 스크립트 dry-run 결과에 변환 대상 파일 목록이 출력된다.
- [x] 변환 제외 파일이 출력 목록에서 제외된다.

**Dependencies:** Task 1, Task 2

**Files likely touched:**
- `scripts/extract_html_md_content.py` 또는 유사 스크립트

**Estimated scope:** Medium

## Task 4: 단일 파일 파일럿 변환

**Description:** 가장 복잡한 `01_requirements.md` 또는 중간 규모의 `02_overturizim.md` 중 하나를 먼저 변환해 품질을 검증한다.

**Acceptance criteria:**
- [x] 변환 후 파일이 `#` 제목 또는 자연스러운 Markdown 본문으로 시작한다.
- [x] HTML fence와 전체 HTML 구조가 제거된다.
- [x] 주요 섹션 제목, 표, 요구사항 ID, 변경 이력이 보존된다.
- [x] 변환 결과에서 `<div`, `<span`, `<section`, `<table`, `<tr`, `<td>` 같은 잔여 HTML이 과도하게 남지 않는다.

**Verification:**
- [x] `Get-Content docs\01_requirements\01_requirements.md -TotalCount 30`
- [x] `Select-String -Path docs\01_requirements\01_requirements.md -Pattern '<!DOCTYPE html>|<html|<body|<div|<table|^```html'`

**Dependencies:** Task 3

**Files likely touched:**
- 변환 대상 파일 1개

**Estimated scope:** Medium

### Checkpoint: 파일럿 검증 완료
- [x] 파일럿 변환 결과가 사람이 읽을 수 있는 Markdown이다.
- [x] 표와 요구사항 ID가 보존된다.
- [x] 변환 규칙을 보완해야 할 항목이 정리된다.

### Phase 3: 전체 변환 및 정리

## Task 5: 전체 HTML 형식 `.md` 변환

**Description:** 파일럿에서 검증한 규칙으로 모든 HTML 형식 `.md` 파일을 Markdown 본문으로 변환한다.

**Acceptance criteria:**
- [x] `01_requirements.md`~`06_kdrama-pipeline.md`가 Markdown 본문으로 변환된다.
- [x] `07_animation.md`, `08_japan_add_function.md`는 내용 손상 없이 유지된다.
- [x] 모든 변환 대상 파일에서 HTML fence, doctype, head, body, sidebar, script가 제거된다.
- [x] 제목, 섹션, 표, 리스트, 링크가 Markdown으로 읽히는 형태로 보존된다.

**Verification:**
- [x] `Get-ChildItem docs -Recurse -Filter *.md | Select-String -Pattern '<!DOCTYPE html>|<html|<body|^```html'`
- [x] `git diff -- docs\01_requirements`

**Dependencies:** Task 4

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `docs/01_requirements/02_overturizim.md`
- `docs/01_requirements/03_korea_japan.md`
- `docs/01_requirements/04_trip_train.md`
- `docs/01_requirements/05_astro_rag_proposal.md`
- `docs/01_requirements/06_kdrama-pipeline.md`

**Estimated scope:** Large

## Task 6: Markdown 품질 정리

**Description:** 자동 변환 후 남은 불필요한 공백, 깨진 표, 반복된 내비게이션 문구, HTML 엔티티를 정리한다.

**Acceptance criteria:**
- [x] 문서별 첫 번째 제목이 명확하다.
- [x] Markdown table의 컬럼 구분이 깨지지 않는다.
- [x] 내비게이션, 인쇄 버튼, footer 같은 페이지 UI 문구가 제거된다.
- [x] `<br />` 변환으로 생긴 부자연스러운 줄바꿈이 정리된다.

**Verification:**
- [x] `rg -n "<[^>]+>|CONFIDENTIAL|인쇄 / PDF 저장|toc-link|aside|script" docs\01_requirements`
- [x] 주요 문서 2~3개를 수동으로 읽어 구조를 확인한다.

**Dependencies:** Task 5

**Files likely touched:**
- 변환 대상 Markdown 파일

**Estimated scope:** Medium

### Checkpoint: 전체 변환 완료
- [x] 변환 대상 파일 전체가 Markdown 본문으로 정리됐다.
- [x] 변환 제외 파일이 손상되지 않았다.
- [x] 잔여 HTML과 페이지 UI 문구가 허용 범위 안으로 줄었다.

### Phase 4: 문서 운영 규칙 갱신 및 검증

## Task 7: README 문서 운영 방식 보강

**Description:** `docs/`는 원본 Markdown, `pages/`는 HTML 산출물이라는 원칙을 README에 더 명확히 기록한다.

**Acceptance criteria:**
- [x] `docs/*/*.md`에는 HTML 전체 문서를 저장하지 않는다는 원칙이 추가된다.
- [x] HTML 공유본은 `pages/*.html`에 둔다는 원칙이 유지된다.
- [x] 향후 HTML을 Markdown으로 되돌리는 작업 기준이 짧게 남는다.

**Verification:**
- [x] `rg -n "docs/|pages/|HTML|Markdown" README.md`

**Dependencies:** Task 5

**Files likely touched:**
- `README.md`

**Estimated scope:** Small

## Task 8: 최종 검증

**Description:** 변환 후 대상 파일, 제외 파일, 문서 운영 규칙, Git diff를 최종 검증한다.

**Acceptance criteria:**
- [x] HTML 전체 문서가 남은 `.md` 파일이 없다.
- [x] 변환 제외 파일의 내용이 의도치 않게 크게 변경되지 않았다.
- [x] 공유용 HTML 산출물은 이 작업에서 변경하지 않았거나, 변경했다면 이유가 명확하다.
- [x] 작업 결과가 하나의 문서 정리 커밋으로 묶일 수 있다.

**Verification:**
- [x] `git diff --check`
- [x] `git status --short`
- [x] `Get-ChildItem docs -Recurse -Filter *.md | Select-String -Pattern '<!DOCTYPE html>|<html|<body|^```html'`
- [x] `git diff --stat`

**Dependencies:** Task 6, Task 7

**Files likely touched:**
- All converted docs
- `README.md`
- conversion script, if kept

**Estimated scope:** Small

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 자동 변환 중 표 구조가 깨짐 | High | 파일럿 변환으로 표 변환 규칙을 먼저 검증하고, 변환 후 Markdown table을 수동 확인한다. |
| CSS 클래스 기반 의미가 사라짐 | Medium | `key-cell`, `req-id`, `note-box`, `warn-box` 등 의미 있는 클래스는 Markdown 표현 규칙으로 매핑한다. |
| 링크와 앵커가 손실됨 | Medium | `<a href>`는 Markdown link로 변환하고 내부 앵커는 제목 구조로 대체한다. |
| 변환 제외 파일이 실수로 수정됨 | High | HTML 패턴 판정 대상만 처리하고, `git diff`에서 제외 파일 변경 여부를 확인한다. |
| 공유용 HTML 산출물과 원본 Markdown 내용이 일시적으로 불일치함 | Medium | 이번 작업의 범위를 원본 정리로 한정하고, 필요 시 후속 HTML 재생성 플랜을 별도로 둔다. |
| 변환 스크립트가 과도하게 복잡해짐 | Medium | 파일럿 변환 후 필요한 규칙만 추가하고, 사람이 검토 가능한 Markdown 산출을 우선한다. |

## Open Questions

- 변환 스크립트를 작업 후 저장소에 남길지, 일회성 도구로만 사용할지 결정이 필요하다.
- `01_requirements.md`처럼 현재 `pages/01_requirements.html`과 거의 동일한 문서는 원본 Markdown과 HTML 산출물의 차이를 어떻게 관리할지 결정이 필요하다.
- `02`~`06` 문서를 계속 독립 원본으로 유지할지, 이미 통합된 요구사항 정의서의 참고 자료로만 둘지 결정이 필요하다.
- 변환 후 `pages/` HTML을 다시 생성하는 작업까지 같은 브랜치에서 할지 후속 브랜치로 분리할지 결정이 필요하다.

## Definition of Done

- [x] `docs/*/*.md` 중 HTML 전체 문서인 파일 목록이 확정된다.
- [x] HTML 형식 `.md` 파일이 Markdown 본문으로 변환된다.
- [x] 이미 Markdown인 파일은 의도치 않게 변경되지 않는다.
- [x] 변환 결과에서 HTML fence, doctype, head, body, script, sidebar가 제거된다.
- [x] 주요 제목, 표, 리스트, 링크, 요구사항 ID가 Markdown으로 보존된다.
- [x] README에 원본 Markdown과 HTML 산출물의 역할 분리가 보강된다.
- [x] 최종 검증 명령이 통과한다.
