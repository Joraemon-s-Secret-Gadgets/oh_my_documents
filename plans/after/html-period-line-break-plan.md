---
작성자: Codex
상태: 진행후
---

# Implementation Plan: HTML 마침표 기준 줄넘김 정리

## Overview
현재 공개 문서 HTML에는 긴 문단과 표 셀 안에 여러 문장이 한 줄로 이어진 부분이 있다. 이 계획은 HTML 구조를 깨지 않으면서, 본문 텍스트에서 문장 마침표(`.`) 뒤에 줄넘김을 적용해 문서 가독성을 높이는 절차를 정의한다.

## Scope
- 대상 공개 HTML: `pages/01_requirements.html`
- 원본 문서: `docs/01_requirements/01_requirements.md`
- 필요 시 문서 허브: `index.html`
- 제외 대상: CSS, JS, HTML 속성, URL, 파일명, 버전 번호, 숫자 소수점, 코드 조각

## Architecture Decisions
- `pages/01_requirements.html`은 generated output이므로 직접 편집하지 않고 `docs/01_requirements/01_requirements.md`를 먼저 수정한 뒤 재생성한다.
- 마침표 기준 줄넘김은 HTML 태그 내부 속성이 아니라 텍스트 노드에만 적용한다.
- 모든 `.`를 줄넘김하지 않는다. 문장 종료로 판단되는 마침표만 처리한다.
- 줄넘김은 화면에서 문장 단위가 드러나도록 HTML 텍스트에 개행을 넣는 방식으로 우선 처리한다. 실제 시각적 줄바꿈이 반드시 필요하면 CSS 또는 `<br>` 적용 여부를 별도 검토한다.

## Classification Rules

### 줄넘김 후보
- 한국어 설명문 안에서 문장이 끝나는 마침표
- `<p>`, `<td>`, `<li>`, `<span>`, `<div>` 등 본문 텍스트 노드 안의 문장 구분
- 한 문단 안에 2개 이상의 완결 문장이 이어지는 경우

### 줄넘김 제외
- HTML 속성값: `href="./pages/01_requirements.html"`, `class="..."`, `id="..."`
- 파일명과 경로: `01_requirements.html`, `site.css`, `requirements.js`
- 버전과 숫자: `v1.1`, `1.5초`, `3.6`, `4.5`
- URL과 도메인
- 약어 또는 제품명 일부로 쓰이는 점
- 코드 블록, `<code>`, `<script>`, `<style>` 안의 텍스트

## Task List

### Phase 1: Inventory

## Task 1: Identify period-heavy text nodes

**Description:** 현재 HTML과 원본 Markdown에서 마침표가 포함된 본문 텍스트 위치를 조사하고, 문장 줄넘김 후보와 제외 대상을 분리한다.

**Acceptance criteria:**
- [x] `docs/01_requirements/01_requirements.md`에서 본문 텍스트 내 마침표 후보가 목록화된다.
- [x] URL, 파일명, 버전, 숫자, HTML 속성의 마침표는 제외 목록으로 분류된다.
- [x] `pages/01_requirements.html`은 generated output으로만 확인한다.

**Verification:**
- [x] `rg -n "\." docs\01_requirements\01_requirements.md pages\01_requirements.html index.html` 결과를 검토한다.
- [x] 후보가 문장 텍스트인지 수동 확인한다.

**Dependencies:** None

**Files likely touched:**
- None during audit

**Estimated scope:** Small

## Task 2: Define safe replacement strategy

**Description:** 단순 전체 치환 대신 텍스트 노드 또는 명확한 본문 구간만 대상으로 하는 수정 기준을 정한다.

**Acceptance criteria:**
- [x] HTML 태그 속성은 변경하지 않는 방식이 확정된다.
- [x] `<code>`, `<script>`, `<style>` 내부는 변경하지 않는 방식이 확정된다.
- [x] 문장 마침표 뒤 줄넘김 형식이 확정된다.

**Verification:**
- [x] 샘플 문장 3~5개에 대해 적용 전후 예시를 검토한다.
- [x] 파일명, 버전 번호, URL이 변경되지 않는지 확인한다.

**Dependencies:** Task 1

**Files likely touched:**
- `plans/html-period-line-break-plan.md`

**Estimated scope:** Small

### Checkpoint: Audit Complete
- [x] 줄넘김 후보와 제외 대상이 구분됐다.
- [x] 적용 방식이 HTML 구조를 깨지 않는다는 근거가 확인됐다.

### Phase 2: Source Update

## Task 3: Apply line breaks in source Markdown HTML

**Description:** `docs/01_requirements/01_requirements.md`의 본문 텍스트에서 문장 종료 마침표 뒤에 줄넘김을 적용한다.

**Acceptance criteria:**
- [x] 요구사항 문서의 긴 본문 문단은 문장 단위로 줄이 나뉜다.
- [x] HTML 태그 구조는 변경되지 않는다.
- [x] URL, 파일명, 버전, 숫자 표기는 변경되지 않는다.

**Verification:**
- [x] `rg -n "01_requirements\.html|v1\.1|1\.5|requirements\.css|requirements\.js"`로 제외 대상이 유지되는지 확인한다.
- [x] 주요 문단을 수동 검토한다.

**Dependencies:** Task 2

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

## Task 4: Regenerate public HTML

**Description:** 수정된 원본 Markdown에서 `pages/01_requirements.html`을 재생성한다.

**Acceptance criteria:**
- [x] `pages/01_requirements.html`이 원본과 같은 줄넘김 구조를 반영한다.
- [x] generated page에 Markdown 코드 fence가 남지 않는다.
- [x] 외부 CSS/JS 링크가 유지된다.

**Verification:**
- [x] `rg -n "^```" pages\01_requirements.html` returns no matches.
- [x] `rg -n "../assets/css/requirements.css|../assets/js/requirements.js" pages\01_requirements.html` confirms asset links.

**Dependencies:** Task 3

**Files likely touched:**
- `pages/01_requirements.html`

**Estimated scope:** Small

### Checkpoint: Source and Generated HTML Match
- [x] 원본과 generated HTML이 같은 본문 줄넘김 정책을 가진다.
- [x] generated HTML이 정상적으로 로드 가능한 구조를 유지한다.

### Phase 3: Validation

## Task 5: Validate HTML structure and visual risk

**Description:** 줄넘김 후 HTML 태그, 표, 목차, 스크립트 참조가 깨지지 않았는지 확인한다.

**Acceptance criteria:**
- [x] inline `<style>` 또는 inline `<script>`가 다시 생기지 않는다.
- [x] 삭제된 `02_`~`06_` HTML 링크가 다시 생기지 않는다.
- [x] 주요 표와 문단의 텍스트가 과도하게 분리되지 않는다.

**Verification:**
- [x] `rg --pcre2 -n '<style|</style>|<script(?![^>]*\bsrc=)' docs\01_requirements\01_requirements.md pages\01_requirements.html` returns no matches.
- [x] `rg -n '02_overturizim\.html|03_korea_japan\.html|04_trip_train\.html|05_astro_rag_proposal\.html|06_kdrama-pipeline\.html' docs pages index.html` returns no matches.
- [x] Static preview checks that line breaks improve readability without layout breakage.

**Dependencies:** Task 4

**Files likely touched:**
- None unless fixes are needed

**Estimated scope:** Small

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| HTML 속성 안의 `.`를 잘못 줄바꿈 | High | 텍스트 노드 또는 수동 확인된 본문 구간만 수정한다. |
| 파일명, 버전, 숫자 표기가 깨짐 | High | 제외 패턴을 검증 명령으로 확인한다. |
| 표 셀 텍스트가 과도하게 길어지거나 어색해짐 | Medium | 표 셀은 긴 문장만 선별 적용한다. |
| 화면 줄바꿈이 HTML 개행을 반영하지 않음 | Medium | 실제 시각적 줄바꿈이 필요하면 `<br>` 또는 CSS `white-space` 적용을 별도 검토한다. |

## Open Questions
- 줄넘김은 HTML 소스 가독성 목적이면 개행 문자만 넣을지, 브라우저 표시까지 강제하려면 `<br>`을 넣을지 결정이 필요하다.
- 모든 문장 마침표에 적용할지, 긴 문단과 표 셀에만 적용할지 결정이 필요하다.

## Definition of Done
- [x] 줄넘김 후보와 제외 대상이 문서화된다.
- [x] 원본 Markdown HTML에 문장 단위 줄넘김이 적용된다.
- [x] generated HTML이 재생성된다.
- [x] URL, 파일명, 버전, 숫자 표기가 깨지지 않는다.
- [x] HTML 구조와 asset 링크가 유지된다.

