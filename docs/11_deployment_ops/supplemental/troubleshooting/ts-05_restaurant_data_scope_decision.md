# TS-05 식당 데이터 취득 범위 조정

> 문서 성격: 트러블슈팅 하위 Markdown
> 상위 문서: `../troubleshooting.md`

> 문서 버전: v0.2
> 문서 상태: 초안 (Draft)
> 작성일: 2026-07-09
> 작성자: llm팀
> 문서 목적: 경북·강원 관광지와 축제 데이터 취득 과정에서 식당 데이터를 직접 취득하지 않고 Kakao Map API로 대체한 판단 근거를 정리한다.

---

# 1. 요약

| 항목 | 내용 |
| --- | --- |
| 문제 | 경북·강원 관광지·축제 데이터 취득 시 식당 데이터도 함께 취득해 실제로 사용했으나, 의미 있는 결과가 나오지 않았고 S3 vector 변환 작업 시간이 증가했다. |
| 원인 | 식당 데이터 수량이 방대하고, DynamoDB 저장·인덱스·조회 비용, DB 운영 문제, S3 vector 변환·인덱싱 부담이 증가할 수 있었다. |
| 해결 과정 | 식당 데이터는 직접 취득 대상에서 제외하고, Kakao Map API를 통해 사용자 맥락에 맞게 조회하는 방식으로 전환했다. |
| 결과 | 프로젝트 보유 데이터는 관광지·축제 중심으로 유지하고, 식당 데이터는 외부 API 연동 대상으로 정리했다. |

# 2. 문제

경북·강원 관광지와 축제 데이터를 취득하는 과정에서 식당 데이터도 함께 취득 대상으로 검토했고, 당시에는 식당 데이터를 실제로 취득해 사용하였다.

그러나 취득한 식당 데이터를 적용했을 때 추천·검색 품질 측면에서 의미 있는 결과가 나오지 않았다. 또한 식당 데이터는 관광지·축제 데이터보다 수량이 많아 S3 vector로 변환하는 작업 시간이 증가하는 문제가 발생했다.

이 상태로 식당 데이터를 계속 직접 보유하면 수집, 정제, S3 vector 변환, 갱신, 품질 검증 부담이 프로젝트 범위를 넘어설 수 있었다.

# 3. 원인

| 원인 | 내용 |
| --- | --- |
| 데이터 규모 | 식당 데이터는 관광지나 축제보다 후보 수가 많아 전체 취득량과 전처리 비용이 커진다. |
| DynamoDB 비용 증가 | 식당 데이터를 모두 DynamoDB에 적재하면 저장 용량, GSI, 조회 요청량이 함께 증가해 DB 운영 비용이 커질 수 있다. |
| DB 운영 문제 | 대량 식당 데이터가 누적되면 파티션 키 설계, GSI 관리, 조회 패턴 관리, 데이터 갱신 주기 관리가 복잡해져 핵심 관광지·축제 데이터 운영에도 영향을 줄 수 있다. |
| S3 vector 변환 부담 | 식당 데이터까지 S3 vector로 변환하면 embedding 생성 대상이 크게 늘어나 작업 시간이 증가하고, S3 vector index 생성·검증·재생성 비용도 함께 커진다. |
| 품질 기준의 주관성 | 식당 후기는 개인 취향, 방문 목적, 동행 유형, 가격 민감도에 따라 평가가 크게 달라진다. |
| 최신성 요구 | 영업 여부, 메뉴, 가격, 평점, 후기 변화가 잦아 정적 데이터로 보관할 경우 빠르게 낡을 수 있다. |
| 서비스 맥락 | 식당 추천은 사용자 위치, 일정, 시간대, 선호도와 결합되어야 의미가 커진다. |

# 4. 해결 과정

1. 관광지·축제 데이터와 식당 데이터의 성격을 분리해 검토했다.
2. 관광지·축제는 프로젝트 도메인 데이터로 직접 취득·정제하는 쪽이 적합하다고 판단했다.
3. 식당 데이터는 정적 데이터로 직접 취득하면 DynamoDB 비용과 DB 운영 부담이 커질 수 있다고 판단했다.
4. 식당 데이터는 사용자의 위치, 일정, 시간대, 선호도에 따라 실시간으로 달라지는 성격이 강하다고 정리했다.
5. 식당 데이터는 직접 취득 대상에서 제외하고, Kakao Map API를 통해 사용자 맥락에 맞게 조회하는 방향으로 전환했다.

# 5. 결과

식당 데이터는 프로젝트 내부 데이터셋으로 대량 취득하지 않는다.

대신 관광지·축제 데이터는 직접 취득·정제 대상으로 유지하고, 식당 데이터는 Kakao Map API를 통해 필요 시점에 조회하는 외부 API 연동 대상으로 정리한다. 이를 통해 데이터 보유 범위, DynamoDB 운영 비용, S3 vector 변환 부담을 줄이고, 식당 데이터의 최신성과 사용자 취향 반영 가능성을 확보한다.

# 6. 출처 및 근거

| 출처 | 확인 내용 | TS-05 반영 |
| --- | --- | --- |
| [Kakao Developers - Local REST API](https://developers.kakao.com/docs/en/local/dev-guide) | Kakao Local API는 주소-좌표 변환, 좌표-주소 변환, 키워드 기반 장소 검색 등을 REST API로 제공한다. | 식당 데이터를 직접 보유하지 않고, 사용자 위치·일정·검색어에 따라 API 조회로 대체한다. |
| [Kakao Developers - Local Concepts](https://developers.kakao.com/docs/latest/en/local/common) | Local API는 장소 검색, 카테고리 기반 검색, 좌표 기반 주소/행정구역 조회를 제공한다. | 식당 추천은 정적 데이터셋보다 위치와 맥락 기반 실시간 조회가 적합하다는 판단 근거로 사용한다. |
| [Amazon DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/) | DynamoDB 비용은 저장 용량, 읽기/쓰기 요청, 용량 모드, 부가 기능 사용에 따라 증가한다. | 식당 대량 적재는 저장 비용과 요청 비용, GSI 운영 비용을 증가시킬 수 있으므로 직접 취득 범위를 줄인다. |
| [DynamoDB throughput capacity](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/capacity-mode.html) | On-demand mode는 요청 단위 과금이고, provisioned mode는 설정한 처리량 기준으로 운영된다. | 식당 데이터 조회량이 커질 경우 테이블 처리량과 비용이 핵심 운영 리스크가 된다. |
| [AWS S3 Vectors - Working with S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html) | S3 Vectors는 embedding 저장과 similarity query를 제공하며, vector 생성·저장·조회 대상이 늘수록 운영 범위가 커진다. | 식당 데이터를 S3 vector 변환 대상에서 제외해 embedding 생성 시간과 index 검증 부담을 줄인다. |
| [korea_data_acquisition_plan_updated.md](../../../03_data_collect_plan/supplemental/korea_data_acquisition_plan_updated.md) | 미식·노포 테마는 관광식당 코드로 제한하고 일반 음식점, 카페, 주점 등은 제외하는 수집 기준을 명시한다. | 식당 전체가 아니라 관광 도메인에 필요한 제한된 범위만 검토하고, 일반 식당은 API 조회 대상으로 분리한다. |
| [data_preprocessing_plan.md](../../../08_data_preprocessing/data_preprocessing_plan.md) | V2 운영 계약에서 `restaurant`를 활성 entity로 복원하지 않고, vector 생성 대상도 `city_metadata`, `attraction`, `festival` 중심으로 둔다. | 프로젝트 보유 데이터셋은 관광지·축제 중심으로 유지하고 식당 데이터 직접 적재를 제외한다. |

# 7. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.2 | 2026-07-09 | llm팀 | Kakao Local API, DynamoDB 비용/처리량, S3 Vectors, 로컬 취득·전처리 기준 근거 추가 |
| v0.1 | 2026-07-09 | llm팀 | 식당 데이터 취득 범위 조정 이슈 초안 작성 |
