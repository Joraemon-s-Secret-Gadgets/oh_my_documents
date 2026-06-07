---
작성자: Codex
상태: 진행중
---

# Git Diff 기반 문서 변경 정리 계획

## 목적

현재 작업트리에 남아 있는 문서 변경사항을 `git diff`와 `git status` 기준으로 확인하고, 불필요한 보조 초안은 삭제 방향으로 정리한다.

이번 계획은 `docs/06_database_design/drafts/`를 대표 문서 반영 대상으로 보지 않고 삭제 대상으로 분류한다.
또한 `docs/04_data_collect_plan/04_data_collect_plan.md`와 관련 국가별 취득 계획서, 생성 HTML이 최신 데이터 취득 방향과 맞는지 재확인한다.

## 현재 Diff 요약

| 상태 | 파일 또는 경로 | 정리 방향 |
| --- | --- | --- |
| `??` | `docs/06_database_design/drafts/` | 대표 문서 반영 없이 삭제 대상으로 정리 |
| `M` | `pages/06_database_design.html` | 현재 diff 본문은 없고 LF/CRLF 경고만 확인됨. 실질 변경 여부를 확인한 뒤 필요 시 정리 |
| `??` | `plans/during/git-diff-document-reflection-plan.md` | 현재 작업 계획 파일로 유지 |

## 대상 파일

| 구분 | 파일 |
| --- | --- |
| 삭제 정리 대상 | `docs/06_database_design/drafts/` |
| 대표 DB 설계 문서 | `docs/06_database_design/06_database_design.md` |
| DB 설계 HTML 생성물 | `pages/06_database_design.html` |
| 재확인 대상 원본 | `docs/04_data_collect_plan/04_data_collect_plan.md` |
| 재확인 대상 국가별 초안 | `docs/04_data_collect_plan/korea_data_acquisition_plan.md`, `docs/04_data_collect_plan/japan_data_acquisition_plan.md` |
| 재확인 대상 HTML | `pages/04_data_collect_plan.html` |

## 반영 원칙

- `docs/06_database_design/drafts/`는 현재 문서 체계에 남기지 않는다.
- 데이터베이스 설계 대표 문서는 `docs/06_database_design/06_database_design.md`로 유지한다.
- `pages/06_database_design.html`은 줄바꿈 상태만 변경된 경우 내용 변경으로 취급하지 않는다.
- 데이터 수집 계획은 `docs/04_data_collect_plan/04_data_collect_plan.md`를 대표 문서로 본다.
- 국가별 취득 계획서는 대표 문서의 상세 초안으로 유지한다.
- 데이터 수집 계획의 최신 기준은 한국 경북·강원 40개 도시 우선 취득, 일본 관동 지역 지자체 후속 수집, JSON 원본 S3 Raw Bucket 저장, Lambda 전처리, DynamoDB 적재이다.

## Data Plan 재확인 결과

| 확인 항목 | 확인 결과 |
| --- | --- |
| 우선 취득 범위 | `04_data_collect_plan.md`와 `pages/04_data_collect_plan.html`에 한국은 경북과 강원의 40개 도시를 우선 취득한 뒤 일본 관동 지역 지자체를 수집한다고 명시되어 있음 |
| City 취득 방식 | 한국은 도 간략 정보와 산하 도시 목록, 일본은 도도부현 간략 정보와 산하 도시 목록을 먼저 확보하고 해당 산하 City만 Wikipedia 크롤링 대상으로 둠 |
| 저장 흐름 | JSON 직렬화 후 S3 Raw Bucket 적재, 일정 기간 누적, Lambda 배치 전처리, DynamoDB 적재 흐름이 원본과 HTML에 반영되어 있음 |
| 기후 검증 | City `climate`는 Wikipedia 취득값을 기준으로 한국은 기상청, 일본은 일본기상청(JMA) 자료와 비교한다고 반영되어 있음 |
| HTML 동기화 | `pages/04_data_collect_plan.html`에 대표 문서의 핵심 문구가 반영되어 있음 |

## 작업 체크리스트

### 1. Diff 범위 확정

- [x] `git status --short`로 남은 변경 범위를 확인한다.
- [x] `git diff --name-status`로 `pages/06_database_design.html`의 실질 변경 여부를 확인한다.
- [x] `docs/06_database_design/drafts/`가 untracked 신규 초안 묶음임을 확인한다.
- [x] `docs/04_data_collect_plan/04_data_collect_plan.md`와 `pages/04_data_collect_plan.html`의 핵심 문구를 재확인한다.

### 2. 삭제 방향 정리

- [x] `docs/06_database_design/drafts/`를 삭제 대상으로 확정한다.
- [x] 삭제 전 마지막으로 `docs/06_database_design/drafts/` 안에 필요한 내용이 대표 문서에 이미 반영되어 있는지 확인한다.
- [x] 필요 내용이 없으면 `docs/06_database_design/drafts/` 전체를 작업트리에서 제거한다.
- [x] 삭제 후 `git status --short`에서 `docs/06_database_design/drafts/`가 사라졌는지 확인한다.

### 3. DB 설계 HTML 상태 정리

- [ ] `pages/06_database_design.html`이 LF/CRLF 상태 변경만 있는지 재확인한다.
- [ ] 실질 내용 변경이 없다면 별도 문서 변경으로 취급하지 않는다.
- [ ] 실질 변경이 있다면 원본 `docs/06_database_design/06_database_design.md`와의 동기화 여부를 먼저 확인한다.

### 4. Data Plan 유지 확인

- [x] `docs/04_data_collect_plan/04_data_collect_plan.md`에서 경북·강원 40개 도시 우선 취득 문구를 확인한다.
- [x] `docs/04_data_collect_plan/04_data_collect_plan.md`에서 S3 Raw Bucket, Lambda, DynamoDB 흐름을 확인한다.
- [x] `docs/04_data_collect_plan/04_data_collect_plan.md`에서 Wikipedia 취득 후 기상청/JMA 비교 검증 문구를 확인한다.
- [x] `docs/04_data_collect_plan/korea_data_acquisition_plan.md`에서 한국 City 취득 방식과 S3 저장 흐름을 확인한다.
- [x] `docs/04_data_collect_plan/japan_data_acquisition_plan.md`에서 일본 City 취득 방식과 S3 저장 흐름을 확인한다.
- [x] `pages/04_data_collect_plan.html`에 같은 핵심 문구가 반영되어 있는지 확인한다.

### 5. 검증

- [x] 삭제 정리 후 `git status --short`를 확인한다.
- [x] 삭제 정리 후 `git diff --name-status`를 확인한다.
- [x] `git diff --check`로 공백 오류를 확인한다.
- [ ] staged 대상에서 삭제 정리와 무관한 변경이 제외되어 있는지 확인한다.
- [ ] 필요 시 Conventional Commit 형식으로 정리 커밋을 만든다.

## 수용 기준

- `docs/06_database_design/drafts/`는 최종 변경 대상에서 제거된다.
- `pages/06_database_design.html`의 변경이 줄바꿈 상태인지 실질 내용 변경인지 구분되어 있다.
- `docs/04_data_collect_plan/04_data_collect_plan.md`, 국가별 취득 계획서, `pages/04_data_collect_plan.html`은 최신 데이터 취득 방향과 의미가 일치한다.
- 데이터 수집 계획의 S3 Raw 저장, Lambda 전처리, DynamoDB 적재 흐름은 유지된다.
- 한국과 일본의 City 취득 방식과 기후 비교 검증 방식이 원본과 HTML에 같이 남아 있다.

## 위험 및 대응

| 위험 | 대응 |
| --- | --- |
| `drafts/` 안의 일부 내용을 실수로 필요한 변경으로 오해함 | 삭제 전 대표 문서와 data plan에 필요한 내용이 이미 반영되어 있는지 확인한다. |
| `pages/06_database_design.html`의 줄바꿈 상태를 내용 변경으로 오인함 | diff 본문이 없는지 확인하고, 실질 변경이 있을 때만 원본과 동기화한다. |
| data plan 원본과 HTML 의미가 어긋남 | `rg`로 핵심 문구를 원본 Markdown과 HTML 양쪽에서 확인한다. |
