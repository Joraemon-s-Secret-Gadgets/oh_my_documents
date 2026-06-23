# 데이터 저장소 결정 요약

> 문서 성격: 보조 Markdown
> 대표 문서: `04_database_design.md`
> 정리 기준: 이 문서는 저장소 선택 결정을 요약한 참고 문서이며, 데이터베이스 설계 정본은 `04_database_design.md`로 유지한다.

| 구분 | 결정 | 비고 |
| --- | --- | --- |
| RDBMS | MySQL 8 LTS | 서비스 핵심 관계형 데이터 저장소로 사용한다. |
| NoSQL | AWS DynamoDB | AgentCore와 SAM(Serverless Application Model) 로그를 적재한다. |
| RAG Vector Index | S3 vector 기능 활용 | 목적지·축제·관광지 chunk와 embedding index를 S3 vector 기능 기반으로 관리한다. 별도 벡터 DB 제품 도입은 기본 범위가 아니다. |
| 관계 탐색 보조 | Lambda + DynamoDB 인접 리스트 | 도시·축제·테마·장소 관계를 Lambda로 탐색해 추천 후보 확장과 관계 기반 재랭킹에 사용한다. Neptune은 고도화 승격 옵션으로만 둔다. |
