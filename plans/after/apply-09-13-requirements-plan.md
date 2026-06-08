---
작성자: llm팀
상태: 진행후
---

# Implementation Plan: 09-13 요구사항 정의서 통합

## Overview
`docs/01_requirements/09_craft_experience.md`부터 `13_weather_first.md`까지의 신규 테마와 챗봇 진입점 기능을 현재 요구사항 정의서와 공개 HTML에 반영한다. 기존 `pages/01_requirements.html`에는 02-08 문서의 핵심 항목은 대체로 통합되어 있으나, 공예·웰니스·사계절 액티비티 테마와 예산 역산·날씨 기반 추천 진입점은 아직 반영되지 않았다.

## Current Gap Summary

| Source | 현재 HTML 반영 상태 | 반영 필요 내용 |
|---|---|---|
| `09_craft_experience.md` | 미반영 | 공예·장인 체험 테마, 우천 적합 실내 체험, 소요 시간·난이도·예약·완성품 수령 방식 |
| `10_healing_wellness.md` | 미반영 | 치유·웰니스 테마, 온천·숲 치유·템플스테이·명상, 한적함·저자극 기준 |
| `11_seasonal_activity.md` | 미반영 | 사계절 액티비티 테마, 스키·서핑·트레킹 등 계절 직접 연동형 추천 |
| `12_budget_first.md` | 일부만 간접 반영 | `budget-first` 챗봇 진입점, 예산·기간·인원 파싱, 비용 내역과 초과/조정 안내 |
| `13_weather_first.md` | 일부만 간접 반영 | `weather-first` 챗봇 진입점, 예보 비교 기반 역추천, 날씨 기준 시각과 우천 대안 |

## Target Integration

- Source: `docs/01_requirements/01_requirements.md`
- Generated/public page: `pages/01_requirements.html`
- Optional hub update: `index.html`, 현재 문서 허브가 09-13 원천 문서를 별도로 노출해야 하는 경우만 수정
- Optional styles: `assets/css/requirements.css`, 기존 표/카드 레이아웃으로 수용이 어려운 경우만 수정

별도 `09_*.html`~`13_*.html`은 만들지 않고, 기존 정책처럼 `01_requirements.html`에 통합한다.

## Architecture Decisions

- 09-11은 신규 "테마"로 통합하고, 기존 6개 테마 표현은 "기본 테마 + 확장 테마" 구조로 조정한다.
- 12-13은 테마가 아니라 챗봇 직접 질의 기반 "추천 진입점"으로 분리한다.
- 기능 요구사항 ID는 중복을 피하기 위해 `FR-THEME-CRAFT-*`, `FR-THEME-WELLNESS-*`, `FR-THEME-ACTIVITY-*`, `FR-ENTRY-BUDGET-*`, `FR-ENTRY-WEATHER-*` 형식으로 둔다.
- 12 예산 기능은 프로젝트 예산안 섹션과 혼동되지 않도록 "사용자 여행 예산"이라고 명확히 표현한다.
- 13 날씨 기능은 기존 WeatherAPI 표시 기능을 "추천 변수"로 승격하는 내용으로 정리하되, API 공급자는 현재 문서의 WeatherAPI 기준을 유지한다.
- 신규 테마의 DB 관련 내용은 저장 스키마가 아니라 `7. 데이터 요구사항`의 필요 데이터 항목으로 표현한다.

## Task List

### Phase 1: 범위 확정

## Task 1: 09-13 원천 문서 요구사항 추출

**Description:** 09-13 문서에서 기능, 사용자 시나리오, 추천 결과 포함 항목, 데이터 요구사항, 기존 구조 반영 방식을 분리한다.

**Acceptance criteria:**
- [x] 공예, 웰니스, 사계절 액티비티가 신규 테마로 분류된다.
- [x] 예산 역산, 날씨 기반 추천이 테마가 아닌 챗봇 진입점으로 분류된다.
- [x] 각 문서의 추천 시 포함 항목이 기능/데이터 요구사항 후보로 정리된다.

**Verification:**
- [x] `rg -n "공예|웰니스|액티비티|budget-first|weather-first" docs\01_requirements`

**Dependencies:** None

**Files likely touched:**
- None during audit

**Estimated scope:** Small

## Task 2: 기존 반영 범위 재검증

**Description:** `pages/01_requirements.html`에 02-08은 이미 반영되어 있고 09-13이 누락된 상태인지 최종 확인한다.

**Acceptance criteria:**
- [x] 오버투어리즘, 축제, 철도, 별 관측, K-drama, 애니메이션, 일본 소도시 맞춤 추천은 HTML에 존재한다.
- [x] 공예, 웰니스, 액티비티, `budget-first`, `weather-first`는 HTML에 없거나 기능 요구사항으로 충분히 표현되지 않았음이 확인된다.

**Verification:**
- [x] `rg -n "공예|웰니스|액티비티|budget-first|weather-first" pages\01_requirements.html`
- [x] `rg -n "오버투어리즘|축제|철도|별 관측|K-drama|애니메이션|일본 소도시" pages\01_requirements.html`

**Dependencies:** Task 1

**Files likely touched:**
- None during audit

**Estimated scope:** Small

### Phase 2: 요구사항 정의서 통합

## Task 3: 문서 범위와 서비스 개요 갱신

**Description:** `1.2 범위`, `3.1 서비스 소개`, `3.2 핵심 가치 제안`, `3.4 서비스 흐름 요약`에 확장 테마와 직접 질의 진입점을 반영한다.

**Acceptance criteria:**
- [x] 기존 "6개 테마" 표현이 신규 테마 확장을 수용하는 표현으로 바뀐다.
- [x] 공예·웰니스·액티비티가 테마 기반 여정 추천 범위에 포함된다.
- [x] 예산·날씨 직접 질의가 챗봇 추천 시작 방식으로 추가된다.

**Verification:**
- [x] `rg -n "확장 테마|공예|웰니스|액티비티|예산|날씨" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 1

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

## Task 4: 기능 요구사항 추가

**Description:** `4.2 추천·탐색 기능`, `4.4 RAG·챗봇·에이전트 기능`, `4.6 서비스별 세부 기능`에 09-13의 기능 요구사항을 추가한다.

**Acceptance criteria:**
- [x] 공예 테마는 체험 종류, 소요 시간, 난이도, 예약, 완성품 수령, 우천 적합성을 포함한다.
- [x] 웰니스 테마는 온천, 숲 치유, 템플스테이, 명상, 한적함·저자극 기준을 포함한다.
- [x] 액티비티 테마는 계절별 액티비티, 강습·장비 대여, 난이도, 적합 동행 유형을 포함한다.
- [x] `budget-first`는 예산·기간·인원 파싱, 비용 내역, 예산 초과 표시, 숙박 수준별 대안을 포함한다.
- [x] `weather-first`는 날씨·시기 파싱, 예보 비교, 기준 시각 표시, 우천 시 실내 체험형 대안을 포함한다.

**Verification:**
- [x] `rg -n "FR-THEME-CRAFT|FR-THEME-WELLNESS|FR-THEME-ACTIVITY|FR-ENTRY-BUDGET|FR-ENTRY-WEATHER" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 3

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

## Task 5: 데이터 요구사항 추가

**Description:** `7. 데이터 요구사항`에 신규 테마와 진입점 기능이 필요로 하는 데이터 항목을 추가한다.

**Acceptance criteria:**
- [x] 공예 데이터에는 공예 종류, 체험 시간, 난이도, 예약 필요 여부, 배송/수령 방식, 우천 적합성이 포함된다.
- [x] 웰니스 데이터에는 회복 활동 유형, 한적함, 운영 정보, 참여 방법, 적합 동행 유형이 포함된다.
- [x] 액티비티 데이터에는 계절별 액티비티 태그, 기상 조건, 난이도, 강습, 장비 대여가 포함된다.
- [x] 예산 데이터에는 교통비, 숙박비, 식비, 액티비티 비용 추정치와 기간·인원 기준이 포함된다.
- [x] 날씨 데이터에는 예보, 강수 확률, 기온, 풍속, 기준 시각, 우천 대안 연결 정보가 포함된다.

**Verification:**
- [x] `rg -n "체험 시간|완성품|저자극|강습|장비 대여|비용 내역|기준 시각" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 4

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

## Task 6: API·외부 데이터 요구사항 보강

**Description:** 예산 추정과 날씨 역추천에 필요한 외부 데이터/API 처리 기준을 `4.5`와 `5. API 연동 요구사항`에 맞춰 보강한다.

**Acceptance criteria:**
- [x] WeatherAPI는 단순 표시뿐 아니라 추천 후보 비교에 사용된다고 명시된다.
- [x] 날씨 데이터 기준 시각과 갱신 실패 시 안내 기준이 포함된다.
- [x] 예산 추정에 쓰는 교통·숙박·체험 비용 데이터는 출처와 갱신 시점 관리 대상이 된다.
- [x] 우천 시 공예 같은 실내 체험형 대안을 연결하는 규칙이 반영된다.

**Verification:**
- [x] `rg -n "WeatherAPI|예보 비교|기준 시각|비용 추정|실내 체험" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 5

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Small

### Checkpoint: 요구사항 원본 통합
- [x] `docs/01_requirements/01_requirements.md`에 09-13의 기능, 데이터, API 관점이 모두 반영된다.
- [x] 12의 사용자 여행 예산과 9장의 프로젝트 예산안이 문맥상 혼동되지 않는다.
- [x] 13의 날씨 기능이 기존 WeatherAPI 정책과 충돌하지 않는다.

### Phase 3: 공개 HTML 동기화

## Task 7: `pages/01_requirements.html` 재생성 또는 수동 동기화

**Description:** 갱신된 원본 요구사항 정의서와 동일한 내용이 공개 HTML에 반영되도록 동기화한다.

**Acceptance criteria:**
- [x] HTML 목차와 본문에 신규 테마/진입점 요구사항이 표시된다.
- [x] 기존 CSS/JS 링크가 유지된다.
- [x] Markdown code fence나 깨진 표 구조가 HTML에 남지 않는다.

**Verification:**
- [x] `rg -n "공예|웰니스|액티비티|budget-first|weather-first|예산 역산|날씨 기반" pages\01_requirements.html`
- [x] `rg -n "^```" pages\01_requirements.html` returns no matches.

**Dependencies:** Task 3, Task 4, Task 5, Task 6

**Files likely touched:**
- `pages/01_requirements.html`

**Estimated scope:** Medium

## Task 8: 문서 허브 필요 여부 확인 및 반영

**Description:** `index.html`이 원천 문서 통합 상태를 표시하는 구조라면 09-13 항목도 01 요구사항 정의서에 통합된 문서로 표시한다.

**Acceptance criteria:**
- [x] 허브에 09-13 원천 문서가 있다면 `01 요구사항 정의서에 통합` 상태와 일치한다.
- [x] 별도 `pages/09_*.html`~`pages/13_*.html` 링크는 추가하지 않는다.

**Verification:**
- [x] `rg -n "09|10|11|12|13|공예|웰니스|액티비티|예산 역산|날씨 기반" index.html`

**Dependencies:** Task 7

**Files likely touched:**
- `index.html`

**Estimated scope:** Small

## Task 9: 최종 일관성 검증

**Description:** 요구사항 ID, 내부 앵커, 용어, 누락 여부를 검증한다.

**Acceptance criteria:**
- [x] 신규 요구사항 ID가 중복되지 않는다.
- [x] HTML 목차의 `href="#..."` 대상 id가 모두 존재한다.
- [x] "6개 테마"처럼 신규 테마와 충돌하는 표현이 남지 않거나 문맥상 "초기 6개"로 정리된다.
- [x] `budget-first`는 프로젝트 예산안이 아니라 사용자 여행 예산 기능으로 표현된다.
- [x] `weather-first`는 WeatherAPI 정책과 일관된다.

**Verification:**
- [x] `rg -n "6개 테마|budget-first|weather-first|WeatherAPI" docs\01_requirements\01_requirements.md pages\01_requirements.html`
- [x] 기존 HTML 검증 스크립트 또는 수동 검사로 내부 링크 확인
- [x] `git diff --check`

**Dependencies:** Task 8

**Files likely touched:**
- None unless fixes are needed

**Estimated scope:** Small

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 09-11을 기존 6개 테마와 합치며 테마 수 표현이 불일치함 | Medium | "초기 6개 테마 + 확장 테마" 또는 "테마 기반"으로 표현을 조정한다. |
| `budget-first`가 9장 프로젝트 예산안과 혼동됨 | Medium | 기능 요구사항에서는 "사용자 여행 예산"과 "여정 비용"이라는 표현을 사용한다. |
| 날씨 기능이 기존 단순 날씨 표시 요구사항과 중복됨 | Medium | 기존 WeatherAPI 표시 기능을 재사용하되, 추천 후보 비교와 기준 시각 표시를 신규 요구사항으로 분리한다. |
| 비용 추정 데이터의 정확도가 과도하게 보장되는 것처럼 보임 | Medium | "대략적 비용", "추정치", "출처/갱신 시점"을 함께 명시한다. |
| 4.6 서비스별 세부 기능 표가 과도하게 길어짐 | Low | 상세 유저 스토리는 요약하고, 반복 항목은 데이터 요구사항으로 분산한다. |

## Definition of Done

- [x] 09-11 신규 테마가 요구사항 정의서와 HTML에 반영된다.
- [x] 12-13 챗봇 직접 질의 진입점이 기능 요구사항으로 반영된다.
- [x] 신규 테마/진입점에 필요한 데이터 요구사항이 추가된다.
- [x] WeatherAPI와 비용 추정 데이터의 활용 기준이 API/외부 데이터 요구사항에 반영된다.
- [x] `pages/01_requirements.html`이 원본 요구사항 정의서와 동기화된다.
- [x] 별도 09-13 HTML을 만들지 않고 01 통합 정책을 유지한다.
