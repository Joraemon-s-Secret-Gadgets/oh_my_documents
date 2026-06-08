---
작성자: llm팀
상태: 진행후
---

# Implementation Plan: 우선순위별 PoC·Production 범위 반영

## Overview
`docs/01_requirements/14_P_plan.md`의 P1~P4 우선순위와 단계별 추진 기준을 요구사항 원문과 HTML 문서에 일관되게 반영한다. 긴 단계 설명은 표 위 문단에 두고, 표 안에는 `구현`, `설계`, `정의`, `제외` 같은 짧은 상태값만 남긴다.

## Implementation Result

PoC/Production 단계 설명은 표 위 문단으로 분리하고, 표 안에는 짧은 상태값만 남긴다. 이 방식은 HTML/PDF 출력에서 단계 컬럼의 글자가 잘리는 문제를 줄이고, 우선순위별 의미를 표 위 설명에서 명확히 전달한다.

| 반영 항목 | 결과 |
|---|---|
| 단계 설명 | 표 위 문단으로 분리 |
| PoC 컬럼 | `구현`, `설계`, `정의`, `제외` 같은 짧은 상태값 사용 |
| Production 컬럼 | `고도화`, `구현`, `검토` 같은 짧은 상태값 사용 |
| 상태 컬럼 | `핵심`, `선택 구현`, `설계`, `Production`, `제외`로 정리 |
| HTML 대응 | 긴 문구를 표 밖으로 분리해 좁은 화면과 PDF 출력에서 잘림 위험 완화 |
| 기능 ID 표 | 우선순위 순서로 재정렬하고 비고는 원래 설명으로 유지 |

## Target Scope

PoC 단계는 P1 구현을 핵심 범위로 한다.
P2는 PoC에서 설계까지 완료하고, 일정 여유가 있을 경우 일부 구현한다.
P3는 PoC에서 설계 산출물까지만 정리한다.
P4는 Production 단계에서 구현한다.
P5는 이번 프로젝트 대상에서 제외하고 향후 검토한다.

| 우선순위 | 기능 범위 | PoC | Production | 상태 |
|---|---|---|---|---|
| P1 | 오버투어리즘 회피, 한일 축제 기반 여정 추천, 일주일 이내 여행의 날씨 기반 추천 | 구현 | 고도화 | 핵심 |
| P2 | K-Drama 촬영지 탐색, 애니메이션 성지순례 | 설계 | 구현 | 선택 구현 |
| P3 | 철도 패스 기반 소도시 여행, 체험형 여행 | 설계 | 구현 | 설계 |
| P4 | 스키 액티비티 여행 추천 | 정의 | 구현 | Production |
| P5 | 별 관측, 치유·웰니스, 예산 역산 | 제외 | 검토 | 제외 |

## Architecture Decisions

- `14_P_plan.md`를 우선순위와 단계 기준의 단일 기준 문서로 둔다.
- `01_requirements.md`는 기능 요구사항의 상세 정의를 유지하되, 각 기능의 추진 단계와 현재 범위를 명확히 표시한다.
- `pages/01_requirements.html`은 표 안의 긴 문구를 줄이고 표 위 설명으로 단계 기준을 전달한다.
- P5 항목은 상세 요구기능 표에서는 제외하고, `우선순위 및 단계별 추진 범위` 표에 `이번 프로젝트 제외 / 향후 검토` 상태로 남겨 후속 기획에서 추적 가능하게 한다.

## Task List

### Phase 1: 기준 문서 정리

## Task 1: `14_P_plan.md`에 단계별 추진 기준 추가

**Description:** 기존 P1~P5 우선순위 목록에 PoC·Production 단계 기준을 추가한다. 사용자가 문서 하나만 봐도 어떤 기능을 언제 구현하거나 설계하는지 알 수 있게 만든다.

**Acceptance criteria:**
- [x] 표 위 설명에 P1은 PoC 핵심 구현 범위로 명시된다.
- [x] 표 위 설명에 P2는 PoC 설계 및 일정 여유 시 일부 구현으로 명시된다.
- [x] 표 위 설명에 P3는 PoC 설계 산출물 범위로 명시된다.
- [x] 표 위 설명에 P4는 Production 구현 범위로 명시된다.
- [x] 표 위 설명에 P5는 이번 프로젝트 제외 및 향후 검토로 명시된다.
- [x] 표 안의 단계 컬럼은 `구현`, `설계`, `정의`, `제외`, `검토`처럼 짧은 상태값을 사용한다.

**Verification:**
- [x] `rg -n "PoC 단계는 P1|P2는 PoC|P3는 PoC|P4는 Production|P5는 이번|구현|설계|정의|제외" docs/01_requirements/14_P_plan.md`

**Dependencies:** None

**Files likely touched:**
- `docs/01_requirements/14_P_plan.md`

**Estimated scope:** Small

### Phase 2: 요구사항 원문 반영

## Task 2: `01_requirements.md`의 범위 설명 정합성 조정

**Description:** 요구사항 문서의 범위, 핵심 가치, 서비스별 세부 기능 설명을 P1~P4 중심으로 조정한다. P5에 해당하는 별 관측, 치유·웰니스, 예산 역산은 현재 구현 범위가 아니라 후속 검토 대상으로 표현한다.

**Acceptance criteria:**
- [x] `1.2 범위`가 P1~P4 기준과 충돌하지 않는다.
- [x] `3.2 핵심 가치 제안`에서 PoC 핵심 가치가 P1 중심으로 드러난다.
- [x] P5 항목은 현재 프로젝트 구현 범위처럼 보이지 않는다.

**Verification:**
- [x] `rg -n "별 관측|치유·웰니스|예산 역산|향후 검토|이번 프로젝트 제외" docs/01_requirements/01_requirements.md`

**Dependencies:** Task 1

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

## Task 3: `4.6 서비스별 세부 기능`에 우선순위·단계 표 추가

**Description:** `4.6 서비스별 세부 기능` 상단에 P1~P5 매핑 표를 추가한다. 단계별 상세 설명은 표 위 문단에 두고, 표 안에는 짧은 상태값만 사용한다.

**Acceptance criteria:**
- [x] P1~P5별 기능 범위와 단계가 표로 정리된다.
- [x] 날씨 기반 추천은 P1 행에 포함되고 PoC 값은 `구현`으로 표시된다.
- [x] K-Drama와 애니메이션 성지순례는 P2 행에 포함되고 PoC 값은 `설계`로 표시된다.
- [x] 철도 패스와 체험형 여행은 P3 행에 포함되고 PoC 값은 `설계`로 표시된다.
- [x] 스키 액티비티는 P4 행에 포함되고 Production 값은 `구현`으로 표시된다.
- [x] 별 관측, 웰니스, 예산 역산은 P5 행에 포함되고 PoC 값은 `제외`로 표시된다.

**Verification:**
- [x] `rg -n "PoC 단계는 P1|P2는 PoC|P3는 PoC|P4는 Production|P5는 이번|우선순위" docs/01_requirements/01_requirements.md`

**Dependencies:** Task 2

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

## Task 4: 기능 요구사항 표를 우선순위 순서로 정렬하고 비고 원복

**Description:** 후속 요청에 따라 기존 FR 표의 비고에는 우선순위와 추진 단계를 넣지 않고 원래 설명을 유지한다. 대신 기능 ID가 있는 표는 P1, P2, P3, P4, P5, 우선순위 미지정 순서로 정렬한다.

**Acceptance criteria:**
- [x] `FR-OTR-*`, `FR-FES-*`, 날씨 기반 추천은 P1 그룹으로 정렬된다.
- [x] K-Drama 및 `FR-ANIME-*`는 P2 그룹으로 정렬된다.
- [x] `FR-RAIL-*`, 공예·체험형 여행은 P3 그룹으로 정렬된다.
- [x] 스키 중심 액티비티는 P4 그룹으로 정렬된다.
- [x] `FR-ASTRO-*`, 웰니스, 예산 역산은 P5 상세 요구기능에서 제외하고 우선순위 및 단계별 추진 범위 표에만 기록한다.
- [x] `FR-JP-*`는 우선순위 미지정 기반 기능으로 마지막에 배치된다.
- [x] 기능 ID 표의 비고는 우선순위 문구 없이 원래 설명으로 유지된다.

**Verification:**
- [x] `rg -n "P1 /|P2 /|P3 /|P4 /|P5 /|PoC 구현|PoC 설계|가능 시 구현|이번 프로젝트 제외" docs/01_requirements/01_requirements.md pages/01_requirements.html`

**Dependencies:** Task 3

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

### Phase 3: HTML 문서 반영

## Task 5: `pages/01_requirements.html`에 우선순위 표와 배지 추가

**Description:** Markdown 요구사항 문서의 변경 사항을 HTML 페이지에 반영한다. `4.6 서비스별 세부 기능`에 우선순위 및 단계별 추진 범위 표를 추가하고, 기능 ID 표는 우선순위 순서로 정렬하되 비고는 원래 설명을 유지한다.

**Acceptance criteria:**
- [x] HTML에서 P1~P4 추진 단계가 명확히 보인다.
- [x] P5는 표 위 설명과 P5 행에서 제외/검토로 구분된다.
- [x] 기존 TOC와 섹션 ID가 깨지지 않는다.
- [x] 기존 표 구조와 문서 레이아웃이 유지된다.
- [x] HTML 기능 ID 표의 비고는 우선순위 문구 없이 원래 설명으로 유지된다.

**Verification:**
- [x] `rg -n "PoC 단계는 P1|P2는 PoC|P3는 PoC|P4는 Production|P5는 이번|phase-status|P1|P2|P3|P4|P5" pages/01_requirements.html`

**Dependencies:** Task 4

**Files likely touched:**
- `pages/01_requirements.html`

**Estimated scope:** Medium

## Task 6: CSS 배지 스타일 보강

**Description:** HTML에 추가되는 P1~P5와 단계 상태를 기존 문서 디자인 톤에 맞게 표시할 수 있도록 CSS 클래스를 추가한다.

**Acceptance criteria:**
- [x] `P1`, `P2`, `P3`, `P4`, `P5` 우선순위 배지와 `구현`, `설계`, `정의`, `제외` 상태 배지가 구분된다.
- [x] 모바일 화면에서 배지와 표 텍스트가 겹치지 않도록 줄바꿈 가능한 배지 스타일을 사용한다.
- [x] 기존 `sbadge` 또는 유사 스타일과 충돌하지 않는다.

**Verification:**
- [x] `rg -n "priority|phase|p1|p2|p3|p4|scope" assets/css/requirements.css`

**Dependencies:** Task 5

**Files likely touched:**
- `assets/css/requirements.css`

**Estimated scope:** Small

### Phase 4: 최종 검증

## Task 7: 문서 간 정합성 검증

**Description:** `14_P_plan.md`, `01_requirements.md`, `01_requirements.html`의 우선순위와 단계 표현이 서로 일치하는지 확인한다.

**Acceptance criteria:**
- [x] 세 문서 모두 표 위 설명에서 P1은 PoC 핵심 구현으로 표현한다.
- [x] 세 문서 모두 표 위 설명에서 P2는 PoC 설계 및 일정 여유 시 일부 구현으로 표현한다.
- [x] 세 문서 모두 표 위 설명에서 P3는 PoC 설계 산출물로 표현한다.
- [x] 세 문서 모두 표 위 설명에서 P4는 Production 구현으로 표현한다.
- [x] 세 문서 모두 표 위 설명에서 P5는 이번 프로젝트 제외 또는 향후 검토로 표현한다.
- [x] 세 문서 모두 표 안에서는 짧은 상태값을 사용한다.

**Verification:**
- [x] `rg -n "PoC 단계는 P1|P2는 PoC|P3는 PoC|P4는 Production|P5는 이번|향후 검토" docs/01_requirements pages/01_requirements.html`
- [x] `git diff -- docs/01_requirements/14_P_plan.md docs/01_requirements/01_requirements.md pages/01_requirements.html assets/css/requirements.css`

**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6

**Files likely touched:**
- `docs/01_requirements/14_P_plan.md`
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`
- `assets/css/requirements.css`

**Estimated scope:** Small

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 기존 요구사항에 P5 기능이 이미 포함되어 있어 범위가 혼란스러울 수 있음 | Medium | 상세 요구기능에서는 제외하고 추진 범위 표에 `향후 검토` 상태로 명확히 표시 |
| Markdown과 HTML 문서 내용이 어긋날 수 있음 | Medium | `rg`로 핵심 문구를 양쪽에서 검증 |
| HTML 표에 배지 추가 시 모바일 레이아웃이 깨질 수 있음 | Medium | 기존 CSS 패턴을 재사용하고 줄바꿈 가능한 배지로 구현 |
| P2의 선택 구현 범위가 모호할 수 있음 | Low | P2는 기본적으로 설계 산출물을 완료 기준으로 두고 일부 구현 가능성은 표 위 설명으로 분리 |

## Open Questions

- K-Drama 촬영지 탐색은 별도 FR ID를 신규로 추가할지, 기존 촬영지/콘텐츠 추천 요구사항에 통합할지 결정이 필요하다.
- P4 스키 액티비티를 기존 `사계절 액티비티` 요구사항의 하위 범위로 둘지, 별도 스키 전용 요구사항으로 분리할지 결정이 필요하다.
- P5 제외 항목은 상세 요구기능 표가 아니라 우선순위 및 단계별 추진 범위 표 안의 `제외/검토` 상태값으로 표시한다.
