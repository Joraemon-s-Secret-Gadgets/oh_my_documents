---
작성자: llm팀
상태: 진행후
---

# 데이터 전처리 계획서 초안 작성 계획

## 목적

`docs/04_data_collect_plan/04_data_collect_plan.md`와 국가별 데이터 취득 초안을 기준으로 로브 추천 DB와 AI/RAG 파이프라인에 투입할 데이터 전처리 계획서 초안을 작성한다.

## 대상 파일

| 구분 | 경로 | 처리 |
| --- | --- | --- |
| 기준 문서 | `docs/04_data_collect_plan/04_data_collect_plan.md` | 읽기 전용 참조 |
| 기준 문서 | `docs/04_data_collect_plan/korea_data_acquisition_plan.md` | 읽기 전용 참조 |
| 기준 문서 | `docs/04_data_collect_plan/japan_data_acquisition_plan.md` | 읽기 전용 참조 |
| 산출 문서 | `docs/04_data_collect_plan/data_preprocessing_plan.md` | 신규 작성 |

## 유지할 항목

- 수집 계획서의 `City -> Attraction/Festival` 관계 구조
- 전체 필드 선취득 후 검증·보정하는 운영 원칙
- `collected`, `needs_review`, `missing`, `blocked` 취득 상태 체계
- 원본 데이터와 정규화 데이터, 출처·검수 메타데이터 분리 원칙

## 변경할 항목

- 수집 이후 원본 정제, 정규화, 중복 제거, 품질 검증, 파생 피처 생성, 적재 기준을 별도 초안 문서로 정리한다.
- 한국과 일본의 행정구역·명칭·날짜·운영정보·좌표·라이선스 차이를 전처리 규칙으로 명시한다.
- 추천, RAG, 관리자 검수에 필요한 산출 데이터셋과 검증 체크포인트를 정의한다.

## 작업 체크리스트

- [x] 저장소 문서 작성 규칙 확인
- [x] 수집 계획서와 국가별 취득 초안 확인
- [x] 전처리 계획서 초안 구조 설계
- [x] `docs/04_data_collect_plan/data_preprocessing_plan.md` 신규 작성
- [x] Markdown 기본 검증
- [x] 결과 요약

## 검증 방법

- `rg`로 신규 문서 경로와 핵심 제목이 확인되는지 검증한다.
- `git diff --check`로 Markdown 공백 오류를 확인한다.
