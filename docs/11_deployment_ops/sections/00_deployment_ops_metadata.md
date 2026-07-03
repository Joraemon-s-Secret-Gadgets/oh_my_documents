# 로브 (Lovv) 배포·운영 가이드

> 문서 버전: v0.5
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-12
> 작성자: llm팀
> 기준 문서: `../06_technical_spec/06_technical_spec.md`, `../07_api_spec/07_api_spec.md`, `../08_data_preprocessing/data_preprocessing_plan.md`, `../04_database_design/04_database_design.md`, `supplemental/troubleshooting.md`

---

> **[PRD 반영 v0.1 — 대화형 빌더]** 관측: **OTel + AWS X-Ray + CloudWatch Structured JSON Logs**로
> 노드별 토큰·컨텍스트·레이턴시·I/O 트레이싱(정본: `Lovv-agent/docs/specs/LOVV_AGENTCORE_OBSERVABILITY_SPEC.md`).
> CI/CD: 기존 게이트(pytest·compileall·parity·`agentcore validate`/`deploy --dry-run`) + 빌더 게이트
> (무상태 회귀·state serde round-trip·geo-filter·soft floor 폴백·정합성 게이트·interrupt/resume 스모크).
> 상세: `../98_prd/interactive_builder_prd.md`.
