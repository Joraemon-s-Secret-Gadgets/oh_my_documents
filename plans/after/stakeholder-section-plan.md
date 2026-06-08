---
작성자: llm팀
상태: 진행후
---

# Implementation Plan: 이해관계자 섹션 추가

## Overview
요구사항 정의서에는 개발 대상 기능뿐 아니라 요구사항을 읽고 검토할 이해관계자가 명확해야 한다. 이 계획은 사용자가 제공한 이해관계자 카드 HTML을 문서 흐름에 자연스럽게 추가하고, 기존 섹션 번호와 목차를 일관되게 재정렬하는 절차를 정의한다.

## Current Structure
현재 `01_requirements` 문서는 다음 순서로 구성되어 있다.

```text
1. 문서 개요
2. 서비스 개요
3. 기능 요구사항
4. API 연동 요구사항
5. 비기능 요구사항
6. 데이터 요구사항
7. 제약사항 및 가정
8. 변경 이력
```

사용자가 제안한 섹션은 `4. 이해관계자`로 되어 있지만, 현재 4번은 API 연동 요구사항이다. 요구사항 정의서 흐름상 이해관계자는 기능/API보다 앞에서 정의되는 편이 자연스럽다.

## Target Structure
이해관계자 섹션을 `문서 개요` 다음, `서비스 개요` 앞에 배치한다.

```text
1. 문서 개요
2. 이해관계자
3. 서비스 개요
4. 기능 요구사항
5. API 연동 요구사항
6. 비기능 요구사항
7. 데이터 요구사항
8. 제약사항 및 가정
9. 변경 이력
```

## Architecture Decisions
- `pages/01_requirements.html`은 generated output이므로 직접 편집하지 않고 `docs/01_requirements/01_requirements.md`를 수정한 뒤 재생성한다.
- 새 섹션 id는 충돌을 피하고 의미를 명확히 하기 위해 `s2`를 사용한다.
- 기존 `s2`~`s8`은 한 단계씩 뒤로 밀어 `s3`~`s9`로 재정렬한다.
- 사용자가 제공한 `s4sh` id는 현재 문서의 섹션 체계와 맞지 않으므로 사용하지 않는다.
- 이해관계자 카드는 기존 문서 스타일에 맞춰 `card-grid`, `mini-card`, `mc-type`, `mc-name`, `mc-desc` CSS를 추가한다.

## Task List

### Phase 1: Structure and Numbering

## Task 1: Insert stakeholder section after document overview

**Description:** `1. 문서 개요` 섹션 다음에 이해관계자 섹션을 추가한다. 사용자가 제공한 카드 내용을 유지하되, 번호는 `2. 이해관계자`, id는 `s2`로 정리한다.

**Acceptance criteria:**
- [x] 새 섹션이 `1. 문서 개요`와 `서비스 개요` 사이에 위치한다.
- [x] 섹션 제목은 `2. 이해관계자`다.
- [x] 이해관계자 카드 4개가 포함된다.
- [x] 제공 문구의 `분역` 오탈자는 문맥상 `분위기`로 보정하지 않는다. 해당 요청은 카드 내용과 별개이므로 유지 대상이 아니다.

**Verification:**
- [x] `rg -n "2. 이해관계자|자유여행자|지자체|서비스 관리자|공공 데이터 제공 기관" docs\01_requirements\01_requirements.md`

**Dependencies:** None

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

## Task 2: Renumber existing sections and ids

**Description:** 새 이해관계자 섹션 삽입으로 기존 2~8번 섹션을 3~9번으로 밀고, 목차 링크와 본문 id를 함께 수정한다.

**Acceptance criteria:**
- [x] 기존 `2. 서비스 개요`가 `3. 서비스 개요`가 된다.
- [x] 기존 `3. 기능 요구사항`이 `4. 기능 요구사항`이 된다.
- [x] 기존 `4. API 연동 요구사항`이 `5. API 연동 요구사항`이 된다.
- [x] 기존 `5. 비기능 요구사항`이 `6. 비기능 요구사항`이 된다.
- [x] 기존 `6. 데이터 요구사항`이 `7. 데이터 요구사항`이 된다.
- [x] 기존 `7. 제약사항 및 가정`이 `8. 제약사항 및 가정`이 된다.
- [x] 기존 `8. 변경 이력`이 `9. 변경 이력`이 된다.
- [x] TOC의 href와 본문 id가 모두 일치한다.

**Verification:**
- [x] `rg -n "id=\"s[2-9]|href=\"#s[2-9]|Section 0[2-9]|[2-9]\." docs\01_requirements\01_requirements.md` 결과를 수동 검토한다.
- [x] 기존 `s4sh` id가 없음을 확인한다.

**Dependencies:** Task 1

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

### Checkpoint: Document Structure
- [x] 섹션 번호가 1~9까지 자연스럽게 이어진다.
- [x] TOC에서 모든 링크가 실제 id를 가리킨다.

### Phase 2: Styling

## Task 3: Add card grid styles

**Description:** 이해관계자 카드가 기존 문서 톤과 맞도록 `requirements.css`에 카드 레이아웃 스타일을 추가한다.

**Acceptance criteria:**
- [x] `.card-grid`가 반응형 grid로 표시된다.
- [x] `.mini-card`가 기존 `detail-docs` 또는 `info-tbl`과 어울리는 restrained card 스타일을 가진다.
- [x] `.mc-type`, `.mc-name`, `.mc-desc`가 계층적으로 읽힌다.
- [x] 모바일에서 카드가 1열로 정렬된다.

**Verification:**
- [x] `rg -n "card-grid|mini-card|mc-type|mc-name|mc-desc" assets\css\requirements.css`
- [x] HTML에서 카드 클래스가 CSS와 일치하는지 확인한다.

**Dependencies:** Task 1

**Files likely touched:**
- `assets/css/requirements.css`

**Estimated scope:** Small

### Phase 3: Regeneration and Validation

## Task 4: Regenerate `pages/01_requirements.html`

**Description:** 원본 Markdown HTML을 기준으로 public page를 재생성한다.

**Acceptance criteria:**
- [x] `pages/01_requirements.html`에 이해관계자 섹션이 반영된다.
- [x] Markdown code fence가 generated page에 남지 않는다.
- [x] CSS/JS 링크가 유지된다.

**Verification:**
- [x] `rg -n "^```" pages\01_requirements.html` returns no matches.
- [x] `rg -n "../assets/css/requirements.css|../assets/js/requirements.js" pages\01_requirements.html`

**Dependencies:** Task 2, Task 3

**Files likely touched:**
- `pages/01_requirements.html`

**Estimated scope:** Small

## Task 5: Validate navigation and regressions

**Description:** 섹션 번호 변경으로 TOC, active navigation, 기존 내부 링크가 깨지지 않았는지 확인한다.

**Acceptance criteria:**
- [x] TOC의 모든 `href="#..."` 대상 id가 존재한다.
- [x] 삭제된 `02_`~`06_` HTML 링크가 다시 생기지 않는다.
- [x] inline `<style>` 또는 inline `<script>`가 생기지 않는다.
- [x] 기존 `s4` API 링크가 새 번호 체계에 맞게 업데이트된다.

**Verification:**
- [x] Static id/href validation script or grep review confirms link targets exist.
- [x] `rg --pcre2 -n '<style|</style>|<script(?![^>]*\bsrc=)' docs\01_requirements\01_requirements.md pages\01_requirements.html` returns no matches.
- [x] `rg -n '02_overturizim\.html|03_korea_japan\.html|04_trip_train\.html|05_astro_rag_proposal\.html|06_kdrama-pipeline\.html' docs pages index.html` returns no matches.

**Dependencies:** Task 4

**Files likely touched:**
- None unless fixes are needed

**Estimated scope:** Small

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| 섹션 번호를 일부만 변경해 TOC가 깨짐 | High | id/href 검증을 실행한다. |
| 기존 내부 링크 `#s3-6` 등이 잘못된 섹션을 가리킴 | High | 기능 요구사항 섹션 id를 함께 `s4-*`로 이동한다. |
| 카드 스타일이 문서 톤과 어긋남 | Medium | 기존 문서의 `detail-docs`, `info-tbl`, brand token을 재사용한다. |
| 변경 이력, 제약사항 섹션 분리 스타일이 잘못된 id에 남음 | Medium | `#s8` 전용 CSS가 있다면 새 변경 이력 id `#s9`로 조정한다. |

## Open Questions
- 이해관계자 섹션을 `2. 이해관계자`로 둘지, 사용자가 제안한 대로 `4. 이해관계자`로 둘지 최종 결정이 필요하다. 본 계획은 요구사항 정의서 흐름상 `2. 이해관계자`를 권장한다.

## Definition of Done
- [x] 이해관계자 섹션이 문서 개요 뒤에 추가된다.
- [x] 전체 섹션 번호와 TOC가 일관된다.
- [x] 이해관계자 카드가 기존 디자인과 어울리게 표시된다.
- [x] generated HTML이 재생성된다.
- [x] 내부 링크, asset 링크, HTML 구조가 검증된다.

