# 9. 운영·검토 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/admin/data-submissions` | Admin/Operator | 데이터 제안 목록 |
| POST | `/admin/data-submissions` | Operator/DataProvider | 데이터 제안 등록 |
| PATCH | `/admin/data-submissions/{submissionId}/review` | Admin | 승인, 반려, 수정 요청 |
| GET | `/admin/audit-logs` | Admin | 검토·승인 이력 조회 |
