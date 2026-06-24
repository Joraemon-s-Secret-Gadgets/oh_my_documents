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
