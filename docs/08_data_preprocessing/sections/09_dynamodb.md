# 9. DynamoDB 저장 및 적재 기준

## 9.1 저장 계층

| 계층 | 저장 내용 | 용도 |
| --- | --- | --- |
| S3 Raw Bucket | 원본 응답, 추출 원문, 수집 메타데이터 | 재처리·감사·오류 추적 |
| DynamoDB Normalized Tables | City, Attraction, Festival, VisitorStatistics, 검수 상태 | 서비스 조회 |
| Search Index | 검색 문서, 임베딩 대상 텍스트, 키워드 | RAG·검색 |
| DynamoDB Review Table | 검수 큐, 검수 결과, 승인·반려 이력 | 운영 관리 |

## 9.2 DynamoDB 테이블 후보

| 테이블 | Partition Key | Sort Key | 저장 내용 |
| --- | --- | --- | --- |
| `LovvCity` | `country_code` | `city_id` | 국가별 City 정규화 데이터 |
| `LovvAttraction` | `city_id` | `attraction_id` | City에 속한 Attraction 정규화 데이터 |
| `LovvFestival` | `city_id` | `festival_id` | City에 속한 Festival 정규화 데이터 |
| `LovvVisitorStats` | `city_id` | `stat_period` | City에 연결된 월별 또는 지역별 방문·관광 통계 |
| `LovvDataQuality` | `entity_id` | `checked_at` | 품질 검증 결과, 신뢰도, 실패 사유 |
| `LovvReviewQueue` | `queue_name` | `entity_id` | 수동 검수 대상과 처리 상태 |

## 9.3 Item 공통 속성

| 속성 | 설명 |
| --- | --- |
| `entity_id` | City, Attraction, Festival, VisitorStatistics의 안정 식별자 |
| `entity_type` | `city`, `attraction`, `festival`, `visitor_statistics` |
| `country_code` | `KR` 또는 `JP` |
| `source_name` | 원본 출처명 |
| `source_url` | 원본 또는 공식 확인 URL |
| `s3_raw_uri` | 재처리를 위한 S3 Raw 객체 경로 |
| `normalized_payload` | 서비스 조회용 정규화 데이터 |
| `quality_status` | `collected`, `needs_review`, `missing`, `blocked` |
| `data_confidence` | 출처, 최신성, 필드 충족률 기반 신뢰도 |
| `collected_at` | 원본 수집 시각 |
| `processed_at` | Lambda 처리 시각 |
| `verified_at` | 공식 확인 또는 수동 검수 시각 |

## 9.4 적재 조건

| 대상 | 최소 적재 조건 |
| --- | --- |
| City | 표준 ID, 도시명, 국가, 행정구역, 출처 URL |
| Attraction | 표준 ID, 이름, City 매핑, 출처 URL, 주소 또는 좌표 |
| Festival | 표준 ID, 이름, City 매핑, 기간 원문 또는 개최 월, 출처 URL |
| VisitorStatistics | 표준 ID, City 매핑, 집계 기간, 지표명, 수치, 출처 URL |
| 검색 문서 | 내부 요약문, 출처 링크, 최신성 상태 |
| 서비스 노출 | 필수 필드 충족, 저작권 위험 없음, `blocked` 아님 |

## 9.5 DynamoDB V2 및 S3 Vector V2 생성 기준

Search Index는 DynamoDB 정규화 결과에서 파생되는 S3 vector index를 기준으로 한다. S3 vector index는 원본 저장소가 아니며, S3 Raw와 DynamoDB 정규화 문서를 기준으로 언제든 재생성할 수 있어야 한다.

KR 상세 데이터의 현재 운영 기준은 V2이다. 기준 원천은 `raw/KR/details/20260629/`이고, `kr-pipeline-transform`이 생성한 `processed/KR/details/20260629/passed/` 산출물만 DynamoDB V2 적재와 vector rebuild 입력으로 사용한다. 현재 완료 판단은 `supplemental/kr_20260630_preprocessing_completion_report.md`를 우선한다.

DynamoDB source of truth는 `TourKoreaDomainDataV2`이다. Entity type은 `city_metadata`, `attraction`, `festival`, `visitor_statistics`를 기준으로 하며, 현재 V2 운영 계약에서는 `restaurant`를 활성 entity로 복원하지 않는다.

S3 Vector V2는 `lovv-vector-dev` bucket 안의 `kr-tour-domain-v2` index를 사용한다. Vector 생성 대상은 `city_metadata`, `attraction`, `festival`이며, `visitor_statistics`는 DynamoDB에는 적재하지만 개별 vector 대상에서는 제외한다. `visitor_statistics`는 city 문맥의 계절성·혼잡도 보조 정보로만 활용한다.

2026-06-30 완료 보고서 기준 현재 V2 검증 결과는 다음과 같다.

| 항목 | 값 |
| --- | ---: |
| 전처리 대상 raw detail | 240개 |
| `kr-pipeline-transform` 성공 | 240개 |
| DynamoDB V2 live item | 8,010건 |
| Vector export 대상 | 7,662건 |
| S3 Vector V2 unique key | 7,606개 |
| Vector sample query | 성공 |
| Vector manifest 작성 | 완료 |

| 항목 | 기준 |
| --- | --- |
| Vector bucket | `lovv-vector-dev` |
| Vector index | `kr-tour-domain-v2` |
| DynamoDB table | `TourKoreaDomainDataV2` |
| Embedding | Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`), 1024 차원, cosine 고정 |
| Vector ID | `{source_type}#{source_id}#{chunk_no}` 3분절. 예: `attraction#126157#001` |
| 원천 읽기 | `EntityTypeDomainIndex` entity type별 query, 부분 재색인은 `PK = CITY#{CITY_KEY}` query |
| Metadata filter | `country`, `province`, `city_id`, `city_name_en`, `entity_type`, `content_type`, `content_id`, `theme_tags`, `season_tags`, `recommended_months`, `latitude`/`longitude`, `quality_status`, `source_type`, `index_version` |
| 원본 재조회 | S3 vector 결과의 `ddb_pk`, `ddb_sk`, `raw_s3_uri`로 DynamoDB와 S3 Raw를 역추적 |
| 재생성 조건 | embedding model, chunk template, metadata schema, 품질 기준, `city_id` 형식 변경 |

상세 chunk template, metadata allowlist, PutVectors 배치 기준, 샘플 질의 검증 기준은 `supplemental/kr_20260630_preprocessing_completion_report.md`, `supplemental/vector_search_v2_guide.md`, `supplemental/s3_vector_index_plan.md`를 함께 확인한다. V1 문서(`agentcore_v1_*`)는 AgentCore V1 조회 보조 자료로만 보고, 현재 데이터 전처리·적재 판단의 기준으로 사용하지 않는다.

## 9.6 Lambda 적재 실패 처리

| 실패 유형 | 처리 |
| --- | --- |
| 스키마 오류 | DynamoDB에 적재하지 않고 S3 `failed/` Prefix와 품질 리포트에 사유 기록 |
| 필수 필드 누락 | `LovvReviewQueue`에 검수 대상으로 등록 |
| DynamoDB 조건부 쓰기 실패 | 기존 Item과 충돌 여부를 확인하고 변경 이력 후보로 분류 |
| Lambda 타임아웃 | 처리 단위를 더 작은 S3 객체 또는 배치로 나누어 재시도 |
| 일시적 AWS 오류 | 재시도 후 실패 이벤트를 DLQ 또는 실패 Prefix에 보존 |
