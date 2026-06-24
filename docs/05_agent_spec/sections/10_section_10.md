# 10. 품질 검증 기준

| 검증 항목 | 기준 |
| --- | --- |
| 조건 충족 | 국가, 월, 일정 유형, active theme 반영 100% |
| 단일 목적지 | 최종 추천은 소도시 1곳 중심 |
| 축제 날짜 정확성 | 일정 배치 축제는 `confirmed` 100% |
| 국가 분리 | KR/JP 혼합 0건 |
| 루프 안전성 | `validation_retry_count <= 2` |
| 근거성 | 추천 이유가 DB/검색 근거와 연결 |
| 폴백 안전성 | 결측·실패 시 `confidence` 하향과 `user_notice` 포함 |
| 후보 없음 분기 | `no_candidate`는 검증 재시도와 분리해 즉시 안전 폴백 |
| 축제 검증 비용 | 축제 포함 요청은 Candidate Evidence Agent가 구성한 상위 도시/축제 후보 K건만 웹 검증 |

테스트 하네스는 `supplemental/agent_harness_design.md`를 따른다.
PR 단계는 결정적 L1/L2/L4 핵심 케이스를 우선하고, LLM 평가와 전체 trajectory 평가는 nightly 또는 릴리즈 게이트로 분리한다.

## 10.1 Candidate Evidence Agent 비교 검증

검색·후보 구성의 Baseline은 raw query similarity만 사용하는 단순 RAG로 정의한다. Ours는 동일한 hard-theme gate, 후보 예산, fallback 조건 위에 soft retrieval, 다요소 scoring, entropy balance, min quota와 soft max quota를 추가한다.

설계 차이와 현재 실험 근거는 `supplemental/candidate_evidence_baseline_comparison.md`를 따른다. 도시·관광지 검색 테스트 계획과 상세 결과의 정본은 `../10_test_plan/supplemental/candidate_evidence_search_test_plan.md`, `../10_test_plan/supplemental/candidate_evidence_evaluation_results.md`다.
