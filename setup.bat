@echo off
REM E2E 테스트 환경 설정 스크립트 (Windows)

echo ====================================
echo ACS WebApp E2E 테스트 환경 설정
echo ====================================
echo.

REM Python 버전 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요.
    exit /b 1
)

echo [1/4] Python 가상환경 생성...
if exist venv (
    echo 가상환경이 이미 존재합니다.
) else (
    python -m venv venv
    echo 가상환경 생성 완료
)
echo.

echo [2/4] 가상환경 활성화...
call venv\Scripts\activate
echo.

echo [3/4] Python 패키지 설치...
pip install -r requirements.txt
echo.

echo [4/4] Playwright 브라우저 설치...
playwright install chromium
echo.

echo ====================================
echo 설치 완료!
echo ====================================
echo.
echo 테스트 실행 방법:
echo   1. 가상환경 활성화: venv\Scripts\activate
echo   2. 웹 서버 시작: cd .. ^&^& npm run web-client:dev
echo   3. 테스트 실행: pytest
echo.
pause
