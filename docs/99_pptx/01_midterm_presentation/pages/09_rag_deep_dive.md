# 슬라이드 B4-1 — RAG 딥다이브

> 원본 위치: `../01_midterm_presentation.md`
> 상태: Slide Content
> 역할: PoC에서 힘을 준 근거 기반 추천 구조 설명

## 화면 문구

**추천은 생성이 아니라, 근거 패키지에서 시작한다**

| 단계 | 처리 | 결과 |
| --- | --- | --- |
| 검색 | 도시·축제·날씨 경향 검색 | 후보 evidence 수집 |
| 정리 | Planner가 쓸 수 있는 형태로 패키징 | Candidate Evidence Package |
| 생성 | 후보 근거를 바탕으로 설명·일정 작성 | 출처 포함 추천 결과 |

## 레이아웃

| 영역 | 내용 |
| --- | --- |
| 좌측 | 데이터 조각: 도시, 축제, 날씨, 장소 |
| 중앙 | Candidate Evidence Package |
| 우측 | 추천 이유와 일정 |

## 발표자 노트

- 낯선 소도시 추천은 신뢰가 핵심입니다.
- 그래서 LLM이 바로 답을 만들지 않고, 먼저 검색된 근거를 Planner가 사용할 수 있는 패키지로 만듭니다.
- 이 구조 덕분에 추천 이유와 출처를 함께 보여줄 수 있습니다.

## 근거·출처

- `../references/agent_deep_dive_slides_condensed_agent_spec_update_proposal.md`

## 제작 체크

- [ ] RAG를 벡터 검색 한 단어로 끝내지 않는다.
- [ ] “근거 패키지” 개념을 시각적으로 보여준다.
