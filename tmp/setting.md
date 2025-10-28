# e2e

## 기본 장소 선택
import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://172.16.150.200:4021/signin?reason=session_expired&returnUrl=%2Flocation%3Ftab%3Dlocation")
    page.get_by_role("textbox", name="Enter your Login ID or Email").click()
    page.get_by_role("textbox", name="Enter your Login ID or Email").fill("superadmin")
    page.get_by_role("textbox", name="Enter your Login ID or Email").press("Tab")
    page.get_by_role("textbox", name="Password").fill("superadmin")
    page.get_by_role("button", name="Sign In").click()
    page.get_by_role("button", name="출입 통합 관리").click()
    page.get_by_role("button", name="장소 정보 관리").click()
    page.get_by_role("button", name="장소 추가").click()
    page.get_by_role("textbox", name="장소 이름").click()
    page.get_by_role("textbox", name="장소 이름").fill("test2")
    page.get_by_label("", exact=True).click()
    page.get_by_role("option", name="사무공간").click()
    page.get_by_role("spinbutton", name="표시 순서").dblclick()
    page.get_by_role("spinbutton", name="표시 순서").click()
    page.get_by_role("spinbutton", name="표시 순서").fill("1")
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="저장").click()
    page.get_by_role("treeitem", name="test2").locator("div").nth(2).click()

    
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)


   
## 선택한 장소 취소
    page.get_by_role("treeitem", name="본사사옥").locator("div").nth(2).click()
    page.get_by_role("button", name="장소 선택 취소").click()
    page.get_by_role("treeitem", name="test2").locator("div").nth(2).click()
    page.get_by_role("button", name="장소 선택 취소").click()


### 장소 관리 기능
- 1단 추가, 1단 수정, 1단 삭제
- 2단 추가, 2단 수정, 2단 삭제
- 3단 추가, 3단 수정, 3단 삭제
  


# fuction
## 장소 추가