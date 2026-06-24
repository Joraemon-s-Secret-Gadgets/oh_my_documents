# 4. 전처리 파이프라인

## 4.1 처리 흐름

```text
S3 Raw 데이터 적재
↓
Raw 보관 기간 / 배치 기준 확인
↓
Lambda 배치 실행
↓
스키마 검증
↓
필드 정제
↓
엔티티 정규화
↓
중복 제거 및 병합
↓
품질 점수 산정
↓
파생 필드 생성
↓
검수 대상 분류
↓
DynamoDB 적재
```

## 4.2 단계별 처리 기준

| 단계 | 처리 내용 | 산출물 |
| --- | --- | --- |
| S3 Raw 데이터 적재 | API 응답, HTML 추출값, 수동 입력값을 JSON 문서로 저장 | S3 Raw Object |
| Raw 보관 기간 / 배치 기준 확인 | 일정 기간 또는 처리 기준만큼 누적된 Raw Prefix를 전처리 대상으로 확정 | Batch Manifest |
| Lambda 배치 실행 | 확정된 S3 Prefix 또는 Manifest를 입력으로 전처리 함수 실행 | Lambda Invocation |
| 스키마 검증 | 필수 필드 존재 여부, 타입, 인코딩, 날짜 포맷 점검 | schema_validation_result |
| 필드 정제 | 공백, HTML 태그, 제어문자, 중복 문장, 깨진 URL 제거 | cleaned_fields |
| 엔티티 정규화 | 도시·관광지·축제명, 방문·관광 통계, 행정구역, 좌표, 날짜를 공통 포맷으로 변환 | normalized_entities |
| 중복 제거 및 병합 | 동일 대상의 다중 출처 데이터를 하나의 대표 엔티티로 병합 | merged_entities |
| 품질 점수 산정 | 출처 신뢰도, 최신성, 필드 충족률, 검수 여부를 점수화 | data_confidence |
| 파생 필드 생성 | 테마 태그, 월별 추천 태그, 검색 인덱스 텍스트 생성 | feature_dataset |
| 검수 대상 분류 | 누락·충돌·저작권 위험 항목을 검수 큐로 이동 | review_queue |
| DynamoDB 적재 | City, Attraction, Festival, VisitorStatistics, 품질 메타데이터를 Item 단위로 저장 | DynamoDB Item |
