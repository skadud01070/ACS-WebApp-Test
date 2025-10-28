"""
장소 관리 단순 E2E 테스트
경로: (main)/(access)/location
서버: http://172.16.150.200:4021/

테스트 구조:
- 1단 장소: 추가 -> 수정 -> 삭제
- 2단 장소: 추가 -> 수정 -> 삭제
- 3단 장소: 추가 -> 수정 -> 삭제

사전조건: conftest.py의 authenticated_context fixture를 통해 자동으로 로그인됨
"""
import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.location
class TestLocationSimple:
    """
    장소 관리 단순 테스트

    1단, 2단, 3단 장소를 순차적으로 추가/수정/삭제
    """

    def test_1_level_location_add_edit_delete(self, navigate_to_location):
        """
        1단 장소: 추가 -> 수정 -> 삭제
        """
        page = navigate_to_location()

        # 모든 다이얼로그 자동 처리 (저장 시에는 dismiss, 삭제 시에는 accept)
        def handle_dialog(dialog):
            # 삭제 확인 다이얼로그는 accept, 나머지는 dismiss
            if "삭제" in dialog.message or "delete" in dialog.message.lower():
                dialog.accept()
            else:
                dialog.accept()  # 또는 dialog.dismiss() - 서버 동작에 따라 조정

        page.on("dialog", handle_dialog)

        timestamp = int(time.time())
        original_name = f'1단_원본_{timestamp}'
        edited_name = f'1단_수정_{timestamp}'

        # === 1단 장소 추가 ===
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(original_name)
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()
        page.get_by_role("spinbutton", name="표시 순서").fill("1")

        page.get_by_role("button", name="저장").click()

        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 추가 확인
        treeitem = page.get_by_role("treeitem", name=original_name)
        expect(treeitem).to_be_visible(timeout=5000)

        # === 1단 장소 수정 ===
        treeitem.click()
        page.wait_for_timeout(1000)

        # 수정 버튼이 있으면 클릭 (UI에 따라 다를 수 있음)
        edit_button = page.get_by_role("button", name="수정")
        if edit_button.is_visible():
            edit_button.click()
            page.wait_for_timeout(1000)

        # 이름 수정
        name_field = page.get_by_role("textbox", name="장소 이름")
        if name_field.is_visible():
            name_field.clear()
            name_field.fill(edited_name)

            page.get_by_role("button", name="저장").click()

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 수정 확인
            expect(page.get_by_role("treeitem", name=edited_name)).to_be_visible(timeout=5000)

        # === 1단 장소 삭제 ===
        treeitem_updated = page.get_by_role("treeitem", name=edited_name)
        treeitem_updated.click()
        page.wait_for_timeout(1000)

        delete_button = page.get_by_role("button", name="삭제")
        if delete_button.is_visible():
            delete_button.click()
            page.wait_for_timeout(500)

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 삭제 확인
            expect(page.get_by_role("treeitem", name=edited_name)).not_to_be_visible()


    def test_2_level_location_add_edit_delete(self, navigate_to_location):
        """
        2단 장소: 추가 -> 수정 -> 삭제 -> 부모 삭제

        사전조건: 1단 부모 장소가 필요함
        """
        page = navigate_to_location()

        # 모든 다이얼로그 자동 처리
        def handle_dialog(dialog):
            if "삭제" in dialog.message or "delete" in dialog.message.lower():
                dialog.accept()
            else:
                dialog.accept()

        page.on("dialog", handle_dialog)

        timestamp = int(time.time())
        parent_name = f'2단_부모_{timestamp}'
        original_name = f'2단_원본_{timestamp}'
        edited_name = f'2단_수정_{timestamp}'

        # === 1단 부모 장소 추가 ===
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(parent_name)
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()
        page.get_by_role("spinbutton", name="표시 순서").fill("10")

        page.get_by_role("button", name="저장").click()

        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 부모 장소 선택
        parent_treeitem = page.get_by_role("treeitem", name=parent_name)
        expect(parent_treeitem).to_be_visible(timeout=5000)
        parent_treeitem.click()
        page.wait_for_timeout(1000)

        # === 2단 자식 장소 추가 ===
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(original_name)
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()
        page.get_by_role("spinbutton", name="표시 순서").fill("1")

        page.get_by_role("button", name="저장").click()

        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 추가 확인
        child_treeitem = page.get_by_role("treeitem", name=original_name)
        expect(child_treeitem).to_be_visible(timeout=5000)

        # === 2단 장소 수정 ===
        child_treeitem.click()
        page.wait_for_timeout(1000)

        edit_button = page.get_by_role("button", name="수정")
        if edit_button.is_visible():
            edit_button.click()
            page.wait_for_timeout(1000)

        name_field = page.get_by_role("textbox", name="장소 이름")
        if name_field.is_visible():
            name_field.clear()
            name_field.fill(edited_name)

            page.get_by_role("button", name="저장").click()

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 수정 확인
            expect(page.get_by_role("treeitem", name=edited_name)).to_be_visible(timeout=5000)

        # === 2단 장소 삭제 ===
        child_treeitem_updated = page.get_by_role("treeitem", name=edited_name)
        child_treeitem_updated.click()
        page.wait_for_timeout(1000)

        delete_button = page.get_by_role("button", name="삭제")
        if delete_button.is_visible():
            delete_button.click()
            page.wait_for_timeout(500)

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 삭제 확인
            expect(page.get_by_role("treeitem", name=edited_name)).not_to_be_visible()

        # === 1단 부모 장소 삭제 ===
        parent_treeitem = page.get_by_role("treeitem", name=parent_name)
        if parent_treeitem.is_visible():
            parent_treeitem.click()
            page.wait_for_timeout(1000)

            delete_button = page.get_by_role("button", name="삭제")
            if delete_button.is_visible():
                delete_button.click()
                page.wait_for_timeout(500)

                page.wait_for_timeout(3000)
                page.wait_for_load_state('networkidle', timeout=10000)

                # 부모 삭제 확인
                expect(page.get_by_role("treeitem", name=parent_name)).not_to_be_visible()


    def test_3_level_location_add_edit_delete(self, navigate_to_location):
        """
        3단 장소: 추가 -> 수정 -> 삭제 -> 2단 부모 삭제 -> 1단 부모 삭제

        사전조건: 1단 부모, 2단 부모 장소가 필요함
        """
        page = navigate_to_location()

        # 모든 다이얼로그 자동 처리
        def handle_dialog(dialog):
            if "삭제" in dialog.message or "delete" in dialog.message.lower():
                dialog.accept()
            else:
                dialog.accept()

        page.on("dialog", handle_dialog)

        timestamp = int(time.time())
        parent1_name = f'3단_부모1_{timestamp}'
        parent2_name = f'3단_부모2_{timestamp}'
        original_name = f'3단_원본_{timestamp}'
        edited_name = f'3단_수정_{timestamp}'

        # === 1단 부모 장소 추가 ===
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(parent1_name)
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()
        page.get_by_role("spinbutton", name="표시 순서").fill("20")

        page.get_by_role("button", name="저장").click()

        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 1단 부모 선택
        parent1_treeitem = page.get_by_role("treeitem", name=parent1_name)
        expect(parent1_treeitem).to_be_visible(timeout=5000)
        parent1_treeitem.click()
        page.wait_for_timeout(1000)

        # === 2단 부모 장소 추가 ===
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(parent2_name)
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()
        page.get_by_role("spinbutton", name="표시 순서").fill("1")

        page.get_by_role("button", name="저장").click()

        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 2단 부모 선택
        parent2_treeitem = page.get_by_role("treeitem", name=parent2_name)
        expect(parent2_treeitem).to_be_visible(timeout=5000)
        parent2_treeitem.click()
        page.wait_for_timeout(1000)

        # === 3단 자식 장소 추가 ===
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(original_name)
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()
        page.get_by_role("spinbutton", name="표시 순서").fill("1")

        page.get_by_role("button", name="저장").click()

        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 추가 확인
        child_treeitem = page.get_by_role("treeitem", name=original_name)
        expect(child_treeitem).to_be_visible(timeout=5000)

        # === 3단 장소 수정 ===
        child_treeitem.click()
        page.wait_for_timeout(1000)

        edit_button = page.get_by_role("button", name="수정")
        if edit_button.is_visible():
            edit_button.click()
            page.wait_for_timeout(1000)

        name_field = page.get_by_role("textbox", name="장소 이름")
        if name_field.is_visible():
            name_field.clear()
            name_field.fill(edited_name)

            page.get_by_role("button", name="저장").click()

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 수정 확인
            expect(page.get_by_role("treeitem", name=edited_name)).to_be_visible(timeout=5000)

        # === 3단 장소 삭제 ===
        child_treeitem_updated = page.get_by_role("treeitem", name=edited_name)
        child_treeitem_updated.click()
        page.wait_for_timeout(1000)

        delete_button = page.get_by_role("button", name="삭제")
        if delete_button.is_visible():
            delete_button.click()
            page.wait_for_timeout(500)

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 삭제 확인
            expect(page.get_by_role("treeitem", name=edited_name)).not_to_be_visible()

        # === 2단 부모 장소 삭제 ===
        parent2_treeitem = page.get_by_role("treeitem", name=parent2_name)
        if parent2_treeitem.is_visible():
            parent2_treeitem.click()
            page.wait_for_timeout(1000)

            delete_button = page.get_by_role("button", name="삭제")
            if delete_button.is_visible():
                delete_button.click()
                page.wait_for_timeout(500)

                page.wait_for_timeout(3000)
                page.wait_for_load_state('networkidle', timeout=10000)

                # 2단 부모 삭제 확인
                expect(page.get_by_role("treeitem", name=parent2_name)).not_to_be_visible()

        # === 1단 부모 장소 삭제 ===
        parent1_treeitem = page.get_by_role("treeitem", name=parent1_name)
        if parent1_treeitem.is_visible():
            parent1_treeitem.click()
            page.wait_for_timeout(1000)

            delete_button = page.get_by_role("button", name="삭제")
            if delete_button.is_visible():
                delete_button.click()
                page.wait_for_timeout(500)

                page.wait_for_timeout(3000)
                page.wait_for_load_state('networkidle', timeout=10000)

                # 1단 부모 삭제 확인
                expect(page.get_by_role("treeitem", name=parent1_name)).not_to_be_visible()
