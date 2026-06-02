---
작성자: Codex
상태: 진행전
---

# 서비스 흐름 HTML 반영 계획

## 목적

`docs/02_service_flow/02_service_flow.md`에 반영된 v0.2 서비스 흐름 명세를 GitHub Pages 공유용 HTML 생성물인 `pages/02_service_flow.html`에 동기화한다.

루트 `AGENT.md` 기준에 따라 `docs/`의 Markdown 원본을 source of truth로 삼고, HTML은 원본을 반영한 공유용 생성물로 취급한다.

## 대상 파일

| 구분 | 파일 | 역할 |
| --- | --- | --- |
| 원본 문서 | `docs/02_service_flow/02_service_flow.md` | 서비스 흐름 명세서 v0.2 기준 문서 |
| 폴더 지침 | `docs/02_service_flow/AGENT.md` | 서비스 흐름 문서 작성 규칙 |
| HTML 생성물 | `pages/02_service_flow.html` | GitHub Pages 공유용 서비스 흐름 문서 |
| 문서 허브 | `index.html` | 서비스 흐름 문서 카드의 버전, 상태, 설명 갱신 대상 |
| 공통 스타일 | `assets/css/requirements.css` | HTML 문서 공통 스타일. 기본적으로 수정하지 않음 |

## 유지할 항목

- `docs/02_service_flow/02_service_flow.md`의 v0.2 내용을 기준으로 한다.
- `pages/02_service_flow.html`은 기존 문서 페이지 구조인 `aside`, `toc`, `main`, `table-wrap`, `info-tbl`, `bullet-list`, `doc-p` 패턴을 유지한다.
- HTML 링크는 GitHub Pages 기준 상대 경로를 유지한다.
- 공통 CSS는 기존 `assets/css/requirements.css`를 사용하며, 필요성이 확인되기 전에는 새 CSS를 추가하지 않는다.
- PoC 흐름과 Production 목표 흐름을 문서 내에서 구분한다.
- 저장, 피드백, 온보딩 관련 내용은 개인정보 및 저장 범위 제한을 함께 유지한다.

## 변경할 항목

- `pages/02_service_flow.html`의 문서 버전을 `v0.2`로 갱신한다.
- 문서 상태를 `검토 중 (Review)` 기준으로 갱신한다.
- 기준 문서를 `docs/01_requirements/01_requirements.md` v1.8로 갱신한다.
- TOC를 v0.2의 13개 섹션 구조에 맞게 재구성한다.
- 본문에 `User Flow`, `Service Flow`, 운영·관리자 데이터 흐름, 관련 요구사항 및 API 영향 섹션을 추가한다.
- `index.html`의 서비스 흐름 카드 버전, 상태, 설명을 v0.2 기준으로 갱신한다.

## 작업 체크리스트

- [ ] 루트 `AGENT.md`와 `docs/02_service_flow/AGENT.md` 지침을 재확인한다.
- [ ] `docs/02_service_flow/02_service_flow.md` v0.2 섹션 목록과 `pages/02_service_flow.html`의 현재 섹션을 매핑한다.
- [ ] `pages/02_service_flow.html`의 `<title>`, aside 버전, 문서 상태, 기준 문서 정보를 v0.2로 갱신한다.
- [ ] `pages/02_service_flow.html`의 TOC를 섹션 1~13 구조에 맞춰 갱신한다.
- [ ] 문서 개요와 사용자 유형 섹션을 v0.2 내용으로 갱신한다.
- [ ] `User Flow` 7단계 표를 HTML에 반영한다.
- [ ] `Service Flow` 8단계 표를 HTML에 반영하고 API 경로 표기를 `/api/v1` 기준과 정합화한다.
- [ ] 온보딩, 목적지 탐색, 챗봇 및 AI 일정 생성 흐름을 v0.2 내용으로 갱신한다.
- [ ] 추천 결과, 실시간 피드백, 저장·피드백·마이페이지 흐름을 v0.2 내용으로 갱신한다.
- [ ] 운영·관리자 데이터 흐름, 예외 흐름, 관련 요구사항 및 API 영향, 변경 이력을 추가한다.
- [ ] `index.html`의 서비스 흐름 문서 카드 버전과 설명을 갱신한다.
- [ ] HTML 렌더링, TOC anchor, 표 구조, 상대 링크를 검증한다.
- [ ] `git diff`로 의도하지 않은 파일 변경이 없는지 확인한다.

## 검증 방법

- [ ] `docs/02_service_flow/02_service_flow.md`와 `pages/02_service_flow.html`의 문서 버전, 상태, 기준 문서가 일치하는지 확인한다.
- [ ] HTML 본문에 Markdown v0.2의 섹션 1~13이 모두 반영됐는지 확인한다.
- [ ] `pages/02_service_flow.html`의 TOC 링크가 각 섹션 id로 이동하는지 확인한다.
- [ ] 긴 표가 기존 `table-wrap` 안에 들어가며 레이아웃을 깨지 않는지 확인한다.
- [ ] `index.html`에서 `pages/02_service_flow.html`로 이동 가능한지 확인한다.

## 리스크와 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 긴 표가 모바일 화면에서 과도하게 넓어짐 | 중간 | 기존 `table-wrap` 구조를 유지해 가로 스크롤로 처리한다 |
| TOC anchor 누락 또는 id 불일치 | 중간 | 섹션 번호별 `href`와 본문 `id`를 1:1로 대조한다 |
| Markdown 원본과 HTML 생성물 내용 불일치 | 중간 | v0.2 섹션 목록과 변경 이력을 기준으로 최종 대조한다 |
| 문서 허브 카드 버전 미갱신 | 낮음 | HTML 본문 갱신 후 `index.html`을 별도 단계로 확인한다 |

## 완료 기준

- `pages/02_service_flow.html`이 `docs/02_service_flow/02_service_flow.md` v0.2 내용을 반영한다.
- `index.html`의 서비스 흐름 카드가 v0.2 기준으로 표시된다.
- 루트 `AGENT.md`의 원본 우선 규칙과 `plans/AGENT.md`의 계획 문서 형식을 만족한다.
