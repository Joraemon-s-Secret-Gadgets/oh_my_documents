# Lovv Agent V2 — 아키텍처 검증 계획 (전반)

> 문서 성격: 보조 Markdown (V2 스냅샷 묶음 = `supplemental/v2/`)
> 대표 문서: `../../05_agent_spec.md`
> 정본 위치: `Lovv-agent/docs/reports/v2/V2_10_VERIFICATION_PLAN.md` (공유용 스냅샷)
> 연관: `architecture_final.md` · `intent_parsing_spec.md`(Intent 세부) · `../../../10_test_plan/10_test_plan.md`

## 0. 먼저 — 검증의 전제는 "계측"이다
측정할 수 없는 것은 검증할 수 없다. 아래 계측이 선결.

| 계측 항목 | 어디서 | 쓰는 곳 |
|---|---|---|
| 점수 분해 로깅(score_city/score_place 각 항) | scoring/Planner | 스코어 회귀·단조성·분포 |
| seed id 기록 | scoring | seed 결정성·보존 |
| response_status + userNotice 사유 코드(enum) | Packager | E2E 상태·엣지 |
| 재인출 파라미터(top_k·거리·필터) | retrieval/Planner | 수정 루프 |
| execution_mode·플래그 | Intent | 분기 |
| LLM 비결정 통제(temperature·seed 고정 or 캡처) | LLM 노드 | 결정성 |

> 착수 1순위 = 구조화 로깅 + 사유 코드 enum.

## 1. 검증 유형
U 단위·결정론 / G 라벨셋·골든셋 / M 메트릭·분포 / J LLM-judge+휴먼 / I 통합(계약, 의존 mock) / E E2E / R 회귀(V1).

## 2. 노드별 검증
| 노드 | 항목 | 유형 | 방법 / 합격(초안) | 난이도 |
|---|---|---|---|---|
| Intent | 파싱·분기·플래그 | U+G+J | `intent_parsing_spec.md` 부록 A | 중 |
| Supervisor | 분기·라우팅·response_status | U | 조합 단위테스트 100% | 하 |
| retrieval_node | 검색·merge·prune·재인출 | I+U | mock S3, 파라미터 단언 | 중 |
| **scoring_and_selection** ★ | score_city·soft 게이트·capacity 제거·seed·transport/geo | M+U+G | 항별 단조성 단위 · 골든 도시셋(top-1/k) · **soft vs AND 기준선**(소도시 생존율↑) · seed 결정성 | 상 |
| Festival Verifier | 날짜 검증·테마 정합 | U+G | 날짜 교차 100%, 정합 라벨셋(데이터 후) | 중 |
| **Planner** ★ | 2-pass·seed 배치·geo·다건 일괄 재배치·Plan B·weather 룰 | U+M | 구조 단언(seed anchor·≤3) · 동선 haversine<FIFO · **배치 순서 독립** · weather 룰 단위 | 상 |
| Response Packager | 스키마·status·interrupt | U | 스키마 100%, 평시 alt/notice=null | 하 |
| Profile Agent | read·저장 기반 write·fallback | U+I+G | 저장 시에만 write 단언, fallback n 경계 | 중 |
| Memory | checkpoint/resume·TTL·세션 avoid | I | resume 왕복 동치, avoid TTL | 중 |

## 3. 데이터 계약 검증 (I + U)
스키마 validation(candidate_sufficiency 부재·theme_weights·seed·transport_pref·alternativeItinerary/weatherNotice nullable·modification_pending·saved_trip_count) · 직렬화 왕복 · front 호환 계약(필드 추가가 기존 파서 안 깸, move 미채움 단언).

## 4. 결정 준수 테스트
| 결정 | 준수 단언 | 유형 |
|---|---|---|
| D-A | 평시 alt=null, 자동 사전 생성 0 | U+E |
| D-B | seed 불변·≤3·추가/삭제 없음·도시변경=경로만 | U |
| 배치 편집 | 다건 분해·부분 적용+안내·모순 되묻기 | U+E |
| D-K | 저장 시에만 write·수정 누적 0·fallback n 경계 | U |
| D-E | walk 페널티↑/car 완화 방향성 | M |
| D-J | 임계 룰대로 발동(수치 추후) | U |
| soft 게이트 | 부분 충족 생존·완전 0매칭만 no_candidate | M+G |
| capacity 제거 | candidate_sufficiency 미사용 | U |
| 기피 | 세션 avoid TTL·영구 미반영 | I |
| 응답상태 | modification_pending 1개만 | U |
| 되묻기 | 모순 → 절충 0 | G |

## 5. E2E 시나리오 (SC-* 골든 트레이스, 핵심 8~9개)
| SC | 검증 포인트 | 유형 |
|---|---|---|
| SC-00/G2 | move 채움(front)·seed anchor·completed | E+U |
| SC-G1 멀티테마 | soft 게이트 소도시 생존(AND 대비↑) | E+M |
| SC-G3 축제 | confirmed만·날짜 분산·미확정 userNotice | E |
| SC-R1/R3 | Pass2 축소↓ / 완전 0매칭만 END_WAIT | E+M |
| SC-02 날씨 | weatherNotice 발동·primary 유지·자동 Plan B 0 | E+U |
| SC-03 슬롯 교체 | 해당 슬롯만·seed 불변·modification_pending | E+U |
| 다건 동시 | 분해·일괄 재배치·부분 적용+안내 | E |
| SC-M4 리셋 | avoid·차순위 재생성 | E+I |
| SC-N2 모순 | 절충 없이 되묻기 | E+G |

## 6. 검증 난이도 → 우선순위
- 결정론(쉬움·0허용): execution_mode·Supervisor 라우팅·스키마·seed 보호·배치 ≤3·capacity 제거·weather 룰.
- 분포(중·기준선 대비): score_city·soft 생존율·동선 haversine·transport 방향성. **기준선(V1/AND/FIFO) 동시 실행 필수.**
- 정성(어려움·judge+스팟): 모순·범위밖·무드·대화 E2E.
> 비결정 노드: 스키마는 결정론, 의미는 judge로 이원화. LLM 호출 seed/temperature 고정 or 캡처.

## 7. 실행 지침
검증 프레임워크를 코드보다 먼저 짓지 말 것. 1순위 = §0 계측 → thin slice 코드와 나란히 단위·계약 테스트 → 골든셋·E2E·judge는 기능 가동 후. 측정 가능하게 만든 뒤 기준선과 비교하라.
