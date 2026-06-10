# Harness Framework: Robot Behavior Intelligence Research

## 🚀 세션 시작 체크리스트
새 세션을 시작할 때 반드시 수행하라:
1. `README.md`를 읽고 프로젝트 구조와 적용 방법을 파악한다.
2. 가상환경이 있는지 확인한다(`venv/`, `.venv/`, `conda` 환경 등). 있으면 해당 환경에서 작업한다.
   - conda: `conda activate <env>` / venv: `source venv/bin/activate`
3. `continuation_plan.md`가 있으면 읽고 이전 세션의 중단 지점부터 이어서 시작한다.

## 🧪 로봇 연구 프로토콜
- **수정 범위 (Write Scope)**: 모든 소스 코드 수정은 이 작업 레포지토리 내부에서 수행합니다. (단, `references/`는 읽기 전용 — 아래 참조)
- **환경 관리 (Environment)**: 패키지 설치 및 \`requirements.txt\`, \`environment.yml\` 생성/수정은 레포지토리 루트에서 관리합니다.
- **참조 범위 (Read Scope)**: \`references/\` 폴더의 오픈소스 코드를 분석하여 로직을 이식하되, 수정은 절대 금지합니다.
- **출처 표기**: `references/`에서 코드를 가져올 경우 `# From: references/repo_name/file.py`와 같이 주석을 남기십시오.
- **실험 기록**: 의미 있는 변화(알고리즘 교체, 핵심 파라미터 변경) 발생 시 `experiments/` 내에 기록을 남기십시오.

## 🤖 기술 스택 (Robot Learning)
- **Core**: Python, PyTorch (Device management: cuda/mps/cpu)
- **Policy**: Diffusion Policy, Flow Matching, ACT, etc.
- **Config**: Hydra (preferred), YAML
- **Data**: Zarr, HDF5, Gym/Robosuite environments
- **Experiment**: WandB, Tensorboard

## 🏗️ 아키텍처 가이드 (Robot Pipeline)
1. **Dataset/Replay Buffer**: Data loading & normalization
2. **Policy/Network**: Neural network architecture
3. **Environment Wrapper**: State/Action space mapping & observation stacking
4. **Trainer/Evaluator**: Training loops and simulation/real-world benchmarks

## 🖥️ 하드웨어 환경 (3-PC Workflow)
현재 프로젝트는 다음 3대의 환경을 오가며 개발됩니다. 코드를 설계할 때 이 환경의 제약을 반드시 고려하십시오.
1. **코딩용 PC (Local)**: GPU 없음. 코드 작성, 리팩토링, Git 관리 수행. (이 하네스가 주로 실행되는 곳)
2. **학습용 PC (Server)**: GPU 있음. 대용량 데이터 전처리 및 모델 학습 (WandB로 로깅).
3. **추론용 PC (Robot)**: GPU 있음. 로봇과 연결하여 실제 모델 추론 및 배포.
* **주의**: 코딩용 PC에는 GPU가 없으므로, 하네스 환경 내에서 코드를 테스트할 때는 CPU Fallback(`device='cuda' if torch.cuda.is_available() else 'cpu'`) 처리가 되어 있어야 합니다.

## 📝 개발 프로세스
- **Phase Execution**: `scripts/execute.py`를 사용하여 복잡한 리팩토링이나 구현 단계를 안전하게 수행하십시오.
- **Commit Message**: Scoped Conventional Commits 사용. **커밋 메시지(제목·본문)는 영어로 작성**한다. 괄호 안에 수정된 모듈 영역(`policy`, `env`, `data`, `config`, `harness` 등 베이스라인 이름이나 모듈)을 명시하고, **반드시 본문에 멀티라인(여러 줄) 상세 설명을 추가**하십시오. (예: `feat(policy): short description` + 본문 상세)
- 작업을 완료할 때마다 `experiments/`에 수정 사항 요약을 작성하십시오.

## 🤖 모델 선택 가이드
작업 복잡도에 따라 적절한 모델을 사용자에게 제안하라. 클로드는 실행 중인 세션의 모델을 변경할 수 없으므로, 인터랙티브 세션의 모델 선택은 **세션 시작 전**에 이루어진다. execute.py 실행 시에는 phase 기본값(`--model`) 또는 **step별 세분화** 둘 다 가능하다.

| 모델 | 적합한 작업 |
|---|---|
| **opus** | 신규 아키텍처 설계, 복잡한 알고리즘 구현, 다단계 추론이 필요한 phase |
| **sonnet** | 일반 코딩, 리팩토링, 대부분의 day-to-day 작업 (기본값) |
| **haiku** | 단순 수정, 문서 작성, 빠른 조회성 작업 |

execute.py는 step별 `model` 필드 → phase 기본값(`--model`) → sonnet 순으로 모델을 결정한다:
```bash
python3 scripts/execute.py <phase_dir> --model sonnet  # phase 기본값 지정
```
```json
// phases/<phase>/index.json — step별로 다른 모델 지정 가능
{ "step": 1, "name": "design", "model": "opus",   ... }
{ "step": 2, "name": "implement", "model": "sonnet", ... }
{ "step": 3, "name": "update-docs", "model": "haiku",  ... }
```

## 🛠️ 유틸리티 명령어
- `python scripts/execute.py <phase_dir> [--model MODEL]` # 클로드의 자가 교정 실행 (하네스 내부용)
- `python scripts/merge_to_main.py <feat-branch> [--push]` # feature 브랜치를 main에 병합 (pull→rebase→`--no-ff`)
- `python scripts/schedule_continuation.py [--in 2h30m | --reset-at HH:MM]` # 세션 재시작 예약 (인자 없으면 /usage로 리셋 시각 자동 조회)

### ⏰ 세션 연속 규칙
**리셋 시각은 `/usage`로 공식 조회한다 — 추측하지 않는다.** `schedule_continuation.py`는 시각 인자가 없으면 `claude -p "/usage"`를 실행해 **실제 세션 리셋 시각**을 읽어 그대로 예약한다(추정 아님). 토큰 잔량%도 같이 나온다. 사용자가 다른 시각을 원하면 `--in`/`--reset-at`으로 덮어쓴다.

#### 1. 큰 작업 시작 전 — 승인과 함께 예약 여부를 묻는다
`execute.py` 실행 등 **여러 step짜리 큰 작업을 시작하기 직전**, 평소 승인을 받던 그 타이밍에 다음을 함께 안내·선택받는다 (`AskUserQuestion` 사용):
1. 이 작업의 **대략적 토큰 소모량**을 규모감(작음/보통/큼)으로 알린다. 필요하면 `claude -p "/usage"`로 현재 사용률%를 조회해 근거로 제시한다.
2. 사용자에게 두 선택지를 제시한다:
   - **그냥 실행** — 바로 작업을 시작한다.
   - **자동 예약도 함께** — 한도에 걸려 끊길 때 세션 리셋 시각에 이어지도록 미리 예약해 둔다.
3. "자동 예약" 선택 시 `continuation_plan.md`를 작성한 뒤 아래 명령으로 예약한다(시각 인자 없이 실행하면 `/usage`의 리셋 시각으로 자동 예약).

#### 2. 작업 중/언제든 — 사용자가 예약을 지시하면
사용자가 "이어서 예약 걸어줘" / "N시간 M분 후에 예약" 처럼 말하면 클로드가 스스로 처리한다:
1. `continuation_plan.md`에 진행 상황과 다음에 할 일을 기록한다.
2. **모델**은 이어서 할 작업의 복잡도로 정한다 (모델 선택 가이드: 설계=opus / 일반=sonnet / 단순=haiku).
3. 예약한다 (세션ID·권한모드는 스크립트가 처리, 권한모드는 best-effort 감지 후 실패 시 CC 기본값):
   ```bash
   python3 scripts/schedule_continuation.py --model sonnet                  # /usage 리셋 시각 자동 조회
   python3 scripts/schedule_continuation.py --in 2h30m --model sonnet       # 사용자가 시각을 줬을 때 (상대)
   python3 scripts/schedule_continuation.py --reset-at 14:30 --model sonnet  # 사용자가 시각을 줬을 때 (절대)
   ```
4. 터미널에 카운트다운이 뜬다. 시간을 바꾸려면 Ctrl+C 후 다른 `--in`/`--reset-at`으로 재실행한다.

**스킬 경유 (대안)** — `/schedule-continuation` 스킬을 써도 된다.

### 🔀 main 병합 규칙 (CRITICAL)
사용자가 feature 브랜치를 **main에 병합**해달라고 요청하면:
- **반드시 `scripts/merge_to_main.py` 사용을 안내하라.** `git merge`/`git rebase`를 직접 치지 마라. 이유: 이 스크립트가 `pull --ff-only` → `rebase` → `--no-ff merge` 순서와 충돌 시 자동 abort를 보장한다.
- **클로드가 직접 실행하지 마라.** main/origin을 건드리는 작업이므로, 실행할 명령어(`python3 scripts/merge_to_main.py <feat-branch>`)를 제시하고 **사용자가 직접 실행**하게 하라. (사용자가 명시적으로 "네가 실행해"라고 하면 그때만 `--yes`를 붙여 실행)
- step 압축(squash)은 feature 브랜치 내부에서만 일어나며, main 병합 시에는 각 step 커밋을 그대로 보존한다.
