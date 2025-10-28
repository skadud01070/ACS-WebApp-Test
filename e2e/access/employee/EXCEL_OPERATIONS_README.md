# Excel Operations Demo Script

## 개요

`excel_operations_demo.py`는 Python의 openpyxl 라이브러리를 사용하여 Excel 파일을 생성하고 조작하는 방법을 종합적으로 시연하는 교육용 스크립트입니다.

## 주요 기능

이 스크립트는 다음과 같은 Excel 작업을 수행합니다:

### 1. 워크북 생성/열기
- 새로운 Excel 워크북 생성
- 기존 파일이 있으면 열기
- 에러 처리 포함

### 2. 시트 관리
- 새 시트 추가 (`create_sheet()`)
- 시트 존재 여부 확인
- 불필요한 기본 시트 삭제

### 3. 데이터 작성
- 헤더 행 작성
- 샘플 데이터 행 추가
- `ws.append()` 메서드 사용

### 4. 셀 서식 지정
- **배경색**: `PatternFill`로 색상 지정
- **폰트**: `Font`로 굵기, 색상, 크기 지정
- **정렬**: `Alignment`로 가로/세로 정렬
- **테두리**: `Border`로 셀 테두리 설정

### 5. 레이아웃 조정
- **컬럼 너비**: `column_dimensions[letter].width`
- **행 높이**: `row_dimensions[number].height`
- 각 컬럼별로 적절한 너비 설정

### 6. 이미지 삽입
- 이미지 파일 검색 (jpg, png, bmp, gif 등)
- `XLImage`로 이미지 로드
- 이미지 크기 조정 (width, height)
- 특정 셀 위치에 이미지 삽입 (`ws.add_image()`)

### 7. 다중 시트 관리
- 메인 데이터 시트
- 추가 정보 시트
- 각 시트별로 독립적인 서식 적용

### 8. 파일 저장
- `wb.save(filename)` 메서드
- 예외 처리 포함
- 성공/실패 메시지 출력

## 실행 방법

### 1. 필수 패키지 설치

```bash
# openpyxl과 pillow 설치
pip install openpyxl pillow

# 또는 uv 사용 시
uv pip install openpyxl pillow
```

### 2. 스크립트 실행

```bash
# 현재 디렉토리에서 실행
python excel_operations_demo.py

# 절대 경로로 실행
python C:\00project\2025\SDG\ACS-WebApp-Test\e2e\access\employee\excel_operations_demo.py
```

### 3. 결과 확인

스크립트 실행 후 다음 파일이 생성됩니다:
- `excel_demo_output.xlsx`

파일을 열어서 다음을 확인하세요:
1. **샘플데이터 시트**: 서식이 적용된 헤더와 데이터
2. **작성정보 시트**: 파일 메타데이터

## 출력 예시

```
================================================================================
Excel 파일 생성 및 조작 종합 예제 스크립트
================================================================================

[INFO] 새 워크북을 생성합니다: excel_demo_output.xlsx
[INFO] 새 시트를 생성합니다: 샘플데이터
[INFO] 헤더 행을 작성합니다...
[INFO] 헤더 셀 서식을 지정합니다...
[INFO] 샘플 데이터를 작성합니다...
[INFO] 컬럼 너비를 조정합니다...
[INFO] 행 높이를 조정합니다...
[INFO] 이미지를 삽입합니다...
[INFO] 이미지 파일이 없습니다. 샘플 이미지 없이 진행합니다.
[TIP] 이미지를 삽입하려면 'C:\...\employee' 폴더에 이미지 파일을 추가하세요.
[INFO] 추가 정보 시트를 생성합니다...
[INFO] Excel 파일을 저장합니다: excel_demo_output.xlsx
[SUCCESS] Excel 파일이 성공적으로 저장되었습니다: excel_demo_output.xlsx

================================================================================
작업 완료!
================================================================================
```

## 코드 구조

### 함수 구성

```python
def create_sample_excel():
    """메인 로직: Excel 파일 생성"""
    # 1. 워크북 생성/열기
    # 2. 시트 추가
    # 3. 헤더 작성
    # 4. 헤더 서식
    # 5. 데이터 작성
    # 6. 컬럼 너비 조정
    # 7. 행 높이 조정
    # 8. 이미지 삽입
    # 9. 추가 시트 생성
    # 10. 저장
    return file_path

def main():
    """실행 진입점"""
    # 에러 처리 및 출력 메시지
```

## 주요 openpyxl 패턴

### 1. 셀 서식 적용

```python
from openpyxl.styles import Font, PatternFill, Alignment

# 배경색
cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

# 폰트
cell.font = Font(bold=True, color="FFFFFF", size=11)

# 정렬
cell.alignment = Alignment(horizontal="center", vertical="center")
```

### 2. 컬럼 너비 조정

```python
from openpyxl.utils import get_column_letter

# 방법 1: 컬럼 레터로 직접
ws.column_dimensions['A'].width = 20

# 방법 2: 숫자를 레터로 변환
col_letter = get_column_letter(1)  # 'A'
ws.column_dimensions[col_letter].width = 20
```

### 3. 이미지 삽입

```python
from openpyxl.drawing.image import Image as XLImage

# 이미지 로드
img = XLImage('photo.jpg')

# 크기 조정
img.width = 60
img.height = 75

# 셀 위치에 삽입
ws.add_image(img, 'I2')  # I2 셀에 삽입
```

## 이미지 삽입 테스트

이미지 삽입 기능을 테스트하려면:

1. `e2e/access/employee/images/` 폴더 생성
2. 테스트용 이미지 파일(jpg, png 등) 복사
3. 스크립트 재실행

스크립트가 자동으로 이미지를 찾아서 Excel 파일에 삽입합니다.

## test_employee_management.py와의 연관성

이 스크립트는 `test_employee_management.py`의 다음 패턴을 참고했습니다:

- **라인 625-655**: 시트 생성 및 헤더 서식
- **라인 839-855**: 이미지 삽입 로직
- openpyxl 사용 패턴 전반

주요 차이점:
- **단순화**: 테스트 코드에서 핵심 패턴만 추출
- **교육 목적**: 각 단계별 상세한 주석 추가
- **독립 실행**: 별도 의존성 없이 단독 실행 가능
- **에러 처리**: 완전한 예외 처리 로직 포함

## 활용 방법

### 1. 학습 자료로 활용
- openpyxl 라이브러리 사용법 학습
- Excel 자동화 기초 습득
- 실무 패턴 참고

### 2. 템플릿으로 활용
- 코드 복사하여 프로젝트에 적용
- 필요한 부분만 발췌하여 사용
- 커스터마이징하여 확장

### 3. 테스트용으로 활용
- Excel 파일 생성 기능 검증
- 데이터 포맷 테스트
- 이미지 삽입 동작 확인

## 문제 해결

### openpyxl 설치 오류

```bash
[ERROR] 필수 패키지를 설치해주세요: No module named 'openpyxl'
```

**해결책**:
```bash
pip install openpyxl pillow
```

### 이미지 삽입 실패

```bash
[WARNING] 이미지 삽입 실패 (photo.jpg): ...
```

**원인**:
- 이미지 파일 손상
- 지원하지 않는 형식
- 파일 경로 오류

**해결책**:
- 이미지 파일 형식 확인 (jpg, png, bmp, gif)
- 파일 손상 여부 확인
- 파일 경로 및 권한 확인

### 파일 저장 실패

```bash
[ERROR] 파일 저장 실패: Permission denied
```

**원인**:
- Excel 파일이 이미 열려있음
- 디렉토리 쓰기 권한 없음

**해결책**:
- 기존 Excel 파일 닫기
- 관리자 권한으로 실행
- 다른 디렉토리에 저장

## 추가 리소스

### 공식 문서
- [openpyxl 공식 문서](https://openpyxl.readthedocs.io/)
- [openpyxl 스타일 가이드](https://openpyxl.readthedocs.io/en/stable/styles.html)
- [Pillow 문서](https://pillow.readthedocs.io/)

### 관련 파일
- `test_employee_management.py`: 실제 E2E 테스트에서 사용하는 Excel 조작 코드
- `create_excel.py`: 기존 템플릿 생성 스크립트
- `em_add.xlsx`: 템플릿 파일 (생성됨)

## 라이선스

이 스크립트는 교육 및 학습 목적으로 자유롭게 사용 가능합니다.
