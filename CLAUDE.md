# Harness Framework: Robot Behavior Intelligence Research

## 🚀 세션 시작 체크리스트
새 세션을 시작할 때 반드시 수행하라:
1. `README.md`를 읽고 프로젝트 구조와 적용 방법을 파악한다.
2. 가상환경이 있는지 확인한다(`venv/`, `.venv/`, `conda` 환경 등). 있으면 해당 환경에서 작업한다.
   - conda: `conda activate <env>` / venv: `source venv/bin/activate`
3. `docs/ARCHITECTURE.md`, `docs/ADR.md`, `docs/private/ENVIRONMENT.md`를 읽고 현재 구조·결정 이력·하드웨어 구성을 파악한다.
4. `phases/index.json`에서 `status: "pending"`인 phase가 있는지 확인해 이어서 할 작업이 있는지 파악한다.
5. `continuation_plan.md`가 있으면 읽고 이전 세션의 중단 지점부터 이어서 시작한다.

## 🧪 로봇 연구 프로토콜
- **수정 범위 (Write Scope)**: 모든 소스 코드 수정은 이 작업 레포지토리 내부에서 수행합니다. (단, `references/`는 읽기 전용 — 아래 참조)
- **환경 관리 (Environment)**: 패키지 설치 및 \`requirements.txt\`, \`environment.yml\` 생성/수정은 레포지토리 루트에서 관리합니다.
- **참조 범위 (Read Scope)**: \`references/\` 폴더의 오픈소스 코드를 분석하여 로직을 이식하되, 수정은 절대 금지합니다.
- **출처 표기**: `references/`에서 코드를 가져올 경우 `# From: references/repo_name/file.py`와 같이 주석을 남기십시오.
- **실험 기록**: 의미 있는 변화(알고리즘 교체, 핵심 파라미터 변경) 발생 시 `experiments/` 내에 기록을 남기십시오.

## 📐 아키텍처 & 기술 스택
이 프로젝트의 스택·구조·결정 이력은 `docs/ARCHITECTURE.md`(현재 구조 스냅샷)와 `docs/ADR.md`(결정-이유-트레이드오프 로그)가 단일 진처다. 구조에 영향을 주는 작업 전에는 반드시 두 문서를 먼저 확인하라.

CLAUDE.md 자체는 특정 기술 스택을 전제하지 않는다 — 실제 채택 스택(PyTorch/JAX 등), 파이프라인 구조는 프로젝트마다 다르므로 전부 `docs/ARCHITECTURE.md`·`docs/ADR.md`에서 확인하라. 하드웨어 환경(1대/여러 대 PC, GPU 유무, 디바이스 하드코딩 금지 등)은 `docs/private/ENVIRONMENT.md`(git 미추적, 로컬 전용 — 프로젝트 레포가 public일 수 있어 인프라 정보만 분리했다)에서 확인하라. 이 하네스를 새 프로젝트에 처음 적용할 때는 이 세 문서에 해당 프로젝트의 실제 스택·하드웨어를 채워 넣는다.

## 📝 개발 프로세스
- **기본 워크플로우 — 직접 세션 협업**: 새 설계나 구현 방향은 먼저 사용자와 논의해 확정한 뒤 진행한다. 작업 도중 설계 판단이 필요한 지점(접근 방식 선택, 시도가 실패했을 때의 다음 방향, 결과 해석)마다 먼저 확인받고, 사용자 모르게 재설계하지 않는다. 결과가 기대와 다르게 나오면 "안 됐다"로 뭉개지 말고, 무엇을 어떻게 시도했고 왜 그렇게 판단했는지 구체적으로 보고해 사용자가 직접 검증할 수 있게 한다.
- **`scripts/execute.py` (보조 도구, 예외적 사용)**: 설계가 이미 사용자와 합의되어 여러 step으로 기계적으로 쪼갤 수 있는 작업에만 쓴다. 여러 step을 자동 자가교정으로 연속 실행하는 도구라 중간 설계 판단이 사용자 확인 없이 이뤄질 수 있다 — 쓸지 여부와 phase/step 설계 자체도 실행 전에 사용자와 먼저 논의한다. 상세 워크플로우는 `harness` 스킬(`.claude/commands/harness.md`) 참고.
- **Commit Message**: Scoped Conventional Commits 사용. **커밋 메시지(제목·본문)는 영어로 작성**한다. 괄호 안에 수정된 모듈 영역(`policy`, `env`, `data`, `config`, `harness` 등 베이스라인 이름이나 모듈)을 명시하고, **제목은 명사형이 아닌 서술형(동사 중심 문장)으로** 작성하며, **반드시 본문에 글머리기호(`-`)를 사용한 멀티라인 상세 설명을 추가**하라. 예시:
  ```
  feat(policy): add diffusion head to transformer backbone

  - replace MLP decoder with DDPM noise predictor to match paper Sec 3.2
  - expose num_diffusion_steps as Hydra config key (default 100)
  - update forward() signature: obs_seq → (action_pred, noise_pred)
  ```
- 작업을 완료할 때마다 `experiments/`에 수정 사항 요약을 작성하십시오.

## 🤖 모델 선택 가이드
작업 복잡도에 따라 적절한 모델을 사용자에게 제안하라. 클로드는 실행 중인 세션의 모델을 변경할 수 없으므로, 인터랙티브 세션의 모델 선택은 **세션 시작 전**에 이루어진다. execute.py 실행 시에는 phase 기본값(`--model`) 또는 **step별 세분화** 둘 다 가능하다.

| 모델 | 적합한 작업 |
|---|---|
| **fable** | 최고 난이도 — 복합 연구 설계, 장시간 자율 작업, 가장 까다로운 디버깅 |
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
- `python scripts/tmux_autoresume.py [--session NAME]` # tmux에서 claude 실행 → 리밋 시 리셋 후 자동 "continue" (세션 이어가기, 권장)
- `python scripts/scheduler.py {--time HH:MM | --in 2h30m} [--resume <id> | --cmd "..."] --prompt "..."` # 지정 시각에 claude/명령 실행 (외부 터미널용)

### ⏰ 세션 연속 규칙
리밋을 넘겨 이어가는 방법은 작업 종류에 따라 다르다. **추측해서 시각을 자동계산하지 않는다** — 리셋 시각이 필요하면 `claude -p "/usage"`로 공식값을 조회한다.

#### ① 인터랙티브 작업 → tmux 자동 재개 (권장)
`tmux_autoresume.py`는 claude를 tmux 안에서 띄우고, 감시 창이 화면을 폴링하다 리밋을 감지하면 **리셋 시각에 같은 세션에 `send-keys "continue"`**를 보낸다. 새 프로세스 resume이 아니라 살아있는 세션에 입력을 꽂는 것이라 **fork가 없고**, 터미널을 닫아도 tmux라 생존한다.
```bash
python3 scripts/tmux_autoresume.py            # tmux 세션 띄우고 claude+감시기 시작, attach
```
한 번 띄워두면 그 뒤 리밋이 와도 무인으로 이어진다. (tmux 필요: `sudo apt install tmux`. 리밋 배너 문구가 버전마다 달라 감지 정규식 조정이 필요할 수 있다.)

#### ② execute.py(헤드리스) → 재진입으로 이어간다
execute.py는 `index.json`의 완료 step을 건너뛰므로, 리밋 등으로 중단돼도 **리셋 후 `python3 scripts/execute.py <phase>`를 다시 실행**하면 이어진다. 별도 예약 메커니즘이 없어도 된다. 원하면 그 재실행을 리셋 시각에 예약할 수 있다:
```bash
python3 scripts/scheduler.py --time HH:MM --cmd "python3 scripts/execute.py <phase>"
```

#### 큰 작업 시작 전 — 승인과 함께 안내한다
`execute.py` 등 여러 step짜리 큰 작업을 시작하기 직전(평소 승인 타이밍)에 `AskUserQuestion`으로:
1. 이 작업의 **대략적 토큰 소모 규모**(작음/보통/큼)를 알린다. 필요하면 `claude -p "/usage"`로 현재 사용률%를 근거로 제시한다.
2. **그냥 실행** vs **리셋 시각 재실행 예약도 함께**(②의 scheduler.py `--cmd`) 중 선택받는다.

> `scheduler.py`로 `--resume <현재 세션>`을 거는 것은 살아있는 세션에 동시에 발화하면 fork 위험이 있다. 인터랙티브 이어가기는 ①(tmux)을 쓰고, scheduler는 "새 세션 시작"이나 ②의 헤드리스 재실행에 쓴다.

### 🔀 main 병합 규칙 (CRITICAL)
사용자가 feature 브랜치를 **main에 병합**해달라고 요청하면:
- **반드시 `scripts/merge_to_main.py` 사용을 안내하라.** `git merge`/`git rebase`를 직접 치지 마라. 이유: 이 스크립트가 `pull --ff-only` → `rebase` → `--no-ff merge` 순서와 충돌 시 자동 abort를 보장한다.
- **클로드가 직접 실행하지 마라.** main/origin을 건드리는 작업이므로, 실행할 명령어(`python3 scripts/merge_to_main.py <feat-branch>`)를 제시하고 **사용자가 직접 실행**하게 하라. (사용자가 명시적으로 "네가 실행해"라고 하면 그때만 `--yes`를 붙여 실행)
- step 압축(squash)은 feature 브랜치 내부에서만 일어나며, main 병합 시에는 각 step 커밋을 그대로 보존한다.
