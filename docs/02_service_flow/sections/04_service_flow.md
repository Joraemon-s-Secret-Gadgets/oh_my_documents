# 4. Service Flow

API 경로는 `docs/07_api_spec/07_api_spec.md`의 Base URL `/api/v1`을 전제로 표기한다.

| 단계 | Trigger | Frontend 처리 | 상태 / 데이터 관리 | AI & Infra 비즈니스 로직 | 결과 |
| --- | --- | --- | --- | --- | --- |
| 1 | 앱 로드 및 세션 검증 | 브라우저 쿠키의 Refresh Token 유무를 확인하고 현재 사용자 조회를 요청한다 | `GET /auth/me`, `Cookie: Refresh Token`, `Memory: Access Token` | 백엔드가 토큰 유효성을 검증하고 사용자 ID와 역할을 식별한다. 만료 시 재발급 또는 로그인 전환을 처리한다 | 유효하면 메인 화면으로 진입하고, 토큰이 없거나 만료되면 로그인 화면으로 이동한다 |
| 2 | 소셜/자체 로그인 완료 | OAuth 인가 코드 또는 로그인 폼 데이터를 백엔드로 전송한다 | `POST /auth/login`, `User`, `Preference`, `SavedItinerary` | 자체 로그인은 비밀번호 해시를 검증하고, 소셜 로그인은 제공자 API로 사용자를 식별한 뒤 신규/기존 회원을 매핑한다 | JWT 발급, 보안 쿠키 설정, 개인화 메인 대시보드 출력 준비가 완료된다 |
| 3 | 목적지 및 테마 전송 | 사용자가 입력한 국가, 시기, 자연어 취향, 테마 칩을 추천 요청 상태로 구성한다 | `GET /destinations/map-markers`, `POST /recommendations`, `State: recommendationSession` | 자연어 쿼리를 조건 객체로 구조화하고, 벡터 DB와 목적지 DB에서 소도시 후보를 검색한다. 혼잡도와 계절성 필터를 적용한다 | 메이저 대도시를 대체할 수 있는 소도시 후보군 또는 1차 추천 결과가 반환된다 |
| 4 | 소도시 선택 및 대화 시작 | 특정 소도시를 확정한 뒤 AI 일정 생성 챗봇으로 진입한다 | `State: selectedDestination`, `State: chatSession`, `PlanDraft` | 선택 소도시의 축제 정보, 월별 기상 경향, 온보딩 선호, 피드백 이력을 초기 프롬프트와 Agent 상태에 주입한다 | 초기 어시스턴트 메시지와 소도시 맞춤 상태 칩 UI가 렌더링된다 |
| 5 | 동적 AI 일정 생성 요청 | 사용자가 기간, 이동 성향, 동행, 축제 포함 여부를 메시지로 전송한다 | `POST /recommendations`, `PlanDraft`, `RecommendationResult` | Intent Agent, Supervisor Router, Retriever, Festival Verifier, Ranker, Itinerary Writer, Output Validator 순으로 실행한다 | 데이터 출처와 검증 상태 뱃지가 포함된 오전/오후/저녁 타임라인과 챗봇 응답을 출력한다 |
| 6 | 실시간 일정 피드백 | 사용자가 카페 추가, 동선 최적화, 덜 걷기 등 수정 요구사항을 입력한다 | `State: PlanDraft`, `POST /recommendations/{recommendationId}/alternatives/weather` | 기존 PlanDraft와 신규 요구사항을 재투입하고 특정 타임라인 블록만 수정한다. 월별 기상 경향에 따라 실내 중심 대체 일정을 결합한다 | 수정된 타임라인 레이아웃과 대체 일정 토글 UI가 반영된다 |
| 7 | 최종 일정 저장 및 외부 연동 | 사용자가 마이페이지 저장, 지도 열기, 숙소/맛집 상세 링크를 클릭한다 | `POST /me/itineraries`, `POST /me/feedback`, `GET /external/search-links`, `GET /external/stay-links` | 저장 일정은 사용자 ID와 매핑하고 피드백은 향후 랭킹 가중치 업데이트 데이터로 축적한다. 숙소는 직접 추천하지 않고 검색 딥링크만 생성한다 | 마이페이지 내 일정이 보존되고 신뢰 가능한 현지 플랫폼으로 외부 이동한다 |
| 8 | 지자체 데이터 검증 및 업데이트 | 지자체나 로컬 파트너가 축제/체험 정보 업데이트를 제안한다 | `POST /admin/data-submissions`, `PATCH /admin/data-submissions/{submissionId}/review` | 관리자 승인 후 RDB와 벡터 DB에 콘텐츠를 반영하고 출처·검증 상태를 갱신한다 | 일반 사용자 추천 풀에 최신 로컬 데이터와 검증 완료 뱃지가 반영된다 |
