"""
장소 수정 E2E 테스트
경로: (main)/(access)/location
서버: http://172.16.150.200:4021/

사전조건: conftest.py의 authenticated_context fixture를 통해 자동으로 로그인됨
"""
import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.location
class TestLocationEdit:
    """
    장소 수정 기능 테스트

    모든 테스트는 conftest.py의 authenticated_context를 통해
    자동으로 로그인된 상태에서 시작됩니다.
    """

    def create_test_location(self, page: Page, location_name: str):
        """테스트용 장소 생성 헬퍼"""
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(location_name)
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()
        page.get_by_role("spinbutton", name="표시 순서").fill("1")

        page.once("dialog", lambda dialog: dialog.dismiss())
        page.get_by_role("button", name="저장").click()

        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)


    def test_edit_location_name(self, navigate_to_location):
        """
        장소 이름 수정
        """
        page = navigate_to_location()

        # 테스트 장소 생성
        timestamp = int(time.time())
        original_name = f'수정전_{timestamp}'
        new_name = f'수정후_{timestamp}'

        self.create_test_location(page, original_name)

        # 생성된 장소 선택
        treeitem = page.get_by_role("treeitem", name=original_name)
        expect(treeitem).to_be_visible(timeout=5000)
        treeitem.click()
        page.wait_for_timeout(1000)

        # 수정 버튼 찾기 (UI에 따라 다를 수 있음)
        # 가능한 선택자: "수정", "편집", "Edit" 등
        edit_button = page.get_by_role("button", name="수정")
        if edit_button.is_visible():
            edit_button.click()
            page.wait_for_timeout(1000)

            # 장소 이름 변경
            name_field = page.get_by_role("textbox", name="장소 이름")
            name_field.clear()
            name_field.fill(new_name)

            # 저장
            page.once("dialog", lambda dialog: dialog.dismiss())
            page.get_by_role("button", name="저장").click()

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 변경된 이름으로 확인
            expect(page.get_by_role("treeitem", name=new_name)).to_be_visible(timeout=5000)


    def test_edit_location_type(self, navigate_to_location):
        """
        장소 타입 수정
        """
        page = navigate_to_location()

        timestamp = int(time.time())
        location_name = f'타입수정_{timestamp}'

        self.create_test_location(page, location_name)

        # 장소 선택
        treeitem = page.get_by_role("treeitem", name=location_name)
        treeitem.click()
        page.wait_for_timeout(1000)

        # 수정 버튼 클릭
        edit_button = page.get_by_role("button", name="수정")
        if edit_button.is_visible():
            edit_button.click()
            page.wait_for_timeout(1000)

            # 장소 타입 변경
            page.get_by_label("", exact=True).click()
            page.wait_for_timeout(500)

            # 다른 타입 선택 (첫 번째 옵션)
            options = page.get_by_role("option").all()
            if len(options) > 1:
                options[1].click()  # 두 번째 옵션 선택

            # 저장
            page.once("dialog", lambda dialog: dialog.dismiss())
            page.get_by_role("button", name="저장").click()

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 여전히 존재하는지 확인
            expect(page.get_by_role("treeitem", name=location_name)).to_be_visible(timeout=5000)


    def test_edit_location_display_order(self, navigate_to_location):
        """
        표시 순서 수정
        """
        page = navigate_to_location()

        timestamp = int(time.time())
        location_name = f'순서수정_{timestamp}'

        self.create_test_location(page, location_name)

        # 장소 선택
        treeitem = page.get_by_role("treeitem", name=location_name)
        treeitem.click()
        page.wait_for_timeout(1000)

        # 수정
        edit_button = page.get_by_role("button", name="수정")
        if edit_button.is_visible():
            edit_button.click()
            page.wait_for_timeout(1000)

            # 표시 순서 변경
            order_field = page.get_by_role("spinbutton", name="표시 순서")
            order_field.clear()
            order_field.fill("999")

            # 저장
            page.once("dialog", lambda dialog: dialog.dismiss())
            page.get_by_role("button", name="저장").click()

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            expect(page.get_by_role("treeitem", name=location_name)).to_be_visible(timeout=5000)


    def test_cancel_location_edit(self, navigate_to_location):
        """
        장소 수정 취소
        """
        page = navigate_to_location()

        timestamp = int(time.time())
        original_name = f'취소테스트_{timestamp}'

        self.create_test_location(page, original_name)

        # 장소 선택 및 수정 시작
        treeitem = page.get_by_role("treeitem", name=original_name)
        treeitem.click()
        page.wait_for_timeout(1000)

        edit_button = page.get_by_role("button", name="수정")
        if edit_button.is_visible():
            edit_button.click()
            page.wait_for_timeout(1000)

            # 일부 변경 시도
            name_field = page.get_by_role("textbox", name="장소 이름")
            name_field.clear()
            name_field.fill("변경취소될이름")

            # 취소 버튼 클릭
            cancel_button = page.get_by_role("button", name="취소")
            if cancel_button.is_visible():
                cancel_button.click()
                page.wait_for_timeout(1000)

                # 원래 이름이 그대로 있는지 확인
                expect(page.get_by_role("treeitem", name=original_name)).to_be_visible(timeout=5000)

                # 변경된 이름은 없어야 함
                expect(page.get_by_role("treeitem", name="변경취소될이름")).not_to_be_visible()


    def test_edit_multiple_fields(self, navigate_to_location):
        """
        여러 필드를 한 번에 수정
        """
        page = navigate_to_location()

        timestamp = int(time.time())
        original_name = f'다중수정_{timestamp}'
        new_name = f'다중수정완료_{timestamp}'

        self.create_test_location(page, original_name)

        # 장소 선택
        treeitem = page.get_by_role("treeitem", name=original_name)
        treeitem.click()
        page.wait_for_timeout(1000)

        edit_button = page.get_by_role("button", name="수정")
        if edit_button.is_visible():
            edit_button.click()
            page.wait_for_timeout(1000)

            # 이름 변경
            name_field = page.get_by_role("textbox", name="장소 이름")
            name_field.clear()
            name_field.fill(new_name)

            # 타입 변경
            page.get_by_label("", exact=True).click()
            page.wait_for_timeout(500)
            page.get_by_role("option").first.click()

            # 순서 변경
            order_field = page.get_by_role("spinbutton", name="표시 순서")
            order_field.clear()
            order_field.fill("88")

            # 저장
            page.once("dialog", lambda dialog: dialog.dismiss())
            page.get_by_role("button", name="저장").click()

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 변경된 이름으로 확인
            expect(page.get_by_role("treeitem", name=new_name)).to_be_visible(timeout=5000)
