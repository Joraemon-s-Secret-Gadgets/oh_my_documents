# Agent Instructions for 13_system_architecture

이 폴더는 Lovv 시스템 아키텍처와 구성도를 번호가 부여된 대표 문서로 관리한다.

## Source of Truth

- 대표 문서는 `docs/13_system_architecture/13_system_architecture.md`다.
- AWS 현재 상태는 live 조회 결과를 우선하고, 기존 운영 문서인 `docs/11_deployment_ops/supplemental/current_aws_system_architecture.md`는 과거 스냅샷 또는 비교 기준으로 사용한다.
- 서비스/API/DB/Agent 세부 계약은 각 상세 문서와 실제 배포 상태가 충돌할 때 실제 배포 상태를 먼저 확인한 뒤 문서에 반영한다.

## Editing Rules

- 실제 secret 값, OAuth client secret, token, raw Lambda environment dump는 문서에 기록하지 않는다.
- AWS 리소스 식별자는 운영 이해에 필요한 범위에서만 기록하고, credential 값은 관리 방식만 설명한다.
- Mermaid 구성도는 Markdown 안에 inline block으로 유지할 수 있다. 사용자가 이미지 생성을 요청하면 같은 폴더에 SVG/PNG 구성도 산출물을 추가하고 대표 문서에서 참조한다.
- 현재 상태를 바꾸는 AWS 배포, 테이블 쓰기, 코드 변경은 이 문서 작업 범위에 포함하지 않는다.
