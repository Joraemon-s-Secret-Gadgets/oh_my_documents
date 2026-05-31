---
작성자: Codex
상태: 진행후
---

# Implementation Plan: 07·08 요구사항 정의서 통합

## Overview
`docs/01_requirements/07_animation.md`와 `docs/01_requirements/08_japan_add_function.md`의 내용을 현재 요구사항 정의서에 반영한다. 기존 정책에 따라 별도 HTML 문서를 생성하지 않고, `01_requirements.html`의 서비스별 세부 기능, 기능 요구사항, 데이터 요구사항, API/외부 링크 요구사항에 통합한다.

## Source Documents
- `docs/01_requirements/07_animation.md`
  - 애니메이션 성지순례 대주제와 하위 테마
  - 작품·장소·도시·근거 URL·신뢰도 기반 RAG 데이터 필드
  - Anime Tourism 88, JNTO, KTO TourAPI, OSM, Wikidata, 지자체/공식 사이트 활용 방향
- `docs/01_requirements/08_japan_add_function.md`
  - 일본 소도시 특화 기능 `FR-JP-001`~`FR-JP-012`
  - 대도시 대체 추천, 접근성, 여행 스타일 프리셋, 계절 추천, 일본어 키워드, 숙박/맛집 딥링크, 교통패스, 혼잡 회피 근거, 경험 수준 분기, 일정 자동 생성
  - 일본 목적지 데이터 필드와 초기 후보 지역

## Target Integration
적용 대상은 다음 문서로 한정한다.

- Source: `docs/01_requirements/01_requirements.md`
- Generated: `pages/01_requirements.html`
- Hub: `index.html`
- Style, if needed: `assets/css/requirements.css`

`07_animation.md`, `08_japan_add_function.md`는 원천 기획 자료로 유지한다. 단, 공개 페이지에는 별도 `07_*.html`, `08_*.html`을 만들지 않는다.

## Architecture Decisions
- 현재 문서 구조는 `01_requirements` 하나에 세부 기능 요구사항을 통합하는 방식이므로 07·08도 같은 방식으로 반영한다.
- 07 애니메이션 성지순례는 신규 서비스 영역 `애니메이션 성지순례`로 추가하고 요구사항 ID는 `FR-ANIME-*`를 사용한다.
- 08 일본 기능 확장은 신규 서비스 영역 `Japan 소도시 확장`으로 추가하고 원문 ID인 `FR-JP-001`~`FR-JP-012`를 유지한다.
- 08 원문에 있는 DB 예시는 요구사항 정의서 톤에 맞게 `데이터 요구사항`의 "필요 데이터 항목"으로 변환한다. 저장 구조나 DB 스키마로 표현하지 않는다.
- 08 원문 MVP 제외 항목 중 `Open-Meteo`, `Naver Maps`, `Kakao Maps` 등 현재 문서 정책과 충돌하는 내용은 현재 기준에 맞춰 조정한다. 날씨는 `WeatherAPI` 기준을 유지한다.
- 출처 문서 링크 컬럼은 다시 만들지 않는다. 필요한 경우 비고에 "07 통합", "08 통합"처럼 짧게 표기한다.
- 기존 02~06 세부 기능 항목은 문서명이나 프로젝트명처럼 보이는 표현을 줄이고, 사용자가 이해할 수 있는 기능명 중심으로 재작성한다.

## Task List

### Phase 1: Source Analysis

## Task 1: Extract 07 animation pilgrimage requirements

**Description:** `07_animation.md`에서 기능 요구사항, 데이터 요구사항, 외부 데이터 소스, RAG 검증 기준을 분리한다.

**Acceptance criteria:**
- [x] 애니메이션 성지순례 하위 테마가 목록화된다.
- [x] 작품명, 장소명, 작품과의 관계, 근거 URL, 신뢰도 등 필요한 데이터 항목이 정리된다.
- [x] Anime Tourism 88, JNTO, KTO TourAPI, OSM, Wikidata, 공식 사이트의 역할이 구분된다.
- [x] 요구사항 후보 ID `FR-ANIME-*`가 중복 없이 정의된다.

**Verification:**
- [x] `rg -n "애니메이션|성지|Anime Tourism|Wikidata|신뢰도" docs\01_requirements\07_animation.md`

**Dependencies:** None

**Files likely touched:**
- None during audit

**Estimated scope:** Small

## Task 2: Extract 08 Japan feature requirements

**Description:** `08_japan_add_function.md`의 `FR-JP-001`~`FR-JP-012`를 현재 요구사항 분류에 맞게 기능, 데이터, 외부 링크/API, 비기능 관점으로 분류한다.

**Acceptance criteria:**
- [x] `FR-JP-001`~`FR-JP-012` 전체가 누락 없이 목록화된다.
- [x] 대도시 대체 추천, 접근성, 프리셋, 계절, 일본어 키워드, 딥링크, 교통패스, 혼잡 회피, 경험 수준, 일정 생성이 분류된다.
- [x] 일본 목적지 데이터 필드는 "필요 데이터 항목"으로 재표현된다.
- [x] 현재 문서와 충돌하는 지도/날씨 정책이 식별된다.

**Verification:**
- [x] `rg -n "FR-JP-00|FR-JP-01|Open-Meteo|Naver|Kakao|교통패스|딥링크" docs\01_requirements\08_japan_add_function.md`

**Dependencies:** None

**Files likely touched:**
- None during audit

**Estimated scope:** Small

### Checkpoint: Extraction Complete
- [x] 07·08에서 반영할 요구사항이 기능/데이터/API 기준으로 나뉜다.
- [x] 현재 `01_requirements`와 충돌하는 표현이 조정 대상에 올라간다.

### Phase 2: Requirements Integration

## Task 3: Update service detail scope list as feature names

**Description:** `4.6 서비스별 세부 기능`의 서비스 목록을 기능명 중심으로 정리하고, `애니메이션 성지순례`와 `Japan 소도시 확장`을 추가한다. 기존 02~06 항목도 문서명/프로젝트명보다 사용자가 실제로 받는 기능을 드러내는 이름으로 바꾼다.

**Acceptance criteria:**
- [x] 기존 `오버투어리즘 대응 여행 추천 서비스`는 `혼잡 회피 대체 여행지 추천`처럼 기능명 형태로 변경된다.
- [x] 기존 `한일 축제 여행 챗봇`은 `한일 축제 기반 여정 추천`처럼 기능명 형태로 변경된다.
- [x] 기존 `RailRoute-RAG`는 `철도 패스 기반 소도시 경로 추천`처럼 기능명 형태로 변경된다.
- [x] 기존 `StarryNight-RAG`는 `별 관측 조건 기반 여행지 추천`처럼 기능명 형태로 변경된다.
- [x] 기존 `K-drama 촬영지 데이터 파이프라인`은 `K-drama 촬영지 탐색·검증`처럼 기능명 형태로 변경된다.
- [x] `애니메이션 성지순례` 항목이 추가된다.
- [x] `Japan 소도시 확장` 항목은 `일본 소도시 맞춤 추천`처럼 기능명 형태로 추가된다.
- [x] 기존 02~06 통합 항목과 같은 표현 톤을 유지한다.

**Verification:**
- [x] `rg -n "혼잡 회피 대체 여행지 추천|한일 축제 기반 여정 추천|철도 패스 기반 소도시 경로 추천|별 관측 조건 기반 여행지 추천|K-drama 촬영지 탐색|애니메이션 성지순례|일본 소도시 맞춤 추천" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 1, Task 2

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Small

## Task 4: Add functional requirements for 07 and 08

**Description:** `4.6 서비스별 세부 기능` 요구사항 표에 `FR-ANIME-*`와 `FR-JP-*` 요구사항을 추가한다.

**Acceptance criteria:**
- [x] 애니메이션 성지순례 요구사항이 최소 3개 이상 추가된다.
- [x] `FR-JP-001`~`FR-JP-012`가 현재 문서 톤에 맞게 반영된다.
- [x] 요구사항 ID가 기존 `FR-*`와 중복되지 않는다.
- [x] 우선순위 컬럼을 추가하지 않는다.
- [x] 출처 문서 컬럼을 추가하지 않는다.

**Verification:**
- [x] `rg -n "FR-ANIME|FR-JP-001|FR-JP-012" docs\01_requirements\01_requirements.md`
- [x] 중복 ID 검증 스크립트 또는 수동 검토로 동일 `req-id`가 없는지 확인한다.

**Dependencies:** Task 3

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

## Task 5: Update data requirements

**Description:** 07·08에서 필요한 데이터 필드를 `7. 데이터 요구사항`에 추가한다. DB 구조가 아니라 서비스가 확보해야 하는 데이터 항목으로 표현한다.

**Acceptance criteria:**
- [x] 애니메이션 성지순례 데이터 항목이 추가된다.
- [x] 일본 소도시 목적지 데이터 항목이 추가된다.
- [x] 작품·장소 관계, 공식성, 신뢰도, 근거 URL, 방문 가능 여부가 포함된다.
- [x] 일본어 명칭, 지역권, 접근성, 교통패스, 검색 키워드, 딥링크, 혼잡 회피 근거가 포함된다.
- [x] 저장소, 테이블, 컬렉션, 인덱스 같은 DB 설계 표현을 사용하지 않는다.

**Verification:**
- [x] `rg -n "작품|성지|신뢰도|일본어 명칭|교통패스|검색 키워드|딥링크" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 1, Task 2

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

## Task 6: Update API and external data requirements

**Description:** 07·08에서 제안한 외부 데이터 소스와 딥링크를 현재 `5. API 연동 요구사항`과 `4.5 외부 데이터/API 연동`에 맞춰 반영한다.

**Acceptance criteria:**
- [x] Anime Tourism 88은 애니메이션 성지 seed 후보 수집 소스로 기록된다.
- [x] Wikidata, OSM, JNTO, KTO TourAPI, 지자체/공식 사이트의 역할이 정리된다.
- [x] 일본 숙박·맛집·카페 플랫폼은 직접 API가 아닌 딥링크/외부 링크 요구사항으로 표현된다.
- [x] 날씨 연동은 `WeatherAPI` 기준을 유지한다.
- [x] Naver Maps는 다시 추가하지 않는다.

**Verification:**
- [x] `rg -n "Anime Tourism 88|Wikidata|OSM|JNTO|KTO|WeatherAPI|Naver" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 4, Task 5

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

### Checkpoint: Requirements Updated
- [x] 기능 요구사항, 데이터 요구사항, API/외부 링크 요구사항이 서로 같은 방향을 가리킨다.
- [x] 07·08 원문 내용이 요구사항 정의서에 맞게 요약·통합된다.

### Phase 3: Hub and Generated HTML

## Task 7: Update document hub wording

**Description:** `index.html`의 세부 기능 요구사항 목록에 07·08 원천 문서가 `01 요구사항 정의서에 통합`되었음을 표시한다.

**Acceptance criteria:**
- [x] 기존 02~06 통합 표시와 같은 톤으로 07, 08 항목이 추가된다.
- [x] 별도 `pages/07_*.html`, `pages/08_*.html` 링크는 만들지 않는다.
- [x] 문서 허브가 현재 통합 정책과 일치한다.

**Verification:**
- [x] `rg -n "07|08|애니메이션|Japan|01 요구사항 정의서" index.html`

**Dependencies:** Task 4

**Files likely touched:**
- `index.html`

**Estimated scope:** Small

## Task 8: Regenerate public HTML

**Description:** 수정된 `docs/01_requirements/01_requirements.md`를 기준으로 `pages/01_requirements.html`을 재생성한다.

**Acceptance criteria:**
- [x] `pages/01_requirements.html`에 07·08 통합 내용이 반영된다.
- [x] generated page에 Markdown code fence가 남지 않는다.
- [x] CSS/JS asset 링크가 유지된다.

**Verification:**
- [x] `rg -n "^```" pages\01_requirements.html` returns no matches.
- [x] `rg -n "../assets/css/requirements.css|../assets/js/requirements.js" pages\01_requirements.html`

**Dependencies:** Task 4, Task 5, Task 6, Task 7

**Files likely touched:**
- `pages/01_requirements.html`

**Estimated scope:** Small

## Task 9: Validate consistency

**Description:** 요구사항 ID, 내부 링크, 삭제된 별도 HTML 링크, 금지된 지도/날씨 표현이 다시 생기지 않았는지 검증한다.

**Acceptance criteria:**
- [x] 요구사항 ID가 중복되지 않는다.
- [x] TOC의 모든 `href="#..."` 대상 id가 존재한다.
- [x] `pages/07_*.html`, `pages/08_*.html`이 생성되지 않는다.
- [x] Naver Maps가 다시 등장하지 않는다.
- [x] Open-Meteo가 WeatherAPI를 대체하지 않는다.
- [x] inline `<style>` 또는 inline `<script>`가 새로 생기지 않는다.

**Verification:**
- [x] Static id/href validation script confirms link targets exist.
- [x] `rg -n "Naver|Open-Meteo|07_.*\.html|08_.*\.html" docs\01_requirements\01_requirements.md pages index.html`
- [x] `rg --pcre2 -n '<style|</style>|<script(?![^>]*\bsrc=)' pages\01_requirements.html`

**Dependencies:** Task 8

**Files likely touched:**
- None unless fixes are needed

**Estimated scope:** Small

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| 08 원문의 기능이 많아 4.6 표가 비대해짐 | Medium | `FR-JP-*`는 핵심 문장으로 압축하고, 세부 설명은 데이터/API 요구사항으로 분산한다. |
| 07 애니메이션 성지 정보가 검증 없이 추천에 사용됨 | High | 공식 배경지, 작가 고향, 공식 콜라보, 팬 성지, 분위기 유사 등 관계 유형과 신뢰도를 필수 데이터로 둔다. |
| DB 설계 문서처럼 보일 수 있음 | Medium | `데이터 요구사항`은 필요한 데이터 항목과 품질 기준만 정의한다. |
| 기존 지도/날씨 정책과 충돌 | Medium | Naver Maps는 추가하지 않고, 날씨는 WeatherAPI로 유지한다. |
| 별도 HTML이 다시 생성됨 | Low | 07·08은 원천 Markdown만 유지하고 공개 HTML은 01 통합 방식으로 유지한다. |

## Definition of Done
- [x] `07_animation.md`의 애니메이션 성지순례 기능과 데이터 요구사항이 `01_requirements`에 통합된다.
- [x] `08_japan_add_function.md`의 `FR-JP-001`~`FR-JP-012`가 `01_requirements`에 통합된다.
- [x] `index.html`에서 07·08이 01 요구사항 정의서에 통합된 문서로 표시된다.
- [x] `pages/01_requirements.html`이 재생성된다.
- [x] 요구사항 ID, 내부 링크, 금지 표현, 별도 HTML 생성 여부가 검증된다.

