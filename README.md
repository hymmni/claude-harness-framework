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
CLAUDE.md        # 프로젝트 규칙 및 로봇 연구 프로토콜 (git 추적)
.claude/         # 클로드 설정 및 커맨드 (harness, review) — git 미추적
docs/            # 아키텍처 가이드 (ARCHITECTURE, ADR, ROBOT_GUIDE) — git 추적
  private/       #   PC/GPU 등 로컬 인프라 정보 (ENVIRONMENT.md) — git 미추적
scripts/         # 하네스 실행기 (execute.py, merge_to_main.py) — git 미추적
experiments/     # 실험 결과 기록 (LOG_TEMPLATE 활용) — git 미추적
references/      # 외부 오픈소스를 분석용으로 Clone (Read-only) — git 미추적
.gitignore       # harness 산출물 제외 규칙
```

`CLAUDE.md`와 `docs/`(단 `docs/private/` 제외)는 작업 코드와 함께 git 이력으로 관리되고, 나머지 하네스 파일(`.claude/`, `scripts/`, `experiments/`, `references/`, `docs/private/`)은 로컬 전용입니다 — 대상 프로젝트가 public 레포일 수 있어, 인프라 정보나 도구 자체는 굳이 공개하지 않도록 설계했습니다. 워크플로우 실행 시 `phases/` 디렉토리가 생성되어 step 정의와 실행 기록을 담습니다(역시 로컬 전용).

## 시작하기
상세한 사용법 및 클로드와의 협업 워크플로우는 `docs/ROBOT_GUIDE.md`를 참고하십시오.

## 세션 리밋 이어가기

세션 리밋(5시간)에 걸려도 작업이 끊기지 않게 하는 두 가지 방법이 있습니다.

### tmux 자동 재개 (`scripts/tmux_autoresume.py`) — 권장

claude를 tmux 안에서 띄우고, 감시 창이 화면을 폴링하다 리밋을 감지하면 **리셋 시각에 같은 세션에 `continue`를 자동 입력**합니다. 새 프로세스로 resume하는 게 아니라 살아있는 세션에 키를 넣는 방식이라 **대화가 갈라지지 않고**, 터미널을 닫아도 tmux라 생존합니다. 한 번 띄워두면 그 뒤는 무인으로 이어집니다.
```bash
sudo apt install -y tmux                       # 최초 1회
python3 scripts/tmux_autoresume.py             # 세션 띄우고 claude+감시기 시작 → attach
# 분리: Ctrl+b d   재접속: tmux attach -t claude-harness   창 전환: Ctrl+b 0/1
```

### 시각 예약 (`scripts/scheduler.py`) — 보조

특정 시각에 **세션을 시작/재개**하거나 임의 명령을 실행합니다. 외부 터미널에서 켜두면 예약 시각에 카운트다운 후 실행됩니다. (execute.py가 리밋으로 끊긴 경우 재실행 예약 등에 유용 — execute.py는 재진입 가능하므로 다시 돌리면 이어집니다.)
```bash
python3 scripts/scheduler.py --time 07:00 --prompt "작업 내용"                       # 새 세션을 07:00에 시작
python3 scripts/scheduler.py --in 2h30m --resume <session-id> --prompt "이어서..."   # 2시간 30분 뒤 특정 세션 재개
python3 scripts/scheduler.py --time 09:00 --cmd "python3 scripts/execute.py 0-mvp"   # 09:00에 phase 재실행
```
리셋 시각이 필요하면 `claude -p "/usage"`로 공식값을 확인하세요(`--time`에 사용). CONFIG 섹션(`scheduler.py` 상단)을 직접 편집해 인자 없이 실행할 수도 있습니다.
