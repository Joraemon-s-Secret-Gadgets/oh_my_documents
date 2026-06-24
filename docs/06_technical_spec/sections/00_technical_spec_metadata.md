# 로브 (Lovv) 기술 명세서

> 문서 버전: v0.5
> 문서 상태: 검토 중 (Review)
> 기준 문서: 요구사항 명세서 v1.7, 서비스 흐름 명세서 v0.2, 데이터 수집 계획서 v0.6, 데이터베이스 설계 명세서 v0.2, Agent 명세서 v0.4, API 명세서 v0.2

> **[PRD 반영 v0.1 — 대화형 빌더]** 핵심 기술 결정: **결정론 코드 Supervisor**(LLM 라우팅 아님) · 스텝별
> **병렬 fan-out**(Candidate∥지도API∥축제) · **AgentCore Memory checkpointer**(interrupt/resume) · 메모리
> 2계층(단기 AgentCore / 장기 DynamoDB TTL→S3) · **관측성**(OTel + AWS X-Ray + CloudWatch JSON Logs) ·
> 기반은 LangGraph/AgentCore(가이드의 Bedrock Agents는 패턴만 차용). 상세: `../98_prd/interactive_builder_prd.md`.
