# TS-02 S3 vector index 계약 정합성

> 문서 성격: 트러블슈팅 하위 Markdown
> 상위 문서: `../troubleshooting.md`

> 문서 버전: v0.2
> 문서 상태: 초안 (Draft)
> 작성일: 2026-07-09
> 작성자: llm팀
> 문서 목적: `TS-02` 이슈의 문제, 원인, 판단, 조치, 재발 방지 기준을 본 문서에서 분리해 상세 관리한다.

---


## 1. 증상

S3 vector index 생성 기준을 정리하는 과정에서 `city_id`, vector ID, embedding dimension, metadata filter 기준이 초기 설계와 실제 적재 데이터 사이에서 어긋날 수 있었다.

## 2. 원인

| 항목 | 초기 위험 |
| --- | --- |
| `city_id` | 과거 설계는 `KR-GB-ANDONG` 계열을 가정했지만 실제 데이터는 `KR-Andong` 형식 |
| Vector ID | `#chunk#` 리터럴 포함 4분절과 3분절 형식이 혼재 가능 |
| Embedding | dimension과 metric은 index 생성 후 변경이 어려움 |
| Metadata | filterable 2KB 제한을 넘길 수 있음 |

## 3. 조치

- `city_id`는 실데이터 기준 `KR-{CityNameEn}` 형식으로 확정한다.
- Vector ID는 `{source_type}#{source_id}#{chunk_no}` 3분절로 통일한다.
- Amazon Titan Text Embeddings V2, 1024 dimension, cosine 기준으로 고정한다.
- `visitor_statistics`는 개별 vector가 아니라 city chunk의 보조 문맥으로만 반영한다.
- CEA 검색 요구에 맞춰 restaurant chunk에는 주소를 포함한다.

## 4. 재발 방지

- index 생성 전에 dimension, metric, non-filterable key를 문서와 IaC에서 대조한다.
- GSI3 entity type별 export 결과로 원천 수량을 manifest에 남긴다.
- S3 vector 결과는 DynamoDB `ddb_pk`/`ddb_sk`로 재검증하는 것을 기본 계약으로 둔다.

## 5. 출처 및 근거

| 출처 | 확인 내용 | TS-02 반영 |
| --- | --- | --- |
| [AWS S3 Vectors - Working with S3 Vectors and vector buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html) | S3 Vectors는 vector bucket/index에 embedding을 저장하고 similarity query와 metadata filtering을 제공한다. | S3 vector index를 원본 저장소가 아니라 검색 인덱스로 두고, DynamoDB/S3 Raw 재조회 키를 함께 보존한다. |
| [AWS S3 Vectors - Metadata filtering](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-metadata-filtering.html) | filterable metadata는 similarity query에서 필터로 사용할 수 있고, 필터 가능한 metadata 크기 제한을 고려해야 한다. | metadata filter key를 사전에 제한하고, 큰 설명/본문은 filterable metadata가 아니라 vector text 또는 원본 재조회 대상으로 분리한다. |
| [Amazon Bedrock - Titan Text Embeddings models](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html) | `amazon.titan-embed-text-v2:0`은 텍스트 검색과 유사도에 사용할 수 있는 embedding 모델이며 1024차원 vector를 제공한다. | Titan Text Embeddings V2, 1024 dimension, cosine 기준을 index 계약으로 고정한다. |
| [data_preprocessing_plan.md](../../../08_data_preprocessing/data_preprocessing_plan.md) | V2 기준에서 `TourKoreaDomainDataV2`, `kr-tour-domain-v2`, vector 대상 entity, 7,606 unique vector 기준을 정리한다. | 문서의 `city_id`, entity type, visitor statistics 제외, 원본 재조회 계약과 동기화한다. |
| [s3_vector_index_plan.md](../../../08_data_preprocessing/supplemental/s3_vector_index_plan.md) | KR 전처리 산출물 기반 S3 vector index 구축안과 vector ID, embedding, metadata 기준을 정리한다. | TS-02의 vector ID 3분절, Titan V2 1024/cosine, GSI3 export 기준의 직접 근거로 사용한다. |

## 6. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.2 | 2026-07-09 | llm팀 | S3 Vectors, metadata filtering, Titan Text Embeddings V2 공식 문서와 로컬 전처리 기준 문서 근거 추가 |
| v0.1 | 2026-07-09 | llm팀 | S3 vector index 계약 정합성 이슈 초안 작성 |
