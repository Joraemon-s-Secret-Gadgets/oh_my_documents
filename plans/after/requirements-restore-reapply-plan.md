---
작성자: Codex
상태: 진행후
---

# 01_requirements.md 복구 및 선별 재적용 계획

## 목적

현재 `docs/01_requirements/01_requirements.md` 내용이 오염되었을 가능성이 있으므로, 현재 내용을 별도 백업한 뒤 신뢰할 수 있는 이전 커밋의 파일 상태로 복귀하고, 백업본과 기존 계획 문서에서 필요한 추가·수정 내용만 선별해 다시 적용한다.

## 현재 확인 사항

- 현재 브랜치: `main`
- `docs/01_requirements/01_requirements.md`는 `aabd5f6` 기준으로 파일 단위 복구한 뒤 최신 요구사항을 선별 재적용한 상태다.
- 현재 작업 트리에는 복구·재적용 결과로 `docs/`, `pages/`, `index.html`, `.gitignore`, plan 파일 변경이 남아 있다.
- 최근 관련 커밋 후보:
  - `2af6943 docs(project): add project planning document`
  - `aabd5f6 docs(requirements): align service priority scope`
  - `8c2c0c0 docs(requirements): add auth review requirements`
  - `1d64857 docs(requirements): assign api key ownership`
- 복구 기준 커밋은 `aabd5f6`로 확정했다.
- 백업 파일은 `backups/requirements/01_requirements.current.20260529-165609.md`와 `backups/requirements/01_requirements.current.20260529-165609.html`로 생성했다.

## 실행 결과 요약

- `docs/01_requirements/01_requirements.md`를 백업 후 `aabd5f6` 기준으로 복구했다.
- `plans/requirements_update_plan.md`의 기능명세서 성격 항목을 요구사항 정의서 형식으로 선별 반영했다.
- `docs/01_requirements/14_priority_plan.md`를 P1~P5 최신 기준으로 정리했다.
- `docs/00_project_plan/00_project_plan.md`에서 소도시 1곳 집중 일정, 지도 마커 진입, 월별 기상 경향 기준과 충돌하는 문구를 보정했다.
- `pages/01_requirements.html`, `pages/00_project_plan.html`, `index.html`을 원본 문서와 동기화했다.
- `backups/`는 `.gitignore`에 추가해 백업 파일이 커밋에 섞이지 않도록 했다.
- 검증 결과: 핵심 공개/통합 문서에서 `2~4곳`, `군집`, `FR-JP-012`, `공통 기반 기능`, `FR-REC-006` 등 오래된 표현이 검색되지 않았고, inline `<style>`/inline `<script>` 검증과 `git diff --check`가 통과했다.

## 원칙

- `git reset --hard`는 사용하지 않는다.
- 복구는 파일 단위로만 수행한다.
- 현재 파일 내용은 복구 전에 반드시 백업한다.
- 백업본은 재적용 판단용으로 사용하고, 최종 문서의 source of truth는 `docs/01_requirements/01_requirements.md`로 유지한다.
- `pages/01_requirements.html`은 원본 Markdown 복구·재적용 후 마지막에 동기화한다.
- 새 요구사항 ID와 우선순위는 `plans/requirements_update_plan.md`, `plans/docs-content-refresh-plan.md`, `docs/01_requirements/14_priority_plan.md` 기준으로 검증한다.

## 대상 파일

| 구분 | 파일 | 처리 |
| --- | --- | --- |
| 복구 대상 | `docs/01_requirements/01_requirements.md` | 백업 후 이전 커밋 상태로 파일 단위 복귀 |
| 비교 기준 | `backups/requirements/01_requirements.current.<timestamp>.md` | 현재 오염 의심본 백업 |
| 실제 백업 | `backups/requirements/01_requirements.current.20260529-165609.md` | 복구 전 Markdown 백업 |
| 실제 백업 | `backups/requirements/01_requirements.current.20260529-165609.html` | 복구 전 HTML 백업 |
| 선별 적용 기준 | `plans/requirements_update_plan.md` | 추가·수정해야 할 최신 요구사항 원천 |
| 실행 계획 기준 | `plans/docs-content-refresh-plan.md` | docs 전체 최신화 순서 |
| 우선순위 기준 | `docs/01_requirements/14_priority_plan.md` | P1~P5 정합성 확인 |
| 공개 산출물 | `pages/01_requirements.html` | 원본 복구 후 동기화 |

## 작업 계획

### Phase 1. 백업과 기준 커밋 선정

#### Task 1. 현재 오염 의심본 백업

**Description:** 현재 `docs/01_requirements/01_requirements.md` 내용을 복구 전 별도 파일로 저장한다. 필요하면 현재 `pages/01_requirements.html`도 함께 백업해 원본·HTML 차이를 추적한다.

**Acceptance criteria:**
- [x] `backups/requirements/` 아래에 현재 `01_requirements.md` 백업이 생성된다.
- [x] 백업 파일명에 생성 시각 또는 기준 커밋이 포함된다.
- [x] 백업 후 원본과 백업의 해시 또는 크기를 비교해 복사 누락이 없음을 확인한다.

**Verification:**
- [x] `Test-Path backups/requirements/01_requirements.current.<timestamp>.md`
- [x] `Get-FileHash docs/01_requirements/01_requirements.md backups/requirements/01_requirements.current.<timestamp>.md`

**Dependencies:** None

**Files likely touched:**
- `backups/requirements/01_requirements.current.<timestamp>.md`

**Estimated scope:** S

#### Task 2. 복구 기준 커밋 확정

**Description:** 최근 커밋의 `01_requirements.md`를 비교해 오염 전으로 판단되는 기준 커밋을 확정한다. 우선 후보는 `aabd5f6` 이전 또는 `2af6943` 이전 상태이며, 실제 기준은 diff 검토 후 결정한다.

**Acceptance criteria:**
- [x] 오염이 처음 등장한 커밋이 식별된다.
- [x] 복구 기준 커밋 `<baseline>`이 명시된다.
- [x] `<baseline>`의 문서가 필수 요구사항을 지나치게 잃지 않는지 확인된다.

**Verification:**
- [x] `git log --oneline -- docs/01_requirements/01_requirements.md`
- [x] `git diff <baseline>..HEAD -- docs/01_requirements/01_requirements.md`
- [x] `git show <baseline>:docs/01_requirements/01_requirements.md`

**Dependencies:** Task 1

**Files likely touched:** None

**Estimated scope:** S

### Phase 2. 파일 단위 복구

#### Task 3. `01_requirements.md`를 기준 커밋으로 복귀

**Description:** 확정한 `<baseline>`에서 `docs/01_requirements/01_requirements.md`만 가져와 현재 작업 트리에 복구한다. 브랜치 전체를 되돌리지 않고 파일 하나만 복구한다.

**Acceptance criteria:**
- [x] `docs/01_requirements/01_requirements.md`가 `<baseline>` 내용과 일치한다.
- [x] 다른 파일은 이 단계에서 변경하지 않는다.
- [x] 백업 파일은 보존된다.

**Verification:**
- [x] `git diff -- docs/01_requirements/01_requirements.md`
- [x] `git diff <baseline> -- docs/01_requirements/01_requirements.md`
- [x] `git status --short`

**Dependencies:** Task 2

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** S

### Phase 3. 필요한 변경사항 선별 추출

#### Task 4. 백업본에서 유지할 변경사항 목록화

**Description:** 백업본과 복구된 원본을 비교해 유지해야 할 변경, 버려야 할 오염, 판단이 필요한 항목을 분류한다. 단순히 백업본 전체를 다시 덮어쓰지 않는다.

**Acceptance criteria:**
- [x] 유지할 요구사항 ID와 섹션 변경이 목록화된다.
- [x] 제거할 오염 문구가 목록화된다.
- [x] 판단이 필요한 충돌 항목은 별도 메모로 남긴다.

**Verification:**
- [x] `rg -n "FR-STORE|FR-ONBOARD|FR-MAP-005|FR-FEST-ENTRY|FR-PERS|FR-WEATHER|FR-TRIP|FR-STAY|FR-MY|FR-JP-005" backups/requirements docs/01_requirements/01_requirements.md`
- [x] `rg -n "실시간 예보.*추천|복수 소도시|FR-RANK-002|FR-REC-006|예산 역산" backups/requirements docs/01_requirements/01_requirements.md`

**Dependencies:** Task 3

**Files likely touched:**
- Optional: `plans/requirements-restore-reapply-notes.md`

**Estimated scope:** M

#### Task 5. 최신 계획 문서 기준으로 재적용 범위 확정

**Description:** `plans/requirements_update_plan.md`와 `plans/docs-content-refresh-plan.md`를 기준으로, 복구된 요구사항 정의서에 다시 들어가야 할 변경사항을 최종 확정한다.

**Acceptance criteria:**
- [x] `requirements_update_plan.md` 적용 순서 1~16이 재적용 체크리스트로 매핑된다.
- [x] 이미 복구 기준 커밋에 존재하는 항목은 중복 적용하지 않는다.
- [x] 신규 반영 대상과 기존 수정 대상이 구분된다.

**Verification:**
- [x] `rg -n "적용 순서 제안|FR-STORE|FR-WEATHER|FR-ONBOARD|FR-TRIP|FR-MAP|FR-PERS|FR-STAY|FR-MY|FR-API-007" plans/requirements_update_plan.md plans/docs-content-refresh-plan.md`

**Dependencies:** Task 4

**Files likely touched:** None

**Estimated scope:** S

### Phase 4. 요구사항 재적용

#### Task 6. 핵심 서비스 흐름과 추천 파이프라인 재적용

**Description:** 복구된 `01_requirements.md`에 소도시 1곳 집중 일정, 지도·챗봇 진입점, 추천 파이프라인, Explainability 4요소를 반영한다.

**Acceptance criteria:**
- [x] 용어 정의와 3.4 서비스 흐름이 최신 흐름과 일치한다.
- [x] `FR-REC-003`이 추천 이유 4요소를 포함한다.
- [x] 4.8 추천 파이프라인 명세가 추가된다.

**Verification:**
- [x] `rg -n "소도시 1곳|일별 세부 일정|추천 파이프라인|FR-REC-003|Explainability|일정 흐름 이유" docs/01_requirements/01_requirements.md`

**Dependencies:** Task 5

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** M

#### Task 7. 개인화·저장·온보딩·피드백 요구사항 재적용

**Description:** 대화 로그 미저장, 일정·선호 저장, 필수 온보딩, 좋아요/싫어요 피드백, 마이페이지 요구사항을 반영한다.

**Acceptance criteria:**
- [x] `NFR-013`이 저장 대상과 미저장 대상을 분리한다.
- [x] `FR-STORE-*`, `FR-ONBOARD-*`, `FR-PERS-*`, `FR-MY-*`가 요구사항 수준으로 추가된다.
- [x] PoC 로컬 스토리지와 Production 회원 저장이 구분된다.

**Verification:**
- [x] `rg -n "NFR-013|FR-STORE|FR-ONBOARD|FR-PERS|FR-MY|로컬 스토리지|대화 로그" docs/01_requirements/01_requirements.md`

**Dependencies:** Task 6

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** M

#### Task 8. 지도·일정 유형·축제 포함 여부 재적용

**Description:** 메인 소도시 지도, 국가·월·테마 필터, 마커 클릭 추천 진입, 공통 일정 유형, 추천 직전 축제·행사 포함 여부 확인을 반영한다.

**Acceptance criteria:**
- [x] `FR-MAP-005`~`FR-MAP-007`이 추가된다.
- [x] `FR-TRIP-001`이 공통 일정 유형으로 추가된다.
- [x] `FR-FEST-ENTRY-001`이 지도와 챗봇 진입점에 모두 연결된다.

**Verification:**
- [x] `rg -n "FR-MAP-005|FR-MAP-006|FR-MAP-007|FR-TRIP-001|FR-FEST-ENTRY-001|4박5일|축제.*포함" docs/01_requirements/01_requirements.md`

**Dependencies:** Task 6

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** M

#### Task 9. 날씨·숙소·일본어 키워드·우선순위 재적용

**Description:** 월별 기상 경향 기반 추천, WeatherAPI 표시 전용 정책, 숙소 검색 링크 정책, 일본어 검색 키워드 P2 편입, P2/P3 우선순위 조정을 반영한다.

**Acceptance criteria:**
- [x] `FR-WEATHER-*`, `FR-STAY-*`, `FR-JP-005`가 최신 기준으로 반영된다.
- [x] `FR-API-007`은 WeatherAPI 표시 전용으로 수정된다.
- [x] 4.6절의 P1~P5 표가 `14_priority_plan.md`와 일치한다.
- [x] K-Drama·애니메이션은 P3로 이동한다.

**Verification:**
- [x] `rg -n "FR-WEATHER|월별 기상 경향|FR-API-007|FR-STAY|FR-JP-005|FR-KDRAMA|FR-ANIME|P2|P3" docs/01_requirements/01_requirements.md docs/01_requirements/14_priority_plan.md`

**Dependencies:** Task 6

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `docs/01_requirements/14_priority_plan.md`

**Estimated scope:** M

### Phase 5. 공개 HTML 재동기화

#### Task 10. `pages/01_requirements.html` 재동기화

**Description:** 복구·재적용이 끝난 `docs/01_requirements/01_requirements.md`를 기준으로 `pages/01_requirements.html`을 동기화한다. HTML만의 오래된 문구나 오염 문구가 남지 않도록 원본과 비교한다.

**Acceptance criteria:**
- [x] 신규·수정 요구사항 ID가 HTML에 반영된다.
- [x] 원본에 없는 오염 문구가 HTML에 남지 않는다.
- [x] HTML은 기존 외부 CSS/JS 참조를 유지한다.

**Verification:**
- [x] `rg -n "FR-STORE|FR-ONBOARD|FR-MAP-005|FR-FEST-ENTRY|FR-PERS|FR-WEATHER|FR-TRIP|FR-STAY|FR-MY|FR-JP-005" pages/01_requirements.html`
- [x] `rg --pcre2 -n "<style|</style>|<script(?![^>]*\\bsrc=)" pages/01_requirements.html`
- [x] `rg -n "^```" pages/01_requirements.html`

**Dependencies:** Task 7, Task 8, Task 9

**Files likely touched:**
- `pages/01_requirements.html`

**Estimated scope:** M

### Phase 6. 검증과 정리

#### Task 11. 복구 후 문서 정합성 검증

**Description:** 원본 Markdown, 우선순위 문서, 공개 HTML이 같은 요구사항 집합과 같은 우선순위를 갖는지 확인한다.

**Acceptance criteria:**
- [x] `docs/01_requirements/01_requirements.md`와 `pages/01_requirements.html`의 핵심 ID가 일치한다.
- [x] `14_priority_plan.md`와 4.6절 우선순위가 일치한다.
- [x] 오염으로 판단한 문구가 재등장하지 않는다.

**Verification:**
- [x] `rg -n "FR-STORE|FR-ONBOARD|FR-MAP-005|FR-FEST-ENTRY|FR-PERS|FR-WEATHER|FR-TRIP|FR-STAY|FR-MY" docs pages`
- [x] `rg -n "실시간 예보.*추천|복수 소도시|FR-RANK-002|FR-REC-006" docs pages`
- [x] `git diff --check`

**Dependencies:** Task 10

**Files likely touched:** None

**Estimated scope:** S

#### Task 12. 백업 보존 정책 결정

**Description:** 백업 파일을 저장소에 남길지, 작업 완료 후 git 추적 대상에서 제외할지 결정한다. 백업 파일은 복구 추적용으로 유용하지만 장기 문서 산출물은 아니므로 커밋 여부를 별도로 판단한다.

**Acceptance criteria:**
- [x] 백업 파일을 커밋할지 제외할지 결정된다.
- [x] 커밋하지 않을 경우 `.gitignore` 또는 별도 안내로 백업 위치를 정리한다.
- [x] 최종 커밋 대상에는 원본 문서, HTML 산출물, 필요한 plan만 포함된다.

**Verification:**
- [x] `git status --short`
- [x] `git diff --stat`

**Dependencies:** Task 11

**Files likely touched:**
- Optional: `.gitignore`

**Estimated scope:** S

## 체크포인트

### Checkpoint 1. 복구 기준 확정

- [x] 현재 파일 백업 완료
- [x] 오염 발생 범위 확인
- [x] `<baseline>` 커밋 확정 (`aabd5f6`)

### Checkpoint 2. 파일 복구 완료

- [x] `01_requirements.md`가 `<baseline>` 상태로 복구됨
- [x] 백업본이 보존됨
- [x] 다른 파일이 불필요하게 변경되지 않음

### Checkpoint 3. 선별 재적용 완료

- [x] 최신 요구사항 변경사항만 재적용됨
- [x] 오염 문구가 재적용되지 않음
- [x] `14_priority_plan.md`와 4.6절이 정합성을 가짐

### Checkpoint 4. 공개 문서 동기화 완료

- [x] `pages/01_requirements.html` 동기화 완료
- [x] HTML 형식 검증 통과
- [x] `git diff --check` 통과

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 기준 커밋을 잘못 선택해 정상 변경까지 제거 | High | 최근 커밋별 diff를 먼저 검토하고 `<baseline>`을 명시한 뒤 파일 단위 복구 |
| 백업본 전체를 다시 덮어써 오염 재발 | High | 백업본은 참고용으로만 사용하고 요구사항 ID 단위로 선별 적용 |
| HTML만 최신화되어 원본과 불일치 | High | `docs/` 먼저 수정 후 `pages/01_requirements.html` 동기화 |
| 우선순위 문서와 요구사항 본문 불일치 | Medium | `14_priority_plan.md`와 4.6절을 같은 단계에서 검증 |
| 백업 파일이 불필요하게 커밋됨 | Low | 최종 `git status`에서 커밋 대상 결정 |

## 완료 기준

- [x] 현재 `01_requirements.md` 내용이 별도 백업되어 있다.
- [x] `docs/01_requirements/01_requirements.md`가 신뢰 가능한 이전 커밋 상태에서 출발해 필요한 변경만 다시 반영한다.
- [x] `pages/01_requirements.html`이 원본과 동기화된다.
- [x] 오염 문구가 `docs/`와 `pages/`에 남지 않는다.
- [x] `git diff --check`가 통과한다.
