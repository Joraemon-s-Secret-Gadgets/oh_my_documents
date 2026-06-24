# 5. API 연동 요구사항

각 플랫폼 API는 역할을 분담하여 정보를 보완 제공한다.
클라이언트 측 직접 호출이 불가한 REST API는 딥링크로 대체하며, 향후 백엔드 프록시를 통해 연동한다.

🌐

Google Maps Platform

장소 상세 · 사진 · 주변 명소 (전 지역)

**역할:** 플랫폼 공통 지도 + Places API로 실시간 장소 정보

**상태:** ✓ 클라이언트 직접 연동

🟡

Kakao Maps

카카오 지도 · 주변 맛집·숙박 (국내 전용)

**역할:** 카카오 지도 SDK + Local REST API (맛집 검색)

**상태:** △ SDK + REST Key 선택

🔴

Yahoo Japan

일본 여행 · 숙박 · 맛집 (일본 전용)

**역할:** Yahoo Travel · じゃらん · 食べログ 딥링크

**상태:** 딥링크 / REST 백엔드 예정

☀

WeatherAPI

실시간 날씨 (전 지역 · API Key 필요)

**역할:** 목적지 상세 화면의 기온, 날씨 상태, 풍속, 습도 자동 제공

**상태:** △ API Key 설정 필요

## 5.1 Google Maps Platform

| 항목 | 내용 |
| --- | --- |
| 역할 | 장소 상세 정보, 지도 표시, 주변 명소 검색 (전 지역 공통) |
| 사용 API | Maps JavaScript API, Places API — Text Search / Find Place / Get Details / Nearby Search |
| 연동 방식 | JavaScript SDK — 클라이언트 직접 호출 가능 |
| 필수 키 | Google Cloud API Key (Maps JS API + Places API 활성화 필요) |
| 제공 데이터 | 평점, 리뷰 수, 사진(최대 4장), 운영시간, 현재 영업 여부, 공식 사이트, 주변 명소(반경 3km) |
| 적용 국가 | 국내 소도시 + 일본 소도시 (공통 적용) |
| CORS 제약 | 없음 — SDK 방식으로 브라우저에서 직접 사용 가능 |

## 5.2 Kakao Maps

| 항목 | 내용 |
| --- | --- |
| 역할 | 국내 소도시 카카오 지도 표시, 주변 맛집·카페·숙박 검색 |
| 사용 API | Kakao Maps JavaScript SDK (지도), Kakao Local REST API (주변 검색) |
| 연동 방식 | JavaScript SDK (지도): 클라이언트 직접 / Local REST: REST Key 필요 |
| 필수 키 | Kakao JavaScript App Key (지도 필수), Kakao REST API Key (로컬 검색, 선택) |
| 제공 데이터 | 카카오 지도, 주변 맛집/카페/숙박 검색 결과, 장소 URL |
| 적용 국가 | 국내 소도시 전용 |
| CORS 제약 | Maps SDK: 없음 / Local REST: 등록 도메인 한정 (로컬 파일 환경 제약) → 오류 시 딥링크 대체 |

## 5.3 Yahoo Japan

**⚠ Yahoo Japan Maps JS SDK 지원 중단:**

Yahoo Japan Maps JavaScript SDK(Yjans)가 서비스 종료되어 일본 소도시 지도는 Google Maps API로 대체 제공한다.

Yahoo Japan REST API는 CORS 제한으로 클라이언트 직접 호출이 불가하며, 딥링크 방식으로 제공한다.

| 항목 | 내용 |
| --- | --- |
| 역할 | 일본 소도시 여행 정보, 숙박·음식점 플랫폼 딥링크 제공 |
| 사용 API | Yahoo Japan Local Search REST API (향후), じゃらん/食べログ/楽天トラベル 딥링크 (현재) |
| 연동 방식 | 현재: 딥링크 URL 제공 / 향후: 백엔드 프록시를 통한 REST API 연동 |
| 필수 키 | Yahoo Japan App ID (향후 적용 예정, 현재 입력 항목만 준비) |
| 제공 데이터 | Yahoo Japan Maps 링크, Yahoo Travel 링크, じゃらん, 食べログ, 楽天トラベル 링크 |
| 추가 딥링크 | 一休, Booking.com, Agoda, Google Hotels, Retty, Hot Pepper, Instagram 해시태그 검색 링크 |
| 적용 국가 | 일본 소도시 전용 |
| 지도 대체 | Yahoo Japan Maps JS SDK 지원 중단 → Google Maps 대체 제공 |

## 5.4 WeatherAPI (날씨)

| 항목 | 내용 |
| --- | --- |
| 역할 | 전 목적지 실시간 날씨 정보 제공 (목적지 상세 화면 표시용, API Key 필요). 추천 후보 스코어링에는 월별 기상 경향 데이터를 사용한다. |
| 사용 API | WeatherAPI Current Weather API 및 Forecast API |
| 연동 방식 | REST API — API Key 기반 호출, 운영 환경에서는 백엔드 프록시 권장 |
| 필수 키 | WeatherAPI API Key |
| 제공 데이터 | 현재 기온(℃), 날씨 상태, 풍속(km/h), 습도(%), 강수 확률, 예보 데이터, 데이터 기준 시각 |
| 적용 국가 | 국내 + 일본 소도시 공통 적용 |
| 제약사항 | 요금제, 호출량 제한, API Key 노출 방지 정책 확인 필요. 갱신 실패 시 마지막 기준 시각 또는 날씨 정보 미제공 상태를 안내해야 함 |

## 5.5 API 연동 현황 요약

| 플랫폼 | 역할 특화 | 지도 SDK | REST API | 현재 상태 |
| --- | --- | --- | --- | --- |
| **Google Maps** | 장소 상세·사진·주변 명소 | ✓ 지원 | ✓ 지원 | 클라이언트 직접 연동 |
| **Kakao Maps** | 맛집·카페·숙박 검색 | ✓ 지원 | △ 조건부 | SDK + REST Key 선택 |
| **Yahoo Japan** | 일본 여행·숙박·맛집 | ✗ SDK 중단 | ✗ CORS | 딥링크 제공 |
| **WeatherAPI** | 목적지 상세 현재 날씨 표시 | — | △ Key 필요 | API Key 설정 필요 |
