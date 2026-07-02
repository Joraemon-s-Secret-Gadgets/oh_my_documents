# 5. 검증 명령

HTML 문서 구조 검증:

```powershell
python scripts\generate_pages.py
python scripts\verify_pages_structure.py
```

관리자 보안·로컬 DB 문서 정합성 검증:

```powershell
rg -n "001_product_api_tables|전역 MFA|global MFA|MFA 게이트|MFA gate|admin.*MFA.*필수" docs\01_requirements docs\04_database_design docs\07_api_spec docs\09_ui_ux_guide docs\10_test_plan
git diff --check
```

BE 저장소에서 확인할 관리자 보안 테스트:

```powershell
$env:PYTHONPATH='src'
python -m unittest
python -m unittest tests.test_admin_high_risk_app
python -m unittest tests.test_admin_mfa_app.AdminMfaAppTest.test_admin_read_routes_need_role_only_and_mfa_status_is_accessible
```

admin_web 저장소에서 확인할 프론트 검증:

```powershell
npm.cmd run lint
npm.cmd test
npm.cmd run build
```

opt-in 실DB 통합 테스트는 일반 unittest에서 skip되는 별도 검증이다. 실행하지 않았다면 완료로 표기하지 않는다.

```powershell
$env:RUN_ADMIN_DB_INTEGRATION='1'
$env:RUN_RDS_DATA_API_INTEGRATION='1'
python -m unittest
```

`docker compose config`는 compose 파일이 있는 BE/admin_web 작업 폴더에서 실행한다. 이 문서 저장소에 compose 파일이 없으면 실행 불가로 구분 기록한다.

PDF 문서 검증:

```powershell
cd pdf
xelatex -interaction=nonstopmode -halt-on-error <target>.tex
xelatex -interaction=nonstopmode -halt-on-error <target>.tex
```
