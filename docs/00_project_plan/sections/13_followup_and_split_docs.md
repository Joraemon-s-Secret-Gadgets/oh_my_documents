# 13. 후속 문서 및 분리 문서

| 문서 | 목적 |
| --- | --- |
| 요구사항 명세서 | 기능·비기능 요구사항과 우선순위 상세 정의 |
| 서비스 흐름 명세서 | 역할별 사용 흐름과 기대 결과 정의 |
| 화면 흐름 / 정보 구조 | 화면 구성, 메뉴, 페이지 이동 정의 |
| 시스템 아키텍처 | 프론트엔드, 백엔드, 데이터, 외부 API 구조 정의 |
| 데이터베이스 설계 | 데이터 모델, 권한, 검증 이력 구조 정의 |
| API 명세서 | 엔드포인트, 요청·응답, 인증·인가 정의 |
| 테스트 계획서 | 기능, 권한, API 장애, 추천 품질 검증 기준 정의 |
| B2C 수요 검증 | 한국인 방일·일본인 방한 소도시 수요와 제품 범위 검증 |
| B2B 제휴 전략 | 클룩·라쿠텐 트래블·KKday 성과형 제휴 모델 |
| KICK 설계 | 공개 일정 탐색, 유사 취향 매칭, 1탭 복제, 전환 검증 |
| Aha Moment 설계 | 추천 경험의 발견·납득·실행가능성 강화 전략 |
| 시장조사 | 트리플·트립닷컴 대비 최소 기능과 차별점 |
| B2G 공익 협력 | 비과금 월간 여행지 노출과 공공 성과 측정 |

대표 기획서와 같은 기준으로 관리하는 보조 Markdown은 `docs/00_project_plan/supplemental/`에서 관리한다.

| 보조 Markdown | 분리 내용 |
| --- | --- |
| `supplemental/market_positioning.md` | 카피, 시장 포지셔닝, 기존 서비스 대비 차별점 |
| `supplemental/feature_scope_summary.md` | 대표 기획서와 동일한 사용자 흐름, 사용자 기능, 추천 기능, 운영·관리 기능 상세 |
| `supplemental/business_model.md` | 대표 기획서와 동일한 B2C·B2B·B2G 모델 상세 |
| `supplemental/data_ops_scope.md` | 대표 기획서와 동일한 데이터 범위, 외부 연동, 데이터 파이프라인, 운영 리스크 |
| `supplemental/kick_summary.md` | 대표 기획서와 동일한 KICK 정의, 공개 일정·1탭 복제 원칙, 개인정보 원칙 |
| `supplemental/aha_moment_summary.md` | 대표 기획서와 동일한 Aha Moment, funnel, cold start, 취향 프로필 |
| `supplemental/technical_direction_summary.md` | 대표 기획서와 동일한 Explainable RAG 파이프라인과 시스템 원칙 상세 |

대표 기획서의 최상위 `#` 장 단위 하위 Markdown은 `docs/00_project_plan/sections/*.md`에 둔다. 하위 Markdown은 장 단위 편집 원본이며, 대표 문서인 `00_project_plan.md`는 이 파일들을 순서대로 합쳐 만든 통합본이다.

앞으로 프로젝트 기획서 본문은 `sections/*.md`를 먼저 수정한 뒤 `00_project_plan.md` 통합본에 반영한다.
