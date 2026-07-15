---
작성자: llm팀
상태: 진행전
---

# LLM 연동 웹 애플리케이션 개발 결과 보고서 작성 계획

## 목적

본 계획은 Lovv 프로젝트의 LLM 연동 웹 애플리케이션 개발 결과를 제출용 결과물로 서술하기 위한 작성 기준을 정리한다. 포트폴리오처럼 개인 기여나 회고를 강조하지 않고, 개발된 시스템의 목적, 구조, 기능, LLM/RAG/Agent 연동 방식, API/데이터 연동, 검증 결과를 결과 보고서 형식으로 설명한다.

## 작성 대상

- 결과 보고서 제목: `LLM 연동 웹 애플리케이션 개발 결과 보고서`
- 대상 서비스: Lovv 여행 추천 웹 애플리케이션
- 작성 관점: 결과 제출용 산출물
- 제외 관점: 개인 포트폴리오, 개인 역할 소개, 역량 어필, 주관적 회고 중심 서술

## 참조 문서

| 참조 문서 | 활용 목적 |
| --- | --- |
| `docs/05_agent_spec/05_agent_spec.md` | LLM/Agent 파이프라인, Intent Agent, Candidate Evidence Agent, Planner Agent 구조 근거 |
| `docs/05_agent_spec/supplemental/agent_integrated_explanation.md` | 비전문 독자에게 설명 가능한 Agent 처리 흐름 근거 |
| `docs/05_agent_spec/supplemental/candidate_evidence_runtime_retrieval.md` | RAG 검색, S3 Vector, DynamoDB 조회, 후보 패키징 흐름 근거 |
| `docs/06_technical_spec/06_technical_spec.md` | 전체 시스템 구성, Frontend/Backend/Agent/Data/외부 API 기술 구조 근거 |
| `docs/07_api_spec/07_api_spec.md` | `/recommendations`, `/agent/answer`, 저장 일정 API 등 웹/API 연동 근거 |
| `docs/10_test_plan/supplemental/candidate_evidence_evaluation_results.md` | Candidate Evidence Agent 평가와 검증 결과 근거 |
| `docs/11_deployment_ops/11_deployment_ops.md` | 배포·운영 관점 설명이 필요한 경우의 보조 근거 |

## 권장 최종 목차

1. 개발 개요
2. 개발 목표
3. 전체 시스템 구성
4. LLM 연동 구조
5. Agent/RAG 추천 처리 흐름
6. 주요 기능 개발 결과
7. 데이터 및 RAG 연동 결과
8. API 및 웹 연동 결과
9. 검증 결과
10. 개발 결과 요약
11. 한계 및 향후 개선 사항

## 섹션별 서술 계획

### 1. 개발 개요

- Lovv를 "사용자 자연어 입력을 기반으로 여행 조건을 해석하고, 검증된 여행 데이터를 검색해 소도시 중심 일정을 추천하는 웹 애플리케이션"으로 정의한다.
- 결과물 범위는 웹 화면, 백엔드 API, LLM/Agent 추천 파이프라인, RAG 검색, 데이터 연동, 검증 결과로 한정한다.
- 개인 역할, 팀원별 담당, 회고는 포함하지 않는다.

### 2. 개발 목표

- 단순 챗봇이 아니라 근거 기반 여행 추천 시스템 개발이 목표였음을 설명한다.
- 목표 항목은 다음 기준으로 정리한다.
  - 자연어 여행 조건 입력
  - LLM 기반 의도 해석
  - RAG 기반 후보 검색
  - 데이터 기반 후보 점수화와 검증
  - 일정과 추천 이유 생성
  - 웹/API/데이터 연동
  - 검증 가능한 결과 산출

### 3. 전체 시스템 구성

- Frontend Web, Backend API, Recommendation Agent, RAG Index, DynamoDB/S3 Vector, 외부 API, 운영 구성을 계층별로 설명한다.
- Mermaid 구조도를 포함해 사용자의 요청이 어떤 구성 요소를 거쳐 결과로 반환되는지 시각화한다.
- 기술 스택 나열로 끝내지 않고 각 구성 요소의 책임을 함께 쓴다.

### 4. LLM 연동 구조

- LLM이 맡은 책임과 결정론적 Tool/데이터 로직이 맡은 책임을 분리해서 설명한다.
- LLM 사용 영역:
  - 사용자 자연어 의도 해석
  - 추천 설명 생성
  - 일정 흐름 설명 생성
  - 부족 조건 또는 안내 문구 생성
- 비-LLM 처리 영역:
  - 도시/장소 후보 검색
  - DynamoDB/S3 Vector 조회
  - 후보 점수화
  - 필수 입력 검증
  - API 응답 포장
- 핵심 문장은 "LLM이 임의로 여행지를 생성하는 방식이 아니라, 검색된 후보와 검증된 데이터를 기반으로 응답을 생성하도록 구성하였다"로 잡는다.

### 5. Agent/RAG 추천 처리 흐름

- 추천 생성 흐름을 다음 순서로 서술한다.
  1. 사용자가 웹 화면에서 자연어와 여행 조건을 입력한다.
  2. Backend API가 요청을 정규화해 Agent 실행 경계로 전달한다.
  3. Intent Agent가 국가, 월, 여행 기간, 테마, 축제 포함 여부, 목적지 anchor 등을 구조화한다.
  4. Candidate Evidence Agent가 S3 Vector와 DynamoDB 기반으로 도시/장소/축제 후보를 검색한다.
  5. Scoring/Validation 로직이 후보 충분성, 테마 커버리지, 중복, fallback 필요 여부를 판단한다.
  6. Planner Agent가 후보 패키지를 기반으로 일정, 추천 이유, 사용자 안내를 생성한다.
  7. Backend가 프론트엔드/API 응답 형식으로 결과를 포장한다.
  8. 웹 화면이 추천 일정과 추천 이유를 표시한다.
- 이 섹션에는 처리 흐름 Mermaid를 포함한다.

### 6. 주요 기능 개발 결과

- 기능을 "구현된 사용자 결과" 중심으로 정리한다.
- 포함 기능:
  - 자연어 여행 추천 요청
  - 국가, 월, 여행 기간, 테마 조건 기반 추천
  - 소도시 1곳 중심 일정 생성
  - 추천 이유와 일정 흐름 이유 제공
  - 지도, 숙소, 맛집 검색 링크 제공
  - 후보 부족 시 fallback 처리
  - 저장 일정 및 피드백 API 연동
  - 단일 턴 Agent 답변 API 제공

### 7. 데이터 및 RAG 연동 결과

- 데이터 수집·전처리 결과가 추천 품질과 어떻게 연결되는지 설명한다.
- DynamoDB는 정형 도메인 데이터 source of truth로, S3 Vector는 자연어·테마 기반 의미 검색 인덱스로 설명한다.
- 검색 결과가 바로 최종 응답이 되는 것이 아니라, 후보 패키지와 점수화 과정을 거쳐 Planner 입력으로 사용된다는 점을 명확히 한다.
- 실시간성이 필요한 축제 날짜 등은 별도 검증 또는 사용자 안내 대상으로 분리한다.

### 8. API 및 웹 연동 결과

- 웹 애플리케이션 결과물임을 보여주기 위해 프론트엔드 요청에서 API 응답까지의 흐름을 설명한다.
- 주요 API:
  - `POST /recommendations`: 추천 생성
  - `GET /recommendations/{recommendationId}`: 추천 결과 조회
  - `POST /agent/answer`: 저장 없는 단일 턴 AI 답변 생성
  - `POST /me/itineraries`: 추천 일정 저장
  - 지도/목적지 상세 조회 API
- API 설명은 엔드포인트 목록으로 끝내지 않고 "웹 화면에서 어떤 사용자 행동과 연결되는지"를 함께 서술한다.

### 9. 검증 결과

- 검증은 결과 제출물의 핵심 근거로 배치한다.
- 포함할 검증 항목:
  - 로컬 결정적 테스트 결과
  - Candidate Evidence Agent 평가 결과
  - Baseline 대비 후보 충분성 개선
  - 테마 커버리지와 후보 다양성 개선
  - 블라인드 LLM judge 또는 정성 평가 결과
  - 비용·성능 trade-off
- 한계도 함께 쓴다.
  - LLM judge는 실제 사용자 평가를 완전히 대체하지 않는다.
  - 실시간 영업 여부, 예약 가능 여부, 혼잡도는 확정 추천 근거로 쓰지 않는다.
  - Planner-level 이동 시간, 운영 시간, 실제 방문 가능성 평가는 후속 검증 대상이다.

### 10. 개발 결과 요약

- 결과를 3~5문장으로 압축한다.
- 예시 방향:
  - "본 개발을 통해 Lovv는 자연어 입력, RAG 기반 후보 검색, Agent 기반 일정 생성, 웹/API 연동을 포함한 LLM 연동 여행 추천 웹 애플리케이션 구조를 구현하였다."
  - "LLM은 의도 해석과 설명 생성에 사용하고, 추천 후보 검색과 검증은 데이터와 Tool 기반으로 분리해 근거 기반 추천 구조를 확보하였다."

### 11. 한계 및 향후 개선 사항

- 과장 없이 남은 과제를 결과 보고서 형식으로 정리한다.
- 포함 항목:
  - 실시간 교통/영업/예약 API 연동
  - 사용자 저장 일정 기반 개인화 강화
  - 장기 메모리와 선호도 반영
  - human blind review 기반 추천 품질 평가 확대
  - 비동기 추천 처리 또는 스트리밍 응답 도입

## 작업 체크리스트

- [ ] 제출 양식 또는 분량 제한이 있는지 확인한다.
- [ ] 최종 문서 위치를 정한다. 후보: `docs/99_pptx/`, `docs/00_project_plan/supplemental/`, 별도 제출용 Markdown.
- [ ] `docs/05_agent_spec/05_agent_spec.md`에서 Agent 구성과 역할을 발췌한다.
- [ ] `docs/06_technical_spec/06_technical_spec.md`에서 전체 시스템 구조를 발췌한다.
- [ ] `docs/07_api_spec/07_api_spec.md`에서 주요 API와 웹 연동 흐름을 발췌한다.
- [ ] `docs/10_test_plan/supplemental/candidate_evidence_evaluation_results.md`에서 검증 결과를 발췌한다.
- [ ] 위 목차에 맞춰 1차 본문을 작성한다.
- [ ] Mermaid 시스템 구성도와 Agent 처리 흐름도를 추가한다.
- [ ] 포트폴리오식 개인 기여 표현을 제거한다.
- [ ] 결과, 근거, 검증, 한계가 모두 들어갔는지 점검한다.
- [ ] 필요한 경우 Markdown 원본을 기준으로 HTML 또는 PDF 산출물을 생성한다.
- [ ] 생성물이 있다면 `python scripts/generate_pages.py`와 `python scripts/verify_pages_structure.py`로 문서 사이트 구조를 검증한다.

## 검증 방법

- 문서 내용 검증:
  - 각 주요 주장에 대응하는 참조 문서가 있는지 확인한다.
  - LLM, RAG, Agent, API, 데이터, 검증 결과가 모두 포함됐는지 확인한다.
  - 개인 포트폴리오 문체가 남아 있지 않은지 확인한다.
- 산출물 검증:
  - Markdown만 제출하는 경우: 제목, 목차, 표, Mermaid 코드 블록 렌더링 가능 여부 확인.
  - HTML을 생성하는 경우: `python scripts/generate_pages.py` 실행 후 `python scripts/verify_pages_structure.py` 실행.
  - PDF를 생성하는 경우: 원본 Markdown과 PDF 산출물의 문서 의미가 일치하는지 확인.

## 완료 기준

- 제출용 결과 보고서가 포트폴리오가 아닌 개발 결과물 관점으로 작성되어 있다.
- 전체 시스템 구성, LLM 연동 구조, RAG/Agent 처리 흐름, 주요 기능 결과, API/웹 연동, 검증 결과, 한계 및 개선 사항이 모두 포함되어 있다.
- Lovv의 차별점이 "LLM 챗봇"이 아니라 "근거 기반 여행 추천 Agent 웹 애플리케이션"으로 드러난다.
- 필요한 경우 HTML/PDF 생성물까지 검증된다.
