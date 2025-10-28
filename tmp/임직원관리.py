import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://dev-acs.secernai.net/signin?reason=session_expired&returnUrl=%2F")
    page.get_by_role("textbox", name="Enter your Login ID or Email").click()
    page.get_by_role("textbox", name="Enter your Login ID or Email").fill("superadmin")
    page.get_by_role("textbox", name="Enter your Login ID or Email").press("Tab")
    page.get_by_role("textbox", name="Password").fill("string")
    page.get_by_role("textbox", name="Password").press("Enter")
    page.get_by_role("button", name="Sign In").click()
    page.get_by_role("button", name="출입 통합 관리").click()
    page.get_by_role("button", name="임직원 출입자 관리").click()
    page.get_by_role("tab", name="임직원 출입자").click()
    page.get_by_role("cell", name="1000460", exact=True).click()
    page.get_by_role("button", name="삭제").click()
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="삭제").click()
    page.get_by_role("button", name="검색").click()
    page.get_by_role("button", name="필터").click()
    page.get_by_role("textbox", name="이름").click()
    page.get_by_role("textbox", name="이름").click()
    page.get_by_role("textbox", name="이름").fill("1000415")
    page.get_by_role("button", name="검색").click()
    page.get_by_role("cell", name="00000000000").click()
    page.get_by_role("button", name="삭제").click()
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="삭제").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
