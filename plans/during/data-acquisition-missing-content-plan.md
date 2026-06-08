---
작성자: llm팀
상태: 완료
---

# 데이터 취득 문서 누락 보완 계획

## 목적

현재 데이터 취득 문서 묶음에서 실제 수집, 전처리, 공유 산출물 기준과 맞지 않거나 누락된 내용을 확인한다.

확인 결과를 기준으로 대표 문서, 국가별 상세 문서, 전처리 문서, HTML, PDF 산출물이 같은 의미를 갖도록 수정한다.

## 점검 대상

- 대표 문서: `docs/04_data_collect_plan/04_data_collect_plan.md`
- 한국 상세 문서: `docs/04_data_collect_plan/korea_data_acquisition_plan.md`
- 일본 상세 문서: `docs/04_data_collect_plan/japan_data_acquisition_plan.md`
- 전처리 문서: `docs/04_data_collect_plan/data_preprocessing_plan.md`
- 공유 HTML: `pages/04_data_collect_plan.html`, `index.html`
- PDF 산출물: `pdf/data_collect_plan.*`, `pdf/korea_data_acquisition_plan.*`, 필요 시 일본/전처리 PDF

## 현재 누락 및 보완 후보

| 구분 | 발견 내용 | 보완 방향 |
|---|---|---|
| 전처리 기준 관계 | 한국 데이터 취득 문서는 `VisitorStatistics`를 수집 대상으로 포함하지만 `data_preprocessing_plan.md`의 기준 관계는 `City -> Attraction/Festival`만 표현한다. | `City -> VisitorStatistics` 관계를 추가하고 방문 통계가 월별/지역별 보조 데이터임을 명시한다. |
| 전처리 저장 모델 | 전처리 문서의 DynamoDB 후보 테이블과 정규화 산출물에 방문 통계 항목이 빠져 있다. | `LovvVisitorStatistics` 또는 동등한 통계 저장 후보와 `visitor_statistics_normalized` 산출물을 추가한다. |
| 일본 상세 범위 | 대표 문서는 한국 경북·강원 40개 도시 이후 일본 관동 지자체 수집을 명시하지만 일본 상세 문서에는 관동 우선 범위가 충분히 드러나지 않는다. | 일본 상세 문서의 수집 범위와 우선순위에 관동 지자체 우선 수집을 명시한다. |
| 일본 통계 데이터 | 일본 상세 문서는 JNTO Statistics, e-Stat, RESAS를 언급하지만 대상 모델은 City, Attraction, Festival 중심으로만 정리되어 있다. | 방문/관광 통계를 필수 엔티티로 둘지 후보 데이터로 둘지 결정하고, 결정에 맞춰 모델과 검증 항목을 정리한다. 기본 보완안은 `VisitorStatistics` 후보 추가다. |
| 일본 JSON/S3 계약 | 한국 문서는 `data/KR/*.json` 검증 산출물과 S3 Raw 적재 기준이 명확하지만 일본 상세 문서는 동일 수준의 로컬 JSON 검증 파일 및 Prefix 기준이 약하다. | `data/JP/*.json` 검증 산출물, S3 Raw Prefix, 메타데이터 키 기준을 한국 문서와 같은 수준으로 보강한다. |
| 한국 상세 문서 메타 표현 | 한국 상세 문서 상단에 이미 반영된 문서를 `반영 예정`으로 표현하는 문구가 남아 있다. | `동기화 대상` 또는 `공유 산출물` 표현으로 변경해 현재 상태와 맞춘다. |
| 일본 문서 반영 계획 표현 | 일본 상세 문서의 반영 계획은 파일을 참조하는 방식이 강하고, 최근 한국 문서의 운영 방향 중심 표현과 톤이 다르다. | 어떤 방식으로 수집, 검증, 저장, 공유 산출물에 반영할지를 설명하는 운영 방향 중심 문장으로 수정한다. |
| 생성 산출물 | Markdown 수정 뒤 HTML/PDF가 동일한 의미로 재생성되어야 한다. | HTML과 PDF를 재생성하고, 표·차트·흐름도가 페이지 폭이나 페이지 경계에서 잘리지 않는지 이미지로 확인한다. |

## 실행 순서

1. 문서 기준 재확인
   - `docs/04_data_collect_plan/AGENT.md` 기준에 따라 수집 출처, 빈도, 포맷, 보존, 기상 데이터 처리 기준을 다시 점검한다.
   - 현재 남아 있는 unrelated 변경 파일은 별도 요청이 없으면 수정하지 않는다.

2. 전처리 문서 보완
   - `data_preprocessing_plan.md`의 기준 관계에 `VisitorStatistics`를 추가한다.
   - DynamoDB 후보 테이블, 정규화 산출물, 품질 검증 기준에 방문 통계 데이터를 반영한다.
   - 한국 City ID 예시와 S3 Raw 입력 계약은 기존 기준을 유지한다.

3. 일본 데이터 취득 문서 보완
   - 관동 지자체 우선 수집 범위를 명시한다.
   - 일본 상세 문서에 `data/JP/*.json` 검증 산출물과 S3 Raw Prefix 기준을 추가한다.
   - 일본 관광 통계는 필수 수집 항목 또는 후보 보강 항목 중 하나로 정리한다.
   - 문서 말미의 반영 계획은 파일 나열보다 수집, 검증, 저장, 공유 산출물 반영 방식 중심으로 다시 쓴다.

4. 한국 데이터 취득 문서 정리
   - 상단의 `반영 예정` 표현을 현재 상태와 맞는 표현으로 바꾼다.
   - 이미 확정된 경북·강원 40개 도시, TourAPI 4.0, DataLabService, Wikipedia/Wikidata, 기상청 비교, S3 Raw 적재 기준은 유지한다.

5. 대표 문서 동기화
   - `04_data_collect_plan.md`가 한국·일본 상세 문서 및 전처리 문서의 최종 의미와 맞는지 확인한다.
   - 필요한 경우 일본 방문 통계, `data/JP/*.json`, S3 Raw Prefix, 전처리 연계 표현을 보강한다.

6. 생성 산출물 갱신
   - `pages/04_data_collect_plan.html`과 `index.html`을 대표 문서 기준으로 갱신한다.
   - 수정 범위에 따라 `pdf/data_collect_plan.*`, `pdf/korea_data_acquisition_plan.*`, 필요 시 일본/전처리 PDF를 재생성한다.
   - PDF는 이미지로 확인해 표, 차트, 흐름도, 긴 텍스트가 좌우 폭이나 페이지 경계에서 잘리지 않는지 검증한다.

7. 검증 및 커밋 준비
   - `rg`로 핵심 용어가 문서 간 일관되게 반영되었는지 확인한다.
   - `git diff --check`로 공백 오류를 확인한다.
   - `git status --short`로 unrelated 변경이 커밋 범위에 섞이지 않았는지 확인한다.
   - 사용자가 요청하면 conventional commit 형식으로 관련 파일만 스테이징하고 커밋한다.

## 체크포인트

- 전처리 문서에 `VisitorStatistics` 관계, 저장 후보, 산출물, 검증 기준이 모두 반영되어 있다.
- 일본 상세 문서에 관동 우선 범위와 JSON/S3 Raw 계약이 명확히 들어가 있다.
- 대표 문서와 국가별 상세 문서가 서로 다른 수집 범위나 저장 방식을 말하지 않는다.
- HTML/PDF 산출물이 Markdown 변경 사항과 같은 의미를 갖는다.
- PDF에서 표와 흐름도가 페이지 폭 또는 페이지 경계에서 잘리지 않는다.

## 리스크

- 일본 방문 통계를 필수 엔티티로 추가하면 실제 구현 범위를 과하게 확장할 수 있다.
- PDF 재생성 과정에서 기존 수동 페이지 넘김 조정이 일부 사라질 수 있다.
- 현재 작업과 무관한 기존 변경 파일이 커밋 범위에 섞일 수 있다.

## 확인이 필요한 결정

- 일본 방문 통계를 필수 수집 엔티티로 둘지, 후보/검증 보조 데이터로 둘지 결정해야 한다.
- `korea_data_acquisition_plan_updated.md`를 최종 문서로 병합할지, 참고용 산출물로 유지할지 결정해야 한다.

## 실행 결과

- 일본 방문 통계는 필수 확정 수량이 아니라 City에 연결되는 `VisitorStatistics` 보조 데이터로 반영했다.
- 한국 상세 문서는 대표 문서와 공유 산출물 동기화 상태에 맞춰 메타 표현을 정리했다.
- 일본 상세 문서는 관동 지역 지자체 우선 수집, `data/JP/*.json` 로컬 검증 산출물, S3 Raw Prefix 기준을 보강했다.
- 전처리 문서는 `VisitorStatistics` 관계, 정규화 산출물, DynamoDB 후보 테이블, 적재 조건을 보강했다.
- 대표 Markdown, 공유 HTML, 관련 PDF 산출물을 재생성하고 PDF 이미지 contact sheet로 표와 흐름도 잘림 여부를 확인했다.
