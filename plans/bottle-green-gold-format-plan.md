# Implementation Plan: Bottle Green & Gold 문서 포맷 통일

## Overview
문서 사이트와 생성 HTML 문서의 시각 언어를 클래식 보틀 그린과 샴페인 골드 중심으로 통일한다. 목표는 트립닷컴류의 가벼운 블루 톤이 아니라, 오래된 유럽 기차 여행, 가죽 여권 케이스, 신뢰감 있는 프리미엄 여정의 인상을 주는 문서 브랜드를 만드는 것이다. 수정은 `docs/` Markdown 원본을 우선으로 하며, `pages/` HTML은 원본 반영 후 재생성한다.

## Brand Direction
- **Keywords:** 전통적인, 신뢰, 발견, 클래식한 여정
- **Tone:** 고급스럽고 진중한 프리미엄 여행 문서
- **Primary audience:** 비즈니스 여행, 프리미엄 여행 서비스, 높은 연령층도 신뢰할 수 있는 문서 경험
- **Avoid:** 가벼운 파란색 SaaS 톤, 과한 그라데이션, 지나치게 발랄한 여행 앱 스타일

## Color System
```text
Primary / Bottle Green: #1B3B32
Accent / Champagne Gold: #D4AF37
```

Recommended tokens:

```css
:root {
  --brand-green: #1B3B32;
  --brand-green-900: #10251F;
  --brand-green-800: #173329;
  --brand-green-100: #E6EEE9;
  --brand-gold: #D4AF37;
  --brand-gold-700: #A9821E;
  --brand-gold-100: #F6EBC4;
  --paper: #F7F3EA;
  --surface: #FFFFFF;
  --ink: #17211D;
  --muted: #66736D;
  --rule: #D9D0BF;
}
```

## Current State
- `index.html` uses shared CSS from `assets/css/site.css`.
- `pages/*.html` are generated from `docs/01_requirements/*.md`.
- Current documentation scope is only `01_requirements`.
- `pages/01_requirements.html` is the parent requirements document.
- `pages/02_overturizim.html` through `pages/06_kdrama-pipeline.html` are detailed functional requirement documents under `pages/01_requirements.html`.
- Current generated requirement documents contain large inline `<style>` blocks inside each Markdown source.
- Several documents use independent color systems, including navy, blue, dark festival colors, or custom proposal themes.
- Because `pages/` is generated output, format changes must be applied to `docs/` first and then regenerated.

## Architecture Decisions
- Keep `docs/` as the source of truth. Do not manually theme only `pages/*.html`.
- Treat `01_requirements.html` as the parent requirements landing document. The `02_`-`06_` pages must be presented as child/detail requirement documents, not sibling top-level document categories.
- Introduce a shared brand token vocabulary even when each source document keeps inline CSS.
- Standardize document-level structure before visual details: header, navigation/sidebar, section titles, tables, badges, callouts.
- Use bottle green for persistent structure and trust signals: page frame, navigation, major headings, table headers.
- Use gold sparingly for discovery and premium accents: active states, section markers, key metrics, badges, hover borders.
- Keep document cards and tables at `8px` radius or less to preserve a mature, editorial feel.

## Format Standard

### Information Hierarchy
- `index.html` should show one top-level requirements entry: `01_requirements.html`.
- `02_` through `06_` documents should appear as nested detail links below the `01_requirements.html` entry.
- `pages/01_requirements.html` should include a "세부 기능 요구사항" section that links to the `02_` through `06_` generated pages.
- Future document categories such as user stories, architecture, API, or deployment should be added as separate top-level groups only when their source documents exist.

### Page Layout
- Left navigation or top document navigation uses `--brand-green-900` or `--brand-green`.
- Main document background uses warm paper tone `--paper`.
- Content surface uses white or near-white with restrained borders.
- Maximum readable body width should stay around 860-960px.

### Typography
- Use a readable Korean body font already present in each document where possible.
- Use serif or semi-serif display typography only for hero/title areas if already available.
- Do not enlarge all content globally; keep document pages dense enough for repeated reading.

### Components
- Status badges: green background for stable/complete, gold accent for highlighted states.
- Tables: bottle green header, subtle paper rows, thin rule borders.
- Callouts: gold left border or gold top rule, not full gold backgrounds.
- Buttons/links: gold hover or underline, bottle green text by default.
- Navigation active state: gold line or gold text on bottle green background.

## Task List

### Phase 1: Token and Scope Audit

## Task 1: Audit document color usage

**Description:** Inspect every `docs/01_requirements/*.md` file and list the current CSS tokens, hard-coded colors, and layout patterns that need normalization.

**Acceptance criteria:**
- [x] Each source document has its current primary/accent colors identified.
- [x] Inline CSS sections that control global theme, navigation, tables, badges, and headings are located.
- [x] Any document-specific visual concept that should be preserved is noted.

**Verification:**
- [x] `rg "#[0-9a-fA-F]{3,6}|:root|background|color" docs/01_requirements` has been reviewed.
- [x] Risky hard-coded blue/purple accent colors are listed for replacement.

**Dependencies:** None

**Files likely touched:**
- None during audit

**Estimated scope:** Small: read-only audit

## Task 2: Define common brand tokens

**Description:** Add or align CSS custom properties in `assets/css/site.css` and document source inline styles so every page can reference the same brand colors.

**Acceptance criteria:**
- [x] `assets/css/site.css` uses `#1B3B32` as the primary brand color.
- [x] `assets/css/site.css` uses `#D4AF37` as the primary accent color.
- [x] Each source document has compatible brand token names or direct replacements.

**Verification:**
- [x] `index.html` visually uses bottle green and gold.
- [x] No blue accent remains in the shared site CSS unless it is part of content, not branding.

**Dependencies:** Task 1

**Files likely touched:**
- `assets/css/site.css`
- `docs/01_requirements/*.md`

**Estimated scope:** Medium: shared CSS plus source document styles

## Task 2.5: Normalize requirements hierarchy

**Description:** Update the document hub and parent requirements page so `01_requirements.html` acts as the only top-level requirements document and `02_`-`06_` pages are nested below it as detailed functional requirements.

**Acceptance criteria:**
- [x] `index.html` shows `01_requirements.html` as the parent requirement document.
- [x] `index.html` shows `02_`-`06_` as child/detail links below the parent requirement document.
- [x] `docs/01_requirements/01_requirements.md` includes a detail document section linking to `02_`-`06_`.
- [x] `pages/01_requirements.html` reflects the same detail document section after regeneration.

**Verification:**
- [x] Links from `index.html` to `pages/01_requirements.html` and all child pages resolve.
- [x] Links from `pages/01_requirements.html` to the `02_`-`06_` pages resolve.
- [x] `02_`-`06_` are no longer presented as independent top-level cards in `index.html`.

**Dependencies:** Task 2

**Files likely touched:**
- `index.html`
- `assets/css/site.css`
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html` after regeneration

**Estimated scope:** Small: parent/child navigation update

### Checkpoint: Brand Foundation
- [x] Shared site colors are bottle green and gold.
- [x] Token naming is consistent enough for future agents to follow.
- [x] Requirements hierarchy is parent `01_requirements.html` plus child detail documents `02_`-`06_`.
- [x] No generated-only page has been edited without source changes.

### Phase 2: Source Document Format Unification

## Task 3: Normalize page frames and navigation

**Description:** Apply the bottle green frame to sidebars, top bars, document headers, active navigation states, and major page chrome across all requirement documents.

**Acceptance criteria:**
- [x] Navigation backgrounds use `#1B3B32` or a darker derived green.
- [x] Active navigation and hover states use `#D4AF37` or a subdued gold derivative.
- [x] Navigation text contrast remains readable.

**Verification:**
- [x] Each generated page has visible brand continuity in its navigation and header.
- [ ] Mobile layouts do not overlap or hide navigation text.

**Dependencies:** Task 2

**Files likely touched:**
- `docs/01_requirements/*.md`
- `pages/*.html` after regeneration

**Estimated scope:** Medium: 6 source documents plus generated pages

## Task 4: Normalize headings, tables, badges, and callouts

**Description:** Standardize document body components so tables, priority badges, callout boxes, section labels, and links share the same visual hierarchy.

**Acceptance criteria:**
- [x] Table headers consistently use bottle green.
- [x] Important highlights use gold sparingly.
- [x] Priority badges remain semantically distinct and readable.
- [x] Section titles use a consistent green/gold hierarchy.

**Verification:**
- [x] Tables remain scannable in every generated document.
- [x] Gold is used as an accent and does not dominate full sections.
- [x] Text contrast is acceptable on green and gold backgrounds.

**Dependencies:** Task 3

**Files likely touched:**
- `docs/01_requirements/*.md`
- `pages/*.html` after regeneration

**Estimated scope:** Medium: repeated component style updates

### Checkpoint: Source Format
- [x] All `docs/01_requirements/*.md` files follow the same brand direction.
- [x] Existing content is preserved.
- [x] No code fences are broken.
- [x] The HTML inside Markdown still starts with `<!DOCTYPE html>` after the opening ```html fence.

### Phase 3: Regeneration and Verification

## Task 5: Regenerate pages from docs

**Description:** Rebuild `pages/*.html` from `docs/01_requirements/*.md` after source style changes.

**Acceptance criteria:**
- [x] Every source Markdown file has a matching generated HTML file in `pages/`.
- [x] Generated pages do not contain Markdown code fences.
- [x] `index.html` links still point to existing files.

**Verification:**
- [x] `Select-String -Path pages\*.html -Pattern '^```'` returns no matches.
- [x] `Get-ChildItem pages\*.html` shows 6 HTML files.
- [x] `git diff --stat` clearly separates source changes and generated output.

**Dependencies:** Task 4

**Files likely touched:**
- `pages/*.html`

**Estimated scope:** Small: generated output

## Task 6: Visual and responsive review

**Description:** Open the generated site and inspect desktop and mobile widths for visual consistency, readability, and link integrity.

**Acceptance criteria:**
- [x] `index.html` presents the bottle green/gold brand clearly.
- [x] `index.html` presents `02_`-`06_` pages as child/detail documents under `01_requirements.html`.
- [x] Each `pages/*.html` page appears consistent enough to belong to one requirements document set.
- [ ] No headings, buttons, tables, or navigation labels overlap on mobile.

**Verification:**
- [ ] Manual browser check for `index.html`.
- [ ] Manual browser spot check for all 6 generated pages.
- [x] Confirm all card links from `index.html` open existing generated pages.

**Dependencies:** Task 5

**Files likely touched:**
- None unless defects are found

**Estimated scope:** Small: review and fixes

### Checkpoint: Ready To Commit
- [x] Source `docs/` changes are complete.
- [x] Generated `pages/` changes reflect source.
- [x] `index.html` and `assets/css/site.css` use the new brand colors.
- [ ] Working tree changes can be split into `docs(theme)` and `docs(pages)` or committed together if tightly coupled.

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Each document has heavily customized inline CSS | High | Normalize tokens and major components first; avoid rewriting every layout detail in one pass. |
| Generated HTML diverges from Markdown source | High | Edit `docs/` first, then regenerate `pages/`; do not hand-edit generated pages. |
| Gold overuse harms readability | Medium | Use gold for accents, active states, and highlights only. Keep long text on light paper or white. |
| Existing document-specific character is lost | Medium | Preserve layout intent where possible while replacing brand colors and component hierarchy. |
| Mobile table layouts break after style changes | Medium | Verify the widest tables and sidebar behavior on narrow widths. |

## Open Questions
- Should every requirement document become visually identical, or should each keep a subtle sub-theme under the shared bottle green/gold brand?
- Should `assets/css/site.css` eventually be injected into all generated pages instead of relying on inline CSS in each Markdown source?
- Should a build script be added to automate docs-to-pages regeneration instead of running the conversion manually?

## Definition of Done
- [x] `#1B3B32` is the primary brand color across the index and generated documents.
- [x] `#D4AF37` is the main accent color across the index and generated documents.
- [x] `docs/` source documents are updated before `pages/` generated files.
- [x] `pages/*.html` are regenerated from `docs/`.
- [x] The site has a consistent premium, classic travel document feel.
- [x] `02_`-`06_` requirement pages are grouped under `01_requirements.html`.
- [x] No generated page contains Markdown code fences.
- [x] All links from `index.html` resolve to existing pages.
