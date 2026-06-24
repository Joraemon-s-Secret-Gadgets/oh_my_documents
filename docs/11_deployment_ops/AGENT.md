# Agent Instructions for deployment & operations

이 폴더는 로브(Lovv) 배포·운영 가이드를 관리한다.

## Primary Document

대표 문서는 `11_deployment_ops.md`다. 배포 파이프라인, 환경 구성, 운영 절차(runbook)를 정의한다. 인프라의 "왜"는 기술 명세서(06)에 두고, 이 문서는 "어떻게 배포·운영하는가"에 집중한다.
## Representative Document Flow

- `11_deployment_ops.md` is the integrated representative document for this folder.
- `sections/*.md` is the editing source for `11_deployment_ops.md`.
- When changing representative document body content, edit the matching `sections/*.md` file first, then regenerate or update `11_deployment_ops.md` in the same change.
- `supplemental/*.md` stores supporting notes, rationale, drafts, and detailed references for this folder.
- Do not keep supplemental Markdown documents at this folder root.
- Do not create an `index.md` file in this folder.

## Documents

```text
11_deployment_ops.md  배포·운영 대표 문서
supplemental/troubleshooting.md    프로젝트 진행 중 발생한 주요 이슈와 대응 기준
```

## Scope Boundary (06 vs 11)

- `../06_technical_spec/06_technical_spec.md` (설계): AWS 서비스 선택 근거, Lambda 분리 기준, 권한 경계 원칙, 데이터 계층 구조(S3 vector / Lambda 관계 탐색 / DynamoDB / Bedrock).
- `11_deployment_ops.md` (운영): SAM build/deploy 절차, CI/CD 파이프라인, 환경별(dev/stg/prod) 설정, Secrets 관리 운영, 모니터링·알람 구성, 롤백, 비용 관리.

## Dependencies

- 기술 명세(인프라 설계): `../06_technical_spec/06_technical_spec.md`
- API 계약: `../07_api_spec/07_api_spec.md`
- 데이터 전처리 파이프라인: `../08_data_preprocessing/`

## Editing Rules

- 06과 중복되는 설계 결정은 다시 적지 않고 06을 참조한다. 운영 절차만 이 문서에 작성한다.
- 환경 변수·시크릿은 실제 값이 아니라 관리 방식만 기술한다.
- 같은 폴더 안에 보조 Markdown을 추가해 초안·근거를 먼저 작성하고, Agent가 검토해 대표 문서에 반영한다.
- 문서 버전, 문서 상태(Draft/Review/Complete), 기준 문서를 상단 메타데이터에 유지한다.
