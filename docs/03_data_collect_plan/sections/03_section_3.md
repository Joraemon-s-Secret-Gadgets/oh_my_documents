# 3. 데이터 취득 파이프라인

## 3.1 처리 흐름

```text
자동 수집
↓
로컬 검증 산출물 생성
↓
JSON 직렬화
↓
S3 Raw Bucket 적재
↓
Raw 보관 기간 경과
↓
Lambda 배치 전처리
↓
취득 상태 분류
↓
공식 사이트 확인 / Web Search Worker
↓
수동 검수
↓
정규화 DB 적재
```

정의된 모든 필드가 JSON 원본으로 저장되도록 시도한다. 한국은 실제 수집 검증 단계에서 `data/KR/*.json` 로컬 산출물로 City, Attraction, Festival, 방문객 통계의 구조와 수량을 먼저 확인한다. 일본은 관동 지역 지자체 우선 수집 결과를 `data/JP/*.json` 로컬 산출물로 확인하고 City, Attraction, Festival, 관광 통계의 구조를 검증한다. 이후 수집 결과는 엔티티 유형과 출처별 JSON 문서로 직렬화한 뒤 S3 Raw Bucket에 적재한다. Raw 데이터는 재사용과 재처리를 위해 일정 기간 누적 보관하고, 보관 기간 또는 배치 기준이 충족되면 Lambda가 해당 Prefix의 JSON 원본을 읽어 전처리한 뒤 DynamoDB에 적재한다. 운영시간, 운영기간, 입장료, 사진, 축제 기간처럼 출처별 표현 차이가 큰 값도 최초 수집 대상에 포함하며, 자동 수집 실패 시 같은 파이프라인 안에서 공식 확인 또는 수동 검수로 채운다.

## 3.2 취득 상태 관리

| 취득 상태 | 기준 | 처리 방식 |
| --- | --- | --- |
| `collected` | 자동 수집 값이 있고 출처가 명확함 | JSON 저장 후 S3 Raw Bucket 적재 |
| `needs_review` | 값은 있으나 표현이 모호하거나 최신성 확인이 필요함 | 공식 사이트 확인 또는 수동 검수 |
| `missing` | 자동 수집에서 값을 찾지 못함 | Web Search Worker 또는 수동 입력 대상 |
| `blocked` | 약관·저작권·접근 제한으로 수집 불가 | 딥링크 또는 빈 값으로 대체하고 사유 기록 |

## 3.3 원본 및 정규화 저장

| 구분 | 저장 내용 |
| --- | --- |
| Raw 데이터 | API 응답, Wikipedia HTML 수집 원본, 공식 사이트 확인 결과, 이미지 메타데이터를 JSON 문서로 저장한 S3 객체 |
| 로컬 검증 산출물 | 한국 `data/KR/*.json`, 일본 `data/JP/*.json`처럼 S3 Raw 적재 전 수집 구조와 수량을 검증하는 JSON 파일 |
| S3 Raw 객체 | `raw/{country}/{source}/{entity_type}/{yyyy}/{mm}/{dd}/` Prefix에 저장되는 원본 JSON |
| Raw 보관 및 배치 처리 | 일정 기간 Raw Prefix에 누적한 뒤 Lambda 배치 전처리 대상으로 사용 |
| 정규화 데이터 | City, Attraction, Festival, VisitorStatistics, 기후, 검색 링크 |
| 검수 메타데이터 | `verified_at`, `verified_source_url`, `verification_note`, `data_confidence` |
| 출처 메타데이터 | `source_name`, `source_url`, `collected_at`, `license_type` |
