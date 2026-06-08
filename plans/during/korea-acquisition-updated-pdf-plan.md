---
작성자: llm팀
상태: 완료
---

# 한국 데이터 취득 업데이트 및 PDF 반영 계획

## 목적

`docs/04_data_collect_plan/korea_data_acquisition_plan_updated.md`의 실제 수집 결과와 API 명세 분석 내용을 기준으로 한국 데이터 취득 관련 문서를 정리하고, Markdown 원본, HTML 생성물, PDF 산출물을 같은 의미로 동기화한다.

이번 계획의 기준은 강원·경북 40개 도시 실제 수집, TourAPI 4.0 KorService2, DataLabService 방문객 통계, `data/KR/*.json` 검증 산출물, S3 Raw Bucket 적재, Lambda 전처리, DynamoDB 적재 흐름이다.

## 현재 확인 결과

| 항목 | 현재 상태 | 조치 방향 |
| --- | --- | --- |
| `korea_data_acquisition_plan_updated.md` | 실제 수집 결과 기반 최신 문서 | 기준 문서로 사용 |
| `korea_data_acquisition_plan.md` | 기존 한국 상세 초안 | 업데이트본을 반영해 갱신 |
| `04_data_collect_plan.md` | 대표 요약 문서 v0.4 | 실제 수집 수량·ID·DataLab 요약 반영 |
| `data_preprocessing_plan.md` | S3/Lambda/DynamoDB 전처리 문서 | 한국 ID 형식과 `data/KR/*.json` 역할 정합화 |
| `pages/04_data_collect_plan.html` | 대표 문서 생성 HTML | 대표 문서 수정 후 재생성 |
| `pdf/korea_data_acquisition_plan.*` | 한국 상세 문서 PDF 산출물 | 한국 상세 원본 기준 재생성 |
| `pdf/data_collect_plan.*` | 대표 데이터 수집 계획 PDF 산출물 | 대표 문서 기준 재생성 |
| `pdf/data_preprocessing_plan.*` | 전처리 계획 PDF 산출물 | 전처리 문서 수정 시 재생성 |

## 반영 기준

- 대표 문서는 `docs/04_data_collect_plan/04_data_collect_plan.md`로 유지한다.
- 한국 상세 기준 문서는 `docs/04_data_collect_plan/korea_data_acquisition_plan.md`로 유지한다.
- `korea_data_acquisition_plan_updated.md`는 반영 기준으로 사용하되, 최종 문서 구조에서는 중복 문서가 되지 않게 정리 방향을 결정한다.
- `data/KR/*.json`은 실제 수집 검증 산출물이자 S3 Raw Bucket 적재 전 로컬 산출물로 설명한다.
- 최종 서비스용 정규화 저장은 S3 Raw Bucket 누적 후 Lambda 전처리를 거쳐 DynamoDB에 적재하는 흐름으로 유지한다.
- 작성자 표기는 데이터 수집 계획 문서 묶음과 일관되게 `LLM 파트`로 맞춘다.
- PDF 문구 변경은 대응하는 `docs/` Markdown 원본을 먼저 수정한 뒤 `pdf/*.tex`와 `pdf/*.pdf`를 재생성한다.

## 반영할 핵심 변경

| 구분 | 반영 내용 |
| --- | --- |
| 우선 수집 범위 | 한국은 강원·경북 40개 도시를 실제 수집 검증 범위로 명시 |
| City ID | `KR-{도_코드}-{CITY_EN}` 형식으로 정리. 예: `KR-42-GANGNEUNG`, `KR-47-ANDONG` |
| 광역 단위 | `province`, `district_type` 중심 표현은 `prefecture_id`와 `data/KR/prefectures.json` 참조 구조로 보강 |
| City 데이터 | `data/KR/cities.json` 40개 도시 수집 결과와 Wikipedia/Wikidata 기반 필드 반영 |
| 기후 데이터 | `climate`와 `climate_table`의 관계를 정리하고, 자동 실패 시 `needs_review`로 관리 |
| 관광지 | TourAPI 4.0 KorService2 기반 관광지 3,709건 수집 결과 요약 반영 |
| 축제 | TourAPI 4.0 KorService2 기반 축제 106건과 테마 수동 재분류 46건 반영 |
| 방문객 통계 | DataLabService 월별 도시별 방문객 통계와 월별 일평균 산출 기준 반영 |
| 저장 구조 | `data/KR/*.json` 로컬 검증 산출물과 S3 Raw/DynamoDB 적재 흐름의 관계 명확화 |
| 검증 기준 | City 매핑, TourAPI 코드 매핑, 포항 통합, 테마 수량, 방문객 통계 월 누락 검증 반영 |

## 대상 파일

| 구분 | 파일 |
| --- | --- |
| 기준 문서 | `docs/04_data_collect_plan/korea_data_acquisition_plan_updated.md` |
| 수정 대상 | `docs/04_data_collect_plan/korea_data_acquisition_plan.md` |
| 수정 대상 | `docs/04_data_collect_plan/04_data_collect_plan.md` |
| 조건부 수정 대상 | `docs/04_data_collect_plan/data_preprocessing_plan.md` |
| 조건부 수정 대상 | `docs/04_data_collect_plan/preprocessing_budget_estimate.md` |
| HTML 생성물 | `pages/04_data_collect_plan.html` |
| PDF TeX 생성물 | `pdf/korea_data_acquisition_plan.tex`, `pdf/data_collect_plan.tex`, `pdf/data_preprocessing_plan.tex` |
| PDF 최종 산출물 | `pdf/korea_data_acquisition_plan.pdf`, `pdf/data_collect_plan.pdf`, `pdf/data_preprocessing_plan.pdf` |

## 작업 체크리스트

### 1. 기준 확정

- [x] `korea_data_acquisition_plan_updated.md`의 문서 버전, 상태, 업데이트 요약을 확인한다.
- [x] 기존 `korea_data_acquisition_plan.md`와 대표 문서가 아직 업데이트본을 참조하지 않음을 확인한다.
- [x] PDF 생성 지침 `pdf/AGENT.md`와 변환 스크립트 `scripts/markdown_to_tex.py`를 확인한다.
- [x] `korea_data_acquisition_plan_updated.md`를 최종 보조 문서로 유지할지, 기존 `korea_data_acquisition_plan.md`에 병합 후 제거할지 결정한다.
  - 결정: 기존 `korea_data_acquisition_plan.md`에 병합하고, 업데이트본은 병합 기준을 남기는 보조 근거 문서로 유지한다.

### 2. 한국 상세 문서 갱신

- [x] `korea_data_acquisition_plan.md`를 업데이트본 기준으로 갱신한다.
- [x] 제목에서 `초안` 표현을 유지할지 실제 수집 결과 반영 문서로 변경할지 정리한다.
- [x] 작성자 표기를 `LLM 파트`로 통일한다.
- [x] `city_id`, `prefecture_id`, `climate_table`, `field_status`를 실제 수집 구조와 맞춘다.
- [x] TourAPI 4.0 KorService2, DataLabService, API Key Rotation, 체크포인트 재시작 정책을 반영한다.
- [x] `data/KR/*.json`은 로컬 검증 산출물이며 이후 S3 Raw Prefix에 업로드되는 입력이라는 설명을 추가한다.

### 3. 대표 문서 갱신

- [x] `04_data_collect_plan.md`의 한국 상세 문서 참조를 최신 기준으로 정리한다.
- [x] 1.2 수집 원칙에 강원·경북 40개 도시 실제 검증 완료 맥락을 추가한다.
- [x] 2.3 City 수집 항목에 `prefecture_id`, `climate_table` 또는 대응 설명을 반영할지 결정한다.
- [x] 2.4 Attraction 수집 항목에 TourAPI 4.0 KorService2와 실제 수집 건수 요약을 반영한다.
- [x] 2.5 Festival 수집 항목에 축제 106건 및 테마 재분류 요약을 반영한다.
- [x] 2.6.1 한국 데이터 출처에 DataLabService와 TourAPI 4.0 역할을 구체화한다.
- [x] 3.1 처리 흐름에서 로컬 `data/KR/*.json` 검증 산출물과 S3 Raw 적재 흐름을 연결한다.
- [x] 변경 이력을 v0.5로 추가하고 작성자를 `LLM 파트`로 기록한다.

### 4. 전처리 문서 정합화

- [x] `data_preprocessing_plan.md`의 한국 City ID 예시를 `KR-{도_코드}-{CITY_EN}` 형식으로 갱신한다.
- [x] `KR-JEONNAM-SUNCHEON` 같은 폐기 예시가 남아 있는지 확인한다.
- [x] `data/KR/*.json`을 S3 Raw 업로드 전 검증 산출물 또는 Manifest 입력으로 설명할 필요가 있는지 반영한다.
- [x] `climate`와 `climate_table`의 전처리 매핑 기준을 명시한다.
- [x] 전처리 문서를 수정했다면 변경 이력을 추가한다.

### 5. HTML 생성물 갱신

- [x] `python scripts\generate_pages.py`를 실행해 `pages/04_data_collect_plan.html`을 갱신한다.
- [x] `python scripts\verify_pages_structure.py`로 페이지 구조를 검증한다.
- [x] `rg`로 `TourAPI 4.0`, `DataLabService`, `KR-42-GANGNEUNG`, `S3 Raw Bucket`, `DynamoDB`가 Markdown과 HTML에 같은 의미로 반영됐는지 확인한다.
- [x] 필요 시 `index.html`의 데이터 수집 문서 카드 설명이나 버전 표기를 갱신한다.

### 6. PDF 재생성

- [x] `korea_data_acquisition_plan.md` 기준으로 `pdf/korea_data_acquisition_plan.tex`를 재생성한다.
- [x] `04_data_collect_plan.md` 기준으로 `pdf/data_collect_plan.tex`를 재생성한다.
- [x] `data_preprocessing_plan.md`를 수정했다면 `pdf/data_preprocessing_plan.tex`를 재생성한다.
- [x] `xelatex`를 각 TeX마다 두 번 실행해 목차와 페이지 번호를 안정화한다.
- [x] `Select-String -Path pdf\*.log -Pattern 'Overfull \\hbox'`로 표·차트 잘림을 확인한다.
- [x] `pdftotext -layout`으로 핵심 섹션이 누락 없이 출력되는지 확인한다.
- [x] 필요하면 PDF를 이미지로 렌더링해 표 좌우 폭과 페이지 넘김을 육안 검수한다.

### 7. PDF 생성 명령 기준

- [x] 한국 상세 PDF 생성 명령을 실행한다.

```powershell
python scripts\markdown_to_tex.py docs\04_data_collect_plan\korea_data_acquisition_plan.md pdf\korea_data_acquisition_plan.tex --title "한국 데이터 취득 계획서" --author "이창우, 전승권, 전종혁, 조동휘, 최수아" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스 데이터 수집 계획" --section-pagebreak --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"
```

- [x] 대표 데이터 수집 PDF 생성 명령을 실행한다.

```powershell
python scripts\markdown_to_tex.py docs\04_data_collect_plan\04_data_collect_plan.md pdf\data_collect_plan.tex --title "데이터 수집 계획서" --author "이창우, 전승권, 전종혁, 조동휘, 최수아" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스 데이터 수집 계획" --section-pagebreak --body-pagebreak-before "2.3 City 수집 항목" "2.4 Attraction 수집 항목" "2.6 데이터 출처" "2.6.2 일본 데이터 출처" --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"
```

- [x] 전처리 PDF가 변경 대상이면 생성 명령을 실행한다.

```powershell
python scripts\markdown_to_tex.py docs\04_data_collect_plan\data_preprocessing_plan.md pdf\data_preprocessing_plan.tex --title "데이터 전처리 계획서" --author "이창우, 전승권, 전종혁, 조동휘, 최수아" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스 데이터 수집 계획" --section-pagebreak --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"
```

### 8. 최종 검증

- [x] `git diff --check`로 공백 오류를 확인한다.
- [x] `git status --short`로 변경 파일 범위를 확인한다.
- [x] `git diff --name-status`로 Markdown, HTML, PDF 산출물이 의도한 범위에만 포함되는지 확인한다.
- [x] `korea_data_acquisition_plan_updated.md`의 처리 방향이 변경 파일 목록에 맞게 정리됐는지 확인한다.
- [x] Conventional Commit이 필요하면 문서/HTML/PDF 변경을 한 커밋으로 묶되, 무관한 `pages/06_database_design.html` LF/CRLF 상태 변경은 제외한다.
  - 확인: `pages/06_database_design.html`은 내용 diff가 없고 line-ending 상태만 남아 있으므로 이번 변경 범위에서 제외한다.

## 수용 기준

- 한국 데이터 취득 기준 문서가 실제 수집 결과와 API 명세 분석을 반영한다.
- 대표 데이터 수집 계획서가 한국 상세 문서의 실제 수집 결과를 과도하게 길게 복사하지 않고 요약 반영한다.
- `data/KR/*.json`과 S3 Raw Bucket, Lambda, DynamoDB의 관계가 문서 전체에서 충돌하지 않는다.
- `KR-{도_코드}-{CITY_EN}` ID 형식이 한국 데이터 취득 문서와 전처리 문서에서 일관된다.
- HTML과 PDF 산출물이 최신 Markdown 원본과 같은 의미를 가진다.
- PDF 표와 코드 블록이 좌우로 잘리지 않고, `Overfull \hbox`가 새로 남지 않는다.

## 위험 및 대응

| 위험 | 대응 |
| --- | --- |
| 업데이트본과 기존 한국 상세 문서가 중복 문서로 남음 | 기존 `korea_data_acquisition_plan.md`에 병합하고 업데이트본은 삭제 또는 보조 근거 문서로 명확히 분리한다. |
| 로컬 `data/KR/*.json`이 최종 DB처럼 오해됨 | 로컬 검증 산출물 및 S3 Raw 적재 입력이라고 명시한다. |
| PDF 재생성으로 표가 다시 잘림 | `pdf/AGENT.md`의 표/차트 하네스를 따라 변환 스크립트 규칙을 우선 조정한다. |
| 전처리 문서의 기존 ID 예시가 남아 충돌함 | `rg -n "KR-JEONNAM-SUNCHEON|KR-42-GANGNEUNG|KR-47-ANDONG"`로 잔여 예시를 확인한다. |
| 무관한 DB 설계 HTML 줄바꿈 상태가 커밋에 섞임 | staging 전 `git diff --name-status`로 관련 파일만 선별한다. |
