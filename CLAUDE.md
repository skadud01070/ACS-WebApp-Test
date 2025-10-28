# CLAUDE.md - E2E 테스트 아키텍처 가이드

이 문서는 ACS WebApp E2E 테스트 시스템의 아키텍처, 패턴, 그리고 새로운 기능 추가 시 참고할 가이드라인을 설명합니다.

## 목차
1. [아키텍처 개요](#아키텍처-개요)
2. [핵심 설계 패턴](#핵심-설계-패턴)
3. [프로젝트 구조](#프로젝트-구조)
4. [인증 시스템](#인증-시스템)
5. [테스트 작성 가이드](#테스트-작성-가이드)
6. [실행 환경](#실행-환경)
7. [트러블슈팅 패턴](#트러블슈팅-패턴)
8. [새 기능 추가 시 체크리스트](#새-기능-추가-시-체크리스트)

---

## 아키텍처 개요

### 기술 스택
- **테스트 프레임워크**: Playwright for Python (v1.55.0+)
- **테스트 러너**: pytest (v8.4.2+)
- **패키지 관리**: uv (권장) 또는 venv
- **브라우저**: Chromium (기본)
- **언어**: Python 3.11+

### 핵심 설계 원칙

```yaml
설계 원칙:
  1. Session-Scoped Authentication: 세션당 1회 로그인으로 성능 최적화
  2. Test Isolation: 각 테스트는 독립적이며 고유한 데이터 사용
  3. Headless-First: 기본 headless 실행, 실패 시 자동 artifact 수집
  4. Complete Cleanup: 모든 테스트는 생성한 데이터를 완전히 삭제
  5. Event-Driven Dialog Handling: page.on()으로 모든 다이얼로그 처리
```

### 실행 모드

**Headless 모드 (기본, 권장)**:
```bash
uv run pytest --browser chromium
```
- 브라우저 창 표시 안 함
- 빠른 실행 속도
- 실패 시에만 스크린샷/비디오 자동 저장
- CI/CD 환경에 적합

**Headed 모드 (디버깅용)**:
```bash
uv run pytest --headed --browser chromium
```
- 브라우저 창 표시
- 실행 과정 시각적 확인 가능
- 느린 실행: `--slowmo 1000` 옵션 추가 가능

---

## 핵심 설계 패턴

### 1. 세션 기반 인증 (Session-Scoped Authentication)

**위치**: `e2e/conftest.py:31-65`

**패턴**:
```python
@pytest.fixture(scope='session')
def authenticated_context(browser: Browser):
    """세션당 1회만 로그인, 모든 테스트에서 재사용"""
    context = browser.new_context(...)
    page = context.new_page()

    # 로그인 수행
    page.goto(f'{BASE_URL}signin')
    page.get_by_role("textbox", name="Enter your Login ID or Email").fill(TEST_USER_EMAIL)
    page.get_by_role("textbox", name="Password").fill(TEST_USER_PASSWORD)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_url(f'{BASE_URL}**', timeout=15000)

    storage = context.storage_state()
    page.close()

    yield context
    context.close()
```

**이점**:
- 테스트 세션당 1회만 로그인 → 수십 배 빠른 실행 속도
- 모든 테스트는 `authenticated_context`에서 파생된 페이지 사용
- 인증 상태는 세션 전체에서 공유

**사용 예**:
```python
@pytest.fixture
def page(authenticated_context: BrowserContext):
    """각 테스트는 인증된 컨텍스트에서 새 페이지 생성"""
    page = authenticated_context.new_page()
    page.goto(BASE_URL)
    yield page
    page.close()
```

### 2. 다이얼로그 자동 처리 (Event-Driven Dialog Handling)

**패턴**:
```python
def handle_dialog(dialog):
    """모든 확인창 자동 처리"""
    if "삭제" in dialog.message or "delete" in dialog.message.lower():
        dialog.accept()  # 삭제 확인 다이얼로그는 accept
    else:
        dialog.accept()  # 저장 확인 다이얼로그도 accept

page.on("dialog", handle_dialog)  # 모든 다이얼로그 처리
```

**주의사항**:
- `page.once("dialog", ...)` 사용 금지 → 첫 번째 다이얼로그만 처리됨
- `page.on("dialog", ...)` 사용 → 모든 다이얼로그 지속적으로 처리
- 테스트 시작 시 한 번만 등록하면 자동으로 모든 다이얼로그 처리

**왜 중요한가**:
- Playwright Codegen은 확인창을 감지하지 못함
- 수동으로 다이얼로그 핸들러 등록 필수
- 등록하지 않으면 테스트가 다이얼로그에서 멈춤

### 3. 테스트 격리 및 데이터 정리 (Test Isolation & Cleanup)

**패턴**:
```python
import time

def test_2_level_location_add_edit_delete(self, navigate_to_location):
    """2단 장소: 부모 생성 → 자식 추가/수정/삭제 → 부모 삭제"""
    page = navigate_to_location()

    # 다이얼로그 핸들러 등록
    page.on("dialog", handle_dialog)

    # 고유한 타임스탬프로 데이터 생성
    timestamp = int(time.time())
    parent_name = f'2단_부모_{timestamp}'
    child_name = f'2단_자식_{timestamp}'

    # 1. 부모 생성
    # ... 부모 추가 로직 ...

    # 2. 자식 추가/수정/삭제
    # ... 자식 추가/수정/삭제 로직 ...

    # 3. 부모 삭제 (완전한 정리)
    parent_treeitem = page.get_by_role("treeitem", name=parent_name)
    if parent_treeitem.is_visible():
        parent_treeitem.click()
        page.get_by_role("button", name="삭제").click()
        expect(page.get_by_role("treeitem", name=parent_name)).not_to_be_visible()
```

**핵심 원칙**:
1. **고유한 데이터**: `timestamp`로 테스트 간 충돌 방지
2. **완전한 정리**: 생성한 모든 데이터를 역순으로 삭제 (자식 → 부모)
3. **검증 포함**: 삭제 후 반드시 `not_to_be_visible()` 확인

### 4. 계층적 정리 패턴 (Hierarchical Cleanup)

**3단 계층 예시**:
```python
# 생성 순서: 1단 부모 → 2단 부모 → 3단 자식
# 삭제 순서: 3단 자식 → 2단 부모 → 1단 부모

# 1. 3단 자식 삭제
child_treeitem.click()
page.get_by_role("button", name="삭제").click()
expect(page.get_by_role("treeitem", name=child_name)).not_to_be_visible()

# 2. 2단 부모 삭제
parent2_treeitem = page.get_by_role("treeitem", name=parent2_name)
if parent2_treeitem.is_visible():
    parent2_treeitem.click()
    page.get_by_role("button", name="삭제").click()
    expect(page.get_by_role("treeitem", name=parent2_name)).not_to_be_visible()

# 3. 1단 부모 삭제
parent1_treeitem = page.get_by_role("treeitem", name=parent1_name)
if parent1_treeitem.is_visible():
    parent1_treeitem.click()
    page.get_by_role("button", name="삭제").click()
    expect(page.get_by_role("treeitem", name=parent1_name)).not_to_be_visible()
```

**왜 중요한가**:
- 데이터베이스 외래 키 제약 조건 준수
- 고아 데이터(orphaned data) 방지
- 다음 테스트 실행 시 깨끗한 상태 보장

---

## 프로젝트 구조

```
tests-python/
├── e2e/                                    # E2E 테스트 루트
│   ├── conftest.py                        # 공통 픽스처 (인증, 페이지)
│   ├── auth/                              # 인증 테스트
│   │   └── signin/
│   │       └── test_signin.py
│   ├── access/                            # 출입통제 기능 테스트
│   │   └── location/                      # 장소 관리
│   │       ├── test_location_simple.py    # 1단/2단/3단 장소 테스트
│   │       ├── test_dialog_check.py       # 다이얼로그 감지 테스트
│   │       ├── backup/                    # 이전 복잡한 테스트 백업
│   │       │   ├── test_location_add.py
│   │       │   ├── test_location_edit.py
│   │       │   └── test_location_delete.py
│   │       └── README.md
│   ├── fixtures/                          # 테스트 데이터 (필요 시)
│   └── helpers/                           # 유틸리티 함수 (필요 시)
├── test-results/                          # 실패 시 자동 생성
│   └── [test-name]/
│       ├── test-failed-1.png              # 스크린샷
│       ├── video.webm                      # 비디오
│       └── trace.zip                       # Playwright Trace
├── .env.test                              # 환경 변수
├── pytest.ini                             # pytest 설정
├── pyproject.toml                         # uv 프로젝트 설정
├── requirements.txt                       # Python 의존성
├── run-tests.bat                          # Windows 실행 스크립트
├── QUICK-START.md                         # 빠른 시작 가이드
├── TESTING-GUIDE.md                       # 상세 테스트 가이드
├── README.md                              # 프로젝트 개요
└── CLAUDE.md                              # 이 문서
```

### 파일별 역할

| 파일 | 역할 | 수정 빈도 |
|------|------|----------|
| `conftest.py` | 공통 픽스처, 인증, 브라우저 설정 | 낮음 |
| `pytest.ini` | pytest 설정, 마커, 출력 옵션 | 낮음 |
| `pyproject.toml` | uv 프로젝트 및 의존성 관리 | 낮음 |
| `.env.test` | 환경별 설정 (URL, 계정) | 중간 |
| `test_*.py` | 실제 테스트 케이스 | 높음 |
| `README.md` | 사용자 가이드 | 중간 |
| `CLAUDE.md` | 개발자 아키텍처 가이드 | 낮음 |

---

## 인증 시스템

### 인증 흐름

```
┌─────────────────────────────────────────────────────────┐
│ pytest 세션 시작                                         │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│ authenticated_context fixture (scope='session')         │
│ 1. 브라우저 컨텍스트 생성                               │
│ 2. /signin 페이지로 이동 (networkidle 대기)             │
│ 3. 폼 필드가 enabled 상태가 될 때까지 대기              │
│ 4. TEST_USER_EMAIL, TEST_USER_PASSWORD 입력             │
│ 5. Sign In 버튼 클릭                                     │
│ 6. URL 변경 확인 (signin 페이지 벗어남)                 │
│ 7. networkidle + 추가 안전 대기                          │
│ 8. storage_state() 저장                                  │
│ 9. 로그인 성공 메시지 출력                               │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│ page fixture (각 테스트마다)                            │
│ - authenticated_context에서 new_page() 생성             │
│ - 인증 상태 자동 공유                                    │
│ - 테스트 종료 시 page.close()                           │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│ navigate_to_location fixture                            │
│ - 메뉴를 통해 장소 관리 페이지로 이동                   │
│ - 테스트에 준비된 페이지 반환                           │
└─────────────────────────────────────────────────────────┘
```

### 로그인 안정성 개선사항 (2025-10-27 업데이트)

**위치**: `e2e/conftest.py:31-105`

**개선 내용**:

1. **폼 필드 준비 상태 확인**
```python
email_field = page.get_by_role("textbox", name="Enter your Login ID or Email")
email_field.wait_for(state='visible', timeout=10000)  # 보이기 대기
email_field.fill(TEST_USER_EMAIL)

# 버튼 클릭 전 추가 대기
sign_in_button.wait_for(state='visible', timeout=10000)
page.wait_for_timeout(500)  # 버튼 활성화를 위한 추가 대기
sign_in_button.click()
```
- React 앱의 동적 렌더링을 고려하여 각 필드가 실제로 보일 때까지 대기
- 버튼 클릭 전 500ms 추가 대기로 활성화 확보

2. **명확한 로그인 성공 검증**
```python
# URL 기반 검증 (더 안정적)
page.wait_for_url(lambda url: 'signin' not in url, timeout=20000)
```
- 특정 UI 요소 대신 URL 변경으로 검증
- 어떤 페이지로든 이동하면 성공으로 간주

3. **에러 핸들링 및 디버깅**
```python
except Exception as e:
    print(f"[ERROR] Login failed: {e}")  # Windows 콘솔 호환
    print(f"Current URL: {page.url}")
    page.screenshot(path='test-results/login-failure.png', full_page=True)
    print(f"Screenshot saved: test-results/login-failure.png")
    raise
```
- 로그인 실패 시 자동으로 스크린샷 저장
- 디버깅 정보 출력 (이모지 제거로 Windows 콘솔 호환)

4. **다층 대기 전략**
```python
# 1단계: networkidle 대기
page.goto(f'{BASE_URL}signin', wait_until='networkidle')

# 2단계: React 렌더링 대기
page.wait_for_timeout(1000)

# 3단계: 요소별 가시성 확인
email_field.wait_for(state='visible', timeout=10000)

# 4단계: 버튼 클릭 전 추가 대기
page.wait_for_timeout(500)

# 5단계: 로그인 후 페이지 안정화
page.wait_for_url(lambda url: 'signin' not in url, timeout=20000)
page.wait_for_load_state('networkidle', timeout=15000)
page.wait_for_timeout(2000)
```
- 네트워크 → React 렌더링 → 요소 가시성 → 버튼 활성화 → URL 전환 → 페이지 안정화
- 각 단계마다 충분한 타임아웃 설정 (총 ~20초)

### 환경 변수 (.env.test)

```env
# 테스트 대상 서버
BASE_URL=http://172.16.150.200:4021/

# 테스트 계정 (실제 존재하는 계정)
TEST_USER_EMAIL=superadmin
TEST_USER_PASSWORD=superadmin
```

**중요**:
- `TEST_USER_EMAIL`과 `TEST_USER_PASSWORD`는 실제 서버에 존재하는 계정이어야 함
- 권한이 충분한 계정 사용 (장소 추가/수정/삭제 권한 필요)

### 픽스처 체인

```python
# 1. 세션 스코프: 1회 로그인
authenticated_context (scope='session')
    ↓
# 2. 테스트 스코프: 각 테스트마다 새 페이지
page (scope='function')
    ↓
# 3. 헬퍼 픽스처: 특정 페이지로 이동
navigate_to_location (scope='function')
```

---

## 테스트 작성 가이드

### 기본 테스트 템플릿

```python
"""
[기능명] E2E 테스트
경로: (main)/[경로]
서버: http://172.16.150.200:4021/

테스트 구조:
- [테스트 케이스 1 설명]
- [테스트 케이스 2 설명]

사전조건: conftest.py의 authenticated_context fixture를 통해 자동으로 로그인됨
"""
import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.[마커명]  # 예: location, auth, device
class Test[기능명]:
    """
    [기능명] 테스트

    [상세 설명]
    """

    def test_[기능]_add_edit_delete(self, navigate_to_location):
        """
        [기능]: 추가 -> 수정 -> 삭제
        """
        page = navigate_to_location()

        # 모든 다이얼로그 자동 처리
        def handle_dialog(dialog):
            if "삭제" in dialog.message or "delete" in dialog.message.lower():
                dialog.accept()
            else:
                dialog.accept()

        page.on("dialog", handle_dialog)

        # 고유한 타임스탬프 생성
        timestamp = int(time.time())
        original_name = f'테스트_{timestamp}'
        edited_name = f'수정_{timestamp}'

        # === 추가 ===
        page.get_by_role("button", name="추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="이름").fill(original_name)
        # ... 필드 입력 ...

        page.get_by_role("button", name="저장").click()
        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 추가 확인
        expect(page.get_by_role("treeitem", name=original_name)).to_be_visible(timeout=5000)

        # === 수정 ===
        page.get_by_role("treeitem", name=original_name).click()
        page.wait_for_timeout(1000)

        edit_button = page.get_by_role("button", name="수정")
        if edit_button.is_visible():
            edit_button.click()
            page.wait_for_timeout(1000)

        name_field = page.get_by_role("textbox", name="이름")
        if name_field.is_visible():
            name_field.clear()
            name_field.fill(edited_name)
            page.get_by_role("button", name="저장").click()
            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 수정 확인
            expect(page.get_by_role("treeitem", name=edited_name)).to_be_visible(timeout=5000)

        # === 삭제 ===
        page.get_by_role("treeitem", name=edited_name).click()
        page.wait_for_timeout(1000)

        delete_button = page.get_by_role("button", name="삭제")
        if delete_button.is_visible():
            delete_button.click()
            page.wait_for_timeout(500)
            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 삭제 확인
            expect(page.get_by_role("treeitem", name=edited_name)).not_to_be_visible()
```

### 페이지 객체 선택자 패턴

Playwright는 사용자 중심 선택자를 권장합니다:

```python
# ✅ 권장: Role 기반 (접근성 향상)
page.get_by_role("button", name="장소 추가")
page.get_by_role("textbox", name="장소 이름")
page.get_by_role("treeitem", name="1층")

# ✅ 권장: 텍스트 기반
page.get_by_text("저장")
page.locator('text=성공적으로 저장되었습니다')

# ⚠️ 가능: CSS 선택자 (불가피한 경우만)
page.locator('.MuiButton-root')

# ❌ 비권장: XPath (유지보수 어려움)
page.locator('//div[@class="container"]//button')
```

### 대기 패턴

```python
# ✅ 네트워크가 안정될 때까지 대기
page.wait_for_load_state('networkidle', timeout=10000)

# ✅ 특정 시간 대기 (최소화)
page.wait_for_timeout(1000)  # 1초

# ✅ 요소가 나타날 때까지 대기
expect(page.get_by_role("button", name="저장")).to_be_visible(timeout=5000)

# ❌ 고정 대기는 최소화 (느린 실행)
time.sleep(5)  # 가능하면 피하기
```

### 검증 패턴

```python
# ✅ 요소 표시 확인
expect(page.get_by_role("treeitem", name=location_name)).to_be_visible()

# ✅ 요소 숨김 확인
expect(page.get_by_role("treeitem", name=location_name)).not_to_be_visible()

# ✅ 텍스트 확인
expect(page.locator('text=저장되었습니다')).to_be_visible()

# ✅ 개수 확인
expect(page.get_by_role("row")).to_have_count(5)

# ✅ URL 확인
page.wait_for_url(f'{BASE_URL}location', timeout=5000)
```

---

## 실행 환경

### pytest.ini 설정

```ini
[pytest]
# 테스트 파일 패턴
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 테스트 디렉터리
testpaths = e2e

# 출력 옵션
addopts =
    -v
    --tb=short
    --strict-markers
    --screenshot only-on-failure
    --video retain-on-failure
    --tracing retain-on-failure

# 마커 정의
markers =
    smoke: 핵심 기능 스모크 테스트
    location: 장소 관리 관련 테스트
    auth: 인증 관련 테스트
    slow: 실행 시간이 긴 테스트
```

**주요 옵션 설명**:
- `--screenshot only-on-failure`: 실패 시에만 스크린샷 저장
- `--video retain-on-failure`: 실패 시에만 비디오 유지
- `--tracing retain-on-failure`: 실패 시에만 트레이스 유지
- `-v`: 상세 출력 (verbose)
- `--tb=short`: 짧은 traceback

### 실행 명령어 참고

```bash
# 기본 실행 (headless, 실패 시 스크린샷/비디오 자동 저장)
uv run pytest --browser chromium

# 특정 마커만 실행
uv run pytest -m location --browser chromium
uv run pytest -m "location and not slow" --browser chromium

# 특정 테스트 클래스
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple --browser chromium

# 특정 테스트 메서드
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_2_level_location_add_edit_delete --browser chromium

# Headed 모드 (디버깅)
uv run pytest --headed --browser chromium

# 느린 실행 (동작 확인)
uv run pytest --headed --browser chromium --slowmo 1000

# 상세 출력 + print 문 표시
uv run pytest -v -s --browser chromium

# 실패한 테스트만 재실행
uv run pytest --lf --browser chromium
```

---

## 트러블슈팅 패턴

### 1. 로그인 실패

**증상 A: 타임아웃 에러**
```
TimeoutError: page.wait_for_url: Timeout 20000ms exceeded.
```

**원인**:
- 서버가 응답하지 않음
- 잘못된 계정 정보
- 네트워크 지연

**해결**:
1. `.env.test`의 계정 정보 확인 (실제 존재하는 계정인지)
2. 서버가 실행 중인지 확인 (`BASE_URL` 접속 가능한지)
3. 로그인 페이지에 수동으로 접속하여 계정 테스트
4. `test-results/login-failure.png` 스크린샷 확인

**증상 B: 간헐적 실패**
```
로그인이 때때로 실패함 (재실행하면 성공)
```

**원인**:
- React 앱의 비동기 렌더링으로 인한 타이밍 이슈
- 폼 필드가 아직 활성화되지 않음
- 네트워크 불안정

**해결** (이미 적용됨 - `conftest.py:49-97`):
```python
# 각 요소가 보일 때까지 대기
email_field.wait_for(state='visible', timeout=10000)

# 버튼 클릭 전 추가 대기로 활성화 확보
page.wait_for_timeout(500)

# URL 기반 로그인 성공 검증
page.wait_for_url(lambda url: 'signin' not in url, timeout=20000)
```
- 요소 가시성 확인 후 버튼 활성화를 위한 추가 대기 시간 확보
- 로그인 성공을 URL 변경으로 검증 (더 안정적)
- 다층 대기 전략으로 타이밍 이슈 해결

**디버깅**:
```bash
# Headed 모드로 로그인 과정 직접 확인
uv run pytest e2e/auth/ --headed --browser chromium -s

# 로그인 실패 시 자동 저장되는 스크린샷 확인
cat test-results/login-failure.png
```

### 2. 다이얼로그 감지 안 됨

**증상**:
- 테스트가 확인창에서 멈춤
- `TimeoutError`

**해결**:
```python
# ❌ 잘못된 방법
page.once("dialog", lambda dialog: dialog.accept())  # 첫 번째만 처리

# ✅ 올바른 방법
def handle_dialog(dialog):
    dialog.accept()
page.on("dialog", handle_dialog)  # 모든 다이얼로그 처리
```

### 3. 요소를 찾을 수 없음

**증상**:
```
TimeoutError: locator.click: Timeout 30000ms exceeded.
```

**해결**:
1. Headed 모드로 실행하여 실제 UI 확인
2. 선택자가 정확한지 확인 (대소문자, 공백 주의)
3. 페이지 로딩 대기 추가: `page.wait_for_load_state('networkidle')`
4. 요소가 나타날 때까지 대기 시간 증가: `timeout=10000`

### 4. 타임스탬프 충돌

**증상**:
- "이미 존재하는 데이터" 에러

**해결**:
```python
import time

# ✅ 각 테스트에서 고유한 타임스탬프 생성
timestamp = int(time.time())
name = f'테스트_{timestamp}'

# ✅ 필요 시 랜덤 추가
import random
name = f'테스트_{timestamp}_{random.randint(1000, 9999)}'
```

### 5. 브라우저 설치 안 됨

**증상**:
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**해결**:
```bash
# uv 사용 시
uv run playwright install chromium

# venv 사용 시
playwright install chromium
```

---

## 새 기능 추가 시 체크리스트

### 1. 테스트 파일 생성

```bash
# 경로: e2e/[카테고리]/[기능명]/test_[기능명]_simple.py
# 예시: e2e/access/device/test_device_simple.py
```

**템플릿**:
```python
"""
[기능명] E2E 테스트
경로: (main)/[경로]
서버: http://172.16.150.200:4021/

테스트 구조:
- 기본 CRUD: 추가 -> 수정 -> 삭제

사전조건: conftest.py의 authenticated_context fixture를 통해 자동으로 로그인됨
"""
import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.[기능명]
class Test[기능명]Simple:
    """[기능명] 단순 테스트"""

    def test_basic_crud(self, navigate_to_[기능명]):
        """기본 CRUD: 추가 -> 수정 -> 삭제"""
        page = navigate_to_[기능명]()

        # 다이얼로그 핸들러
        def handle_dialog(dialog):
            if "삭제" in dialog.message or "delete" in dialog.message.lower():
                dialog.accept()
            else:
                dialog.accept()
        page.on("dialog", handle_dialog)

        timestamp = int(time.time())
        # ... 테스트 로직 ...
```

### 2. 필요 시 픽스처 추가 (conftest.py)

```python
@pytest.fixture
def navigate_to_[기능명](page: Page):
    """[기능명] 페이지로 이동하는 헬퍼 픽스처"""
    def _navigate():
        page.get_by_role("button", name="[메뉴]").click()
        page.wait_for_timeout(500)
        page.get_by_role("button", name="[하위메뉴]").click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state('networkidle')
        return page
    return _navigate
```

### 3. 마커 등록 (pytest.ini)

```ini
markers =
    [기능명]: [기능명] 관련 테스트  # 추가
```

### 4. 문서 작성

**README.md 생성** (`e2e/[카테고리]/[기능명]/README.md`):
```markdown
# [기능명] 테스트 가이드

## 개요
[기능 설명]

## 테스트 실행
\`\`\`bash
uv run pytest e2e/[카테고리]/[기능명]/ --browser chromium
\`\`\`

## 테스트 구조
- test_basic_crud: 기본 추가/수정/삭제
```

### 5. 실행 및 검증

```bash
# 1. Headed 모드로 실행하여 동작 확인
uv run pytest e2e/[카테고리]/[기능명]/ --headed --browser chromium

# 2. Headless 모드로 최종 확인
uv run pytest e2e/[카테고리]/[기능명]/ --browser chromium

# 3. 전체 테스트 실행하여 영향 확인
uv run pytest --browser chromium
```

### 6. 문서 업데이트

- `tests-python/README.md`: 프로젝트 구조에 새 기능 추가
- `tests-python/TESTING-GUIDE.md`: 실행 명령어 예시 추가
- 필요 시 `QUICK-START.md` 업데이트

---

## 베스트 프랙티스 요약

### DO (권장)

✅ **Session-scoped authentication 사용**
```python
@pytest.fixture(scope='session')
def authenticated_context(browser: Browser):
    # 세션당 1회만 로그인
```

✅ **page.on() for dialog handling**
```python
page.on("dialog", lambda dialog: dialog.accept())
```

✅ **Headless 기본, 실패 시 artifact 자동 수집**
```ini
--screenshot only-on-failure
--video retain-on-failure
```

✅ **고유한 타임스탬프로 데이터 격리**
```python
timestamp = int(time.time())
name = f'테스트_{timestamp}'
```

✅ **완전한 데이터 정리 (역순 삭제)**
```python
# 자식 삭제 → 부모 삭제
```

✅ **Role 기반 선택자 사용**
```python
page.get_by_role("button", name="저장")
```

### DON'T (비권장)

❌ **각 테스트마다 로그인**
```python
# 느림, 불필요
def test_something(self, page):
    page.goto('/signin')
    # ...
```

❌ **page.once() for dialogs**
```python
# 첫 번째 다이얼로그만 처리됨
page.once("dialog", ...)
```

❌ **수동 스크린샷 저장**
```python
# pytest.ini에서 자동 처리됨
page.screenshot(path='screenshot.png')
```

❌ **고정된 데이터 이름**
```python
# 테스트 충돌 발생
name = '테스트장소'
```

❌ **불완전한 정리**
```python
# 부모만 삭제하고 자식 남김 → 외래 키 에러
```

❌ **XPath 남용**
```python
# 유지보수 어려움
page.locator('//div[@class="..."]')
```

---

## 참고 자료

### 공식 문서
- [Playwright Python 문서](https://playwright.dev/python/docs/intro)
- [pytest 문서](https://docs.pytest.org/)
- [uv 문서](https://github.com/astral-sh/uv)

### 프로젝트 내 문서
- `QUICK-START.md`: 1분 안에 테스트 실행하기
- `TESTING-GUIDE.md`: 상세 테스트 실행 가이드
- `e2e/access/location/README.md`: Location 테스트 상세 가이드
- `README.md`: 프로젝트 개요 및 설치

### 주요 파일 위치
- 인증 로직: `e2e/conftest.py:31-65`
- pytest 설정: `pytest.ini`
- 환경 변수: `.env.test`
- Location 테스트 예시: `e2e/access/location/test_location_simple.py`

---

## 마지막 업데이트

- **날짜**: 2025-10-27
- **버전**: Playwright 1.55.0+, pytest 8.4.2+
- **주요 변경사항**:
  - Session-scoped authentication 패턴 적용
  - Headless-first 실행 모드 설정
  - Dialog handling 패턴 개선 (page.on 사용)
  - 계층적 데이터 정리 패턴 추가
  - 실패 시 자동 artifact 수집 설정
