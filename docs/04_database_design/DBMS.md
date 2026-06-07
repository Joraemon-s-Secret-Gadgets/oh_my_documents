# 데이터 베이스에 대해서 정리

| 구분 | 결정 | 비고 |
| --- | --- | --- |
| RDBMS | MySQL 8 LTS | 서비스 핵심 관계형 데이터 저장소로 사용한다. |
| NoSQL | AWS DynamoDB | AgentCore와 SAM(Serverless Application Model) 로그를 적재한다. |
| RAG Vector Index | S3 vector 기능 활용 | 목적지·축제·관광지 chunk와 embedding index를 S3 vector 기능 기반으로 관리한다. 별도 벡터 DB 또는 그래프 DB 이관은 기본 범위가 아니다. |
