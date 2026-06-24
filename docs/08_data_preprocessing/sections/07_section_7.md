# 7. 품질 검증 및 검수 큐

## 7.1 자동 검증 기준

| 검증 항목 | 기준 | 실패 시 상태 |
| --- | --- | --- |
| 필수 필드 | ID, 이름, City 매핑, 출처 URL 존재 | `missing` 또는 `needs_review` |
| City 매핑 | Attraction/Festival/VisitorStatistics가 하나의 City와 연결됨 | `needs_review` |
| 통계 기간 | 방문·관광 통계의 집계 기간과 지표명이 존재함 | `needs_review` |
| URL 유효성 | HTTP 접근 가능 또는 공식 딥링크 보존 가능 | `needs_review` |
| 좌표 범위 | 국가별 좌표 범위 안에 존재 | `needs_review` |
| 날짜 포맷 | ISO 날짜 또는 반복 규칙으로 변환 가능 | `needs_review` |
| 저작권 | 사진·설명 사용 조건 확인 가능 | `blocked` 또는 `needs_review` |
| 최신성 | 운영시간·입장료·축제 기간 확인일 존재 | `needs_review` |

## 7.2 검수 큐 분류

| 큐 | 대상 | 처리자 |
| --- | --- | --- |
| `location_review` | City 매핑 충돌, 좌표 이상치, 주소 누락 | 데이터 담당자 |
| `date_review` | 축제 기간 불명확, 연도별 일정 미확인 | 데이터 담당자 |
| `license_review` | 사진·설명문 사용 조건 불명확 | 기획/운영 담당자 |
| `content_review` | 설명 품질 낮음, 관광지 성격 모호 | 기획/운영 담당자 |
| `source_review` | 공식 출처 부재, 비공식 출처만 존재 | 데이터 담당자 |

## 7.3 신뢰도 점수

`data_confidence`는 다음 요소를 기준으로 산정한다.

| 요소 | 가중 기준 |
| --- | --- |
| 출처 공식성 | 공식 API·공식 관광 사이트·지자체 사이트를 높게 평가 |
| 최신성 | `verified_at`이 최근일수록 높게 평가 |
| 필드 충족률 | 필수 필드와 추천 핵심 필드가 채워질수록 높게 평가 |
| 출처 일치도 | 다중 출처 값이 일치할수록 높게 평가 |
| 수동 검수 | 검수 완료 항목을 높게 평가 |
