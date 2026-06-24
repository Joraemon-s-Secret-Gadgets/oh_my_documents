# 3. 전처리 아키텍처

## 3.1 구성 방향

수집 결과는 먼저 JSON 원본 파일로 직렬화해 S3 Raw Bucket에 적재한다. Raw 원본은 재사용과 재처리를 위해 일정 기간 Prefix 단위로 누적 보관하고, 보관 기간 또는 처리 기준이 충족되면 Lambda가 해당 원본 JSON 묶음을 읽어 정제·정규화·품질 검증·파생 필드 생성을 수행한 뒤 DynamoDB에 저장한다.

```text
Collector / Web Search Worker / Manual Review
↓
S3 Raw Bucket
↓
Raw 보관 기간 / 배치 기준 충족
↓
AWS Lambda Preprocessor
↓
DynamoDB Normalized Tables
↓
Search Index / RAG Dataset / Admin Review
```

## 3.2 AWS 구성 요소

| 구성 요소 | 역할 | 저장/처리 단위 |
| --- | --- | --- |
| S3 Raw Bucket | 수집 원본 누적 보존 | 국가, 출처, 엔티티 유형, 수집일 기준 객체 |
| S3 Processed Prefix | Lambda 처리 결과와 품질 리포트 보존 | 정규화 JSON, 실패 리포트, 검수 대상 목록 |
| Lambda Preprocessor | 일정 기간 누적된 Raw JSON 묶음의 스키마 검증, 필드 정제, 정규화, 중복 후보 탐지, DynamoDB 적재 | S3 Prefix 또는 배치 묶음 |
| DynamoDB | City, Attraction, Festival, VisitorStatistics, 검수 상태, 품질 메타데이터 저장 | 엔티티 단위 Item |
| CloudWatch Logs | Lambda 실행 로그와 실패 원인 기록 | 실행 요청 단위 |
| DLQ 또는 실패 Prefix | 처리 실패 이벤트 격리 | 실패 S3 객체 또는 이벤트 |

## 3.3 S3 경로 기준

| 영역 | 예시 Prefix | 내용 |
| --- | --- | --- |
| Raw | `raw/{country}/{source}/{entity_type}/{yyyy}/{mm}/{dd}/` | JSON으로 저장한 수집 원본 API 응답, HTML 추출값, 수동 입력 원본 |
| Processed | `processed/{country}/{entity_type}/{yyyy}/{mm}/{dd}/` | Lambda 전처리 결과 JSON |
| Quality | `quality/{country}/{entity_type}/{yyyy}/{mm}/{dd}/` | 품질 검증 리포트 |
| Review | `review/{queue_name}/{yyyy}/{mm}/{dd}/` | 수동 검수 대상 목록 |
| Failed | `failed/{country}/{source}/{entity_type}/{yyyy}/{mm}/{dd}/` | 처리 실패 원본과 실패 사유 |
