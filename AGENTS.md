# Repository Guidelines
## 응답
- 필수 단어를 제외하고는 한글로 답변해줘.

## 프로젝트 구조 및 모듈 구성
- `main.py`는 최소한의 Python 진입점을 제공하며, 공용 유틸리티는 테스트 트리와 섞이지 않도록 인접 위치에 둡니다.
- `e2e/`에는 흐름별(`auth/`, `access/`) Playwright 기반 pytest 스위트가 있고, 재사용 가능한 픽스처는 `e2e/conftest.py`에 모여 있습니다.
- `employee/`와 `employee_add/`는 온보딩 시나리오에서 활용하는 이미지 자산이므로 읽기 전용으로 취급하십시오.
- `playwright-report/`는 최근 실행 결과물(스크린샷, trace, video)을 보관하므로 커밋 전 불필요한 스냅샷을 정리합니다.

## 빌드·테스트·개발 명령
- `uv sync`는 잠금된 의존성을 현재 환경에 설치합니다.
- `uv run pytest --headed -v --browser chromium`은 기본 상호작용 테스트 러닝을 수행하며, 필요 시 marker 혹은 추가 인자를 전달하십시오.
- `pytest -m smoke`는 uv 없이 빠르게 로컬 검증할 때 유용한 최소 시나리오 묶음입니다.
- `setup.bat`은 Windows 가상환경 생성, requirements 설치, Chromium 러untime 준비까지 1회 설정을 자동화합니다.
- `run-tests.bat`은 uv/venv 분기 처리를 캡슐화하고 headed Chromium을 기본값으로 실행하여 CI 스모크 검사에 적합합니다.

## 코딩 스타일 및 네이밍 규칙
- Python 3.11 기준 4칸 들여쓰기를 사용하고 black 호환 포맷을 유지하며, selector·helper 명칭은 의도를 드러나게 작성합니다.
- 테스트와 헬퍼 모듈 이름은 pytest 규칙(`test_*`)에 맞춰 시나리오 기반 슬러그(`test_reset_password.py`, `signin_flow.py`)로 지정합니다.
- Playwright selector는 의미 있는 상수로 묶고, 비직관적 대기 조건은 근거를 주석으로 설명합니다.

## 테스트 가이드라인
- `pytest.ini`에 정의된 marker(`smoke`, `location`, `auth`, `slow`)를 활용하고, 새 marker는 동일 파일에 선등록합니다.
- 사용자 흐름 단계마다 핵심 assertion 하나씩을 유지하고 비즈니스 규칙은 헬퍼 함수로 분리하여 trace 가독성을 확보합니다.
- 환경 변수 덮어쓰기는 `.env.test`에 기록하고 픽스처로 로드하며, 테스트 코드에 자격 증명을 직접 삽입하지 않습니다.
- PR 제출 전 `uv run pytest --browser chromium --video retain-on-failure`를 실행해 최신 아티팩트를 생성하고 회귀 여부를 확인합니다.

## 커밋 및 PR 가이드라인
- 최근 히스토리는 간결한 명령형 제목(`Initial upload to personal repo`)을 사용하므로, 동일한 톤을 유지하거나 범위가 큰 작업은 `type: summary` 형태의 Conventional Commit 접두어를 검토하십시오.
- 본문에는 관련 이슈 링크, 검증한 핵심 시나리오 목록, 실패 원인 설명에 도움이 되는 최신 `playwright-report/` 자산을 첨부합니다.
- PR 템플릿에는 변경 목적, 환경 설정 특이 사항, 실행한 테스트 명령과 요약 결과, 검토자 참고용 스크린샷 또는 trace 링크를 포함합니다.
