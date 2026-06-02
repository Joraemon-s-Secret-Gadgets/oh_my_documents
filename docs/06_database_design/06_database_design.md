# 로브 (Lovv) 데이터베이스 설계 명세서

> 문서 버전: v0.1
> 문서 상태: 기획 단계 (Planning)
> 기준 문서: `docs/01_requirements/01_requirements.md` v1.5

# 1. 문서 개요

## 1.1 목적

본 문서는 로브 서비스의 핵심 데이터 모델, 테이블 후보, 관계, 인덱스, 보존 정책을 정의한다.
PoC에서는 일부 데이터를 정적 파일과 로컬 스토리지로 대체할 수 있으나, Production 전환 시 본 문서를 기준으로 데이터베이스를 설계한다.

## 1.2 데이터베이스 방향

| 항목 | 결정 | 비고 |
| --- | --- | --- |
| 기본 모델 | 관계형 데이터베이스 우선 | 서비스 핵심 데이터는 정규화된 관계형 모델을 기준으로 설계한다. |
| RDBMS | MySQL 8 LTS | 목적지, 축제, 사용자, 저장 일정, 검토 이력 등 핵심 트랜잭션 데이터를 저장한다. |
| NoSQL | AWS DynamoDB | AgentCore와 SAM(Serverless Application Model) 로그를 적재한다. |
| VectorDB | PoC 단계에서는 VectorDB로 구현 | 이후 GraphDB로 이관할지 결정한다. |
| 이유 | ACID 트랜잭션 필요 | 목적지, 축제, 사용자, 저장 일정, 검토 이력 간 관계가 명확하다. |
| 보조 저장소 | DynamoDB 및 VectorDB | 운영 로그와 RAG/검색 보조 데이터를 핵심 RDBMS와 분리해 관리한다. |
