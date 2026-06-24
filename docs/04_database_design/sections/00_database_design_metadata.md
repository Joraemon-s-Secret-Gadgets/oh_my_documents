# 로브 (Lovv) 데이터베이스 설계 명세서

> 문서 버전: v0.7
> 문서 상태: 설계 진행중 (Designing)
> 기준 문서: 요구사항 명세서 v1.7, 데이터 수집 계획서 v0.7, Agent 명세서 v0.6, 기술 명세서 v0.4, API 명세서 v0.3
> 보조 문서: 데이터베이스 보존 기간·Neptune 비용 업데이트 초안, Neptune 대체 설계 명세서

> **[PRD 반영 v0.1 — 대화형 빌더 메모리]** 에이전트 상태/메모리를 2계층으로 둔다:
> **단기 = AgentCore Memory**(빌더 상태 `itinerary_builder` + 세션 + checkpoint, `event_expiry` 자동정리), **장기 = 커스텀 DynamoDB**(① 파생 개인화 프로필: 핫, TTL 없음 ② raw 이벤트: TTL→Streams→Lambda→S3 콜드).
> 매핑 테이블·raw PII는 어느 저장소에도 넣지 않고 별도 KMS·IAM, actorId=가명. 상세: `../98_prd/interactive_builder_prd.md`, 보존/TTL 라인: 보조 문서 `supplemental/database_design_retention_neptune_update.md` §0.
