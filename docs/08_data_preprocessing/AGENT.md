# Agent Instructions for data preprocessing

이 폴더는 로브(Lovv)의 **수집된 데이터 및 전처리 문서**를 관리한다. 데이터 수집(03)과 데이터베이스 설계(04) 사이의 ELT 전처리 단계 산출물과 설계를 담는다.

## Primary Document

대표 문서는 `data_preprocessing_plan.md`다. 한국·일본 공통 전처리 원칙과 아키텍처를 다룬다.

## Documents

```text
data_preprocessing_plan.md             전처리 대표 계획서 (공통 원칙·아키텍처)
preprocessing_budget_estimate.md       전처리 PoC 예산 산정
kr_preprocessing_detail_design.md      한국(KR) ELT 전처리 상세 설계 (설계 의도 기준)
kr_preprocessing_code_based_design.md  한국(KR) 전처리 설계 (tour-api-korea 샘플 코드 산출물 기준)
preprocessing_report.md                KR 상세 데이터 전처리 완료 보고서
korea_data_preprocessing_result_report.md  한국 데이터 전처리 결과보고서 (DynamoDB 적재 결과 확정본)
s3_vector_index_plan.md                KR 전처리 산출물 기반 S3 vector index 구축안 (기준: korea_data_preprocessing_result_report.md)
```

향후 수집된 데이터 산출물 정리 문서, 일본(JP) 상세 설계, Lambda 변환 구현 설계 등을 같은 폴더에 추가한다. 새 보조 문서를 추가할 때 대표 문서(`data_preprocessing_plan.md`)와 모순되지 않도록 동기화한다.

## Dependencies (읽기 전용 기준)

- 수집 계획서: `../03_data_collect_plan/03_data_collect_plan.md`
- 한국 실수집 기준: `../03_data_collect_plan/korea_data_acquisition_plan_updated.md`
- 적재 설계 기준: `../04_database_design/nosql_schema_design.md`
- 기술 명세서: `../06_technical_spec/06_technical_spec.md`

## Editing Rules

- ELT(Extract → Load Raw → Transform) 단계와 입출력, 변환 규칙, 품질 검증, 적재 조건을 정의한다.
- 데이터 정본은 S3로 두고 코드·문서·소량 설정만 GitHub에 둔다. 수집 산출물(>15MB 또는 데이터 성격)은 S3로 직접 적재한다.
- 수량·필드는 실수집 기준(`../03_data_collect_plan/korea_data_acquisition_plan_updated.md`)과 일치시키고, 불일치는 신뢰도와 함께 명시한다.
