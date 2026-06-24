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

## 9.5 S3 vector index 생성 기준

Search Index는 DynamoDB 정규화 결과에서 파생되는 S3 vector index를 기준으로 한다. S3 vector index는 원본 저장소가 아니며, S3 Raw와 DynamoDB 정규화 문서를 기준으로 언제든 재생성할 수 있어야 한다.

KR 상세 데이터의 현재 운영 기준은 `TourKoreaDomainData`이며, 한국 데이터 전처리 결과보고서(`supplemental/korea_data_preprocessing_result_report.md`) 기준 `raw/KR/details/20260609/` 40개 도시 전처리 완료 결과를 S3 vector 생성 입력으로 사용한다. 생성 대상은 `city_metadata`, `attraction`, `restaurant`, `festival`이며, `visitor_statistics`(약 480건)는 개별 벡터화 대상에서 제외하고 city chunk의 혼잡도·계절성 보조 문맥으로만 반영한다. `quality_status = passed` 등 서비스 노출 가능한 상태만 index에 반영한다.

`city_id`는 실제 적재 데이터 기준 `KR-{CityNameEn}` 형식(예: `KR-Andong`)을 사용하며, 과거 설계의 도 코드 포함 형식(`KR-GB-ANDONG`)은 사용하지 않는다. 도/광역 구분은 별도 `province` metadata(GSI2와 동일한 한글 표기)로 둔다.

| 항목 | 기준 |
| --- | --- |
| Vector bucket | `lovv-vector-dev` |
| Vector index | `kr-tour-domain-v1` |
| Embedding | Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`), 1024 차원, cosine 고정 |
| Vector ID | `{source_type}#{source_id}#{chunk_no}` 3분절. 예: `attraction#126157#001` |
| 원천 읽기 | GSI3 entity type별 query, 부분 재색인은 `PK = CITY#{city_name_en}` query |
| Metadata filter | `country`, `province`, `city_id`, `city_name_en`, `entity_type`, `content_type`, `content_id`, `theme_tags`, `season_tags`, `recommended_months`, `latitude`/`longitude`, `quality_status`, `source_type`, `index_version` |
| 원본 재조회 | S3 vector 결과의 `ddb_pk`, `ddb_sk`, `raw_s3_uri`로 DynamoDB와 S3 Raw를 역추적 |
| 재생성 조건 | embedding model, chunk template, metadata schema, 품질 기준, `city_id` 형식 변경 |

상세 chunk template, metadata allowlist, PutVectors 배치 기준, 샘플 질의 검증 기준은 `supplemental/s3_vector_index_plan.md`를 따른다.

## 9.6 Lambda 적재 실패 처리

| 실패 유형 | 처리 |
| --- | --- |
| 스키마 오류 | DynamoDB에 적재하지 않고 S3 `failed/` Prefix와 품질 리포트에 사유 기록 |
| 필수 필드 누락 | `LovvReviewQueue`에 검수 대상으로 등록 |
| DynamoDB 조건부 쓰기 실패 | 기존 Item과 충돌 여부를 확인하고 변경 이력 후보로 분류 |
| Lambda 타임아웃 | 처리 단위를 더 작은 S3 객체 또는 배치로 나누어 재시도 |
| 일시적 AWS 오류 | 재시도 후 실패 이벤트를 DLQ 또는 실패 Prefix에 보존 |
