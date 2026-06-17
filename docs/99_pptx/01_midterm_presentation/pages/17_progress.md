# 슬라이드 B11 — 진행 경과 · 협업

> 원본 위치: `../01_midterm_presentation.md`
> 상태: Slide Content
> 역할: 4주간의 진행 경과를 한눈에 보여주고, 그 진행을 어떤 협업 도구로 함께 만들었는지 한 장에 합쳐 보여준다
> 비고: 기존 `16_collaboration.md`(협업)와 `17_progress.md`(진행 상황)를 한 장으로 통합

## 화면 문구

**문제 정의에서 중간 발표까지, 4주 진행 경과 · 협업**

### 주차별 진행

| 주차 | 진행 내용 |
| --- | --- |
| 1주차 · 기획 | 요구사항 정의 · WBS · 협업 환경 구축 |
| 2주차 · 데이터 | 추천 기준 정의 · 데이터 수집 · DB 설계 |
| 3주차 · 설계 | 멀티에이전트 재설계 · RAG · S3 Vector |
| 4주차 · PoC | PoC 구현 · 백엔드/인증 API · 프론트 목업 배포 |

**마일스톤:** M1 PoC → M2 Production

### 협업 — 도구로 나눠, 한 흐름으로

| 영역 | 도구 |
| --- | --- |
| 진행·일정 | Notion · GitHub Projects |
| 개발 | GitHub |
| 문서·산출물 | GitHub Pages |
| 기획·디자인 | Notion · Figma |

## 레이아웃

| 영역 | 내용 |
| --- | --- |
| 상단 | "4주 진행 경과 · 협업" 메시지 |
| 중앙 상 | 주차별 진행 현황 4장(주차 · 키워드 · 한 줄) |
| 중앙 | 마일스톤(중간 발표 6/16 → 최종 7/16) |
| 하단 | 협업 4영역 + 사용 도구(간단 스트립) |

## 발표자 노트

- **프레임** — 한 장에서 4주 진행과 협업을 같이 본다 / 문제 정의 → 중간 발표, 단계적으로 좁혀옴 / 그 진행을 어떤 도구로 함께 굴렸는지가 아래 협업 스트립
- **스프린트 운영** — 1주 = 1 스프린트(Sprint 1~4), 단 1주차(Sprint 1)는 5/22~5/31 10일 킥오프
- **1주차** — 프로젝트 기획 · 요구사항 정의 · WBS · 협업 환경 구축
- **2주차** — 추천 근거 데이터 확정 / 한국 40개로 먼저 검증 후 일본 확장 / retriever 필터링→유사도→랭킹·festival DB 사전저장 방향 / 데이터 수집·DB 설계
- **3주차** — 통합 멀티에이전트(Candidate_Evidence + Planner) 재설계 / DB·RAG·S3 Vector 설계 / 데이터 전처리
- **4주차** — PoC 구현 완료: LangGraph 전체 추천 로직 + AWS Bedrock AgentCore 배포 / 백엔드 API(인증·선호·소도시·추천·저장일정) + Cognito 인증 / 프론트 목업 Vercel 배포
- **마일스톤** — 외부 고정일 2개: M1 중간 발표(6/16) → M2 최종·Production(7/16)
- **협업** — 영역별로 도구를 나누되 한 흐름으로: 진행·일정은 Notion 데일리 스크럼 + GitHub Projects WBS / 개발은 GitHub 역할 분담·PR 리뷰 / 문서·산출물은 GitHub Pages / 기획·디자인은 Notion·Figma
- **현재** — PoC end-to-end 동작(Intent→Candidate_Evidence→Planner), 중간 발표에서 가설→검증 데모 / 다음 장(확장 방향)으로 연결

## 제작 체크

- [ ] 주차별 진행 현황(4장)과 협업 스트립을 한 장에 함께 넣는다(상세 WBS는 GitHub Projects).
- [ ] 화면엔 기간을 넣지 않고, "1주 = 1 스프린트(1주차는 10일 킥오프)"는 발표자 노트로만 설명한다.
- [ ] 마일스톤은 2개(중간 발표 6/16 · 최종 7/16) 기준으로 표기한다.
- [ ] 협업 도구는 실제 사용한 Notion · GitHub · GitHub Projects · GitHub Pages · Figma 기준으로 표기한다.
- [ ] 현재 위치(4주차 진행 중)를 강조해 다음 확장 방향과 잇는다.

## 근거·출처

- WBS·일정 관리: GitHub Projects (`sooa/lovv_github_projects_wbs.md`, `sooa/wbs_revision_plan.md` — 마일스톤 2개 재편안)
- 3~4주차 실제 진행: 팀 Notion Daily Scrum / 진행상황 공유 (6/10 이후, 통합 에이전트·LangGraph·AgentCore·백엔드 인증·프론트 목업)
- 협업 워크스페이스: Notion `Final-Project-Lovv` (Members · Role · Agile WorkFlow · Daily Scrum · 진행상황 공유 · Trouble Shooting · Meeting Minutes · 멘토링)
- 코드: https://github.com/Joraemon-s-Secret-Gadgets/Lovv
- 디자인: Figma `Final Project-Lovv`
- 산출물·문서: https://joraemon-s-secret-gadgets.github.io/oh_my_documents/
