"""
다이얼로그 감지 테스트
크롬 확인창(alert/confirm/prompt)을 감지하고 처리하는 방법 테스트
"""
import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.location
class TestDialogDetection:
    """
    다이얼로그 감지 및 처리 테스트
    """

    def test_detect_dialogs_on_save(self, navigate_to_location):
        """
        장소 저장 시 나타나는 모든 다이얼로그 감지
        """
        page = navigate_to_location()

        # 다이얼로그 로그 저장용
        dialogs_detected = []

        # 모든 다이얼로그 자동 감지 및 처리
        def handle_dialog(dialog):
            dialog_info = {
                'type': dialog.type,  # alert, confirm, prompt
                'message': dialog.message,
                'default_value': dialog.default_value if dialog.type == 'prompt' else None
            }
            dialogs_detected.append(dialog_info)
            print(f"\n[다이얼로그 감지] Type: {dialog.type}, Message: {dialog.message}")

            # 자동으로 수락
            dialog.accept()

        # 다이얼로그 리스너 등록 (page.on은 계속 유지됨)
        page.on("dialog", handle_dialog)

        timestamp = int(time.time())
        location_name = f'다이얼로그테스트_{timestamp}'

        # === 장소 추가 ===
        print("\n=== 장소 추가 시작 ===")
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(location_name)
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()
        page.get_by_role("spinbutton", name="표시 순서").fill("1")

        print("저장 버튼 클릭...")
        page.get_by_role("button", name="저장").click()

        # 다이얼로그 처리 대기
        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 감지된 다이얼로그 출력
        print(f"\n감지된 다이얼로그 개수: {len(dialogs_detected)}")
        for i, dialog in enumerate(dialogs_detected, 1):
            print(f"다이얼로그 {i}: {dialog}")

        # 장소 추가 확인
        treeitem = page.get_by_role("treeitem", name=location_name)
        expect(treeitem).to_be_visible(timeout=5000)

        print("\n=== 장소 추가 완료 ===")


    def test_detect_dialogs_on_edit(self, navigate_to_location):
        """
        장소 수정 시 나타나는 모든 다이얼로그 감지
        """
        page = navigate_to_location()

        dialogs_detected = []

        def handle_dialog(dialog):
            dialog_info = {
                'type': dialog.type,
                'message': dialog.message,
            }
            dialogs_detected.append(dialog_info)
            print(f"\n[다이얼로그 감지] Type: {dialog.type}, Message: {dialog.message}")
            dialog.accept()

        page.on("dialog", handle_dialog)

        timestamp = int(time.time())
        original_name = f'수정테스트_{timestamp}'
        edited_name = f'수정완료_{timestamp}'

        # 장소 추가
        print("\n=== 테스트용 장소 추가 ===")
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

        # 수정 시작
        print(f"\n=== 장소 수정 시작 (다이얼로그 감지 초기화) ===")
        dialogs_detected.clear()  # 추가 시 다이얼로그는 제외

        treeitem = page.get_by_role("treeitem", name=original_name)
        treeitem.click()
        page.wait_for_timeout(1000)

        edit_button = page.get_by_role("button", name="수정")
        if edit_button.is_visible():
            edit_button.click()
            page.wait_for_timeout(1000)

        name_field = page.get_by_role("textbox", name="장소 이름")
        if name_field.is_visible():
            name_field.clear()
            name_field.fill(edited_name)

            print("저장 버튼 클릭...")
            page.get_by_role("button", name="저장").click()

            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 수정 시 감지된 다이얼로그 출력
            print(f"\n수정 시 감지된 다이얼로그 개수: {len(dialogs_detected)}")
            for i, dialog in enumerate(dialogs_detected, 1):
                print(f"다이얼로그 {i}: {dialog}")

            expect(page.get_by_role("treeitem", name=edited_name)).to_be_visible(timeout=5000)

        print("\n=== 장소 수정 완료 ===")


    def test_detect_dialogs_on_delete(self, navigate_to_location):
        """
        장소 삭제 시 나타나는 모든 다이얼로그 감지
        """
        page = navigate_to_location()

        dialogs_detected = []

        def handle_dialog(dialog):
            dialog_info = {
                'type': dialog.type,
                'message': dialog.message,
            }
            dialogs_detected.append(dialog_info)
            print(f"\n[다이얼로그 감지] Type: {dialog.type}, Message: {dialog.message}")
            dialog.accept()  # 삭제 확인

        page.on("dialog", handle_dialog)

        timestamp = int(time.time())
        location_name = f'삭제테스트_{timestamp}'

        # 장소 추가
        print("\n=== 테스트용 장소 추가 ===")
        page.get_by_role("button", name="장소 추가").click()
        page.wait_for_timeout(1000)

        page.get_by_role("textbox", name="장소 이름").fill(location_name)
        page.get_by_label("", exact=True).click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="사무공간").click()
        page.get_by_role("spinbutton", name="표시 순서").fill("1")

        page.get_by_role("button", name="저장").click()
        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # 삭제 시작
        print(f"\n=== 장소 삭제 시작 (다이얼로그 감지 초기화) ===")
        dialogs_detected.clear()

        treeitem = page.get_by_role("treeitem", name=location_name)
        treeitem.click()
        page.wait_for_timeout(1000)

        delete_button = page.get_by_role("button", name="삭제")
        if delete_button.is_visible():
            print("삭제 버튼 클릭...")
            delete_button.click()
            page.wait_for_timeout(500)

            # 삭제 확인 다이얼로그 대기
            page.wait_for_timeout(3000)
            page.wait_for_load_state('networkidle', timeout=10000)

            # 삭제 시 감지된 다이얼로그 출력
            print(f"\n삭제 시 감지된 다이얼로그 개수: {len(dialogs_detected)}")
            for i, dialog in enumerate(dialogs_detected, 1):
                print(f"다이얼로그 {i}: {dialog}")

            expect(page.get_by_role("treeitem", name=location_name)).not_to_be_visible()

        print("\n=== 장소 삭제 완료 ===")
