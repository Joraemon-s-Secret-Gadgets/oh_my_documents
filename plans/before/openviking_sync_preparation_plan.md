---
작성자: 조동휘 nobrain711
상태: 진행중
---

# OpenViking 문서 이관 준비 계획

## 목적

GitHub 저장소 `Joraemon-s-Secret-Gadgets/oh_my_documents`의 문서 원본을 OpenViking의 `viking://resources/oh_my_documents/`로 동기화할 수 있도록 이관 기준 문서와 sync 스크립트를 추가한다.

GitHub repo는 Markdown 원본 저장소로 유지하고, OpenViking은 Agent 검색 및 컨텍스트 저장소로 사용한다. 이 작업은 이관 준비만 다루며 실제 OpenViking 업로드 CLI 연동은 이후 환경별 설정에 맞춰 확정한다.

## 원칙

- 원본 문서는 `docs/**/*.md`를 기준으로 한다.
- `README.md`, 루트 `AGENT.md`, `docs/**/AGENT.md`도 Agent 컨텍스트 유지를 위해 함께 이관한다.
- `index.html`, `pages/`, `pdf/`, `assets/`는 생성 산출물이므로 이관 대상에서 제외한다.
- 이미지, PPTX, PDF, HTML 산출물은 sync 대상에서 제외한다.
- 기존 `docs/` 원본 문서 본문은 수정하지 않는다.
- `pages/`, `pdf/`, `assets/` 산출물은 수정하지 않는다.

## 대상 파일

새로 추가할 파일:

- `docs/OPENVIKING_SUMMARY.md`
- `scripts/sync_openviking_docs.py`

수정하지 않을 파일과 디렉터리:

- `README.md`
- `AGENT.md`
- `docs/**/*.md`
- `index.html`
- `pages/`
- `pdf/`
- `assets/`

## Parent Issue

생성된 Parent Issue: <https://github.com/Joraemon-s-Secret-Gadgets/oh_my_documents/issues/3>

### Title

OpenViking 문서 이관 준비

### Body

```markdown
## 목표

`Joraemon-s-Secret-Gadgets/oh_my_documents`의 문서 원본을 OpenViking `viking://resources/oh_my_documents/`로 동기화할 수 있도록 이관 기준 문서와 sync 스크립트를 준비합니다.

## 범위

- `docs/OPENVIKING_SUMMARY.md` 추가
- `scripts/sync_openviking_docs.py` 추가
- GitHub repo는 원본 저장소, OpenViking은 Agent 검색/컨텍스트 저장소로 사용하는 운영 기준 정리

## 제외

- 기존 `docs/` 원본 문서 본문 수정
- `index.html`, `pages/`, `pdf/`, `assets/` 산출물 수정
- 실제 OpenViking CLI 업로드 연동 확정

## 하위 작업

- [x] #4
- [x] #5
- [x] #6
- [x] #7
- [ ] #8
```

### Labels

- `docs`
- `openviking`
- `migration`

## Task Issues

생성된 Task Issues:

- Task 0: <https://github.com/Joraemon-s-Secret-Gadgets/oh_my_documents/issues/4> (완료)
- Task 1: <https://github.com/Joraemon-s-Secret-Gadgets/oh_my_documents/issues/5> (완료)
- Task 2: <https://github.com/Joraemon-s-Secret-Gadgets/oh_my_documents/issues/6> (완료)
- Task 3: <https://github.com/Joraemon-s-Secret-Gadgets/oh_my_documents/issues/7> (완료)
- Task 4: <https://github.com/Joraemon-s-Secret-Gadgets/oh_my_documents/issues/8>

### Task 0: GitHub Issue 생성 및 작업 추적 구조 확정

**Issue title:** OpenViking 이관 준비 Issue 생성 및 작업 추적 구조 확정

**Description:** 구현을 시작하기 전에 Parent Issue와 Task별 하위 Issue를 먼저 생성하고, 각 Task Issue가 Parent Issue와 연결되도록 작업 추적 구조를 확정한다. GitHub parent-child issue 연결이 환경에서 지원되지 않으면 Parent Issue 체크리스트와 Task Issue 본문 상호 링크로 대체한다.

**Acceptance criteria:**

- [x] Parent Issue가 생성되어 있다.
- [x] Task 1, Task 2, Task 3, Task 4 하위 Issue가 생성되어 있다.
- [x] 각 Task Issue 본문에 Parent Issue URL 또는 번호가 명시되어 있다.
- [x] Parent Issue 본문에 Task Issue 링크가 체크리스트로 반영되어 있다.
- [x] 작성자는 `조동휘 nobrain711`로 계획 문서에 기록되어 있다.

**Verification:**

- [x] Parent Issue 본문에서 Task Issue 링크 확인
- [x] Task Issue 본문에서 Parent Issue 링크 확인

**Dependencies:** None

**Files likely touched:**

- `plans/before/openviking_sync_preparation_plan.md`

**Estimated scope:** Small

### Task 1: OpenViking 이관 기준 인덱스 작성

**Issue title:** OpenViking 이관 기준 인덱스 작성

**Description:** `docs/OPENVIKING_SUMMARY.md`를 추가해 OpenViking 이관 목적, 원본 문서 기준, 함께 이관할 Agent 문서, 대상 경로, 주요 문서 목록, 제외 대상, 운영 방식을 정리한다.

**Acceptance criteria:**

- [x] `docs/OPENVIKING_SUMMARY.md`가 추가되어 있다.
- [x] OpenViking 대상 경로 `viking://resources/oh_my_documents/`가 명시되어 있다.
- [x] 원본 기준 `docs/**/*.md`와 함께 이관할 `README.md`, 루트 `AGENT.md`, `docs/**/AGENT.md`가 명시되어 있다.
- [x] 제외 대상 `index.html`, `pages/`, `pdf/`, `assets/`, `*.pdf`, `*.pptx`, `*.png`, `*.jpg`, `*.jpeg`, `*.html`이 명시되어 있다.
- [x] GitHub repo와 OpenViking의 역할 분리가 명시되어 있다.

**Verification:**

- [x] `git diff -- docs/OPENVIKING_SUMMARY.md`로 신규 문서 내용 확인
- [x] 기존 `docs/` 원본 문서 본문이 수정되지 않았는지 확인

**Dependencies:** Task 0

**Files likely touched:**

- `docs/OPENVIKING_SUMMARY.md`

**Estimated scope:** Small

### Task 2: OpenViking sync 스크립트 추가

**Issue title:** OpenViking 문서 sync 스크립트 추가

**Description:** `scripts/sync_openviking_docs.py`를 추가해 OpenViking으로 동기화할 파일 목록을 수집하고, 실제 업로드 로직을 `upload_file()` 함수 하나에 모아 향후 CLI 변경에 대응할 수 있게 한다.

**Acceptance criteria:**

- [x] `scripts/sync_openviking_docs.py`가 추가되어 있다.
- [x] `TARGET_ROOT = "viking://resources/oh_my_documents"` 상수가 정의되어 있다.
- [x] 포함 대상은 `README.md`, `AGENT.md`, `docs/**/*.md`, `docs/**/*.txt`, `docs/**/*.json`, `docs/**/*.yml`, `docs/**/*.yaml`로 제한되어 있다.
- [x] 기본 제외 대상은 `index.html`, `pages/`, `pdf/`, `assets/`, `.git/`, `.venv/`, `node_modules/`, 이미지, PPTX, HTML 산출물을 포함한다.
- [x] 실제 업로드 변경 지점은 `upload_file()` 함수 하나로 모여 있다.

**Verification:**

- [x] `python -m py_compile scripts\sync_openviking_docs.py`
- [x] `python scripts\sync_openviking_docs.py --dry-run`

**Dependencies:** Task 0, Task 1

**Files likely touched:**

- `scripts/sync_openviking_docs.py`

**Estimated scope:** Small

### Task 3: sync 대상/제외 규칙 검증

**Issue title:** OpenViking sync 대상 및 제외 규칙 검증

**Description:** sync 스크립트 dry-run 결과를 확인해 원본 문서와 Agent 컨텍스트 파일만 포함되고 생성 산출물이 제외되는지 검증한다.

**Acceptance criteria:**

- [x] dry-run 결과에 `README.md`와 루트 `AGENT.md`가 포함되어 있다.
- [x] dry-run 결과에 `docs/OPENVIKING_SUMMARY.md`와 `docs/**/AGENT.md`가 포함되어 있다.
- [x] dry-run 결과에 허용 확장자 외 파일이 포함되지 않는다.
- [x] dry-run 결과에 `index.html`, `pages/`, `pdf/`, `assets/`, 이미지, PPTX, HTML 산출물이 포함되지 않는다.

**Verification:**

- [x] `python scripts\sync_openviking_docs.py --dry-run`
- [x] dry-run 출력에서 포함/제외 파일 표본 확인

**Dependencies:** Task 0, Task 2

**Files likely touched:**

- None

**Estimated scope:** Small

### Task 4: 변경 범위 검증 및 커밋

**Issue title:** OpenViking 이관 준비 변경 범위 검증 및 커밋

**Description:** 변경 범위가 계획된 신규 파일 두 개로 제한되는지 확인하고, 생성된 GitHub Issue 번호를 커밋 메시지의 `Refs:`에 반영해 커밋한다.

**Acceptance criteria:**

- [ ] 변경 파일이 `docs/OPENVIKING_SUMMARY.md`, `scripts/sync_openviking_docs.py`로 제한되어 있다.
- [ ] 기존 `README.md`, `AGENT.md`, `docs/` 원본 본문, `pages/`, `pdf/`, `assets/`가 수정되지 않았다.
- [ ] 커밋 메시지는 요청 형식을 따른다.
- [ ] `Refs: #이슈번호`에 실제 Parent Issue 번호가 반영되어 있다.

**Verification:**

- [ ] `git status --short`
- [ ] `git diff --name-only`
- [ ] `git diff --cached --check`
- [ ] `git log -1 --oneline`

**Dependencies:** Task 0, Task 1, Task 2, Task 3

**Files likely touched:**

- `docs/OPENVIKING_SUMMARY.md`
- `scripts/sync_openviking_docs.py`

**Estimated scope:** Small

## 작업 체크리스트

- [x] Task 0 수행: Parent Issue 생성 및 Task Issue 연결 구조 확정
- [x] Parent Issue 생성
- [x] Task 1 하위 Issue 생성
- [x] Task 2 하위 Issue 생성
- [x] Task 3 하위 Issue 생성
- [x] Task 4 하위 Issue 생성
- [x] `docs/OPENVIKING_SUMMARY.md` 추가
- [x] `scripts/sync_openviking_docs.py` 추가
- [x] `python -m py_compile scripts\sync_openviking_docs.py` 실행
- [x] `python scripts\sync_openviking_docs.py --dry-run` 실행
- [ ] 변경 범위 확인
- [ ] 요청한 커밋 메시지 형식으로 커밋

## GitHub Issue 생성 명령 예시

Parent Issue:

```powershell
gh issue create --title "OpenViking 문서 이관 준비" --label "docs,openviking,migration" --body-file .\plans\before\openviking_parent_issue.md
```

Task Issue:

```powershell
gh issue create --title "OpenViking 이관 기준 인덱스 작성" --label "docs,openviking" --body-file .\plans\before\openviking_task_1_issue.md
```

GitHub CLI에서 parent-child issue 연결 방식은 project 설정과 GitHub 기능 활성화 상태에 따라 다를 수 있다. 자동 연결이 어려운 경우 각 Task Issue 본문에 Parent Issue URL을 명시하고, Parent Issue의 하위 작업 체크리스트에 Task Issue 링크를 반영한다.

## 검증 방법

- `git status --short`로 계획 문서 추가 범위를 확인한다.
- 구현 단계에서는 `python -m py_compile scripts\sync_openviking_docs.py`로 스크립트 문법을 확인한다.
- 구현 단계에서는 `python scripts\sync_openviking_docs.py --dry-run`으로 이관 대상 목록을 확인한다.
- 구현 단계에서는 `git diff --name-only`로 생성 산출물이 수정되지 않았는지 확인한다.

## 위험 및 대응

| Risk | Impact | Mitigation |
| --- | --- | --- |
| OpenViking CLI 명령이 환경마다 다름 | 업로드 연동이 깨질 수 있음 | `upload_file()` 함수 하나에 업로드 로직을 격리 |
| 생성 산출물이 sync 대상에 포함됨 | OpenViking 검색 컨텍스트가 중복되거나 오염됨 | 포함 확장자 allowlist와 제외 디렉터리 blocklist를 함께 적용 |
| 기존 문서 운영 규칙과 충돌 | GitHub Pages/PDF 산출물 흐름이 혼란스러워짐 | GitHub는 원본, OpenViking은 Agent 컨텍스트 저장소로 역할 분리 |
| GitHub parent-child issue 연결이 불가능함 | Task 추적성이 낮아짐 | Parent Issue 체크리스트와 Task Issue 본문 상호 링크로 대체 |

## 완료 기준

- `docs/OPENVIKING_SUMMARY.md`와 `scripts/sync_openviking_docs.py`가 추가되어 있다.
- GitHub Parent Issue와 Task Issue가 생성되어 있다.
- sync 대상/제외 규칙이 dry-run으로 검증되어 있다.
- 요청한 커밋 메시지 형식으로 커밋되어 있다.
