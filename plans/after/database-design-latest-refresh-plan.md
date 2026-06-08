---
작성자: llm팀
상태: 진행후
---

# 데이터베이스 설계 문서 최신화 계획

## 목적

`docs/04_database_design/04_database_design.md`를 현재 문서 번호 체계와 최신 요구사항, 데이터 수집 계획, Agent 명세, API 명세에 맞게 갱신한다. 작업은 Markdown 원본을 먼저 수정하고, 이후 `pages/04_database_design.html`과 `index.html` 등 GitHub Pages 생성물을 동기화하는 순서로 진행한다.

## 기준 문서

| 구분 | 기준 파일 | 확인할 내용 |
| --- | --- | --- |
| 요구사항 | `docs/01_requirements/01_requirements.md` | 사용자·권한, 기능 요구사항, 비기능 요구사항, 데이터 요구사항, 보안·보존 조건 |
| 데이터 수집 | `docs/03_data_collect_plan/03_data_collect_plan.md` | City/Attraction/Festival/VisitorStatistics, S3 Raw, Lambda 전처리, DynamoDB 적재 기준 |
| DB 설계 | `docs/04_database_design/04_database_design.md` | 개념·논리·물리 설계, 저장소 책임, 인덱스, 보존 정책 |
| Agent | `docs/05_agent_spec/05_agent_spec.md` | UnifiedAgentState, AgentCore Memory, 축제 검증 캐시, 실행 상태, trace |
| 기술 명세 | `docs/06_technical_spec/06_technical_spec.md` | AWS 구성, 백엔드·데이터 계층, S3 vector 기능 사용 범위, PoC와 Production 경계 |
| API | `docs/07_api_spec/07_api_spec.md` | 인증, 추천, 지도, 저장·피드백, 운영 API의 요청·응답 필드 |

## 대상 파일

| 구분 | 파일 | 처리 |
| --- | --- | --- |
| 원본 | `docs/04_database_design/04_database_design.md` | 최신화 주 대상 |
| 보조 원본 | `docs/04_database_design/DBMS.md` | DBMS 결정 표와 대표 문서의 저장소 책임 일치 확인 |
| 보조 원본 | `docs/04_database_design/integrated_draft.md` | 상세 초안과 대표 문서 사이의 엔티티·저장소 충돌 확인 |
| 보조 원본 | `docs/04_database_design/nosql_schema_design.md` | DynamoDB 테이블·PK/SK·GSI·TTL 후보 반영 |
| 보조 원본 | `docs/04_database_design/lovv-service-db-erd.md` | ERD와 대표 문서의 관계·테이블명 일치 확인 |
| 생성물 | `pages/04_database_design.html` | Markdown 수정 후 재생성 |
| 생성물 | `index.html` | 문서 상태·요약·링크 동기화 |
| 리다이렉트 | `pages/05_database_design.html`, `pages/06_database_design.html` | 구 번호 문서가 `04_database_design.html`로 연결되는지 확인 |

## 최신화 방향

1. 문서 버전과 기준 문서를 현재 상태로 갱신한다.
2. 저장소 책임을 `MySQL 8 LTS`, `DynamoDB`, `S3 vector 기능 기반 RAG 인덱스`, `Object Storage`로 명확히 분리한다.
3. 데이터 수집 계획의 `City -> Attraction/Festival/VisitorStatistics` 구조와 S3 Raw/Lambda/DynamoDB 흐름을 DB 설계에 반영한다.
4. Agent 명세의 AgentCore Runtime/Memory/Gateway/Observability 요소를 저장소 모델에 연결한다.
5. API 명세의 요청·응답 식별자와 DB 엔티티의 키 이름을 맞춘다.
6. 사용자 대화 전문 장기 저장 금지, PII 마스킹, TTL, 권한별 접근 범위를 보존 정책에 명시한다.
7. PoC 로컬 JSON·정적 파일 대체와 Production DB 설계를 분리해 적는다.
8. 기존 `VectorDB` 표현은 별도 VectorDB 제품 도입이 아니라 S3 vector 기능을 활용하는 검색 인덱스 계층으로 정리한다.

## 작업 체크리스트

- [x] 현재 작업 트리의 번호 재배치 변경을 확인하고, 사용자 변경을 되돌리지 않는 범위를 확정한다.
- [x] `docs/04_database_design/04_database_design.md`의 문서 버전, 기준 문서, 변경 이력을 확인한다.
- [x] 요구사항 문서에서 DB에 직접 영향을 주는 사용자, 권한, 추천, 저장, 피드백, 운영, 보안 요구사항을 추출한다.
- [x] 데이터 수집 계획에서 City, Attraction, Festival, VisitorStatistics, Raw/Normalized 저장 흐름을 추출한다.
- [x] Agent 명세에서 AgentCore Memory, 실행 상태, 비동기 작업, 축제 검증 캐시, trace 저장 요구를 추출한다.
- [x] API 명세에서 `recommendationId`, `festivalId`, `destinationId`, 저장 일정, 피드백 필드와 DB 키 후보를 대조한다.
- [x] MySQL 논리 모델에 목적지·관광지·축제·방문통계·추천요청·추천결과·일정·피드백·운영검수 테이블 후보가 빠짐없이 있는지 확인한다.
- [x] DynamoDB 논리 모델에 Agent 실행 상태, async job, 사용자 이벤트, API 로그, 축제 검증 캐시, TTL/GSI 후보가 명확한지 확인한다.
- [x] S3 vector 기능 기반 RAG 인덱스 모델에 문서 chunk, embedding, source reference, metadata filter 기준이 명확한지 확인한다.
- [x] 보존 정책에 대화 전문 미저장, PII 마스킹, 이벤트 TTL, 운영 로그 접근 권한을 반영한다.
- [x] `DBMS.md`, `integrated_draft.md`, `nosql_schema_design.md`, `lovv-service-db-erd.md`와 대표 문서 사이의 충돌을 정리한다.
- [x] `scripts/generate_pages.py`로 HTML 생성물을 재생성한다.
- [x] `pages/04_database_design.html`, `index.html`, 구 번호 리다이렉트 페이지의 링크와 상태를 확인한다.
- [x] `git diff --check`와 문서 링크/앵커 검색으로 Markdown·HTML 구조 오류를 검증한다.
- [x] 변경 요약과 남은 의사결정 항목을 정리한다.

## 검증 방법

- [x] `python scripts/generate_pages.py`
- [x] `git diff --check`
- [x] `rg -n "04_database_design|05_database_design|06_database_design" index.html pages scripts docs`
- [x] `rg -n "대화 전문|TTL|GSI|AgentCore|VisitorStatistics|S3 vector|recommendationId|festivalId|destinationId" docs/04_database_design/04_database_design.md pages/04_database_design.html`
- [x] `rg -n "docs/04_database_design|04_database_design.html" README.md AGENT.md docs/AGENT.md`

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 문서 번호 재배치가 진행 중이라 구 경로와 신 경로가 동시에 존재함 | 생성 HTML과 리다이렉트가 혼동될 수 있음 | 실제 기준 경로 `docs/04_database_design/`를 우선하고, 구 번호 HTML은 리다이렉트로만 검증 |
| DB 설계 보조 문서가 대표 문서보다 상세함 | 대표 문서에 누락이 남을 수 있음 | 보조 문서는 근거로 읽되 최종 공개 기준은 대표 문서에 요약 반영 |
| AgentCore/SAM 상태 저장 위치가 문서별로 다르게 표현될 수 있음 | MySQL과 DynamoDB 책임 경계가 흐려짐 | MySQL은 서비스 원장, DynamoDB는 실행 상태·이벤트·TTL 로그로 통일 |
| 기존 문서에 별도 VectorDB 제품 도입처럼 표현된 문장이 남아 있음 | 기술 선택과 구현 범위가 잘못 전달될 수 있음 | `VectorDB` 표현을 S3 vector 기능 기반 RAG 인덱스로 치환하고, 별도 VectorDB/GraphDB 검토 문구는 제거 또는 후순위 검토로 낮춤 |
| API 필드명과 DB 엔티티명이 어긋날 수 있음 | 구현 단계에서 매핑 비용 증가 | API 식별자를 DB 논리 키 후보와 함께 명시 |
| 개인정보·대화 원문 저장 정책이 누락될 수 있음 | 보안·비기능 요구사항 위반 | 보존 정책과 저장소 책임 표에 명시적으로 반복 |

## 완료 기준

- [x] 대표 DB 설계 문서가 최신 요구사항, 수집 계획, Agent 명세, API 명세와 충돌하지 않는다.
- [x] MySQL, DynamoDB, S3 vector 기능 기반 RAG 인덱스, Object Storage의 책임이 한눈에 구분된다.
- [x] 주요 엔티티별 키, 관계, 인덱스, TTL 또는 보존 정책 후보가 적혀 있다.
- [x] PoC 대체 저장 방식과 Production 설계가 분리되어 있다.
- [x] `pages/04_database_design.html`과 `index.html`이 Markdown 원본과 동기화되어 있다.
