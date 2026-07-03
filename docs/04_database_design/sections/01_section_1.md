# 1. 문서 개요

## 1.1 목적

본 문서는 로브 서비스의 핵심 데이터 모델, 테이블 후보, 관계, 인덱스, 보존 정책을 정의한다.
PoC에서는 일부 데이터를 정적 파일과 로컬 스토리지로 대체할 수 있으나, Production 전환 시 본 문서를 기준으로 데이터베이스를 설계한다.

## 1.2 설계 기준

| 항목 | 결정 | 비고 |
| --- | --- | --- |
| 기본 모델 | 관계형 데이터베이스 우선 | 서비스 핵심 데이터는 정규화된 관계형 모델을 기준으로 설계한다. |
| RDBMS | MySQL 8 LTS | 사용자, 소셜 계정, 저장 일정, 일정 항목, 일정 반응 등 핵심 트랜잭션 데이터를 저장한다. |
| NoSQL | AWS DynamoDB | AgentCore/SAM 실행 상태, 비동기 작업, 사용자 이벤트 로그, API 로그처럼 TTL이 필요한 비정형 데이터를 저장한다. |
| RAG Vector Index | S3 vector 기능 활용 | RAG 검색용 chunk, embedding, metadata filter를 S3 vector 기능 기반 검색 인덱스로 관리한다. 별도 벡터 DB 제품 도입은 기본 전제가 아니다. |
| 관계 탐색 보조 | Lambda 기반 관계 탐색 (Neptune 직접 도입 보류) | 목적지·축제·테마·인접 도시·이동 관계를 DynamoDB 인접 리스트, 사전계산 후보, Lambda 인메모리 그래프로 탐색한다. Neptune은 고도화 승격 옵션으로만 둔다. |
| 대화 전문 | 저장하지 않음 | 요구사항 `NFR-013`에 따라 사용자 대화 로그 전문은 서버나 외부 저장소에 장기 저장하지 않는다. |
| 보조 저장소 | DynamoDB, S3 vector index, Lambda 관계 탐색 | 로그성 데이터, 의미 검색 인덱스, 관계 탐색 보조 기능을 MySQL 원장과 분리해 관리한다. |

## 1.3 저장소 책임

| 저장소 | 책임 | 주요 데이터 |
| --- | --- | --- |
| MySQL 8 LTS | 서비스 원장, 트랜잭션, 조회 기준 데이터 | 사용자 계정, 소셜 계정, 저장 일정, 일정 항목, 일정 반응 |
| DynamoDB | 비정형 실행 상태, 이벤트 로그, TTL 로그, 수집 정규화 결과 | Agent run, async job, 사용자 행동 이벤트, API 로그, 운영 trace, City/Attraction/Festival/VisitorStatistics 정규화 문서 |
| S3 vector index | 의미 검색 인덱스 | 목적지·축제·관광지 문서 chunk, embedding, source reference, metadata filter |
| Lambda 관계 탐색 | 그래프DB 대체 기능 (PoC/Prod 1차) | 도시-테마, 도시-축제, 인접 도시, 일정 항목-장소 후보 관계를 DynamoDB 인접 리스트와 Lambda 인메모리 그래프로 탐색. Neptune은 고도화 단계 승격 옵션 |
| Object Storage | 원본 수집 파일과 대용량 정적 산출물 | S3 Raw 수집 원본, 전처리 결과, 이미지/첨부 파일 |

## 1.4 현재 AWS 구조 확인 기준

2026-07-03 기준으로 `us-east-1` live AWS와 인접 구현 저장소를 확인한 결과, 저장소 경계는 다음처럼 분리되어 있다.
문서에는 공개 공유를 고려해 RDS endpoint, secret ARN, 계정 상세 식별자는 싣지 않고 리소스 역할과 물리 이름만 기록한다.

| 경계 | 현재 확인 기준 | 핵심 리소스 |
| --- | --- | --- |
| Backend Data Stack | `03_lovv_BE/infra/data-stack/template.yaml`, CloudFormation `lovv-dev-data-stack` | RDS MySQL `lovv-dev-mysql`, DynamoDB `lovv_dev_*`, S3 image bucket `lovv-image-dev-925273580929` |
| Data Collect Pipeline | `02_lovv_data_collect/infrastructure/terraform` | S3 raw/processed bucket `lovv-data-pipeline-dev-925273580929`, image pipeline bucket `lovv-pipeline-images-dev-925273580929`, DynamoDB `TourKoreaDomainData`, `TourKoreaDomainDataV2` |
| Vector Retrieval | Terraform S3 Vector shim과 live `s3vectors get-index` | `lovv-vector-dev` / `kr-tour-domain-v2`, `lovv-agentcore-v1-vector` / `kr-agentcore-v1` |
| Network Access | Backend data stack VPC endpoint 및 선택 NAT instance | RDS는 private subnet에 배치하고, S3/DynamoDB는 Gateway VPC Endpoint, Secrets Manager/SSM은 Interface VPC Endpoint로 접근 |
