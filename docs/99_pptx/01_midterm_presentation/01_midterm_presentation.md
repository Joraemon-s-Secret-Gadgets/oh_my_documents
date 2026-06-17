# Lovv 중간발표 — 대표 문서 (14장)

> 문서 성격: `99_pptx/01_midterm_presentation` 폴더의 대표 Markdown.
> 기준 PPTX: `artifacts/pptx/lovv_midterm_focus_current.pptx`
> 동기화 기준: 2026-06-15 현재 PPT 화면 구성.
> 원칙: 화면에는 한 메시지와 핵심 단어만 남기고, 배경 설명은 발표자 노트로 분리한다.

---

## 발표 흐름

Lovv 소개 → 오버투어리즘 정의·사례 → 한일 시장 근거 → 핵심 문제와 기능 연결 → 시스템 흐름 → 사용자 흐름 → Agent 구조 → Candidate Evidence → Planner → 데이터 → 데모 → 차별점 → 출처 → Q&A

## 디자인 기준

| 토큰 | HEX | 용도 |
| --- | --- | --- |
| Main Orange | `#F26518` | 핵심 강조, 진행선, Lovv 브랜드 |
| Deep Charcoal | `#222222` | 제목, 다크 패널 |
| Soft Beige | `#FFF3E7` | 전체 배경 |
| Card White | `#FFFFFF` | 본문 카드 |
| Blue | `#2F6F8F` | 검증·백엔드 계열 |
| Green | `#2E855B` | 근거·데이터 계열 |
| Purple | `#8A5A96` | 외부 API·검증 계열 |
| Sub Gray | `#666666` | 보조 설명, 출처 |

---

## 슬라이드 1 — Lovv

**화면 메시지**
서울·오사카 말고, 지금은 이곳

**화면 요소**

| 영역 | 내용 |
| --- | --- |
| 좌측 | `Lovv`, 한일 소도시 대화형 여행 추천, 슬로건 |
| 우측 | Local / Vibe / Voyage 의미 카드 |
| 하단 | 조동휘 · 조라에몽의 만능 도구들 |

**발표자 노트**
- Lovv는 도시를 먼저 정한 뒤 검색하는 앱이 아니라, 조건에서 소도시를 찾는 여행 추천 서비스다.
- Local은 대도시 밖 지역 맥락, Vibe는 취향과 분위기, Voyage는 추천에서 일정까지 이어지는 경험을 뜻한다.

---

## 슬라이드 2 — 오버투어리즘 정의와 사례

**화면 메시지**
오버투어리즘이란?

**화면 요소**

| 문제 | 사례 | 한 줄 설명 |
| --- | --- | --- |
| 생활 문제 | 북촌 · 서울 | 주거지와 관광지가 겹쳐 소음·사생활 침해 |
| 환경 문제 | 제주 | 방문객 급증으로 생활폐기물·처리 부담 |
| 도시 문제 | 가마쿠라 에노덴 | 촬영 인파가 건널목·차도로 몰림 |
| 문화 문제 | 교토 기온 | 사유지 출입·무단 촬영으로 일상 침범 |

**발표자 노트**
- 오버투어리즘은 관광 수요가 한 지역의 수용 한계를 넘어 주민 삶과 방문 경험을 함께 해치는 상태다.
- 사례의 공통점은 관광객 개인의 문제가 아니라 특정 장소로 수요가 몰리는 구조다.

---

## 슬라이드 3 — 한일 시장 근거

**화면 메시지**
한일 여행은 가깝고, 반복되고, 확장 가능합니다

**화면 요소**

| 방향 | 근거 |
| --- | --- |
| 일본 → 한국 | 외국인 관광객 2029년 3,000만 목표, 일본 개별 자유여행 비중 90%+ |
| 한국 → 일본 | 일본 소도시 예약 +35%, 구마모토 예약 +261% |

**발표자 노트**
- 한국과 일본은 가까운 반복 여행권이고, 대도시 외 지역으로 확장될 여지가 크다.
- Lovv는 대형 여행지 경쟁보다 소도시 발견과 수요 분산 단계에 집중한다.

---

## 슬라이드 4 — 핵심 문제와 Lovv 기능

**화면 메시지**
발견·정리·신뢰가 병목입니다

**화면 요소**

| 문제 | Lovv 기능 | 구현 축 |
| --- | --- | --- |
| 유명지만 간다 | 조건 기반 목적지 탐색 | Candidate Evidence Agent |
| 찾다가 지친다 | 대화형 일정 정리 | Planner Agent |
| 추천은 못 믿는다 | 추천 이유와 검증 노출 | Explainable RAG |

**발표자 노트**
- 사용자는 유명지를 좋아해서만 가는 것이 아니라 실패 비용을 피하려고 검증된 장소로 쏠린다.
- Lovv는 대체 소도시를 찾고, 흩어진 후보를 일정으로 묶고, 추천 이유와 출처를 함께 보여준다.

---

## 슬라이드 5 — 시스템 흐름

**화면 메시지**
책임 경계로 나눕니다

**화면 요소**

| 계층 | 역할 |
| --- | --- |
| Client Web | 입력, 지도, 결과 표시 |
| Backend API / SAM | 인증, 검증, 추천 실행 |
| Agent Runtime | 검색, 검증, 일정 생성 |
| Retrieval & Data | 근거 후보, 정규 상세, 캐시 |
| External APIs | 지도, 날씨, 딥링크 |

**발표자 노트**
- 시스템 흐름은 사용자 플로우가 아니라 책임 경계다.
- Agent가 모든 것을 직접 만드는 것이 아니라, 백엔드와 데이터 계층이 검증 가능한 입력을 제공한다.

---

## 슬라이드 6 — 사용자 흐름

**화면 메시지**
도시를 몰라도 조건만 말하면 됩니다

**화면 요소**

| 단계 | 내용 |
| --- | --- |
| 1 조건을 말한다 | 일본 · 5월 · 조용한 바다 · 축제 |
| 2 소도시를 받는다 | 추천 도시 1곳 · 추천 이유 · 근거 뱃지 |
| 3 일정으로 실행한다 | 오전/오후 일정 · 지도 · 상세 링크 |

**발표자 노트**
- 첫 질문은 "어디로 갈래?"가 아니라 "언제, 어느 나라, 어떤 취향인가?"다.
- 목적지를 모르는 사용자도 추천과 일정으로 바로 이어질 수 있어야 한다.
- 하단 설명 문구는 사용하지 않고, 카드 문구 자체로 흐름을 이해하게 한다.

---

## 슬라이드 7 — Agent 오케스트레이션

**화면 메시지**
Agent는 역할을 나누고 상태만 넘깁니다

**화면 요소**

| Agent | 역할 |
| --- | --- |
| Intent Agent | 조건 구조화 |
| Supervisor | 다음 단계 결정 |
| Candidate | 후보 근거 생성 |
| Festival | 축제 검증 |
| Planner Agent | 일정 생성 |

**발표자 노트**
- 단일 LLM 호출로 바로 일정을 만들지 않는다.
- 입력 정리, 후보 생성, 축제 검증, 일정 생성의 책임을 나눠 검증 가능한 상태를 넘긴다.

---

## 슬라이드 8 — Candidate Evidence

**화면 메시지**
검색 결과를 근거 패키지로 압축합니다

**화면 요소**

| 단계 | 산출 |
| --- | --- |
| 후보 검색 | Vector + DB 후보 |
| 점수화 | 테마, 거리, 혼잡 보정 |
| 근거 묶음 | 선정 이유 정리 |
| 입력 고정 | Planner 입력 고정 |

**Evidence Package**
선택 도시, 추천 장소, 예비 후보, 검증 로그

**발표자 노트**
- Candidate Evidence는 도시를 "감으로 고르는" 단계가 아니라 Planner가 사용할 근거 패키지를 만드는 단계다.
- 후보를 줄이고 이유를 묶어 다음 Agent가 같은 근거를 보게 한다.

---

## 슬라이드 9 — Planner Agent

**화면 메시지**
Planner는 검증된 후보만 일정에 씁니다

**화면 요소**

| 단계 | 처리 |
| --- | --- |
| 후보 입력 | 도시, 장소, 축제 |
| 일정 배치 | 시간대별 slot 구성 |
| 검증 | 후보 외 장소, 축제 날짜 확인 |
| 사용자 출력 | 일정, 이유, 링크, 안내 |

**검증 규칙**
후보 외 장소 금지 / 식사 링크 안내 / 검증된 축제만 / 한계 안내 / 실패 시 축소

**발표자 노트**
- Planner는 검색 Agent가 아니다. Candidate Evidence Package에 없는 장소를 새로 만들지 않는다.
- 부족한 정보는 지어내지 않고 링크, 자유시간, 안내 문구로 처리한다.

---

## 슬라이드 10 — 데이터

**화면 메시지**
추천에 필요한 데이터만 구조화합니다

**화면 요소**

| 구분 | 주요 출처 | 활용 |
| --- | --- | --- |
| 한국 | TourAPI, DataLab, Wikipedia, 기상청 | 후보 생성, 테마 매핑, 월별 보정 |
| 일본 | Wikipedia, JNTO/JTA, e-Stat, RESAS, JMA | 공통 구조, 계절성, 공식 근거 |
| 공통 운영 | S3 Raw, Lambda, DynamoDB, S3 vector | 출처 추적, 최신성 검수, 재처리 |

**화면 수치**
한국 도시 40 / 관광지 3,709 / 축제 106 / 월별 방문객 40×12

**발표자 노트**
- 데이터는 많이 모으는 것이 아니라 추천 판단에 필요한 형태로 맞추는 것이 핵심이다.
- 모든 데이터는 출처와 수집 시각을 남겨 RAG 근거 추적이 가능하게 한다.

---

## 슬라이드 11 — 데모

**화면 메시지**
조건 입력에서 근거 있는 일정까지

**화면 요소**
입력 → 추천 → 실행

**발표자 노트**
- 데모는 국가·시기·취향 입력에서 소도시 추천, 추천 이유, 일정 실행까지 이어지는 흐름을 보여준다.
- 완성 기능 전체가 아니라 PoC 핵심 가설 검증 범위다.

---

## 슬라이드 12 — 차별점

**화면 메시지**
트리플과 차이점

**화면 요소**

| 서비스 | 시작점 | 강점 |
| --- | --- | --- |
| 트리플 | 도시를 정한 뒤 | 일정·예약 연결 |
| Lovv | 국가·시기·취향에서 | 소도시 발견, 수요 분산, 근거 추천 |

**발표자 노트**
- 트리플은 이미 도시를 정한 사용자에게 강하다.
- Lovv는 아직 어디로 갈지 모르는 사용자에게 소도시 후보를 먼저 찾아준다.

---

## 슬라이드 13 — 출처

**화면 메시지**
발표에 사용한 외부 출처

**화면 요소**

| 구분 | 화면 표기 |
| --- | --- |
| 문제·트렌드 | UN Tourism, AP, news.com.au, Guardian |
| 시장·사례 | Dailybrief, Hankyung, SomeTrend, Newsis |
| 데이터 | TourAPI, DataLab, Wikipedia, JNTO/JTA, e-Stat |
| 서비스·비교 | Triple Guide, InterparkTriple |

**발표자 노트**
- 발표 화면의 출처 목록은 외부 근거 중심으로 유지한다.

---

## 슬라이드 14 — Q&A

**화면 메시지**
Q&A

**화면 요소**
LOCAL · VIBE · VOYAGE / Lovv / 감사합니다 · 조동휘 · 2026.06.16

**발표자 노트**
- 발표를 마무리하고 질문을 받는다.

---

## 출처

### 오버투어리즘 정의·사례
- UN Tourism: https://www.e-unwto.org/doi/book/10.18111/9789284420070
- AP: https://apnews.com/article/europe-mass-tourism-france-spain-italy-overtourism-fc99da0aa610dca84b8a2753645a0d6a
- Guardian: https://www.theguardian.com/world/2024/feb/03/a-free-for-all-japan-divided-as-return-of-tourists-brings-instagrammers-and-litter
- 뉴시스: https://www.newsis.com/view/NISX20240315_0002662388
- 제주일보: https://www.jejunews.com/news/articleView.html?idxno=2134351

### 핵심 문제
- AP 후지산 가림막: https://apnews.com/article/japan-mt-fuji-screen-overcrowding-tourism-e1fa287577735d6949aad140d54b0568
- news.com.au Ask Skye: https://www.news.com.au/travel/escape-launches-ai-assistant-ask-skye-to-end-holiday-planning-pain/news-story/1e24c7ca514f2b9366a1f0da1a7cefa8
- Guardian AI 여행 계획: https://www.theguardian.com/travel/2026/mar/25/tell-us-have-you-used-ai-to-plan-a-holiday

### 시장 근거
- 데일리브리프: https://www.dailybrief.co.kr/news/articleView.html?idxno=5149
- 서울경제TV: https://www.sentv.co.kr/article/view/sentv202507220207
- 이지경제: https://www.ezyeconomy.com/news/articleView.html?idxno=217723
- 한국경제: https://www.hankyung.com/article/202606046704g
- 썸트렌드: https://some.co.kr/briefing/domestic-small-city-travel-trend-report-2026

### 경쟁 제품 비교
- Triple Guide: https://triple.guide/intro
- InterparkTriple: https://www.interparktriple.com/
