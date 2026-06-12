# Candidate Evidence Agent 도시 및 관광지 검색 테스트 계획서

> 문서 버전: v1.0  
> 문서 상태: 검토 중 (Review)  
> 문서 범위: 도시 선정 및 관광지·음식점 Candidate Evidence 검색  
> 기준 문서: `../05_agent_spec/candidate_evidence_agent.md`, `../05_agent_spec/candidate_evidence_baseline_comparison.md`  
> 현재 실행 근거: `../../../rag_test/`

# 1. 목적

본 문서는 Lovv 전체 통합 테스트 계획서가 아니다. `Candidate_Evidence_Agent`가 수행하는 **도시 선정과 관광지·음식점 Candidate Evidence 검색**만을 대상으로 현재 구현·실행된 평가를 정본화한다. 핵심 질문은 다음 세 가지다.

1. Baseline과 Ours를 같은 후보 예산과 실패 조건에서 비교할 수 있는가?
2. Ours에 추가된 각 요소가 설계 의도대로 동작하는가?
3. 그 요소가 통제된 조건에서 실제 결과 품질을 좋은 방향으로 바꿀 수 있는가?

현재 단계에서는 고정 정답 도시 기반 정확도보다 정성 비교와 요소별 인과 검증을 우선한다. 오픈 월드 검색에서는 정답 목록 밖의 합리적인 소도시가 선택될 수 있어 단일 city label이 오히려 평가를 왜곡할 수 있기 때문이다.

# 2. 테스트 범위와 경계

| 범위 | 현재 상태 | 검증 내용 |
| --- | --- | --- |
| Candidate retrieval | 구현·실행 | raw/soft 검색, 테마 filter, 중복 병합, AND gate |
| City/place scoring | 구현·실행 | similarity, entropy, sufficiency, distance, congestion, source quality |
| Candidate packaging | 구현·실행 | primary/reserve, min/soft max quota, fallback, audit |
| 오류·후보 부족 복원력 | 구현·실행 | AWS 예외 격리, `no_candidate`, `insufficient_candidates` |
| Planner itinerary | 범위 외 | 별도 Planner/E2E 테스트 계획에서 검증 |
| Festival verification | 범위 외 | 별도 Festival Verifier 테스트 계획에서 검증 |
| 전체 LangGraph trajectory | 범위 외 | 전체 Agent 통합 테스트 계획에서 검증 |
| 검색 결과 블라인드 선호 | 계획 | 도시와 장소 후보를 전략명 없이 pairwise 평가 |

Planner 일정 생성, Festival 검증, LangGraph 전체 trajectory, API E2E는 본 문서의 테스트 대상이 아니다. 해당 항목은 향후 Lovv 전체 테스트 계획이 확정될 때 `10_test_plan.md` 대표 문서의 상위 범위로 편입한다.

# 3. 비교 대상

## 3.1 공통 조건

Baseline과 Ours는 필수 테마별 검색, hard-theme AND gate, 일정별 후보 예산, 후보 충분성 fallback, 상태·오류 기록, primary rehydration을 공유한다.

## 3.2 차이

Baseline은 raw query similarity만 사용한다. Ours는 soft retrieval, raw/soft 병합, 다요소 place/city score, entropy balance, min quota, soft max quota, source quality, 거리와 혼잡도 신호를 추가한다.

상세 차이는 `../05_agent_spec/candidate_evidence_baseline_comparison.md`를 따른다.

# 4. 테스트 레이어

| 레이어 | 목적 | 현재 구현 |
| --- | --- | --- |
| L1 Resilience | 실패가 전체 실행을 중단하지 않는지 검증 | 5건 |
| L2 Strategy intent component | 각 전략 요소가 의도한 방향으로 반응하는지 검증 | 26건 |
| L3 Outcome quality | 외부 utility 기준으로 결과가 개선되는 통제 사례 검증 | 7건 |
| L4 AWS search integration | 실제 S3 Vector·DynamoDB에서 도시·관광지 검색 24개 시나리오 비교 | 24건 |
| L5 Human blind review | 장소 목록과 도시 선택을 전략명 없이 평가 | 계획 |
| 범위 외 연계 | Candidate Package가 실행 가능한 일정으로 이어지는지 평가 | 본 계획의 합격 기준에서 제외 |

## 4.1 Intent component와 outcome quality의 구분

두 로컬 테스트는 서로 다른 질문에 답한다.

| 테스트 | 질문 | 판정 대상 | 해석 제한 |
| --- | --- | --- | --- |
| Strategy intent component | 입력 변화에 점수·순위·audit가 설계 방향으로 반응하는가? | 내부 동작과 전략 계약 | 실제 추천 품질 향상을 직접 증명하지 않음 |
| Strategy outcome quality | 그 변화가 scorer 외부의 사용자 시나리오별 utility를 높이는가? | 선택 도시와 primary 결과 | 합성 fixture의 인과 예시이며 실제 개선 비율이 아님 |

원본 실행 보고서는 다음과 같다.

- `../../../rag_test/docs/report/strategy_intent_component_test_results.md`
- `../../../rag_test/docs/report/strategy_outcome_quality_test_results.md`

# 5. 데이터셋 설계

현재 `evaluation_testset.json`은 24건으로 구성한다.

| 케이스 범주 | 목적 |
| --- | --- |
| quiet/vibrant 대조쌍 | 같은 raw query에서 soft preference 방향성 확인 |
| 복수 필수 테마 | AND gate, entropy, quota와 최종 primary 구성 확인 |
| 출발지 변경 | distance signal 민감도 확인 |
| 일정 길이 변경 | primary/reserve 충분성과 장기 일정 희소성 확인 |
| 희소 조합 | 안전한 후보 부족·fallback 확인 |
| 오탈자·구어체 | embedding 검색 견고성 확인 |

각 케이스는 고정 정답 도시 대신 다음 정보를 가진다.

- 평가 목적
- 사용자 입력과 필수 테마
- 비교 초점
- 정성 pass criteria
- disqualifier

이 데이터셋은 통계적 대표 표본이 아니라 설계 위험을 드러내기 위한 시나리오 표본이다.

# 6. 평가 기준

## 6.1 결정적 기준

| 기준 | 기대값 |
| --- | --- |
| AWS·runtime 예외 격리 | 해당 케이스만 `error`, 다음 케이스 계속 실행 |
| 후보 없음 | `no_candidate` 반환, 프로세스 중단 없음 |
| 후보 부족 | `insufficient_candidates`와 failure signal 기록 |
| 동일 `place_id` 중복 | 더 좋은 distance를 유지해 한 후보로 병합 |
| 동일 title 중복 | quota 전에 제거하고 가능한 경우 slot 보충 |
| hard-theme AND gate | 필수 테마가 없는 도시 제외 |
| min quota | 가능한 범위에서 필수 테마 최소 수량 우선 배정 |
| soft max quota | 공급이 충분하면 한 테마가 primary 절반 초과 금지 |
| quota relaxation | primary slot이 비는 경우에만 완화하고 audit 기록 |

## 6.2 결과 품질 기준

| 항목 | 확인 질문 |
| --- | --- |
| vibe alignment | quiet/vibrant 의도가 도시와 장소에 드러나는가? |
| theme coverage | 최종 primary에 모든 필수 테마가 남아 있는가? |
| theme balance | 한 테마가 목록을 과도하게 독점하지 않는가? |
| evidence quality | 제목·좌표·도시·테마 등 근거 필드가 충분한가? |
| candidate sufficiency | Planner가 사용할 primary/reserve 예산을 충족하는가? |
| small-city discovery | 데이터가 많은 대표 도시만 반복 선택하지 않는가? |
| feasibility | 출발지, 일정 길이, 도시 내부 이동 부담이 합리적인가? |

Outcome quality fixture의 oracle은 scorer가 직접 사용하는 city/place score에서 읽지 않는다. 동일 raw 후보와 예산을 제공한 뒤, 도시 적합도·테마 coverage·primary theme entropy·독립 evidence quality label을 외부 utility로 계산한다. Ours의 utility가 Baseline보다 엄격하게 높을 때만 통과한다.

## 6.3 자원 기준

결과 품질과 함께 다음 비용을 반드시 기록한다.

- 쿼리당 평균·전체 실행 시간
- S3 Vector query 수
- 반환·고유·선택 도시 후보 수
- DynamoDB GetItem 추정 수
- 평균·최대 peak RSS 증가

# 7. 실행 절차

```powershell
python -m unittest discover -s rag_test\tests -p "test_*.py" -v
python rag_test\evaluate.py --testset-file rag_test\evaluation_testset.json --profile skn26_final
python rag_test\generate_raw_outputs.py
```

실행 산출물은 다음과 같다.

| 산출물 | 용도 |
| --- | --- |
| `evaluation_report.json` | 전략별 결과, latency, memory, retrieval metric |
| `baseline_raw_outputs.json` | Baseline Candidate Package 원본 |
| `ours_raw_outputs.json` | Ours Candidate Package와 quota audit 원본 |

# 8. 현재 합격 기준

## 8.1 PR 회귀 게이트

- 38개 로컬 결정적 테스트 100% 통과
- Python 문법 검사 통과
- 오류·후보 부족 케이스가 예외를 외부로 전파하지 않음
- quota audit 필수 필드 누락 0건

## 8.2 AWS 통합 게이트

- 24건 전체 실행 완료
- 미격리 실행 오류 0건
- 후보 부족은 실패 숨김 없이 상태와 audit로 기록
- Baseline/Ours에 동일 예산과 testset 적용

## 8.3 품질 판단 규칙

현재 비블라인드 정성 평가는 참고 근거이며 배포 차단 게이트로 사용하지 않는다. 최종 품질 게이트는 최소 2인의 블라인드 pairwise 평가와 평가자 일치도 확인 후 확정한다.

# 9. 회귀 전략

| 변경 유형 | 필수 재실행 |
| --- | --- |
| 검색 filter·dedup 변경 | L1, L2, AWS 24건 |
| score weight·entropy 변경 | L2, L3, AWS 24건, 도시 변경 diff |
| quota·candidate budget 변경 | L1, L2, L3, raw output audit diff |
| 데이터·index 변경 | AWS 24건 전체, 후보 수·도시 분포 비교 |
| Planner 연결 변경 | Candidate Package schema test, Planner/E2E |

데이터와 embedding index가 바뀌면 이전 JSON 산출물을 덮어쓰기 전에 실행 일자와 index version을 기록해야 한다. 동일 코드라도 외부 데이터 변경으로 결과가 달라질 수 있기 때문이다.

# 10. 상세 결과

2026년 6월 12일 기준 상세 결과는 `candidate_evidence_evaluation_results.md`에 기록한다. 요약은 다음과 같다.

- 로컬 결정적 테스트: `38/38` 통과
- AWS 시나리오: `24/24` 실행, 양쪽 전략 오류 0건
- 후보 예산 충족: Baseline `7/24`, Ours `17/24`
- 평균 실행 시간: Baseline `2.28초`, Ours `7.31초`
- 복수 테마 20건 중 soft max 준수 11건, 완화 9건
- 비블라인드 추천 내용 예비 판정: Ours 18건, Baseline 2건, 동률 4건

# 11. 한계

1. 24건은 통계적 일반화를 위한 표본이 아니다.
2. 고정 도시 정답이 없어 Hit Rate로 종합 우열을 판단할 수 없다.
3. 비블라인드 평가는 평가자 기대와 전략 정보에 영향을 받을 수 있다.
4. 합성 outcome-quality fixture는 인과 검증에는 유용하지만 실제 관광 품질을 증명하지 않는다.
5. theme taxonomy 오류는 entropy와 quota 결과를 동시에 왜곡한다.
6. AWS index와 원본 데이터가 변경되면 동일 코드의 결과도 달라질 수 있다.
7. 장소의 휴폐업, 영업시간, 계절 운영, 실제 이동 시간은 검증하지 않았다.
8. Candidate Evidence Package 품질과 최종 일정 품질은 동일하지 않다.

# 12. 보완 계획

| 단계 | 작업 | 완료 조건 |
| --- | --- | --- |
| 1 | theme taxonomy 표본 감사 | 오분류 유형과 수정 기준 문서화 |
| 2 | 2인 이상 블라인드 pairwise 평가 | 전략명 비공개, 평가자 일치도 산출 |
| 3 | 50~100건으로 시나리오 확장 | 테마·지역·일정·출발지 분포표 확보 |
| 4 | score·quota ablation | 각 요소 제거 전후 품질·비용 변화 기록 |
| 5 | distance·congestion sensitivity grid | weight 변화에 따른 rank 안정성 확인 |
| 6 | index snapshot/version 고정 | 재현 가능한 실행 식별자와 데이터 버전 기록 |
| 7 | Planner 테스트로 handoff | 이동 거리·운영시간 검증 요구사항을 별도 Planner 계획에 전달 |
| 8 | 운영 모니터링 | latency, fallback, shortfall, 사용자 피드백 추적 |

# 13. 변경 이력

| 버전 | 날짜 | 변경 내용 |
| --- | --- | --- |
| v1.0 | 2026-06-12 | `rag_test` 기반 도시·관광지 검색 비교·회귀·정성 평가 계획과 현재 합격 기준 정본화 |
