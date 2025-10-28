# 🚀 빠른 시작 가이드

장소추가 E2E 테스트를 5분 안에 실행하는 가이드입니다.

## ⚡ 한 번에 실행 (Windows)

```bash
# 1. tests 디렉터리로 이동
cd tests

# 2. 환경 설정 및 설치 (최초 1회)
setup.bat

# 3. 웹 클라이언트 시작 (별도 터미널)
cd ../apps/web-client
npm run dev

# 4. 테스트 실행
cd ../../tests
run-tests.bat
```

## 📝 단계별 상세 가이드

### 1️⃣ 환경 설정 (최초 1회만)

```bash
cd tests
setup.bat
```

이 스크립트가 자동으로:
- ✅ Python 가상환경 생성
- ✅ 필요한 패키지 설치 (Playwright, pytest 등)
- ✅ Chromium 브라우저 설치

**소요 시간**: 약 2-3분

### 2️⃣ 테스트 계정 설정

`.env.test` 파일을 열고 테스트 계정 정보를 확인합니다:

```env
TEST_USER_EMAIL=admin@test.com
TEST_USER_PASSWORD=test1234!
```

이 계정이 웹 애플리케이션에 존재하고 로그인 가능한지 확인하세요.

### 3️⃣ 웹 클라이언트 시작

**새 터미널 창을 열고** 다음 명령어를 실행:

```bash
cd apps/web-client
npm run dev
```

웹 서버가 `http://localhost:3000`에서 실행됩니다.
브라우저로 접속하여 정상 작동하는지 확인하세요.

### 4️⃣ 테스트 실행

**원래 터미널**에서:

```bash
cd tests
run-tests.bat
```

또는 수동으로:

```bash
# 가상환경 활성화
venv\Scripts\activate

# 테스트 실행
pytest --headed
```

## 🎯 첫 테스트 결과 확인

테스트가 실행되면:

1. ✅ Chromium 브라우저가 자동으로 열립니다
2. ✅ 자동으로 로그인이 수행됩니다
3. ✅ 장소 관리 페이지로 이동합니다
4. ✅ 장소 추가 폼을 테스트합니다
5. ✅ 결과가 터미널에 출력됩니다

### 성공 예시

```
====================================== test session starts ======================================
collected 8 items

e2e/location/test_location_add.py::TestLocationAdd::test_navigate_to_location_page PASSED
e2e/location/test_location_add.py::TestLocationAdd::test_open_location_add_form PASSED
e2e/location/test_location_add.py::TestLocationAdd::test_add_location_with_required_fields PASSED
...

====================================== 8 passed in 45.23s =======================================
```

## 🛠️ 다양한 실행 방법

### 브라우저를 숨기고 실행 (빠른 실행)

```bash
pytest
```

### 브라우저를 보면서 실행

```bash
pytest --headed
```

### 천천히 실행 (디버깅용)

```bash
pytest --headed --slowmo 1000
```

### 특정 테스트만 실행

```bash
# 장소추가 테스트만
pytest e2e/location/test_location_add.py

# 특정 함수만
pytest e2e/location/test_location_add.py::TestLocationAdd::test_add_location_with_required_fields
```

### 마커로 필터링

```bash
# 장소 관련 테스트만
pytest -m location

# 스모크 테스트만
pytest -m smoke
```

## 📊 테스트 리포트 확인

테스트 실행 후:

- **HTML 리포트**: `playwright-report/index.html` 브라우저로 열기
- **스크린샷**: 실패한 테스트의 스크린샷은 `playwright-report/screenshots/`

## ❓ 문제 해결

### 웹 서버가 실행되지 않음

```bash
cd apps/web-client
npm install
npm run dev
```

### 로그인 실패

1. `.env.test`의 계정 정보 확인
2. 브라우저에서 수동으로 로그인 시도
3. 로그인 URL 확인 (`http://localhost:3000/signin`)

### Playwright 브라우저 없음

```bash
venv\Scripts\activate
playwright install chromium
```

### 포트 3000이 사용 중

`.env.test` 수정:

```env
BASE_URL=http://localhost:다른포트
```

## 📚 다음 단계

1. **테스트 살펴보기**: `e2e/location/test_location_add.py` 파일 열어보기
2. **새 테스트 작성**: 기존 테스트를 참고하여 새로운 시나리오 추가
3. **자동 코드 생성**: `playwright codegen http://localhost:3000` 실행
4. **상세 가이드**: [README.md](README.md) 및 [INSTALL.md](INSTALL.md) 읽기

## 🎓 테스트 시나리오

현재 구현된 테스트:

- ✅ 장소 관리 페이지 접근
- ✅ 장소 추가 폼 열기
- ✅ 필수 필드로 장소 추가
- ✅ 모든 필드로 장소 추가
- ✅ 빈 장소명 유효성 검증
- ✅ 중복 장소명 유효성 검증
- ✅ 장소 추가 취소

## 💡 팁

- **빠른 개발**: `pytest --headed` 사용하여 브라우저 동작 확인
- **디버깅**: 테스트 코드에 `page.pause()` 추가하면 일시 정지
- **스크린샷**: 테스트 실패 시 자동으로 스크린샷 저장됨
- **병렬 실행**: `pytest -n auto` (pytest-xdist 설치 필요)

## 🎉 완료!

축하합니다! E2E 테스트 실행에 성공했습니다.

질문이나 문제가 있으면:
- [README.md](README.md) 참고
- [INSTALL.md](INSTALL.md) 트러블슈팅 섹션 참고
- 프로젝트 팀에 문의
