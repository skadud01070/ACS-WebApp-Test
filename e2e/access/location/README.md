# Location 테스트 가이드

## 개요

장소(Location) 관리 기능에 대한 E2E 테스트입니다.

### 자동 로그인 처리

모든 테스트는 `tests-python/e2e/conftest.py`의 `authenticated_context` fixture를 통해 **자동으로 로그인된 상태**에서 시작됩니다.

- **세션 기반 인증**: 한 번만 로그인하여 모든 테스트에서 재사용
- **테스트 격리**: 각 테스트는 독립적인 페이지를 받지만 동일한 인증 상태 공유
- **환경 설정**: `.env.test` 파일의 `TEST_USER_EMAIL`과 `TEST_USER_PASSWORD` 사용

## 테스트 파일

### test_location_simple.py
장소 계층 구조 테스트 (추가 -> 수정 -> 삭제 -> 부모 삭제)
- **1단 장소**: 추가 -> 수정 -> 삭제
- **2단 장소**: 부모 생성 -> 자식 추가 -> 수정 -> 삭제 -> 부모 삭제
- **3단 장소**: 1단/2단 부모 생성 -> 자식 추가 -> 수정 -> 삭제 -> 2단 부모 삭제 -> 1단 부모 삭제

각 테스트는 독립적으로 실행되며, 생성한 모든 데이터를 삭제하여 완전히 격리됩니다.

## 테스트 실행

### uv 사용 (권장)

```bash
cd tests-python

# Headless 모드 (백그라운드 실행, 실패 시에만 스크린샷/비디오 저장)
uv run pytest e2e/access/location/ --browser chromium

# Headed 모드 (브라우저 표시, 실행 과정 확인)
uv run pytest e2e/access/location/ --headed --browser chromium

# 마커로 실행
uv run pytest -m location --browser chromium
```

### 특정 테스트 메서드 실행

```bash
# 1단 장소 테스트만 (headless)
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_1_level_location_add_edit_delete --browser chromium

# 2단 장소 테스트만 (부모 삭제 포함, headless)
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_2_level_location_add_edit_delete --browser chromium

# 3단 장소 테스트만 (부모들 삭제 포함, headless)
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_3_level_location_add_edit_delete --browser chromium

# 브라우저를 보면서 실행하려면 --headed 추가
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_2_level_location_add_edit_delete --headed --browser chromium
```

### 디버깅 모드

```bash
# 느린 속도로 실행 (동작 관찰)
uv run pytest e2e/access/location/ --headed --browser chromium --slowmo 1000

# Headless 모드 (빠른 실행, 권장)
uv run pytest e2e/access/location/ --browser chromium
```

### 실패 시 스크린샷/비디오

기본 설정으로 실패 시 자동 저장됩니다:
- 위치: `tests-python/test-results/`
- 스크린샷: `.png` 파일
- 비디오: `.webm` 파일
- 트레이스: `.zip` 파일 (Playwright Trace Viewer로 분석 가능)

### 기존 venv 방식 (대안)

```bash
# 가상환경 활성화
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 테스트 실행
pytest e2e/access/location/ --headed --browser chromium
```

## 환경 설정

테스트 실행 전에 `.env.test` 파일을 확인하세요:

```env
# 테스트 대상 서버
BASE_URL=http://172.16.150.200:4021/

# 테스트 계정 (실제 존재하는 계정)
TEST_USER_EMAIL=superadmin
TEST_USER_PASSWORD=superadmin
```

## Fixture 사용법

### navigate_to_location
메인 페이지에서 메뉴를 통해 장소 관리 페이지로 이동합니다.

```python
def test_something(self, navigate_to_location):
    page = navigate_to_location()
    # 이제 장소 관리 페이지에 있음
    page.get_by_role("button", name="장소 추가").click()
```

### goto_location_page
URL을 통해 직접 장소 관리 페이지로 이동합니다.

```python
def test_something(self, goto_location_page):
    page = goto_location_page()
    # 바로 장소 관리 페이지로 이동
```

## 테스트 작성 가이드

### 테스트 구조 예시

```python
@pytest.mark.location
class TestLocationSimple:
    def test_1_level_location_add_edit_delete(self, navigate_to_location):
        """1단 장소: 추가 -> 수정 -> 삭제"""
        page = navigate_to_location()

        # 모든 다이얼로그 자동 처리
        def handle_dialog(dialog):
            if "삭제" in dialog.message or "delete" in dialog.message.lower():
                dialog.accept()
            else:
                dialog.accept()
        page.on("dialog", handle_dialog)

        # 고유한 이름 생성
        timestamp = int(time.time())
        original_name = f'1단_원본_{timestamp}'
        edited_name = f'1단_수정_{timestamp}'

        # 추가
        page.get_by_role("button", name="장소 추가").click()
        page.get_by_role("textbox", name="장소 이름").fill(original_name)
        # ... 필드 입력 ...
        page.get_by_role("button", name="저장").click()  # 다이얼로그 자동 처리
        expect(page.get_by_role("treeitem", name=original_name)).to_be_visible()

        # 수정
        treeitem.click()
        # ... 이름 변경 ...
        page.get_by_role("button", name="저장").click()  # 다이얼로그 자동 처리
        expect(page.get_by_role("treeitem", name=edited_name)).to_be_visible()

        # 삭제
        page.get_by_role("button", name="삭제").click()  # 다이얼로그 자동 처리
        expect(page.get_by_role("treeitem", name=edited_name)).not_to_be_visible()
```

### 주의사항

1. **고유한 이름 사용**: `timestamp`를 사용하여 테스트 간 충돌 방지
2. **적절한 대기**: `wait_for_timeout()`, `wait_for_load_state()` 사용
3. **다이얼로그 자동 처리**: `page.on("dialog", handle_dialog)`로 모든 확인창 자동 처리
4. **명확한 검증**: `expect()` 사용하여 결과 확인
5. **계층 구조**: 2단/3단 테스트는 부모 장소를 먼저 생성
6. **완전한 정리**: 각 테스트는 생성한 모든 장소를 삭제 (자식 → 부모 순)

## 트러블슈팅

### 로그인 실패
- `.env.test`의 계정 정보가 실제 서버에 존재하는지 확인
- 서버가 실행 중인지 확인 (`BASE_URL` 접속 가능한지)

### 타임아웃 에러
- 네트워크가 느린 경우 `timeout` 값 증가
- `wait_for_timeout()` 시간 조정

### 요소를 찾을 수 없음
- Playwright Inspector 사용: `pytest --headed --slowmo 1000`
- 스크린샷 확인: `playwright-report/screenshots/`

## 추가 정보

- 전체 테스트 가이드: `tests-python/README.md`
- Playwright 문서: https://playwright.dev/python/
- pytest 문서: https://docs.pytest.org/
