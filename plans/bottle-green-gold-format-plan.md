# Implementation Plan: ColorHunt Green & Gold 문서 포맷 통일

## Overview
문서 사이트와 생성 HTML 문서의 시각 언어를 ColorHunt 팔레트 `#005F02`, `#427A43`, `#C0B87A`, `#F2E3BB` 중심으로 통일한다. 목표는 트립닷컴류의 가벼운 블루 톤이 아니라, 오래된 유럽 기차 여행, 가죽 여권 케이스, 신뢰감 있는 프리미엄 여정의 인상을 주는 문서 브랜드를 만드는 것이다. 수정은 `docs/` Markdown 원본을 우선으로 하며, `pages/` HTML은 원본 반영 후 재생성한다.

## Brand Direction
- **Keywords:** 전통적인, 신뢰, 발견, 클래식한 여정
- **Tone:** 고급스럽고 진중한 프리미엄 여행 문서
- **Primary audience:** 비즈니스 여행, 프리미엄 여행 서비스, 높은 연령층도 신뢰할 수 있는 문서 경험
- **Avoid:** 가벼운 파란색 SaaS 톤, 과한 그라데이션, 지나치게 발랄한 여행 앱 스타일

## Typography System
All generated document pages should use this Google Fonts import:

```html
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
```

Recommended font tokens:

```css
:root {
  --font-display: "Outfit", "Noto Sans KR", sans-serif;
  --font-body: "Noto Sans KR", "Outfit", sans-serif;
  --font-ui: "Outfit", "Noto Sans KR", sans-serif;
}
```

Usage:
- Use `--font-display` for page titles, hero headings, section numbers, badges, and navigation labels.
- Use `--font-body` for Korean body text and long-form requirements.
- Use `--font-ui` for tables, status badges, buttons, filters, and metadata.
- Remove or replace previous document-specific font imports such as serif display families, mono-first UI stacks, or unrelated Google Font combinations unless a code sample specifically needs monospace.

## Color System
```text
Primary / Deep Green: #005F02
Secondary / Heritage Green: #427A43
Accent / Muted Gold: #C0B87A
Paper / Warm Cream: #F2E3BB
```

Recommended tokens:

```css
:root {
  --brand-green: #005F02;
  --brand-green-700: #427A43;
  --brand-gold: #C0B87A;
  --brand-paper: #F2E3BB;
  --brand-green-900: #003A01;
  --brand-green-100: #E2EBDD;
  --brand-gold-700: #8E864F;
  --brand-gold-100: #F7EFCF;
  --paper: #F2E3BB;
  --surface: #FFFFFF;
  --ink: #143018;
  --muted: #5F6B58;
  --rule: #D1C68C;
}
```

Palette source: `https://colorhunt.co/palette/005f02427a43c0b87af2e3bb`

## Current State
- `index.html` uses shared CSS from `assets/css/site.css`.
- `pages/01_requirements.html` is generated from `docs/01_requirements/01_requirements.md`.
- Current documentation scope is only `01_requirements`.
- `pages/01_requirements.html` is the parent requirements document.
- `02_` through `06_` detailed functional requirements are integrated into `pages/01_requirements.html` and kept as Markdown source material under `docs/01_requirements/`.
- Current generated requirement documents contain large inline `<style>` blocks inside each Markdown source.
- Several documents use independent color systems, including navy, blue, dark festival colors, or custom proposal themes.
- Because `pages/` is generated output, format changes must be applied to `docs/` first and then regenerated.

## Architecture Decisions
- Keep `docs/` as the source of truth. Do not manually theme only `pages/*.html`.
- Treat `01_requirements.html` as the single requirements landing document. The `02_`-`06_` topics must be presented as integrated child/detail sections, not separate published HTML pages.
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
- Left navigation or top document navigation uses `--brand-green-900`, `--brand-green`, or `--brand-green-700`.
- Main document background uses warm paper tone `--paper`.
- Content surface uses white or near-white with restrained borders.
- Maximum readable body width should stay around 860-960px.

### Typography
- Use `Outfit` and `Noto Sans KR` as the standard font pair across the index and generated requirement pages.
- Use `Noto Sans KR` for readable Korean body text.
- Use `Outfit` for English labels, numeric metadata, badges, navigation, and display accents.
- Avoid adding new serif or decorative display fonts during this pass.
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
- [ ] `assets/css/site.css` uses `#005F02` as the primary brand color.
- [ ] `assets/css/site.css` uses `#C0B87A` as the primary accent color.
- [ ] `assets/css/site.css` uses `#F2E3BB` as the warm paper background.
- [ ] `assets/css/site.css` uses `Outfit` and `Noto Sans KR` as the standard font pair.
- [x] Each source document has compatible brand token names or direct replacements.

**Verification:**
- [ ] `index.html` visually uses the ColorHunt green/gold/cream palette.
- [ ] `index.html` imports Outfit and Noto Sans KR from Google Fonts.
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
- [ ] Shared site colors use the ColorHunt palette.
- [x] Token naming is consistent enough for future agents to follow.
- [x] Requirements hierarchy is parent `01_requirements.html` plus child detail documents `02_`-`06_`.
- [x] No generated-only page has been edited without source changes.

### Phase 2: Source Document Format Unification

## Task 3: Normalize page frames and navigation

**Description:** Apply the bottle green frame to sidebars, top bars, document headers, active navigation states, and major page chrome across all requirement documents.

**Acceptance criteria:**
- [ ] Navigation backgrounds use `#005F02`, `#427A43`, or a darker derived green.
- [ ] Active navigation and hover states use `#C0B87A` or a subdued gold derivative.
- [x] Navigation text contrast remains readable.

**Verification:**
- [ ] Each generated page has visible ColorHunt palette continuity in its navigation and header.
- [ ] Mobile layouts do not overlap or hide navigation text.

**Dependencies:** Task 2

**Files likely touched:**
- `docs/01_requirements/*.md`
- `pages/*.html` after regeneration

**Estimated scope:** Medium: 6 source documents plus generated pages

## Task 4: Normalize typography, headings, tables, badges, and callouts

**Description:** Standardize document body typography and components so headings, tables, priority badges, callout boxes, section labels, and links share the same visual hierarchy.

**Acceptance criteria:**
- [ ] Every generated page imports `Outfit` and `Noto Sans KR`.
- [ ] Previous unrelated Google Font imports are removed from source documents.
- [ ] Body text uses `Noto Sans KR` or the shared body token.
- [ ] UI labels and display accents use `Outfit` or the shared display/UI token.
- [x] Table headers consistently use bottle green.
- [x] Important highlights use gold sparingly.
- [x] Priority badges remain semantically distinct and readable.
- [x] Section titles use a consistent green/gold hierarchy.

**Verification:**
- [ ] `Select-String -Path docs\01_requirements\*.md -Pattern 'Outfit|Noto Sans KR'` confirms the standard font pair.
- [ ] `Select-String -Path docs\01_requirements\*.md -Pattern 'DM Serif|Syne|Pretendard|IBM Plex|Noto Serif'` returns no active document font imports unless intentionally kept for code/mono usage.
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
| Gold overuse harms readability | Medium | Use `#C0B87A` for accents, active states, and highlights only. Keep long text on `#F2E3BB`, light paper, or white. |
| Existing document-specific character is lost | Medium | Preserve layout intent where possible while replacing brand colors and component hierarchy. |
| Mobile table layouts break after style changes | Medium | Verify the widest tables and sidebar behavior on narrow widths. |

## Open Questions
- Should every requirement document become visually identical, or should each keep a subtle sub-theme under the shared bottle green/gold brand?
- Should `assets/css/site.css` eventually be injected into all generated pages instead of relying on inline CSS in each Markdown source?
- Should a build script be added to automate docs-to-pages regeneration instead of running the conversion manually?

## Definition of Done
- [ ] `#005F02` is the primary brand color across the index and generated documents.
- [ ] `#427A43` is used as the secondary green across the index and generated documents.
- [ ] `#C0B87A` is the main accent color across the index and generated documents.
- [ ] `#F2E3BB` is used as the warm paper/background color where appropriate.
- [ ] `Outfit` and `Noto Sans KR` are the standard fonts across the index and generated documents.
- [x] `docs/` source documents are updated before `pages/` generated files.
- [x] `pages/*.html` are regenerated from `docs/`.
- [x] The site has a consistent premium, classic travel document feel.
- [x] `02_`-`06_` requirement pages are grouped under `01_requirements.html`.
- [x] No generated page contains Markdown code fences.
- [x] All links from `index.html` resolve to existing pages.
