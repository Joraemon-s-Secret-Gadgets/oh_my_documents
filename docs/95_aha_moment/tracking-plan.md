# 로브(Lovv) Aha 트래킹 플랜 (이벤트 명세)

> 문서 성격: 보조 Markdown
> 대표 문서: `95_aha_moment.md`

> 문서 버전: v0.1
> 문서 상태: 초안 (Draft)
> 적용 범위: 95_aha_moment 화면들의 측정 이벤트를 한 곳에 모은 트래킹 명세
> 상위 문서: `95_aha_moment.md`(대표) · 화면 문서: `aha-card-slot.md` / `theme-detail.md` / `followup-requery.md` / `plan-detail.md`

## 1. 목적

각 화면 문서의 '측정 이벤트' 절에 흩어진 지표를 **이벤트명·속성·발생 위치**로 통일한다. 이 저장소의 product-tracking 플러그인으로 구현·추적 계획을 만들 수 있다.

**프라이버시.** 대화 원문·자연어 입력은 저장하지 않는다(06_기술명세 정책). 이벤트에는 **파생 신호만**(intent 분류값, 테마 id, 카운트 등) 담는다.

## 2. 이벤트 명세

### 2.1 메인 카드 슬롯 (단계 0·4)

| 이벤트 | 주요 속성 | 용도 |
| --- | --- | --- |
| `slot_view` | state(기본/개인화) | 노출·time-to-first 기준점 |
| `slot_card_click` | theme, isDiscover, rank, state | **첫 aha** · 발견 작동(비선택 테마 클릭률) |
| `perso_card_view` | variant(갔던곳/안가본곳) | 개인화 노출 |
| `perso_explore_x_click` | — | 안 가본 곳(explore) 전환율 |

### 2.2 THEME DETAIL (단계 1)

| 이벤트 | 주요 속성 | 용도 |
| --- | --- | --- |
| `theme_detail_view` | theme | 도달률(슬롯 클릭 대비) |
| `theme_reason_read` | theme | 추천 이유 정독 |
| `plan_cta_click` | theme | **단계 3 전환(핵심 지표)** |
| `other_reco_click` | theme | 단계 2(채팅) 전환 |

### 2.3 채팅 후속 질의 (단계 2)

| 이벤트 | 주요 속성 | 용도 |
| --- | --- | --- |
| `chat_open` | entry(theme_cta/map/chatbot/plan_back) | 진입 경로 분포 |
| `chat_followup` | intent, isCanned(간판 여부) | follow-up 발생·간판 비중 |
| `requery_result_view` | intent | 재추천 노출 |
| `chat_limit_response` | intent | 한계 응답률(데이터로 못 답한 비율) |

### 2.4 PLAN DETAIL (단계 3)

| 이벤트 | 주요 속성 | 용도 |
| --- | --- | --- |
| `plan_generate_start` | entry, country, month | 생성 시작 |
| `plan_generated` | latencyMs, cityId | 생성 성공·레이턴시(P50·P95) |
| `plan_generate_fail` | reason(timeout/empty/error) | 실패율·실패 사유 |
| `itinerary_scroll_complete` | cityId | 일정 완독률 |
| `map_link_click` / `klook_link_click` | placeId | 실행 보조 클릭(탐색/예약) |
| `feedback_positive` | tag(한적함/자연/동선/알참) | 긍정 시드 |
| `feedback_negative` | — | 부정 시드("관심 없어요") |
| `plan_save` | cityId | 저장 전환(peak-end) |

### 2.5 재방문 (단계 4)

| 이벤트 | 주요 속성 | 용도 |
| --- | --- | --- |
| `revisit_personalized_view` | thresholdPassed | 개인화 점등 여부 |
| `perso_card_click` | variant | 개인화 적중 |
| `soft_prefill_edit` | field(month/nights/country) | prefill 수정률 |

## 3. 핵심 funnel·검증 지표

- **time-to-first-aha:** `slot_view` → 첫 `slot_card_click` 시간.
- **발견 작동:** `slot_card_click`의 `isDiscover=true` 비율(0이면 발견 실패).
- **단계 전환:** slot_card_click → `plan_cta_click` → `plan_generated` → `plan_save` → 재방문.
- **생성 신뢰성:** `plan_generated` / (`plan_generated`+`plan_generate_fail`), 레이턴시 분포.
- **개인화:** `perso_card_click`률, `perso_explore_x_click`(explore 전환), `feedback_negative`률.

## 4. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-18 | 로브 기획팀 | 화면별 측정 이벤트를 단일 트래킹 플랜으로 통합(이벤트명·속성·funnel 지표) |
