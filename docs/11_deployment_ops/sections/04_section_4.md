# 4. 현재 우선 운영 항목

| 영역 | 현재 기준 |
| --- | --- |
| 인증·인가 | Cognito Hosted UI/OIDC가 Social Login을 담당하고 Lovv backend는 `/api/v1/auth/cognito/session` bridge로 세션 shape를 구성 |
| 데이터 적재 | KR 상세 데이터는 `TourKoreaDomainData` 기준 |
| 검색 인덱스 | S3 vector index `kr-tour-domain-v1` 구축 기준 수립 |
| 그래프DB | 현재 직접 도입하지 않고 Lambda 기반 관계 탐색 보조 기능으로 유사 기능 구현 예정. Neptune은 승격 기준 충족 시 재검토 |
| 문서 배포 | `docs/` Markdown 원본 → `pages/*.html` 생성 |
| PDF 배포 | 대응 Markdown 원본 → `pdf/*.tex`/`pdf/*.pdf` 생성 |
