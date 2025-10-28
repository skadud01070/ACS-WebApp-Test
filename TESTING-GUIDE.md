# 테스트 실행 가이드

## 빠른 시작

### 1. uv 사용 (권장)

```bash
# tests-python 디렉터리로 이동
cd tests-python

# 모든 테스트 실행 (브라우저 표시)
uv run pytest --headed --browser chromium

# Location 테스트만 실행
uv run pytest -m location --headed --browser chromium
```

### 2. Windows 스크립트 사용

```bash
# tests-python 디렉터리에서
run-tests.bat
```

스크립트가 자동으로 uv 또는 venv를 감지하여 실행합니다.

## 테스트 종류

### Location (장소 관리) 테스트

단순화된 계층 구조 테스트 (완전한 생성/수정/삭제 라이프사이클):

```bash
# 1단 장소 테스트 (추가 -> 수정 -> 삭제)
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_1_level_location_add_edit_delete --headed

# 2단 장소 테스트 (부모 생성 -> 자식 추가 -> 수정 -> 삭제 -> 부모 삭제)
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_2_level_location_add_edit_delete --headed

# 3단 장소 테스트 (부모들 생성 -> 자식 추가 -> 수정 -> 삭제 -> 부모들 삭제)
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_3_level_location_add_edit_delete --headed

# Location 전체 테스트
uv run pytest -m location --headed
```

### Auth (인증) 테스트

```bash
# 로그인 테스트
uv run pytest -m auth --headed
```

## 실행 옵션

### 브라우저 제어

```bash
# 브라우저 숨김 (Headless 모드, 권장) - 실패 시에만 스크린샷/비디오 저장
uv run pytest --browser chromium

# 브라우저 표시 (Headed 모드) - 실행 과정 확인
uv run pytest --headed --browser chromium

# 느린 속도로 실행 (디버깅)
uv run pytest --headed --browser chromium --slowmo 1000

# 특정 테스트만 headless로 실행
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_2_level_location_add_edit_delete --browser chromium
```

### 스크린샷 및 비디오

기본 설정(`pytest.ini`)에서 자동으로 실패 시에만 저장됩니다:
- **스크린샷**: `test-results/` 디렉터리
- **비디오**: `test-results/` 디렉터리
- **트레이스**: `test-results/` 디렉터리

```bash
# 수동으로 스크린샷 옵션 변경
uv run pytest --screenshot on           # 항상 저장
uv run pytest --screenshot only-on-failure  # 실패 시만 (기본값)
uv run pytest --screenshot off          # 저장 안 함

# 비디오 옵션
uv run pytest --video on                # 항상 녹화
uv run pytest --video retain-on-failure # 실패 시만 (기본값)
uv run pytest --video off               # 녹화 안 함
```

### 출력 제어

```bash
# 상세 출력
uv run pytest -v --headed

# 매우 상세한 출력
uv run pytest -vv --headed

# 실패한 테스트만 재실행
uv run pytest --lf --headed
```

### 특정 테스트 실행

```bash
# 파일 단위
uv run pytest e2e/access/location/test_location_simple.py --headed

# 클래스 단위
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple --headed

# 메서드 단위
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_1st_level_location_add_edit_delete --headed
```

## 환경 설정

테스트 실행 전 `.env.test` 파일 확인:

```env
# 테스트 대상 서버
BASE_URL=http://172.16.150.200:4021/

# 테스트 계정 (실제 존재하는 계정)
TEST_USER_EMAIL=superadmin
TEST_USER_PASSWORD=superadmin
```

## 자동 로그인

모든 테스트는 자동으로 로그인된 상태에서 시작됩니다.

- **세션 기반 인증**: 테스트 세션당 한 번만 로그인
- **자동 공유**: 모든 테스트가 동일한 인증 컨텍스트 사용
- **설정 위치**: `e2e/conftest.py`의 `authenticated_context` fixture

## 결과 확인

### 테스트 리포트

```bash
# HTML 리포트 생성
uv run pytest --headed --html=report.html --self-contained-html
```

### 스크린샷

테스트 실패 시 자동으로 스크린샷 저장:
- 위치: `playwright-report/screenshots/`
- 파일명: `{테스트명}.png`

### 비디오 녹화

비디오 녹화 활성화:

```bash
# pytest.ini 또는 명령줄 옵션으로 설정
uv run pytest --headed --video=retain-on-failure
```

## 트러블슈팅

### uv가 없는 경우

```bash
# uv 설치
pip install uv

# 또는 가상환경 사용
venv\Scripts\activate  # Windows
pytest --headed --browser chromium
```

### 브라우저가 설치되지 않음

```bash
# 가상환경에서
playwright install

# 또는 uv 사용
uv run playwright install
```

### 로그인 실패

1. `.env.test`의 계정 정보 확인
2. 서버가 실행 중인지 확인 (`BASE_URL` 접속 가능한지)
3. 계정이 실제로 존재하는지 확인

### 타임아웃 에러

네트워크가 느린 경우 `pytest.ini`에서 타임아웃 증가:

```ini
[pytest]
timeout = 60000
```

## 추가 정보

- 전체 문서: `README.md`
- Location 테스트 가이드: `e2e/access/location/README.md`
- Playwright 문서: https://playwright.dev/python/
- pytest 문서: https://docs.pytest.org/
