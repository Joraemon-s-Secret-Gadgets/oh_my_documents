# K-DRAMA 촬영지 데이터 파이프라인

공식 관광데이터 + 촬영지 큐레이션 + 자체 검증 조합의
현실적 데이터 파이프라인 설계 가이드

8+

Data Sources

26만

Tour API 건수

5

Pipeline Steps

## 데이터 소스

## 쓸만한 출처

K-drama 촬영지만 깔끔하게 API로 제공되는 단일 DB는 부족해서, 공식 관광 데이터 + 촬영지 큐레이션 데이터 + 자체 검증 조합이 현실적입니다.

| 용도 | 데이터 소스 | 우선순위 |
| --- | --- | --- |
| 국내 관광지 기본 정보 | [한국관광공사 TourAPI](https://www.data.go.kr/data/15101578/openapi.do) | 최우선 |
| 공식 드라마 촬영지 콘텐츠 | [VisitKorea Filming Locations](https://english.visitkorea.or.kr) | 높음 |
| 도시별 드라마 촬영지 코스 | VisitKorea K-drama course examples | 높음 |
| 서울권 촬영지 | Visit Seoul K-drama locations | 중간 |
| 지역/지자체 촬영지 | 각 시·도 관광공사, 시청/군청 관광 페이지 | 중간 |
| 영화/촬영지 데이터 참고 | 한국영상자료원 촬영지 데이터 | 중간 |
| 좌표/지도 보강 | OpenStreetMap / Wikidata | 중간 |
| 커뮤니티 보강 | K-drama Locations 팬 DB — 라이선스 확인 필요 | 참고용 |

가장 우선순위 높은 건 한국관광공사 TourAPI — 국내 관광정보 약 26만 건 제공. 지역기반 / 위치기반 / 키워드검색 / 공통정보 / 이미지정보 쿼리 지원.
추천 데이터 파이프라인

## 사용자 쿼리 →
데이터 수집 파이프라인

VisitKorea seed 수집부터 신뢰도 등급 부여까지 5단계 플로우입니다.
Seed Collection

드라마 촬영지 seed 수집

VisitKorea / 지자체 페이지에서 드라마 촬영지 seed 수집. 수원 K-drama 코스, 제주 "King the Land" 촬영지 등 RAG 문서로 활용하기 좋은 콘텐츠.
API Enrichment

TourAPI로 기본 정보 보강

관광지 기본 정보, 주소, 이미지, 좌표. 드라마·촬영지·작품명 키워드로 검색해서 seed를 보강합니다.

# TourAPI 키워드 검색 예시

keyword

:

"드라마 촬영지"

|

"작품명"

contentTypeId

:
(관광지)

areaCode

:

지역코드

→ 좌표·이미지 반환
Geo Enrichment

OSM / Wikidata로 좌표·분류 보강

좌표 누락 항목 보완. 행정구역·분류 태그 정규화. OpenStreetMap + Wikidata 조합으로 커버.
Tagging

작품명·관계 타입 자체 태깅

작품명, 장소명, 관계 타입을 자체 태깅. drama_id ↔ place_id 매핑 + relation_type 분류.

relation_type

:

official_filming_location

← 제작사 공식

tourism_board_recommended

← 관광공사

fan_pilgrimage

← 팬 커뮤니티

atmosphere_match

← 분위기 유사
Quality Scoring

신뢰도 등급 부여

공식 관광공사 출처 → HIGH / 지자체 추천 → MID / 팬 커뮤니티 → LOW. confidence_level로 RAG 검색 시 필터링 활용.

confidence_level

:

HIGH

— 공식 발표, 제작사 확인

MID

— 관광공사·지자체 추천

LOW

— 팬 커뮤니티, 블로그
데이터 모델

## 데이터 스키마

Drama · Place · DramaPlaceRelation 3개 엔티티로 구성. 관계 타입과 신뢰도 등급이 핵심 필드입니다.

Drama

ENTITY

FIELD_01

title

작품 제목. 검색 및 매핑의 기준 키.

str

FIELD_02

original_title

한국어 원제. 공식 표기 기준.

str

FIELD_03

year / genre

방영 연도 및 장르 분류.

int

str

Place

ENTITY

FIELD_01

name

실제 방문 가능한 구체적 장소명.

str

FIELD_02

country / region / city

도도부현 + 시정촌 형태. 지역 여행 동선 구성에 필수.

서울

제주

부산

FIELD_03

lat / lng

지도 표시 및 위치기반 검색 핵심 좌표.

float

DramaPlaceRelation

RELATION

FIELD_01

drama_id / place_id

Drama ↔ Place 연결 FK.

fk

FIELD_02

relation_type

스팟과 작품의 연결 근거. 신뢰도에 직결되는 핵심 필드.

공식 배경지

팬 성지

분위기 유사

FIELD_03

confidence_level

HIGH / MID / LOW 3단계. 공식 발표=HIGH, 팬 커뮤니티=LOW.

HIGH

MID

LOW

FIELD_04

scene_description

어느 장면에서 등장하는지 설명.

str

FIELD_05

evidence_url

공식 관광청·제작사·지자체 등 1차 출처 URL.

url

FIELD_06

source_url

팬사이트는 신뢰도 낮음 표기.

url
촬영지 스팟 예시

## 핵심 촬영지 스팟

작품별 대표 성지를 신뢰도와 관계 유형으로 구조화했습니다.

킹더랜드

HIGH

제주 성산일출봉 일대

📍 제주특별자치도 서귀포시

킹더랜드 주요 촬영지. 성산일출봉 주변 해안 산책로 및 카페 거리 다수 등장.

자연경관

해안

공식 배경지

✓ 연중 방문 가능

참고 →

이상한 변호사 우영우

HIGH

소덕동 팽나무 마을

📍 경상남도 창원시

드라마 핵심 배경. 실제 팽나무와 마을 전경이 그대로 보존되어 있어 성지 방문객 급증.

마을

자연

공식 배경지

✓ 연중 방문 가능

참고 →

오징어 게임

MID

인천 을왕리 해수욕장

📍 인천광역시 중구

시즌 1 초반 배경 촬영지. 드라마 흥행 후 한국 관광명소로 부상. 방문객 안내 시설 운영 중.

해변

관광공사 추천

✓ 연중 방문 가능

참고 →
라이선스 주의사항

## MVP 전략 &
라이선스 가이드

**⚠ 팬 사이트·블로그 데이터 직접 DB화 금지**

팬 사이트·블로그 데이터를 그대로 긁어와 DB화하면 라이선스 문제가 생길 수 있습니다. MVP는

**공식 관광공사·지자체·공공데이터 중심**

으로 가고, 팬 데이터는

**링크·참고 수준**

또는

**직접 작성 요약**

으로 다루는 게 안전합니다.

✓ 안전

공공데이터 활용

한국관광공사 TourAPI, VisitKorea, 지자체 공식 관광 페이지. 공공누리 라이선스 확인 후 사용.

△ 주의

팬 데이터 참고

K-drama Locations 등 팬 DB는 링크·참고 수준으로만 활용. 직접 DB화 금지. 반드시 라이선스 확인.

✗ 금지

무단 스크래핑

블로그·SNS·팬사이트 콘텐츠 무단 수집 및 DB화. 저작권법 위반 가능. 요약 직접 작성으로 대체.
