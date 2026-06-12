# 로브 (Lovv) KR S3 vector index 구축안

> 문서 버전: v0.2
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-10
> 기준 보고서: `docs/08_data_preprocessing/korea_data_preprocessing_result_report.md`
> 기준 저장소: `TourKoreaDomainData`, `s3://lovv-data-pipeline-dev-925273580929/raw/KR/details/20260609/*.json`
> 관련 문서: `docs/08_data_preprocessing/data_preprocessing_plan.md`, `docs/04_database_design/04_database_design.md`, `docs/05_agent_spec/05_agent_spec.md`

# 1. 목적

본 문서는 한국 데이터 전처리 결과보고서 기준으로, 추천 검색과 RAG 후보 생성을 위한 S3 vector index를 생성하는 기준을 정의한다.

S3 vector index는 원본 저장소가 아니다. 정본은 S3 Raw와 DynamoDB `TourKoreaDomainData`이며, S3 vector index는 정규화된 도메인 데이터를 chunk와 embedding으로 복제한 파생 검색 인덱스다. 장애 복구, 모델 변경, metadata 변경, 품질 기준 변경 시 S3 Raw와 DynamoDB 기준으로 전체 재생성한다.

# 2. 입력 기준

## 2.1 전처리 완료 상태 (결과보고서 기준)

| 항목 | 값 |
| --- | --- |
| Raw S3 prefix | `raw/KR/details/20260609/` |
| 처리 도시 수 | 40 (강원도, 경상북도) |
| Lambda | `kr-domain-loader` |
| DynamoDB table | `TourKoreaDomainData` (GSI1, GSI2, GSI3 모두 `ACTIVE`) |
| 최종 DynamoDB item 수 | 4,334 |
| 성공/부분 성공/실패 파일 수 | 40 / 0 / 0 |
| 단위 테스트 | 18 passed (전처리 전용·부분 실패 경로 포함) |
| legacy `TourKoreaData` | Terraform·AWS에서 제거 완료 |

## 2.2 식별자 기준 (실데이터 확정)

`city_id`는 실제 적재 데이터 기준 `KR-{CityNameEn}` 형식을 사용한다. 예: `KR-Andong`, `KR-Gangneung`.

이는 `transform.py`의 `_build_city_id` 폴백 경로로 생성된 값이며, raw meta에 도 코드가 없어 40개 도시 전체가 이 형식으로 적재되었음을 확인했다. 과거 설계 문서의 `KR-GB-ANDONG` 형식(도 코드 포함)은 사용하지 않는다. 추후 도 코드 포함 형식으로 전환하는 경우 전처리 수정, DynamoDB 재적재, vector index 전체 재색인이 함께 필요하다.

도/광역 구분은 `city_id`에 넣지 않고 별도 `province` metadata로 둔다. 값은 DynamoDB GSI2 키와 동일한 한글 표기(`강원도`, `경상북도`)를 사용한다.

## 2.3 S3 vector 생성 대상

| entity type | 포함 여부 | 생성 문서 |
| --- | --- | --- |
| `city_metadata` | 포함 | 도시 요약, 행정구역, 좌표, 추천 월, 대표 테마 |
| `attraction` | 포함 | 장소 요약, 테마, 운영정보, 위치, 추천 이유 |
| `restaurant` | 포함 | 음식점 요약, 음식 카테고리, 대표 메뉴, 영업정보 |
| `festival` | 포함 | 축제 요약, 개최 기간, 장소, 계절 태그 |
| `visitor_statistics` | 제한 포함 | 도시별 월간 방문 패턴 요약. 개별 통계값 전체를 벡터화하지 않고 city chunk의 보조 문맥으로만 사용 |

대상 수량 추정 (신뢰도: 중간 — 안동 기준 도시당 통계 12건 가정의 추정값이며, 정확한 분해는 GSI3 집계로 export 시 확정한다):

| 구분 | 추정 수 |
| --- | ---: |
| 전체 item | 4,334 |
| visitor_statistics (제외, 40 × 12) | 480 |
| city_metadata | 40 |
| attraction + restaurant + festival | 3,814 |
| 벡터화 대상 합계 (city 포함) | 약 3,854 |

# 3. 인덱스 구성

## 3.1 리소스 기준

| 항목 | 결정 |
| --- | --- |
| Vector bucket | `lovv-vector-dev` |
| Vector index | `kr-tour-domain-v1` |
| Embedding model | Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`) |
| Dimension | 1024 (고정) |
| Similarity metric | Cosine |
| Non-filterable keys | `raw_s3_uri`, `ddb_pk`, `ddb_sk`, `embedding_model` (index 생성 시 고정) |
| 생성 방식 | DynamoDB GSI3 기반 entity type별 query -> chunk 생성 -> embedding 생성 -> S3 vector upsert |
| 재생성 방식 | index version을 올려 신규 index 생성 후 라우팅 전환 |

dimension, metric, non-filterable key 목록은 index 생성 후 변경할 수 없으므로 v1 생성 전에 본 표 기준으로 고정한다.

## 3.2 원천 읽기 방식

결과보고서 기준 `TourKoreaDomainData`는 GSI 3종을 제공한다. 전체 scan 대신 GSI를 사용한다.

| 읽기 목적 | 방식 |
| --- | --- |
| entity type별 export | GSI3 (entity type 기준 전체 조회) query |
| 도시 단위 부분 재색인 | `PK = CITY#{city_name_en}` query |
| 도 단위 검증·집계 | GSI2 (`PROVINCE#{province}`) query |

## 3.3 Index layout

PoC는 단일 index로 시작한다.

```text
vector bucket: lovv-vector-dev
└── index: kr-tour-domain-v1
    ├── city chunks
    ├── attraction chunks
    ├── restaurant chunks
    └── festival chunks
```

| 확장 조건 | 분리안 |
| --- | --- |
| 국가 추가 | `jp-tour-domain-v1` 별도 index 생성 |
| 콘텐츠 유형별 질의량 편차 증가 | `kr-place-v1`, `kr-festival-v1`, `kr-restaurant-v1` 분리 |
| 고QPS 실시간 검색 필요 | S3 vector를 장기 저장 계층으로 두고 OpenSearch Serverless 연동 검토 |

# 4. Vector record 계약

## 4.1 Vector ID

데이터베이스 설계 명세서의 `source_type#source_id#chunk_no` 원칙과 동일한 3분절 형식으로 통일한다. (v0.1의 `#chunk#` 리터럴 포함 4분절 형식은 폐기)

| entity type | vector id 형식 | 예시 |
| --- | --- | --- |
| city | `city#{city_id}#{chunk_no}` | `city#KR-Andong#001` |
| attraction | `attraction#{contentid}#{chunk_no}` | `attraction#126157#001` |
| restaurant | `restaurant#{contentid}#{chunk_no}` | `restaurant#2687882#001` |
| festival | `festival#{contentid}#{chunk_no}` | `festival#4060101#001` |

## 4.2 Vector payload

```json
{
  "key": "attraction#126157#001",
  "data": {
    "float32": [0.0123, -0.0456]
  },
  "metadata": {
    "country": "KR",
    "province": "경상북도",
    "city_id": "KR-Andong",
    "city_name_en": "Andong",
    "entity_type": "attraction",
    "content_type": "attraction",
    "content_id": "126157",
    "theme_tags": ["역사·전통"],
    "season_tags": ["봄", "가을"],
    "recommended_months": [4, 5, 10],
    "latitude": 36.539,
    "longitude": 128.731,
    "quality_status": "passed",
    "source_type": "tourapi",
    "index_version": "kr-tour-domain-v1",
    "raw_s3_uri": "s3://lovv-data-pipeline-dev-925273580929/raw/KR/details/20260609/Andong.json",
    "ddb_pk": "CITY#Andong",
    "ddb_sk": "ATTRACTION#126157",
    "embedding_model": "amazon.titan-embed-text-v2"
  }
}
```

## 4.3 Filterable metadata

S3 vector metadata는 filterable 2KB, 키 수 제한(vector당 최대 50, non-filterable은 index당 최대 10)을 고려해 짧고 안정적인 값만 둔다.

| metadata | 타입 | 필터 사용 | 설명 |
| --- | --- | --- | --- |
| `country` | string | 예 | `KR` |
| `province` | string | 예 | `강원도`, `경상북도`. GSI2 표기와 동일 |
| `city_id` | string | 예 | `KR-{CityNameEn}` 실데이터 형식 |
| `city_name_en` | string | 예 | DynamoDB PK 역조회 보조 |
| `entity_type` | string | 예 | `city`, `attraction`, `restaurant`, `festival` |
| `content_type` | string | 예 | UI/API 노출 유형 |
| `content_id` | string | 예 | TourAPI contentid |
| `theme_tags` | list | 예 | 6대 테마 기반 필터 |
| `season_tags` | list | 예 | 계절 필터 |
| `recommended_months` | list | 예 | 여행 월 필터. festival은 원천 `visit_months`를 이 키로 매핑 |
| `latitude` / `longitude` | number | 예 | DB 설계 명세서 3.4절 필수 metadata. 거리 기반 후처리용 |
| `quality_status` | string | 예 | `passed`만 검색 노출 |
| `source_type` | string | 예 | `tourapi`, `manual`, `derived` |
| `index_version` | string | 예 | 라우팅 및 검증 |
| `raw_s3_uri` | string | 아니오 | 추적용 |
| `ddb_pk` / `ddb_sk` | string | 아니오 | DynamoDB 역조회 |
| `embedding_model` | string | 아니오 | 재색인 추적 |

사용자 ID, 대화 전문, 비공개 운영 메모는 metadata와 chunk text에 저장하지 않는다.

# 5. Chunk 생성 규칙

## 5.1 공통 원칙

- 외부 원문을 그대로 복제하지 않고 내부 요약문과 구조화 필드 중심으로 문서를 만든다.
- 하나의 vector chunk는 하나의 검색 의도에 대응하도록 짧게 유지한다.
- item 1개당 기본 1 chunk. city는 대표 관광지·축제 요약을 포함해 1~3 chunk.
- `quality_status = passed` 또는 서비스 노출 가능한 상태만 index에 반영한다.
- 방문 통계는 개별 월별 item이 아니라 city chunk의 혼잡도·계절성·월별 방문 패턴 설명에 녹인다.

## 5.2 Entity별 chunk 템플릿

### City

```text
[도시] {city_name_ko}({city_name_en})는 {province}의 소도시다.
대표 테마는 {theme_tags}이며 추천 월은 {recommended_months}이다.
방문 통계 기준 {visitor_summary} 경향을 보인다.
대표 관광지/축제: {top_attractions_and_festivals}.
```

### Attraction

```text
[관광지] {title}은 {city_name_ko}의 {theme_tags} 테마 장소다.
주소는 {address}이며 운영 정보는 {opening_hours}이다.
추천 포인트: {description_summary}
계절 태그: {season_tags}, 추천 월: {recommended_months}
```

### Restaurant

```text
[음식점] {title}은 {city_name_ko}의 {restaurant_category} 음식점이다.
주소는 {address}이다.
대표 메뉴/음식 태그: {signature_menu_or_cuisine_tags}
운영 정보: {opening_hours}, 휴무: {closed_days}
추천 포인트: {description_summary}
```

### Festival

```text
[축제] {title}은 {city_name_ko}에서 열리는 {theme_tags} 축제다.
기간은 {event_start_date}부터 {event_end_date}까지이며 장소는 {venue}이다.
계절 태그: {season_tags}, 추천 월: {visit_months}
주요 내용: {description_summary}
```

# 6. 생성 파이프라인

## 6.1 처리 흐름

```text
TourKoreaDomainData GSI3 entity type별 query
↓
chunk 생성 (entity별 템플릿)
↓
embedding 생성 (Titan V2, 1024)
↓
PutVectors batch upsert (≤500)
↓
샘플 QueryVectors 검증
↓
index manifest와 품질 리포트 저장
```

## 6.2 배치 단위

| 단계 | 기준 |
| --- | --- |
| DynamoDB 읽기 | GSI3 entity type별 query, 부분 재색인은 `PK = CITY#{city_name_en}` |
| chunk 생성 | item 1개당 기본 1 chunk, city는 1~3 chunk |
| embedding batch | 모델 API 제한에 맞춰 16~64 texts 단위 |
| PutVectors batch | 최대 500 vectors. index당 쓰기 처리량(초당 요청 1,000 / 벡터 2,500) 이내 |
| 실패 격리 | embedding 실패, metadata 초과, PutVectors 실패를 `failed/KR/s3-vector/{yyyymmdd}/`에 기록 |

PutVectors는 batch 단위 원자성이 없으므로 실패 시 batch 단위 재시도하고, 반복 실패 레코드만 실패 리포트로 분리한다.

## 6.3 산출물

| 산출물 | 위치 |
| --- | --- |
| chunk JSONL | `processed/KR/s3-vector/chunks/{yyyymmdd}/chunks.jsonl` |
| embedding JSONL | `processed/KR/s3-vector/embeddings/{yyyymmdd}/embeddings.jsonl` |
| index manifest | `processed/KR/s3-vector/manifests/{yyyymmdd}/kr-tour-domain-v1.json` |
| 품질 리포트 | `quality/KR/s3-vector/{yyyymmdd}/summary.json` |
| 실패 리포트 | `failed/KR/s3-vector/{yyyymmdd}/failed_records.jsonl` |

결과보고서의 남은 이슈(ingest manifest가 적재 이력을 완전히 대표하지 못함)를 고려해, index manifest에는 entity type별 원천 수·chunk 수·vector 성공 수와 원천 조회 시각(GSI3 query 기준)을 함께 기록해 색인 시점 스냅샷을 자체 보존한다.

# 7. 검증 기준

## 7.1 수량 검증

| 검증 | 기준 |
| --- | --- |
| DynamoDB 원천 수 | 전체 4,334 items. GSI3 집계로 entity type별 분해 확정 |
| index 대상 제외 | `visitor_statistics`(약 480), 검색 비노출 상태 제외 |
| chunk 수 | entity type별 생성 수를 manifest에 기록 |
| vector 수 | chunk 수와 PutVectors 성공 수 일치 |
| 실패 수 | 0 목표. 실패 시 원천 item ID와 사유 기록 |

## 7.2 검색 검증

| 질의 | 기대 |
| --- | --- |
| `안동 역사 여행` | `city_id = KR-Andong`, 역사·전통 관광지 우선 |
| `가을 축제 있는 조용한 도시` | `entity_type = festival`, `season_tags` 가을, city 후보 반환 |
| `강릉 바다 카페와 해안 산책` | 강릉(`KR-Gangneung`), 바다·해안, 음식점/관광지 혼합 반환 |
| `봄에 걷기 좋은 자연 여행` | `recommended_months` 3~5, 자연·트레킹 관광지 우선 |

검색 결과는 S3 vector 결과만으로 확정하지 않는다. Retriever(`Candidate_Evidence_Agent`)는 S3 vector 결과의 `ddb_pk`/`ddb_sk`로 `TourKoreaDomainData`를 재조회해 운영 여부, 축제 날짜, 품질 상태를 다시 확인한다.

# 8. 운영 정책

| 항목 | 정책 |
| --- | --- |
| 전체 재색인 | embedding model, chunk template, metadata schema, 품질 기준, `city_id` 형식 변경 시 수행 |
| 부분 재색인 | 특정 `city_id`, `entity_type`, `content_id` 변경 시 해당 vector id prefix 삭제 후 재생성 |
| 버전 전환 | `kr-tour-domain-v2` 신규 생성 후 샘플 검증 통과 시 Retriever 설정 전환 |
| 롤백 | 이전 index version을 유지하고 라우팅만 되돌림 |
| 보존 | S3 vector는 TTL 없음. manifest와 품질 리포트 보존 |
| 권한 | `s3vectors:*` 권한은 index writer Lambda와 Retriever 역할로 분리 |

# 9. 구현 체크리스트

- [ ] GSI3 기반 entity type별 export 함수를 만들고 entity별 수량을 집계한다 (2.3 추정값 확정).
- [ ] `city`, `attraction`, `restaurant`, `festival` chunk template을 구현한다.
- [ ] metadata allowlist와 2KB filterable metadata 예산 검사를 구현한다.
- [ ] `lovv-vector-dev` bucket과 `kr-tour-domain-v1` index를 1024/cosine/non-filterable 4종으로 생성한다.
- [ ] PutVectors batch upsert와 batch 단위 재시도·실패 격리 로직을 구현한다.
- [ ] `quality/KR/s3-vector/.../summary.json`에 원천 수, chunk 수, vector 성공 수, 실패 수를 기록한다.
- [ ] Retriever가 S3 vector 결과를 `ddb_pk`/`ddb_sk`로 DynamoDB 재검증하도록 연결한다.
- [ ] 샘플 질의 4종의 Top-K 결과를 검증 리포트로 남긴다.

# 10. AWS 공식 제약 참고

본 문서는 2026-06-10 기준 AWS 공식 문서를 확인해 작성했다. 주요 제한: index당 최대 2B vectors, vector dimension 1~4,096, vector당 metadata 40KB(키 최대 50), filterable metadata 2KB, non-filterable key index당 최대 10, PutVectors/DeleteVectors 1회 최대 500 vectors, index당 쓰기 초당 요청 1,000·벡터 2,500, QueryVectors Top-K 최대 100. IAM은 `s3vectors` namespace를 사용한다.

참고:

- AWS S3 Vectors 소개: https://aws.amazon.com/s3/features/vectors/
- AWS S3 Vectors User Guide: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html
- AWS S3 Vectors limitations: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-limitations.html

# 11. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.3 | 2026-06-11 | 조동휘 | Candidate_Evidence_Agent v0.1 rich embedding_text 요구 대조(`docs/98_prd/s3_vector_index_prd.md`)에 따라 restaurant chunk 템플릿에 주소 추가 |
| v0.2 | 2026-06-10 | 조동휘 | 한국 데이터 전처리 결과보고서 기준 갱신: `city_id` 실데이터(`KR-Andong`) 확정, GSI3 기반 export, `province`·좌표 metadata 추가, vector ID를 DB 설계와 동일한 3분절로 통일, Titan V2 1024/cosine 고정, 쓰기 처리량·키 수 제약 반영 |
| v0.1 | 2026-06-10 | 조동휘 | KR 전처리 완료 보고서 기준으로 `TourKoreaDomainData` -> S3 vector index 생성 계약, chunk template, metadata filter, 재색인/검증 기준 작성 |
