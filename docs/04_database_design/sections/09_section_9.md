# 9. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v1.1 | 2026-07-03 | Codex | live AWS 기준 RDS, DynamoDB, S3/S3 Vector 구조 확인 결과와 Backend/Data Collect 저장소 경계, `user_preferences`, auth session, 익명 세그먼트, pipeline image bucket drift를 반영 |
| v1.0 | 2026-07-02 | Codex | `001_product_api_tables.sql` 삭제 유지, base schema 단일 기준, admin migration 002→003→004 적용 순서와 004의 MFA·고위험 테이블 source of truth 명시 |
| v0.9 | 2026-06-30 | Codex | `R-SUPER-ADMIN` 역할·지역 할당, 고위험 변경 요청 상태·제약·인덱스와 C4 감사 로그 action 커버리지 반영 |
| v0.8 | 2026-06-30 | Codex | 관리자 Step-up MFA 자격·세션 테이블과 보존 기준 추가 |
| v0.7 | 2026-06-22 | 로브 기획팀 | 대화형 빌더 메모리 2계층 저장 기준과 개인정보 비저장 원칙 반영 |
| v0.6 | 2026-06-12 | 로브 기획팀 | 그래프DB 직접 도입 대신 Lambda 기반 관계 탐색 보조 기능 구현 예정으로 물리 설계와 운영 기준 조정 |
| v0.5 | 2026-06-08 | 로브 기획팀 | 보존 기간·TTL 권고·잠정값(5.1절) 추가, Neptune 비용 주의·대체 설계 명세서 반영, 운영 대시보드(CloudWatch·Budgets)를 Production 운영 단계에 추가 |
| v0.4 | 2026-06-08 | 로브 기획팀 | AWS Neptune을 추천 관계 탐색용 그래프 인덱스로 반영 |
| v0.3 | 2026-06-07 | 로브 기획팀 | 별도 벡터 DB 전제를 S3 vector 기능 기반 RAG 인덱스로 정리하고, VisitorStatistics와 S3 Raw/Lambda/DynamoDB 정규화 흐름 반영 |
| v0.2 | 2026-06-07 | 로브 기획팀 | 개념 설계, 논리 설계, 물리 설계 구조와 RDB/NoSQL 사용자 설계 반영 |
| v0.1 | 2026-06-04 | 로브 기획팀 | DBMS 방향 초안 작성 |
