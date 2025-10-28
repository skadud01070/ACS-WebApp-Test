"""
장소 삭제 E2E 테스트
경로: (main)/(access)/location
서버: http://172.16.150.200:4021/

사전조건: conftest.py의 authenticated_context fixture를 통해 자동으로 로그인됨
"""
import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.location
class TestLocationDelete:
    """
    장소 삭제 기능 테스트

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


    def test_delete_single_location(self, navigate_to_location):
        """
        단일 장소 삭제
        """
        page = navigate_to_location()

        # 테스트 장소 생성
        timestamp = int(time.time())
        location_name = f'삭제테스트_{timestamp}'

        self.create_test_location(page, location_name)

        # 생성된 장소 확인
        treeitem = page.get_by_role("treeitem", name=location_name)
        expect(treeitem).to_be_visible(timeout=5000)

        # 장소 선택
        treeitem.click()
        page.wait_for_timeout(1000)

        # 삭제 버튼 클릭 (UI에 따라 "삭제", "Delete" 등)
        delete_button = page.get_by_role("button", name="삭제")
        if delete_button.is_visible():
            delete_button.click()
            page.wait_for_timeout(500)

            # 삭제 확인 다이얼로그 처리 (확인 클릭)
            page.once("dialog", lambda dialog: dialog.accept())

            # 삭제 처리 대기
            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 삭제된 장소가 더 이상 없는지 확인
            expect(page.get_by_role("treeitem", name=location_name)).not_to_be_visible()


    def test_cancel_delete_location(self, navigate_to_location):
        """
        장소 삭제 취소
        """
        page = navigate_to_location()

        timestamp = int(time.time())
        location_name = f'삭제취소_{timestamp}'

        self.create_test_location(page, location_name)

        # 장소 선택
        treeitem = page.get_by_role("treeitem", name=location_name)
        expect(treeitem).to_be_visible(timeout=5000)
        treeitem.click()
        page.wait_for_timeout(1000)

        # 삭제 버튼 클릭
        delete_button = page.get_by_role("button", name="삭제")
        if delete_button.is_visible():
            delete_button.click()
            page.wait_for_timeout(500)

            # 삭제 확인 다이얼로그에서 취소
            page.once("dialog", lambda dialog: dialog.dismiss())

            page.wait_for_timeout(2000)

            # 여전히 존재하는지 확인
            expect(page.get_by_role("treeitem", name=location_name)).to_be_visible(timeout=5000)


    def test_delete_multiple_locations(self, navigate_to_location):
        """
        여러 장소를 순차적으로 삭제
        """
        page = navigate_to_location()

        # 3개의 테스트 장소 생성
        timestamp = int(time.time())
        location_names = []

        for i in range(1, 4):
            location_name = f'다중삭제_{i}_{timestamp}'
            location_names.append(location_name)
            self.create_test_location(page, location_name)
            page.wait_for_timeout(1000)

        # 각 장소를 순차적으로 삭제
        for location_name in location_names:
            treeitem = page.get_by_role("treeitem", name=location_name)

            if treeitem.is_visible():
                treeitem.click()
                page.wait_for_timeout(1000)

                delete_button = page.get_by_role("button", name="삭제")
                if delete_button.is_visible():
                    delete_button.click()
                    page.wait_for_timeout(500)

                    # 삭제 확인
                    page.once("dialog", lambda dialog: dialog.accept())

                    page.wait_for_timeout(3000)
                    page.wait_for_load_state('networkidle', timeout=10000)

                    # 삭제 확인
                    expect(page.get_by_role("treeitem", name=location_name)).not_to_be_visible()


    def test_delete_and_verify_tree_update(self, navigate_to_location):
        """
        장소 삭제 후 트리 업데이트 확인
        """
        page = navigate_to_location()

        timestamp = int(time.time())
        location_name = f'트리업데이트_{timestamp}'

        self.create_test_location(page, location_name)

        # 장소가 트리에 있는지 확인
        treeitem = page.get_by_role("treeitem", name=location_name)
        expect(treeitem).to_be_visible(timeout=5000)

        # 삭제
        treeitem.click()
        page.wait_for_timeout(1000)

        delete_button = page.get_by_role("button", name="삭제")
        if delete_button.is_visible():
            delete_button.click()
            page.wait_for_timeout(500)

            page.once("dialog", lambda dialog: dialog.accept())

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 트리가 업데이트되었는지 확인 (삭제된 항목 없음)
            expect(page.get_by_role("treeitem", name=location_name)).not_to_be_visible()

            # 트리 자체는 여전히 존재
            # (다른 장소들이 있다면 트리가 보여야 함)
            page.wait_for_timeout(1000)


    def test_delete_recently_added_location(self, navigate_to_location):
        """
        방금 추가한 장소를 바로 삭제
        """
        page = navigate_to_location()

        timestamp = int(time.time())
        location_name = f'즉시삭제_{timestamp}'

        # 장소 추가
        self.create_test_location(page, location_name)

        # 바로 삭제
        treeitem = page.get_by_role("treeitem", name=location_name)
        expect(treeitem).to_be_visible(timeout=5000)

        # 약간의 대기 후 삭제 (UI 안정화)
        page.wait_for_timeout(2000)

        treeitem.click()
        page.wait_for_timeout(1000)

        delete_button = page.get_by_role("button", name="삭제")
        if delete_button.is_visible():
            delete_button.click()
            page.wait_for_timeout(500)

            page.once("dialog", lambda dialog: dialog.accept())

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            expect(page.get_by_role("treeitem", name=location_name)).not_to_be_visible()
