# 로브 (Lovv) 기술 명세서

> 문서 버전: v0.3
> 문서 상태: 검토 중 (Review)
> 기준 문서: 요구사항 명세서 v1.7, 서비스 흐름 명세서 v0.2, 데이터 수집 계획서 v0.6, 데이터베이스 설계 명세서 v0.2, Agent 명세서 v0.4, API 명세서 v0.2

# 1. 문서 개요

## 1.1 목적

본 문서는 로브 서비스의 시스템 구성, 프론트엔드·백엔드·데이터·AI/RAG·외부 연동 기술 방향을 정의한다.
구현 세부 코드는 포함하지 않고, PoC와 Production 단계에서 공통으로 지켜야 할 기술 경계와 책임을 명세한다.

## 1.2 설계 원칙

- Markdown 요구사항 명세서를 source of truth로 삼고 구현 문서는 이를 참조한다.
- 프론트엔드는 사용자 입력, 지도, 결과 화면, 로컬 저장을 담당한다.
- 백엔드는 인증, 데이터 검증, 외부 API 프록시, 추천 파이프라인 실행을 담당한다.
- 외부 API 응답은 신뢰하지 않고 경계에서 검증한다.
- 추천 로직은 실시간 예보가 아닌 월별 기상 경향 통계 데이터를 기반으로 Supervisor 노드가 폴백 상태를 판단한다.

# 2. 시스템 개요

| 계층 | 책임 |
| --- | --- |
| Client Web | 온보딩, 지도, 챗봇 UI, 추천 결과, 마이페이지, 로컬 스토리지 |
| Backend API | 인증·인가, 데이터 조회, 추천 요청, 저장/피드백, 운영 데이터 검토 |
| Recommendation Agent | 조건 분류, 후보 검색, 후보 선정, 일정 구성, 추천 이유 생성 |
| Data Store | 목적지, 축제, 월별 기상 경향, 사용자 저장 데이터, 운영 검토 이력 |
| External APIs | Google Maps, Kakao Maps, Yahoo Japan 딥링크, WeatherAPI 표시용 데이터 |

# 3. 배포 단계별 기술 범위

| 영역 | PoC | Production |
| --- | --- | --- |
| 프론트엔드 | 단일 웹 앱, 로컬 스토리지 저장 | 계정 기반 저장, 마이페이지 완성 |
| 백엔드 | 추천 API 및 외부 API 프록시 최소 구현 | 인증·인가, 운영/검토 API, 감사 이력 |
| 데이터 | 정적 JSON 또는 시드 데이터 | 관리형 DB와 데이터 갱신 파이프라인 |
| AI/RAG | 문서/정적 데이터 기반 검색 및 프롬프트 | 평가, 재시도, 정책 관리, 모니터링 |
| 외부 API | 지도/날씨 표시와 딥링크 | 키 보안, 호출량 제어, 캐시 |

# 4. 프론트엔드 명세

## 4.1 주요 화면

| 화면 | 책임 |
| --- | --- |
| 온보딩 | 대도시 스타일 선택, 기본 테마 매핑, 선호 저장 |
| 메인 지도 | 국가·월·테마 필터, 소도시 마커 표시, 마커 클릭 진입 |
| 챗봇 | 자연어 조건 입력, 추가 질문, 축제 포함 여부 확인 |
| 추천 결과 | 소도시 1곳 일정 카드, 추천 이유, 외부 링크, 피드백 |
| 마이페이지 | 저장 일정, 온보딩 선호, 피드백 이력 조회 |

## 4.2 클라이언트 상태

| 상태 | 저장 위치 | 설명 |
| --- | --- | --- |
| onboardingProfile | PoC 로컬 스토리지 | 기본 테마 선호 |
| selectedDestination | 메모리/URL 상태 | 지도 마커로 선택한 소도시 |
| recommendationSession | 메모리 | 국가, 월, 테마, 일정 유형, 축제 포함 여부 |
| savedItineraries | PoC 로컬 스토리지 | 저장된 추천 일정 |
| feedbackHistory | PoC 로컬 스토리지 | 좋아요/싫어요 기록 |

# 5. 백엔드 명세

## 5.1 모듈 구성

| 모듈 | 책임 |
| --- | --- |
| Auth Module | 로그인, 역할 기반 인가, 세션/토큰 관리 |
| User Preference Module | 온보딩 선호, 피드백, 저장 일정 관리 |
| Destination Module | 소도시, 테마, 계절, 혼잡도 데이터 조회 |
| Recommendation Module | LangGraph 기반 Agent 실행, Supervisor Router 상태 제어, 결정적 Skill 호출, 후보 선정, 일정·설명 생성, 검증 루프 제어 |
| External Proxy Module | WeatherAPI, Kakao Local 등 서버 경유 호출 |
| Admin Review Module | 데이터 제안, 승인, 반려, 이력 관리 |

## 5.2 공통 응답 원칙

모든 API 오류는 동일한 구조를 사용한다.

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "요청 값이 올바르지 않습니다.",
    "details": {}
  }
}
```

## 5.3 AWS SAM 기반 Lambda 분리 전략

Production 백엔드는 AWS SAM으로 API Gateway와 Lambda 리소스를 정의한다. API Gateway는 단일 `/api/v1` 진입점을 제공하고, 요청 성격에 따라 인증, 지도/콘텐츠 조회, AI 추론 Lambda로 라우팅한다.

SAM/CloudFormation 템플릿의 logical ID는 하이픈 없이 `AuthFunction`, `MapFunction`, `AgentCoreFunction`처럼 alphanumeric으로 작성한다. 실제 AWS Lambda 표시 이름이 필요하면 `FunctionName`에 `Auth-Function`, `Map-Function`, `AgentCore-Function` 같은 물리 이름을 별도로 지정한다.

| Lambda | 담당 역할 | 분리 이유 |
| --- | --- | --- |
| `Auth-Function` | Google, Kakao 간편 로그인 토큰 검증, JWT 발급·검증, 로그인 직후 사용자 정보·저장 테마·저장 일정 요약 조회 | 서비스 진입 시 가장 먼저 호출되고 호출 빈도가 높으므로, 무거운 AI 의존성과 분리해 빠른 응답과 안정적인 인증 경계를 유지한다. |
| `Map-Function` | 소도시 마커 좌표 목록 조회, 특정 소도시 상세 콘텐츠 조회, DB/S3 기반 읽기 API 처리 | 지도와 콘텐츠 조회는 읽기 중심의 가벼운 API다. AI 라이브러리와 분리하면 패키지 크기와 초기화 비용을 낮게 유지할 수 있다. |
| `AgentCore-Function` | LLM 호출, 자연어 질문 응답, 추천 설명 생성, 대화 원문 저장 없는 순수 추론 처리 | LangChain, OpenAI SDK, Boto3, Bedrock SDK 등 무거운 의존성이 포함될 수 있어 초기화 지연이 커질 수 있다. AI 추론만 독립 실행해 인증·지도 API의 응답 지연 전파를 막는다. |

Lambda 분리 기준은 기능 이름이 아니라 응답 특성, 의존성 무게, 권한 경계, 장애 영향 범위다. 인증 Lambda는 토큰과 사용자 세션 권한을 다루고, 지도 Lambda는 공개 또는 낮은 권한의 조회 데이터에 집중하며, AgentCore Lambda는 모델 호출과 추론 전용 권한만 가진다.

| 구분 | 기능 요구사항 | 담당 Lambda | 특이사항 / 운영 팁 |
| --- | --- | --- | --- |
| 인증 | Google, Kakao 간편 로그인 | `Auth-Function` | OAuth 공급자 토큰은 서버에서 검증하고 클라이언트에는 서비스 JWT 또는 세션 상태만 반환한다. |
| 세션 | 유저 저장 테마, 저장 일정 요약 로드 | `Auth-Function` | 로그인 성공 후 첫 대시보드 진입 시 한 번에 조회하되, 상세 일정 본문은 별도 저장 API에서 필요할 때 조회한다. |
| 지도 | 소도시 마커 표시 | `Map-Function` | 초기 지도 진입용 마커 리스트는 좌표, 도시명, 테마 태그처럼 가벼운 필드만 반환한다. |
| 콘텐츠 | 마커 클릭 시 여행 콘텐츠 로드 | `Map-Function` | `destinationId` 또는 DB의 `city_id`를 조건으로 상세 데이터를 조회한다. |
| AI | 모델 호출 및 답변 생성 | `AgentCore-Function` | 대화 원문은 저장하지 않는다. 동기 응답은 API Gateway 제한을 고려해 29초 내외 완료를 목표로 하고, 초과 가능성이 큰 작업은 비동기 작업 또는 스트리밍으로 분리한다. |

운영 제약은 다음 기준을 따른다.

| 항목 | 기준 |
| --- | --- |
| Lambda timeout | Lambda 자체 실행 시간은 최대 15분까지 설정할 수 있지만, 사용자 대면 동기 API는 짧은 응답 시간을 우선한다. |
| API Gateway integration timeout | SAM `Api` event의 `TimeoutInMillis` 기본값은 29,000ms다. LLM 응답이 이를 넘을 수 있으면 비동기 처리, 작업 상태 조회, 또는 응답 스트리밍 전환을 검토한다. |
| 패키지 크기 | 인증·지도 Lambda에는 AI SDK, LangChain, 벡터 검색 클라이언트 등 불필요한 의존성을 포함하지 않는다. |
| 권한 | Lambda별 IAM Role을 분리하고, `Auth-Function`은 인증/사용자 세션, `Map-Function`은 목적지 읽기, `AgentCore-Function`은 모델 호출과 필요한 검색 리소스에만 접근한다. |
| 저장 정책 | AgentCore는 대화 원문을 저장하지 않는다. 저장 일정은 사용자가 명시적으로 저장 API를 호출할 때만 계정 데이터로 남긴다. |

# 6. 데이터 처리 명세

## 6.1 추천용 데이터

| 데이터 | 처리 방식 |
| --- | --- |
| 통합 목적지 DB | 축제명, 장소 개요, 이미지, 위경도 좌표 등 무거운 마스터 정보를 저장하고 있는 DB로, 1차 조회 시 성능과 레이턴시 확보를 위해 사용 |
| S3 vector 기반 RAG Index | 장소·테마·자연어 조건의 임베딩 검색과 유사도 재랭킹에 사용. 정형 필터는 DB, 의미 검색은 S3 vector 기능 기반 인덱스로 분리 |
| AWS Neptune Graph Index | 도시·축제·테마·장소 관계의 다단계 탐색과 관계 기반 후보 확장에 사용. 의미 검색은 S3 vector, 관계 탐색은 Neptune으로 분리 |
| 축제 검증 캐시 | `festival_id + travelYear` 기준으로 해당 연도 날짜 검증 결과를 재사용해 웹 검색 비용과 지연을 줄임 |
| 실시간 API 교차 검증 | 당해 연도 정확한 개최 일정/기간 등 실시간 최신화가 필수적인 특정 항목에 한해, `Festival_Verifier_Agent`가 공식 웹 출처를 확인하고 정적 필드를 보완하는 하이브리드 데이터 연동 |
| 목적지 기본 정보 | 정규화된 소도시 단위로 관리 |
| 테마 태그 | 기본 6개 테마와 확장 테마 분리 |
| 월별 기상 경향 | 추천용 정적 통계 데이터(장마 플래그, 태풍 경향 등)로 관리 |
| 축제·행사 | 지역, 월, 개최 상태, 출처 링크 포함 |
| 혼잡도 | 방문객 수 또는 대체 지표 기반 점수화 |

## 6.2 표시용 데이터

| 데이터 | 처리 방식 |
| --- | --- |
| 현재 날씨 | WeatherAPI를 통해 상세 화면에 표시 |
| 지도/장소 상세 | Google Maps/Kakao Maps 링크와 API 결과 사용 |
| 숙소 검색 링크 | 직접 추천 없이 플랫폼 검색 URL 생성 |

# 7. 보안 및 개인정보

| 항목 | 정책 |
| --- | --- |
| 대화 로그 | 전문 저장 금지 |
| 일정·선호·피드백 | PoC 로컬, Production 계정 기반 저장 |
| API Key | 서버 환경 변수 또는 프록시에서 관리 |
| 운영 기능 | 역할 기반 인증·인가 필수 |
| 외부 응답 | 스키마 검증 후 사용 |
| Agent 권한 | AgentCore Identity 또는 동등한 권한 경계로 Memory, Gateway Skill, Browser, Knowledge Base 접근 범위를 분리 |
| Agent 정책 | 국가 혼합 금지, 미검증 축제 일정 배치 금지, 대화 원문 trace 금지를 Policy/Validation Skill로 강제 |

# 8. 품질 및 관측성

| 항목 | 기준 |
| --- | --- |
| 추천 처리 시간 | 멀티스텝 Agent 전체 8초 이내 목표 |
| RAG 검색 | 1초 이내 반환 목표 |
| 외부 API 실패 | 폴백 메시지와 부분 결과 제공 |
| 추천 품질 | 추천 이유와 출처를 함께 제공 |
| Agent 추적 | 노드명, next_node, matrix 상태, retry_count, fallback 여부, latency, token 사용량을 redacted trace로 기록 |
| 운영 추적 | 데이터 제안·검토·승인 이력 저장 |

## 8.1 Agent 런타임 경계

| 계층 | 기술 후보 | 책임 |
| --- | --- | --- |
| Runtime | LangGraph, AgentCore Runtime | Supervisor와 Sub-Agent 그래프 실행 |
| Memory | AgentCore Memory, DynamoDB | 세션 상태, 롤링 요약, `fulfilled_matrix`, 축제 검증 캐시 저장 |
| Gateway | Lambda/API 기반 Skill | Scoring, Matrix Transition, Validation, Link, Weather, Packaging 같은 결정적 Skill 실행 |
| Model | Amazon Bedrock Converse API | Sub-Agent별 LLM 추론과 모델 교체 추상화 |
| Retrieval | S3 vector 기반 RAG Index, AWS Neptune | 자연어·테마 임베딩 검색은 S3 vector, 도시·축제·테마 관계 탐색은 Neptune으로 분리 |
| Evaluation | AgentCore Evaluations 또는 동등 하네스 | trajectory, 조건 충족, 근거성, 루프 안전성 회귀 평가 |

# 9. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.3 | 2026-06-08 | 로브 기획팀 | AWS SAM 기반 Auth, Map, AgentCore Lambda 분리 전략과 timeout·패키지·권한 경계 기준 추가 |
| v0.2 | 2026-05-31 | 로브 기획팀 | 통합 목적지 DB 및 실시간 API 교차 검증 하이브리드 아키텍처 반영, Recommendation Module 내 Supervisor Router의 상태 제어 역할 추가 |
| v0.1 | 2026-05-29 | 로브 기획팀 | 기술 명세서 초안 작성 |
