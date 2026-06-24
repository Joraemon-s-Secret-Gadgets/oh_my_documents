# 로브 (Lovv) Agent 명세서

> 문서 버전: v0.15
> 문서 상태: 검토 중 (Review)
> 기준 문서: 요구사항 명세서 v1.7, 서비스 흐름 명세서 v0.2, 데이터 수집 계획서 v0.7, 데이터베이스 설계 명세서 v0.5, 기술 명세서 v0.3, API 명세서 v0.2
> 상세 정본: `supplemental/langgraph_flow.md`, `supplemental/intent_agent.md`, `supplemental/candidate_evidence_agent.md`, `supplemental/candidate_evidence_baseline_comparison.md`, `supplemental/planner_agent.md`, `supplemental/agent_harness_design.md`

> **[PRD 반영 v0.1 — 대화형 빌더]** 일정 생성 단계를 자동 배치에서 **사용자 주도 HITL 반경 루프**로
> 전환한다(소도시 선정까지는 유지). 주요 변경: ① Candidate Evidence **3층 분해**(공유 코어 + 도시선정
> 1회 + 반경 Provider 루프, 게이트 `city｜radius`) ② **Intent action 어휘**(PICK·REPLACE_PLACE·
> EXCLUDE·FILTER·DONE) + **Profile Agent 분리·Lock** ③ Planner = **Geo-Filter**(동선=선택 순서)
> ④ 결정론 Supervisor·스텝 병렬 fan-out 유지. 근거·상세: `../98_prd/interactive_builder_prd.md`.
