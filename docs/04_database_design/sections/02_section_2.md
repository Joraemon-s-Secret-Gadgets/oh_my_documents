# 2. 개념 설계

## 2.1 핵심 도메인

| 도메인 | 설명 | 대표 엔티티 |
| --- | --- | --- |
| 사용자·계정 | 일반 여행 사용자의 계정과 소셜 로그인 연결 | User, SocialAccount |
| 저장 일정 | 사용자가 저장한 여행 일정과 저장 당시의 조건 스냅샷 | Itinerary |
| 일정 항목 | 일정에 포함된 장소, 방문 순서, 이동 힌트, 추천 이유 | ItineraryItem |
| 일정 반응 | 사용자가 일정에 남긴 좋아요/싫어요 등 가벼운 반응 | PlanReaction |
| 관리자 권한·고위험 변경 | 역할·지역 할당, 2인 승인 요청, 실행 결과와 감사 추적 | RoleAssignment, RegionAssignment, HighRiskChangeRequest, AdminAuditLog |
| 수집·검색 보조 | RDB 원장이 아닌 DynamoDB/S3 vector/Lambda 관계 탐색 기반 검색·로그 보조 데이터 | ContentDocument, S3VectorIndex, RelationGraphSnapshot |
| Agent·로그 | Agent 실행, 비동기 작업, API 호출, 사용자 이벤트, 운영 trace | AgentRun, AsyncJob, EventLog |
| RAG 검색 | 검색 문서, chunk, embedding, metadata filter | RagDocument, RagChunk, S3VectorIndex |

## 2.2 사용자 데이터 개념 모델

사용자 데이터는 최종 상태를 보존해야 하는 원장 데이터와, 분석·디버깅에 필요한 일시 이벤트 데이터로 나눈다.

| 구분 | 저장소 | 저장 대상 | 저장하지 않는 대상 |
| --- | --- | --- | --- |
| 사용자 원장 | MySQL | 계정, 소셜 계정, 저장 일정, 일정 항목, 일정 반응 | 대화 전문, 민감 자유 입력 원문 |
| 사용자 이벤트 | DynamoDB | 로그인/로그아웃 이벤트, 추천 실행 이벤트, 일정 반응 클릭 이벤트, 화면 이벤트, 오류 로그 | 사용자 상태의 최종 원장, 삭제 권한이 필요한 본문 데이터 |
| 추천 검색 보조 | S3 vector index | 사용자 조건과 매칭할 콘텐츠 chunk 및 embedding | 사용자 개인정보, 대화 전문, 비공개 운영 메모 |
| 추천 관계 탐색 | Lambda 관계 탐색 보조 | 도시·축제·테마·인접 도시·이동 관계를 요청 시 또는 배치 사전계산으로 탐색 | 사용자 개인정보, 대화 전문, 최종 원장 데이터 |

## 2.3 개념 ERD

아래 ERD는 사용자 계정, 소셜 계정, 저장 일정, 일정 항목, 일정 반응의 관계를 나타낸다.

![Lovv RDB 개념 ERD](../../assets/images/database-rdb-concept-erd.png)
