---
작성자: llm팀
상태: 진행후
---

# Implementation Plan: 불필요 HTML 정리 및 CSS/JS 분리

## Overview
현재 `docs/01_requirements/*.md` 원본과 `pages/*.html` 생성물은 각 문서 안에 큰 inline `<style>`과 `<script>`를 포함한다. 이 구조는 빠르게 공유하기에는 편하지만, 포맷 통일, 유지보수, 중복 제거, Git diff 검토에는 불리하다. 이 계획은 불필요한 HTML 생성물을 정리하고, CSS와 JS를 `assets/css/`, `assets/js/`로 분리하는 절차를 정의한다.

## Current State
```text
docs/01_requirements/*.md   HTML 전체를 ```html 코드블록으로 포함하는 원본
pages/01_requirements.html  docs에서 생성된 공개 요구사항 HTML
assets/css/*.css            index와 요구사항 문서용 외부 CSS
assets/js/*.js              요구사항 문서용 외부 JS
```

초기 확인 구조:
- 6개 `docs/01_requirements/*.md` 모두 inline `<style>` 포함
- 6개 `docs/01_requirements/*.md` 모두 inline `<script>` 포함
- 6개 `pages/*.html` 모두 inline `<style>`과 `<script>` 포함
- `index.html`은 `assets/css/site.css`를 사용
- `pages/01_requirements.html`은 상위 요구사항 문서
- `pages/02_*.html`~`pages/06_*.html`은 하위 세부 기능 요구사항 문서였으나, 01에 통합 후 삭제 대상

## Goals
- 실제로 필요한 HTML만 남긴다.
- 생성물인 `pages/*.html`을 직접 편집하지 않고 `docs/` 원본을 기준으로 재생성한다.
- 문서별 inline CSS를 외부 CSS 파일로 분리한다.
- 문서별 inline JS를 외부 JS 파일로 분리한다.
- `index.html`, `pages/01_requirements.html`, 01 내부 세부 기능 요구사항 링크 구조를 유지한다.
- GitHub Pages에서 정적 파일만으로 동작하게 유지한다.

## Keep / Remove Policy

### Keep
- `index.html`: GitHub Pages 문서 허브
- `pages/01_requirements.html`: 요구사항 정의서 상위 문서
- `docs/01_requirements/*.md`: 원본 문서와 세부 기능 요구사항 소스
- `assets/css/site.css`: 문서 허브 공통 CSS

### Remove Candidates
아래 조건을 만족하는 HTML은 삭제 후보로 본다.
- `pages/`에 있으나 `index.html` 또는 `pages/01_requirements.html`에서 링크되지 않는 파일
- 같은 내용을 중복으로 담은 임시 HTML
- `01_requirements.html`에 통합된 뒤 중복이 된 `pages/02_*.html`~`pages/06_*.html`
- 과거 실험용 HTML
- 원본 `docs/`에 대응 파일이 없는 generated HTML

`01_requirements.html`에 02~06 세부 기능 요구사항이 통합되면, `pages/02_*.html`~`pages/06_*.html`은 중복 생성물로 보고 삭제한다. 이 경우 `index.html`과 `01_requirements.html` 내부 링크는 `pages/01_requirements.html#s3-6` 또는 `#s3-6`로 정리한다.

## Target Structure
`02_`~`06_` HTML을 공개 산출물에서 제거했으므로, 공개 Pages에서 로드되는 asset만 유지한다. 현재 유지 대상은 `index.html`용 `site.css`와 `01_requirements.html`용 `requirements.css`, `requirements.js`다.

```text
assets/
├── css/
│   ├── site.css
│   └── requirements.css
└── js/
    └── requirements.js
```

Generated HTML should reference assets like:

```html
<link rel="stylesheet" href="../assets/css/requirements.css">
<script src="../assets/js/requirements.js" defer></script>
```

For `index.html`, keep:

```html
<link rel="stylesheet" href="./assets/css/site.css">
```

## Task List

### Phase 1: Inventory and Delete Criteria

## Task 1: Build HTML inventory

**Description:** List all HTML files, their source Markdown files, inbound links, and whether they are required by the current document hierarchy.

**Acceptance criteria:**
- [x] Every `pages/*.html` file has a matching `docs/01_requirements/*.md` source.
- [x] Every `pages/*.html` file is linked from `index.html` or `pages/01_requirements.html`.
- [x] Orphan or redundant HTML files are listed.

**Verification:**
- [x] `rg --files pages` output is reviewed.
- [x] Links in `index.html` and `pages/01_requirements.html` are checked.

**Dependencies:** None

**Files likely touched:**
- None during audit

**Estimated scope:** Small

## Task 2: Remove orphan generated HTML

**Description:** Delete generated HTML files that have no source Markdown or no inbound link.

**Acceptance criteria:**
- [x] No orphan or redundant HTML remains in `pages/`.
- [x] No required linked page is removed.
- [x] `index.html` and `pages/01_requirements.html` links remain valid.

**Verification:**
- [x] `Test-Path` succeeds for every linked `pages/*.html`.
- [x] Git diff only deletes confirmed redundant generated HTML files.

**Dependencies:** Task 1

**Files likely touched:**
- `pages/*.html` only if orphan files exist

**Estimated scope:** Small

### Checkpoint: HTML Pruning
- [x] Required pages are preserved.
- [x] Orphan or redundant pages are removed or confirmed absent.
- [x] Parent/child requirement hierarchy still works.

### Phase 2: CSS Extraction

## Task 3: Extract inline styles from source Markdown

**Description:** Move each source document's inline `<style>` content into a matching `assets/css/*.css` file, then replace the inline style block with an external stylesheet link.

**Acceptance criteria:**
- [x] `docs/01_requirements/01_requirements.md` uses `../assets/css/requirements.css`.
- [x] `02_`~`06_` source Markdown no longer references removed document-specific CSS files.
- [x] No inline `<style>` remains in `docs/01_requirements/*.md`.

**Verification:**
- [x] `Select-String -Path docs\01_requirements\*.md -Pattern '<style|</style>'` returns no matches.
- [x] `Select-String -Path assets\css\*.css -Pattern '#1B3B32|#D4AF37|--brand-green|--brand-gold'` confirms brand tokens remain available.

**Dependencies:** Task 1

**Files likely touched:**
- `docs/01_requirements/*.md`
- `assets/css/*.css`

**Estimated scope:** Medium

## Task 4: Identify shared CSS candidates

**Description:** Compare extracted CSS files and identify repeated declarations that can later move into `assets/css/requirements-common.css`.

**Acceptance criteria:**
- [ ] Common brand tokens are documented.
- [ ] Common table, badge, navigation, and layout styles are identified.
- [ ] No premature large refactor is performed unless duplication is obvious and safe.

**Verification:**
- [ ] Repeated selectors and token blocks are listed in notes or the plan.

**Dependencies:** Task 3

**Files likely touched:**
- Optional: `assets/css/requirements-common.css`
- Optional: `docs/01_requirements/*.md`

**Estimated scope:** Small to Medium

### Checkpoint: CSS Split
- [x] Source Markdown no longer contains inline CSS.
- [x] Generated pages load external CSS.
- [x] Existing visual brand tokens are preserved.

### Phase 3: JS Extraction

## Task 5: Extract inline scripts from source Markdown

**Description:** Move each document's inline `<script>` content into a matching `assets/js/*.js` file and replace the inline block with a deferred external script tag.

**Acceptance criteria:**
- [x] `docs/01_requirements/01_requirements.md` uses `../assets/js/requirements.js`.
- [x] `02_`~`06_` source Markdown no longer references removed document-specific JS files.
- [x] No inline `<script>` remains in `docs/01_requirements/*.md`.

**Verification:**
- [x] `Select-String -Path docs\01_requirements\*.md -Pattern '<script>|</script>'` returns no inline script blocks.
- [x] `assets/js/*.js` files exist and contain the extracted behavior.

**Dependencies:** Task 3

**Files likely touched:**
- `docs/01_requirements/*.md`
- `assets/js/*.js`

**Estimated scope:** Medium

## Task 6: Normalize script loading

**Description:** Ensure generated pages load JS with `defer`, and that DOM-dependent code still runs after the document is parsed.

**Acceptance criteria:**
- [x] Script tags use `defer`.
- [ ] Code that assumes DOM availability still works.
- [x] No duplicate script logic remains in HTML.

**Verification:**
- [x] Static grep confirms script tags reference external files.
- [ ] Manual browser check or Playwright check confirms navigation, filters, tabs, or calculators still work.

**Dependencies:** Task 5

**Files likely touched:**
- `docs/01_requirements/*.md`
- `assets/js/*.js`

**Estimated scope:** Small

### Checkpoint: JS Split
- [x] Source Markdown no longer contains inline JS.
- [x] Generated pages load external JS.
- [ ] Interactive behavior still works.

### Phase 4: Regeneration and Validation

## Task 7: Regenerate `pages/*.html`

**Description:** Rebuild generated HTML from updated Markdown sources.

**Acceptance criteria:**
- [x] `pages/*.html` contains no inline `<style>` blocks.
- [x] `pages/*.html` contains no inline `<script>` blocks.
- [x] `pages/*.html` links to external CSS and JS under `../assets/`.
- [x] Generated pages contain no Markdown code fences.

**Verification:**
- [x] `Select-String -Path pages\*.html -Pattern '<style|</style>|<script>.*</script>'` returns no inline blocks.
- [x] `Select-String -Path pages\*.html -Pattern '../assets/css|../assets/js'` confirms external assets.
- [x] `Select-String -Path pages\*.html -Pattern '^```'` returns no matches.

**Dependencies:** Task 6

**Files likely touched:**
- `pages/*.html`

**Estimated scope:** Small

## Task 8: Link and asset validation

**Description:** Validate that every generated page references existing CSS/JS files and that all linked pages exist.

**Acceptance criteria:**
- [x] Every CSS file referenced from generated pages exists.
- [x] Every JS file referenced from generated pages exists.
- [x] Every page link from `index.html` and `pages/01_requirements.html` exists.

**Verification:**
- [x] `Test-Path` checks pass for all linked CSS, JS, and HTML files.
- [x] Browser or static check confirms no obvious missing asset paths.

**Dependencies:** Task 7

**Files likely touched:**
- None unless fixes are needed

**Estimated scope:** Small

### Checkpoint: Ready To Commit
- [x] Orphan HTML deletion is complete or confirmed unnecessary.
- [x] CSS is externalized.
- [x] JS is externalized.
- [x] Generated pages are regenerated from source.
- [x] Static link and asset checks pass.

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Moving JS breaks DOM-dependent interactions | High | Use `defer`; keep script content unchanged during first extraction. |
| CSS path differs between docs source and generated pages | High | Because generated pages live in `pages/`, use `../assets/...` in source HTML. |
| Inline code inside JavaScript strings is accidentally extracted incorrectly | Medium | Extract only top-level `<script>` blocks, preserve content verbatim. |
| Visual regressions after CSS extraction | Medium | Keep extracted CSS unchanged first; refactor common CSS only after validation. |
| Removing generated HTML breaks links | High | Delete only orphan files confirmed by link inventory. |

## Open Questions
- Should extracted CSS remain document-specific, or should a shared `requirements-common.css` be introduced immediately?
- Should `pages/02_*.html` through `pages/06_*.html` remain standalone pages, or eventually become sections within `pages/01_requirements.html`?
- Should a repeatable build script be added so CSS/JS extraction and page generation do not rely on manual agent steps?

## Definition of Done
- [x] No unnecessary generated HTML remains.
- [x] `docs/01_requirements/*.md` has no inline `<style>` blocks.
- [x] `docs/01_requirements/*.md` has no inline `<script>` blocks.
- [x] `pages/*.html` has no inline `<style>` blocks.
- [x] `pages/*.html` has no inline `<script>` blocks.
- [x] `assets/css/` contains extracted document CSS files.
- [x] `assets/js/` contains extracted document JS files.
- [x] All page, CSS, and JS links resolve.
- [x] Generated pages contain no Markdown code fences.
