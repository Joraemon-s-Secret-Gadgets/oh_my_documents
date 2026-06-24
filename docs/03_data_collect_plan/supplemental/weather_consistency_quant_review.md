# 데이터 수집 계획서 검토 — 날씨 데이터 활용·정합성 정량화 초안

> 문서 성격: 보조 Markdown
> 대표 문서: `../03_data_collect_plan.md`

> 보조 문서 (AGENT.md 워크플로 기준 초안)
> 대상 원본: `../03_data_collect_plan.md`, `korea_data_acquisition_plan_updated.md`, `japan_data_acquisition_plan.md`
> 작성일: 2026-06-08
> 상태: Review 대기 (파라미터 확정 후 대표 문서 반영)

지적사항:
> 날씨 관련해서 한국·일본 날씨 데이터를 어떻게 활용할지, 정합성을 어떻게 맞출지
> 수식 또는 정량적 지표가 나오면 좋을 것으로 사료됨.

---

## 1. 현재 문서 검토 결과

### 1.1 "표에서 취득" 여부 — 반영됨

날씨(기후) 데이터를 표에서 취득한다는 내용은 명시되어 있다.

| 위치 | 내용 |
| --- | --- |
| `../03_data_collect_plan.md` L61 | "Wikipedia 기후 표는 `climate_table`로 보존하고 자동 취득 실패 시 `needs_review`로 관리" |
| `../03_data_collect_plan.md` L73 | climate: 한국=Wikipedia 취득 후 기상청 API허브·기후통계 비교 / 일본=Wikipedia 취득 후 JMA 비교 |
| `../03_data_collect_plan.md` L123·136 | 기상청·JMA 월별 기후(평균 기온·강수량·계절 메모) 비교 검증 |
| `korea_..._updated.md` L70·263~271 | `climate_table`(Wikipedia 기후 표 wikitext) + 기상청 보완, "계절 추천 지표 산출에 사용" |
| `japan_..._plan.md` L57·159·347 | Wikipedia climate + JMA 비교, 불일치 검수 메타데이터 기록 |

→ 취득원: **Wikipedia 기후 표**(기준값) + **기상청/JMA**(비교·보완). 확인됨.

### 1.2 미흡 — 활용 방식·정합성의 정량 정의 부재

| 항목 | 현재 상태 | 판정 |
| --- | --- | --- |
| 날씨 데이터 활용 방식 | "월별 추천 근거", "계절 추천 지표 산출" 언급만, 산식 없음 | 정성적, 정량화 필요 |
| 정합성 기준 | "기상청/JMA와 비교해 불일치 여부 기록"(L202·237·347·377) | 임계값·점수·수식 없음 |
| 한·일 비교 가능성 | 국가별 출처만 명시, 단위·기준연도·관측소 매핑 정규화 기준 없음 | 정량 기준 필요 |

신뢰도 안내: 아래 수식·파라미터는 **권고 기본값**이며, 표본 데이터로 보정해 확정해야 한다.
(권고값 신뢰도: 중)

---

## 2. 날씨 데이터 정규화 기준 (한·일 공통)

국가 간 비교가 가능하려면 취득값을 공통 스키마로 정규화한다.

| 항목 | 기준 |
| --- | --- |
| 기온 단위 | °C (월평균 기온 `t_avg_m`) |
| 강수 단위 | mm/월 (월 강수량 `precip_m`) |
| 기준 기간 | 평년값(climatology) 동일 기간 권고: 1991–2020. 출처별 상이 시 메모 |
| 관측소 매핑 | `city_id` ↔ 대표 관측소 1개(최근접 또는 대표). 거리 `d_station_km` 기록 |
| 결측 처리 | 표 취득 실패 시 `needs_review`, 공식 자료로 대체 시 `source=official` 표기 |

표기: 월 인덱스 `m ∈ {1..12}`, Wikipedia 취득값 `*_wiki`, 공식(기상청/JMA) 값 `*_off`.

---

## 3. 정합성(일치도) 정량 지표

Wikipedia 기후 표와 공식 자료(기상청/JMA)의 월별 값을 비교한다.

### 3.1 월별 오차

- 기온 절대오차: `eT_m = |t_avg_wiki,m − t_avg_off,m|` (°C)
- 강수 상대오차: `eP_m = |precip_wiki,m − precip_off,m| / max(precip_off,m, ε)` (ε=5mm, 0 나눗셈 방지)

### 3.2 연간 집계

- 기온 평균절대오차: `MAE_T = (1/12) Σ eT_m`
- 강수 평균절대백분율오차: `MAPE_P = (1/12) Σ eP_m`

### 3.3 정합성 점수 (0~100)

정규화 후 가중합으로 단일 점수를 만든다.

```
nT = min(MAE_T / τ_T, 1)        # τ_T = 3.0 °C (기온 허용 상한)
nP = min(MAPE_P / τ_P, 1)        # τ_P = 0.40 (강수 40% 허용 상한)
ConsistencyScore = 100 × (1 − (wT·nT + wP·nP))   # wT=0.6, wP=0.4
```

### 3.4 판정 규칙

| 조건 | 상태 | 처리 |
| --- | --- | --- |
| `MAE_T ≤ 1.5` 그리고 `MAPE_P ≤ 0.20` | `verified` | Wikipedia 값 채택 |
| 위 미달이나 `ConsistencyScore ≥ 60` | `needs_review` | 검수 후 채택/보정 |
| `ConsistencyScore < 60` 또는 표 취득 실패 | `rejected` | 공식 자료를 기준값으로 대체 |

검수 메타데이터에 `MAE_T`, `MAPE_P`, `ConsistencyScore`, `status`, `d_station_km`, `base_source`를 기록한다.

---

## 4. 활용 — 월별 여행 적합도(계절 추천 지표)

정합성 통과 값으로 도시·월별 적합도 점수를 산출해 `recommended_months`·`seasonal_fit` 근거로 쓴다.

### 4.1 기온 쾌적도

```
T_score_m = max(0, 1 − |t_avg_m − T_ideal| / T_span)
# T_ideal = 20 °C, T_span = 15  → 5°C 이하·35°C 이상에서 0
```

### 4.2 강수 패널티

```
P_score_m = max(0, 1 − precip_m / P_cap)     # P_cap = 300 mm/월
```

### 4.3 월별 적합도 (0~100)

```
ComfortScore_m = 100 × (α·T_score_m + β·P_score_m)   # α=0.6, β=0.4
```

(선택) 폭염·한파·강설일수 `extreme_days_m`가 있으면 패널티 항 추가:
`ComfortScore_m × (1 − γ·min(extreme_days_m / 10, 1))`, γ=0.3.

### 4.4 추천 연결

- `recommended_months` = `ComfortScore_m ≥ 70`인 월 집합(없으면 상위 3개월).
- 추천 랭킹의 시즌 적합 항으로 `ComfortScore_m`을 정규화해 반영(04 DB 설계의 `SEASONAL_FIT`/`recommended_months`와 연결).
- 한·일 동일 산식·동일 단위로 계산하므로 **국가 무관 비교가 가능**하다.

---

## 5. 적용 체크리스트

- [ ] 2장 정규화 기준(단위·기준연도·관측소 매핑)을 대표 문서에 반영
- [ ] 3장 정합성 수식·임계값·판정 규칙을 4절 검증 기준 표(특히 "기후 정합성" 행)에 반영
- [ ] 4장 ComfortScore 산식을 `korea_..._updated.md` 3.5 "계절 추천 지표"에 구체화
- [ ] 검수 메타데이터 스키마에 `MAE_T`, `MAPE_P`, `ConsistencyScore`, `status` 추가
- [ ] 파라미터(τ_T, τ_P, T_ideal, P_cap, 가중치) 표본 데이터로 보정·확정
- [ ] 실시간 날씨 필요 여부 결정(현재는 평년값 기반. AGENT.md의 "실시간 날씨" 범위와 정합)
- [ ] `pages/` HTML 생성물 최신화

---

## 6. 참고

- 기상청 API허브: https://apihub.kma.go.kr/
- 일본기상청(JMA) 기후 데이터: https://www.data.jma.go.jp/stats/data/en/index.html
- 파라미터 기본값은 권고 예시이며 표본 검증으로 확정 필요(신뢰도: 중).
