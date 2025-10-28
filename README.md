# ACS WebApp E2E 테스트

Python Playwright를 사용한 ACS WebApp의 End-to-End 테스트 프로젝트입니다.

## 설치 방법

### 1. Python 가상환경 생성 (권장)

```bash
# tests 디렉터리로 이동
cd tests

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 의존성 설치

```bash
# Python 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install
```

## 테스트 실행

### 웹 클라이언트 개발 서버 시작

테스트 실행 전에 웹 클라이언트가 실행 중이어야 합니다:

```bash
# 프로젝트 루트에서
npm run web-client:dev
```

기본적으로 `http://localhost:3000`에서 실행됩니다.

### 테스트 실행 명령어

#### 방법 1: uv 사용 (권장)

```bash
# tests-python 디렉터리로 이동
cd tests-python

# 모든 테스트 실행 (Headless 모드)
uv run pytest --browser chromium

# 브라우저를 보면서 테스트 실행 (Headed 모드)
uv run pytest --headed --browser chromium

# 특정 테스트 파일만 실행
uv run pytest e2e/access/location/test_location_simple.py --headed --browser chromium

# 특정 테스트 함수만 실행
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_1st_level_location_add_edit_delete --headed --browser chromium

# 마커로 테스트 필터링
uv run pytest -m location --headed --browser chromium     # 장소 관련 테스트만
uv run pytest -m auth --headed --browser chromium         # 인증 관련 테스트만

# 디버깅 모드 (느린 속도로 실행)
uv run pytest --headed --browser chromium --slowmo 1000
```

#### 방법 2: 가상환경 사용 (대안)

```bash
# 가상환경 활성화
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 테스트 실행
pytest --headed --browser chromium
```

#### 편의 스크립트 사용 (Windows)

```bash
# 자동으로 headed 모드로 실행
run-tests.bat
```

## 환경 변수 설정

`.env.test` 파일에서 테스트 환경 변수를 설정합니다:

```env
# 테스트 대상 URL
BASE_URL=http://localhost:3000

# 테스트 계정
TEST_USER_EMAIL=admin@test.com
TEST_USER_PASSWORD=test1234!

# 브라우저 설정
HEADLESS=false
SLOW_MO=100
```

## 프로젝트 구조

```
tests-python/
├── e2e/                                    # E2E 테스트
│   ├── conftest.py                        # 공통 픽스처 및 설정 (로그인 처리)
│   ├── auth/                              # 인증 테스트
│   │   └── signin/
│   │       └── test_signin.py
│   ├── access/                            # 출입 통제 관련 테스트
│   │   └── location/                      # 장소 관리 테스트
│   │       ├── test_location_simple.py    # 단순화된 계층 테스트
│   │       ├── backup/                    # 이전 복잡한 테스트 (백업)
│   │       └── README.md
│   ├── fixtures/                          # 테스트 데이터 및 헬퍼
│   └── helpers/                           # 유틸리티 함수
├── playwright-report/                     # 테스트 리포트
├── .env.test                              # 환경 변수
├── pytest.ini                             # pytest 설정
├── pyproject.toml                         # uv 프로젝트 설정
├── requirements.txt                       # Python 의존성
└── README.md
```

## 테스트 작성 가이드

### 기본 테스트 구조

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.location
class TestLocationFeature:
    """장소 관련 기능 테스트"""

    def test_something(self, goto_location_page):
        """테스트 설명"""
        page = goto_location_page()

        # 테스트 로직
        page.click('button:has-text("버튼")')

        # 검증
        expect(page.locator('text=성공')).to_be_visible()
```

### 사용 가능한 픽스처

- `page`: 인증된 페이지 객체
- `goto_location_page`: 장소 관리 페이지로 이동하는 헬퍼 함수
- `authenticated_context`: 인증된 브라우저 컨텍스트

### 마커 사용

```python
@pytest.mark.smoke      # 스모크 테스트
@pytest.mark.location   # 장소 관련
@pytest.mark.auth       # 인증 관련
@pytest.mark.slow       # 느린 테스트
```

## 디버깅

### 스크린샷

테스트 실패 시 자동으로 스크린샷이 `playwright-report/screenshots/`에 저장됩니다.

### 브라우저 보면서 실행

```bash
pytest --headed --slowmo 1000
```

### Playwright Inspector 사용

```bash
pytest --headed --browser chromium --browser-channel chrome -k test_name
```

## 주의사항

1. **테스트 계정**: `.env.test`의 테스트 계정이 실제로 존재하고 로그인 가능해야 합니다.
2. **웹 서버 실행**: 테스트 전에 웹 클라이언트가 실행 중이어야 합니다.
3. **포트 충돌**: 기본 포트 3000이 사용 중이면 `.env.test`의 `BASE_URL`을 수정하세요.

## 트러블슈팅

### Playwright 브라우저가 설치되지 않음

```bash
playwright install
```

### 로그인 실패

`.env.test`의 테스트 계정 정보를 확인하세요.

### 타임아웃 에러

`pytest.ini`의 타임아웃 설정을 늘리세요:

```ini
addopts =
    --timeout 60000
```

## 추가 리소스

- [Playwright Python 문서](https://playwright.dev/python/docs/intro)
- [pytest 문서](https://docs.pytest.org/)
