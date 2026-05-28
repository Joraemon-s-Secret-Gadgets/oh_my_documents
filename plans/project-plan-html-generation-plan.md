# 00 프로젝트 기획서 HTML 생성 계획

## 목적

`docs/00_project_plan/00_project_plan.md` 원본 Markdown을 GitHub Pages에서 공유 가능한 HTML 문서로 생성한다.

생성 산출물은 `pages/00_project_plan.html`로 둔다. 기존 `pages/01_requirements.html`의 문서 레이아웃, 사이드바, 표 스타일, 인쇄 버튼, 공통 CSS를 재사용해 문서 사이트의 시각적 일관성을 유지한다.

## 입력 문서

- 원본: `docs/00_project_plan/00_project_plan.md`
- 생성 대상: `pages/00_project_plan.html`
- 필요 시 문서 허브 갱신: `index.html`

## 적용 원칙

- Markdown 원본의 의미 구조를 HTML에 그대로 반영한다.
- HTML은 공유·인쇄용 산출물로 보고, 본문 내용 수정은 Markdown 원본에서 먼저 한다.
- 기존 요구사항 정의서 HTML의 디자인 톤을 재사용한다.
- 프로젝트 기획서는 요구사항 정의서보다 앞선 문서이므로 문서 번호는 `00`으로 둔다.
- 표, 목록, 변경 이력은 원본과 같은 순서로 유지한다.

## 작업 범위

### 1. HTML 파일 생성

- `pages/00_project_plan.html`을 새로 만든다.
- `<title>`은 `로브 (Lovv) — 프로젝트 기획서 v0.1`로 둔다.
- 사이드바 버전 표기는 `Project Plan · v0.1`로 둔다.
- 표지 라벨은 `Project Planning Document`로 둔다.
- 문서 상태는 `기획 초안 (Draft)`로 둔다.

### 2. 사이드바 목차 구성

`00_project_plan.md`의 1~14장 구조를 기준으로 목차를 구성한다.

| 섹션 | 목차 항목 |
| --- | --- |
| 표지 | 표지 / 문서 정보 |
| 1 | 프로젝트 개요 |
| 2 | 문제 정의 |
| 3 | 프로젝트 목표 |
| 4 | 서비스 개념 |
| 5 | 주요 사용자 및 이해관계자 |
| 6 | 프로젝트 범위 |
| 7 | 기능 구성 |
| 8 | 데이터 및 외부 연동 |
| 9 | 기술 방향 |
| 10 | 추진 일정 |
| 11 | 기대 효과 |
| 12 | 리스크 및 대응 |
| 13 | 후속 문서 |
| 14 | 변경 이력 |

### 3. 본문 변환

- Markdown의 `#` 섹션은 HTML의 `.doc-section` 단위로 변환한다.
- 최상위 장 제목은 `h1.s-h1`로 둔다.
- 하위 제목은 `h2.s-h2`로 둔다.
- 문단은 `p.doc-p`로 둔다.
- 목록은 `ul.bullet-list` 또는 `ol.bullet-list`로 둔다.
- 표는 기존 `info-tbl` 또는 `req-tbl` 스타일을 사용한다.

### 4. 프로젝트 기획서용 표현 조정

요구사항 정의서의 문구를 그대로 복사하지 않고, 기획서 성격에 맞게 다음 표현을 유지한다.

- `요구사항 정의서`가 아니라 `프로젝트 기획서`
- `기획 초안 (Draft)`
- `PoC 및 Production 기획`
- P5는 상세 요구기능이 아니라 추진 범위 기록 항목
- 소도시는 인구수 기준이 아니라 관광지 방문객 수 기준
- 국가와 여행 시기를 먼저 입력받고 이후 자연어 취향을 반영하는 흐름

### 5. 문서 허브 반영

`index.html`에 프로젝트 기획서 링크를 추가한다.

수정 방향:

- 요구사항 정의서 섹션 위에 `프로젝트 기획서` 섹션을 추가한다.
- 링크 대상은 `./pages/00_project_plan.html`로 둔다.
- 카드 제목은 `로브 (Lovv) — 프로젝트 기획서 v0.1`로 둔다.
- 설명은 `프로젝트 배경, 목표, 범위, 우선순위, 추진 일정을 정리한 기획 문서입니다.`로 둔다.

## 작업 순서

1. `docs/00_project_plan/00_project_plan.md`의 최신 내용을 확인한다.
2. `pages/01_requirements.html`의 레이아웃과 공통 클래스를 기준으로 HTML 골격을 만든다.
3. 표지, 사이드바, 목차를 `00_project_plan` 구조에 맞춘다.
4. Markdown 본문을 HTML 섹션으로 변환한다.
5. 표와 목록의 구조가 깨지지 않았는지 확인한다.
6. `index.html`에 `00_project_plan.html` 링크를 추가한다.
7. 브라우저에서 열었을 때 표와 문단이 잘리는 부분이 없는지 확인한다.

## 검증 기준

- `pages/00_project_plan.html`이 생성되어 있다.
- `index.html`에서 프로젝트 기획서로 이동할 수 있다.
- HTML 제목, 표지, 사이드바가 프로젝트 기획서 기준으로 표시된다.
- 1~14장 본문이 누락 없이 포함되어 있다.
- 표가 깨지지 않고 기존 문서 스타일과 같은 톤으로 보인다.
- `docs/00_project_plan/00_project_plan.md`의 주요 문구와 HTML 본문 의미가 일치한다.

## 검증 명령

```powershell
rg -n "프로젝트 기획서|Project Planning Document|Project Plan|s14|변경 이력" pages/00_project_plan.html index.html
```

```powershell
rg -n "국가와 여행 시기|방문객 수|P5|지역 문화 체험|미디어 촬영지" docs/00_project_plan/00_project_plan.md pages/00_project_plan.html
```

```powershell
git diff --check
```

## 완료 기준

- Markdown 원본과 HTML 산출물이 함께 존재한다.
- 문서 허브에서 00 프로젝트 기획서와 01 요구사항 정의서를 모두 접근할 수 있다.
- HTML 산출물은 기존 요구사항 정의서와 같은 문서 디자인 시스템을 사용한다.
- 원본 Markdown의 주요 내용이 HTML에 누락 없이 반영되어 있다.

## 주의 사항

- 이번 작업은 HTML 산출물 생성 계획이며, 요구사항 내용 자체를 추가 변경하지 않는다.
- `pages/01_requirements.html`은 참조만 하고 직접 수정하지 않는다.
- 기존 `requirements.css`를 우선 재사용하고, 새 CSS 파일은 필요할 때만 만든다.
