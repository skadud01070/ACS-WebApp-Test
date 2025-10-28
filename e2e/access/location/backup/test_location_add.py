"""
장소 추가 E2E 테스트
경로: (main)/(access)/location
서버: http://172.16.150.200:4021/

add.py의 장소 추가 동작을 기반으로 작성됨

사전조건: conftest.py의 authenticated_context fixture를 통해 자동으로 로그인됨
"""
import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.location
class TestLocationAdd:
    """
    장소 추가 기능 테스트

    모든 테스트는 conftest.py의 authenticated_context를 통해
    자동으로 로그인된 상태에서 시작됩니다.
    """


    def test_location_page_loads(self, navigate_to_location):
        """
        장소 관리 페이지가 정상적으로 로드되는지 확인
        """
        page = navigate_to_location()

        # 장소 추가 버튼이 보이는지 확인
        expect(page.get_by_role("button", name="장소 추가")).to_be_visible(timeout=5000)


    def test_add_location_basic(self, navigate_to_location):
        """
        기본 필드로 장소 추가 (add.py 동작 재현)
        """
        page = navigate_to_location()

        # 고유한 장소명 생성
        timestamp = int(time.time())
        location_name = f'테스트장소_{timestamp}'

        # 장소 추가 버튼 클릭
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        # 필수 필드 입력
        page.get_by_role("textbox", name="장소 이름").fill(location_name)

        # 장소 타입 선택
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()

        # 표시 순서 입력
        page.get_by_role("spinbutton", name="표시 순서").fill("1")

        # 다이얼로그 처리
        page.once("dialog", lambda dialog: dialog.dismiss())

        # 저장 버튼 클릭
        page.get_by_role("button", name="저장").click()

        # 저장 후 충분히 대기
        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 트리에 추가된 장소 확인
        expect(page.get_by_role("treeitem", name=location_name)).to_be_visible(timeout=5000)


    def test_add_location_with_all_fields(self, navigate_to_location):
        """
        모든 필드를 입력하여 장소 추가
        """
        page = navigate_to_location()

        timestamp = int(time.time())
        location_name = f'완전한장소_{timestamp}'

        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        # 모든 필드 입력
        page.get_by_role("textbox", name="장소 이름").fill(location_name)

        # 장소 타입 선택
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()

        # 표시 순서
        page.get_by_role("spinbutton", name="표시 순서").fill("5")

        # 다이얼로그 처리 및 저장
        page.once("dialog", lambda dialog: dialog.dismiss())
        page.get_by_role("button", name="저장").click()

        # 충분한 대기
        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 검증
        expect(page.get_by_role("treeitem", name=location_name)).to_be_visible(timeout=5000)


    def test_add_location_different_type(self, navigate_to_location):
        """
        다른 장소 타입으로 추가
        """
        page = navigate_to_location()

        timestamp = int(time.time())
        location_name = f'회의실_{timestamp}'

        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(location_name)

        # 장소 타입 드롭다운 열기
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)

        # 사용 가능한 옵션 중 선택
        options = page.get_by_role("option").all()
        if len(options) > 0:
            # 첫 번째 옵션 선택
            options[0].click()

        page.get_by_role("spinbutton", name="표시 순서").fill("10")

        page.once("dialog", lambda dialog: dialog.dismiss())
        page.get_by_role("button", name="저장").click()

        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        expect(page.get_by_role("treeitem", name=location_name)).to_be_visible(timeout=5000)


    def test_add_multiple_locations(self, navigate_to_location):
        """
        여러 장소를 연속으로 추가
        """
        page = navigate_to_location()

        for i in range(1, 4):
            timestamp = int(time.time())
            location_name = f'연속_{i}_{timestamp}'

            page.get_by_role("button", name="장소 추가").click()
            page.wait_for_timeout(1000)

            page.get_by_role("textbox", name="장소 이름").fill(location_name)
            page.get_by_label("", exact=True).click()
            page.wait_for_timeout(500)
            page.get_by_role("option").first.click()
            page.get_by_role("spinbutton", name="표시 순서").fill(str(i))

            page.once("dialog", lambda dialog: dialog.dismiss())
            page.get_by_role("button", name="저장").click()

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            expect(page.get_by_role("treeitem", name=location_name)).to_be_visible(timeout=5000)

            # 다음 장소 추가를 위한 대기
            page.wait_for_timeout(1000)


    def test_add_location_empty_name(self, navigate_to_location):
        """
        빈 장소명으로 추가 시도 (유효성 검증)
        """
        page = navigate_to_location()

        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        # 장소 이름을 입력하지 않고 저장 시도
        page.get_by_role("spinbutton", name="표시 순서").fill("1")

        page.once("dialog", lambda dialog: dialog.dismiss())
        page.get_by_role("button", name="저장").click()

        page.wait_for_timeout(2000)

        # 저장이 실패하고 여전히 폼이 열려있는지 확인
        # (에러 메시지가 표시되거나 폼이 닫히지 않음)
        expect(page.get_by_role("textbox", name="장소 이름")).to_be_visible()


    def test_click_added_location(self, navigate_to_location):
        """
        추가한 장소를 트리에서 클릭하여 선택 (add.py 동작)
        """
        page = navigate_to_location()

        timestamp = int(time.time())
        location_name = f'클릭테스트_{timestamp}'

        # 장소 추가
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(location_name)
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()
        page.get_by_role("spinbutton", name="표시 순서").fill("99")

        page.once("dialog", lambda dialog: dialog.dismiss())
        page.get_by_role("button", name="저장").click()

        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 트리에서 장소 클릭 (add.py의 .locator("div").nth(2).click() 재현)
        treeitem = page.get_by_role("treeitem", name=location_name)
        expect(treeitem).to_be_visible(timeout=5000)

        treeitem.locator("div").nth(2).click()
        page.wait_for_timeout(1000)

        # 클릭 후에도 보이는지 확인
        expect(treeitem).to_be_visible()
