# Harness Framework: Robot Behavior Intelligence

이 저장소는 로봇 행동 지능(Diffusion Policy, Flow Matching 등) 연구를 위한 **드롭인(drop-in) 코드 하네스 템플릿**입니다. 작업할 베이스라인 레포지토리에 아래 하네스 파일들을 복사해 넣으면, 클로드와 함께 구조화된 워크플로우(탐색 → step 설계 → 자가 교정 실행)로 코드를 이식하고 실험할 수 있습니다.

## 적용 방법

상황에 맞는 **한 줄**을 복사해 실행하면 클론부터 세팅까지 끝납니다.

### ▶ 이미 코드가 있는 프로젝트에 적용 (adoption)

**적용할 프로젝트 레포 루트에서** 실행:

```bash
git clone https://github.com/hymmni/claude-harness-framework.git harness && python3 harness/install.py
```

`harness/`로 클론한 뒤 `install.py`가 파일 복사(비파괴) → `.gitignore` 병합 → 디렉토리 생성 →
클론 자가삭제까지 처리합니다. 기존 파일은 덮어쓰지 않으며, 기존 `CLAUDE.md`가 있으면 harness
버전을 `CLAUDE.harness.md`로 남겨 수동 병합하게 합니다. (대상 경로 확인을 건너뛰려면 끝에 ` --yes`)

### ▶ 빈 상태에서 새로 시작 (from scratch)

프로젝트 이름(`my-project`)만 바꿔서, **아무 곳에서나** 실행:

```bash
git clone https://github.com/hymmni/claude-harness-framework.git my-project && cd my-project && rm -rf .git && git init && rm install.py
```

템플릿을 프로젝트로 클론하고 git 이력만 새로 시작한 뒤 설치기를 제거합니다. 별도 세팅이 필요 없습니다.

### 적용 후 구성

```
CLAUDE.md        # 프로젝트 규칙 및 로봇 연구 프로토콜
.claude/         # 클로드 설정 및 커맨드 (harness, review)
docs/            # 아키텍처 가이드 (ARCHITECTURE, ADR, ROBOT_GUIDE)
scripts/         # 하네스 실행기 (execute.py, merge_to_main.py)
experiments/     # 실험 결과 기록 (LOG_TEMPLATE 활용)
references/      # 외부 오픈소스를 분석용으로 Clone (Read-only)
.gitignore       # harness 산출물 제외 규칙
```

하네스 파일과 작업 코드는 동일한 레포지토리의 `.git` 이력으로 함께 관리됩니다. 워크플로우 실행 시 `phases/` 디렉토리가 생성되어 step 정의와 실행 기록을 담습니다.

## 시작하기
상세한 사용법 및 클로드와의 협업 워크플로우는 `docs/ROBOT_GUIDE.md`를 참고하십시오.
