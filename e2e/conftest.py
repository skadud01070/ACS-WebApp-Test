"""
E2E 테스트 공통 설정 및 픽스처
"""
import os
import pytest
from playwright.sync_api import Page, BrowserContext, Browser
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('.env.test')

# 테스트 설정
BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')
TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'admin@test.com')
TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'test1234!')


@pytest.fixture(scope='session')
def browser_context_args(browser_context_args):
    """
    브라우저 컨텍스트 공통 설정
    """
    return {
        **browser_context_args,
        'viewport': {'width': 1920, 'height': 1080},
        'locale': 'ko-KR',
        'timezone_id': 'Asia/Seoul',
    }


@pytest.fixture(scope='session')
def authenticated_context(browser: Browser):
    """
    인증된 브라우저 컨텍스트 생성 (세션 전체에서 재사용)

    개선사항:
    - 폼 필드가 실제로 입력 가능한 상태일 때까지 대기
    - 로그인 성공 검증을 URL 변경으로 명확하게 처리
    - 각 단계마다 충분한 대기 시간 확보
    """
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='ko-KR',
        timezone_id='Asia/Seoul',
    )

    page = context.new_page()

    try:
        # 로그인 페이지로 이동 및 완전한 로딩 대기
        page.goto(f'{BASE_URL}signin', wait_until='networkidle')

        # 추가 대기: React 앱이 완전히 렌더링될 때까지
        page.wait_for_timeout(1000)

        # 로그인 폼 필드가 실제로 보일 때까지 대기 후 입력
        email_field = page.get_by_role("textbox", name="Enter your Login ID or Email")
        email_field.wait_for(state='visible', timeout=10000)
        email_field.fill(TEST_USER_EMAIL)

        password_field = page.get_by_role("textbox", name="Password")
        password_field.wait_for(state='visible', timeout=10000)
        password_field.fill(TEST_USER_PASSWORD)

        # 로그인 버튼이 보일 때까지 대기 후 클릭
        sign_in_button = page.get_by_role("button", name="Sign In")
        sign_in_button.wait_for(state='visible', timeout=10000)
        page.wait_for_timeout(500)  # 버튼 활성화를 위한 추가 대기
        sign_in_button.click()

        # 로그인 성공 확인: signin 페이지에서 벗어났는지 URL로 검증
        # 어떤 페이지로든 이동하면 성공으로 간주 (signin이 아니면 OK)
        page.wait_for_url(lambda url: 'signin' not in url, timeout=20000)

        # 페이지 로딩 완료 대기
        page.wait_for_load_state('networkidle', timeout=15000)

        # 추가 안전 대기: 메인 UI 요소 확인
        page.wait_for_timeout(2000)

        # 인증 상태 저장
        storage = context.storage_state()

        print(f"[OK] Login successful: {page.url}")

    except Exception as e:
        # 로그인 실패 시 디버깅 정보 출력 (Windows 콘솔 호환)
        print(f"[ERROR] Login failed: {e}")
        print(f"Current URL: {page.url}")

        # 실패 시 스크린샷 저장
        screenshot_path = 'test-results/login-failure.png'
        os.makedirs('test-results', exist_ok=True)
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved: {screenshot_path}")

        raise
    finally:
        page.close()

    yield context

    context.close()


@pytest.fixture
def page(authenticated_context: BrowserContext):
    """
    인증된 페이지 픽스처
    """
    page = authenticated_context.new_page()
    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')
    yield page
    page.close()


@pytest.fixture
def goto_location_page(page: Page):
    """
    장소 관리 페이지로 이동하는 헬퍼 픽스처
    직접 URL로 이동하거나 메뉴를 통해 이동
    """
    def _goto():
        page.goto(f'{BASE_URL}/location')
        page.wait_for_load_state('networkidle')
        return page

    return _goto


@pytest.fixture
def navigate_to_location(page: Page):
    """
    메인 페이지에서 장소 관리 페이지로 메뉴를 통해 이동하는 헬퍼 픽스처
    """
    def _navigate():
        page.get_by_role("button", name="출입 통합 관리").click()
        page.wait_for_timeout(500)
        page.get_by_role("button", name="장소 정보 관리").click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state('networkidle')
        return page

    return _navigate


@pytest.fixture
def take_screenshot(page: Page, request):
    """
    테스트 실패 시 자동 스크린샷
    """
    yield

    if request.node.rep_call.failed:
        screenshot_dir = 'playwright-report/screenshots'
        os.makedirs(screenshot_dir, exist_ok=True)

        screenshot_path = os.path.join(
            screenshot_dir,
            f'{request.node.name}.png'
        )
        page.screenshot(path=screenshot_path, full_page=True)
        print(f'스크린샷 저장: {screenshot_path}')


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    테스트 결과를 픽스처에서 접근할 수 있도록 저장
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f'rep_{rep.when}', rep)
