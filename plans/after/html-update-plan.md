---
작성자: Codex
상태: 진행후
---

# HTML 업데이트 계획

## 목적

`docs/`의 대표 Markdown 문서를 기준으로 GitHub Pages 공유용 HTML 산출물인 `index.html`과 `pages/*.html`을 최신 상태로 갱신한다. 이번 작업은 HTML을 직접 고치는 것이 아니라, 원본 문서와 생성 스크립트의 현재 계약을 확인한 뒤 `scripts/generate_pages.py`로 재생성하고 구조 검증을 통과시키는 데 초점을 둔다.

## 기준 원칙

- 내용의 기준은 항상 `docs/` 아래 대표 Markdown 문서다.
- `index.html`과 `pages/*.html`은 공유용 생성물로 취급한다.
- HTML에서 발견된 문구, 버전, 기준 문서, 링크 오류는 대응하는 Markdown 원본이나 생성 스크립트에서 먼저 수정한다.
- 과거 번호 체계의 HTML은 삭제하기 전에 리다이렉트 또는 호환 링크 정책을 확인한다.
- `docs/99_pptx`는 발표 자료 영역이므로 기본 HTML 공개 대상에 포함하지 않는다.

## 대상 파일

### 원본 문서

- `docs/00_project_plan/00_project_plan.md`
- `docs/01_requirements/01_requirements.md`
- `docs/02_service_flow/02_service_flow.md`
- `docs/03_data_collect_plan/03_data_collect_plan.md`
- `docs/04_database_design/04_database_design.md`
- `docs/05_agent_spec/05_agent_spec.md`
- `docs/06_technical_spec/06_technical_spec.md`
- `docs/07_api_spec/07_api_spec.md`
- `docs/08_data_preprocessing/08_data_preprocessing.md` 또는 해당 폴더의 대표 문서가 있을 경우

### 생성물

- `index.html`
- `pages/*.html`

### 생성 및 검증 스크립트

- `scripts/generate_pages.py`
- `scripts/verify_pages_structure.py`

## 작업 체크리스트

- [x] `git status --short`로 기존 미커밋 변경을 확인하고 HTML 업데이트 범위와 분리한다.
- [x] `docs/` 대표 문서 목록과 `scripts/generate_pages.py`의 생성 대상 목록이 일치하는지 확인한다.
- [x] `docs/08_data_preprocessing`의 공개 HTML 포함 여부를 결정한다.
- [x] 각 대표 Markdown의 상단 메타데이터에서 문서 버전, 문서 상태, 기준 문서를 확인한다.
- [x] HTML에서 수정이 필요한 문구가 있으면 대응하는 Markdown 원본 또는 생성 스크립트 수정 대상으로 분류한다.
- [x] 과거 번호 체계로 남아 있는 `pages/*.html` 파일의 리다이렉트 정책을 확인한다.
- [x] 필요한 원본 Markdown 또는 `scripts/generate_pages.py` 수정을 먼저 적용한다.
- [x] `python scripts\generate_pages.py`로 `index.html`과 `pages/*.html`을 재생성한다.
- [x] `python scripts\verify_pages_structure.py`로 문서 허브, 페이지 목록, 이전/다음 링크 구조를 검증한다.
- [x] `index.html`의 문서 카드 순서, 상태, 링크가 생성 대상 문서 순서와 일치하는지 확인한다.
- [x] `pages/*.html`의 상단 메타데이터, 목차, 이전/다음 링크, 상대 경로가 올바른지 확인한다.
- [x] `rg`로 오래된 파일명, 오래된 문서 번호, raw `docs/...` 기준 문서 표기가 남아 있는지 확인한다.
- [x] `git diff --check`로 공백 및 줄 끝 문제를 확인한다.
- [x] 변경 파일 목록을 검토하고 원본 문서 변경과 HTML 생성물 변경이 같은 계약을 반영하는지 확인한다.

## 검증 방법

```powershell
python scripts\generate_pages.py
```

```powershell
python scripts\verify_pages_structure.py
```

```powershell
rg -n "문서 버전|문서 상태|기준 문서" docs pages index.html
```

```powershell
rg -n "docs/0[0-8]_|03_technical_spec|04_api_spec|05_database_design|06_agent_spec" index.html pages
```

```powershell
git diff --check
```

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| HTML만 직접 수정해 원본과 다시 불일치 | High | Markdown 원본 또는 생성 스크립트 수정 후 재생성한다. |
| 과거 HTML 링크가 삭제되어 외부 공유 링크가 깨짐 | Medium | 기존 파일은 삭제 전 리다이렉트 유지 여부를 확인한다. |
| `08_data_preprocessing` 공개 여부가 불명확함 | Medium | 생성 대상 포함 전 대표 문서 존재와 문서 흐름상 위치를 확인한다. |
| `git diff --check`가 CRLF 경고를 출력함 | Low | 실제 공백 오류와 Windows 줄 끝 경고를 구분해 판단한다. |

## 완료 기준

- [x] `scripts/generate_pages.py` 실행 후 `index.html`과 `pages/*.html`이 최신 Markdown 기준으로 갱신되어 있다.
- [x] `python scripts\verify_pages_structure.py`가 통과한다.
- [x] `index.html`에서 공개 대상 문서로 이동할 수 있다.
- [x] 각 `pages/*.html`의 이전/다음 링크가 문서 순서와 일치한다.
- [x] HTML의 문서 버전, 상태, 기준 문서 표기가 Markdown 원본과 일치한다.
- [x] 오래된 번호 체계 HTML은 리다이렉트 또는 유지/삭제 정책이 명확하다.
