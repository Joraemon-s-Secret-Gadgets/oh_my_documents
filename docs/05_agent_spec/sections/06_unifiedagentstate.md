# 6. UnifiedAgentState

LangGraph 그래프 전역 상태다.
구현 기준은 Python 3.12 `TypedDict`이며 상세 정본은 `supplemental/langgraph_flow.md`를 따른다.

```python
from typing import TypedDict, List, Dict, Any, Optional

class UnifiedAgentState(TypedDict):
    # --- 대화/컨텍스트 (Intent_Agent 소유) ---
    messages: List[Dict[str, str]]            # 전체 멀티턴 백로그 (Supervisor에 미전달)
    conversation_summary: str                 # 롤링 요약 (백로그 토큰 bound)
    turn_index: int                           # 현재 사용자 턴 번호
    session_id: str                           # 세션 식별자
    recommendation_request_id: Optional[str]  # MySQL 추천 요청/결과 원장 연결 키
    agent_run_id: Optional[str]               # DynamoDB Agent 실행 trace 연결 키

    # --- Intent → Supervisor handoff payload ---
    extracted_inputs: Dict[str, Any]          # country, travelMonth, travelYear, tripType, theme, entryType, includeFestivals
    user_preferences: List[str]               # RAG/검색용 선호 문장 (의도 관련성 명확분만)
    onboarding_themes: List[str]              # 장기 선호 (온보딩 1~3개)
    chat_extracted_themes: List[str]          # 자연어에서 추출된 테마
    active_required_themes: List[str]         # 필수 충족 대상 (온보딩+자연어 병합, 최대 3)
    theme_priority: Dict[str, str]            # 테마별 high|normal|low
    soft_preferences: List[str]               # quiet, scenic_view 등 랭킹 가산 조건
    cleaned_raw_query: str                    # 반영 가능 조건만 남긴 원문
    theme_queries: Dict[str, str]             # 테마별 벡터 검색 쿼리
    soft_preference_query: str                # 분위기 통합 쿼리
    unsupported_conditions: List[str]         # RAG 미전달, user_notice 대상
    backup_themes: List[str]                  # active 3개 초과 시 밀려난 온보딩 테마
    user_location: Optional[Dict[str, float]] # API userLocation을 Intent adapter가 정규화한 내부 좌표
    user_notice: Optional[str]                # 예외 안내 문구
    excluded_themes: List[str]                # 명시적 거부 테마

    # --- 라우팅 제어 (Supervisor 소유) ---
    next_node: str
    fulfilled_matrix: Dict[str, str]          # 테마/단계별 X|O|△|N/A
    target_region: Optional[str]              # 하위 호환용 지역 상태. 신규 흐름은 selected_city/candidate_evidence_package를 우선 사용
    validation_retry_count: int               # 검증 실패 재시도 카운터 (상한 2)

    # --- 수집/생성물 (Worker/Skill 누적) ---
    candidate_evidence_package: Optional[Dict[str, Any]]  # Candidate_Evidence_Agent 출력
    raw_collected_data: List[Dict[str, Any]]  # 하위 호환용 수집 데이터, 기상 경향 등
    festival_verifications: List[Dict[str, Any]]  # Festival_Verifier 결과 JSON
    selected_destination: Optional[Dict[str, Any]]
    itinerary: Optional[Dict[str, Any]]
    recommendation_reasons: Optional[List[str]]
    confidence: Optional[float]
```

상태 정책:

- `messages` 원문은 Memory에만 두고 Supervisor에 통째 전달하지 않는다.
- `conversation_summary`와 최근 N턴만 `Intent_Agent` 입력으로 사용한다.
- `fulfilled_matrix`는 `X`, `O`, `△`, `N/A`만 사용한다.
- `validation_retry_count` 상한은 2회다.
- `unsupported_conditions`는 RAG 검색 조건으로 전달하지 않고 `user_notice`와 외부 검색 링크로 분리한다.
- `recommendation_request_id`는 MySQL 추천 요청/결과 원장과 연결되는 추적 키다.
- `agent_run_id`는 DynamoDB `lovv_agent_runs`의 Agent 실행 trace와 연결되는 추적 키다.
- `agent_run_id`, `recommendation_request_id`, `session_id`는 원문 대화 없이 상태 요약과 장애 분석 로그를 연결하기 위한 최소 식별자로만 사용한다.
