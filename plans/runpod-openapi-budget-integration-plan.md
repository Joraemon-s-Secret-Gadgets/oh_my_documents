# Implementation Plan: 인프라·AI 달러 예산 분리 반영

## Overview
요구사항 정의서의 예산안을 최종 정책에 맞게 정리한다. 인프라 예산은 `300,000원`으로 유지하고, AI 실행과 LLM/API 사용은 각각 달러 예산으로 분리한다. Runpod은 AI 실행 예산 `$300`, OpenAPI는 LLM/API 사용 예산 `$300`으로 표시하며, 확정 예산 합계는 `300,000원 + $600`으로 통화별 합계를 보여준다.

## Implementation Result

| 항목 | 반영 결과 |
|---|---|
| 문서 버전 | `v1.4.2 — 인프라·AI 달러 예산 분리` |
| 인프라 예산 | `300,000원` |
| AI 실행 예산 | `AI 실행 (Runpod)` `$300` |
| LLM/API 예산 | `LLM/API 사용 (OpenAPI)` `$300` |
| 달러 예산 합계 | `$600` |
| 확정 예산 합계 | `300,000원 + $600` |
| 관리 원칙 | AWS 인프라, Runpod AI 실행, OpenAPI LLM/API, 외부 API 호출량을 분리 관리 |
| 변경 이력 | v1.4.2에 인프라 예산 복원과 달러 예산 분리 내역 추가 |

## Files Updated

- `docs/01_requirements/01_requirements.md`
- `pages/01_requirements.html`
- `index.html`
- `plans/runpod-openapi-budget-integration-plan.md`

## Architecture Decisions

- Runpod과 OpenAPI는 대체 관계가 아니라 서로 다른 달러 예산 항목으로 표현한다.
- Runpod은 GPU 실행, 모델 서빙, 배치 작업을 담당하는 `AI 실행` 예산으로 둔다.
- OpenAPI는 LLM API, 임베딩, 벡터 검색을 담당하는 `LLM/API 사용` 예산으로 둔다.
- 인프라 예산은 AWS 호스팅, DB, 스토리지, 모니터링 비용으로 `300,000원`을 유지한다.
- 원화와 달러를 환율 없이 합산하지 않고 `300,000원 + $600`으로 병기한다.

## Task List

### Phase 1: 요구사항 원본 반영

## Task 1: 예산안 표를 분리형 구조로 수정

**Description:** `9.2 예산안`의 AI 관련 항목을 Runpod과 OpenAPI로 분리하고, 인프라 예산을 `300,000원`으로 복원한다.

**Acceptance criteria:**
- [x] `AI 실행 (Runpod)` 항목이 `$300`으로 표시된다.
- [x] `LLM/API 사용 (OpenAPI)` 항목이 `$300`으로 표시된다.
- [x] `인프라` 항목이 `300,000원`으로 표시된다.
- [x] `확정 예산 합계`가 `300,000원 + $600`으로 표시된다.

**Verification:**
- [x] `rg -n "AI 실행 \\(Runpod\\)|LLM/API 사용 \\(OpenAPI\\)|300,000원 \\+ \\$600|확정 예산 합계" docs\01_requirements\01_requirements.md`

**Dependencies:** None

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Small

## Task 2: 예산 관리 원칙 수정

**Description:** `9.6 예산·인력·일정 관리 원칙`을 AWS 인프라, Runpod AI 실행, OpenAPI LLM/API를 분리 관리하는 방향으로 수정한다.

**Acceptance criteria:**
- [x] AWS 인프라 예산은 `300,000원`으로 관리된다고 명시된다.
- [x] Runpod과 OpenAPI는 각각 `$300` 한도로 분리 관리된다고 명시된다.
- [x] 예산 사용량 확인 대상에 AWS 인프라, Runpod AI 실행, OpenAPI LLM/API, 외부 API 호출량이 포함된다.

**Verification:**
- [x] `rg -n "AWS 인프라|Runpod AI 실행|OpenAPI LLM/API|300,000원" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 1

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Small

## Task 3: 버전과 변경 이력 갱신

**Description:** 요구사항 정의서 버전을 `v1.4.2`로 갱신하고 변경 이력에 인프라 예산 복원과 달러 예산 분리 내역을 추가한다.

**Acceptance criteria:**
- [x] 문서 버전이 `v1.4.2`로 표시된다.
- [x] 변경 이력에 v1.4.2 항목이 추가된다.
- [x] 변경 이력은 인프라 `300,000원`, Runpod `$300`, OpenAPI `$300` 분리 정책을 설명한다.

**Verification:**
- [x] `rg -n "v1\\.4\\.2|인프라 300,000원|Runpod AI 실행 \\$300|OpenAPI LLM/API \\$300" docs\01_requirements\01_requirements.md`

**Dependencies:** Task 2

**Files likely touched:**
- `docs/01_requirements/01_requirements.md`

**Estimated scope:** Small

### Phase 2: 공개 HTML 및 허브 동기화

## Task 4: 공개 HTML 예산 섹션 동기화

**Description:** 원본 Markdown의 예산 표, 관리 원칙, 변경 이력을 `pages/01_requirements.html`에 동일하게 반영한다.

**Acceptance criteria:**
- [x] HTML 예산 표에 `AI 실행 (Runpod)` `$300`이 표시된다.
- [x] HTML 예산 표에 `LLM/API 사용 (OpenAPI)` `$300`이 표시된다.
- [x] HTML 예산 표에 `인프라` `300,000원`이 표시된다.
- [x] HTML 확정 예산 합계가 `300,000원 + $600`으로 표시된다.
- [x] HTML 변경 이력에 v1.4.2가 표시된다.

**Verification:**
- [x] `rg -n "AI 실행 \\(Runpod\\)|LLM/API 사용 \\(OpenAPI\\)|300,000원 \\+ \\$600|v1\\.4\\.2" pages\01_requirements.html`

**Dependencies:** Task 3

**Files likely touched:**
- `pages/01_requirements.html`

**Estimated scope:** Medium

## Task 5: 문서 허브 버전 갱신

**Description:** `index.html`의 요구사항 정의서 카드 버전을 `v1.4.2`로 갱신한다.

**Acceptance criteria:**
- [x] 문서 허브에 `로브 (Lovv) — 요구사항 정의서 v1.4.2`가 표시된다.

**Verification:**
- [x] `rg -n "요구사항 정의서 v1\\.4\\.2" index.html`

**Dependencies:** Task 4

**Files likely touched:**
- `index.html`

**Estimated scope:** Small

### Phase 3: 최종 검증

## Task 6: 일관성 검증

**Description:** 원본 Markdown, 공개 HTML, 문서 허브, 계획서가 같은 예산 정책을 표시하는지 검증한다.

**Acceptance criteria:**
- [x] 원본 Markdown과 HTML의 예산 항목이 일치한다.
- [x] `OpenAPI는 Runpod으로 대체` 같은 이전 정책 표현이 산출물에 남지 않는다.
- [x] HTML 내부 앵커가 정상이다.
- [x] `git diff --check`에서 공백 오류가 없다.

**Verification:**
- [x] `rg -n "OpenAPI는.*Runpod.*대체|Runpod.*대체|OpenAPI.*대체" docs\01_requirements\01_requirements.md pages\01_requirements.html index.html`
- [x] HTML 내부 앵커 검증
- [x] `git diff --check`

**Dependencies:** Task 5

**Files likely touched:**
- `plans/runpod-openapi-budget-integration-plan.md`

**Estimated scope:** Small

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 원화와 달러가 한 숫자로 합산되어 오해됨 | High | 확정 예산 합계를 `300,000원 + $600`으로 병기한다. |
| Runpod과 OpenAPI가 다시 대체 관계로 해석됨 | Medium | 예산 항목을 `AI 실행 (Runpod)`과 `LLM/API 사용 (OpenAPI)`로 분리한다. |
| 인프라 예산이 AI 예산에 포함된 것으로 오해됨 | Medium | 인프라 행을 별도로 유지하고 포함 항목을 AWS 호스팅, DB, 스토리지, 모니터링으로 한정한다. |
| HTML만 수정되고 Markdown 원본이 누락됨 | Medium | 원본 Markdown 수정 후 HTML을 동기화한다. |

## Open Questions

- `OpenAPI`가 실제로 `OpenAI API`를 의미하는지 확인이 필요하다.
- Runpod/OpenAPI의 `$300`이 월 예산, 프로젝트 총 예산, 또는 크레딧 한도 중 무엇인지 결정이 필요하다.

## Verification Results

- [x] v1.4.2와 분리 예산 표현 확인: `rg -n "v1\.4\.2|AI 실행 \(Runpod\)|LLM/API 사용 \(OpenAPI\)|300,000원 \+ \$600|확정 예산 합계" docs\01_requirements\01_requirements.md pages\01_requirements.html index.html`
- [x] 이전 대체 정책 문구 없음: `rg -n "OpenAPI는.*Runpod.*대체|Runpod.*대체|OpenAPI.*대체" docs\01_requirements\01_requirements.md pages\01_requirements.html index.html`
- [x] HTML 내부 앵커 정상
- [x] `git diff --check` 공백 오류 없음. LF→CRLF 경고만 표시됨.

## Definition of Done

- [x] 인프라 예산 `300,000원`이 복원된다.
- [x] Runpod AI 실행 예산 `$300`이 별도 항목으로 표시된다.
- [x] OpenAPI LLM/API 예산 `$300`이 별도 항목으로 표시된다.
- [x] 확정 예산 합계가 `300,000원 + $600`으로 표시된다.
- [x] 원본 요구사항 정의서, 공개 HTML, 문서 허브, 계획서가 같은 예산 정책을 표시한다.
