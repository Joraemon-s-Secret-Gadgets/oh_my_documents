---
작성자: Codex
상태: 진행중
---

# 프로젝트 색상맵 반영 계획

## 목적

루트 `color-map.md`에 정의된 로브 프로젝트 색상맵을 GitHub Pages 문서 사이트와 향후 HTML 화면 구현에 일관되게 반영한다.

루트 `AGENT.md` 기준에 따라 `docs/` Markdown 원본과 루트 기준 문서를 우선 관리하고, `index.html`, `pages/*.html`, `assets/`는 공유용 생성물과 정적 리소스로 취급한다.

## 대상 파일

| 구분 | 파일 | 역할 |
| --- | --- | --- |
| 색상 기준 문서 | `color-map.md` | 프로젝트 공통 색상맵 원본 |
| 공통 사이트 스타일 | `assets/css/site.css` | `index.html` 문서 허브 스타일 |
| 공통 문서 스타일 | `assets/css/requirements.css` | `pages/*.html` 문서 페이지 스타일 |
| 문서 허브 | `index.html` | 색상 적용 결과 확인 대상 |
| HTML 문서 | `pages/*.html` | 색상 적용 결과 확인 대상 |

## 유지할 항목

- HTML 본문 구조와 문서 내용은 변경하지 않는다.
- 색상 변경은 가능한 한 CSS 변수 중심으로 처리한다.
- 기존 GitHub Pages 상대 경로와 문서 링크는 유지한다.
- 문서 원본과 HTML 생성물의 내용 동기화 작업과 색상 적용 작업을 혼동하지 않는다.

## 변경할 항목

- `assets/css/site.css`의 기존 녹색/골드 계열 CSS 변수를 프로젝트 색상맵 기준으로 재정의한다.
- `assets/css/requirements.css`에 동일한 색상 변수 체계를 적용하거나 기존 변수와 매핑한다.
- 배경은 `Soft Beige (#FFF3E7)` 중심으로 조정한다.
- 본문/타이틀 텍스트는 `Dark Charcoal (#222222)` 중심으로 조정한다.
- CTA, 활성 TOC, 강조선, 로고 계열은 `Main Orange (#F26518)` 중심으로 조정한다.
- 보조 제목과 상태성 강조는 `Muted Brown (#D44A14)`을 사용한다.
- 카드 배경 또는 정보 블록 배경은 `Card Peach (#FCE7DB)`을 사용한다.
- 보조 설명과 footer 계열 텍스트는 `Sub Text Gray (#666666)`을 사용한다.

## 작업 체크리스트

- [x] `color-map.md`의 색상명, HEX, 용도 정의를 확인한다.
- [x] `assets/css/site.css`의 현재 CSS 변수와 사용 위치를 확인한다.
- [x] `assets/css/requirements.css`의 현재 CSS 변수와 사용 위치를 확인한다.
- [x] 두 CSS 파일의 변수명을 유지할지, 새 변수명을 추가할지 결정한다.
- [x] `site.css`에 색상맵을 반영해 `index.html` 문서 허브 색상을 갱신한다.
- [x] `requirements.css`에 색상맵을 반영해 `pages/*.html` 문서 페이지 색상을 갱신한다.
- [x] 타이틀/본문은 `Dark Charcoal`, 로고/강조는 `Main Orange`, 소제목은 `Muted Brown`, 카드 배경은 `Card Peach` 기준으로 사용처를 분리한다.
- [ ] 카드, 표, 사이드바, TOC active 상태, code 스타일의 대비를 확인한다.
- [ ] 브라우저에서 `index.html`과 대표 문서 페이지를 열어 색상 적용 상태를 검증한다.
- [x] `git diff`로 색상 외 의도하지 않은 변경이 없는지 확인한다.

## 검증 방법

- [ ] `index.html` 배경이 `Soft Beige` 계열로 보이는지 확인한다.
- [ ] 문서 카드 또는 정보 블록에 `Card Peach` 계열이 적용됐는지 확인한다.
- [ ] 주요 강조 요소에 `Main Orange`가 적용됐는지 확인한다.
- [ ] 제목과 본문 텍스트가 `Dark Charcoal` 기준으로 충분한 대비를 유지하는지 확인한다.
- [ ] 보조 문구와 footer 텍스트가 `Sub Text Gray`로 표시되는지 확인한다.
- [ ] 모바일 폭에서도 색상 변경으로 인한 가독성 저하가 없는지 확인한다.

## 리스크와 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 기존 녹색/골드 브랜드 톤과 새 오렌지/베이지 팔레트가 혼재됨 | 중간 | CSS 변수부터 일괄 매핑하고 직접 HEX 사용을 검색해 제거한다 |
| 카드 배경과 본문 배경의 대비가 약함 | 중간 | `Card Peach`는 카드/블록에만 제한하고 텍스트는 `Dark Charcoal`을 유지한다 |
| 강조색 과다 사용으로 문서 사이트가 산만해짐 | 낮음 | `Main Orange`는 CTA, active, 핵심 강조에만 사용한다 |
| HTML 생성물만 수정되고 기준 문서가 누락됨 | 중간 | 루트 `color-map.md`를 색상 기준 문서로 유지한다 |

## 완료 기준

- 루트 `color-map.md`가 프로젝트 색상 기준 문서로 저장되어 있다.
- `assets/css/site.css`와 `assets/css/requirements.css`에 색상맵 반영 계획이 명확히 정의되어 있다.
- 향후 실제 적용 시 `index.html`과 `pages/*.html`에서 동일한 팔레트를 사용하도록 작업 순서가 정리되어 있다.
