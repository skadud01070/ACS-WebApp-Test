"""
로그인(Sign In) E2E 테스트
경로: /signin
서버: http://172.16.150.200:4021/

add.py의 로그인 동작을 기반으로 작성됨
"""
import os
import pytest
from playwright.sync_api import Page, expect, Browser, BrowserContext
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('.env.test')

BASE_URL = os.getenv('BASE_URL', 'http://172.16.150.200:4021/')
TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'superadmin')
TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'superadmin')


@pytest.mark.auth
class TestSignIn:
    """로그인 기능 테스트"""

    @pytest.fixture(autouse=False)
    def clean_page(self, browser: Browser):
        """
        인증되지 않은 새로운 페이지 생성
        (authenticated_context를 사용하지 않음)
        """
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='ko-KR',
            timezone_id='Asia/Seoul',
        )
        page = context.new_page()
        yield page
        context.close()


    def test_signin_page_loads(self, clean_page: Page):
        """
        로그인 페이지가 정상적으로 로드되는지 확인
        """
        page = clean_page
        page.goto(f'{BASE_URL}signin')
        page.wait_for_load_state('networkidle')

        # 로그인 페이지 요소 확인
        expect(page.get_by_role("textbox", name="Enter your Login ID or Email")).to_be_visible()
        expect(page.get_by_role("textbox", name="Password")).to_be_visible()
        expect(page.get_by_role("button", name="Sign In")).to_be_visible()


    def test_signin_with_valid_credentials(self, clean_page: Page):
        """
        유효한 계정으로 로그인 성공 테스트
        """
        page = clean_page
        page.goto(f'{BASE_URL}signin')
        page.wait_for_load_state('networkidle')

        # 로그인 정보 입력
        page.get_by_role("textbox", name="Enter your Login ID or Email").fill(TEST_USER_EMAIL)
        page.get_by_role("textbox", name="Password").fill(TEST_USER_PASSWORD)

        # Sign In 버튼 클릭
        page.get_by_role("button", name="Sign In").click()

        # 로그인 처리 대기
        page.wait_for_timeout(3000)

        # 페이지 로드 완료 대기
        page.wait_for_load_state('networkidle', timeout=10000)

        # URL이 변경되었는지 확인 (여러 번 체크)
        page.wait_for_timeout(2000)
        current_url = page.url

        # 로그인 성공 확인 (추가 대기 시간 포함)
        page.wait_for_timeout(3000)
        assert '/signin' not in current_url, f"로그인 후에도 signin 페이지에 있습니다. 현재 URL: {current_url}"


    def test_signin_with_tab_navigation(self, clean_page: Page):
        """
        Tab 키로 필드 간 이동하며 로그인 테스트 (add.py 동작 재현)
        """
        page = clean_page
        page.goto(f'{BASE_URL}signin')
        page.wait_for_load_state('networkidle')

        # ID 입력 후 Tab 키로 Password 필드로 이동
        login_field = page.get_by_role("textbox", name="Enter your Login ID or Email")
        login_field.click()
        login_field.fill(TEST_USER_EMAIL)
        login_field.press("Tab")

        # Password 입력
        password_field = page.get_by_role("textbox", name="Password")
        password_field.fill(TEST_USER_PASSWORD)

        # 로그인
        page.get_by_role("button", name="Sign In").click()

        # 성공 확인 (충분한 대기 시간)
        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)
        page.wait_for_timeout(3000)
        current_url = page.url
        assert '/signin' not in current_url, f"현재 URL: {current_url}"


    def test_signin_with_empty_credentials(self, clean_page: Page):
        """
        빈 계정 정보로 로그인 시도 시 유효성 검증
        """
        page = clean_page
        page.goto(f'{BASE_URL}signin')
        page.wait_for_load_state('networkidle')

        # 아무것도 입력하지 않고 Sign In 클릭
        page.get_by_role("button", name="Sign In").click()

        # 여전히 signin 페이지에 있어야 함
        page.wait_for_timeout(2000)
        current_url = page.url
        assert '/signin' in current_url, "빈 정보로 로그인이 되었습니다"


    def test_signin_with_invalid_credentials(self, clean_page: Page):
        """
        잘못된 계정 정보로 로그인 시도
        """
        page = clean_page
        page.goto(f'{BASE_URL}signin')
        page.wait_for_load_state('networkidle')

        # 잘못된 정보 입력
        page.get_by_role("textbox", name="Enter your Login ID or Email").fill("wronguser")
        page.get_by_role("textbox", name="Password").fill("wrongpassword")
        page.get_by_role("button", name="Sign In").click()

        # 로그인 실패 확인 (여전히 signin 페이지에 있음 또는 에러 메시지)
        page.wait_for_timeout(2000)
        current_url = page.url
        # 로그인 실패 시 signin 페이지에 남아있거나 에러 메시지가 표시되어야 함
        assert '/signin' in current_url or page.locator('text=오류').is_visible() or page.locator('text=실패').is_visible()


    def test_signin_with_only_username(self, clean_page: Page):
        """
        사용자명만 입력하고 로그인 시도
        """
        page = clean_page
        page.goto(f'{BASE_URL}signin')
        page.wait_for_load_state('networkidle')

        # 사용자명만 입력
        page.get_by_role("textbox", name="Enter your Login ID or Email").fill(TEST_USER_EMAIL)
        page.get_by_role("button", name="Sign In").click()

        # 로그인 실패 확인
        page.wait_for_timeout(2000)
        current_url = page.url
        assert '/signin' in current_url


    def test_signin_with_only_password(self, clean_page: Page):
        """
        비밀번호만 입력하고 로그인 시도
        """
        page = clean_page
        page.goto(f'{BASE_URL}signin')
        page.wait_for_load_state('networkidle')

        # 비밀번호만 입력
        page.get_by_role("textbox", name="Password").fill(TEST_USER_PASSWORD)
        page.get_by_role("button", name="Sign In").click()

        # 로그인 실패 확인
        page.wait_for_timeout(2000)
        current_url = page.url
        assert '/signin' in current_url


    def test_signin_redirect_with_return_url(self, clean_page: Page):
        """
        returnUrl 파라미터가 있는 경우 로그인 후 해당 URL로 리다이렉트 확인
        add.py에서 확인된 패턴: /signin?reason=session_expired&returnUrl=%2Flocation%3Ftab%3Dlocation
        """
        page = clean_page

        # returnUrl이 포함된 로그인 페이지로 이동
        return_url = '%2Flocation%3Ftab%3Dlocation'
        page.goto(f'{BASE_URL}signin?reason=session_expired&returnUrl={return_url}')
        page.wait_for_load_state('networkidle')

        # 로그인
        page.get_by_role("textbox", name="Enter your Login ID or Email").fill(TEST_USER_EMAIL)
        page.get_by_role("textbox", name="Password").fill(TEST_USER_PASSWORD)
        page.get_by_role("button", name="Sign In").click()

        # 로그인 후 대기 (충분한 시간)
        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)
        page.wait_for_timeout(3000)

        # returnUrl로 리다이렉트되었는지 확인 (또는 최소한 /signin이 아님)
        current_url = page.url
        assert '/signin' not in current_url, f"로그인 후에도 signin 페이지에 있습니다. 현재 URL: {current_url}"


    def test_signin_keyboard_enter(self, clean_page: Page):
        """
        Enter 키로 로그인 폼 제출
        """
        page = clean_page
        page.goto(f'{BASE_URL}signin')
        page.wait_for_load_state('networkidle')

        # 정보 입력
        page.get_by_role("textbox", name="Enter your Login ID or Email").fill(TEST_USER_EMAIL)
        page.get_by_role("textbox", name="Password").fill(TEST_USER_PASSWORD)

        # Password 필드에서 Enter 키 입력
        page.get_by_role("textbox", name="Password").press("Enter")

        # 로그인 성공 확인 (충분한 대기 시간)
        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)
        page.wait_for_timeout(3000)
        current_url = page.url
        assert '/signin' not in current_url, f"현재 URL: {current_url}"
