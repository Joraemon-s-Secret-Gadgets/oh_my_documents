# Implementation Plan: Markdown 서비스 기능을 기능 요구사항에 통합

## Overview
`docs/01_requirements/02_*.md`부터 `06_*.md`까지의 세부 기능 요구사항 문서를 읽고, 각 서비스의 핵심 기능을 추출해 상위 문서인 `docs/01_requirements/01_requirements.md`의 `3. 기능 요구사항` 섹션에 체계적으로 반영한다. `docs/`가 원본이므로 모든 내용 변경은 Markdown 원본에 먼저 적용하고, 이후 `pages/*.html`을 재생성한다.

## Source Documents
```text
Parent:
- docs/01_requirements/01_requirements.md

Detail sources:
- docs/01_requirements/02_overturizim.md
- docs/01_requirements/03_korea_japan.md
- docs/01_requirements/04_trip_train.md
- docs/01_requirements/05_astro_rag_proposal.md
- docs/01_requirements/06_kdrama-pipeline.md
```

## Goal
- 세부 문서에 흩어진 서비스 기능을 상위 요구사항 정의서의 기능 요구사항으로 통합한다.
- `02_`~`06_` 문서는 하위 세부 기능 요구사항 문서로 유지한다.
- `01_requirements.md`에는 전체 서비스를 아우르는 기능 요구사항 카탈로그를 둔다.
- 중복 요구사항, ID 충돌, 추상적인 기능 설명을 줄이고 추적 가능한 요구사항으로 정리한다.

## Integration Strategy

### Parent Requirement Structure
`docs/01_requirements/01_requirements.md`의 `3. 기능 요구사항`은 다음 구조를 목표로 한다.

```text
3. 기능 요구사항
├── 3.1 공통 사용자 인터페이스
├── 3.2 추천/탐색 기능
├── 3.3 지도/위치/경로 기능
├── 3.4 RAG/챗봇/에이전트 기능
├── 3.5 외부 데이터/API 연동
├── 3.6 서비스별 세부 기능
│   ├── 3.6.1 오버투어리즘 대응 여행 추천
│   ├── 3.6.2 한일 축제 여행 챗봇
│   ├── 3.6.3 RailRoute-RAG
│   ├── 3.6.4 StarryNight-RAG
│   └── 3.6.5 K-drama 촬영지 데이터 파이프라인
└── 3.7 관리자/운영/검증 기능
```

### Requirement ID Convention
기존 `FR-001` 형식은 유지하되, 서비스별 기능은 추적 가능한 prefix를 추가한다.

```text
FR-COM-###  공통 기능
FR-REC-###  추천/탐색 기능
FR-MAP-###  지도/경로 기능
FR-RAG-###  RAG/챗봇/에이전트 기능
FR-API-###  외부 API/데이터 연동
FR-OTR-###  오버투어리즘 서비스 기능
FR-FES-###  한일 축제 여행 챗봇 기능
FR-RAIL-### RailRoute-RAG 기능
FR-ASTRO-### StarryNight-RAG 기능
FR-KDRAMA-### K-drama 파이프라인 기능
FR-OPS-###  운영/관리 기능
```

### Requirement Row Format
상위 문서의 기능 요구사항 표는 다음 필드를 기본으로 한다.

```text
ID | 서비스/영역 | 요구사항 내용 | 우선순위 | 출처 문서 | 비고
```

출처 문서는 하위 문서 링크를 사용한다.

```html
<a href="./02_overturizim.html">02_overturizim</a>
```

## Task List

### Phase 1: Source Reading and Extraction

## Task 1: Extract service features from detail Markdown

**Description:** `02_`~`06_` Markdown 원본에서 서비스 기능, 사용자 행동, 시스템 기능, 데이터 처리 기능, 외부 연동 기능을 추출한다.

**Acceptance criteria:**
- [ ] 각 세부 문서별 핵심 기능 목록이 정리된다.
- [ ] 기능이 사용자 기능, 시스템 기능, 데이터 기능, 외부 연동 기능으로 분류된다.
- [ ] 단순 설명 문장과 실제 요구사항 후보가 구분된다.

**Verification:**
- [ ] 각 문서에서 최소 5개 이상의 기능 후보가 추출된다.
- [ ] 추출 기능마다 출처 문서명이 연결된다.

**Dependencies:** None

**Files likely touched:**
- Read only during extraction

**Estimated scope:** Medium: 5 source documents

## Task 2: Deduplicate and classify extracted features

**Description:** 세부 문서에서 추출한 기능 중 중복되는 요구사항을 병합하고, 공통 기능과 서비스별 기능을 분리한다.

**Acceptance criteria:**
- [ ] 공통 기능과 서비스별 기능이 분리된다.
- [ ] 같은 의미의 요구사항은 하나로 병합된다.
- [ ] 병합된 요구사항은 모든 출처 문서를 유지한다.

**Verification:**
- [ ] 챗봇, 추천, 지도, 외부 API, 데이터 파이프라인 기능이 중복 없이 분류된다.
- [ ] 서비스별 고유 기능은 별도 섹션에 남아 있다.

**Dependencies:** Task 1

**Files likely touched:**
- Temporary notes or direct edits to `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

### Checkpoint: Extraction Complete
- [ ] 기능 후보 목록이 문서별로 존재한다.
- [ ] 공통 기능과 서비스별 기능이 구분된다.
- [ ] 상위 문서에 넣을 요구사항 ID 체계가 확정된다.

### Phase 2: Parent Requirement Update

## Task 3: Redesign the functional requirements section

**Description:** `docs/01_requirements/01_requirements.md`의 `3. 기능 요구사항` 섹션을 새 분류 체계와 ID convention에 맞게 정리한다.

**Acceptance criteria:**
- [ ] `3. 기능 요구사항`에 공통 기능 섹션이 있다.
- [ ] `3. 기능 요구사항`에 서비스별 세부 기능 섹션이 있다.
- [ ] 각 요구사항은 ID, 서비스/영역, 내용, 우선순위, 출처, 비고를 가진다.
- [ ] 기존 요구사항 중 유효한 내용은 보존하거나 새 ID로 매핑한다.

**Verification:**
- [ ] `FR-COM`, `FR-REC`, `FR-MAP`, `FR-RAG`, `FR-API` 계열 요구사항이 존재한다.
- [ ] `FR-OTR`, `FR-FES`, `FR-RAIL`, `FR-ASTRO`, `FR-KDRAMA` 계열 요구사항이 존재한다.
- [ ] 출처 링크가 `pages/` 기준 상대 링크로 동작한다.

**Dependencies:** Task 2

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Large: one large source document section

## Task 4: Update table of contents and cross-links

**Description:** 기능 요구사항 섹션이 바뀌면 TOC, anchor ID, 세부 기능 요구사항 링크를 함께 갱신한다.

**Acceptance criteria:**
- [ ] TOC의 `3. 기능 요구사항` 하위 항목이 실제 섹션 ID와 일치한다.
- [ ] 세부 기능 요구사항 문서 링크가 유지된다.
- [ ] 중복 anchor ID가 없다.

**Verification:**
- [ ] `Select-String`으로 `href="#..."`와 실제 `id="..."`를 spot check한다.
- [ ] `pages/01_requirements.html` 재생성 후 TOC 클릭이 가능한 구조다.

**Dependencies:** Task 3

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Small

### Checkpoint: Parent Source Updated
- [ ] 상위 요구사항 문서가 모든 세부 기능을 요약한다.
- [ ] 세부 문서는 상세 근거 문서로 계속 유지된다.
- [ ] 요구사항 ID가 중복되지 않는다.
- [ ] 출처 링크가 유지된다.

### Phase 3: Regeneration and Verification

## Task 5: Regenerate HTML pages from Markdown

**Description:** 수정된 `docs/` 원본을 기준으로 `pages/*.html`을 다시 생성한다.

**Acceptance criteria:**
- [ ] `pages/01_requirements.html`에 새 기능 요구사항 섹션이 반영된다.
- [ ] `pages/*.html`에 Markdown 코드펜스가 남지 않는다.
- [ ] 6개 generated HTML 파일이 유지된다.

**Verification:**
- [ ] `Select-String -Path pages\*.html -Pattern '^```'` returns no matches.
- [ ] `Get-ChildItem pages\*.html` shows 6 files.
- [ ] `pages/01_requirements.html` contains the new `FR-*` IDs.

**Dependencies:** Task 4

**Files likely touched:**
- `pages/01_requirements.html`
- Other `pages/*.html` if full regeneration is used

**Estimated scope:** Small: generated output

## Task 6: Validate traceability

**Description:** 상위 기능 요구사항과 하위 세부 문서 간 추적성을 검증한다.

**Acceptance criteria:**
- [ ] 각 서비스별 요구사항에는 출처 문서 링크가 있다.
- [ ] 상위 문서에서 `02_`~`06_` 세부 문서로 이동할 수 있다.
- [ ] `index.html`의 요구사항 문서 계층 구조와 상위 문서 내부 구조가 일치한다.

**Verification:**
- [ ] `index.html` links to `01_requirements.html` as parent and `02_`~`06_` as children.
- [ ] `pages/01_requirements.html` links to `02_`~`06_`.
- [ ] 각 서비스 prefix 요구사항이 최소 1개 이상 존재한다.

**Dependencies:** Task 5

**Files likely touched:**
- None unless fixes are needed

**Estimated scope:** Small

### Checkpoint: Ready To Commit
- [ ] `docs/01_requirements/01_requirements.md` contains integrated functional requirements.
- [ ] `pages/01_requirements.html` reflects the integrated requirements.
- [ ] Detail documents remain available as supporting requirement documents.
- [ ] Changes can be committed as `docs(requirements): integrate service features`.

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| 세부 문서가 HTML-heavy Markdown이라 기능 추출이 어렵다 | High | 제목, 카드, 표, badge, section heading 중심으로 추출한다. |
| 기능 요구사항이 너무 많아 상위 문서가 비대해진다 | Medium | 상위 문서는 카탈로그 수준으로 요약하고, 상세 내용은 출처 문서 링크로 연결한다. |
| 기존 `FR-###` ID와 새 ID가 충돌한다 | Medium | 새 prefix 기반 ID를 사용하고 기존 ID는 필요한 경우 비고에 남긴다. |
| 서비스별 기능과 공통 기능이 섞인다 | Medium | 공통 기능은 먼저 추출하고, 서비스 고유 기능은 별도 하위 섹션으로 분리한다. |
| 생성 HTML과 Markdown 원본이 달라진다 | High | 항상 `docs/` 수정 후 `pages/`를 재생성한다. |

## Open Questions
- 기존 `FR-001` 형식을 완전히 새 prefix 체계로 대체할 것인가, 기존 ID를 일부 유지할 것인가?
- 상위 문서에 모든 서비스 기능을 표로 넣을 것인가, 서비스별 요약 표와 상세 링크만 둘 것인가?
- 요구사항 우선순위는 세부 문서에 있는 값을 따를 것인가, 상위 문서에서 재평가할 것인가?

## Definition of Done
- [ ] `02_`~`06_` 세부 문서에서 서비스 기능이 추출되어 있다.
- [ ] `01_requirements.md`의 `3. 기능 요구사항`에 공통 기능과 서비스별 기능이 통합되어 있다.
- [ ] 요구사항 ID가 중복되지 않는다.
- [ ] 각 서비스별 요구사항은 출처 문서 링크를 가진다.
- [ ] `pages/01_requirements.html`이 재생성되어 변경사항을 반영한다.
- [ ] `pages/*.html`에 Markdown 코드펜스가 없다.
- [ ] `index.html`의 문서 계층 구조와 상위 요구사항 문서 내부 구조가 일치한다.
