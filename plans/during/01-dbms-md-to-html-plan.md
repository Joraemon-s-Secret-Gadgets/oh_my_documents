# 확정 DBMS 문서 및 HTML 반영 계획

## 목적

이미 결정된 DBMS 내용을 `docs/05_database_design/01_DBMS.md`, `docs/05_database_design/05_database_design.md`, HTML 출력물에 일관되게 반영한다. DBMS 후보 비교나 선정 논의를 새로 진행하지 않고, 확정된 DBMS 기준으로 문서 내용과 화면 표시를 동기화한다.

## 진행 상태

- [x] 계획 파일을 작업중 폴더(`plans/during`)로 이관했다.
- [x] `docs/05_database_design/01_DBMS.md`의 VectorDB 결정 전 표현을 확정된 PoC 방향으로 정리했다.
- [x] `docs/05_database_design/05_database_design.md`의 DBMS 방향을 MySQL 8 LTS, AWS DynamoDB, VectorDB 기준으로 반영했다.
- [x] `pages/05_database_design.html`에도 동일한 DBMS 내용을 반영했다.
- [x] `01_DBMS.md`, `05_database_design.md`, `05_database_design.html`에 DBMS별 비고를 반영했다.
- [x] 이전 DBMS 기준과 결정 전 표현의 잔여 여부를 검색해 남아 있지 않음을 확인했다.
- [x] 사전에 작성된 `1.2 데이터베이스 방향` 이후의 상세 설계 내용은 제거한다.

## 대상

- DBMS 상세 문서: `docs/05_database_design/01_DBMS.md`
- 통합 Markdown 반영 대상: `docs/05_database_design/05_database_design.md`
- 관련 참고 문서: `plans/before/md-html-linebreak-revert-plan.md`
- 예상 출력 대상:
  - 기존 HTML 문서 페이지
  - 정적 HTML 출력 디렉터리
  - 또는 Markdown 렌더링을 담당하는 프론트엔드/템플릿 영역

## 작업 단계

### 1. 현재 구조 확인

- [x] 확정된 DBMS명이 `docs/05_database_design/01_DBMS.md`에 명확히 반영되어 있는지 확인한다.
- [x] `docs/05_database_design/01_DBMS.md`에서 후보 비교, 결정 전 표현, 선택 예정 표현이 남아 있는지 확인한다.
- [x] `docs/05_database_design/05_database_design.md`의 기존 문서 구성과 DBMS 섹션 포함 방식을 확인한다.
- [x] 표, 목록, 코드블록, 링크, 이미지, HTML 태그 포함 여부를 확인한다.
- [x] 프로젝트 안에서 Markdown을 HTML로 변환하는 기존 스크립트나 템플릿을 찾는다.
- [x] 이미 생성된 HTML 문서가 있다면 파일 위치와 스타일 규칙을 확인한다.

### 2. 반영 기준 확정

- [x] DBMS는 이미 결정된 사항으로 서술하고, 후보군 검토나 선정 과정 중심으로 작성하지 않는다.
- [x] 확정 DBMS의 선택 사유, 적용 범위, 주요 설정 또는 사용 방식을 문서에 반영한다.
- [x] `01_DBMS.md`와 `05_database_design.md`에서 같은 DBMS명을 사용한다.
- [x] Markdown heading은 HTML heading 계층을 그대로 유지한다.
- [x] 표는 `<table>` 구조로 렌더링하되, 화면 폭이 좁을 때 가로 스크롤이 가능해야 한다.
- [x] 코드블록은 `<pre><code>` 구조를 유지한다.
- [x] 내부 링크는 HTML 출력 위치 기준으로 상대 경로가 깨지지 않도록 조정한다.
- [x] 이미지 경로는 원본 Markdown 위치와 HTML 출력 위치의 차이를 고려해 검증한다.
- [x] 줄바꿈 처리는 `md-html-linebreak-revert-plan.md`의 방향과 충돌하지 않게 적용한다.

### 3. 반영 방식 결정

- [x] 기존 HTML 출력 파일인 `pages/05_database_design.html`을 확인한다.
- [x] 이번 변경은 기존 정적 HTML 문서 구조를 유지하고 필요한 DBMS 표기만 직접 갱신한다.
- [x] 단일 문서만 반영하는 별도 임시 로직은 추가하지 않는다.

### 4. Markdown 반영

- [x] `docs/05_database_design/01_DBMS.md`를 확정 DBMS 기준으로 정리한다.
- [x] `docs/05_database_design/05_database_design.md`에 확정 DBMS 내용을 반영한다.
- [x] 두 문서에서 후보 검토가 필요한 것처럼 보이는 문장을 제거하거나 확정 서술로 수정한다.
- [x] `05_database_design.md`가 통합 문서라면 DBMS 상세 내용은 요약하고, 필요한 경우 `01_DBMS.md`로 연결한다.
- [x] `docs/05_database_design/05_database_design.md`에서 사전에 작성된 `1.2 데이터베이스 방향` 이후의 상세 설계 섹션을 제거한다.

### 5. HTML 반영

- [x] `01_DBMS.md` 내용을 대상 HTML 페이지에 반영한다.
- [x] `05_database_design.md` 내용을 대상 HTML 페이지에도 반영한다.
- [x] 문서 제목과 목차가 필요한 경우 heading 기준으로 구성한다.
- [x] 기존 문서 페이지의 CSS 클래스와 레이아웃을 재사용한다.
- [x] 문서 본문 스타일은 다른 HTML 문서와 일관되게 유지한다.
- [x] `pages/05_database_design.html`에서 사전에 작성된 `1.2 데이터베이스 방향` 이후의 상세 설계 섹션과 목차 항목을 제거한다.

### 6. 검증

- [x] `docs/05_database_design/01_DBMS.md`와 `docs/05_database_design/05_database_design.md`의 반영 내용이 서로 어긋나지 않는지 확인한다.
- [x] HTML 화면에서도 DBMS가 확정된 사항으로 표시되는지 확인한다.
- [x] 후보 비교나 결정 전 표현이 남아 있지 않은지 확인한다.
- [x] HTML 페이지에서 heading 계층이 정상적으로 보이는지 확인한다.
- [x] HTML 페이지 목차가 남은 섹션만 가리키는지 확인한다.
- [x] 표가 화면 밖으로 깨지지 않는지 확인한다.
- [x] 코드블록의 줄바꿈과 가로 스크롤을 확인한다.
- [x] 링크와 이미지가 정상 동작하는지 확인한다.
- [x] 기존 Markdown 기반 HTML 페이지가 있다면 렌더링 회귀가 없는지 확인한다.

### 7. 완료 기준

- [x] `docs/05_database_design/01_DBMS.md`의 내용이 HTML 화면에 반영되어 있다.
- [x] `docs/05_database_design/05_database_design.md`에도 동일한 DBMS 문서 변경 내용이 반영되어 있다.
- [x] `docs/05_database_design/05_database_design.md`의 내용도 HTML 화면에 반영되어 있다.
- [x] `1.2 데이터베이스 방향` 이후의 사전 작성 상세 설계 내용이 Markdown과 HTML에서 제거되어 있다.
- [x] DBMS가 확정된 사항으로 문서와 HTML에 일관되게 표현되어 있다.
- [x] 표, 코드블록, 링크, 이미지, 줄바꿈이 깨지지 않는다.
- [x] 기존 문서 렌더링 방식과 스타일 일관성이 유지된다.
- [x] 변경 파일과 검증 결과를 작업 완료 메시지에 정리한다.

## 주의사항

- DBMS 후보를 새로 비교하거나 선정 근거를 재작성하는 작업으로 범위를 넓히지 않는다.
- `01_DBMS.md` 원본 내용은 확정 DBMS 반영 목적 외에는 변경하지 않는다.
- `05_database_design.md`가 HTML 생성의 기준 문서라면 `docs/05_database_design/01_DBMS.md`와 별도로 관리하지 말고, 어느 파일이 원본인지 먼저 확정한다.
- 줄바꿈 정책을 바꿔야 할 경우, 기존 `md-html-linebreak-revert-plan.md`와 충돌 여부를 먼저 확인한다.
- HTML 반영 과정에서 전체 문서 변환 규칙을 변경하면 다른 문서에 영향을 줄 수 있으므로 회귀 확인을 함께 진행한다.
