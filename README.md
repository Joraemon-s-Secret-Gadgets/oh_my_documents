# oh_my_documents

GitHub Pages로 공유할 개발 문서를 관리하는 저장소입니다. 문서 원본은 Markdown으로 작성하고, Codex 같은 에이전트가 원본을 읽어 공유용 HTML 문서를 생성하는 흐름을 기준으로 운영합니다.

## 문서 운영 방식

문서는 원본과 배포 산출물을 분리합니다.

```text
docs/*.md       원본 개발 문서
index.html      GitHub Pages 첫 화면
pages/*.html    원본 Markdown을 바탕으로 생성된 공유용 HTML 문서
assets/         공통 CSS, 이미지 등 정적 리소스
plans/          문서 사이트 구축 및 운영 계획
```

수정은 항상 `docs/*.md`에서 먼저 진행합니다. `index.html`과 `pages/*.html`은 원본 Markdown을 반영해 다시 생성하는 산출물로 취급합니다.

## 개발 문서 작성 흐름

개발 문서는 아래 순서로 작성합니다.

1. **요구사항 정의서**
   프로젝트 목적, 범위, 기능 요구사항, 비기능 요구사항, 제외 범위, 우선순위를 정의합니다.

2. **사용자 시나리오 / 유저 스토리**
   사용자가 어떤 상황에서 어떤 행동을 하고 어떤 결과를 기대하는지 정리합니다.

3. **화면 흐름 / 정보 구조**
   필요한 화면, 메뉴, 페이지 이동 구조, 사이트맵을 정리합니다.

4. **시스템 아키텍처**
   프론트엔드, 백엔드, 데이터베이스, 외부 서비스, 인증 구조 등 전체 기술 구성을 설명합니다.

5. **데이터베이스 설계**
   ERD, 테이블 또는 컬렉션, 필드, 관계, 인덱스, 제약 조건을 정의합니다.

6. **API 명세서**
   엔드포인트, 요청, 응답, 에러 코드, 인증 방식을 정의합니다.

7. **UI/UX 가이드**
   화면 레이아웃, 컴포넌트 규칙, 입력/오류/빈 상태, 반응형 기준을 정리합니다.

8. **테스트 계획서**
   단위 테스트, 통합 테스트, E2E 테스트, 수동 검증 체크리스트를 정리합니다.

9. **배포 가이드**
   로컬 실행, 빌드, 환경 변수, 배포 절차, GitHub Pages 설정 방법을 정리합니다.

10. **운영 가이드**
    로그, 장애 대응, 백업, 모니터링, 정기 점검 기준을 정리합니다.

## 권장 문서 목록

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

문서 내용이 많아지면 단일 Markdown 파일 대신 폴더로 분리해도 됩니다. 이 경우 폴더 안의 `index.md`를 해당 문서의 시작점으로 사용합니다.

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

## GitHub Pages

GitHub Pages는 저장소 루트의 `index.html`을 첫 화면으로 사용합니다. `docs/`는 원본 Markdown 보관 위치로 사용하고, 공유용 HTML은 `pages/`에 생성합니다.

자세한 구축 계획은 [plans/github-pages-documents-plan.md](plans/github-pages-documents-plan.md)를 참고합니다.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
