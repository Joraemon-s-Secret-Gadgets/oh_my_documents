# 로브(Lovv) 프로젝트 기획서 보조 문서 정리안

> 문서 성격: 보조 Markdown 정리안
> 대상 문서: `../00_project_plan.md` v0.5
> 정리일: 2026-06-23
> 백업 위치: `docs/00_project_plan/bak/2026-06-23_before_project_plan_split/`

이 문서는 기존 `00_project_plan_revision_plan.md`의 긴 수정 플랜을 AGENT 규칙에 맞게 정리한 보조 문서다. 원본 수정 플랜과 `update_project_plan.md`는 위 `bak` 폴더에 백업되어 있다.

## 정리 원칙

- `sections/*.md`는 프로젝트 기획서 본문 수정 원본이고, `00_project_plan.md`는 공개·공유 기준 통합 대표 기획서로 유지한다.
- 세부 근거와 초안은 문단 단위가 아니라 논리 단위 보조 Markdown으로 분리한다.
- 보조 Markdown은 정본이 아니며, 대표 기획서에 반영할 근거·결정·초안을 추적하기 위한 작업 문서다. 보조 Markdown은 `supplemental/` 폴더에 둔다.
- 상세 문서(03, 92~96 등)의 원문은 각 폴더의 대표 문서를 기준으로 한다.

## 보조 문서 목록

| 파일 | 역할 |
| --- | --- |
| `market_positioning.md` | 트리플·트립닷컴 대비 Lovv 포지셔닝, 카피, 설명 가능한 RAG 차별점 |
| `feature_scope_summary.md` | 대표 기획서와 동일한 사용자 흐름, 사용자 기능, 추천 기능, 운영·관리 기능 상세 |
| `business_model.md` | 대표 기획서와 동일한 B2C 수요·가치 검증, B2B 성과형 제휴, B2G 비과금 공익 협력 |
| `kick_summary.md` | KICK(P2) 정의, 공개 일정·1탭 복제, 개인정보·cold start 원칙 |
| `aha_moment_summary.md` | 추천 경험의 aha 정의, funnel, cold start, 취향 프로필 요약 |
| `data_ops_scope.md` | 대표 기획서와 동일한 PoC 데이터 범위, 날씨 역할 구분, 데이터 파이프라인, 운영 리스크 |
| `technical_direction_summary.md` | 대표 기획서와 동일한 Explainable RAG 파이프라인, 시스템 원칙, 데이터 파이프라인 연결 |
| `sections/*.md` | 대표 기획서의 최상위 `#` 장 기준 하위 Markdown |

## 대표 문서 반영 완료 항목

- 기획서 버전 `v0.5`로 갱신
- 제품 불변 규칙(추천 1건 = 소도시 1곳) 반영
- KICK을 P2 설계 범위에 편입
- 기존 1~14 장 구조를 유지하고, 비즈니스 모델(B2C·B2B·B2G)은 `7.4 비즈니스 모델`로 반영
- PoC 데이터 범위와 한일 전국 확장 방향 반영
- WeatherAPI와 월별 기후 경향 데이터의 역할 분리
- 공개 일정 스냅샷·사본 계보·patch 계약 방향 반영
- 2026-06-23 이후 추진 일정 반영
- 상세 사용자 흐름, 기능 목록, 운영 기능, 기술 파이프라인을 보조 Markdown으로 분리
- `feature_scope_summary.md`의 사용자 흐름, 기능 목록, 운영 기능 상세는 대표 기획서에도 동일하게 반영
- 시장 포지셔닝, Aha Moment, KICK, 비즈니스 모델, 데이터·운영 범위, 기술 방향 보조 MD 내용을 대표 기획서에도 동일하게 반영
- 대표 기획서 최상위 `#` 장 기준 하위 Markdown을 `sections/`에 생성

## 미반영 유지 항목

- B2C 과금·가격 모델
- B2G 영리화 시나리오
- 상세 문서의 실험표, 이벤트 명세, API operation 전문, 수익성 시뮬레이션 전문

위 항목은 대표 기획서에 직접 병합하지 않고 상세 문서 또는 보조 Markdown 참조로 유지한다.
