# 8. 품질 및 관측성

| 항목 | 기준 |
| --- | --- |
| 추천 처리 시간 | 멀티스텝 Agent 전체 8초 이내 목표 |
| RAG 검색 | 1초 이내 반환 목표 |
| 외부 API 실패 | 폴백 메시지와 부분 결과 제공 |
| 추천 품질 | 추천 이유와 출처를 함께 제공 |
| Agent 추적 | 노드명, next_node, matrix 상태, retry_count, fallback 여부, latency, token 사용량을 redacted trace로 기록 |
| 운영 추적 | 데이터 제안·검토·승인 이력 저장 |

## 8.1 Agent 런타임 경계

| 계층 | 기술 후보 | 책임 |
| --- | --- | --- |
| Runtime | LangGraph, AgentCore Runtime | Supervisor와 Sub-Agent 그래프 실행 |
| Memory | AgentCore Memory, DynamoDB | 세션 상태, 롤링 요약, `fulfilled_matrix`, 축제 검증 캐시 저장 |
| Gateway | Lambda/API 기반 Skill | Scoring, Matrix Transition, Validation, Link, Weather, Packaging 같은 결정적 Skill 실행 |
| Model | Amazon Bedrock Converse API | Sub-Agent별 LLM 추론과 모델 교체 추상화 |
| Retrieval | S3 vector 기반 RAG Index, Lambda 관계 탐색 보조 | 자연어·테마 임베딩 검색은 S3 vector, 도시·축제·테마 관계 탐색은 DynamoDB 인접 리스트, 사전계산 후보, Lambda 인메모리 그래프로 처리 |
| Evaluation | AgentCore Evaluations 또는 동등 하네스 | trajectory, 조건 충족, 근거성, 루프 안전성 회귀 평가 |
