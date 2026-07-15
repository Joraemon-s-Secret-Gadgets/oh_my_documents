# 13. 본 문서 반영 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.9 | 2026-07-03 | 로브 기획팀 | KR V2 운영 기준으로 DynamoDB/Vector 절 보강: `raw/KR/details/20260629/`, `TourKoreaDomainDataV2`, `kr-tour-domain-v2`, 8,010 DDB items, 7,606 unique vectors, V1 문서는 보조 자료로만 사용하도록 명시 |
| v0.8 | 2026-06-11 | 조동휘 | `supplemental/s3_vector_index_plan.md` v0.2 동기화: `city_id` 실데이터 형식(`KR-{CityNameEn}`) 확정, vector ID 3분절 통일, Titan V2 1024/cosine 고정, GSI3 기반 export, `province`·좌표 metadata 추가, `visitor_statistics` 제외 기준 명시 |
| v0.7 | 2026-06-10 | 조동휘 | 과거 V1 기준의 S3 vector index 생성 기준(`TourKoreaDomainData` 입력, `kr-tour-domain-v1`, metadata filter, 재생성 조건) 반영. 현재 운영 판단에는 v0.9의 V2 기준을 우선 적용 |
| v0.6 | 2026-06-09 | 조동휘 | `tour-api-korea` 코드 대조로 한국 식별자 규칙 정정: City `KR-{GW 또는 GB}-*`, Attraction `ATT-{contentid}`, Festival `FEST-{contentid}`. 상세는 `supplemental/kr_preprocessing_detail_design.md` v0.3·`supplemental/kr_preprocessing_code_based_design.md` 참조 |
| v0.5 | 2026-06-07 | LLM 파트 | VisitorStatistics 관계, 정규화 산출물, DynamoDB 후보 테이블, 적재 조건 보완 |
| v0.4 | 2026-06-06 | LLM 파트 | 한국 강원·경북 실제 수집 산출물, `KR-{도_코드}-{CITY_EN}` ID 형식, `climate_table` 전처리 기준 반영 |
| v0.3 | 2026-06-06 | LLM 파트 | S3 Raw 누적 보관 후 Lambda 배치 전처리 및 DynamoDB 적재 흐름 반영 |
| v0.2 | 2026-06-03 | LLM 파트 | S3 Raw 적재, Lambda 전처리, DynamoDB 적재 아키텍처 반영 |
| v0.1 | 2026-06-03 | LLM 파트 | 데이터 수집 계획서를 기반으로 전처리 계획서 초안 작성 |
