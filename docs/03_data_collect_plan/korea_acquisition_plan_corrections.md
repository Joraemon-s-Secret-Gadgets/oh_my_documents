# 한국 데이터 취득 계획서 수정 사항 (샘플 코드 대조)

> 문서 버전: v0.1
> 문서 상태: 초안 (Draft) — 보조 문서(수정 제안)
> 작성일: 2026-06-09
> 작성자: 조동휘
> 대조 기준 코드: `Gloveman/tour-api-korea` (main) — 현재 한국 수집 샘플 코드
> 대상 문서: `docs/03_data_collect_plan/korea_data_acquisition_plan_updated.md` v0.2, `docs/03_data_collect_plan/03_data_collect_plan.md`

## 0. 문서 목적

본 문서는 현재 한국 수집 샘플 코드(`tour-api-korea`)의 **실제 동작·산출 구조**를 기준으로, 한국 데이터 취득 계획서(이하 "취득 계획서")에서 **실제와 다른 부분**을 식별하고 수정안을 제안한다. AGENT.md 규칙에 따라 본 문서는 보조 Markdown(수정 제안 초안)이며, 대표 문서(`03_data_collect_plan.md`)·갱신 문서(`korea_data_acquisition_plan_updated.md`)는 사용자 승인 후 반영한다.

신뢰도 표기: 코드 원문에서 직접 확인한 항목은 **신뢰도: 높음**, 코드에 미구현이라 설계 의도와 실제가 갈리는 항목은 **신뢰도: 확인 필요**로 표기한다.

## 1. 대조한 코드 산출물 (사실 기준)

| 스크립트 | 단계 | 핵심 산출물 |
| --- | --- | --- |
| `scrape_list.py` | 리스트 수집 | `areaBasedList2`(관광지)·`searchFestival2`(축제) → `data/raw/list/{regn}_{sig}_raw.json`·`_filtered.json` |
| `group_lists_by_city.py` | 도시 그룹화 | `data/raw/list_by_city/*.json` (40개 도시) |
| `filter_existing_lists.py` | 테마·오버라이드 | 테마 매핑 + 축제 오버라이드 46건(코드 내 하드코딩) |
| `scrape_details.py` | 상세 수집 | `detailCommon2`·`detailIntro2` → `data/raw/detail/{contentid}.json` (`{common,intro}`), 체크포인트 `data/download_progress.json` |
| `merge_to_final.py` | 병합 | `data/raw/final/{city_en}.json` (각 레코드에 `detail` 부착) |
| `scrape_and_aggregate_visitor.py` | 방문통계 | `DataLabService/locgoRegnVisitrDDList`, 월별 일평균 → final 파일에 `visitor_statistics` **임베드** + `data/visitor/monthly_visitor_averages.json` |
| `normalize_details.py` | 정규화(사용자 영역) | `data/city/{city_en}.json` (`city`·`attractions`·`festivals`·`metadata`) |

## 2. 수정 필요 항목 요약

| # | 항목 | 취득 계획서 현행 | 실제 코드 | 신뢰도 |
| --- | --- | --- | --- | --- |
| 1 | City ID | `KR-42-GANGNEUNG` (도 숫자코드) | `KR-GW-GANGNEUNG` (도 영문약자 GW/GB) | 높음 |
| 2 | Attraction/Festival ID | `KR-42-GANGNEUNG-ATT-{id}` / `-FES-` | `ATT-{contentid}` / `FEST-{contentid}` | 높음 |
| 3 | 광역 단위 모델 | `prefecture_id` 외래키 + `data/KR/prefectures.json` | `province` + `district_type` 사용, `prefecture_id`·`prefectures.json` 없음 | 높음 |
| 4 | 데이터 파일 구조 | `data/KR/{prefectures,cities,attractions,festivals,visitor_statistics}.json` | `data/raw/{list,list_by_city,detail,final}/`, `data/city/`, `data/visitor/` | 높음 |
| 5 | 방문통계 저장 | 독립 엔티티 `data/KR/visitor_statistics.json` | final 파일 내부 `visitor_statistics`에 **임베드** + 전역 요약본 | 높음 |
| 6 | 방문통계 필드명 | `local_daily_avg`·`outsider_daily_avg`·`foreigner_daily_avg` | `locals_daily_avg`·`out_of_town_daily_avg`·`foreigners_daily_avg`(+`_total`,`total_visitors`,`total_daily_avg`,`annual_*`) | 높음 |
| 7 | 방문통계 엔드포인트 | `stayAnalysisVisitorList` | `locgoRegnVisitrDDList` | 높음 |
| 8 | 테마 매핑 키 | `lclsSystm1·2·3` | 조회 키 = `lclsSystm3 or cat3`, 추가로 `lclsSystm1=="C01"` 하드 제외 | 높음 |
| 9 | 축제 오버라이드 위치 | `crawling/KR/targets/festival_theme_overrides.json` | `filter_existing_lists.py` 내 `fest_overrides` 딕셔너리(contentid 키, 46건) | 높음 |
| 10 | tel 폴백(infocenter) | 100% 결측 → infocenter 계열 폴백 적재 | `normalize_details.py`에 tel 필드·폴백 **미구현** | 확인 필요 |
| 11 | City 설명·기후 | Wikipedia 설명 + `climate_table` wikitext | `description`="{도시} 관광 정보"(placeholder), `climate`="기상청 API 연계 예정"(placeholder) | 높음 |
| 12 | City 좌표 출처 | Wikipedia/Wikidata 위·경도 | Excel `korea_region_latitude_longitude.xlsx` 또는 관광지 좌표 centroid | 높음 |
| 13 | `data_confidence` 형식 | 신뢰도 등급/점수 | 문자열 + 역논리: `opening_hours`/`usefee` 있으면 `needs_review`, 없으면 `collected` | 높음 |
| 14 | `field_status` | 레코드별 필드 상태 객체 | 정규화 산출물에 미포함(`data_confidence` 단일 + `verified_*`=null) | 높음 |

## 3. 항목별 상세 수정안

### 3.1 City ID 형식 (#1) — 신뢰도: 높음

`normalize_details.py`는 `city_id = f"KR-{prov_en}-{city_en.upper()}"`이며 `prov_en`은 강원=`GW`, 경북=`GB`다. 따라서 실제 ID는 `KR-GW-GANGNEUNG`, `KR-GB-ANDONG` 형태다.

- 취득 계획서 §2.2의 `KR-42-GANGNEUNG`(강원=42), `KR-47-ANDONG`(경북=47) 예시는 코드와 불일치.
- **수정안(택1)**: (A) 문서를 코드에 맞춰 `KR-GW-*`·`KR-GB-*`로 정정, 또는 (B) 코드를 행정표준코드(42/47) 기반으로 변경하기로 합의되었다면 코드 수정 과제로 분리. 현재 정본 결정 전까지 문서에 **두 형식 병기 금지**, 한쪽으로 확정 권고.

### 3.2 Attraction/Festival ID (#2) — 신뢰도: 높음

코드: `attraction_id = f"ATT-{content_id}"`, `festival_id = f"FEST-{content_id}"`. City 접두어가 없고 축제는 `FES`가 아니라 `FEST`다.

- 취득 계획서 §5.4의 `KR-{도_코드}-{CITY_EN}-ATT-{contentId}` / `-FES-`와 불일치.
- **수정안**: City 매핑은 별도 `city_id` 필드로 유지되므로, ID에 City를 접두하지 않는 현 코드 방식을 정본으로 하거나, 전처리(서비스 적재) 단계에서 `KR-{도}-{CITY}-ATT-{contentid}` 형태로 재구성하는 규칙을 명시. 약어는 `FES`/`FEST` 중 하나로 통일.

### 3.3 광역 단위 모델 (#3) — 신뢰도: 높음

취득 계획서 v0.2는 `province`/`district_type`를 `prefecture_id`로 대체하고 `data/KR/prefectures.json`을 도입한다고 명시했으나, 코드는 여전히 `province`(문자열)와 `district_type`(시/군/구)을 쓰고 `prefecture_id`·`prefectures.json`이 없다.

- **수정안**: (A) 코드가 정본이면 문서의 `prefecture_id`/`prefectures.json` 도입 문구를 "향후 과제"로 강등, 또는 (B) 모델을 정본으로 유지하려면 코드에 `prefecture_id` 산출을 추가하는 과제로 등록. 현 시점 문서는 미구현 모델을 확정 사실처럼 기술하므로 표현 완화 필요.

### 3.4 데이터 파일 구조 (#4) — 신뢰도: 높음

취득 계획서 §7.1의 `data/KR/{prefectures,cities,attractions,festivals,visitor_statistics}.json` 분리 구조는 코드에 존재하지 않는다. 실제 산출 경로는 다음과 같다.

```text
data/
├── ldong_sigungu.json            # 수집 대상 행정 표준 코드(입력)
├── theme_mapping.json            # 관광지 테마 매핑(입력)
├── festival_mapping.json         # 축제 테마 매핑(입력)
├── classification_dict.json      # 분류 코드 사전(입력)
├── download_progress.json        # 상세 수집 체크포인트
├── raw/
│   ├── list/{regn}_{sig}_raw.json, _filtered.json
│   ├── list_by_city/{city_en}.json
│   ├── detail/{contentid}.json          # {common, intro}
│   └── final/{city_en}.json             # 리스트+detail (+visitor_statistics 임베드)
├── city/{city_en}.json           # 정규화 산출물(city/attractions/festivals/metadata)
└── visitor/monthly_visitor_averages.json
```

- **수정안**: 취득 계획서의 저장 구조 절을 위 실제 경로로 교체. 전처리 입력 정본은 `data/raw/final/{city_en}.json`(+임베드 통계)과 정규화본 `data/city/{city_en}.json`임을 명시.

### 3.5 방문통계: 임베드 vs 독립 엔티티 (#5, #6, #7) — 신뢰도: 높음

코드 사실:
- 엔드포인트는 `DataLabService/locgoRegnVisitrDDList`(일별 지역 방문자). `stayAnalysisVisitorList` 아님.
- `touDivCd`: **1=현지인(locals), 2=외지인(out_of_town), 3=외국인(foreigners)**. 월별 `touNum` 합산 후 월 일수로 나눠 일평균 산출.
- 결과는 `data/raw/final/{city_en}.json`의 `visitor_statistics`(`year`,`annual_totals`,`annual_daily_averages`,`monthly_statistics[]`)로 **임베드**되고, 전역 요약 `data/visitor/monthly_visitor_averages.json`에도 저장.
- `monthly_statistics[]` 필드: `month, days, locals_total, locals_daily_avg, out_of_town_total, out_of_town_daily_avg, foreigners_total, foreigners_daily_avg, total_visitors, total_daily_avg`.

취득 계획서 §2.5는 독립 파일 `data/KR/visitor_statistics.json`과 `local_daily_avg`·`outsider_daily_avg`·`foreigner_daily_avg` 필드명을 쓴다.

- **수정안**: (1) 엔드포인트를 `locgoRegnVisitrDDList`로 정정. (2) 필드명을 코드(`locals_*`/`out_of_town_*`/`foreigners_*`)에 맞추거나, 서비스 표준명(`local`/`outsider`/`foreigner`)을 쓰려면 **전처리 단계 매핑 규칙**으로 명시. (3) 취득 단계 산출은 "final 파일 내부 임베드"가 사실이며, "독립 엔티티 분리"는 **전처리(ELT) 단계의 변환 목표**임을 구분해 기술(취득 vs 전처리 경계 정렬).

### 3.6 테마 매핑·제외·오버라이드 (#8, #9) — 신뢰도: 높음

코드 사실:
- 관광지/축제 모두 `lclsSystm1 == "C01"`이면 무조건 제외.
- 테마 조회 키는 `code = lclsSystm3 or cat3` (소분류 우선, cat3 폴백). 매핑 사전은 `theme_mapping.json`/`festival_mapping.json`.
- `should_exclude`는 매핑 사전 항목의 `large_category`(체험관광), `middle_category`(기타문화관광지·레저스포츠시설·교육시설·공연시설·복합관광시설), `name`(기타주점·클럽·기타간이음식·북한관광지·기타안보관광지·기타 종교성지·약수터)을 제외.
- 축제 오버라이드 46건은 `filter_existing_lists.py`의 `fest_overrides`에 contentid→테마로 **하드코딩**.

취득 계획서 §8은 테마 기준을 `lclsSystm1·2·3`로, 오버라이드를 `crawling/KR/targets/festival_theme_overrides.json`로 기술.

- **수정안**: (1) 테마 매핑 키를 "`lclsSystm3`(소분류) 우선, `cat3` 폴백"으로 정정. (2) `lclsSystm1=="C01"` 하드 제외 규칙 추가. (3) 오버라이드 위치를 실제(코드 내 `fest_overrides`, 또는 `data/festival_mapping.json`)로 정정하고, 운영상 외부 파일화가 목표라면 별도 과제로 표기.

### 3.7 tel 폴백 미구현 (#10) — 신뢰도: 확인 필요

취득 계획서 §5.4와 전처리 문서는 `tel` 100% 결측 시 `infocenter`/`infocenterculture`/`infocenterfood`/`sponsor1tel` 폴백을 규정한다. 그러나 제공된 `normalize_details.py`에는 **`tel` 필드 자체가 없고 폴백 로직도 없다**(연락처를 출력하지 않음).

- **수정안**: (A) tel 폴백을 실제로 적용하려면 정규화/전처리 단계에 폴백 구현을 추가(과제 등록), (B) 또는 현 코드대로 연락처 미수집이 정본이면 문서의 tel 폴백 규정을 "전처리 단계 적용 예정"으로 명시. 어느 쪽이든 현재 "적용 필요/적용" 단정 표현은 사실과 어긋남.

### 3.8 City 설명·기후·좌표 (#11, #12) — 신뢰도: 높음

코드 사실: `normalize_details.py`의 City는 `description="{도시명} 관광 정보"`, `climate="기상청 API 연계 예정"`, `site_url=""` 플레이스홀더이며, 좌표는 Excel `korea_region_latitude_longitude.xlsx`(시트 `location`) 우선, 없으면 관광지 좌표 평균(centroid), 둘 다 없으면 `(36.5, 128.0)` 폴백.

취득 계획서는 City를 Wikipedia/Wikidata 기반(설명·`climate_table` wikitext·좌표)으로 기술.

- **수정안**: City 보강(Wikipedia 설명, `climate_table`, 공식 site_url)은 **아직 코드에 없음**을 명시하고 "향후 보강 소스"로 표기. 좌표 출처를 Excel/centroid로 정정. 기후는 기상청 연계 예정(placeholder) 상태로 정정.

### 3.9 신뢰도/상태 표현 (#13, #14) — 신뢰도: 높음

코드의 `data_confidence`는 숫자 점수가 아니라 문자열이며, 관광지의 경우 `opening_hours` 또는 `usefee`가 **있으면** `needs_review`, 없으면 `collected`로 둔다(변동성 큰 필드 존재 시 검수 필요로 본 역논리). 또한 정규화 산출물에는 `field_status` 객체가 없고 `verified_at/verified_source_url/verification_note=null`만 둔다.

- **수정안**: 취득 계획서의 `field_status`(필드별 상태) 예시와 신뢰도 점수 서술을, 코드 실제(레코드 단위 `data_confidence` 문자열 + `verified_*`)와 정렬하거나, `field_status`를 전처리 단계 산출로 분리 기술. 신뢰도 점수(0~1) 모델은 전처리 문서 소관임을 교차 참조.

## 4. 적용 우선순위 제안

| 우선순위 | 항목 | 이유 |
| --- | --- | --- |
| P1 (즉시) | #1 City ID, #2 ATT/FEST ID, #7 엔드포인트, #5/#6 방문통계 구조·필드 | 다운스트림 DB 설계·전처리 계약에 직접 영향 |
| P2 | #4 파일 구조, #8/#9 테마·오버라이드, #13 data_confidence | 입력 계약·정합성 검증 기준 |
| P3 | #3 prefecture 모델, #10 tel 폴백, #11/#12 City 보강, #14 field_status | 설계 의도 vs 미구현 — 과제화/표현 완화 |

## 5. 미해소 확인 사항

- **수량 차이**: 취득 계획서·전처리 문서의 테마별 관광지 합계 **4,911건**과 실제 적재 **3,709건**(README·`merge_to_raw_detail` 기준, 명소 3,709 + 축제 106 = 상세 3,815)의 차이 1,202건. 코드상 필터는 `lclsSystm3` 테마 매핑 + `should_exclude` + `C01` 제외로, 4,911은 매핑 후보(다중/중복 포함) 추정값일 가능성이 높다. **정본은 3,709건**으로 두고 차이 원인은 전처리 수량 정합 검증에서 재집계 권고. (신뢰도: 확인 필요)
- City ID 도 코드 정책(영문 `GW`/`GB` vs 숫자 `42`/`47`) 최종 결정 필요(#1, #3 연동).

## 6. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-09 | 조동휘 | `tour-api-korea` 샘플 코드 대조로 취득 계획서 수정 필요 14개 항목 식별 및 수정안·우선순위 정리 |
