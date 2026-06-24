# Candidate Evidence Agent 도시 및 관광지 검색 평가 결과 보고서

> 문서 버전: v1.2
> 문서 상태: 검토 중 (Review)  
> 실행일: 2026-06-12  
> 대상: Baseline Simple RAG vs Candidate Evidence Agent Ours  
> 평가 범위: 도시 선정 및 관광지·음식점 Candidate Evidence 검색  
> 문서 성격: 보조 Markdown
> 대표 문서: `../10_test_plan.md`
> 테스트 계획: `candidate_evidence_search_test_plan.md`  
> 원본 산출물: Evaluation report, Baseline/Ours raw output, Blind review result

# 1. 실행 구성

Baseline과 Ours에 동일한 24건 testset과 일정별 primary/reserve 예산을 적용했다. Baseline은 raw query 검색과 similarity ranking을 사용하고, Ours는 soft channel, 다요소 scoring, entropy, min quota와 soft max quota를 추가했다. 본 결과는 도시·관광지 검색 단계만 평가하며 Planner 일정, Festival 검증, 전체 LangGraph 통합 품질을 포함하지 않는다.

# 2. 로컬 결정적 테스트

실행 환경은 AWS 호출이 없는 로컬 결정론·합성 fixture다. component test는 설계 의도 반영을, outcome-quality test는 외부 quality oracle 기준의 결과 개선 가능성을 검증한다.

| 그룹 | 실행 | 통과 | 실패 |
| --- | ---: | ---: | ---: |
| Resilience | 5 | 5 | 0 |
| Strategy intent component | 26 | 26 | 0 |
| Strategy outcome quality | 7 | 7 | 0 |
| **전체** | **38** | **38** | **0** |

테스트 프로세스와 Python 문법 검사는 exit code `0`으로 완료됐다.

## 2.1 공통 기반과 Baseline 의도 검증

| 구분 | 검증 요소 | 결과 | 관측 내용 |
| --- | --- | --- | --- |
| 공통 | hard-theme AND gate | 통과 | 필수 테마가 하나라도 없는 도시는 similarity가 높아도 제외 |
| 공통 | `place_id` 중복 병합 | 통과 | 더 작은 cosine distance를 유지 |
| 공통 | primary/reserve 예산 | 통과 | 양쪽 전략에 동일한 일정별 예산 적용 |
| 공통 | 후보 충분성 fallback | 통과 | score winner가 부족하면 충분한 차순위 도시 선택 |
| 공통 | 후보 부족·빈 후보 | 통과 | `insufficient_candidates`, `no_candidate`로 중단 없이 기록 |
| 공통 | AWS/runtime 오류 격리 | 통과 | 직렬화 가능한 `error` 결과로 변환 |
| Baseline | raw similarity ranking | 통과 | 평균 raw similarity가 높은 도시 선택 |
| Baseline | soft channel 비사용 | 통과 | soft-only 후보가 결과에 영향 없음 |
| Baseline | raw Top-K 순서 | 통과 | cosine distance 오름차순으로 primary 구성 |

후보 예산과 fallback은 Ours만의 기능이 아니라 비교를 위한 공통 정책이다. Baseline은 visitor 통계, soft channel, 다요소 scoring과 quota를 사용하지 않는 단순 기준선으로 동작했다.

## 2.2 Ours 의도 component 결과

| 추가 요소 | 결과 | 관측 내용 |
| --- | --- | --- |
| soft-only 후보 확장 | 통과 | raw에 없는 soft 후보가 고유 후보 pool에 추가 |
| raw/soft evidence 병합 | 통과 | 동일 장소에 raw·soft distance를 함께 보존 |
| soft similarity place score | 통과 | soft match가 높은 장소의 점수 상승 |
| quiet/vibrant congestion | 통과 | quiet는 저혼잡, vibrant는 고혼잡 도시가 상대 상승 |
| entropy theme balance | 통과 | 동일 조건에서 `3:3` 분포가 `5:1`보다 높은 balance 획득 |
| min theme quota | 통과 | 점수가 낮은 필수 테마 후보도 primary에 유지 |
| soft max quota | 통과 | 공급이 충분하면 테마별 primary가 절반 상한 이내 |
| max quota relaxation | 통과 | slot이 비는 경우에만 상한 완화 및 audit 기록 |
| title 선제 중복 제거 | 통과 | quota 전에 제거하고 고유 후보로 slot 보충 |
| 후보 충분성 tier·score | 통과 | primary tier fallback과 sparse 도시 감점 확인 |
| 방문객 통계 누락 | 통과 | 누락 도시를 중립 congestion index `0.5`로 처리 |
| 출발지·도시 내부 거리 | 통과 | 먼 도시와 도시 중심에서 먼 장소에 감점 적용 |
| source quality | 통과 | 핵심 metadata가 충분한 장소의 점수 상승 |
| audit 구조 | 통과 | score, fallback, retrieval, count, warning 필드 확인 |

이 결과는 Ours의 각 요소가 의도한 방향으로 동작한다는 근거다. 실제 관광지 정확성이나 최종 일정 품질을 보장하는 결과로 해석하지 않는다.

# 3. AWS 24건 결과

| 항목 | Baseline | Ours |
| --- | ---: | ---: |
| 정상 후보 예산 충족 | 7 | 17 |
| 후보 부족 | 17 | 7 |
| 실행 오류 | 0 | 0 |
| 후보 충분성 fallback | 5 | 19 |
| 전체 실행 시간 | 54.61초 | 175.49초 |
| 평균 실행 시간 | 2.28초 | 7.31초 |
| 평균 peak RSS 증가 | 4.149MiB | 4.108MiB |
| 최대 peak RSS 증가 | 7.137MiB | 5.297MiB |

# 4. 검색·조회 비용

| 항목 | Baseline 전체 / 평균 | Ours 전체 / 평균 |
| --- | ---: | ---: |
| S3 Vector query | 45 / 1.88 | 90 / 3.75 |
| 검색 반환 후보 | 2,250 / 93.75 | 4,500 / 187.50 |
| 고유 후보 | 2,250 / 93.75 | 3,966 / 165.25 |
| AND gate 생존 도시 | 355 / 14.79 | 499 / 20.79 |
| 선택 도시 후보 | 290 / 12.08 | 463 / 19.29 |
| DynamoDB GetItem 추정 | 187 / 7.79 | 711 / 29.62 |

Ours는 평균적으로 더 많은 evidence를 확보했지만 실행 시간은 약 3.2배, DynamoDB GetItem 추정은 약 3.8배였다. 메모리 차이는 이번 실행에서 크지 않았다.

# 5. Theme balance와 quota

복수 테마 요청 20건의 audit 결과는 다음과 같다.

| 결과 | 건수 | 의미 |
| --- | ---: | --- |
| soft max quota 준수 | 11 | 충분한 공급에서 한 테마가 primary 절반을 넘지 않음 |
| soft max quota 완화 | 9 | cap 때문에 slot이 빌 때 추천 수 보존을 위해 완화 |
| minimum quota shortfall | 3 | 해당 테마 후보 자체가 최소량보다 부족 |
| title 중복 제거·보충 | 4 | 같은 title 후보 제거 후 차순위 고유 후보로 보충 |

대표 균형 사례:

- TC-001, TC-002, TC-019: 바다·미식 `5:5`
- TC-020: 역사·자연 `5:5`
- TC-021: 예술·미식 `5:5`
- TC-024: 자연·미식 `5:5`

대표 완화 사례:

- TC-003: 역사·미식 `1:9`
- TC-005: 자연·미식 `3:7`
- TC-006: 자연·미식 `2:8`
- TC-022: 자연·역사·미식 `3:2:9`

완화는 후보 수를 보존하기 위한 의도된 동작이다. 반면 minimum quota shortfall은 데이터 공급 부족 신호이므로 Planner confidence와 사용자 안내에 연결해야 한다.

# 6. 결과 품질 검증

7개 합성 outcome-quality 테스트에서는 scorer가 직접 사용하지 않는 외부 quality oracle을 정의했다. 동일한 raw 후보와 후보 예산에서 Ours utility가 Baseline보다 엄격하게 높을 때만 통과하며, 7개 모두 이 조건을 충족했다.

| ID | 요소 | Baseline 결과 | Ours 결과 | 외부 품질 판정 |
| --- | --- | --- | --- | --- |
| Q-01 | soft channel | raw similarity가 높은 일반 도시 | soft preference target 도시 | target city utility 상승 |
| Q-02 | congestion | 동률인 혼잡 도시 | quiet 요청의 저혼잡 도시 | quiet-fit utility 상승 |
| Q-03 | origin distance | 입력 순서상 먼 도시 | 사용자 출발지 인근 도시 | trip feasibility 상승 |
| Q-04 | entropy balance | raw similarity가 조금 높은 `5:1` 도시 | `3:3` 균형 도시 | multi-theme utility 상승 |
| Q-05 | min quota | primary theme coverage `0.5` | coverage `1.0` | hard-theme 활용 가능성 상승 |
| Q-06 | source quality | metadata가 빈약한 고유사도 장소 | 근거 필드가 충분한 장소 | evidence quality 상승 |
| Q-07 | soft max quota | primary 분포 `8:2` | primary 분포 `5:5` | normalized theme entropy 상승 |

이는 각 요소가 품질을 개선할 수 있는 통제 조건을 보여준다. 실제 데이터 전체에서의 개선 비율을 의미하지는 않는다.

entropy와 quota는 서로 다른 품질 문제를 해결한다. entropy는 도시 ranking의 후보 분포를, min quota는 선택 도시 primary의 필수 테마 coverage를, soft max quota는 primary 비율 편중을 개선한다.

# 7. 24건 정성 검토

전략명을 알고 장소명과 assigned theme을 검토한 예비 판정은 다음과 같다.

| 판정 | 건수 |
| --- | ---: |
| Ours 우세 | 18 |
| Baseline 우세 | 2 |
| 동률 | 4 |

최신 raw output의 선택 도시와 primary theme 구성은 다음과 같다. 판정은 전략명을 알고 수행한 기존 예비 검토이며, quota 변경 후에도 기존 판정을 유지해 기록한 것이다. 최종 판정은 블라인드 재평가가 필요하다.

| Case | Baseline 도시 / primary 구성 | Ours 도시 / primary 구성 | 예비 판정 |
| --- | --- | --- | --- |
| TC-001 | 강릉 / 미식 10 | 고성 / 바다 5, 미식 5 | Ours |
| TC-002 | 강릉 / 미식 10 | 강릉 / 바다 5, 미식 5 | Ours |
| TC-003 | 평창 / 미식 10 | 평창 / 역사 1, 미식 9 | Ours |
| TC-004 | 평창 / 미식 10 | 강릉 / 역사 5, 미식 5 | Ours |
| TC-005 | 예천 / 자연 1, 미식 1 | 강릉 / 자연 3, 미식 7 | Ours |
| TC-006 | 예천 / 자연 1, 미식 1 | 강릉 / 자연 2, 미식 8 | Ours |
| TC-007 | 강릉 / 예술 1, 미식 9 | 강릉 / 예술 5, 미식 5 | Ours |
| TC-008 | 강릉 / 예술 1, 미식 9 | 강릉 / 예술 5, 미식 5 | Ours |
| TC-009 | 삼척 / 자연 2, 바다 8 | 고성 / 자연 3, 바다 7 | Ours |
| TC-010 | 삼척 / 자연 2, 바다 8 | 강릉 / 자연 3, 바다 7 | Ours |
| TC-011 | 홍천 / 자연 5 | 홍천 / 자연 6 | 동률 |
| TC-012 | 영덕 / 자연 3 | 청송 / 자연 5 | Ours |
| TC-013 | 동해 / 자연 2 | 울릉 / 자연 2 | Baseline |
| TC-014 | 인제 / 자연 1 | 영양 / 자연 4 | Ours |
| TC-015 | 양양 / 바다 6 | 양양 / 바다 4, 휴양 2 | Ours |
| TC-016 | 양양 / 바다 6 | 양양 / 바다 4, 휴양 2 | Ours |
| TC-017 | 안동 / 역사 6, 자연 4 | 안동 / 역사 5, 자연 5 | 동률 |
| TC-018 | 안동 / 역사 6, 자연 4 | 안동 / 역사 5, 자연 5 | 동률 |
| TC-019 | 양양 / 바다 1, 미식 9 | 양양 / 바다 5, 미식 5 | Ours |
| TC-020 | 경주 / 역사 4, 자연 6 | 경주 / 역사 5, 자연 5 | Baseline |
| TC-021 | 강릉 / 미식 10 | 강릉 / 예술 5, 미식 5 | Ours |
| TC-022 | 양양 / 자연 1, 역사 2, 미식 11 | 평창 / 자연 3, 역사 2, 미식 9 | Ours |
| TC-023 | 영천 / 예술 4, 휴양 2 | 강릉 / 예술 7, 휴양 2 | 동률 |
| TC-024 | 평창 / 자연 1, 미식 9 | 평창 / 자연 5, 미식 5 | Ours |

주요 Ours 강점은 다음과 같다.

- Baseline Top-K에서 사라지던 필수 테마를 primary에 유지했다.
- quiet/vibrant 대조에서 도시 score winner가 기대 방향으로 달라졌다.
- TC-019, TC-021, TC-024 등에서 최종 장소 목록의 테마 설명력이 개선됐다.
- 오탈자·구어체 입력에서도 복수 테마 의미를 유지했다.

Baseline이 낫거나 동률인 사례도 있었다. 일부 Ours 결과는 theme taxonomy가 설득력이 낮았고, 장거리·장기 일정에서는 데이터 부족을 해결하지 못했다.

# 8. 블라인드 LLM judge 평가

비블라인드 예비 판정의 편향을 줄이기 위해 Blind review runner로 전략명을 숨긴 A/B pairwise 평가를 수행했다. 각 24개 케이스는 A/B 순서 편향을 확인하기 위해 `main`, `reverse` 두 pair로 평가했으며, judge 모델은 `gpt-4o-mini`를 사용했다.

## 8.1 실행 요약

| 항목 | 결과 |
| --- | ---: |
| 평가 pair | 48 |
| 케이스 | 24 |
| judge 오류 | 0 |
| Ours 승 | 19 |
| Baseline 승 | 0 |
| 동률 | 5 |
| invalid | 0 |
| order-sensitive case | 0 |
| Baseline disqualifier | 13 |
| Ours disqualifier | 1 |

블라인드 조건에서도 Baseline이 단독 승리한 케이스는 없었다. Ours는 19건에서 우세했고, 5건은 동률이었다. A/B 순서에 따라 전략 winner가 뒤집힌 케이스는 없었다.

## 8.2 차원별 평균

| 평가 차원 | Baseline | Ours | 차이 |
| --- | ---: | ---: | ---: |
| hard theme validity | 0.9375 | 1.9792 | +1.0417 |
| vibe alignment | 1.1667 | 1.8542 | +0.6875 |
| theme balance | 1.0000 | 1.9375 | +0.9375 |
| candidate sufficiency | 0.5000 | 1.6875 | +1.1875 |
| spatial coherence | 1.1458 | 1.9167 | +0.7709 |
| small city discovery | 1.5417 | 1.9792 | +0.4375 |

가장 큰 차이는 후보 충분성, 필수 테마 validity, 테마 균형에서 나타났다. 이는 Ours가 단순히 다른 도시를 선택한 것이 아니라 최종 primary/reserve 후보 패키지에서 Planner가 사용할 수 있는 근거를 더 잘 유지했다는 신호다.

## 8.3 케이스별 판정

| 판정 | 케이스 |
| --- | --- |
| Ours | TC-001, TC-002, TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009, TC-010, TC-011, TC-014, TC-017, TC-018, TC-019, TC-021, TC-022, TC-023, TC-024 |
| Baseline | 없음 |
| 동률 | TC-012, TC-013, TC-015, TC-016, TC-020 |

동률 케이스는 대체로 두 유형이었다. TC-012, TC-013은 장기 또는 자연 중심 일정에서 양쪽 모두 후보 부족 문제가 있어 동률로 판정됐다. TC-015, TC-016, TC-020은 두 패키지 모두 visible evidence 수준에서 충분히 양호하다고 판단된 케이스다.

## 8.4 해석

블라인드 judge는 Ours의 장점을 다음 항목에서 반복적으로 인식했다.

- Baseline Top-K에서 누락되던 필수 테마가 Ours primary에 남아 있었다.
- Ours는 후보 수와 reserve를 더 충분히 확보했다.
- quiet/vibrant soft preference가 도시와 장소의 분위기에 더 잘 드러났다.
- min quota와 soft max quota 덕분에 복수 테마 편중이 줄었다.
- 선택 도시 안에서 장소들이 더 자연스럽게 묶이는 것으로 평가됐다.

따라서 현재 근거는 "동일 24개 정성 시나리오에서, 더 많은 검색·조회 비용을 허용할 경우 Ours가 Baseline보다 Candidate Evidence Package 품질이 높다"는 결론을 지지한다.

## 8.5 블라인드 평가 한계

LLM judge는 실제 사용자가 아니며, 설명이 풍부한 장소나 명시적 테마 분포를 과대평가할 수 있다. 또한 최초 실행에서는 `qualitative_expectation.pass_criteria` 일부에 `Ours`라는 단어가 남아 있었다. A/B 매핑 자체는 노출되지 않았지만 strict blind 조건에는 맞지 않는다. 이후 Blind review runner는 `Ours`, `Baseline` 텍스트를 중립 표현으로 치환하도록 수정했으므로, 최종 품질 근거로는 sanitized 재실행 결과를 우선 사용한다.

상세 블라인드 보고서와 명세는 평가 산출물로 별도 관리하며, 본 정본에는 핵심 결과와 해석 경계만 반영한다.

# 9. 핵심 한계

## 9.1 높은 fallback 비율

Ours는 `19/24`에서 score winner와 최종 selected city가 달랐다. 소도시 score winner가 후보 예산을 채우지 못해 데이터가 풍부한 도시로 교체되는 경우가 많았다. 이는 소도시 발견 목표와 Planner 사용 가능 후보 수 사이의 구조적 trade-off다.

## 9.2 Theme taxonomy

전망대의 예술 태그, 일부 뮤지엄의 역사 태그처럼 사람이 읽었을 때 설득력이 낮은 분류가 있었다. taxonomy가 틀리면 hard gate, entropy, quota가 모두 잘못된 신호를 강화한다.

## 9.3 거리·혼잡도 민감도

출발지를 서울에서 대구로 바꿔도 같은 도시가 선택된 사례가 있었다. 반대로 congestion weight가 다른 품질 신호를 과도하게 누를 가능성도 있다. 가중치 sensitivity test가 필요하다.

## 9.4 실제 방문 가능성 미검증

영업시간, 휴폐업, 계절 운영, 대중교통, 장소 간 실제 이동 시간은 평가하지 않았다. Candidate Package 수준의 품질과 실제 여행 일정 품질을 구분해야 한다.

## 9.5 평가 편향과 재현성

비블라인드 정성 판정은 설계자 기대에 영향을 받을 수 있고, LLM judge는 실제 사용자 선호를 대체하지 못한다. testset도 24건뿐이다. AWS index가 갱신되면 후보와 도시가 달라질 수 있다. index snapshot, strict blind 재실행, human blind review가 필요하다.

합성 quality oracle은 테스트 작성자가 정한 시나리오별 가치 판단이다. 따라서 outcome-quality `7/7` 통과를 실제 데이터에서 Ours가 항상 우수하다는 비율로 사용해서는 안 된다. 실제 theme taxonomy, 휴폐업·계절성, 여러 score 요소가 충돌할 때의 가중치, fallback에 의한 도시 교체와 실제 사용자 선호는 별도 검증 대상이다.

# 10. 보완 권고

1. `min_quota_shortfalls`가 있으면 Candidate Package confidence를 하향한다.
2. fallback 전에 부족한 테마만 추가 retrieve하는 제한적 보충 검색을 실험한다.
3. theme taxonomy를 층화 표본으로 사람이 감사하고 오분류율을 기록한다.
4. strict blind LLM judge를 `blind_eval_sanitized` 기준으로 재실행한다.
5. Baseline/Ours 이름을 숨긴 2인 이상 human pairwise 평가를 수행한다.
6. distance와 congestion weight를 grid로 변경해 rank 안정성과 품질을 함께 비교한다.
7. 데이터·index version을 결과 JSON에 기록해 회귀 실행을 재현 가능하게 만든다.
8. Planner 단계에서 이동 거리, 운영시간, 식사 슬롯, 대체 일정까지 평가한다.

# 11. 결론

현재 근거는 Ours가 Baseline보다 항상 우월하다는 일반적 증명이 아니다. 다만 Ours가 추가 비용을 사용해 soft preference를 반영하고, 더 많은 evidence를 고려하며, 최종 primary의 필수 테마 누락과 편중을 줄였다는 점은 결정적 테스트, 24건 정성 검토, 블라인드 LLM judge에서 일관되게 관찰됐다.

다음 품질 결론은 strict blind 재실행, human blind review, taxonomy 감사, index version 고정, Planner-level 평가가 완료된 뒤 확정한다.

# 12. 변경 이력

| 버전 | 날짜 | 변경 내용 |
| --- | --- | --- |
| v1.2 | 2026-06-13 | 외부 평가 하네스 파일 경로 직접 참조를 제거하고 산출물 유형과 결과 해석 중심으로 정리 |
| v1.1 | 2026-06-12 | 블라인드 LLM judge 평가 결과와 strict blind 한계·보완 계획 반영 |
| v1.0 | 2026-06-12 | 도시·관광지 검색 평가 결과와 한계 정본화 |
