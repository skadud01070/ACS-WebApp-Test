# 빠른 시작 가이드

## 1분 안에 테스트 실행하기

### 1. 디렉터리 이동
```bash
cd tests-python
```

### 2. 테스트 실행 (headless 모드)

```bash
# Location 전체 테스트 (백그라운드 실행, 실패 시에만 스크린샷)
uv run pytest e2e/access/location/ --browser chromium

# 특정 테스트만
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_2_level_location_add_edit_delete --browser chromium
```

**진행 화면이 안 보이고, 실패 시에만 스크린샷/비디오가 `test-results/` 디렉터리에 저장됩니다.**

### 3. 실행 과정을 보고 싶다면

```bash
# --headed 옵션 추가
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_2_level_location_add_edit_delete --headed --browser chromium
```

## 테스트 종류

### Location 테스트

```bash
# 1단 장소 (추가 -> 수정 -> 삭제)
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_1_level_location_add_edit_delete --browser chromium

# 2단 장소 (부모 생성 -> 자식 추가/수정/삭제 -> 부모 삭제)
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_2_level_location_add_edit_delete --browser chromium

# 3단 장소 (부모들 생성 -> 자식 추가/수정/삭제 -> 부모들 삭제)
uv run pytest e2e/access/location/test_location_simple.py::TestLocationSimple::test_3_level_location_add_edit_delete --browser chromium
```

## 결과 확인

### 성공 시
```
================================ test session starts ================================
e2e/access/location/test_location_simple.py::TestLocationSimple::test_2_level_location_add_edit_delete PASSED [100%]
================================ 1 passed in 25.34s =================================
```

### 실패 시
```
================================ test session starts ================================
e2e/access/location/test_location_simple.py::TestLocationSimple::test_2_level_location_add_edit_delete FAILED [100%]

실패 정보가 표시되고 다음 파일들이 생성됩니다:
- test-results/test-location-simple-py-test-2-level-location-add-edit-delete-chromium/test-failed-1.png
- test-results/test-location-simple-py-test-2-level-location-add-edit-delete-chromium/video.webm
- test-results/test-location-simple-py-test-2-level-location-add-edit-delete-chromium/trace.zip
```

## 주요 옵션

| 옵션 | 설명 | 사용 예 |
|------|------|---------|
| `--browser chromium` | 브라우저 지정 (필수) | 기본 사용 |
| `--headed` | 브라우저 화면 표시 | 디버깅 시 |
| `--slowmo 1000` | 느리게 실행 (1초 대기) | 동작 확인 시 |
| `-v` | 상세 출력 | 이미 기본 설정됨 |
| `-s` | print 출력 표시 | 로그 확인 시 |

## 환경 설정

`.env.test` 파일 확인:
```env
BASE_URL=http://172.16.150.200:4021/
TEST_USER_EMAIL=superadmin
TEST_USER_PASSWORD=superadmin
```

## 트러블슈팅

### uv가 없는 경우
```bash
pip install uv
```

### 브라우저가 설치 안 된 경우
```bash
uv run playwright install chromium
```

### 로그인 실패
- `.env.test`의 계정 정보 확인
- 서버가 실행 중인지 확인 (`BASE_URL` 접속 가능한지)

## 더 자세한 정보

- 전체 가이드: `TESTING-GUIDE.md`
- Location 상세: `e2e/access/location/README.md`
- 전체 문서: `README.md`
