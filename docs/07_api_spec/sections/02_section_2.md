# 2. 공통 오류 응답

| HTTP Status | Code | 의미 |
| --- | --- | --- |
| 400 | BAD_REQUEST | 요청 형식 오류 |
| 401 | UNAUTHENTICATED | 인증 필요 |
| 403 | FORBIDDEN | 권한 없음 |
| 404 | NOT_FOUND | 리소스 없음 |
| 409 | CONFLICT | 중복 또는 상태 충돌 |
| 422 | VALIDATION_ERROR | 의미상 유효하지 않은 요청 |
| 422 | AUTH_MAPPING_ERROR | Cognito 필수 claim은 있으나 Lovv 사용자/role 매핑이 불가능 |
| 500 | INTERNAL_ERROR | 서버 오류 |

`/admin/*` 운영·검토 API의 인가 실패는 본 공통 오류 응답 형식을 따르되, 세부 오류 코드는 `9.1 관리자 인가 규칙`의 관리자 인가 오류 코드 표준을 우선 적용한다.

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "여행 월은 1부터 12 사이여야 합니다.",
    "details": {
      "field": "travelMonth"
    }
  }
}
```
