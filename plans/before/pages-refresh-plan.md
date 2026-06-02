---
작성자: Codex
상태: 진행전
---

# Pages 최신화 계획

## 목적

`docs/`의 최신 Markdown 원본을 기준으로 GitHub Pages 공유용 HTML 산출물인 `index.html`과 `pages/*.html`을 최신화한다. 현재 원본 문서는 `docs/00_project_plan`부터 `docs/07_agent_spec`까지 존재하지만, `pages/`에는 `04_data_collect_plan.html`이 없고 `07_agent_spec.md`가 `pages/06_agent_spec.html`로 연결되어 있어 문서 번호와 허브 구성이 일부 어긋나 있다. 이번 작업은 원본과 생성물의 대응 관계, 문서 버전, 링크, 공통 디자인을 정합화하는 데 집중한다.

## 기준 원칙

- 내용 기준은 항상 `docs/`의 대표 Markdown 파일이다.
- `index.html`과 `pages/*.html`은 공유용 생성물로 취급한다.
- 문서 본문 수정이 필요하면 먼저 대응하는 Markdown 원본에 반영한 뒤 HTML을 갱신한다.
- 모든 HTML 문서는 기존 `assets/css/requirements.css` 기반 문서 레이아웃을 재사용한다.
- GitHub Pages 배포를 고려해 링크는 상대 경로로 유지한다.

## 대상 파일

### 원본 문서

- `docs/00_project_plan/00_project_plan.md`
- `docs/01_requirements/01_requirements.md`
- `docs/02_service_flow/02_service_flow.md`
- `docs/03_technical_spec/03_technical_spec.md`
- `docs/04_data_collect_plan/04_data_collect_plan.md`
- `docs/05_api_spec/05_api_spec.md`
- `docs/06_database_design/06_database_design.md`
- `docs/07_agent_spec/07_agent_spec.md`

### 생성 대상

- `index.html`
- `pages/00_project_plan.html`
- `pages/01_requirements.html`
- `pages/02_service_flow.html`
- `pages/03_technical_spec.html`
- `pages/04_data_collect_plan.html`
- `pages/05_api_spec.html`
- `pages/06_database_design.html`
- `pages/07_agent_spec.html`

## 변경 방향

### 1. 문서 번호 체계 정리

현재 `pages/04_api_spec.html`, `pages/05_database_design.html`, `pages/06_agent_spec.html`은 `docs/04_data_collect_plan`이 빠진 상태의 번호 체계다. 최신 문서 흐름은 아래 순서로 맞춘다.

| 순서 | 원본 | HTML |
| --- | --- | --- |
| 00 | `docs/00_project_plan/00_project_plan.md` | `pages/00_project_plan.html` |
| 01 | `docs/01_requirements/01_requirements.md` | `pages/01_requirements.html` |
| 02 | `docs/02_service_flow/02_service_flow.md` | `pages/02_service_flow.html` |
| 03 | `docs/03_technical_spec/03_technical_spec.md` | `pages/03_technical_spec.html` |
| 04 | `docs/04_data_collect_plan/04_data_collect_plan.md` | `pages/04_data_collect_plan.html` |
| 05 | `docs/05_api_spec/05_api_spec.md` | `pages/05_api_spec.html` |
| 06 | `docs/06_database_design/06_database_design.md` | `pages/06_database_design.html` |
| 07 | `docs/07_agent_spec/07_agent_spec.md` | `pages/07_agent_spec.html` |

기존 번호가 밀린 HTML 파일은 새 파일명으로 생성하고, 필요하면 기존 파일은 호환 링크 또는 삭제 후보로 별도 검토한다. GitHub Pages에서 외부 공유된 링크가 있을 수 있으므로 삭제 여부는 구현 시점에 확인한다.

### 2. 문서 허브 최신화

`index.html`의 카드 목록을 위 문서 순서와 동일하게 갱신한다.

- 프로젝트 기획서 제목을 `v0.4`로 갱신한다.
- 요구사항 명세서 제목을 `v1.7`로 유지한다.
- 데이터 수집 계획서 카드를 새로 추가한다.
- API, 데이터베이스, Agent 명세서 링크를 새 번호 체계에 맞춘다.
- 하단 문서 작성 흐름에 데이터 수집 계획서를 포함한다.

### 3. 각 HTML 본문 최신화

각 HTML의 표지 영역, 사이드바 버전, 문서 메타데이터, 본문 섹션을 Markdown 원본과 맞춘다.

- `문서 버전`, `문서 상태`, `기준 문서`가 원본과 일치해야 한다.
- Markdown의 제목 순서가 사이드바 목차와 본문 앵커에 반영되어야 한다.
- 표, 목록, 코드, mermaid 다이어그램이 있으면 기존 문서 스타일 안에서 깨지지 않아야 한다.
- 이전/다음 문서 링크가 새 번호 체계를 기준으로 연결되어야 한다.

### 4. 생성 방식 정리

현재 저장소에는 HTML에서 Markdown을 추출하는 `scripts/extract_html_md_content.py`는 있지만, Markdown에서 HTML을 생성하는 전용 스크립트는 없다. 이번 최신화는 우선 기존 HTML 구조를 템플릿으로 삼아 수동 생성하되, 반복 비용이 커지면 후속 작업으로 `scripts/generate_pages.py`를 만드는 것을 분리한다.

## 작업 체크리스트

- [ ] `docs/` 대표 Markdown 8개의 문서 버전, 상태, 기준 문서를 확인한다.
- [ ] 기존 `pages/*.html`의 레이아웃, 공통 클래스, 특수 처리 항목을 확인한다.
- [ ] `pages/04_data_collect_plan.html`을 신규 생성한다.
- [ ] 기존 API, DB, Agent HTML을 `05`, `06`, `07` 번호 체계로 재생성하거나 이동한다.
- [ ] `pages/00_project_plan.html`과 `pages/01_requirements.html`의 버전 표기가 `index.html`과 일치하는지 확인하고 갱신한다.
- [ ] `index.html`의 문서 카드, 링크, 상태, 문서 작성 흐름을 최신 문서 순서로 갱신한다.
- [ ] 각 HTML의 이전/다음 링크와 사이드바 목차 링크를 확인한다.
- [ ] 기존 `pages/04_api_spec.html`, `pages/05_database_design.html`, `pages/06_agent_spec.html`의 유지·삭제·리다이렉트 필요성을 결정한다.
- [ ] 모든 링크와 문서 메타데이터를 검색으로 검증한다.
- [ ] `git diff --check`로 공백 오류를 확인한다.

## 검증 방법

```powershell
rg -n "v0.4|v1.7|데이터 수집 계획서|API 명세서|데이터베이스 설계 명세서|Agent 명세서" index.html pages
```

```powershell
rg -n "href=\"\\.\\/pages\\/|href=\"\\.\\/" index.html pages
```

```powershell
rg -n "문서 버전|문서 상태|기준 문서" docs pages
```

```powershell
git diff --check
```

브라우저 수동 검증 항목:

- [ ] `index.html`에서 00~07 문서 카드가 모두 보인다.
- [ ] 각 카드 클릭 시 대상 HTML로 이동한다.
- [ ] 각 문서의 표지, 목차, 표, 목록이 깨지지 않는다.
- [ ] 모바일 폭에서 카드 텍스트와 문서 본문이 겹치지 않는다.
- [ ] 이전/다음 링크가 문서 순서대로 이동한다.

## 리스크와 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 기존 공유 링크가 번호 변경으로 깨짐 | Medium | 기존 파일 삭제 전 외부 공유 여부를 확인하고, 필요하면 호환 안내 페이지를 둔다. |
| Markdown 원본과 HTML 생성물이 다시 불일치함 | High | 갱신 후 `문서 버전`, 제목, 주요 키워드를 `rg`로 교차 검증한다. |
| HTML 수동 생성으로 누락이 생김 | Medium | 문서별 섹션 수와 주요 표 제목을 원본과 HTML에서 비교한다. |
| 공통 CSS와 새 문서 표 구조가 맞지 않음 | Low | 기존 `requirements.css` 클래스를 우선 재사용하고, 필요한 CSS만 최소 추가한다. |

## 완료 기준

- [ ] `docs/` 대표 문서 8개와 `pages/` HTML 8개가 1:1로 대응한다.
- [ ] `index.html`에서 모든 최신 HTML 문서로 이동할 수 있다.
- [ ] `04_data_collect_plan`이 문서 허브와 `pages/`에 포함되어 있다.
- [ ] API, DB, Agent 문서 번호가 최신 문서 흐름과 일치한다.
- [ ] 문서 버전과 상태가 Markdown 원본과 HTML 산출물에서 일치한다.
- [ ] 링크 검증과 `git diff --check`가 통과한다.
