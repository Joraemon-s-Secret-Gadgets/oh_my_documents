# Lovv Agent V2 — 설계 결정 로그 (Step 4)

> 문서 성격: 보조 Markdown (V2 스냅샷 묶음 = `supplemental/v2/`)
> 대표 문서: `../../05_agent_spec.md`
> 정본 위치: `Lovv-agent/docs/reports/v2/V2_DECISIONS_LOG.md` (공유용 스냅샷)
> 연관: `architecture_final.md` · `intent_parsing_spec.md`
> 상태: ✅ 확정 · ◐ 부분 · 표기일 2026-06-28.

## 이미 확정(이전 세션)
- ✅ 테마 게이트 = soft(부분 충족 허용, 미충족 강감점; 누락 테마 audit/userNotice 후보).
- ✅ capacity 결합 제거(candidate_sufficiency 삭제, 항상 rank 0, insufficient는 Planner Pass2로).
- ✅ 수정 재인출 = S3 Vectors(캐시 vector + top_k, 좌표·메타는 vector metadata).
- ✅ 데이터 4종 적재(세부타입·indoor/outdoor·도시월 기상·visitor stats).
- ✅ 이동수단 거친 구분 채택(자동차/뚜벅이, 거친 soft 신호).

## Step 4 결정
### ✅ D-A · 출력 스키마 / Plan B (on-demand)
`alternativeItinerary`를 공식 응답 필드로 두되 **미리 자동 생성하지 않는다**. 임계 초과 시 primary + `weatherNotice`를 반환하고, 사용자가 동의하면 **수정 루프로** 실내 대안을 생성해 `alternativeItinerary`를 채운다. 평시/미발동 = null. Plan B 생성 경로 = 수정 루프(별도 자동 모드 없음). 전제: indoor/outdoor 태깅 + 도시·월 기상.

### ✅ D-B · 수정 처리 범위
1차 = 비-seed 슬롯 교체 + 슬롯 단위 자연어 조건(무드·타입·위치 = 추가 query). 확장(백로그): 전체 무드 재구성·길이·날짜/월·맥락 변화·4d3n·복합. 도시 변경 = city_select 재실행 경로만 설계(1차 미포함).

### ✅ D-K · 프로필 fallback / write
profile은 "저장 확인된 일정"에서만 구성. write = 저장(확정) 시 그 일정의 테마·선택 장소에서 theme_weights 집계(수정 중간 발화·단발 신호 누적 안 함). read/fallback "충분" = 저장 일정 수 ≥ n(추천 이유에 "이전 선호 기반" 명시), 부족하면 되묻기. n 추후 튜닝(초안 2~3). 트리거 = front "일정 저장" 이벤트. `LovvUserProfile.saved_trip_count`.

### ✅ D-E · transport_pref
walk / car / unknown 3값(거친 soft). walk → 슬롯 간 거리 페널티 강화, car → 완화, unknown → 기본. 역·터미널 라우팅 아님.

### ✅ D-J · weatherNotice 발동 임계 (방식 확정 · 수치 추후)
기온 = 기상청 특보 기준 차용(폭염 일최고 33℃ / 한파 일최저 -12℃). 강수 = 월 강수량 → 일평균(mm/day) 환산 절대 구간 + 연평균 대비 2배 상대 보정. 임계 숫자는 데이터·구현 후 튜닝.

### ✅ 4d3n 정책
V2.0은 짧은 일정(daytrip·2d1n·3d2n) 품질 먼저 확인. 4d3n+는 확장(백로그). 요청 시 응답은 하되 userNotice로 한계 고지.

### ◐ D-C · move / 동선 (부분 확정)
출력 move = front가 장소 간 이동시간 제공 → 에이전트 미채움. 배치 동선(Planner) = haversine geo_penalty(무 API) 1차. front 이동시간 API를 배치 스코어링에 쓸지는 ⏳ 검토.

### ✅ 되묻기 경계 (모순/긴서사)
모순 입력은 무조건 되묻기(`needs_clarification`) — 창의적 절충 생성 안 함. 긴서사는 핵심 키워드 추출 후 진행. 짧은 NL도 되묻기.

### ✅ 기피 재생성 (전면 불만)
"다 별로야" 시 기존 도시/테마를 세션 avoid로 설정 → 세션 끝(TTL)까지 계속 제외하고 차순위 재생성. 영구 profile 미반영.

### ✅ 응답상태 확장
기존 `completed` / `END_WAIT_USER` + `modification_pending`(수정 완료 + 다음 수정 대기) 1개만 추가. 풀세트 세분화는 안 감(front 매핑 최소화).

### ✅ 다건 동시 수정 (배치 편집)
한 입력의 복수 편집을 `edit_ops` 리스트로 분해 → 각 비-seed 슬롯 교체 → 일괄 재인출 후 단일 재배치(순차 금지). op 간/슬롯 내 모순 → 되묻기. seed·≤3 불변. 부분 실패 = 부분 적용 + 안내(`modification_pending`).

## 남은 미정(구체화 단계)
D-J 임계 수치 · D-C 실이동 API 사용 여부 · 4d3n 확장 시점 · profile fallback n값 · 수정 응답 diff 반환(front 협의) · 축제 테마 정합 데이터 · 쿼리 임베딩 생성 위치 · tripType 결측 기본값.
