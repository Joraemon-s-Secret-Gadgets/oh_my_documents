# 슬라이드 8 — Agent 오케스트레이션

> 원본 위치: `../01_midterm_presentation.md`
> 상태: Slide Content
> 역할: Agent가 역할별 상태를 넘기는 구조 설명

## 화면 문구

**Agent는 역할을 나눕니다**

| Agent | 역할 |
| --- | --- |
| Intent | 조건 정리 |
| Supervisor | 순서 결정 |
| Candidate | 근거 후보 |
| Festival | 날짜 검증 |
| Planner | 일정 생성 |

## 발표자 노트

- 단일 LLM 호출로 바로 일정을 쓰면 어떤 근거로 추천했는지 추적하기 어렵다.
- Intent는 자연어와 UI 입력을 국가, 월, 테마, 일정 유형 같은 조건으로 정리한다.
- Supervisor는 조건이 충분한지 보고 Candidate, Festival, Planner 중 다음 단계를 결정한다.
- Candidate는 추천 후보와 근거를 만들고, Festival은 해당 연도 축제 날짜처럼 변동성이 큰 정보를 검증한다.
- Planner는 검증된 후보 안에서만 일정을 만들기 때문에 추천 이유와 일정이 어긋나는 위험을 줄인다.
