# E2E 테스트 설치 가이드

## 사전 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)
- Node.js (웹 클라이언트 실행용)

## 빠른 시작 (Windows)

### 1. 자동 설치

```bash
cd tests
setup.bat
```

이 스크립트는 다음을 자동으로 수행합니다:
- Python 가상환경 생성
- 의존성 설치
- Playwright 브라우저 설치

### 2. 테스트 실행

```bash
# 웹 클라이언트 시작 (별도 터미널)
cd apps/web-client
npm run dev

# 테스트 실행 (tests 디렉터리에서)
run-tests.bat
```

## 수동 설치 (Windows/Linux/Mac)

### 1단계: 가상환경 생성

```bash
cd tests

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2단계: 의존성 설치

```bash
pip install -r requirements.txt
```

설치되는 주요 패키지:
- `playwright`: 브라우저 자동화
- `pytest`: 테스트 프레임워크
- `pytest-playwright`: Playwright pytest 플러그인
- `python-dotenv`: 환경 변수 관리

### 3단계: Playwright 브라우저 설치

```bash
# Chromium만 설치 (권장)
playwright install chromium

# 모든 브라우저 설치
playwright install

# 시스템 의존성 포함 설치
playwright install --with-deps chromium
```

### 4단계: 환경 변수 설정

`.env.test` 파일을 확인하고 필요시 수정합니다:

```env
BASE_URL=http://localhost:3000
TEST_USER_EMAIL=admin@test.com
TEST_USER_PASSWORD=test1234!
```

### 5단계: 테스트 계정 준비

웹 애플리케이션에 `.env.test`에 설정된 테스트 계정이 존재하고 로그인 가능한지 확인합니다.

## 설치 확인

### Playwright 버전 확인

```bash
playwright --version
```

### pytest 버전 확인

```bash
pytest --version
```

### 설치된 브라우저 확인

```bash
playwright show-trace
```

## 테스트 실행 준비

### 1. 웹 클라이언트 시작

```bash
# 프로젝트 루트에서
cd apps/web-client
npm run dev
```

웹 서버가 `http://localhost:3000`에서 실행되어야 합니다.

### 2. 테스트 실행

```bash
# tests 디렉터리로 이동
cd tests

# 가상환경 활성화 (아직 활성화하지 않은 경우)
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 테스트 실행
pytest
```

### 테스트 실행 모드

```bash
# Headless 모드 (기본)
pytest

# Headed 모드 (브라우저 표시)
pytest --headed

# 느리게 실행 (디버깅)
pytest --headed --slowmo 1000

# 특정 테스트만 실행
pytest e2e/location/test_location_add.py

# 마커로 필터링
pytest -m location
```

## 트러블슈팅

### 문제: Python을 찾을 수 없음

**해결방법**: Python이 설치되어 있고 PATH에 추가되어 있는지 확인

```bash
python --version
```

### 문제: pip를 찾을 수 없음

**해결방법**: pip 재설치

```bash
python -m ensurepip --upgrade
```

### 문제: Playwright 브라우저 설치 실패

**해결방법**: 시스템 의존성 포함 설치

```bash
# Windows (관리자 권한)
playwright install --with-deps chromium

# Linux
sudo playwright install-deps
playwright install chromium

# Mac
playwright install chromium
```

### 문제: 로그인 실패

**해결방법**:
1. `.env.test`의 계정 정보 확인
2. 웹 애플리케이션에서 해당 계정으로 수동 로그인 가능한지 테스트
3. 로그인 페이지 URL이 올바른지 확인 (`/signin`)

### 문제: 웹 서버 연결 실패

**해결방법**:
1. 웹 클라이언트가 실행 중인지 확인
2. `.env.test`의 `BASE_URL`이 올바른지 확인
3. 포트 충돌 확인

### 문제: 타임아웃 에러

**해결방법**: `pytest.ini`에서 타임아웃 증가

```ini
[pytest]
addopts =
    --timeout 60000
```

### 문제: 가상환경 활성화 오류 (Windows PowerShell)

**해결방법**: 실행 정책 변경

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 다음 단계

설치가 완료되면:

1. [README.md](README.md)에서 테스트 작성 가이드 확인
2. 예제 테스트 실행 (`e2e/location/test_location_add.py`)
3. 새로운 테스트 작성 시작

## 추가 도구

### Playwright Codegen (테스트 자동 생성)

```bash
playwright codegen http://localhost:3000
```

브라우저가 열리고 사용자 액션을 기록하여 테스트 코드를 자동 생성합니다.

### Playwright Inspector (디버깅)

```bash
pytest --headed --browser chromium -k test_name
```

### VS Code 확장

- **Playwright Test for VSCode**: 테스트 실행 및 디버깅 지원

## 도움말

- Playwright Python: https://playwright.dev/python/
- pytest: https://docs.pytest.org/
- 프로젝트 이슈: GitHub Issues
