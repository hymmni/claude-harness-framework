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

## 세션 리밋 이어가기

세션 리밋(5시간)에 걸려도 작업이 끊기지 않게 하는 두 가지 방법이 있습니다.

### tmux 자동 재개 (`scripts/tmux_autoresume.py`) — 권장

claude를 tmux 안에서 띄우고, 감시 창이 화면을 폴링하다 리밋을 감지하면 **리셋 시각에 같은 세션에 `continue`를 자동 입력**합니다. 새 프로세스로 resume하는 게 아니라 살아있는 세션에 키를 넣는 방식이라 **대화가 갈라지지 않고**, 터미널을 닫아도 tmux라 생존합니다. 한 번 띄워두면 그 뒤는 무인으로 이어집니다.
```bash
sudo apt install -y tmux                       # 최초 1회
python3 scripts/tmux_autoresume.py             # 세션 띄우고 claude+감시기 시작 → attach
# 분리: Ctrl+b d   재접속: tmux attach -t claude-harness   창 전환: Ctrl+b 0/1
```

### 시각 예약 (`scripts/schedule_continuation.py`) — 보조

특정 시각에 **새 세션을 예약**합니다. 인자 없이 실행하면 `claude -p "/usage"`로 **공식 리셋 시각을 조회**해 그 시각에 예약합니다(추정 아님). 다른 시각은 `--in`/`--reset-at`으로 덮어씁니다. 세션 ID·권한 모드는 자동 처리됩니다.
```bash
python3 scripts/schedule_continuation.py                    # /usage 리셋 시각 자동 조회 후 예약
python3 scripts/schedule_continuation.py --in 2h30m         # 상대시간 (지금부터)
python3 scripts/schedule_continuation.py --reset-at 22:05   # 절대시각
```
또는 Claude Code에서 `/schedule-continuation` 입력 — Claude가 리셋 시각을 조회하고, 중단 계획을 `continuation_plan.md`에 기록하고 예약까지 처리합니다.

**임의 시각 예약 (`scripts/scheduler.py`):**
```python
# CONFIG 수정 후 실행
TARGET_TIME     = "07:00"   # 실행 시각 (24시간제)
SESSION_ID      = "abc123"  # 비워두면 새 세션
MODEL           = "opus"    # sonnet | opus | haiku  (비워두면 CC 설정값)
PERMISSION_MODE = "auto"    # auto | plan | acceptEdits | dontAsk  (비워두면 CC 설정값)
PROMPT          = "작업 내용을 여기에..."
```
```bash
python3 scripts/scheduler.py --in 2h30m --resume <session-id> --prompt "작업 내용"          # 상대시간
python3 scripts/scheduler.py --time 07:00 --resume <session-id> --model opus --permission-mode auto --prompt "작업 내용"  # 절대시각
```

스크립트를 켜둔 채로 두면 예약 시각에 자동 실행됩니다.
