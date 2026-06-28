# Lovv Agent V2 — 아키텍처 ↔ 시나리오 커버리지

> 문서 성격: 보조 Markdown (V2 스냅샷 묶음 = `supplemental/v2/`)
> 대표 문서: `../../05_agent_spec.md`
> 정본 위치: `Lovv-agent/docs/reports/v2/` (공유용 스냅샷)
> 연관: `architecture_final.md`(다이어그램 포함) · `decisions_log.md`
> 읽는 법: `architecture_final.md`의 다이어그램을 위→아래로 따라가며 "이 구조가 그 시나리오를 어떻게 처리하는가"가 순서대로 설명된다.

## 0. 한 문장 요약
V2는 시나리오를 **세 흐름**으로 처리한다 — 다이어그램의 세 영역과 1:1. ① 초회 생성(Main Graph) ② 자연어 수정 루프 ③ 데이터 계약. 시나리오는 (a) 처음 만들기, (b) 고치기, (c) 막다른 상황 처리.
[V1·고도화] 8건 = "되던 게 좋아짐"(거의 V2.0), [V2·신규] 9건 = "새로 됨"(절반 V2.0, 절반 V2.1).

## 1. 초회 생성 경로 (상단 왼→오)
- **Intent**: 모호(SC-01)·모순→되묻기(SC-N2)·긴서사 키워드 추출·이동수단(SC-N1 transport_pref).
- **Supervisor**: 초회/resume 분기, 수정 시 edit_ops 분해.
- **city_select**: 멀티테마 발견(SC-G1, soft 게이트 — V1 최대 약점 해소), 저밀도(SC-00·번아웃), 개인화(SC-01 A), 도시 지정(SC-G2 anchored), seed 추출, capacity 제거.
- **Festival Verifier**: 축제 포함(SC-G3, 실제 날짜 분산), 시즌 불일치(SC-R2).
- **Planner**: 후보 부족(SC-R1, Pass2 재인출), 동선(SC-00 seed+geo), 이동수단(SC-N1), 날씨(SC-02 weatherNotice + on-demand).
- **Response Packager**: 정상/축소(completed)·no_candidate/거부(END_WAIT, SC-R3/R4) + interrupt.

## 2. 자연어 수정 루프 (하단 우측)
resume → 수정 Intent(edit_ops 분해) → 교체 전용(seed 제외) → 재인출 → 일괄 재배치.
- 슬롯 1개 교체(SC-03, 1차 핵심) · 다건 동시(신규: 분해+일괄+부분 적용) · 모순된 다건→되묻기 · 전면 리셋(SC-M4, 세션 avoid) · 날씨→실내(on-demand Plan B) · 도시 변경(SC-M1, city_select 되감기 — V2.1).
- 상태값: V1 2종 + `modification_pending` 1개.

## 3. 막다른 상황 (엣지 — V1 5종 유지)
불가능 동선 → 축소 · 범위 밖 → 강원·경북 한정 재질의 · 이상값 → 안전 정정 · 축제 시즌 불일치 → 고지+대안 · 후보 0매칭 → 재질의 · 필수 누락 → 안전 거부. 전부 graceful 안내 + 상태값.
범위 밖 요청(숙소·예약·실시간 혼잡·내비·사진/음성) → Intent 인식 후 "못 한다" 안내(구현 X). 조회·지도 동선=front, 안전 정책=별도 트랙.

## 4. 커버리지 한눈에
| 시나리오 | 유형 | 처리 경로 | 잠근 결정 | 출하 |
|---|---|---|---|---|
| SC-00 발견·단일테마 | V1·고도화 | city_select(congestion·profile)+Planner(seed·geo) | D-C | V2.0 |
| SC-G1 멀티테마 | V1·고도화 | city_select soft 게이트 | soft | **V2.0 ★약점 해소** |
| SC-G2 도시 지정 | V1·고도화 | Intent anchored + city_select 고정 | — | V2.0 |
| SC-G3 축제 포함 | V1·고도화 | Festival + Verifier + Planner 날짜배치 | 테마정합(데이터) | V2.0 |
| SC-R1 후보부족→축소 | V1·고도화 | Planner Pass2 재인출 | capacity 제거 | V2.0 |
| SC-R2 축제 시즌 불일치 | V1·고도화 | Verifier not_placeable | — | V2.0 |
| SC-R3 후보 없음 | V1·고도화 | city_select 0생존 → Packager | soft로 빈도↓ | V2.0 |
| SC-R4 안전 거부 | V1·고도화 | Intent 검증 | — | V2.0 |
| SC-01 모호+프로필 | V2·신규 | Profile fallback(saved_trip_count≥n) | D-K | V2.1 |
| SC-02 날씨 Plan B | V2·신규 | Planner weatherNotice → on-demand | D-A·D-J | **안내 V2.0 / 생성 V2.1** |
| SC-N1 이동수단 | V2·신규 | Intent transport_pref → Planner | D-E | V2.1 |
| SC-N2 모순/긴서사 | V2·신규 | Intent 모순→되묻기 / 키워드 추출 | 되묻기 | V2.0 |
| SC-03 슬롯 교체 | V2·신규 | 수정 루프 재인출+재배치 | D-B·응답상태 | **V2.0 ★핵심** |
| 다건 동시 수정 | V2·신규 | edit_ops 분해 + 일괄 재배치 + 부분 적용 | 배치편집 | **V2.0** |
| SC-M1 도시 변경 | V2·신규 | 수정 → city_select 재실행 | D-B(경로만) | V2.1 |
| SC-M2 무드/길이/날짜 | V2·신규 | 의미 재구성/골격 재생성 | D-B 백로그·4d3n | V2.1+ |
| SC-M3 맥락 변화 | V2·신규 | 멀티턴 재구성 | D-B 백로그 | V2.1+ |
| SC-M4 전면 리셋 | V2·신규 | 세션 avoid 재생성 | 기피 | V2.0 |

## 5. V2.0에서 실제로 보이는 것
**thin slice = 초회 품질 개선(soft 테마·seed 배치·capacity 제거) + 슬롯 교체(단일·다건) + 날씨 안내.**
시연 한 줄: "멀티테마로 소도시를 제대로 찾아주고 → 자연어로 '여기 바꿔줘'(여러 개도) 하면 고쳐주고 → 비 오는 달이면 안내까지."
다음 사이클(V2.1): 날씨 실내 대안 실제 생성, 도시 변경, 무드/길이/날짜, 프로필 학습 체감, 이동수단 튜닝.

## 6. 예상 질문 — 미리 답
- 여러 개 한 번에 고치면? → op 분해 + 일괄 재배치, 일부 실패는 부분 적용+안내. 모순이면 되묻기.
- 비 오는 날 두 벌 다 만들어? → 아니다. 안내만, 원하면 그때 생성(on-demand).
- 프로필 학습 시점? → 일정 저장할 때만. 수정 중 변덕은 안 쌓음.
- 숙소/예약/지도? → 범위 밖(안내만) / 지도 동선은 front.
- 4박5일? → 짧은 일정 품질 먼저 → 확장. 요청은 받되 한계 고지.
