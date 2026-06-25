# 5. API 연동 요구사항

각 플랫폼 API는 역할을 분담하여 지도, 장소, 마커 간 이동 동선, 외부 탐색 링크를 보완 제공한다.
월별 날씨 경향은 API 호출 대상이 아니라 Wikipedia에서 추출·전처리한 추천용 정적 데이터로 관리한다.
클라이언트 측 직접 호출이 불가한 REST API는 딥링크 또는 백엔드 프록시로 대체한다.

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

🟢

OpenRouteService

마커 간 이동 경로 · 시간 · 거리 계산

**역할:** Directions API로 일정 마커 간 경로 폴리라인을 계산하고, Matrix API로 후보 장소 간 이동 시간·거리 비교를 보조

**상태:** △ 백엔드 프록시 또는 서버 환경 변수 기반 연동

🔴

Yahoo Japan

일본 여행 · 숙박 · 맛집 (일본 전용)

**역할:** Yahoo Travel · じゃらん · 食べログ 딥링크

**상태:** P5 재검토 보류

## 5.1 Google Maps Platform

| 항목 | 내용 |
| --- | --- |
| 역할 | 장소 상세 정보, 지도 표시, 주변 명소 검색 (전 지역 공통) |
| 사용 API | Maps JavaScript API, Places API — Text Search / Find Place / Get Details / Nearby Search |
| 연동 방식 | JavaScript SDK — 클라이언트 직접 호출 가능 |
| 필수 키 | Google Cloud API Key (Maps JS API + Places API 활성화 필요) |
| 제공 데이터 | 리뷰 수, 사진(최대 4장), 운영시간, 현재 영업 여부, 공식 사이트, 주변 명소(반경 3km) |
| 적용 국가 | 국내 소도시 우선. 일본 소도시는 P5 재검토 |
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

## 5.3 OpenRouteService

| 항목 | 내용 |
| --- | --- |
| 역할 | 일정 마커 간 이동 경로 표시, 후보 장소 간 이동 시간·거리 비교 |
| 사용 API | Directions API, Matrix API |
| 연동 방식 | 백엔드 프록시 또는 서버 환경 변수 기반 호출. 응답의 geometry/polyline과 duration/distance를 프론트 지도 레이어에 전달 |
| 필수 키 | OpenRouteService API Key |
| 제공 데이터 | 경로 geometry, 총 거리, 예상 이동 시간, 후보 지점 간 시간·거리 행렬 |
| 적용 국가 | PoC/P1은 한국 강원·경북 일정 동선 표시 기준. 일본 트랙은 P5 재검토 |
| 제약사항 | 호출량 제한, 지점 수 제한, 네트워크 실패를 고려해 후보 수 제한, 캐시, 직선 연결 또는 목록 중심 폴백 UI를 적용한다. 지도 렌더링 자체는 Google Maps 또는 Kakao Maps가 담당한다. |

## 5.4 Yahoo Japan (P5 재검토)

**⚠ Yahoo Japan Maps JS SDK 지원 중단:**

Yahoo Japan Maps JavaScript SDK(Yjans)가 서비스 종료되어 일본 소도시 지도는 Google Maps API로 대체 제공한다.

Yahoo Japan REST API는 CORS 제한으로 클라이언트 직접 호출이 불가하며, 일본 데이터 수집 경로 복구 전까지 PoC/P1 기능 요구사항에서 제외한다.

| 항목 | 내용 |
| --- | --- |
| 역할 | 일본 소도시 여행 정보, 숙박·음식점 플랫폼 딥링크 제공 |
| 사용 API | Yahoo Japan Local Search REST API (향후), じゃらん/食べログ/楽天トラベル 딥링크 (현재) |
| 연동 방식 | P5 재검토: 딥링크 URL 제공 또는 백엔드 프록시를 통한 REST API 연동 |
| 필수 키 | Yahoo Japan App ID (향후 적용 예정, 현재 입력 항목만 준비) |
| 제공 데이터 | Yahoo Japan Maps 링크, Yahoo Travel 링크, じゃらん, 食べログ, 楽天トラベル 링크 |
| 추가 딥링크 | 一休, Booking.com, Agoda, Google Hotels, Retty, Hot Pepper, Instagram 해시태그 검색 링크 |
| 적용 국가 | 일본 소도시 전용(P5 재검토) |
| 지도 대체 | Yahoo Japan Maps JS SDK 지원 중단 → Google Maps 대체 제공 |

## 5.5 API 연동 현황 요약

| 플랫폼 | 역할 특화 | 지도 SDK | REST API | 현재 상태 |
| --- | --- | --- | --- | --- |
| **Google Maps** | 장소 상세·사진·주변 명소 | ✓ 지원 | ✓ 지원 | 클라이언트 직접 연동 |
| **Kakao Maps** | 맛집·카페·숙박 검색 | ✓ 지원 | △ 조건부 | SDK + REST Key 선택 |
| **OpenRouteService** | 마커 간 경로·시간·거리 | — | △ Key 필요 | 백엔드 프록시 권장 |
| **Yahoo Japan** | 일본 여행·숙박·맛집 | ✗ SDK 중단 | ✗ CORS | P5 재검토 |
