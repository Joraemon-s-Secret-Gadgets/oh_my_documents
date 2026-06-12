# 로브 (Lovv) 트러블슈팅 문서

> 문서 버전: v0.3
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-12
> 작성자: llm팀
> 기준 문서: `../04_database_design/04_database_design.md`, `../04_database_design/neptune_alternative.md`, `../07_api_spec/07_api_spec.md`, `../08_data_preprocessing/korea_data_preprocessing_result_report.md`, `../08_data_preprocessing/s3_vector_index_plan.md`, `../99_pptx/01_midterm_presentation/01_midterm_presentation.md`
> 문서 목적: 프로젝트 진행 중 발생한 주요 이슈를 원인, 판단, 조치, 재발 방지 기준으로 정리해 발표와 운영 문서에서 함께 사용할 수 있게 한다.

---

# 1. 문서 개요

이 문서는 로브(Lovv) 프로젝트에서 발생했거나 현재 운영 기준상 주의해야 하는 이슈를 트러블슈팅 관점으로 정리한다.

정리 기준은 다음과 같다.

| 기준 | 설명 |
| --- | --- |
| 증상 | 겉으로 드러난 문제 또는 의사결정이 필요했던 지점 |
| 원인 | 기술적·운영적 원인 |
| 판단 | 왜 해당 방향으로 결정했는지 |
| 조치 | 실제로 취한 대응 또는 현재 적용할 대응 |
| 재발 방지 | 같은 문제가 반복되지 않도록 남기는 기준 |

# 2. 요약

| ID | 이슈 | 현재 상태 | 핵심 조치 |
| --- | --- | --- | --- |
| TS-01 | Neptune 도입 범위 판단 | Lambda 대체 구현 예정 | 그래프DB 직접 도입 대신 RDS JOIN, DynamoDB 인접 리스트, 사전계산 후보 테이블, Lambda 인메모리 그래프로 유사 기능 구현 |
| TS-02 | KR 전처리 적재 기준 정리 | 완료 | `TourKoreaDomainData` 기준으로 재적재, GSI 3종 활성화, legacy 테이블 제거 |
| TS-03 | S3 vector index 계약 정합성 | 진행 기준 확정 | Titan V2 1024/cosine, 3분절 vector ID, GSI3 export 기준 확정 |
| TS-04 | HTML 공유 문서 생성물 불일치 | 대응 완료 | Markdown 원본 기준으로 `generate_pages.py` 재실행 후 구조 검증 |
| TS-05 | PDF 산출물 생성·검증 | 대응 완료 | `xelatex` 2회 실행, PDF/TeX 산출물과 `pdf/AGENT.md` 목록 동기화 |
| TS-06 | 발표 HTML 검증 중 임시 파일 발생 | 대응 완료 | `.chrome-*` 브라우저 프로필 ignore, 검증 캡처만 산출물로 보관 |
| TS-07 | Cognito / Social Login 책임 경계 충돌 | 기준 확정 | Google/Kakao 직접 검증 API는 legacy로 내리고 Cognito bridge API를 신설 |

# 3. TS-01 Neptune 도입 범위 판단

## 3.1 증상

추천 시스템에서 도시, 테마, 축제, 인접 도시 관계를 다루기 때문에 그래프DB인 Neptune을 도입할 수 있다는 의견이 있었다.

그러나 중간발표 PoC 범위에서는 대부분의 관계 탐색이 1~2-hop 수준이었다. 이 단계에서 Neptune을 바로 넣으면 기능 검증보다 운영 비용과 복잡도가 먼저 증가할 위험이 있었다.

## 3.2 원인

| 항목 | 내용 |
| --- | --- |
| 관계 깊이 | PoC의 주요 질의는 도시-테마, 도시-축제, 도시-장소 수준이다. |
| 비용 | Neptune Serverless도 최소 NCU 기반 고정비가 발생한다. |
| 운영 복잡도 | RDS, DynamoDB, S3 vector 외에 별도 그래프 저장소 운영이 추가된다. |
| 재생성성 | 현재 관계 데이터는 원본 저장소보다 파생 인덱스로 두는 편이 안전하다. |

## 3.3 판단

PoC와 Production 1차에서는 Neptune을 직접 도입하지 않는다.
현재 방향은 그래프DB와 유사한 관계 탐색 기능을 Lambda로 구현하는 것이다.

현재는 다음 대체 방식으로 충분하다.

| 대체 방식 | 적용 범위 |
| --- | --- |
| RDS JOIN | 도시, 테마, 장소, 축제의 정형 관계 조회 |
| DynamoDB 인접 리스트 | 도메인 item 단위 빠른 조회와 서비스 운영 조회 |
| 사전계산 후보 테이블 | 추천 후보 확장과 반복 질의 비용 절감 |
| Lambda 인메모리 그래프 | 요청 시 소규모 관계 탐색, 2-hop 확장, 그래프 재랭킹 보조 |
| S3 vector index | 자연어·분위기 기반 후보 검색 |

## 3.4 조치

- Neptune은 원본 저장소가 아니라 향후 승격 가능한 파생 관계 인덱스로만 정의한다.
- 현재 설계는 RDS, DynamoDB, S3 vector index, Lambda 관계 탐색 보조 기능을 기준으로 작성한다.
- Lambda는 DynamoDB 인접 리스트와 사전계산 후보를 읽어 그래프DB와 유사한 후보 확장·재랭킹 기능을 수행한다.
- 발표에서는 "도입 실패"가 아니라 "비용·범위 검토 후 보류한 기술 판단"으로 설명한다.

## 3.5 승격 기준

다음 조건 중 하나가 실제 요구사항으로 확인되면 Neptune 도입을 재검토한다.

| 승격 조건 | 설명 |
| --- | --- |
| 3-hop 이상 임의 경로 탐색 | 사용자-도시-테마-축제-인접도시처럼 경로가 깊어짐 |
| 대규모 실시간 그래프 쓰기 | 사용자 행동, co-visit, 선호 관계가 지속적으로 누적됨 |
| 복잡한 그래프 알고리즘 | PageRank류 중요도, 커뮤니티 탐지, 경로 추천이 필요해짐 |
| RDS/DynamoDB 대체 구현 한계 | JOIN 또는 사전계산 방식이 운영상 병목이 됨 |

# 4. TS-02 KR 전처리 적재 기준 정리

## 4.1 증상

초기 문서와 일부 설계에는 legacy 테이블명인 `TourKoreaData`가 남아 있었고, 실제 운영 기준은 `TourKoreaDomainData`로 전환됐다.

이 상태를 방치하면 전처리 결과, DynamoDB 조회, S3 vector index 입력 기준이 서로 달라질 수 있었다.

## 4.2 원인

- 초기 설계와 실제 구현이 다른 시점에 갱신됐다.
- Raw JSON 적재, domain loader, Terraform, 문서가 각각 다른 기준을 참조할 수 있었다.
- ingest manifest가 실제 domain load 이력을 완전히 대표하지 못했다.

## 4.3 조치

| 항목 | 조치 |
| --- | --- |
| 테이블 기준 | `TourKoreaDomainData`를 운영 기준으로 확정 |
| 적재 결과 | S3 Raw 40개 파일 기준 4,334 items 적재 |
| GSI | 도시, 도/광역, entity type 조회용 GSI 3종 활성화 |
| legacy 정리 | `TourKoreaData` Terraform resource와 AWS table 제거 |
| 검증 | 전처리 테스트 18개 통과, Lambda 부분 실패 경로 테스트 추가 |

## 4.4 재발 방지

- 문서에는 현재 운영 기준 테이블명을 먼저 적고, 과거 명칭은 migration 맥락에서만 언급한다.
- 신규 검색 인덱스나 API 문서는 `korea_data_preprocessing_result_report.md`를 기준 보고서로 참조한다.
- manifest는 Raw ingest와 domain load를 분리해 기록한다.

# 5. TS-03 S3 vector index 계약 정합성

## 5.1 증상

S3 vector index 생성 기준을 정리하는 과정에서 `city_id`, vector ID, embedding dimension, metadata filter 기준이 초기 설계와 실제 적재 데이터 사이에서 어긋날 수 있었다.

## 5.2 원인

| 항목 | 초기 위험 |
| --- | --- |
| `city_id` | 과거 설계는 `KR-GB-ANDONG` 계열을 가정했지만 실제 데이터는 `KR-Andong` 형식 |
| Vector ID | `#chunk#` 리터럴 포함 4분절과 3분절 형식이 혼재 가능 |
| Embedding | dimension과 metric은 index 생성 후 변경이 어려움 |
| Metadata | filterable 2KB 제한을 넘길 수 있음 |

## 5.3 조치

- `city_id`는 실데이터 기준 `KR-{CityNameEn}` 형식으로 확정한다.
- Vector ID는 `{source_type}#{source_id}#{chunk_no}` 3분절로 통일한다.
- Amazon Titan Text Embeddings V2, 1024 dimension, cosine 기준으로 고정한다.
- `visitor_statistics`는 개별 vector가 아니라 city chunk의 보조 문맥으로만 반영한다.
- CEA 검색 요구에 맞춰 restaurant chunk에는 주소를 포함한다.

## 5.4 재발 방지

- index 생성 전에 dimension, metric, non-filterable key를 문서와 IaC에서 대조한다.
- GSI3 entity type별 export 결과로 원천 수량을 manifest에 남긴다.
- S3 vector 결과는 DynamoDB `ddb_pk`/`ddb_sk`로 재검증하는 것을 기본 계약으로 둔다.

# 6. TS-04 HTML 공유 문서 생성물 불일치

## 6.1 증상

Markdown 원본은 정상인데 `pages/*.html` 생성물이 중간에 끊기거나 오래된 내용을 표시할 수 있었다.

## 6.2 원인

- Markdown 원본 수정 후 HTML 생성 스크립트를 다시 실행하지 않았다.
- 표나 긴 문단이 HTML 변환 과정에서 깨졌는지 확인하지 않았다.

## 6.3 조치

HTML 공유 문서를 갱신한 뒤 다음 명령을 실행한다.

```powershell
python scripts\generate_pages.py
python scripts\verify_pages_structure.py
```

## 6.4 재발 방지

- 본문 의미 변경은 항상 `docs/` Markdown 원본에서 먼저 수행한다.
- `pages/*.html`은 생성물로 보고 직접 수정하지 않는다.
- 커밋 전 `git diff -- pages/*.html`에서 끊긴 표, 깨진 코드블록, 이전/다음 링크를 확인한다.

# 7. TS-05 PDF 산출물 생성·검증

## 7.1 증상

새 결과보고서 Markdown을 추가했지만 PDF/TeX 산출물 또는 `pdf/AGENT.md` 목록이 함께 갱신되지 않으면 배포용 문서와 원본 문서가 어긋난다.

## 7.2 조치

새 PDF 문서를 추가할 때는 다음을 함께 갱신한다.

| 항목 | 경로 예시 |
| --- | --- |
| 원본 Markdown | `docs/08_data_preprocessing/korea_data_preprocessing_result_report.md` |
| TeX 산출물 | `pdf/korea_data_preprocessing_result_report.tex` |
| PDF 산출물 | `pdf/korea_data_preprocessing_result_report.pdf` |
| 산출물 목록 | `pdf/AGENT.md` |

PDF는 다음처럼 2회 빌드한다.

```powershell
cd pdf
xelatex -interaction=nonstopmode -halt-on-error korea_data_preprocessing_result_report.tex
xelatex -interaction=nonstopmode -halt-on-error korea_data_preprocessing_result_report.tex
```

## 7.3 재발 방지

- 목차와 outline 경고가 있으면 2회 빌드한다.
- `pdf/*.aux`, `pdf/*.log`, `pdf/*.out`, `pdf/*.toc`는 중간 산출물이므로 커밋하지 않는다.
- PDF 본문 의미가 바뀌면 먼저 대응 Markdown을 수정한다.

# 8. TS-06 발표 HTML 검증 중 임시 파일 발생

## 8.1 증상

중간발표 HTML을 Playwright/Chrome으로 검증하는 과정에서 `html_export/.chrome-*` 브라우저 프로필 디렉터리가 생성됐다.

## 8.2 판단

검증 캡처는 발표 품질 확인 근거로 보관할 수 있지만, 브라우저 프로필은 로컬 실행 cache이므로 저장소 산출물이 아니다.

## 8.3 조치

| 항목 | 처리 |
| --- | --- |
| `html_export/captures/` | 발표 검증 산출물로 보관 가능 |
| `html_export/.chrome-*` | `.gitignore`로 제외 |
| `lovv_midterm_presentation_native.html` | 실제 발표 HTML 산출물로 보관 |

## 8.4 재발 방지

- 브라우저 자동화는 전용 임시 프로필을 쓰되, 저장소에 남으면 ignore 대상인지 확인한다.
- 발표 HTML을 수정한 뒤에는 주요 슬라이드와 전체 흐름 캡처를 남긴다.
- 전체 화면, 키보드 조작, 내부 애니메이션 상태를 함께 확인한다.

# 9. TS-07 Cognito / Social Login 책임 경계 충돌

## 9.1 배경

초기 Lovv Auth 구조는 프론트가 Google/Kakao에서 받은 provider token을 백엔드로 전달하고, 백엔드가 직접 검증하는 방식이었다.

```text
POST /api/v1/auth/google
POST /api/v1/auth/kakao
↓
Lovv backend가 Google/Kakao provider token 검증
↓
Lovv user 조회/생성
↓
Lovv access token 발급
↓
refresh session 저장
```

하지만 Cognito를 도입하면 Google/Kakao 인증은 Cognito Hosted UI 또는 OIDC IdP가 담당한다. 백엔드는 provider token을 직접 검증하는 대신 Cognito가 검증한 JWT claims 또는 API Gateway Authorizer claims를 기준으로 Lovv 사용자와 세션 응답을 구성해야 한다.

## 9.2 문제 1: 기존 Social Login API와 Cognito 흐름 충돌

| 항목 | 기존 방식 | Cognito 방식 |
| --- | --- | --- |
| Google/Kakao 인증 | Lovv 백엔드가 provider token 직접 검증 | Cognito가 Hosted UI/OIDC IdP로 처리 |
| 백엔드 입력 | provider access token | Cognito JWT claims |
| 백엔드 책임 | provider 검증 + Lovv token 발급 | Lovv user/session shape 변환 |

기존 `/api/v1/auth/google`, `/api/v1/auth/kakao`를 그대로 신규 흐름의 중심으로 두면 인증 책임이 Lovv backend와 Cognito 두 군데로 나뉜다.

### 해결 방향

| API | 상태 | 역할 |
| --- | --- | --- |
| `POST /api/v1/auth/google` | legacy/deprecated | provider token 직접 검증 방식 보존 |
| `POST /api/v1/auth/kakao` | legacy/deprecated | provider token 직접 검증 방식 보존 |
| `POST /api/v1/auth/cognito/session` | 신규 | Cognito claims를 Lovv session 응답으로 변환 |

## 9.3 문제 2: Cognito 로그인 후 Lovv 세션 shape 필요

Cognito가 인증을 처리해도 프론트는 Lovv 서비스 상태가 필요하다.

프론트가 필요한 값은 다음과 같다.

| 값 | 용도 |
| --- | --- |
| `user` | 화면 표시와 사용자 식별 |
| `preferences` | 온보딩 취향 복구 |
| `onboardingCompleted` | 온보딩 진입 여부 결정 |
| `roles` | 사용자/운영자/관리자 화면 분기 |
| `accessToken` 또는 인증 상태 | 인증 API 호출 |
| `sessionRestored` | 세션 복구 성공 여부 |

### 해결 방향

`POST /api/v1/auth/cognito/session`은 API Gateway JWT Authorizer가 검증한 Cognito claims를 받아 Lovv user/session shape로 변환한다.

처리 순서:

```text
Cognito JWT Authorizer 검증
↓
sub, email, cognito:groups claims 확인
↓
Lovv user 조회 또는 생성
↓
Lovv 내부 role 정규화
↓
preferences 조회
↓
onboardingCompleted 계산
↓
session response 반환
```

## 9.4 문제 3: Provider Verifier 재사용 금지

Cognito bridge endpoint에서 기존 Google/Kakao provider verifier를 재사용하면 안 된다. Cognito 흐름에서는 이미 Cognito가 provider 인증을 완료했기 때문이다.

| 경로 | verifier 사용 |
| --- | --- |
| `/auth/google` | Google provider verifier 사용 |
| `/auth/kakao` | Kakao provider verifier 사용 |
| `/auth/cognito/session` | provider verifier 사용 금지. Cognito claims만 매핑 |

## 9.5 문제 4: Cognito claims 누락 시 500 발생 가능

개발 중 missing claims 테스트에서 401이 아니라 500이 발생할 수 있었다.

### 원인

Cognito claims 검증보다 repository 초기화가 먼저 실행되면, 인증 정보가 없는 요청인데 DB/repository 초기화 실패가 먼저 드러나 내부 서버 오류처럼 보인다.

### 해결 방향

- Cognito claims를 먼저 검증한다.
- repository와 DB client는 claims 검증 이후 lazy init한다.
- 인증 실패와 내부 장애를 분리한다.

| 상황 | 기대 응답 |
| --- | --- |
| Cognito claims 없음 | `401 UNAUTHENTICATED` |
| 필수 claim 매핑 불가 | `422 AUTH_MAPPING_ERROR` 또는 명확한 auth mapping error |
| DB 초기화 실패 | claims 검증 이후 `500 INTERNAL_ERROR` |

## 9.6 문제 5: Handler route와 SAM template route 불일치

`src/auth/app.py`에 `/api/v1/auth/cognito/session` 처리를 추가해도 `template.yaml`에 API Gateway route가 없으면 실제 배포 API에서는 접근할 수 없다.

### 해결 방향

코드 테스트뿐 아니라 template route 테스트를 추가한다.

확인 기준:

| 확인 항목 | 기준 |
| --- | --- |
| Handler route | `src/auth/app.py`에 `/api/v1/auth/cognito/session` 처리 존재 |
| SAM route | `template.yaml`의 `AuthFunction` event에 동일 path 존재 |
| API 명세 | `docs/07_api_spec/07_api_spec.md`의 path와 일치 |
| Authorizer | Cognito User Pool/JWT Authorizer 연결은 별도 Task로 추적 |

## 9.7 문제 6: Logout 의미 분리

Cognito 도입 후 logout을 단순히 백엔드 session 삭제로만 설명하면 부족하다. Cognito access token은 JWT이므로 이미 발급된 token은 만료 전까지 유효할 수 있다.

| 구분 | 설명 |
| --- | --- |
| Lovv logout | Lovv backend session/cookie, 프론트 local service state 정리 |
| Cognito logout | Cognito Hosted UI logout URL로 이동해 Hosted UI 세션 종료 |

백엔드가 Cognito token 자체를 즉시 무효화한다고 표현하지 않는다. 프론트는 필요하면 Cognito logout URL로 redirect한다.

## 9.8 문제 7: Role을 Cognito Group만으로 처리하면 복잡해짐

Lovv Admin에는 일반 사용자 외에도 여러 운영 role이 필요하다.

| Role | 의미 |
| --- | --- |
| `R-USER` | 일반 서비스 이용자 |
| `R-ADMIN` | 전체 관리자 |
| `R-LOCAL-OPERATOR` | 담당 지역 데이터와 운영 지표 조회 |
| `R-DATA-PROVIDER` | 관광지, 축제, 체험 데이터 제안 등록 |

### 해결 방향

Cognito Group은 큰 권한 구분만 담당하고, 담당 지역과 provider 소유권 같은 세부 권한은 Lovv DB/backend에서 검증한다.

주의 기준:

- 프론트 route guard만으로 관리자 보안을 처리하지 않는다.
- Lambda/API에서도 role을 검증한다.
- 지역 운영자의 담당 지역 scope는 DB에서 확인한다.

## 9.9 문제 8: API 명세 재정리 필요

기존 OpenAPI/API 명세는 custom social login 기준이라 Cognito bridge 흐름을 설명하지 못했다.

반영 기준:

| 항목 | 반영 내용 |
| --- | --- |
| 신규 경로 | `/api/v1/auth/cognito/session` 추가 |
| 기존 경로 | `/api/v1/auth/google`, `/api/v1/auth/kakao` legacy/deprecated 처리 |
| 보안 스킴 | `cognitoBearerAuth` 추가 |
| 세션 응답 | `/auth/me`, `/auth/session`, `/auth/logout` 응답 shape 정리 |
| Preferences | `selectedThemeIds` alias 추가 |
| Role enum | `R-USER`, `R-ADMIN`, `R-LOCAL-OPERATOR`, `R-DATA-PROVIDER` |

## 9.10 최종 정리

Cognito 도입의 핵심은 Google/Kakao 로그인을 백엔드가 직접 처리하는 구조에서 벗어나, Cognito가 인증을 담당하고 Lovv 백엔드는 Cognito claims를 서비스 사용자/session shape로 변환하는 것이다.

현재 방향:

- Google/Kakao 직접 로그인 API는 legacy로 유지한다.
- Cognito Hosted UI/OIDC가 Social Login을 담당한다.
- Lovv 백엔드는 `/api/v1/auth/cognito/session`으로 bridge 처리한다.
- API Gateway JWT Authorizer 연결은 후속 Task로 분리한다.
- Role은 Cognito Group과 Lovv DB scope 조합으로 처리한다.
- 프론트는 Cognito token 기반으로 session/me를 호출해 서비스 상태를 복구한다.

# 10. 발표용 트러블슈팅 요약 문구

중간발표에서 한 장으로 설명할 때는 다음 구조로 축약한다.

```text
이슈: 그래프DB가 필요해 보였지만 PoC 관계는 대부분 1~2-hop이었다.
판단: Neptune은 지금 넣으면 비용과 운영 복잡도가 먼저 커진다.
대응: 그래프DB 직접 도입 대신 Lambda로 유사 관계 탐색 기능을 구현한다.
구현: RDS JOIN, DynamoDB 인접 리스트, 사전계산 후보 테이블, Lambda 인메모리 그래프를 조합한다.
기준: 3-hop 이상 관계 탐색이나 실시간 그래프 쓰기가 병목이 되면 Neptune으로 승격한다.
```

# 11. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.3 | 2026-06-12 | llm팀 | 그래프DB 직접 도입 대신 Lambda 기반 관계 탐색 보조 기능 구현 예정으로 TS-01 방향 명확화 |
| v0.2 | 2026-06-12 | llm팀 | Cognito/Social Login 책임 경계, bridge session API, claims 검증, SAM route, logout, role scope, API 명세 반영 기준 추가 |
| v0.1 | 2026-06-12 | llm팀 | Neptune 도입 판단, KR 전처리, S3 vector index, HTML/PDF 산출물, 발표 HTML 검증 이슈를 트러블슈팅 문서로 초안화 |
