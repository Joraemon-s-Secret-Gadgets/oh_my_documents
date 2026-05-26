# Agent Instructions

이 저장소는 GitHub Pages로 공유할 개발 문서를 관리한다. 에이전트는 Markdown 원본 문서를 기준으로 HTML 공유 문서를 생성하거나 갱신한다.

## Core Rule

수정은 항상 `docs/`의 Markdown 원본에서 먼저 진행한다.

`index.html`과 `pages/*.html`은 공유용 생성물로 취급한다. HTML을 직접 수정해야 하는 경우에도, 같은 변경이 반드시 대응하는 Markdown 원본에 반영되어 있어야 한다.

## Repository Roles

```text
docs/*.md       원본 개발 문서
docs/*/index.md 폴더형 원본 문서의 시작점
index.html      GitHub Pages 첫 화면
pages/*.html    Markdown 원본을 바탕으로 생성된 공유용 HTML 문서
assets/         공통 CSS, 이미지 등 정적 리소스
plans/          문서 사이트 구축 및 운영 계획
README.md       저장소 소개와 운영 방식 요약
```

## Document Flow

개발 문서는 아래 순서를 기본으로 한다.

1. 요구사항 정의서
2. 사용자 시나리오 / 유저 스토리
3. 화면 흐름 / 정보 구조
4. 시스템 아키텍처
5. 데이터베이스 설계
6. API 명세서
7. UI/UX 가이드
8. 테스트 계획서
9. 배포 가이드
10. 운영 가이드

## Source Document Naming

기본 문서 구조는 다음을 권장한다.

```text
docs/
├── 01_requirements.md
├── 02_user_stories.md
├── 03_information_architecture.md
├── 04_system_architecture.md
├── 05_database_design.md
├── 06_api_specification.md
├── 07_ui_ux_guidelines.md
├── 08_test_plan.md
├── 09_deployment_guide.md
└── 10_operations_guide.md
```

문서 내용이 많아지면 폴더로 분리할 수 있다. 이 경우 `index.md`를 해당 문서의 시작점으로 사용한다.

```text
docs/
├── 01_requirements/
│   ├── index.md
│   ├── functional_requirements.md
│   └── non_functional_requirements.md
└── 06_api_specification/
    ├── index.md
    ├── auth.md
    └── documents.md
```

## HTML Generation Rules

- `index.html`은 전체 문서 목차, 문서별 요약, 상태를 보여주는 GitHub Pages 첫 화면으로 생성한다.
- `pages/*.html`은 `docs/*.md` 또는 `docs/*/index.md`를 바탕으로 생성한다.
- 모든 HTML 문서는 `assets/css/site.css`를 공유한다.
- HTML 문서에는 공통 헤더, 본문, 이전/다음 문서 링크, 푸터를 포함한다.
- 생성된 HTML 링크는 모두 상대 경로를 사용한다.
- 문서 상태는 `Draft`, `Review`, `Complete` 중 하나를 사용한다.

## Verification Checklist

HTML 생성 또는 문서 구조 변경 후 다음을 확인한다.

- `docs/` 원본 문서와 `pages/` 생성 문서의 목록이 대응한다.
- `index.html`에서 모든 문서로 이동할 수 있다.
- `pages/*.html`의 이전/다음 링크가 깨지지 않는다.
- GitHub Pages 기준 상대 경로가 올바르다.
- README의 운영 방식과 실제 구조가 어긋나지 않는다.

## Reference

자세한 계획은 `plans/github-pages-documents-plan.md`를 따른다.
