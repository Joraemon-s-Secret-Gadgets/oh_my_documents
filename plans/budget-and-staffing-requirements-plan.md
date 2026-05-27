# Implementation Plan: 예산안, 인력 분배 및 개발 기한 요구사항 정의

## Overview
로브(Lovv) 요구사항 정의서에 프로젝트 예산안, 인력 분배, 개발 기한 섹션을 추가한다. 이 계획은 개발 착수 전 필요한 비용 항목, 운영 비용, 외부 API 비용, 역할별 투입 인력, 단계별 인력 배치, 마일스톤과 일정 가정을 요구사항 문서에 명확히 반영하기 위한 작업 절차를 정리한다.

## Current Context
현재 요구사항 정의서는 다음 섹션으로 구성되어 있다.

| 섹션 | 내용 |
|---|---|
| 1. 문서 개요 | 목적, 범위, 용어 정의 |
| 2. 이해관계자 | 이해관계자, 역할 모델, 권한 매트릭스 |
| 3. 서비스 개요 | 서비스 소개, 가치 제안, 타겟 사용자, 서비스 흐름 |
| 4. 기능 요구사항 | 공통 UI, 추천, 지도, 챗봇, 외부 API, 세부 기능 |
| 5. API 연동 요구사항 | Google Maps, Kakao Maps, Yahoo Japan, WeatherAPI |
| 6. 비기능 요구사항 | 성능, 보안, 호환성 |
| 7. 데이터 요구사항 | 필요 데이터 항목, 데이터 품질 기준 |
| 8. 제약사항 및 가정 | 기술적 제약, 가정사항 |
| 9. 변경 이력 | 문서 변경 기록 |

예산 관련 내용은 기능 요구사항에서 사용자 조건 중 하나로만 언급되어 있으며, 프로젝트 수행 관점의 예산안, 인력 분배 기준, 개발 기한은 아직 없다.

## Target Document Structure
예산안, 인력 분배, 개발 기한은 요구사항 정의서의 실행 가능성을 설명하는 관리 관점 정보이므로 `8. 제약사항 및 가정` 뒤에 별도 섹션으로 추가한다.

| 변경 전 | 변경 후 |
|---|---|
| 8. 제약사항 및 가정 | 8. 제약사항 및 가정 |
| 9. 변경 이력 | 9. 예산안·인력 분배·개발 기한 |
|  | 10. 변경 이력 |

새 섹션은 다음 하위 항목으로 구성한다.

- `9.1 예산 산정 기준`
- `9.2 예산안`
- `9.3 인력 역할 정의`
- `9.4 단계별 인력 분배`
- `9.5 개발 기한 및 마일스톤`
- `9.6 예산·인력·일정 관리 원칙`

## Budget Draft Model

| 예산 구분 | 예산 | 포함 항목 | 요구사항 반영 방향 | 비고 |
|---|---:|---|---|---|
| 기획·PM | TBD | 요구사항 정리, 일정 관리, 이해관계자 조율 | 문서화 및 일정 관리 비용으로 분리 | 인건비 산정 필요 |
| UI/UX | TBD | 화면 설계, 사용자 흐름, 디자인 시스템 | 데모와 MVP 범위를 구분 | 인건비 산정 필요 |
| 프론트엔드 | TBD | 챗봇 UI, 지도, 결과 화면, 반응형 구현 | 사용자-facing 개발 비용으로 분리 | 인건비 산정 필요 |
| 백엔드/API | TBD | RAG 파이프라인, 외부 API 프록시, 인증/인가 | 서버 구현 및 API 연동 비용으로 분리 | 인건비 산정 필요 |
| 데이터 구축 | TBD | 소도시, 축제, 장소, 출처 데이터 정리 | 초기 구축과 정기 갱신 비용 구분 | 데이터 범위 확정 후 산정 |
| AI/LLM 사용 | 300,000원 | OpenAPI, LLM API, 임베딩, 벡터 검색 | 사용량 기반 변동비로 정의 | OpenAPI는 Runpod으로 대체될 수 있음 |
| 외부 API | TBD | Google Maps, Kakao Maps, WeatherAPI 등 | 무료 한도와 과금 전환 조건 명시 | 호출량 확정 후 산정 |
| 인프라 | 300,000원 | AWS 호스팅, DB, 스토리지, 모니터링 | MVP와 운영 전환 비용 분리 | AWS 예산 |
| QA/검증 | TBD | 기능 테스트, 접근 제어, 데이터 품질 검증 | 릴리스 전 필수 검증 비용으로 정의 | 인건비 산정 필요 |
| 운영·유지보수 | TBD | 장애 대응, 데이터 갱신, API Key 관리 | 월별 운영 비용으로 정의 | 운영 범위 확정 후 산정 |
| 확정 예산 합계 | 600,000원 | AWS, OpenAPI | 현재 확정된 사용 예산 합계 | OpenAPI는 Runpod으로 대체 가능 |

## Staffing Draft Model

| 역할 | 주요 책임 | MVP 기준 투입 |
|---|---|---|
| PM/기획 | 범위 관리, 요구사항 정리, 일정·리스크 관리 | 1명 |
| UI/UX 디자이너 | 사용자 흐름, 화면 설계, 디자인 가이드 | 1명 |
| 프론트엔드 개발자 | 챗봇 UI, 추천 결과, 지도/날씨 화면 구현 | 1~2명 |
| 백엔드 개발자 | API, 인증/인가, 외부 API 프록시, 운영 기능 | 1~2명 |
| AI/RAG 엔지니어 | 추천 파이프라인, RAG, 프롬프트, 평가 기준 | 1명 |
| 데이터 담당자 | 목적지·축제 데이터 수집, 정제, 출처 관리 | 1명 |
| QA 담당자 | 테스트 계획, 기능 검증, 권한·데이터 품질 검증 | 0.5~1명 |
| 운영 담당자 | 배포, 모니터링, API Key, 장애 대응 | 0.5~1명 |

## Timeline Draft Model

| 구분 | 단계 | 기간 | 주요 산출물 | 일정 의존성 |
|---|---|---|---|---|
| PoC | 기획 확정 | 2026-06-01 ~ 2026-06-07 | 요구사항 확정, 범위 동결, 예산·인력 기준 확정 | 이해관계자 합의 |
| PoC | UX/UI 설계 | 2026-06-08 ~ 2026-06-15 | 화면 흐름, 와이어프레임, 디자인 가이드 | 요구사항 확정 |
| PoC | 중간 보고 | 2026-06-16 | PoC 결과, 진행 현황, 예산 사용 계획, 일정 리스크, Production 범위 점검 | 기획·설계 초안 완료 |
| Production | 데이터 준비 | 2026-06-17 ~ 2026-06-24 | 초기 목적지·축제 데이터, 출처 목록, 검증 기준 | PoC 범위 승인, 데이터 제공처 접근 |
| Production | MVP 개발 | 2026-06-25 ~ 2026-07-10 | 챗봇 UI, 추천 결과, 지도·날씨 연동, RAG 초안 | 설계·데이터 초안 |
| Production | 통합 검증 | 2026-07-11 ~ 2026-07-17 | 기능 검증, 권한 검증, API Key 장애 폴백 검증 | MVP 기능 완료 |
| Production | 최종 정리 | 2026-07-18 ~ 2026-07-20 | 최종 문서, 발표 가능 산출물, 운영 체크리스트 | 검증 완료 |

## Architecture Decisions
- 예산안은 확정 견적이 아니라 요구사항 정의서 단계의 산정 기준과 항목 정의로 작성한다.
- 현재 확정된 예산은 AWS 300,000원, OpenAPI 300,000원이며, 그 외 항목은 `TBD` 또는 범위형 추정으로 둘 수 있다.
- 인력 분배는 직무별 책임과 단계별 투입 강도를 중심으로 작성하고, 개인 이름은 기재하지 않는다.
- 개발 기간은 2026-06-01부터 2026-07-20까지로 정의하고, 2026-06-16 중간 보고까지를 PoC, 2026-06-17부터 2026-07-20까지를 Production으로 구분한다.
- 일정은 날짜 단위 범위로 표현하고, 요구사항 확정일과 API Key 확보일 같은 선행 조건을 함께 명시한다.
- MVP와 운영 전환 단계를 구분해 초기 개발비와 월 운영비가 섞이지 않도록 한다.
- 외부 API, LLM, 인프라 비용은 사용량 기반 변동비로 명시해 고정 개발 인건비와 분리한다.
- `docs/01_requirements/01_requirements.md`를 원본으로 수정하고, `pages/01_requirements.html`은 동일 내용을 반영한 공유용 산출물로 맞춘다.

## Task List

### Phase 1: 범위 및 기준 정의

## Task 1: 예산·인력·기한 섹션 위치와 목차 확정

**Description:** 요구사항 정의서에서 예산안, 인력 분배, 개발 기한 섹션을 어디에 배치할지 확정하고, 목차와 섹션 번호 변경 범위를 정리한다.

**Acceptance criteria:**
- [x] 새 섹션 위치가 `8. 제약사항 및 가정` 뒤로 정의된다.
- [x] 기존 `9. 변경 이력`은 `10. 변경 이력`로 변경된다.
- [x] 사이드바 목차에 `9. 예산안·인력 분배·개발 기한` 하위 링크가 추가된다.
- [x] 원본 문서와 공유용 HTML의 섹션 번호가 일치한다.

**Verification:**
- [x] `rg -n "9. 예산안|개발 기한|10. 변경 이력|s9-|s10" docs\01_requirements\01_requirements.md pages\01_requirements.html`

**Dependencies:** None

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Small

## Task 2: 예산 산정 기준 정의

**Description:** 예산안이 어떤 가정과 범위에서 산정되는지 문서화한다. MVP, 운영 전환, 사용량 기반 비용을 구분해 이후 금액 산정의 기준을 만든다.

**Acceptance criteria:**
- [x] MVP 개발비와 월 운영비가 구분된다.
- [x] 확정 예산으로 AWS 300,000원, OpenAPI 300,000원이 명시된다.
- [x] OpenAPI 예산은 Runpod으로 대체될 수 있다는 비고가 포함된다.
- [x] 외부 API, LLM, 인프라 비용은 사용량 기반 변동비로 명시된다.
- [x] 금액이 미정인 항목은 `TBD` 또는 범위형 추정으로 둘 수 있다는 원칙이 명시된다.

**Verification:**
- [x] 예산 산정 기준 표에 고정비, 변동비, 운영비 구분이 포함되어 있는지 확인한다.

**Dependencies:** Task 1

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Small

### Phase 2: 예산안 작성

## Task 3: 예산 항목 표 작성

**Description:** 기획, 디자인, 개발, 데이터, AI/LLM, 외부 API, 인프라, QA, 운영 비용을 표로 정리한다.

**Acceptance criteria:**
- [x] 예산 항목별 포함 범위가 명시된다.
- [x] 각 항목이 초기 구축비 또는 월 운영비 중 어디에 속하는지 구분된다.
- [x] 외부 API와 LLM 비용은 별도 항목으로 분리된다.
- [x] 비용 산정이 어려운 항목은 산정 근거 또는 확인 필요 조건이 함께 적힌다.

**Verification:**
- [x] `rg -n "기획|UI/UX|프론트엔드|백엔드|LLM|외부 API|인프라|QA|운영" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 2

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Medium

## Task 4: 예산 리스크와 관리 원칙 추가

**Description:** API 과금, LLM 토큰 사용량, 데이터 갱신 비용, 운영 인프라 확장 등 예산 초과 가능성이 있는 항목과 관리 원칙을 정리한다.

**Acceptance criteria:**
- [x] 외부 API 무료 한도 초과와 과금 전환 리스크가 명시된다.
- [x] LLM/임베딩 호출량 증가 리스크가 명시된다.
- [x] 데이터 수집·검증·갱신 비용이 반복 운영 비용으로 분리된다.
- [x] 월별 사용량 모니터링과 비용 상한 관리 원칙이 포함된다.

**Verification:**
- [x] 예산 리스크 표에 영향도와 대응 방안이 포함되어 있는지 확인한다.

**Dependencies:** Task 3

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Small

### Checkpoint: 예산안 초안 완료
- [x] 예산 산정 기준, 예산 항목, 예산 리스크가 한 섹션 안에서 연결된다.
- [x] 금액 미정 항목이 확정 금액처럼 보이지 않는다.
- [x] 기존 API 연동 요구사항의 과금·키 관리 내용과 충돌하지 않는다.

### Phase 3: 인력 분배 작성

## Task 5: 역할별 인력 책임 정의

**Description:** 프로젝트 수행에 필요한 역할과 각 역할의 주요 책임을 정의한다.

**Acceptance criteria:**
- [x] PM/기획, UI/UX, 프론트엔드, 백엔드, AI/RAG, 데이터, QA, 운영 역할이 포함된다.
- [x] 각 역할의 책임이 요구사항 정의서의 기능·데이터·운영 범위와 연결된다.
- [x] 역할은 개인 이름이 아닌 직무 기준으로 작성된다.

**Verification:**
- [x] 역할별 책임 표에 주요 산출물 또는 담당 범위가 포함되어 있는지 확인한다.

**Dependencies:** Task 1

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Small

## Task 6: 단계별 인력 분배 표 작성

**Description:** 기획, MVP 개발, 검증, 운영 전환 단계별로 어떤 역할이 얼마나 투입되는지 정리한다.

**Acceptance criteria:**
- [x] 단계는 최소 `기획`, `MVP 개발`, `검증`, `운영 전환`으로 구분된다.
- [x] 각 단계별 핵심 투입 역할과 보조 투입 역할이 구분된다.
- [x] 인력 규모는 확정 인원 대신 `1명`, `1~2명`, `0.5~1명`처럼 추정 범위로 표현된다.
- [x] 인력 투입이 예산 항목과 연결된다는 설명이 포함된다.

**Verification:**
- [x] 단계별 표에 모든 역할이 최소 한 번 이상 등장하는지 확인한다.

**Dependencies:** Task 5

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Medium

## Task 7: 역할·권한 모델과 인력 역할의 혼동 방지

**Description:** `2. 이해관계자`의 서비스 Role ID와 `9. 예산안·인력 분배·개발 기한`의 프로젝트 수행 역할이 서로 다른 개념임을 명시한다.

**Acceptance criteria:**
- [x] `R-USER`, `R-LOCAL-OPERATOR` 등 서비스 권한 역할과 PM/개발자 등 수행 인력 역할이 구분된다.
- [x] 관광 운영자, 서비스 관리자 같은 서비스 사용자와 개발팀 역할이 혼동되지 않도록 설명이 포함된다.
- [x] 후속 사용자 시나리오나 API 명세에서 사용할 Role ID는 기존 역할 모델을 따른다는 문장이 포함된다.

**Verification:**
- [x] `rg -n "서비스 권한 역할|수행 인력|Role ID|PM" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 5

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Small

### Checkpoint: 인력 분배 초안 완료
- [x] 역할별 책임과 단계별 투입이 서로 일관된다.
- [x] 서비스 권한 Role과 프로젝트 수행 역할이 구분된다.
- [x] 예산 항목과 인력 항목이 서로 추적 가능하다.

### Phase 4: 개발 기한 작성

## Task 8: 개발 단계와 마일스톤 정의

**Description:** 프로젝트 개발 기한을 요구사항 확정, 설계, 데이터 준비, MVP 개발, 통합 검증, 베타 운영 준비 단계로 나누고 각 단계별 권장 기간과 산출물을 정리한다.

**Acceptance criteria:**
- [x] 개발 기한은 단일 마감일이 아니라 단계별 기간과 마일스톤으로 표현된다.
- [x] 전체 개발 기간은 2026-06-01부터 2026-07-20까지로 명시된다.
- [x] 2026-06-16 중간 보고까지는 PoC로 명시된다.
- [x] 2026-06-17부터 2026-07-20까지는 Production으로 명시된다.
- [x] 각 단계의 주요 산출물과 완료 조건이 명시된다.
- [x] 요구사항 확정일, API Key 확보, 초기 데이터 확보 같은 일정 의존성이 함께 적힌다.
- [x] 전체 개발 기간과 중간 보고 일정이 요약된다.

**Verification:**
- [x] `rg -n "기획 확정|UX/UI 설계|데이터 준비|MVP 개발|통합 검증|베타 운영 준비|마일스톤" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 2, Task 5, Task 6

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Medium

## Task 9: 일정 리스크와 조정 원칙 추가

**Description:** 외부 API 승인 지연, 데이터 확보 지연, 추천 품질 검증 지연, 인력 공백 등 개발 기한에 영향을 줄 수 있는 리스크와 일정 조정 원칙을 정리한다.

**Acceptance criteria:**
- [x] 외부 API Key 승인·도메인 등록 지연 리스크가 명시된다.
- [x] 초기 데이터 수집·검증 지연 리스크가 명시된다.
- [x] RAG 추천 품질 검증 반복으로 인한 일정 변동 가능성이 명시된다.
- [x] 일정 초과 시 MVP 범위 조정, 기능 후순위화, 단계적 출시 원칙이 포함된다.

**Verification:**
- [x] 일정 리스크 표에 영향도와 대응 방안이 포함되어 있는지 확인한다.

**Dependencies:** Task 8

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`

**Estimated scope:** Small

### Checkpoint: 개발 기한 초안 완료
- [x] 단계별 개발 기한과 마일스톤이 PoC/Production 구분 및 예산·인력 분배와 연결된다.
- [x] 일정은 확정 계약일처럼 보이지 않고 요구사항 단계의 기준 일정으로 표현된다.
- [x] 주요 일정 의존성과 리스크가 문서에 남는다.

### Phase 5: 문서 반영 및 검증

## Task 10: 원본 요구사항 정의서에 섹션 추가

**Description:** `docs/01_requirements/01_requirements.md`에 예산안, 인력 분배, 개발 기한 섹션을 추가하고 기존 변경 이력 번호를 조정한다.

**Acceptance criteria:**
- [x] `9. 예산안·인력 분배·개발 기한` 섹션이 추가된다.
- [x] `9.1`~`9.6` 하위 섹션이 모두 포함된다.
- [x] 기존 변경 이력은 `10. 변경 이력`로 변경된다.
- [x] 문서 톤이 기존 요구사항 정의서와 일치한다.

**Verification:**
- [x] `rg -n "9\\.1 예산 산정 기준|9\\.2 예산안|9\\.3 인력 역할 정의|9\\.4 단계별 인력 분배|9\\.5 개발 기한 및 마일스톤|9\\.6 예산·인력·일정 관리 원칙|10\\. 변경 이력" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Medium

## Task 11: 공유용 HTML 산출물 동기화

**Description:** `pages/01_requirements.html`에 원본 요구사항 정의서와 같은 예산안, 인력 분배, 개발 기한 내용을 반영한다.

**Acceptance criteria:**
- [x] 원본 문서와 공유용 HTML의 목차, 앵커, 섹션 제목이 일치한다.
- [x] 예산안, 인력 분배, 개발 기한 표가 HTML에서 깨지지 않는다.
- [x] 변경 이력 번호가 원본과 동일하게 `10`으로 표시된다.

**Verification:**
- [x] `rg -n "9\\. 예산안|개발 기한|10\\. 변경 이력|budget|staff|timeline" pages\01_requirements.html`

**Dependencies:** Task 10

**Files likely touched:**
- `pages/01_requirements.html`

**Estimated scope:** Medium

## Task 12: 변경 이력 및 계획 완료 상태 갱신

**Description:** 요구사항 정의서의 변경 이력에 예산안, 인력 분배, 개발 기한 섹션 추가 내역을 기록하고, 본 플랜의 체크리스트를 완료 상태로 갱신한다.

**Acceptance criteria:**
- [x] 변경 이력에 예산안, 인력 분배, 개발 기한 추가 내역이 기록된다.
- [x] 본 플랜의 완료된 작업은 `[x]`로 표시된다.
- [x] 미확정 금액, 인력 규모, 개발 기간 가정이 있으면 Open Questions에 남긴다.

**Verification:**
- [x] `git diff --check`
- [x] `rg -n "\\[ \\]|예산안|인력 분배|개발 기한" plans\budget-and-staffing-requirements-plan.md docs\01_requirements\01_requirements.md pages\01_requirements.html`

**Dependencies:** Task 10, Task 11

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`
- `plans/budget-and-staffing-requirements-plan.md`

**Estimated scope:** Small

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 예산안이 확정 견적으로 오해됨 | High | 요구사항 단계의 산정 기준과 추정 항목임을 명시하고 금액은 TBD 또는 범위형으로 표현한다. |
| 외부 API와 LLM 비용이 누락됨 | High | 사용량 기반 변동비 항목을 별도 예산 구분으로 둔다. |
| 개발 인력 역할과 서비스 권한 Role이 혼동됨 | Medium | 섹션 내에서 프로젝트 수행 역할과 서비스 사용자 Role ID를 명확히 구분한다. |
| 개발 기한이 확정 납기처럼 오해됨 | High | 요구사항 단계의 기준 일정이며 선행 조건에 따라 조정될 수 있음을 명시한다. |
| PoC 산출물이 Production 완성 범위로 오해됨 | Medium | 2026-06-16 중간 보고까지는 검증 중심 PoC, 이후는 Production 구현·검증 단계로 구분한다. |
| 외부 API 승인 또는 데이터 확보 지연으로 일정이 밀림 | Medium | 일정 의존성을 별도 컬럼으로 두고, MVP 범위 조정 원칙을 함께 적는다. |
| 초기 구축비와 월 운영비가 섞임 | Medium | 예산 표에 비용 유형 컬럼을 둔다. |
| 산정 근거 없이 금액만 나열됨 | Medium | 각 항목에 포함 범위와 산정 기준 또는 확인 필요 조건을 함께 작성한다. |
| 기존 변경 이력 앵커가 깨짐 | Low | 목차, 섹션 ID, 변경 이력 번호를 원본과 HTML에서 함께 검증한다. |

## Open Questions

- MVP 완료 기준을 내부 데모, 베타 배포, 또는 발표 가능 산출물 중 무엇으로 볼지 결정이 필요하다.
- PoC 중간 보고에서 Production 진행 여부를 승인하는 기준을 정해야 한다.
- 인력 규모를 최소팀 기준으로 쓸지, 권장팀 기준으로 쓸지 결정이 필요하다.
- LLM/API/인프라 비용 산정에 사용할 월간 사용자 수 또는 호출량 가정이 필요하다.
- 예산안 단위를 원화(KRW)로 고정할지, API 비용을 고려해 USD 병기를 허용할지 결정이 필요하다.

## Definition of Done

- [x] 요구사항 정의서에 예산안, 인력 분배, 개발 기한 섹션이 추가된다.
- [x] 예산 산정 기준, 예산 항목, 예산 리스크가 정리된다.
- [x] 역할별 책임과 단계별 인력 분배가 정리된다.
- [x] PoC/Production 기준의 단계별 개발 기한, 마일스톤, 일정 리스크가 정리된다.
- [x] 서비스 권한 Role과 프로젝트 수행 역할의 차이가 명시된다.
- [x] 원본 문서와 공유용 HTML 산출물이 일치한다.
- [x] 변경 이력과 본 플랜 완료 상태가 갱신된다.
