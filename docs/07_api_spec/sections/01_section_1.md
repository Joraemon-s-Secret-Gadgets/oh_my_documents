# 1. 문서 개요

## 1.1 목적

본 문서는 로브 서비스의 프론트엔드, 백엔드, 추천 Agent, 운영 화면이 사용하는 API 계약을 정의한다.
엔드포인트는 Production 기준의 목표 계약이며, PoC에서는 일부를 정적 데이터 또는 로컬 스토리지로 대체할 수 있다.

## 1.2 공통 규칙

| 항목 | 규칙 |
| --- | --- |
| Base URL | `/api/v1` |
| Content-Type | `application/json; charset=utf-8` |
| 인증 | 공개 추천 조회는 선택, 운영·저장·마이페이지는 Cognito JWT 인증 필요 |
| 날짜 형식 | ISO 8601 |
| ID 형식 | UUID 권장 |
| 보안 스킴 | `cognitoBearerAuth` (`Authorization: Bearer <Cognito JWT>`) |

## 1.3 Lambda 라우팅 기준

AWS SAM 기반 배포에서는 API Gateway가 단일 `/api/v1` 진입점을 제공하고, Cognito JWT Authorizer로 인증·인가를 검증한 뒤 요청 성격에 따라 Lambda를 분리해 호출한다.

| 담당 Lambda | API 범위 | 책임 |
| --- | --- | --- |
| `Auth-Function` | `/auth/*`, 초기 `/auth/cognito/session` 세션 조회 | Cognito claims를 Lovv user/session shape로 변환하고, legacy social login API를 유지 |
| `Map-Function` | `/destinations/*` | 지도 마커 목록, 소도시 상세 콘텐츠, DB/S3 기반 읽기 API |
| `AgentCore-Function` | `/recommendations`, `/agent/answer` | LLM 호출, 추천 설명 생성, 대화 원문 저장 없는 순수 AI 추론 |

각 Lambda는 별도 IAM Role과 배포 패키지를 가진다. 인증·지도 API에는 AI SDK와 LangChain 계열 의존성을 포함하지 않고, AgentCore API는 사용자 대면 동기 응답 기준으로 29초 내외 완료를 목표로 한다. 응답 시간이 더 길어질 수 있는 요청은 비동기 작업 또는 스트리밍 API로 별도 설계한다.
