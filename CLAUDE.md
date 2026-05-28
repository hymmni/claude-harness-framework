# Harness Framework: Robot Behavior Intelligence Research

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

## 🛠️ 유틸리티 명령어
- `python scripts/execute.py <phase_dir>` # 클로드의 자가 교정 실행 (하네스 내부용)
