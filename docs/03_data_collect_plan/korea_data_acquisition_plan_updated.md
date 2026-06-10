# 한국 데이터 취득 계획서

> 문서 버전: v0.3
> 문서 상태: 실제 수집 샘플 코드(tour-api-korea) 산출물 기준으로 최신화
> 원본 문서: `oh_my_documents/docs/03_data_collect_plan/korea_data_acquisition_plan.md` v0.1
> 작성일: 2026-06-06 (v0.3 최신화: 2026-06-09)
> 작성자: 조동휘
> 반영 예정 문서: `docs/03_data_collect_plan/03_data_collect_plan.md`
> 반영 예정 HTML: `pages/03_data_collect_plan.html` (재생성 보류)
> 대조 기준 코드: `Gloveman/tour-api-korea` (main)
> 불일치 정리: `docs/03_data_collect_plan/korea_acquisition_plan_corrections.md` v0.1

> **[업데이트 요약]**
> 실제 데이터 수집(`tour-api-korea` 레포지토리)의 **소스 코드 11종을 직접 대조**하여 강원(GW)·경북(GB) 지역 데이터 수집 구조를 사실 기준으로 최신화하였다.
> 이 문서는 실제 수집 산출물(`data/raw/final/{city_en}.json` + 임베드 통계, 정규화본 `data/city/{city_en}.json`) 및 코드 동작을 기준으로 데이터 모델을 갱신한 것이다.
> 변경 사항은 `> [변경]` 블록으로 표시하며, v0.3 코드 대조 정정은 `> [코드정정]` 블록으로 표시한다.
> 신뢰도: 코드 원문에서 직접 확인한 항목은 사실로 기술하고, 코드에 미구현인 설계 의도는 "향후 과제"로 명시한다.

---

# 1. 목적

본 문서는 여행 추천 Multi-Agent 서비스에서 한국 소도시 추천에 필요한 도시·관광지·축제 데이터를 한 번에 취득하기 위한 범위, 데이터 소스, 검증 방식, 저장 구조를 정의한다.

이번 문서의 핵심은 다음과 같다.

- City, Attraction, Festival의 정의된 항목을 모두 수집 대상으로 둔다.
- 한국관광공사 TourAPI 4.0(KorService2) 및 관광 빅데이터 API(DataLabService)를 중심으로 관광지·축제 정보를 취득한다.
- 운영시간, 운영기간, 입장료, 사진처럼 출처별 표현 차이가 큰 항목도 최초 취득 범위에 포함한다. 단, TourAPI에서 실제 제공률이 낮은 항목은 `missing`으로 관리한다.
- 자동 수집, 공식 사이트 확인, Web Search Worker, 수동 검수를 하나의 취득 파이프라인으로 묶어 처리한다.
- 추천 DB는 `City 1:N Attraction`, `City 1:N Festival` 관계를 기준으로 설계한다.
- 관광지·축제는 6대 핵심 테마로 분류하여 관리한다.

---

# 2. 목표 데이터 모델

## 2.1 관계 구조

```text
Prefecture
 └── City
      ├── Attraction
      ├── Festival
      └── VisitorStatistics
```

| 관계 | 설명 |
| --- | --- |
| `Prefecture 1:N City` | 강원과 경북 같은 광역 단위는 여러 City를 가진다. |
| `City 1:N Attraction` | 하나의 한국 도시는 여러 관광지를 가진다. |
| `City 1:N Festival` | 하나의 한국 도시는 여러 축제·행사를 가진다. |
| `City 1:N VisitorStatistics` | 하나의 한국 도시는 월별 방문객 통계 데이터를 가진다. |

## 2.2 City 데이터

City는 추천의 기준 지역이다. 한국 목적지는 시·군·구 단위의 소도시를 기본 단위로 관리한다.

> [코드정정] `city_id` 실제 형식은 `KR-{도_영문약자}-{CITY_EN}`이다. 도 영문약자는 강원=`GW`, 경북=`GB`. 예: `KR-GW-GANGNEUNG`(강릉시), `KR-GB-ANDONG`(안동시). v0.2의 도 숫자코드(`KR-42-*`, `KR-47-*`) 표기는 코드와 불일치하므로 폐기한다. (행정표준코드 42/47 기반으로 전환할지는 별도 정책 결정 사항)
> [코드정정] 정규화 코드(`normalize_details.py`)는 `province`(문자열)와 `district_type`(시/군/구)를 사용한다. `prefecture_id` 외래키와 `data/KR/prefectures.json`은 **코드에 미구현**이며 향후 모델링 과제다.
> [코드정정] City의 `description`·`climate`는 현재 코드에서 플레이스홀더(`"{도시명} 관광 정보"`, `"기상청 API 연계 예정"`)로 채워진다. Wikipedia 설명·`climate_table` wikitext, 기상청 기후 연계는 **향후 보강 과제**다.
> [코드정정] City 좌표는 Excel `korea_region_latitude_longitude.xlsx`(시트 `location`) 우선, 없으면 관광지 좌표 평균(centroid), 둘 다 없으면 `(36.5, 128.0)` 폴백으로 산출된다(Wikidata 직접 취득 아님).

| 필드 | 수집 방식(코드 기준) | 상태 | 설명 |
| --- | --- | --- | --- |
| `city_id` | 내부 생성 | ✅ 코드 확인 | `KR-{GW\|GB}-{CITY_EN_UPPER}` (예: `KR-GW-GANGNEUNG`) |
| `city_name_ko` | 수집 메타 | ✅ 코드 확인 | 한국어 도시명 |
| `city_name_en` | 내부 영문 변환 | ✅ 코드 확인 | 영문 도시명(파일명 키) |
| `province` | 수집 메타 | ✅ 코드 확인 | 광역 문자열(예: 강원특별자치도) |
| `district_type` | 내부 파생 | ✅ 코드 확인 | 시/군/구 |
| `location` | 내부 조합 | ✅ 코드 확인 | `{province} {city_name_ko}` |
| `latitude` / `longitude` | Excel / centroid 폴백 | ✅ 코드 확인 | 공식 좌표표 우선, 없으면 관광지 평균 |
| `description` | placeholder | ⚠️ 미보강 | 현재 `"{도시명} 관광 정보"`. Wikipedia 보강 예정 |
| `climate` | placeholder | ⚠️ 미보강 | 현재 `"기상청 API 연계 예정"`. 기상청 연계 예정 |
| `site_url` | (빈 값) | ⚠️ 미보강 | 현재 `""`. 지자체 관광 URL 보강 예정 |
| `prefecture_id` | — | ❌ 미구현 | 향후 광역 외래키 모델 도입 과제 |
| `climate_table` | — | ❌ 미구현 | 향후 Wikipedia wikitext 보존 과제 |

## 2.3 Attraction 데이터

Attraction은 도시와 1:N 관계를 가지며, 일정 카드와 추천 결과 상세 화면의 핵심 소재로 사용한다.

아래 필드는 실제 수집 과정(tour-api-korea 레포지토리 설계 참고)에서 검증된 출력 파일(`data/raw/final/{city_en}.json`)의 `attractions` 배열 구조 및 API 명세를 기준으로 정의한다.
각 레코드는 TourAPI 리스트 필드, `_assigned_theme`(테마 분류), `detail.common`(공통 상세), `detail.intro`(유형별 소개 상세)로 구성된다.

### 공통 필드 (리스트 + detail.common)

| 필드 | TourAPI 원본 필드 | 실제 수집 및 명세 확인 상태 | 설명 |
| --- | --- | --- | --- |
| `contentid` | `contentid` | ✅ 실제 수집 확인 | TourAPI 콘텐츠 ID. 내부 `attraction_id` 생성에 사용 |
| `contenttypeid` | `contenttypeid` | ✅ 실제 수집 확인 | 콘텐츠 유형 코드 (12·14·15·28·32·38·39) |
| `title` | `title` | ✅ 실제 수집 확인 | 관광지명 (한국어) |
| `addr1` | `addr1` | ✅ 실제 수집 확인 | 주소 1 |
| `addr2` | `addr2` | ✅ 실제 수집 확인 | 주소 2 (건물명, 층수 등). 빈 문자열 가능 |
| `mapx` | `mapx` | ✅ 실제 수집 확인 | 경도 (문자열 형식) |
| `mapy` | `mapy` | ✅ 실제 수집 확인 | 위도 (문자열 형식) |
| `tel` | `tel` | ❌ 100% 결측 확인 | 연락 전화번호. 실제 수집 시에는 `detail.intro` 아래의 `infocenter` 계열 연락처를 탐색하는 폴백(Fallback) 수집 로직 적용 필요 |
| `firstimage` | `firstimage` | 일부 실제 수집 확인 | 대표 이미지 URL. 없으면 빈 문자열 |
| `firstimage2` | `firstimage2` | 일부 실제 수집 확인 | 대표 이미지 썸네일 URL. 없으면 빈 문자열 |
| `cpyrhtDivCd` | `cpyrhtDivCd` | 일부 실제 수집 확인 | 공공누리 저작권 유형 (Type1·Type3 등). 없으면 빈 문자열 |
| `areacode` | `areacode` | 일부 실제 수집 확인 | TourAPI 지역 코드. 일부 레코드에서 빈 문자열 |
| `sigungucode` | `sigungucode` | 일부 실제 수집 확인 | TourAPI 시군구 코드. 일부 레코드에서 빈 문자열 |
| `lDongRegnCd` | `lDongRegnCd` | ✅ 실제 수집 확인 | 법정동 지역 코드 |
| `lDongSignguCd` | `lDongSignguCd` | ✅ 실제 수집 확인 | 법정동 시군구 코드 |
| `lclsSystm1` | `lclsSystm1` | ✅ 실제 수집 확인 | TourAPI 대분류 코드. 테마 매핑의 주 분류 기준으로 활용 |
| `lclsSystm2` | `lclsSystm2` | ✅ 실제 수집 확인 | TourAPI 중분류 코드. 테마 매핑의 주 분류 기준으로 활용 |
| `lclsSystm3` | `lclsSystm3` | ✅ 실제 수집 확인 | TourAPI 소분류 코드. 테마 매핑의 주 분류 기준으로 활용 |
| `cat1` | `detail.common.cat1` | ⚠️ 제공률 낮음 (결측 35%) | TourAPI cat1 대분류. 높은 결측률로 인해 테마 매핑에서 제외하며 보조 참조용으로만 유지 |
| `cat2` | `detail.common.cat2` | ⚠️ 제공률 낮음 (결측 35%) | TourAPI cat2 중분류 |
| `cat3` | `detail.common.cat3` | ⚠️ 제공률 낮음 (결측 35%) | TourAPI cat3 소분류 |
| `overview` | `detail.common.overview` | ✅ 실제 수집 확인 | 관광지 설명 (한국어 전문) |
| `homepage` | `detail.common.homepage` | 일부 실제 수집 확인 | 공식 홈페이지 URL (HTML 앵커 태그 포함 가능). 없으면 빈 문자열 |
| `_assigned_theme` | 내부 생성 | ✅ 실제 수집 확인 | 분류 코드 매핑으로 할당한 6대 테마 값 |

### 소개 상세 필드 (detail.intro) — 콘텐츠 유형별 주요 필드

`detail.intro`의 필드명은 `contenttypeid`에 따라 달라진다.

**관광지 (12)**

| 필드 | TourAPI 원본 필드 | 실제 수집 및 명세 확인 상태 | 설명 |
| --- | --- | --- | --- |
| 운영시간 | `usetime` | ⚠️ API 명세상 제공률 낮음 확인 | 운영시간 문자열 |
| 휴무일 | `restdate` | 일부 실제 수집 확인 | 휴무일 |
| 입장료 | `usefee` | ⚠️ API 명세상 제공률 낮음 확인 | 입장료 문자열 |
| 주차 | `parking` | 일부 실제 수집 확인 | 주차 가능 여부 |
| 문의 | `infocenter` | 일부 실제 수집 확인 | 문의처 |

**문화시설 (14)**

| 필드 | TourAPI 원본 필드 | 실제 수집 및 명세 확인 상태 | 설명 |
| --- | --- | --- | --- |
| 운영시간 | `usetimeculture` | 일부 실제 수집 확인 | 관람 및 이용시간 문자열 |
| 휴무일 | `restdateculture` | 일부 실제 수집 확인 | 휴관일 문자열 |
| 입장료 | `usefee` | 일부 실제 수집 확인 | 관람 요금 및 이용 요금 |
| 주차 | `parkingculture` | 일부 실제 수집 확인 | 주차 가능 여부 |
| 주차요금 | `parkingfee` | 일부 실제 수집 확인 | 주차 요금 문자열 |
| 소요시간 | `spendtime` | 일부 실제 수집 확인 | 관람 소요 시간 |
| 문의 | `infocenterculture` | 일부 실제 수집 확인 | 문의처 전화번호 |

**음식점 (39)**

| 필드 | TourAPI 원본 필드 | 실제 수집 및 명세 확인 상태 | 설명 |
| --- | --- | --- | --- |
| 대표 메뉴 | `treatmenu` | ✅ 대부분 실제 수집 확인 | 대표 메뉴명. `description`에 `[대표 메뉴]` 접두어로 추가 |
| 첫 번째 메뉴 | `firstmenu` | 일부 실제 수집 확인 | 주력 단품 메뉴명 |
| 운영시간 | `opentimefood` | ✅ 대부분 실제 수집 확인 | 영업시간 문자열 (HTML 태그 포함 가능) |
| 휴무일 | `restdatefood` | ✅ 대부분 실제 수집 확인 | 휴무일 문자열 |
| 포장 | `packing` | 일부 실제 수집 확인 | 포장 가능 여부 |
| 예약 | `reservationfood` | 일부 실제 수집 확인 | 예약 방법 |
| 주차 | `parkingfood` | 일부 실제 수집 확인 | 주차 가능 여부 |
| 문의 | `infocenterfood` | 일부 실제 수집 확인 | 문의처 전화번호 |

> **photo_url**: `firstimage`·`firstimage2` 필드로 URL을 취득할 수 있으나, 이미지가 없는 레코드는 빈 문자열이다. `cpyrhtDivCd`로 저작권 유형(Type1·Type3 등)을 함께 저장한다.

## 2.4 Festival 데이터

Festival은 도시와 1:N 관계를 가지며, 월별 추천과 계절성 추천의 주요 근거로 사용한다.

아래 필드는 실제 수집 과정(tour-api-korea 레포지토리 설계 참고)에서 검증된 출력 파일(`data/raw/final/{city_en}.json`)의 `festivals` 배열 구조 및 API 명세를 기준으로 정의한다.
축제 레코드는 `contenttypeid == "15"`이며, 리스트 필드·`_assigned_theme`·`detail.common`·`detail.intro`로 구성된다.

### 공통 필드 (리스트 + detail.common)

| 필드 | TourAPI 원본 필드 | 실제 수집 및 명세 확인 상태 | 설명 |
| --- | --- | --- | --- |
| `contentid` | `contentid` | ✅ 실제 수집 확인 | TourAPI 콘텐츠 ID. 내부 `festival_id` 생성에 사용 |
| `contenttypeid` | `contenttypeid` | ✅ 실제 수집 확인 | 항상 `"15"` (축제행사) |
| `title` | `title` | ✅ 실제 수집 확인 | 축제명 (한국어) |
| `addr1` | `addr1` | ✅ 실제 수집 확인 | 개최 장소 주소 1 |
| `addr2` | `addr2` | ✅ 실제 수집 확인 | 주소 2. 빈 문자열 가능 |
| `mapx` | `mapx` | ✅ 실제 수집 확인 | 경도 (문자열 형식) |
| `mapy` | `mapy` | ✅ 실제 수집 확인 | 위도 (문자열 형식) |
| `tel` | `tel` | ❌ 100% 결측 확인 | 연락 전화번호. 실제 수집 시에는 `detail.intro` 아래의 `infocenter` 및 `sponsor1tel` 등을 우선 폴백 매핑 필요 |
| `eventstartdate` | `eventstartdate` | ✅ 실제 수집 확인 | 축제 시작일 (YYYYMMDD 형식) |
| `eventenddate` | `eventenddate` | ✅ 실제 수집 확인 | 축제 종료일 (YYYYMMDD 형식) |
| `firstimage` | `firstimage` | 일부 실제 수집 확인 | 대표 이미지 URL. 없으면 빈 문자열 |
| `firstimage2` | `firstimage2` | 일부 실제 수집 확인 | 대표 이미지 썸네일 URL |
| `cpyrhtDivCd` | `cpyrhtDivCd` | 일부 실제 수집 확인 | 공공누리 저작권 유형 |
| `lDongRegnCd` | `lDongRegnCd` | ✅ 실제 수집 확인 | 법정동 지역 코드 |
| `lDongSignguCd` | `lDongSignguCd` | ✅ 실제 수집 확인 | 법정동 시군구 코드 |
| `lclsSystm1` | `lclsSystm1` | ✅ 실제 수집 확인 | TourAPI 대분류 코드 (`"EV"` 고정) |
| `lclsSystm2` | `lclsSystm2` | ✅ 실제 수집 확인 | TourAPI 중분류 코드 |
| `lclsSystm3` | `lclsSystm3` | ✅ 실제 수집 확인 | TourAPI 소분류 코드 |
| `progresstype` | `progresstype` | 일부 실제 수집 확인 | 행사 진행 유형 (예: `"전국"`, `"지역"`) |
| `overview` | `detail.common.overview` | ✅ 실제 수집 확인 | 축제 설명 (한국어 전문) |
| `homepage` | `detail.common.homepage` | 일부 실제 수집 확인 | 공식 홈페이지 URL. 없으면 빈 문자열 |
| `_assigned_theme` | 내부 생성 | ✅ 실제 수집 확인 | 6대 테마 값. 수동 오버라이드 46건 적용 |

### 소개 상세 필드 (detail.intro) — 축제 유형 (contenttypeid: 15)

| 필드 | TourAPI 원본 필드 | 실제 수집 및 명세 확인 상태 | 설명 |
| --- | --- | --- | --- |
| 입장료 | `usetimefestival` | ⚠️ API 명세상 제공률 낮음 확인 | 이용 요금 및 시간 문자열 |
| 공연 시간 | `playtime` | 일부 실제 수집 확인 | 공연·행사 운영 시간 |
| 행사 장소명 | `eventplace` | 일부 실제 수집 확인 | 개최 장소 명칭 |
| 주관 기관 | `sponsor1` | 일부 실제 수집 확인 | 주최·주관 기관명 |
| 주관 기관 연락처 | `sponsor1tel` | 일부 실제 수집 확인 | 주관 기관 전화번호 |
| 프로그램 | `program` | 일부 실제 수집 확인 | 세부 프로그램 설명 |
| 할인 정보 | `discountinfofestival` | ⚠️ API 명세상 제공률 낮음 확인 | 할인 조건 |

## 2.5 방문객 통계 데이터 (신규 - 독립 엔티티 분리)

> [신규] TourAPI DataLab Service(관광 빅데이터 API)를 활용한 월별 도시별 방문객 통계가 파이프라인에 추가되었다.
> 고유 방문자 수의 특성상 일별 단순 합산 시 중복 집계 문제가 발생하므로, **1달 단위 구간 쿼리**로 취득하고 해당 월의 일수로 나눈 **월별 일평균**을 최종 지표로 사용한다.
> [코드정정] 실제 엔드포인트는 `DataLabService/locgoRegnVisitrDDList`(지역 방문자 일별)이다. `touDivCd` 코드 매핑은 **1=현지인(locals), 2=외지인(out_of_town), 3=외국인(foreigners)**이다.
> [코드정정] 수집 단계(`scrape_and_aggregate_visitor.py`)에서는 통계를 **도시별 final 파일(`data/raw/final/{city_en}.json`)의 `visitor_statistics` 필드에 임베드**하며, 전역 요약을 `data/visitor/monthly_visitor_averages.json`에 저장한다. **독립 엔티티(`VisitorStatistics`)·독립 파일로의 분리는 전처리(ELT) 단계의 변환 목표**이며, 취득 단계 산출은 임베드 구조다.

`visitor_statistics.monthly_statistics[]`의 실제 필드(코드 기준):

| 필드 | 산출 방식 | 상태 | 설명 |
| --- | --- | --- | --- |
| `month` | 조회 기간 | ✅ 코드 확인 | 월 문자열 (예: `"2025-01"`) |
| `days` | 월 일수 | ✅ 코드 확인 | 28~31 |
| `locals_total` / `locals_daily_avg` | 합산 / 일수 | ✅ 코드 확인 | 현지인 총합·일평균 |
| `out_of_town_total` / `out_of_town_daily_avg` | 합산 / 일수 | ✅ 코드 확인 | 외지인 총합·일평균 |
| `foreigners_total` / `foreigners_daily_avg` | 합산 / 일수 | ✅ 코드 확인 | 외국인 총합·일평균 |
| `total_visitors` / `total_daily_avg` | 세 구분 합 / 일수 | ✅ 코드 확인 | 전체 방문·일평균 |

> 전처리 표준명 매핑(예정): `locals_daily_avg→local_daily_avg`, `out_of_town_daily_avg→outsider_daily_avg`, `foreigners_daily_avg→foreigner_daily_avg`. 통계 출처명은 `DataLabService`.

---

# 3. 데이터 소스 전략

## 3.1 한국관광공사 TourAPI 4.0 (KorService2)

> [변경] TourAPI 버전이 **4.0(KorService2)**으로 확정되었다. 실제 구현 과정에서 확인된 동작 특성을 추가한다.

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 관광지 목록, 축제 목록, 공통 상세정보, 소개 상세정보 |
| 취득 대상 | 관광지명, 주소, 위도, 경도, 설명(overview), 운영시간, 입장료, 축제명, 축제 기간 |
| 장점 | 전국 관광정보를 API로 제공하며 지역기반·행사정보 등을 함께 조회할 수 있다. |
| 한계 | 운영시간·입장료는 콘텐츠 유형별 필드가 다르고 실제 제공률이 낮다. `detailCommon2` 호출 시 `overviewYN` 등 추가 파라미터를 전달하면 `INVALID_REQUEST_PARAMETER_ERROR`(코드 10)가 발생한다. |
| 적용 방식 | Attraction과 Festival 자동 수집의 1차 소스로 사용한다. |
| API 인증 | 디코딩된 키(Decoded Key)만 사용 가능하다. `requests` 라이브러리가 파라미터를 자동 URL 인코딩하므로 인코딩된 키 사용 시 이중 인코딩으로 인증 오류가 발생한다. |
| 키 관리 | 여러 키를 Pool로 관리하며, 쿼터 초과(`resultCode == "0022"`) 시에만 자동 로테이션한다. 인증·파라미터 오류에서는 즉시 중단(Fail-Fast)한다. |

## 3.2 한국관광공사 관광 빅데이터 API (DataLabService)

> [신규] 이동통신 데이터 기반 방문객 통계 API가 파이프라인에 추가되었다.

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 지역별 관광객 방문 통계 |
| 엔드포인트 | `DataLabService/locgoRegnVisitrDDList` (지역 방문자 일별) |
| 취득 대상 | 현지인(touDivCd=1)·외지인(=2)·외국인(=3) 방문객 일별 수치 (1달 단위 구간 집계) |
| 장점 | 이동통신 기반 고유 방문자 수 데이터로 추천 지표 보강에 활용할 수 있다. |
| 한계 | 일별 데이터를 직접 합산하면 기간 내 재방문자가 중복 집계된다. **반드시 1달 단위 구간으로 쿼리해야 한다.** |
| 적용 방식 | 도시별 월별 일평균 방문객 통계를 산출하여 `data/raw/final/{city_en}.json`의 `visitor_statistics`에 임베드하고, 전역 요약을 `data/visitor/monthly_visitor_averages.json`에 저장한다. |

## 3.3 대한민국구석구석 및 지자체 문화관광 홈페이지

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 도시 관광 링크, 공식 설명, 최신 운영정보 확인 |
| 취득 대상 | 지자체 문화관광 홈페이지 URL, 최신 운영정보 |
| 장점 | 공식 또는 준공식 관광 안내 성격이 강해 서비스 설명과 출처 표기에 적합하다. |
| 한계 | 페이지 구조가 지자체마다 다르고, 운영시간·요금 표기 방식이 일정하지 않다. |
| 적용 방식 | TourAPI 수집값의 공식 확인 및 최신성 검증 소스로 사용한다. City의 `site_urls`로 저장한다. |

## 3.4 Wikipedia / Wikidata

> [변경] City 데이터의 **주요 취득 후보 소스**로 검토 중이다. v0.1에서 보조 소스로 기재된 것을 변경하여 검토 대상을 넓힌다.

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 도시 정보, 위치 정보, 역사·문화 개요 |
| 취득 대상 | 도시명, 위치, 설명, 대표 좌표, 기후 표, 외부 링크 |
| 장점 | 도시 단위 설명과 위치 정보가 체계적이며 전국 커버가 가능하다. 한국어 위키백과와 Wikidata를 함께 사용하면 좌표·다국어 도시명을 안정적으로 취득할 수 있다. |
| 한계 | 관광지·축제 상세 정보는 불완전할 수 있고, 설명문 사용 시 라이선스 표기가 필요하다. 기후 표 자동 취득 성공률이 낮아 수작업 보완이 필요한 도시가 많다. |
| 적용 방식 | City 자동 수집의 후보 소스 중 하나로 검토한다. Attraction·Festival에는 사용하지 않는다. |

## 3.5 기상청 API허브 및 기후통계

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 기후 데이터, 월별 여행 적합도 보강 |
| 취득 대상 | 월별 평균 기온, 강수량, 폭염·한파·강설 등 계절성 메모 |
| 장점 | 공식 기상기후 데이터로 월별 추천 근거를 만들 수 있다. |
| 한계 | 시·군·구와 관측 지점 매핑 기준을 별도로 정의해야 한다. Wikipedia 기후 표 자동 취득이 실패한 도시의 보완 소스로 사용한다. |
| 적용 방식 | City의 `climate_table` 보완 및 계절 추천 지표 산출에 사용한다. 정합성은 `03_data_collect_plan.md` 4.1절의 정량 지표(`MAE_T`, `MAPE_P`, `ConsistencyScore`)로 판정하고, 월별 추천 근거는 `ComfortScore_m` 산식으로 산출한다(세부: `weather_consistency_quant_review.md`). |

## 3.6 관광 통계 및 보조 공공데이터

| 출처 | 사용 목적 | 적용 방식 |
| --- | --- | --- |
| 한국관광 데이터랩 (DataLabService) | 지역별 관광 동향, 방문자 통계 | 도시별 월별 일평균 방문객 통계 산출 |
| 행정안전부 행정구역 데이터 | 시·군·구 코드와 행정구역 정규화 | City ID와 TourAPI 지역 코드 매핑 |
| 공공데이터포털 지자체 관광 데이터 | 지자체별 관광 링크·관광 자원 보강 | 공식 링크와 누락 데이터 보강 |
| 지자체 공식 문화관광 사이트 | 운영시간, 입장료, 최신 축제 일정 확인 | 누락·최신성 확인 |

---

# 4. 전체 취득 범위

## 4.1 전체 수집 대상 및 현황

> [변경] 각 항목별 **현재 수집 상태**를 추가한다 (강원·경북 기준).

| 구분 | 수집 항목 | 주요 출처 | 실제 수집 및 명세 확인 상태 |
| --- | --- | --- | --- |
| 도시 | 도시명, 위치, 위도, 경도(설명·기후·사이트는 미보강 placeholder) | Excel 좌표/centroid (Wikipedia 보강 예정) | ✅ 40개 도시 정규화 완료 (`data/city/{city_en}.json`) |
| 관광지 | 관광지명, 주소, 위도, 경도, 설명, 운영시간*, 입장료*, 테마 | TourAPI 4.0 KorService2 | ✅ 3,709건 실제 수집 및 명세 확인 완료 |
| 축제 | 축제명, 주소, 기간, 설명, 테마 | TourAPI 4.0 KorService2 | ✅ 106건 실제 수집 및 명세 확인 완료 (테마 수동 재분류 46건 포함) |
| 통계 | 현지인·외지인·외국인 일평균 방문객 (월별) | DataLab Service | ✅ 2025년 12개월 실제 수집 및 명세 확인 완료 |

*운영시간·입장료는 TourAPI 실제 제공률이 낮아 상당수가 `missing` 상태임.

## 4.2 취득 상태 관리

| 취득 상태 | 기준 | 처리 방식 |
| --- | --- | --- |
| `collected` | 자동 수집 값이 있고 출처가 명확함 | DB 적재 |
| `needs_review` | 값은 있으나 표현이 모호하거나 최신성 확인이 필요함 | 수동 검수 |
| `missing` | 자동 수집에서 값을 찾지 못함 | Web Search 또는 수동 입력 대상 |
| `blocked` | 약관·저작권·접근 제한으로 수집 불가 | 딥링크 또는 빈 값으로 대체하고 사유 기록 |

## 4.3 공식 확인 우선순위

| 항목 | 확인 우선순위 | 사유 |
| --- | --- | --- |
| 운영시간 | 높음 | 사용자 질문 빈도가 높고 일정 구성에 직접 영향을 준다. |
| 운영기간 | 높음 | 계절 운영, 휴관일, 임시 중단 등 예외가 많다. |
| 입장료 | 중간 | 무료·유료·계절 요금·패키지 요금이 혼재한다. |
| 사진 | 중간 | 공공누리 유형과 외부 이미지 사용 조건 확인이 필요하다. |
| 위도·경도 | 높음 | 지도 표시와 동선 계산에 필요하다. |

공식 사이트 또는 수동 검수로 확인한 값에는 `verified_at`, `verified_source_url`, `verification_note`를 함께 기록한다.

---

# 5. 수집 전략

## 5.1 자동 수집 전략

| 대상 | 자동 수집 소스 | 처리 방식 |
| --- | --- | --- |
| 도시 | Wikipedia, Wikidata | 도시명, 위치, 설명, 기후, 사이트 링크, 위도, 경도를 추출하고 City 레코드로 정규화한다. |
| 관광지 | TourAPI 4.0 KorService2 | `/areaBasedList2` → 테마 분류 → `/detailCommon2` + `/detailIntro2` 순서로 수집한다. 체크포인트 파일로 재시작을 지원한다. |
| 축제 | TourAPI 4.0 KorService2 | `/searchFestival2`로 리스트 수집 후 `/detailCommon2` + `/detailIntro2`로 상세 수집한다. |
| 통계 | DataLab Service (`/locgoRegnVisitrDDList`) | 1달 단위 구간 쿼리로 월별 데이터를 수집하고 일수로 나눈 일평균을 저장한다. |

## 5.2 TourAPI 수집 파이프라인 상세

> [신규] 실제 수집 및 TourAPI 명세 분석을 통해 확인된 수집 파이프라인의 단계별 구조를 정의한다.

| 순서 | 단계 | 처리 내용 |
| --- | --- | --- |
| 1 | City 목록 확정 | 강원·경북 40개 City 목록과 내부 `city_id` 기준을 확정한다. |
| 2 | TourAPI 리스트 수집 | 관광지·축제 후보를 TourAPI 목록 API로 수집한다. |
| 3 | 테마 자동 분류 | TourAPI 분류 코드와 내부 매핑으로 6대 테마를 자동 분류한다. |
| 4 | 공통 상세 수집 | `detailCommon2`로 설명, 위치, 이미지 등 공통 상세 정보를 수집한다. |
| 5 | 유형별 상세 수집 | `detailIntro2`로 관광지·축제 유형별 상세 필드를 보강한다. |
| 6 | 취득 상태 할당 | 필드별 수집 결과에 따라 `field_status`를 할당한다. |
| 7 | 로컬 산출물 생성 | `data/raw/final/{city_en}.json`(+통계 임베드) 및 정규화본 `data/city/{city_en}.json`을 생성한다. |
| 8 | S3 적재 대상 확정 | 검증된 산출물을 S3 Raw Prefix 적재 대상으로 확정한다. |

## 5.3 공식 확인 및 검수 전략

공식 확인과 검수는 자동 수집에서 실패했거나 검수 필요 상태로 분류된 항목에 적용한다. 이 과정은 별도 단계가 아니라 같은 취득 파이프라인의 후속 처리로 본다.

| 확인 항목 | 입력 기준 |
| --- | --- |
| 운영시간 | 공식 사이트에 명시된 최신 운영시간만 입력 |
| 운영기간 | 계절 운영 또는 축제 기간이 명확한 경우 입력 |
| 입장료 | 공식 사이트 또는 공공 관광 페이지에 있는 금액만 입력 |
| 사진 | 공공누리 유형 또는 사용 가능 조건이 명확한 이미지 사용 |

## 5.4 데이터 정규화 규칙

> [변경] Lovv_scraping 포맷 확정에 따라 정규화 규칙을 갱신한다.

- **식별자 형식 (코드정정)**:
  - `city_id`: `KR-{GW|GB}-{CITY_EN}` (예: `KR-GW-GANGNEUNG`)
  - `attraction_id`: `ATT-{contentId}` (City 접두 없음. 서비스 PK는 `city_id`+`attraction_id`로 구성)
  - `festival_id`: `FEST-{contentId}` (약어는 `FEST`)
  - 모든 관광지와 축제는 별도 `city_id` 필드로 유효한 도시에 매핑된다. (예: 포항시 남구·북구는 `KR-GB-POHANG`으로 통합)
- **6대 테마 자동 분류 (코드정정)**:
  - 기존의 `cat1/cat2/cat3` 필드는 약 35%의 결측률을 보여 테마 분류 기준으로 부적합하다(필터 후 삭제됨).
  - 테마 조회 키는 **`lclsSystm3`(소분류) 우선, 없으면 `cat3` 폴백**이며, 매핑 사전은 `data/theme_mapping.json`·`data/festival_mapping.json`이다.
  - 추가로 `lclsSystm1 == "C01"` 항목은 무조건 제외하며, `should_exclude` 규칙(체험관광 대분류, 기타문화관광지·레저스포츠시설·교육시설·공연시설·복합관광시설 중분류, 특정 명칭)으로 비대상 항목을 배제한다.
- **전화번호 폴백 (Phone Fallback) — 향후 과제**:
  - 공통 `tel`은 100% 결측이며, 현재 정규화 코드(`normalize_details.py`)는 **연락처(tel)를 출력하지 않는다**(infocenter 폴백 미구현).
  - `detail.intro`의 `infocenter`/`infocenterculture`/`infocenterfood`/`sponsor1tel` 폴백은 **전처리(ELT) 단계에서 보강**하는 것으로 한다.
- **100% 결측 속성의 정제**:
  - 음식점의 `scalefood` 및 축제의 `bookingplace`, `discountinfofestival`, `eventhomepage`, `festivalgrade`, `sponsor2tel`, `subevent` 등 실제 제공률이 0%인 100% 결측 필드들은 저장 구조 및 수집 대상에서 완전히 생략하거나 Optional로 관리하여 스키마 정합성을 확보한다.
- **Boolean 결측 왜곡 예방**:
  - 유모차 대여, 신용카드 사용, 반려동물 동반 등 결측률이 매우 높은 Boolean 대상 필드들은 정보 누락(결측) 시 일괄 `false`로 변환하지 않는다. 데이터 누락 상태는 `null` 또는 필드 생략(undefined)으로 보존하며, 로우 데이터상에 명확한 거부 표현('N', '불가', '없음')이 기재된 경우에만 `false`로 정규화한다.
- **기타 음식점 및 축제 처리**:
  - 음식점(`contentTypeId == "39"`)의 `treatmenu`는 `[대표 메뉴]` 접두어로 `description`에 추가한다. `admission_fee`는 빈 문자열로 처리한다.
  - 축제 기간은 `start_date`(YYYYMMDD)·`end_date`(YYYYMMDD)로 분리 저장하고, `month`는 `start_date[4:6]`로 파생한다.
- **기타 수집 제약**:
  - 운영시간과 입장료는 최신성이 낮을 수 있으므로 `data_confidence`를 `medium` 또는 `low`로 기록한다.
  - 외부 설명문은 원문 복제가 아니라 내부 요약문으로 재작성하거나 TourAPI `overview` 값을 그대로 저장한다.
  - `detailCommon2` 호출 시 `contentId`만 파라미터로 전달한다. 추가 파라미터 전달 시 `INVALID_REQUEST_PARAMETER_ERROR`(코드 10)가 발생한다.

---

# 6. 단일 취득 파이프라인

## 6.1 처리 흐름

| 순서 | 단계 | 처리 내용 |
| --- | --- | --- |
| 1 | 자동 수집 | TourAPI, DataLab, Wikipedia/Wikidata에서 원천 데이터를 취득한다. |
| 2 | 캐시·체크포인트 저장 | 중단 후 재시작할 수 있도록 파일 기반 캐시와 체크포인트를 남긴다. |
| 3 | 취득 상태 할당 | 필드별 취득 결과에 따라 `field_status`를 할당한다. |
| 4 | 로컬 산출물 생성 | `data/raw/final/{city_en}.json` 및 정규화본 `data/city/{city_en}.json`을 생성한다. |
| 5 | JSON 직렬화 | 수집 데이터와 메타데이터를 재사용 가능한 JSON 원본으로 직렬화한다. |
| 6 | S3 Raw Prefix 확정 | 국가, 출처, 엔티티 유형, 수집일 기준의 Raw Prefix를 확정한다. |
| 7 | S3 Raw Bucket 적재 | 검증된 JSON 산출물을 S3 Raw Bucket 적재 대상으로 확정한다. |

정의된 모든 필드가 출력에 들어가도록 시도하는 것이 목표다.
6.1의 처리 흐름은 ETL 라인 이전의 데이터 취득 범위만 다루며, S3 Raw Bucket 적재에서 종료한다.
S3 적재 이후의 전처리, 정규화 DB 적재, 운영 중 보완 처리는 본 절의 범위에서 제외한다.
운영시간·입장료도 최초 수집 대상에 포함하며, 자동 수집 실패 시 `missing` 또는 `needs_review` 상태로 JSON에 남긴다.

예시:

```text
사용자 질문: 순천만국가정원 운영시간 알려줘

1. DB에서 순천만국가정원 Attraction 조회
2. opening_hours가 없거나 오래된 값이면 Web Search Worker 실행
3. 공식 사이트 또는 공식 관광 페이지 확인
4. 운영시간과 확인 출처를 함께 반환
```

## 6.2 API Key Rotation 전략

> [신규] 실제 수집 파이프라인 및 API 명세 분석에서 확인된 키 관리 정책이다.

| 상황 | 처리 방식 |
| --- | --- |
| 쿼터 초과 (`resultCode == "0022"` 또는 LIMIT/EXCEEDED 메시지) | 다음 키로 자동 로테이션 |
| 인증 오류 (`resultCode == "20"`, `"30"` 등) | 즉시 `TourAPIError` 발생 및 중단 (Fail-Fast) |
| 잘못된 파라미터 오류 (`resultCode == "10"`) | 즉시 `TourAPIError` 발생 및 중단 (Fail-Fast) |
| 모든 키 소진 | 체크포인트 파일 저장 후 graceful stop |

## 6.3 Web Search Worker 적용 조건

| 조건 | 처리 |
| --- | --- |
| DB에 정보 없음 | 공식 사이트 검색 |
| 운영시간·입장료 값이 오래됨 | 공식 사이트 재확인 |
| 축제 기간이 연도별로 바뀜 | 해당 연도 공식 페이지 확인 |
| 공식 출처가 아닌 블로그·SNS만 존재 | 답변 근거로 사용하지 않거나 낮은 신뢰도로 표시 |

---

# 7. 저장 구조

## 7.1 핵심 파일

> [코드정정] 실제 코드(`tour-api-korea`)의 저장 구조로 정정한다. `data/KR/*.json` 분리 구조는 코드에 없으며, 단계별 산출 경로는 다음과 같다.

```text
data/
├── ldong_sigungu.json            # 수집 대상 행정 표준 코드(입력)
├── theme_mapping.json            # 관광지 테마 매핑(입력)
├── festival_mapping.json         # 축제 테마 매핑(입력)
├── classification_dict.json      # 분류 코드 사전(입력)
├── download_progress.json        # 상세 수집 체크포인트
├── raw/
│   ├── list/{regn}_{sig}_raw.json, _filtered.json   # 리스트 수집/필터
│   ├── list_by_city/{city_en}.json                  # 40개 도시 그룹화
│   ├── detail/{contentid}.json                       # {common, intro}
│   └── final/{city_en}.json                          # 리스트+detail (+visitor_statistics 임베드)
├── city/{city_en}.json           # 정규화 산출물(city/attractions/festivals/metadata)
└── visitor/monthly_visitor_averages.json             # 방문통계 전역 요약
```

> 데이터 정본은 S3이며, 위 산출물(대용량·캐시·원본)은 `.gitignore`로 Git에서 제외되고 로컬/S3에 둔다. 수량: 관광지 3,709 · 축제 106 · 상세 3,815(3,709+106) · 통계 40도시×12개월.

## 7.2 City 예시

코드(`normalize_details.py`)가 산출하는 `data/city/{city_en}.json`의 `city` 블록:

```json
{
  "city_id": "KR-GW-GANGNEUNG",
  "city_name_ko": "강릉시",
  "city_name_en": "Gangneung",
  "province": "강원특별자치도",
  "district_type": "시",
  "location": "강원특별자치도 강릉시",
  "latitude": 37.75,
  "longitude": 128.9,
  "description": "강릉시 관광 정보",
  "climate": "기상청 API 연계 예정",
  "site_url": ""
}
```

> `description`·`climate`·`site_url`은 현재 플레이스홀더이며, Wikipedia 설명·기상청 기후·지자체 URL 보강은 향후 과제다. 좌표는 Excel/centroid 산출이다.

## 7.3 Attraction 예시

코드가 산출하는 정규화 Attraction 레코드:

```json
{
  "attraction_id": "ATT-126508",
  "city_id": "KR-GW-GANGNEUNG",
  "content_id": "126508",
  "content_type_id": "12",
  "theme": "바다·해안",
  "name": "경포해변",
  "address": "강원특별자치도 강릉시 창해로 514",
  "description": "강릉의 대표 해변으로 길이 약 6km의 백사장이 펼쳐진다.",
  "site_url": "",
  "opening_hours": "",
  "opening_period": "",
  "latitude": 37.7970,
  "longitude": 128.9017,
  "admission_fee": "",
  "photo_url": "http://tong.visitkorea.or.kr/cms/resource/.../126508.jpg",
  "areacode": "",
  "sigungucode": "",
  "source_name": "TourAPI",
  "source_url": "http://apis.data.go.kr/B551011/KorService2/detailCommon2?contentId=126508",
  "collected_at": "2025-06-05 00:00:00",
  "data_confidence": "collected",
  "verified_at": null,
  "verified_source_url": null,
  "verification_note": null
}
```

> `data_confidence`는 코드상 `opening_hours` 또는 `usefee`가 있으면 `"needs_review"`, 없으면 `"collected"`다. tel은 출력되지 않으며(전처리 보강 대상), 음식점(39)은 `description`에 `[대표 메뉴]`가 추가된다.

## 7.4 Festival 예시

코드가 산출하는 정규화 Festival 레코드:

```json
{
  "festival_id": "FEST-2762975",
  "city_id": "KR-GW-GANGNEUNG",
  "content_id": "2762975",
  "theme": "역사·전통",
  "name": "강릉단오제",
  "address": "강원특별자치도 강릉시 남대천 일원",
  "description": "유네스코 인류무형문화유산으로 등재된 강릉단오제는 매년 음력 5월에 열린다.",
  "site_url": "",
  "photo_url": "",
  "period_text": "행사 기간 중 상시 진행",
  "start_date": "20250525",
  "end_date": "20250601",
  "month": "05",
  "latitude": 37.7512,
  "longitude": 128.8761,
  "areacode": "",
  "sigungucode": "",
  "source_name": "TourAPI",
  "source_url": "http://apis.data.go.kr/B551011/KorService2/detailCommon2?contentId=2762975",
  "collected_at": "2025-06-05 00:00:00",
  "verified_at": null,
  "verified_source_url": null,
  "verification_note": null
}
```

> `start_date`/`end_date`는 `detail.intro.eventstartdate/eventenddate`(YYYYMMDD), `month`는 `start_date[4:6]`, `period_text`는 `detail.intro.playtime`에서 온다.

## 7.5 방문객 통계 예시

코드가 산출하는 `visitor_statistics`(final 파일 임베드)의 월별 항목:

```json
{
  "month": "2025-01",
  "days": 31,
  "locals_total": 382540.0,
  "locals_daily_avg": 12340.0,
  "out_of_town_total": 1416018.0,
  "out_of_town_daily_avg": 45678.0,
  "foreigners_total": 3813.0,
  "foreigners_daily_avg": 123.0,
  "total_visitors": 1802371.0,
  "total_daily_avg": 58141.0
}
```

> 전처리 단계에서 이 월별 항목 12건을 도시별 독립 `VisitorStatistics` 아이템으로 분리(unnest)하고, 표준명(`local_daily_avg`/`outsider_daily_avg`/`foreigner_daily_avg`)으로 매핑한다.

---

# 8. 6대 테마 분류

> [신규] 관광지와 축제를 아래 6대 핵심 테마로 분류한다.
> 실제 수집 데이터 분석 결과, TourAPI의 `cat1/cat2/cat3` 필드는 결측률이 약 35%에 달해 분류 기준으로 부적합한 것으로 확인되었습니다.
> 따라서 테마 자동 분류는 **`lclsSystm3`(소분류) 코드를 우선 조회 키로, 없으면 `cat3`로 폴백**하여 `data/theme_mapping.json`·`data/festival_mapping.json` 사전과 매핑합니다(코드 기준). 추가로 `lclsSystm1 == "C01"` 항목은 무조건 제외하며, 축제의 경우 수동 오버라이드를 적용합니다.
> **[필터링 규칙] 수집 파이프라인(`scripts/scrape_list.py`)은 6대 테마 중 하나로 정상 매핑되는 항목만 최종 필터링하여 수집합니다. 6대 테마에 분류되지 않는 카테고리('테마 없음' 및 '제외' 대상 코드)의 관광지 및 축제는 수집 단계에서 원천적으로 필터링(Drop)되어 최종 JSON 데이터셋에서 배제됩니다.**

| 테마 | 설명 | 강원+경북 관광지 수 | 강원+경북 축제 수 |
| --- | --- | --- | --- |
| `온천·휴양` | 온천, 스파, 리조트, 힐링 | 120 | 0 |
| `바다·해안` | 바다, 해안, 해수욕장, 해양 활동 | 249 | 0 |
| `역사·전통` | 역사, 문화유산, 전통 문화 | 1,001 | 10 |
| `미식·노포` | 맛집, 전통 음식점, 식당 | 2,480 | 22 |
| `자연·트레킹` | 자연, 등산, 트레킹, 국립공원 | 687 | 13 |
| `예술·감성` | 예술, 디자인, 감성, 문화, 행사 | 374 | 61 |
| **합계** | | **4,911** | **106** |

### 8.1 테마별 세부 소분류(`lclsSystm`) 매핑 규격 (명시적 제외 조건 반영)

자동 매핑 프로그램(`scripts/build_mapping_dict.py`)의 제외 규칙(`should_exclude`)이 적용된 최종 매핑 규격입니다.

| 6대 테마 | 분류 범위 (중분류 / 소분류) | 핵심 매핑 대상 소분류 코드 예시 |
| :--- | :--- | :--- |
| **온천·휴양** | • **개별 소분류** (자연공원) | `NA040600` (자연휴양림)<br>*(※ `EX05` 웰니스관광 전체는 대분류 '체험관광'으로 제외, `NA010500` 약수터는 명칭 제외)* |
| **바다·해안** | • **자연경관(하천/해양)** (`NA02` 일부 소분류)<br>• **개별 소분류** (랜드마크) | `NA020700` (항구/포구), `NA020800` (해안절경), `NA020900` (해변/해수욕장), `VE010800` (등대)<br>*(※ `EX070100` 유람선관광은 대분류 '체험관광'으로 제외)* |
| **역사·전통** | • **역사관광** (`HS` 대분류 일부)<br>• **개별 소분류** (전시시설) | `HS010100` (고궁), `HS010200` (성곽), `HS010400` (고택), `HS010600` (민속마을), `HS030100` (불교성지/사찰), `VE070100` (박물관)<br>*(※ `EX` 전통/사찰체험은 대분류 '체험관광'으로 제외, `북한관광지`, `기타안보관광지`, `기타 종교성지`는 명칭 제외)* |
| **미식·노포** | • **관광식당** (`FD010100` 소분류 한정) | `FD010100` (관광식당)<br>*(※ 모범음식점, 카페/찻집, 제과/분식 등 일반 간이음식 및 주점 계열 소분류 전체 제외)* |
| **자연·트레킹** | • **자연관광** (`NA` 대분류 대부분)<br>• **개별 소분류** (도시공원/문화관광) | `NA010100` (산/고개), `NA010200` (숲), `NA010400` (계곡), `NA020100` (강), `NA020200` (호수), `NA030100` (동굴), `NA040100` (국립공원), `NA040700` (수목원/정원), `VE030100` (시민공원), `VE040300` (둘레길)<br>*(※ `NA010500` 약수터는 명칭 제외)* |
| **예술·감성** | • **문화시설/랜드마크** (`VE` 중분류 일부) | `VE01` 랜드마크관광 일부(건물/타워/전망대/다리/대교/분수 등), `VE020500` (천문대), `VE070600` (미술관/화랑)<br>*(※ `EX02` 공예체험은 대분류 '체험관광'으로 제외, 중분류가 '공연시설', '교육시설', '복합관광시설', '기타문화관광지'인 소분류 전체 제외)* |

#### ⚠️ 스크립트 기반 명시적 제외 규칙 (`should_exclude`)
데이터 품질 및 여행 추천 서비스의 고유 정체성 유지를 위해 스크립트 상에서 필터링하는 조건입니다.
1. **대분류 제외**: `체험관광` 대분류 전체 제외 (예: 공예체험, 웰니스스파, 사찰/전통문화체험 일체 배제)
2. **중분류 제외**: `기타문화관광지` (서점 등), `레저스포츠시설` (스포츠경기장 등), `교육시설` (도서관, 학교 등), `공연시설` (공연장, 영화관 등), `복합관광시설` (관광단지, 리조트 등) 전체 제외
3. **소분류 명칭 제외**: `기타주점`, `클럽`, `기타간이음식`, `북한관광지`, `기타안보관광지`, `기타 종교성지`, `약수터` 강제 제외
4. **미식·노포 테마 제한**: 음식점(`FD` 대분류)은 오직 `FD010100` (관광식당) 코드만 수집하고, 그 외 모범음식점, 카페, 간이음식, 일반 주점 등은 전부 배제

> **축제 테마 수동 재분류 (코드정정)**: 축제 46건을 수동 검토 후 구체 테마로 재분류하였다. 오버라이드 목록은 `filter_existing_lists.py`의 `fest_overrides` 딕셔너리(`contentid → 테마`, 46건)에 코드 내 하드코딩되어 있다(외부 파일 `crawling/KR/targets/...` 아님). 외부 설정 파일화는 향후 과제다.

---

# 9. 품질 검증 기준

> [변경] 실제 수집 데이터 및 API 명세 분석을 통해 도출된 검증 항목을 추가한다.

| 검증 항목 | 기준 |
| --- | --- |
| City 매핑 | 모든 Attraction과 Festival은 `data/city/{city_en}.json`의 City와 동일한 유효 `city_id`를 가져야 한다. |
| ID 유일성 | `attraction_id`, `festival_id`, `city_id`는 각 파일 내에서 유일해야 한다. |
| 출처 기록 | 모든 자동 수집 데이터는 `source_name`, `source_url`, `collected_at`을 가진다. |
| 전체 필드 상태 | 정의된 모든 필드는 `collected`, `needs_review`, `missing`, `blocked` 중 하나의 상태를 가진다. |
| 최신성 | 운영시간, 운영기간, 입장료는 확인일을 기록한다. |
| 저작권 | 사진과 설명문은 사용 가능 조건을 확인한다. 설명문은 내부 요약문으로 저장한다. |
| 수량 정합성 | 관광지 3,709건, 축제 106건, 도시 40개, 방문객 통계 480건(40×12)이 확인되어야 한다. |
| 포항 통합 | 포항시 남구·북구 레코드가 `KR-GB-POHANG`으로 통합되어 있어야 한다. |
| 행정구역 정합성 | TourAPI 지역 코드와 내부 City ID가 같은 시·군·구를 가리키는지 검증한다. |

---

# 10. 법적·운영 제약

- TourAPI와 공공데이터포털 데이터는 공공누리 유형, API 이용 조건, 출처 표기 조건을 확인한다.
- TourAPI 일일 쿼터 제한을 준수한다. 쿼터 초과 시 자동 키 로테이션을 사용하며, 키 소진 시 graceful stop 후 체크포인트에서 재시작한다.
- Wikipedia 기반 설명은 라이선스 조건에 따라 출처와 원문 링크를 기록한다.
- 지자체 관광 페이지는 이용약관과 크롤링 허용 범위를 확인한다.
- 사진은 저작권 위험이 크므로 자동 수집 값이 있더라도 공공누리 유형을 확인하고, 불명확하면 `needs_review` 또는 `blocked`로 관리한다.
- 운영시간과 입장료는 변경 가능성이 높으므로 "확인일 기준" 문구를 서비스에 표시한다.
- API 키는 `.env` / `.env.local`로 관리하며 Git에 절대 커밋하지 않는다.

---

# 11. 본 문서 반영 계획

이 초안이 확정되면 한국 데이터 취득 계획의 운영 기준을 대표 문서와 공유 산출물에 맞춘다.
반영 방향은 특정 파일을 단순히 갱신하는 것이 아니라, 수집 기준·전처리 입력·검증 산출물·공유 문서가 같은 데이터 계약을 따르도록 정렬하는 데 둔다.

1. 수집 데이터 정보와 분량은 한국 City, Attraction, Festival, 방문객 통계 관계를 기준으로 정리한다.
2. 한국 데이터 출처는 TourAPI 4.0, DataLabService, Wikipedia/Wikidata의 역할이 명확히 구분되도록 구성한다.
3. 데이터 취득 흐름은 S3 Raw Bucket 적재 이전까지의 수집 라인과 이후 전처리 라인이 혼동되지 않도록 구분한다.
4. 품질 관리는 City 매핑, TourAPI 코드 매핑, 출처 기록, 최신성 검증, 수량 검증을 기준으로 운영한다.
5. 법적 검토는 TourAPI·공공누리·지자체 사이트 이용 조건과 API 키 보안 관리가 함께 확인되도록 정리한다.
6. 공유용 HTML과 PDF는 확정된 문서 기준을 사용자가 읽기 쉬운 형태로 제공하도록 재생성하고 검수한다.

---

# 12. 참고 출처

- 한국관광공사 TourAPI 4.0(KorService2): https://www.data.go.kr/data/15101578/openapi.do
- 한국관광공사 관광 빅데이터 API(DataLabService): https://www.data.go.kr/data/15010913/openapi.do
- 대한민국구석구석: https://korean.visitkorea.or.kr/
- 한국관광 데이터랩: https://datalab.visitkorea.or.kr/
- 기상청 API허브: https://apihub.kma.go.kr/
- 공공데이터포털: https://www.data.go.kr/
- Lovv_scraping KR Spec: `Lovv_scraping/docs/specs/kr_attraction_festival_acquisition_spec_ko.md`

---

# 13. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-02 | LLM 파트 | 한국 데이터 취득 계획서 초안 작성 |
| v0.2 | 2026-06-06 | LLM 파트 | 실제 수집 데이터 및 API 명세 분석 결과 반영: Attraction·Festival·방문객 통계 데이터 모델을 실제 수집 필드 기준으로 갱신, city_id 형식 확정, TourAPI 동작 특성, 5단계 파이프라인, 6대 테마 분류 현황 추가 |
| v0.3 | 2026-06-07 | LLM 파트 | 실데이터 결측률 분석 및 팀원 설계 피드백 반영: 6대 테마 분류 기준을 lclsSystm 코드로 정정하고 스크립트 내 명시적 제외 조건(should_exclude)과 미식·노포 테마의 관광식당(FD010100) 한정 제한 필터링 규격을 반영한 세부 소분류 매핑 규격표 추가, 6대 테마 비대상 카테고리의 수집 시점 원천 필터링(Drop) 배제 규칙 명시, tel 결측에 따른 intro infocenter 계열 폴백 수집 정의, scalefood/bookingplace 등 100% 결측 필드 제외/Optional화, Boolean 결측치 왜곡 예방 정책 반영, 방문객 통계(VisitorStatistics)를 독립 엔티티 및 파일로 분리 |
| v0.3 (코드대조) | 2026-06-09 | 조동휘 | `Gloveman/tour-api-korea` 소스 코드 11종 직접 대조로 최신화: City ID `KR-{GW\|GB}-*`, Attraction/Festival ID `ATT-`/`FEST-{contentid}` 정정, 방문통계 엔드포인트 `locgoRegnVisitrDDList`·`touDivCd`(1/2/3)·final 임베드 구조·필드명(`locals_*`/`out_of_town_*`/`foreigners_*`) 정정, 실제 데이터 파일 구조(`data/raw/*`,`data/city/*`,`data/visitor/*`)로 교체, 테마 조회 키 `lclsSystm3 or cat3`·`C01` 제외 명시, 축제 오버라이드 46건의 실제 위치(`filter_existing_lists.py` 하드코딩) 정정, tel 폴백·`prefecture_id`·City 설명/기후/좌표를 코드 미구현(향후 과제)으로 표현 완화, 예시 JSON을 코드 산출물 기준으로 교체. HTML/PDF 재생성 보류. 상세 불일치는 `korea_acquisition_plan_corrections.md` 참조 |
