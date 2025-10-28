@echo off
REM E2E 테스트 실행 스크립트 (Windows)

echo ====================================
echo ACS WebApp E2E 테스트 실행
echo ====================================
echo.

REM uv 설치 확인
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [경고] uv가 설치되지 않았습니다.
    echo uv를 사용하려면 다음 명령으로 설치하세요:
    echo   pip install uv
    echo.
    echo 가상환경 방식으로 실행합니다...

    REM 가상환경 확인
    if not exist venv (
        echo [오류] 가상환경이 없습니다.
        echo setup.bat를 먼저 실행해주세요.
        exit /b 1
    )

    REM 가상환경 활성화
    call venv\Scripts\activate

    REM 테스트 실행 (venv 방식)
    if "%~1"=="" (
        pytest --headed -v --browser chromium
    ) else (
        pytest %*
    )
) else (
    echo uv를 사용하여 테스트를 실행합니다...
    echo.

    REM 테스트 실행 (uv 방식)
    if "%~1"=="" (
        uv run pytest --headed -v --browser chromium
    ) else (
        uv run pytest %*
    )
)

echo.
echo 웹 서버가 실행 중인지 확인하세요:
echo - 로컬: http://localhost:3000
echo - 개발: http://172.16.150.200:4021
echo.

pause
