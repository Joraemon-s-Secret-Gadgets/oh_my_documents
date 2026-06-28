# Lovv Agent V2 — Intent 파싱 기준 (확정 명세)

> 문서 성격: 보조 Markdown (V2 스냅샷 묶음 = `supplemental/v2/`)
> 대표 문서: `../../05_agent_spec.md` (V1 Intent_Agent는 `../intent_agent.md` 참조)
> 정본 위치: `Lovv-agent/docs/reports/v2/V2_09_INTENT_PARSING_SPEC.md` (공유용 스냅샷)
> 연관: `architecture_final.md` · `decisions_log.md` · `verification_plan.md`
> 표기: ✅ 확정 · ⚠ 경계 확인 필요.

목적: Intent가 **어디까지 / 어떻게** 파싱하는지를 확정 기준으로 고정. 초기 생성과 수정(resume)을 분리, 공통/생성전용/수정전용을 가른다.

## 0. 원칙 — Intent는 어디서 멈추나
**Intent = "원시 입력 → 타입된 파싱·검증 객체"까지.** 검색·스코어·도시 선택·배치·프로필 fallback 결정은 다운스트림.

| Intent가 한다 | Intent가 안 한다 |
|---|---|
| 구조 필드 정규화·검증 | S3 Vector 검색 / 임베딩 매칭 |
| execution_mode 도출 | 도시 스코어링·선택 |
| NL → soft 신호 추출 | 장소 배치·동선(Planner) |
| 모순/모호/범위밖/안전 **플래그** | 모호 입력 채울지 결정(Profile fallback) |
| 수정 의도 분류 + edit_ops 분해 | 슬롯 재인출·재배치 |
| raw/soft 쿼리 텍스트 산출 | ⚠ 쿼리 임베딩 생성(retrieval_node로 가정) |

> Intent는 판정하지 않고 표식만 단다. 산출물: 초회 `IntentResult`, resume `ModifyResult`. 분기 라우팅은 Supervisor, 내용 파싱·1차 판별은 Intent.

## 1. 초기 생성 파싱 (IntentResult)
### 1.1 구조 필드 정규화·검증
입력: `themes · tripType · travelMonth · destinationId · includeFestivals · country · userLocation · NL`.

| 필드 | 허용/정규화 | 결측·이상 |
|---|---|---|
| themes | 5종 enum 부분집합 | 빈 배열 → underspecified |
| tripType | daytrip·2d1n·3d2n·(4d3n+ 한계 고지) | 결측 → 기본값 ⚠ |
| travelMonth | 1–12 | 범위 밖 → reject{invalid_value} |
| destinationId | 강원·경북 도시 | 범위 밖 지명 → out_of_scope{region} |
| includeFestivals | bool | 결측 → false |
| country | KR 고정 | KR 외 → out_of_scope{region} |
| userLocation | 좌표 | 결측 허용 |
| NL | 자유 텍스트 | §1.3 |

### 1.2 execution_mode 도출 (결정 트리, 위에서 먼저 매칭)
1. destinationId != null → `anchored_place_search`
2. destinationId == null && includeFestivals → `festival_seeded_city_discovery`
3. else → `city_discovery`
(source=map_marker인데 destinationId==null → 안전 거부)

### 1.3 NL 파싱 — 여기까지만
raw_query(핵심 명사구) · soft_query(분위기·감정) · congestion_pref(한적/북적) · transport_pref(walk/car/unknown) · theme_hint(명시 themes 우선). 임베딩은 retrieval_node에서(⚠).

#### 1.3.1 긴 서사 처리 — 정확한 정의
별도 모드 아님 — 추출 앞단에 **의미 압축 1단계** 추가, 산출물은 동일 raw/soft_query.
- **1단계 분리**: ① 명시 대상(장소·활동 명사) ② 감정·상태 ③ 부정 제약 ④ 순수 배경/토로.
- **2단계 매핑(보수적)** — 핵심 규칙: **감정으로 테마를 단정하지 않는다.**

| 조각 | 예 | 매핑 | 강도 |
|---|---|---|---|
| 명시 대상 | "바다" | theme_hint=[sea_coast] | 강 |
| 감정·상태 | "힘들고 외롭고" | mood=위로·조용 · congestion_pref=낮음 | 약 |
| 부정 제약 | "추운 건 싫어" | soft negative(따뜻 선호) | 약(하드필터 아님) |
| 순수 토로 | "회사가 힘들어" | 폐기 또는 mood 톤 | — |

- **3단계 정합**: 상충 → contradiction → 되묻기 / actionable 0 → underspecified → fallback·되묻기(테마 단정 금지).
- 예: "회사도 힘들고 외로운데 바다는 보고싶고 추운 건 싫어" → raw="바다" · theme_hint=[sea_coast] · soft="조용·위로·한적·따뜻" · congestion=low → 정상.
- 반례: "그냥 다 싫고 어디든 떠나고 싶어" → 명시 대상 0 → underspecified.
- 구현: LLM 의미 압축(Bedrock Converse). 검증 = judge로 핵심 보존 + **과해석 0**.

### 1.4 검증·분기 플래그 (판정 아님)
| 상황 | 산출 | 다음 |
|---|---|---|
| 모순 | contradiction=true | 무조건 되묻기 |
| 모호 | underspecified=true | Profile fallback or 되묻기(D-K) |
| 범위 밖(지역) | out_of_scope{region} | 강원·경북 재질의 |
| 범위 밖(기능) | out_of_scope{feature} | graceful 안내 |
| 이상값 | reject{invalid_value} | 안전 정정 |
| 필수 누락 | reject{missing_field} | 안전 거부 END_WAIT_USER |

## 2. 수정 파싱 (ModifyResult · resume)
### 2.1 수정 의도 분류
| 분류 | 발화 예 | 1차 |
|---|---|---|
| 슬롯 교체(+조건) | "2일차 오후 바다 보이는 데로" | ✅ |
| 다건 슬롯 교체 | "2일차는 카페, 3일차는 바다로" | ✅ |
| 전면 리셋 | "다 별로야, 다른 도시로" | ✅ 세션 avoid |
| 날씨 동의 | "응 실내로" | ✅ on-demand Plan B |
| 발견감 강화 | "더 안 알려진 곳으로" | ✅ |
| 도시 변경 | "속초로 바꿔" | 🟡 경로만(V2.1) |
| 무드/길이/날짜/맥락 | "쉬엄쉬엄"·"1박2일"·"10월로" | ⛔ 백로그 → userNotice |

### 2.2 edit_ops 분해 (다건)
`edit_ops: [{target:{day,time_slot}, op:REPLACE, condition:{mood?,place_type?,location?}}]`. op=REPLACE만(배치 ≤3 불변). seed 슬롯 target → 교체 거부+안내. op 간/슬롯 내 모순 → needs_clarification.

### 2.3 특수 수정 신호
reset{avoid:[city|theme]}(TTL까지) · confirm_plan_b · change_city{target?}(city_select 되감기, V2.1).

### 2.4 백로그 의도 처리
무드/길이/날짜/맥락은 인식하되 실행 대신 userNotice로 한계 고지.

## 3. 공통 / 생성 전용 / 수정 전용
| 항목 | 공통 | 생성 전용 | 수정 전용 |
|---|---|---|---|
| 모순 감지 → 되묻기 | ● | | |
| 범위 밖 인식 → 안내 | ● | | |
| 안전/이상값/필수누락 → 거부 | ● | | |
| NL soft 신호 · theme_hint · 긴서사 압축 | ● | | |
| 구조 필드 정규화 · execution_mode · includeFestivals/destinationId | | ● | |
| 모호 → underspecified 플래그 | | ● | |
| transport_pref | ◐ 추출 공통 | 적용 ● | ⚠ 수정 적용은 백로그 |
| 수정 의도 분류 · edit_ops 분해 · seed 보호 | | | ● |
| reset/avoid · confirm_plan_b · change_city | | | ● |

## 부록 A. 검증 방법
유형: (U)단위·결정론 / (G)라벨셋·골든셋 / (J)LLM-judge+휴먼 / (R)회귀.

| 항목 | 유형 | 방법 | 합격(초안) | 오류 방향 |
|---|---|---|---|---|
| execution_mode 도출 | U | 입력 조합 단위 | 100% | 경로 통째로 틀림 → 0 허용 |
| 구조 필드·경계값 | U | 13월·영하100도·빈 themes·KR외 | 100% | 안전 |
| edit_ops 분해 | U+G | 발화→ops 골든셋, exact/F1 | exact≥0.9 | 슬롯 오지정 |
| seed 보호 | U | seed 지정 → reject | 100% | 일정 정체성 |
| 안전 거부/필수 누락 | U | map_marker+무 도시 | 100% | 안전 |
| 모순 감지 | G | confusion matrix | **recall≥0.95** | false negative=엉뚱 생성 |
| 모호 감지 | G | 라벨셋 | P·R≥0.85 | false positive=마찰 |
| 범위밖 인식 | G | 숙소·예약·제주 라벨셋 | **recall≥0.95** | miss=헛생성 |
| 수정 의도 분류 | G | confusion matrix | macro-F1≥0.85 | 백로그를 슬롯교체로 오인 |
| transport_pref | G | 3-class | acc≥0.85 | 약신호 |
| soft·무드 추출 | J | judge + 스팟 | 평균≥4/5 | 정성 |
| 긴서사 압축 | J | 핵심 보존율 judge | 핵심 누락 0 | 과해석 위험 |
| 전체 파싱 회귀 | R | V1 입력 재생 | 의도 외 0 회귀 | — |

> 우선순위: 모순·범위밖은 recall 우선(놓치면 헛생성), execution_mode·seed·안전은 0허용 결정론, soft는 judge+스팟.

## 부록 B. 열린 경계
- ⚠ 쿼리 임베딩 생성 위치: Intent(텍스트) vs retrieval_node(벡터화). 본 명세는 retrieval 가정.
- ⚠ tripType 결측 기본값: 되묻기 vs 기본 2d1n.
- ⚠ transport_pref 수정 적용: 현재 백로그.
