# Implementation Plan: 필수 Auth·Review 요구사항 보강

## Overview

요구사항 정의서에 역할과 권한 모델은 존재하지만, 이를 기능으로 연결하는 인증(Auth), 인가(Authorization), 데이터 제안 검토(Review/Approval) 요구사항이 명시적으로 부족하다. 본 계획은 누락된 필수 기능을 `docs/01_requirements/01_requirements.md`와 `pages/01_requirements.html`에 요구사항 정의서 수준으로 보강하기 위한 작업 기준을 정의한다.

## Writing Rules

- 요구사항 정의서에는 기능이 제공해야 하는 사용자/시스템 관점의 요구사항만 작성한다.
- 구현 방식, DB 테이블 구조, API 엔드포인트 상세, 토큰 방식, 화면 컴포넌트 설계는 이 문서에 작성하지 않는다.
- 기능 요구사항은 `무엇을 해야 하는가`를 중심으로 작성하고, `어떻게 구현할 것인가`는 후속 설계 문서로 분리한다.
- Role ID, 권한 매트릭스, 데이터 접근 범위와 충돌하지 않도록 기능 ID와 비고를 작성한다.
- PoC 핵심 범위(P1)와 혼동되지 않도록 Auth·Review는 운영/Production 요구사항으로 분리한다.

## Missing Required Features

| 기능 영역 | 누락 이유 | 요구사항 정의서 반영 위치 | 우선 반영 수준 |
|---|---|---|---|
| Auth | `R-ADMIN`, `R-LOCAL-OPERATOR`, `R-DATA-PROVIDER`가 있지만 로그인/인가 기능 요구사항이 부족함 | `4.7 운영·관리·검증 기능` | Production 요구사항 |
| Authorization | 권한 매트릭스는 있으나 역할별 접근 제한 기능 ID가 부족함 | `4.7 운영·관리·검증 기능` | Production 요구사항 |
| Review/Approval | 데이터 제안·제공·승인 책임은 있으나 검토/승인 기능 요구사항이 부족함 | `4.7 운영·관리·검증 기능` | Production 요구사항 |
| Audit History | 승인 이력과 감사 로그 후보는 언급되지만 기능 요구사항 ID가 부족함 | `4.7 운영·관리·검증 기능` | Production 요구사항 |

## Proposed Requirement Rows

| ID | 서비스/영역 | 요구사항 내용 | 비고 |
|---|---|---|---|
| `FR-AUTH-001` | 인증 | 서비스는 관리자, 관광 운영자, 데이터 제공 기관 등 권한이 필요한 역할에 대해 로그인 기반 인증을 제공해야 한다. | Production 운영 기능 |
| `FR-AUTH-002` | 인가 | 서비스는 역할별 권한에 따라 데이터 조회, 제안, 승인, 정책 관리 기능 접근을 제한해야 한다. | 권한 매트릭스 연계 |
| `FR-REVIEW-001` | 데이터 제안 | 관광 운영자와 데이터 제공 기관은 소도시·축제·행사 데이터를 제안하거나 제공할 수 있어야 한다. | 제안 상태 관리 |
| `FR-REVIEW-002` | 데이터 검토 | 서비스 관리자는 제안·제공된 데이터를 검토하고 승인, 반려, 수정 요청할 수 있어야 한다. | 승인 책임 분리 |
| `FR-REVIEW-003` | 이력 관리 | 시스템은 데이터 제안, 검토, 승인, 반려, 수정 요청 이력을 추적할 수 있어야 한다. | 감사 로그 후보 |

## Task List

## Task 1: 요구사항 원문에 Auth 기능 추가

**Description:** `4.7 운영·관리·검증 기능`에 인증과 인가 기능 요구사항을 추가한다.

**Acceptance criteria:**
- [ ] `FR-AUTH-001`이 로그인 기반 인증 요구사항으로 추가된다.
- [ ] `FR-AUTH-002`가 역할별 접근 제한 요구사항으로 추가된다.
- [ ] 구현 방식이나 토큰 구조는 작성하지 않는다.

**Verification:**
- [ ] `rg -n "FR-AUTH-001|FR-AUTH-002|인증|인가" docs/01_requirements/01_requirements.md`

**Dependencies:** None

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Small

## Task 2: 요구사항 원문에 Review/Approval 기능 추가

**Description:** `4.7 운영·관리·검증 기능`에 데이터 제안, 검토, 승인, 반려, 이력 추적 요구사항을 추가한다.

**Acceptance criteria:**
- [ ] `FR-REVIEW-001`이 데이터 제안 요구사항으로 추가된다.
- [ ] `FR-REVIEW-002`가 데이터 검토/승인 요구사항으로 추가된다.
- [ ] `FR-REVIEW-003`이 이력 추적 요구사항으로 추가된다.
- [ ] DB 테이블, 승인 워크플로 구현 방식, API 엔드포인트 상세는 작성하지 않는다.

**Verification:**
- [ ] `rg -n "FR-REVIEW-001|FR-REVIEW-002|FR-REVIEW-003|승인|반려|이력" docs/01_requirements/01_requirements.md`

**Dependencies:** Task 1

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Small

## Task 3: HTML 문서 동기화

**Description:** Markdown 요구사항 문서에 추가한 Auth·Review 요구사항을 HTML 요구사항 페이지의 `4.7 운영·관리·검증 기능` 표에 동일하게 반영한다.

**Acceptance criteria:**
- [ ] HTML에 `FR-AUTH-*`와 `FR-REVIEW-*` 행이 추가된다.
- [ ] Markdown과 HTML의 ID, 서비스/영역, 요구사항 내용, 비고가 일치한다.
- [ ] 기존 TOC와 섹션 ID는 변경하지 않는다.

**Verification:**
- [ ] `rg -n "FR-AUTH|FR-REVIEW" docs/01_requirements/01_requirements.md pages/01_requirements.html`

**Dependencies:** Task 1, Task 2

**Files likely touched:**
- `pages/01_requirements.html`

**Estimated scope:** Small

## Task 4: 최종 검증

**Description:** 요구사항 정의서 수준을 벗어난 구현 상세가 들어가지 않았는지 확인하고, 문서 간 정합성을 검증한다.

**Acceptance criteria:**
- [ ] Auth·Review 요구사항은 기능 요구사항 문장으로만 작성된다.
- [ ] DB/API/토큰/화면 구현 상세는 포함되지 않는다.
- [ ] `git diff --check`가 통과한다.

**Verification:**
- [ ] `rg -n "token|JWT|endpoint|테이블|컬렉션|인덱스" docs/01_requirements/01_requirements.md pages/01_requirements.html`
- [ ] `git diff --check`

**Dependencies:** Task 3

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`
- `plans/auth-review-requirements-plan.md`

**Estimated scope:** Small

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 요구사항 문서가 설계 문서처럼 과도하게 상세해질 수 있음 | Medium | 기능 ID, 요구사항 내용, 비고 수준으로만 작성 |
| 기존 역할/권한 표와 중복될 수 있음 | Low | 권한 매트릭스는 기준, FR은 기능 수행 요구사항으로 역할을 분리 |
| PoC 범위로 오해될 수 있음 | Low | 비고에 Production 운영 기능으로 명시 |

## Open Questions

- Auth·Review 요구사항을 이번 차수에 바로 요구사항 정의서에 반영할지, 별도 설계 문서 작성 후 반영할지 결정이 필요하다.
- 데이터 제공 기관의 인증 방식을 사용자 로그인으로 볼지, 기관 API Key 또는 계정 기반 인증으로 분리할지 후속 설계에서 결정이 필요하다.
