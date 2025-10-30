# Employee (임직원 출입자 관리) 테스트 가이드

## 개요

임직원 출입자 관리 기능에 대한 E2E 테스트입니다.

### 자동 로그인 처리

모든 테스트는 `tests-python/e2e/conftest.py`의 `authenticated_context` fixture를 통해 **자동으로 로그인된 상태**에서 시작됩니다.

- **세션 기반 인증**: 한 번만 로그인하여 모든 테스트에서 재사용
- **테스트 격리**: 각 테스트는 독립적인 페이지를 받지만 동일한 인증 상태 공유
- **환경 설정**: `.env.test` 파일의 `TEST_USER_EMAIL`과 `TEST_USER_PASSWORD` 사용

## 테스트 파일

### test_employee_management.py

임직원 추가, 삭제, 검색 기능 테스트:

- **test_add_employee_with_photo**: 사진을 포함한 임직원 추가
- **test_delete_employee_from_list**: 목록에서 임직원 삭제
- **test_search_and_delete_employee**: 검색 후 임직원 삭제

## 사전 준비

### 테스트 이미지 준비

`tests-python/employee/` 폴더에 임직원 사진 파일을 준비해야 합니다.

```bash
tests-python/
├── employee/              # 테스트용 임직원 사진
│   ├── 1000001.jpg
│   ├── 1000002.jpg
│   └── ...
```

**파일명 규칙**:
- 파일명 = 사번 (예: `1000001.jpg`)
- 지원 포맷: `.jpg`, `.jpeg`, `.png`

**주의사항**:
- 최소 1개 이상의 이미지 파일 필요
- 이미지는 재사용 가능 (이동되지 않음)

## 테스트 실행

### uv 사용 (권장)

```bash
cd tests-python

# Headless 모드 (백그라운드 실행, 실패 시에만 스크린샷/비디오 저장)
uv run pytest e2e/access/employee/ --browser chromium

# Headed 모드 (브라우저 표시, 실행 과정 확인)
uv run pytest e2e/access/employee/ --headed --browser chromium
```

### 특정 테스트 메서드 실행

```bash
# 임직원 추가 테스트만 (headless)
uv run pytest e2e/access/employee/test_employee_management.py::TestEmployeeManagement::test_add_employee_with_photo --browser chromium

# 삭제 테스트만 (headed)
uv run pytest e2e/access/employee/test_employee_management.py::TestEmployeeManagement::test_delete_employee_from_list --headed --browser chromium

# 검색 및 삭제 테스트 (headed)
uv run pytest e2e/access/employee/test_employee_management.py::TestEmployeeManagement::test_search_and_delete_employee --headed --browser chromium
```

### 디버깅 모드

```bash
# 느린 속도로 실행 (동작 관찰)
uv run pytest e2e/access/employee/ --headed --browser chromium --slowmo 1000

# Headless 모드 (빠른 실행, 권장)
uv run pytest e2e/access/employee/ --browser chromium
```

### 실패 시 스크린샷/비디오

기본 설정으로 실패 시 자동 저장됩니다:
- 위치: `tests-python/test-results/`
- 스크린샷: `.png` 파일
- 비디오: `.webm` 파일
- 트레이스: `.zip` 파일 (Playwright Trace Viewer로 분석 가능)

### 기존 venv 방식 (대안)

```bash
# 가상환경 활성화
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 테스트 실행
pytest e2e/access/employee/ --headed --browser chromium
```

## 환경 설정

테스트 실행 전에 `.env.test` 파일을 확인하세요:

```env
# 테스트 대상 서버
BASE_URL=http://172.16.150.200:4021/

# 테스트 계정 (실제 존재하는 계정)
TEST_USER_EMAIL=superadmin
TEST_USER_PASSWORD=superadmin
```

## Fixture 사용법

### navigate_to_employee_page

메인 페이지에서 메뉴를 통해 임직원 출입자 관리 페이지로 이동합니다.

```python
def test_something(self, navigate_to_employee_page):
    page = navigate_to_employee_page()
    # 이제 임직원 출입자 관리 페이지에 있음
    page.get_by_role("button", name="임직원 추가").click()
```

## 테스트 작성 가이드

### 기본 테스트 구조

```python
import pytest
from playwright.sync_api import Page, expect
import time

class TestEmployeeManagement:
    """임직원 출입자 관리 테스트"""

    def test_something(self, navigate_to_employee_page: Page):
        """테스트 설명"""
        page = navigate_to_employee_page

        # 모든 다이얼로그 자동 처리
        def handle_dialog(dialog):
            if "삭제" in dialog.message or "delete" in dialog.message.lower():
                dialog.accept()
            else:
                dialog.accept()
        page.on("dialog", handle_dialog)

        # 고유한 ID 생성
        timestamp = int(time.time())
        employee_id = f'TEST_{timestamp}'

        # 테스트 로직
        # ...
```

### 다이얼로그 처리 패턴

```python
# ✅ 올바른 방법: 모든 다이얼로그 처리
def handle_dialog(dialog):
    if "삭제" in dialog.message:
        dialog.accept()
    else:
        dialog.accept()
page.on("dialog", handle_dialog)

# ❌ 잘못된 방법: 첫 번째 다이얼로그만 처리
page.once("dialog", lambda dialog: dialog.accept())
```

### 파일 업로드 패턴

```python
# 파일 선택 다이얼로그 처리
with page.expect_file_chooser() as fc_info:
    # 파일 선택 트리거 (버튼 클릭 등)
    page.locator("input[type='file']").click()

file_chooser = fc_info.value
file_chooser.set_files("/path/to/image.jpg")
page.wait_for_timeout(500)
```

### 드롭다운 선택 패턴

```python
# 드롭다운 열기
page.locator("#mui-component-select-departmentId").click()
page.wait_for_timeout(500)

# 옵션 목록 가져오기
options = page.locator('[role="option"]').all()

# 첫 번째 옵션 제외하고 랜덤 선택
if len(options) > 1:
    random.choice(options[1:]).click()

page.wait_for_timeout(300)
```

## 주의사항

### 1. 테스트 데이터 의존성

현재 삭제 테스트들은 특정 ID가 존재한다고 가정합니다:
- `test_delete_employee_from_list`: `1000460`
- `test_search_and_delete_employee`: `1000415`

**권장 개선 방향**:
```python
# 더 나은 패턴: 추가 → 확인 → 삭제
def test_employee_lifecycle(self, navigate_to_employee_page):
    page = navigate_to_employee_page

    # 1. 임직원 추가
    employee_id = f'TEST_{int(time.time())}'
    # ... 추가 로직 ...

    # 2. 목록에서 확인
    expect(page.get_by_role("cell", name=employee_id)).to_be_visible()

    # 3. 삭제
    page.get_by_role("cell", name=employee_id).click()
    page.get_by_role("button", name="삭제").click()

    # 4. 삭제 확인
    expect(page.get_by_role("cell", name=employee_id)).not_to_be_visible()
```

### 2. 이미지 파일 관리

- 테스트 대기 이미지: `tests-python/employee/` 폴더
- 성공 시 `tests-python/employee_add/` 폴더로 자동 이동
- 다음 실행 시 `employee/` 폴더의 남은 이미지 사용
- 모든 이미지가 처리되면 `employee_add/`에서 다시 `employee/`로 복사 필요

### 3. 네트워크 대기

```python
# 페이지 로딩 대기
page.wait_for_load_state('networkidle')

# 추가 안전 대기
page.wait_for_timeout(2000)

# URL 변경 대기
page.wait_for_url("**/employee**", timeout=10000)
```

## 개선 사항 (2025-10-27)

### 다이얼로그 처리 개선

**이전 (문제)**:
```python
page.once("dialog", lambda dialog: dialog.accept())  # 첫 번째만 처리
```

**현재 (개선)**:
```python
def handle_dialog(dialog):
    if "삭제" in dialog.message:
        dialog.accept()
    else:
        dialog.accept()
page.on("dialog", handle_dialog)  # 모든 다이얼로그 처리
```

### 검증 로직 개선

**이전 (문제)**:
```python
# 추가 후 안 보이는 것을 확인? (논리적 오류)
expect(page.get_by_text(unique_name)).not_to_be_visible()
```

**현재 (개선)**:
```python
# 목록 페이지로 돌아온 후 employee_id로 확인
page.wait_for_url("**/employee**", timeout=10000)
page.wait_for_load_state('networkidle')

# 추가한 employee_id가 목록에 보이는지 검증
employee_cell = page.get_by_role("cell", name=employee_id, exact=True)
expect(employee_cell).to_be_visible(timeout=10000)
```

### 파일 관리 개선

**현재 동작**:
- 테스트 성공 시 이미지 파일을 `employee_add/` 폴더로 이동
- 이동된 파일은 이미 처리된 임직원으로 간주
- 다음 실행 시 `employee/` 폴더의 다른 이미지 사용

**파일 흐름**:
```
tests-python/
├── employee/           # 테스트 대기 중인 이미지
│   ├── 1000001.jpg    # 다음 테스트에서 사용될 이미지
│   └── 1000002.jpg
└── employee_add/       # 성공적으로 추가된 임직원 이미지
    └── 1000000.jpg    # 이미 처리됨
```

## 트러블슈팅

### 이미지 파일 없음

```
pytest.skip: 테스트할 이미지가 employee 폴더에 없습니다.
```

**해결**:
1. `tests-python/employee/` 폴더 생성
2. 테스트용 이미지 파일 추가 (파일명 = 사번)

### 특정 ID를 찾을 수 없음

```
TimeoutError: locator.click: Timeout 10000ms exceeded
```

**원인**:
- 삭제 테스트에서 지정한 ID가 존재하지 않음

**해결**:
1. 해당 ID의 임직원을 먼저 추가
2. 또는 존재하는 ID로 변경
3. 또는 동적으로 임직원 추가 후 삭제하는 패턴 사용

### 다이얼로그 처리 안 됨

```
TimeoutError: page.wait_for_url: Timeout exceeded
```

**해결**:
- `page.once()` 대신 `page.on()` 사용 확인
- 다이얼로그 핸들러가 테스트 시작 시 등록되었는지 확인

## Excel 기반 테스트: test_add_employees_from_excel

### 개요

Excel 파일(`em_add.xlsx`)의 설정을 기반으로 임직원을 추가하고, "인원" 시트에 자동으로 기록하는 테스트입니다.

### 주요 기능

1. **순차 번호 부여**: "인원" 시트의 마지막 index를 확인하여 다음 번호부터 추가
2. **자동 기록**: 추가된 임직원의 이름과 ID를 "인원" 시트에 자동으로 기록
3. **설정 기반**: "임직원_추가" 시트의 설정(부서, 직급, 직책 등)을 사용

### Excel 파일 구조

#### "임직원_추가" 시트 (설정 템플릿)

| 컬럼 | 이름 | 설명 |
|------|------|------|
| A | index | 사용할 이미지 파일 번호 (1부터 시작) |
| B | department | 부서명 |
| C | job_grade | 직급 |
| D | job_position | 직책 |
| E | assignment_start_date | 발령 시작일 ("today" 또는 날짜) |
| F | access_cases | 출입케이스 (쉼표로 구분) |
| G | rf_card | RF 카드 (쉼표로 구분) |

#### "인원" 시트 (인원 로그)

| 컬럼 | 이름 | 설명 |
|------|------|------|
| A | index | 순차 번호 (자동 부여) |
| B | department | 부서명 |
| C | job_grade | 직급 |
| D | job_position | 직책 |
| E | assignment_start_date | 발령 시작일 |
| F | access_cases | 출입케이스 |
| G | rf_card | RF 카드 |
| H | (빈 칸) | - |
| I | name | 생성된 이름 |
| J | id | 사번 (이미지 파일명) |

### 실행 방법

```bash
# Excel 파일을 먼저 닫아야 합니다!
uv run python -m pytest e2e/access/employee/test_employee_management.py::TestEmployeeManagement::test_add_employees_from_excel --browser chromium

# Headed 모드 (브라우저 표시)
uv run python -m pytest e2e/access/employee/test_employee_management.py::TestEmployeeManagement::test_add_employees_from_excel --headed --browser chromium -s
```

### 중요 사항

1. **Excel 파일 닫기**: 테스트 실행 전에 `em_add.xlsx` 파일을 닫아야 합니다
   - Excel에서 파일이 열려있으면 "인원" 시트에 데이터를 저장할 수 없습니다
   - 잠금 파일 확인: `~$em_add.xlsx` 파일이 있으면 Excel이 열려있는 것입니다

2. **순차 번호 부여**:
   - 테스트 시작 전 "인원" 시트의 마지막 index를 확인
   - 예: 마지막 index가 51이면, 새 임직원은 52, 53, 54... 순으로 추가

3. **이미지 파일**:
   - `employee/` 폴더에서 이미지 읽기
   - 성공 후 `employee_add/` 폴더로 이동
   - 이미지 파일명(확장자 제외)이 사번이 됨

4. **테스트 출력**:
   - 각 임직원 처리 진행 상황 표시
   - 시간 정보 표시
   - "인원" 시트 기록 확인 메시지

### 실행 예시

```
[WARNING] Excel 파일이 다른 프로그램에서 열려있습니다: C:\...\em_add.xlsx
[WARNING] 테스트는 실행되지만 '인원' 시트에 데이터를 저장하지 못할 수 있습니다.
[WARNING] 데이터 저장을 위해 Excel 파일을 닫고 테스트를 실행하세요.

[INFO] '인원' 시트의 마지막 index: 51, 다음 추가할 index: 52
[INFO] Excel에서 읽은 임직원 수: 1명

[START] Processing 1 employees from Excel...

[INFO] Processing employee 1/1: Personnel Index=52, Image Index=1, ID=1098827, Name=1098827-1761723342
[INFO] Using access cases from Excel: ['메인타워', '본사사옥']
[INFO] Selected 2/2 access cases
[OK] Employee added successfully: ID=1098827, Name=1098827-1761723342, Time=5.83s
[INFO] Added to '인원' sheet: Index=52, Name=1098827-1761723342, ID=1098827
[INFO] Image file moved: 1098827.jpg -> employee_add/

[INFO] All employee info saved to Excel '인원' sheet: C:\...\em_add.xlsx

[COMPLETE] Successfully added 1 employees from Excel
[TIME] Total: 6.09s, Average per employee: 6.09s
```

### 트러블슈팅

#### 문제: `[ERROR] Failed to save Excel file: Permission denied`

**해결**: Excel에서 `em_add.xlsx` 파일을 닫고 다시 실행

**확인 방법**:
```bash
ls -la e2e/access/employee/ | grep "~\$"
```

`~$em_add.xlsx` 파일이 보이면 Excel이 열려있는 것입니다.

---

#### 문제: 잘못된 이미지 파일 사용

**해결**: "임직원_추가" 시트의 `index` 컬럼 확인
- index 1 = 첫 번째 이미지 파일
- index 2 = 두 번째 이미지 파일

---

#### 문제: "인원" 시트에 데이터가 없음

**해결**:
1. 테스트가 성공적으로 완료되었는지 확인 (에러 없이)
2. Excel 파일이 잠겨있지 않았는지 확인
3. Excel 파일을 닫고 테스트 재실행

### 동작 방식

1. **테스트 시작**: "인원" 시트에서 마지막 index 읽기 (예: 51)
2. **임직원 1 처리**: 이미지 index 1 사용, 인원 index 52 부여, "인원" 시트에 기록
3. **임직원 2 처리**: 이미지 index 2 사용, 인원 index 53 부여, "인원" 시트에 기록
4. **Excel 저장**: 모든 변경사항을 em_add.xlsx에 저장

## 추가 정보

- 전체 테스트 가이드: `tests-python/TESTING-GUIDE.md`
- Playwright 문서: https://playwright.dev/python/
- pytest 문서: https://docs.pytest.org/
- 아키텍처 가이드: `tests-python/CLAUDE.md`
