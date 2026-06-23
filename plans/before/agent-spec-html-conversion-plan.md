# Agent Spec HTML Conversion Plan

> 작성일: 2026-06-08
> 대상 원본: `docs/05_agent_spec/05_agent_spec.md`
> 대상 HTML: `pages/05_agent_spec.html`
> 범위: Agent 명세 Markdown 변경분을 HTML 공유 문서로 변환
> 제외: PDF 산출물, `agent_spec_revision_plan.md` 요약 반영, 문서 버전 `v0.5` 상향

## 1. 목표

Agent 명세서의 Markdown 원본 변경분을 GitHub Pages용 HTML 산출물에 반영한다. 변환은 `scripts/generate_pages.py`를 사용하고, 생성 후에는 `pages/05_agent_spec.html`만 의도한 변경을 포함하는지 확인한다.

## 2. 원칙

- Markdown 원본인 `docs/05_agent_spec/05_agent_spec.md`를 source of truth로 둔다.
- `pages/05_agent_spec.html`은 직접 편집하지 않고 생성 스크립트로 갱신한다.
- `index.html` 또는 다른 `pages/*.html`이 함께 변경되면 실제 문서 목록/메타데이터 변경 때문인지 diff로 확인한다.
- 이번 작업에서는 PDF를 생성하지 않는다.
- 이번 작업에서는 문서 버전을 `v0.4`로 유지한다.

## 3. 작업 순서

### Task 1: 변환 전 변경 범위 확인

**Description:** 현재 작업트리에서 Agent 명세 관련 Markdown 변경과 기존 untracked plan 파일을 확인한다.

**Acceptance criteria:**
- [ ] `docs/05_agent_spec/05_agent_spec.md` 변경이 HTML 변환 대상임을 확인한다.
- [ ] unrelated 변경이 있는 경우 HTML 변환 commit 범위에서 분리한다.
- [ ] `v0.5` 문자열이 원본 문서에 없는지 확인한다.

**Verification:**
- [ ] `git status --short`
- [ ] `git diff -- docs/05_agent_spec/05_agent_spec.md`
- [ ] `rg -n "v0\\.5" docs/05_agent_spec/05_agent_spec.md`

**Dependencies:** None

**Files likely touched:**
- `docs/05_agent_spec/05_agent_spec.md`
- `plans/before/agent-spec-update-plan.md`

**Estimated scope:** Small

### Task 2: HTML 생성 실행

**Description:** 문서 생성 스크립트를 실행해 Markdown 원본을 HTML 산출물로 변환한다.

**Acceptance criteria:**
- [ ] `pages/05_agent_spec.html`이 최신 `05_agent_spec.md` 내용을 반영한다.
- [ ] 생성 스크립트가 오류 없이 종료된다.
- [ ] HTML은 공통 CSS와 기존 페이지 구조를 유지한다.

**Verification:**
- [ ] `python scripts/generate_pages.py`
- [ ] `Select-String -Path pages/05_agent_spec.html -Pattern "저장소 연결 원칙|lovv_agent_runs|links.map|themes"`

**Dependencies:** Task 1

**Files likely touched:**
- `pages/05_agent_spec.html`
- `index.html` only if generator metadata changes require it

**Estimated scope:** Small

### Task 3: 생성 결과 diff 점검

**Description:** 생성 후 변경된 HTML 파일 목록과 내용이 Agent 명세 변경에 대응하는지 확인한다.

**Acceptance criteria:**
- [ ] `pages/05_agent_spec.html`에 API 매핑과 저장소 계약이 반영된다.
- [ ] `index.html`이나 다른 페이지가 변경되면 생성기 전역 출력인지 확인하고, 불필요하면 제외한다.
- [ ] HTML에 `v0.5`가 나타나지 않는다.

**Verification:**
- [ ] `git diff --name-status`
- [ ] `git diff -- pages/05_agent_spec.html`
- [ ] `rg -n "v0\\.5" pages/05_agent_spec.html`

**Dependencies:** Task 2

**Files likely touched:**
- `pages/05_agent_spec.html`

**Estimated scope:** Small

### Task 4: 구조 검증

**Description:** 문서 사이트 생성물의 구조와 기본 렌더링 규칙을 검증한다.

**Acceptance criteria:**
- [ ] 페이지 구조 검증이 통과한다.
- [ ] Markdown/HTML diff에 trailing whitespace 문제가 없다.
- [ ] 이전/다음 문서 링크와 상대 경로가 유지된다.

**Verification:**
- [ ] `python scripts/verify_pages_structure.py`
- [ ] `git diff --check`
- [ ] 필요 시 `rg -n "05_agent_spec.html|06_technical_spec.html|04_database_design.html" index.html pages/05_agent_spec.html`

**Dependencies:** Task 3

**Files likely touched:**
- None, unless verification exposes generated-output drift

**Estimated scope:** Small

### Task 5: 커밋 준비

**Description:** HTML 변환 산출물과 원본 Markdown 변경을 같은 `docs(agent-spec)` 스코프로 묶을 수 있는지 확인한다.

**Acceptance criteria:**
- [ ] commit 대상은 Agent 명세 원본, Agent 명세 HTML, 관련 plan 파일로 제한된다.
- [ ] PDF 파일은 포함되지 않는다.
- [ ] scope 단위 conventional commit 메시지를 사용할 수 있다.

**Verification:**
- [ ] `git status --short`
- [ ] `git diff --stat`
- [ ] `git diff --cached --name-status` after staging

**Dependencies:** Task 4

**Files likely touched:**
- `docs/05_agent_spec/05_agent_spec.md`
- `pages/05_agent_spec.html`
- `plans/before/agent-spec-update-plan.md`
- `plans/before/agent-spec-html-conversion-plan.md`

**Estimated scope:** Small

## 4. 체크포인트

### Checkpoint A: 변환 전

- [ ] Agent 명세 원본 변경이 확정됐다.
- [ ] `v0.4` 유지가 확인됐다.
- [ ] PDF 제외 범위가 확인됐다.

### Checkpoint B: 변환 후

- [ ] `pages/05_agent_spec.html`이 원본 변경을 반영한다.
- [ ] 다른 HTML 변경이 발생하면 원인을 확인했다.
- [ ] 생성 스크립트와 구조 검증이 통과했다.

### Checkpoint C: 커밋 전

- [ ] `git diff --check`가 통과한다.
- [ ] scope는 `docs(agent-spec)` 또는 `docs(site)` 중 실제 변경 범위에 맞게 선택한다.
- [ ] unrelated 파일이 stage되지 않았다.

## 5. 리스크와 대응

| Risk | Impact | Mitigation |
| --- | --- | --- |
| 전체 생성 스크립트가 다른 페이지까지 갱신 | Medium | `git diff --name-status`로 실제 변경 파일을 확인하고 관련 없는 생성물은 stage하지 않는다. |
| HTML 직접 수정으로 원본과 불일치 | High | `pages/05_agent_spec.html`은 직접 편집하지 않고 `generate_pages.py`만 사용한다. |
| Mermaid, table, code block 렌더링 깨짐 | Medium | 생성 후 `pages/05_agent_spec.html`에서 주요 문자열과 섹션 anchor를 확인한다. |
| PDF가 함께 포함됨 | Low | 이번 범위에서는 `pdf/` 파일을 생성하거나 stage하지 않는다. |

## 6. Open Questions

- 없음. 이번 HTML 변환은 `v0.4` 유지, PDF 제외, `agent_spec_revision_plan.md` 요약 반영 제외 기준으로 진행한다.
