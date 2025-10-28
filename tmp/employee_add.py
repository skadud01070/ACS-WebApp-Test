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
    page.get_by_role("button", name="임직원 추가").click()
    page.locator("#mui-component-select-departmentId").click()
    page.get_by_role("option", name="개발팀").click()
    page.locator("#mui-component-select-jobGradeId").click()
    page.get_by_role("option", name="Pro").click()
    page.locator("#mui-component-select-jobPositionId").click()
    page.get_by_role("option", name="Pro").click()
    page.locator(".MuiSvgIcon-root.MuiSvgIcon-fontSizeMedium.MuiAvatar-fallback").first.click()
    page.get_by_label("Avatar image").first.set_input_files("1000508.jpg")
    page.get_by_role("textbox", name="이름").click()
    page.get_by_role("textbox", name="이름").fill("1000508")
    page.get_by_role("textbox", name="이름").click()
    page.get_by_role("textbox", name="이름").fill("1000508-이름")
    page.get_by_role("textbox", name="이름").click()
    page.get_by_role("textbox", name="사번").click()
    page.get_by_role("textbox", name="사번").fill("1000508")
    page.get_by_role("group", name="발령 시작일").get_by_label("날짜를 선택하세요").click()
    page.get_by_role("gridcell", name="27").click()
    page.get_by_role("textbox", name="이메일").click()
    page.get_by_role("textbox", name="이메일").fill("1000508@s.ai")
    page.locator("#mui-component-select-accessCaseId").click()
    page.get_by_role("option", name="식수테스트정책").click()
    page.locator("#menu-accessCaseId div").first.click()
    page.locator("div").filter(has_text=re.compile(r"^출입자 이미지$")).get_by_label("Avatar image").set_input_files("1000508.jpg")
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="저장").click()
    page.goto("https://dev-acs.secernai.net/organization?tab=employee")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)


# 세부사항
- https://dev-acs.secernai.net/employee/employeeadd 로딩 대기
- page.locator(".MuiSvgIcon-root.MuiSvgIcon-fontSizeMedium.css-185tx24 > path").first.click() 추가
- 부서, 직급, 직책 랜덤선택
- 출입정책은 1~5개 랜덤 선택