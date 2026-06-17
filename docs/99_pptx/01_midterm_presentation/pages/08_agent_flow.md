# 슬라이드 7 — Agent 오케스트레이션

> 원본 위치: `../01_midterm_presentation.md`
> 상태: Slide Content
> 역할: Agent가 역할별 상태를 넘기는 구조 설명

## 화면 문구

**Agent는 역할을 나누고 상태만 넘깁니다**

| Agent | 역할 |
| --- | --- |
| Intent Agent | 조건 구조화 |
| Supervisor | 다음 단계 결정 |
| Candidate | 후보 근거 생성 |
| Festival | 축제 검증 |
| Planner Agent | 일정 생성 |

## 발표자 노트

- 단일 LLM 호출이 아니라 역할 분리 구조다.
- 상태를 나누면 검색, 검증, 일정 생성을 각각 확인할 수 있다.
