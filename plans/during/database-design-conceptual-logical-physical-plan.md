---
작성자: llm팀
상태: 진행중
---

# 데이터베이스 설계 Markdown 작성 계획

## 목적

`docs/04_database_design/04_database_design.md`를 대표 문서로 두고, 로브(Lovv) 서비스의 데이터베이스 설계를 개념 설계, 논리 설계, 물리 설계 순서로 작성한다.
현재 저장소 방향, PoC DB 설계 초안, 통합 설계 보고서, NoSQL 스키마 설계 내용을 정리해 하나의 일관된 Markdown 설계 문서로 반영한다.

## 대상 파일

| 구분 | 파일 | 용도 |
| --- | --- | --- |
| 대표 문서 | `docs/04_database_design/04_database_design.md` | 최종 DB 설계 명세서 본문 |
| RDB 초안 | `docs/04_database_design/lovv-poc-database-design.md` | PoC 기준 MySQL 테이블, 관계, JSON 컬럼 참고 |
| 통합 보고서 | `docs/04_database_design/database_design_integration_report.md` | 전체 도메인, ERD, 인덱스, 보존 정책 참고 |
| NoSQL 초안 | `docs/04_database_design/nosql_schema_design.md` | DynamoDB 또는 NoSQL 데이터 구조 참고 |
| 저장소 결정 요약 | `docs/04_database_design/database_storage_decision_summary.md` | MySQL, DynamoDB, VectorDB 방향 확인 |
| 생성물 | `pages/04_database_design.html` | Markdown 반영 후 재생성 대상 |

## 설계 작성 방향

### 1. 개념 설계

서비스 요구사항을 데이터 관점의 큰 업무 영역과 핵심 엔티티로 정리한다.

- 사용자 및 인증
- 여행 선호도와 온보딩
- 목적지, 관광지, 축제, 콘텐츠 원천
- 추천 요청, 추천 결과, 일정
- 리뷰, 피드백, 신고, 운영 검수
- Agent 실행, 비동기 작업, 로그
- RAG 문서, 벡터 검색 보조 데이터

개념 설계에서는 테이블 컬럼보다 도메인 범위, 엔티티 책임, 주요 관계를 먼저 확정한다.

### 2. 논리 설계

개념 설계의 엔티티를 실제 저장 구조 후보로 분해한다.

- MySQL 8 LTS 기준 정규화 테이블을 정의한다.
- 사용자, 목적지, 추천, 일정, 리뷰, 검수 이력 등 트랜잭션성 데이터는 RDB 중심으로 둔다.
- DynamoDB에는 AgentCore/SAM 실행 상태, async job, 운영 로그, 이벤트 로그처럼 대량 로그성 데이터를 분리한다.
- VectorDB에는 RAG 검색용 chunk, embedding, source reference를 분리한다.
- 각 테이블 또는 컬렉션마다 PK, FK, 주요 속성, 관계, 삭제 정책을 정의한다.
- JSON 컬럼이 필요한 경우 저장 목적과 검증 기준을 함께 적는다.

### 3. 물리 설계

Production 전환을 고려한 실제 DB 구현 기준을 정리한다.

- MySQL 테이블별 컬럼 타입, NOT NULL, UNIQUE, FK, CHECK 후보를 정리한다.
- 주요 조회 패턴별 인덱스 후보를 정의한다.
- DynamoDB PK/SK, GSI, TTL, hot partition 회피 기준을 정의한다.
- VectorDB collection 또는 index 구성, metadata filter 기준을 정의한다.
- 개인정보, 로그, 추천 이력, 원천 데이터의 보존 기간과 접근 권한을 함께 명시한다.
- PoC에서 생략하는 항목과 Production에서 반드시 보강할 항목을 분리한다.

## 문서 구조 초안

```text
1. 문서 개요
2. DBMS 및 저장소 책임
3. 개념 설계
   3.1 업무 도메인
   3.2 핵심 엔티티
   3.3 개념 ERD
4. 논리 설계
   4.1 MySQL 논리 모델
   4.2 DynamoDB 논리 모델
   4.3 VectorDB 논리 모델
   4.4 관계 및 삭제 정책
5. 물리 설계
   5.1 MySQL 물리 테이블
   5.2 DynamoDB 키 설계
   5.3 VectorDB 인덱스 설계
   5.4 주요 인덱스 및 조회 패턴
6. 보존 정책 및 권한
7. PoC 적용 범위와 Production 전환 항목
8. 설계 검토 체크리스트
9. 변경 이력
```

## 작업 체크리스트

- [x] `docs/01_requirements/01_requirements.md`에서 DB 설계를 유도하는 기능·비기능 요구사항을 확인한다.
- [ ] `docs/04_data_collect_plan/04_data_collect_plan.md`에서 수집 데이터와 원천 데이터 보존 기준을 확인한다.
- [x] `docs/05_api_spec/05_api_spec.md`에서 API 요청·응답이 필요로 하는 저장 항목을 확인한다.
- [x] `docs/05_agent_spec/05_agent_spec.md`에서 Agent 실행 상태, 로그, RAG 데이터 저장 요구를 확인한다.
- [x] 기존 DB 설계 초안 4개를 비교해 중복, 충돌, 누락 엔티티를 정리한다.
- [x] 개념 설계 섹션에 도메인, 엔티티, 관계를 작성한다.
- [x] 논리 설계 섹션에 MySQL, DynamoDB, VectorDB 저장 모델을 분리해 작성한다.
- [x] 물리 설계 섹션에 컬럼, 키, 인덱스, TTL, 보존 정책을 작성한다.
- [x] PoC 범위와 Production 전환 범위를 명확히 분리한다.
- [x] `docs/04_database_design/04_database_design.md`를 갱신한다.
- [x] Markdown 원본 기준으로 `pages/04_database_design.html`을 재생성한다.
- [x] `index.html`의 DB 설계 문서 요약 또는 상태가 바뀌었는지 확인한다.
- [ ] `git diff --check`로 Markdown/HTML diff의 기본 형식 문제를 검증한다.
- [ ] DBMS 방향과 저장소 책임이 기존 결정과 충돌하지 않는지 최종 확인한다.

## 검증 방법

- `rg`로 `PostgreSQL`, `미정`, `추후 선정`, `agent_runs`, `async_jobs` 같은 과거 또는 충돌 가능 키워드를 확인한다.
- 대표 문서와 보조 문서의 저장소 결정이 `MySQL 8 LTS`, `AWS DynamoDB`, `VectorDB` 기준으로 일관되는지 확인한다.
- 생성된 HTML의 목차와 본문 섹션이 Markdown 구조와 대응하는지 확인한다.
- 관계형 데이터, 로그성 데이터, 벡터 검색 데이터가 서로 다른 저장소 책임으로 분리되어 있는지 확인한다.

## 완료 기준

- `docs/04_database_design/04_database_design.md`에 개념 설계, 논리 설계, 물리 설계가 모두 포함된다.
- 각 설계 단계가 같은 엔티티와 저장소 책임을 기준으로 이어진다.
- `pages/04_database_design.html`이 대표 Markdown과 같은 내용을 제공한다.
- PoC 구현 범위와 Production 보강 항목이 분리되어 후속 개발자가 바로 작업 단위를 나눌 수 있다.
