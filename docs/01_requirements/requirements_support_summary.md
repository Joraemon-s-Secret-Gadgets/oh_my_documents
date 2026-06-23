# 요구사항 보조 문서 정리안

> 문서 성격: 보조 Markdown 정리안
> 대표 문서: `01_requirements.md`
> 정리일: 2026-06-23
> 백업 위치: `docs/01_requirements/bak/2026-06-23_before_requirements_split/`

이 문서는 `docs/01_requirements/`의 보조 Markdown을 대표 요구사항 문서에 어떻게 반영할지 정리한 보조 문서다. 원문 보조 문서는 삭제하지 않고 유지하며, 정리 전 원본은 `bak` 폴더에 백업했다.

## 운영 원칙

- 대표 요구사항 문서는 `01_requirements.md`다.
- 보조 문서는 요구사항 후보·근거 자료다.
- 확정 내용은 대표 문서의 기능 요구사항, 데이터 요구사항, 제약사항, 변경 이력에 통합한다.
- 아직 검토 단계인 내용은 P5 또는 향후 검토 후보로 유지한다.
- 대표 문서의 1~10 장 구조는 유지한다.

## 보조 문서 분류

| 분류 | 문서 | 상태 |
| --- | --- | --- |
| 핵심 추천·시장 문제 | `overturizim.md`, `korea_japan.md`, `weather_first.md` | P1 반영 |
| 일본 확장 | `japan_add_function.md` | P2 반영 |
| 미디어·교통·체험 확장 | `animation.md`, `kdrama-pipeline.md`, `trip_train.md`, `craft_experience.md` | P3 반영 |
| 개인화·에이전트 | `personalization.md`, `lovv_agent_multiturn_context_spec.md` | P3~Production 반영 |
| 계절 액티비티 | `seasonal_activity.md` | P4 반영 |
| 향후 검토 후보 | `astro_rag_proposal.md`, `healing_wellness.md`, `budget_first.md` | P5 유지 |
| 우선순위 메모 | `priority_plan.md` | P1~P5 기준 자료 |

## 추가 요약 문서

| 파일 | 역할 |
| --- | --- |
| `recommendation_expansion_summary.md` | 미디어, 철도, 체험, 액티비티, P5 후보 정리 |
| `agent_personalization_summary.md` | 개인화와 멀티턴 컨텍스트 요구사항 정리 |

## 대표 문서 반영 완료 항목

- 문서 버전 `v1.9`로 갱신
- 보조 문서의 P1~P5 분류 기준을 `4.6 서비스별 세부 기능`에 반영
- P5 향후 검토 후보의 검토 조건을 명시
- 별 관측 후보 데이터를 `7.1 필요 데이터 항목`에 후보 데이터로 추가
- P5 후보의 제약사항을 `8.2 가정사항`에 추가
- 변경 이력에 보조 문서 정리 내역 추가
