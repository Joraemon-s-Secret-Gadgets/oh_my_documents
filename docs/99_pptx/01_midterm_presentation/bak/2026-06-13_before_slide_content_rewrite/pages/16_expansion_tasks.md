# 슬라이드 B10 — 확장 방향 + 남은 태스크

> 원본 위치: `
../01_midterm_presentation.md
`
> 상태: Draft
> 역할: 대표 문서에서 분리한 슬라이드별 작업 문서

**핵심 메시지 (화면 카피)**
PoC로 핵심 가설을 좁게 검증하고, Production에서 전국·운영·비즈니스로 확장한다

**화면 구성 — PoC → Production 2열**

| 영역 | 지금(PoC) | 다음(Production) |
| --- | --- | --- |
| 데이터 범위 | 강원·경북 40도시 + 일본 관동 일부 | 한국 전국·일본 전역으로 도시·관광지·축제 확장 |
| 데이터 운영 | 1회 수집, 출처·수집시각·신뢰도 기록 | 시변 데이터 정기 갱신 파이프라인, `needs_review` 검수, 관리형 DB 적재 |
| 추천 모드 | Discovery(목적지 미정 → 소도시 발견) 흐름 검증 | 지도 선택·일정 보충 모드로 확장 |
| 추천 기준 | 강원·경북 도시 전체 적재, 소도시 별도 추출 전 | 월별 방문객 수 기반 혼잡도 필터링, 비수기 유명지까지 같은 기준으로 포함 |
| 성능·품질 | 핵심 흐름 동작 검증 | 추천 8초·RAG 1초 목표, 추천 품질 평가·모니터링 하네스 |
| 비즈니스·운영 | 문제·시장 근거 제시 | 지자체 파트너 대시보드(B2G), 송객·콘텐츠 제휴, 역할 기반 운영/검토 |

**마무리 한 줄**
PoC로 핵심 가설이 좁은 범위에서 작동함을 확인 — Production에서 전국·운영·비즈니스로 확장한다.

**발표자 노트**
- 범위는 정직하게 말한다: P1 구현, P2~P3 설계, P5 제외.
- 핵심 축은 "소도시냐 대도시냐"가 아니라 **혼잡도**다. 서울·오사카 말고는 성수기 혼잡 회피의 메시지이며, 비수기 유명지도 같은 로직으로 확장 가능하다.
- 다음 우선순위: ① 데이터 범위 확장 ② 추천 품질 평가·모니터링 하네스 ③ 시변 데이터 갱신 파이프라인 ④ Production 인증·운영 API·지자체 대시보드.

---

---

# 디자인 도구에 넘기기 전 확인 사항

- [ ] 표지에는 단계("중간발표 / PoC") 표기를 넣지 않고, 날짜·발표자만 우측 하단에 배치
- [ ] S1 로고 아래 "무엇인가" 한 줄 정의 포함
- [ ] S2 워드클라우드는 *현상 키워드만*(비용 단어는 S3로), 수치 포함 시 출처 필요. 흩어진-앱 작은 컷(애니메이션)
- [ ] S3 2×2 카드 — 카드당 대표 수치 1개만, 블로그 출처 수치는 정성 표현 or 1차 확인 후
- [ ] S4 인물 사진 미사용(텍스트 인용 카드), 직함 혼동 금지, LCC "구조적 확대"만 화면, 한국 국내는 보조 한 줄
- [ ] S4 일본 국내 칸 없음(확장으로) — "일본 국내는?" Q&A 멘트 준비
- [ ] S5 화면 = 메시지 1 + 컨셉 카드 3(문제 태그) + 의미 1줄, 마무리 S1 태그라인 bookend
- [ ] B1 시스템 흐름은 5계층 큰 그림 1장으로 유지하고, 에이전트 상세는 B3로 넘김
- [ ] B2는 분기→합류 흐름 도식 + 결과 카드 히어로 컷 1장만 사용
- [ ] B3는 7단계 Tool/Agent 파이프라인과 발견·일정·근거 회수 띠를 포함
- [ ] B4-1은 vector+RDS grounding 중심, Neptune은 미래 각주로만 표기
- [ ] B4-2는 Ranker를 최적 공식이 아닌 검증 가능한 scoring framework로 설명
- [ ] B5는 한국/일본/표시·연동용 3카드로 출처와 목적을 같이 표기
- [ ] B6은 영상 준비 전까지 Before/After 도식 자리만 유지
- [ ] B7은 Neptune 이슈를 "도입 실패"가 아니라 "비용·범위 검토 후 대체 아키텍처로 트러블슈팅"으로 설명
- [ ] B8은 트리플 대비 차별점을 완화형 문구로 제시하고, 강한 평가는 발표자가 말로 보완
- [ ] B9은 비즈니스 모델과 예상 수익만 다루며, 수익 수치는 "가정 기반·검증 필요"로 표기
- [ ] B10은 PoC 범위와 Production 확장 항목을 분리하고, 혼잡도 기준과 비수기 유명지 포함 논리를 명시
- [ ] 개별 출처는 관련 카드/근거 박스에 작게 표시하고, 상세 URL은 마지막 출처 모음 또는 문서 하단 §출처에 모음
- [ ] 발표 시간: 서론(S1~S5) 8분 내 — 본론·데모 시간 확보. recap은 빠르게
- [ ] 발표자 노트에 분석 기간·데이터 범위 명시, 시간 측정 리허설

# HTML 변환 후 감량 우선 후보

HTML/PPT 변환 뒤 글자 수가 많거나 시선 집중에 방해될 가능성이 높은 슬라이드는 아래 순서로 먼저 점검한다.

1. **S2 오버투어리즘 워드클라우드** — 단어가 많아지면 메인 단어 6~8개만 강하게 두고, 보조 단어는 흐리게 줄인다. 출처는 단어 묶음 옆 작은 칩으로만 둔다.
2. **S5 핵심 컨셉 3가지** — 3단계 오버레이가 핵심이므로 카드 안 설명문은 1줄 이하로 줄이고, 차별점 설명은 발표자 노트로 내린다.
3. **B3 에이전트 플로우** — 7단계 표가 길면 화면에는 `의도 분류 → 검색·선정 → 검증·일정 → 출력` 4묶음으로 압축하고, 세부 Tool/Agent 차이는 노트로 보낸다.
4. **B4-1 Explainable RAG** — 표의 `역할` 문장이 길면 `사실 원장 / vector / 관계 탐색` 3분할 구조만 남긴다.
5. **B7 Neptune 트러블슈팅** — 표 5행 + 도식이 함께 과밀하면 표를 `이슈·판단·대응·승격 기준` 4행으로 줄인다.
6. **B8 트리플 비교** — 5행 표가 빽빽하면 화면엔 `시작점 / 추천 근거 / 비즈니스 연결` 3행만 두고, 나머지는 발표자 노트로 설명한다.
7. **B10 확장 방향** — 6행 표가 과밀하면 `데이터 / 추천 / 운영·비즈니스` 3묶음으로 접는다.

# 출처

### S2 — 오버투어리즘 현상 키워드
- 오버투어리즘 일반·유럽 수용 한계·인프라 압박 — AP: https://apnews.com/article/europe-mass-tourism-france-spain-italy-overtourism-fc99da0aa610dca84b8a2753645a0d6a
- 일본 관광객 급증·인스타그래머·가마쿠라 슬램덩크 건널목 — Guardian: https://www.theguardian.com/world/2024/feb/03/a-free-for-all-japan-divided-as-return-of-tourists-brings-instagrammers-and-litter
- 교토 기온 사유지 골목 출입 통제·게이샤 무단 촬영 — 뉴시스: https://www.newsis.com/view/NISX20240315_0002662388
- 제주 생활폐기물 증가·관광객 증가 — 제주일보: https://www.jejunews.com/news/articleView.html?idxno=2134351

### S3 — 4가지 비용 (화면 대표 사례)
- 북촌(주민 생활) — 국제뉴스: http://kgunews.com/m/view.php?idx=5426&mcode=m66x1td&page=5 / (1차) 서울연구원 si.re
- 제주(환경) — 제주일보: http://www.jejunews.com/news/articleView.html?idxno=2134351
- 가마쿠라 에노덴(도시 기능, 슬램덩크 배경지) — Guardian: https://www.theguardian.com/world/2024/feb/03/a-free-for-all-japan-divided-as-return-of-tourists-brings-instagrammers-and-litter
- 교토 기온(지역 문화) — 뉴시스: https://www.newsis.com/view/NISX20240315_0002662388
> 상세 검증·신뢰도: `../references/s3_problem_axes_revision.md` §3·§7

### S4 — 한일 양방향 + 한국 국내
- 인바운드 "서울 다음은 어디?"·3,000만·FIT 90%+ — 데일리브리프(5149): https://www.dailybrief.co.kr/news/articleView.html?idxno=5149
- 아웃바운드 구마모토 +261%·홋카이도 +204% — 서울경제TV: https://www.sentv.co.kr/article/view/sentv202507220207 / 이지경제: https://www.ezyeconomy.com/news/articleView.html?idxno=217723
- 아웃바운드 일본 소도시 예약 +35%·다카마쓰 — 한국경제: https://www.hankyung.com/article/202606046704g
- 한국 국내 소도시 언급 +184% — 썸트렌드: https://some.co.kr/briefing/domestic-small-city-travel-trend-report-2026
- (확장용·일본 국내) 관광청 숙박여행통계 2024: https://www.mlit.go.jp/kankocho/content/001905698.pdf / 근거리화·지방부 90% 일본인 — 관광경제신문 / JTB 마이크로투어리즘
> 카드 A/B/C/D 상세·출처 표: `../references/external_evidence_slides_2articles.md`

### 내부 문서
- `00_project_plan.md`, `../references/intro_revision_proposal.md`, `../references/s3_problem_axes_revision.md`, `../references/external_evidence_slides_2articles.md`, `../../midterm_vs_final_presentation_guide.md`

### B8 — 경쟁 제품 비교
- 트리플 공식 서비스 소개(일정 생성·관리, AI 일정 추천, 공동 일정, 항공·숙소·투어티켓 추천/할인, 항공권 시세 확인): https://triple.guide/intro
- NOL Universe 서비스 목록(트리플, NOL World 등): https://www.interparktriple.com/
