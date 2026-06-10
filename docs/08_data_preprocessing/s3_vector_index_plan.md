# 로브 (Lovv) KR S3 vector index 구축안

> 문서 버전: v0.1
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-10
> 기준 보고서: `docs/08_data_preprocessing/preprocessing_report.md`
> 기준 저장소: `TourKoreaDomainData`, `s3://lovv-data-pipeline-dev-925273580929/raw/KR/details/20260609/*.json`
> 관련 문서: `docs/08_data_preprocessing/data_preprocessing_plan.md`, `docs/04_database_design/04_database_design.md`, `docs/05_agent_spec/05_agent_spec.md`

# 1. 목적

본 문서는 KR 상세 Raw 전처리 완료 결과를 기반으로, 추천 검색과 RAG 후보 생성을 위한 S3 vector index를 생성하는 기준을 정의한다.

S3 vector index는 원본 저장소가 아니다. 정본은 S3 Raw와 DynamoDB `TourKoreaDomainData`이며, S3 vector index는 정규화된 도메인 데이터를 chunk와 embedding으로 복제한 파생 검색 인덱스다. 장애 복구, 모델 변경, metadata 변경, 품질 기준 변경 시 S3 Raw와 DynamoDB 기준으로 전체 재생성한다.

# 2. 입력 기준

## 2.1 현재 전처리 완료 상태

| 항목 | 값 |
| --- | --- |
| Raw S3 prefix | `raw/KR/details/20260609/` |
| 처리 도시 수 | 40 |
| Lambda | `kr-domain-loader` |
| DynamoDB table | `TourKoreaDomainData` |
| 최종 DynamoDB item 수 | 4,334 |
| 성공 파일 수 | 40 |
| 부분 성공 파일 수 | 0 |
| 실패 파일 수 | 0 |

## 2.2 S3 vector 생성 대상

| entity type | 포함 여부 | 생성 문서 |
| --- | --- | --- |
| `city_metadata` | 포함 | 도시 요약, 행정구역, 좌표, 추천 월, 대표 테마 |
| `attraction` | 포함 | 장소 요약, 테마, 운영정보, 위치, 추천 이유 |
| `restaurant` | 포함 | 음식점 요약, 음식 카테고리, 대표 메뉴, 영업정보 |
| `festival` | 포함 | 축제 요약, 개최 기간, 장소, 계절 태그 |
| `visitor_statistics` | 제한 포함 | 도시별 월간 방문 패턴 요약. 개별 통계값 전체를 벡터화하지 않고 도시/월 보조 문맥으로 사용 |
| `review` / `failed` | 제외 | 검수 완료 전 검색 노출 금지 |

# 3. 인덱스 구성

## 3.1 리소스 기준

| 항목 | 결정 |
| --- | --- |
| Vector bucket | `lovv-vector-dev` |
| Vector index | `kr-tour-domain-v1` |
| Embedding model | Amazon Titan Text Embeddings V2 우선, Cohere Embed 계열 대안 |
| Dimension | 선택 모델의 출력 차원과 동일하게 고정 |
| Similarity metric | Cosine 기준 |
| 생성 방식 | DynamoDB scan 또는 export 결과 -> chunk 생성 -> embedding 생성 -> S3 vector upsert |
| 재생성 방식 | index version을 올려 신규 index 생성 후 라우팅 전환 |

S3 Vectors는 vector bucket 안에 vector index를 두고, 각 vector에 metadata를 붙여 필터링할 수 있다. 현재 AWS 제한 기준으로 vector index는 최대 2B vectors, vector dimension은 1~4,096, PutVectors 1회 최대 500 vectors, query Top-K 최대 100을 고려한다.

## 3.2 Index layout

PoC는 단일 index로 시작한다.

```text
vector bucket: lovv-vector-dev
└── index: kr-tour-domain-v1
    ├── city chunks
    ├── attraction chunks
    ├── restaurant chunks
    └── festival chunks
```

분리 기준은 운영 규모가 커질 때 적용한다.

| 확장 조건 | 분리안 |
| --- | --- |
| 국가 추가 | `jp-tour-domain-v1` 별도 index 생성 |
| 콘텐츠 유형별 질의량 편차 증가 | `kr-place-v1`, `kr-festival-v1`, `kr-restaurant-v1` 분리 |
| 고QPS 실시간 검색 필요 | S3 vector를 장기 저장 계층으로 두고 OpenSearch Serverless snapshot/export 연동 검토 |

# 4. Vector record 계약

## 4.1 Vector ID

Vector ID는 재생성 가능하고 원천 item과 역추적 가능해야 한다.

| entity type | vector id 형식 | 예시 |
| --- | --- | --- |
| city | `city#{city_id}#chunk#{chunk_no}` | `city#KR-GW-GANGNEUNG#chunk#001` |
| attraction | `attraction#{contentid}#chunk#{chunk_no}` | `attraction#126157#chunk#001` |
| restaurant | `restaurant#{contentid}#chunk#{chunk_no}` | `restaurant#2687882#chunk#001` |
| festival | `festival#{contentid}#chunk#{chunk_no}` | `festival#4060101#chunk#001` |

기존 DB 설계의 `source_type#source_id#chunk_no` 원칙과 호환되도록 `source_type`은 entity type으로, `source_id`는 `contentid` 또는 `city_id`로 둔다.

## 4.2 Vector payload

```json
{
  "key": "attraction#126157#chunk#001",
  "data": {
    "float32": [0.0123, -0.0456]
  },
  "metadata": {
    "country": "KR",
    "city_id": "KR-GB-ANDONG",
    "city_name_en": "Andong",
    "entity_type": "attraction",
    "content_type": "attraction",
    "content_id": "126157",
    "theme_tags": ["역사·전통"],
    "season_tags": ["봄", "가을"],
    "recommended_months": [4, 5, 10],
    "quality_status": "passed",
    "source_type": "tourapi",
    "raw_s3_uri": "s3://lovv-data-pipeline-dev-925273580929/raw/KR/details/20260609/andong.json",
    "ddb_pk": "CITY#Andong",
    "ddb_sk": "ATTRACTION#126157",
    "embedding_model": "amazon.titan-embed-text-v2",
    "index_version": "kr-tour-domain-v1"
  }
}
```

## 4.3 Filterable metadata

S3 vector metadata는 필터 크기와 키 수 제한을 고려해 짧고 안정적인 값만 둔다.

| metadata | 타입 | 필터 사용 | 설명 |
| --- | --- | --- | --- |
| `country` | string | 예 | `KR` |
| `city_id` | string | 예 | 추천 후보 도시 제한 |
| `city_name_en` | string | 예 | 운영 조회 편의 |
| `entity_type` | string | 예 | `city`, `attraction`, `restaurant`, `festival` |
| `content_type` | string | 예 | UI/API 노출 유형 |
| `content_id` | string | 예 | TourAPI contentid |
| `theme_tags` | list | 예 | 6대 테마 기반 필터 |
| `season_tags` | list | 예 | 계절 필터 |
| `recommended_months` | list | 예 | 여행 월 필터 |
| `quality_status` | string | 예 | `passed`만 검색 노출 |
| `source_type` | string | 예 | `tourapi`, `manual`, `derived` |
| `raw_s3_uri` | string | 아니오 | 추적용. filterable metadata가 커지면 non-filterable로 둔다 |
| `ddb_pk` | string | 아니오 | DynamoDB 역조회 |
| `ddb_sk` | string | 아니오 | DynamoDB 역조회 |
| `embedding_model` | string | 아니오 | 재색인 추적 |
| `index_version` | string | 예 | 라우팅 및 검증 |

사용자 ID, 대화 전문, 비공개 운영 메모는 metadata와 chunk text에 저장하지 않는다.

# 5. Chunk 생성 규칙

## 5.1 공통 원칙

- 외부 원문을 그대로 복제하지 않고 내부 요약문과 구조화 필드 중심으로 문서를 만든다.
- 하나의 vector chunk는 하나의 검색 의도에 대응하도록 짧게 유지한다.
- `review` 또는 `failed` 레코드는 index 대상에서 제외한다.
- `quality_status = passed` 또는 서비스 노출 가능한 상태만 index에 반영한다.
- 통계는 개별 월별 item 전체가 아니라 도시의 혼잡도, 계절성, 월별 방문 패턴 설명에 녹인다.

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
TourKoreaDomainData scan/export
↓
entity type별 필터링
↓
검색 chunk 생성
↓
embedding 생성
↓
PutVectors batch upsert
↓
샘플 QueryVectors 검증
↓
index manifest와 품질 리포트 저장
```

## 6.2 배치 단위

| 단계 | 기준 |
| --- | --- |
| DynamoDB 읽기 | `PK = CITY#{city_name_en}` 단위 또는 export manifest 단위 |
| chunk 생성 | item 1개당 기본 1 chunk, 도시 메타데이터는 대표 관광지/축제 요약을 포함해 1~3 chunk |
| embedding batch | 모델 API 제한에 맞춰 16~64 texts 단위 |
| PutVectors batch | S3 Vectors 제한을 고려해 최대 500 vectors 이하 |
| 실패 격리 | embedding 실패, metadata 초과, PutVectors 실패를 `failed/KR/s3-vector/{date}/`에 기록 |

## 6.3 산출물

| 산출물 | 위치 |
| --- | --- |
| chunk JSONL | `processed/KR/s3-vector/chunks/{yyyymmdd}/chunks.jsonl` |
| embedding JSONL | `processed/KR/s3-vector/embeddings/{yyyymmdd}/embeddings.jsonl` |
| index manifest | `processed/KR/s3-vector/manifests/{yyyymmdd}/kr-tour-domain-v1.json` |
| 품질 리포트 | `quality/KR/s3-vector/{yyyymmdd}/summary.json` |
| 실패 리포트 | `failed/KR/s3-vector/{yyyymmdd}/failed_records.jsonl` |

# 7. 검증 기준

## 7.1 수량 검증

| 검증 | 기준 |
| --- | --- |
| DynamoDB 원천 수 | `TourKoreaDomainData` 4,334 items |
| index 대상 제외 | `review`, `failed`, 검색 비노출 상태 제외 |
| chunk 수 | entity type별 생성 수를 manifest에 기록 |
| vector 수 | chunk 수와 PutVectors 성공 수 일치 |
| 실패 수 | 0을 목표로 하되 실패가 있으면 원천 item ID와 사유 기록 |

## 7.2 검색 검증

| 질의 | 기대 |
| --- | --- |
| `안동 역사 여행` | `city_id = KR-GB-ANDONG`, 역사·전통 관광지 우선 |
| `가을 축제 있는 조용한 도시` | `entity_type = festival`, `season_tags` 가을, city 후보 반환 |
| `강릉 바다 카페와 해안 산책` | 강릉, 바다·해안, 음식점/관광지 혼합 반환 |
| `봄에 걷기 좋은 자연 여행` | `recommended_months` 3~5, 자연·트레킹 관광지 우선 |

검색 결과는 S3 vector 결과만으로 확정하지 않는다. Retriever는 S3 vector 결과의 `ddb_pk`/`ddb_sk`로 `TourKoreaDomainData`를 재조회해 운영 여부, 축제 날짜, 품질 상태를 다시 확인한다.

# 8. 운영 정책

| 항목 | 정책 |
| --- | --- |
| 전체 재색인 | embedding model, chunk template, metadata schema, 품질 기준 변경 시 수행 |
| 부분 재색인 | 특정 `city_id`, `entity_type`, `content_id` 변경 시 해당 vector id prefix 삭제 후 재생성 |
| 버전 전환 | `kr-tour-domain-v2` 신규 생성 후 샘플 검증 통과 시 Retriever 설정 전환 |
| 롤백 | 이전 index version을 유지하고 라우팅만 되돌림 |
| 보존 | S3 vector는 TTL 없음. 원본 재생성 가능성을 위해 manifest와 품질 리포트 보존 |
| 권한 | `s3vectors:*` 권한은 index writer Lambda와 Retriever 역할로 분리 |

# 9. 구현 체크리스트

- [ ] `TourKoreaDomainData`에서 `passed` 대상 item을 entity type별로 읽는 export/scan 함수를 만든다.
- [ ] `city`, `attraction`, `restaurant`, `festival` chunk template을 구현한다.
- [ ] metadata allowlist와 2KB filterable metadata 예산 검사를 구현한다.
- [ ] embedding model과 dimension을 확정하고 index 생성 설정에 고정한다.
- [ ] PutVectors batch upsert와 실패 격리 로직을 구현한다.
- [ ] `quality/KR/s3-vector/.../summary.json`에 원천 수, chunk 수, vector 성공 수, 실패 수를 기록한다.
- [ ] Retriever가 S3 vector 결과를 DynamoDB `TourKoreaDomainData`로 재검증하도록 연결한다.
- [ ] 샘플 질의 4종의 Top-K 결과를 검증 리포트로 남긴다.

# 10. AWS 공식 제약 참고

본 문서는 2026-06-10 기준 AWS 공식 문서를 확인해 작성했다. S3 Vectors는 vector bucket, vector index, vector, metadata filter로 구성되며, IAM 정책은 `s3vectors` namespace를 사용한다. 주요 제한은 index당 최대 2B vectors, vector dimension 1~4,096, vector당 metadata 40KB, filterable metadata 2KB, PutVectors 1회 최대 500 vectors, QueryVectors Top-K 최대 100이다.

참고:

- AWS S3 Vectors 소개: https://aws.amazon.com/s3/features/vectors/
- AWS S3 Vectors User Guide: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html
- AWS S3 Vectors limitations: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-limitations.html

# 11. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-10 | 조동휘 | KR 전처리 완료 보고서 기준으로 `TourKoreaDomainData` -> S3 vector index 생성 계약, chunk template, metadata filter, 재색인/검증 기준 작성 |
