# Docker 개발 환경

컨테이너는 리포지토리 전체를 `/workspace`에 bind-mount 합니다. 컨테이너 안에서 코드를 고치는
게 아니라, 평소처럼 호스트(VSCode 등)에서 코드를 고치면 컨테이너에 바로 반영됩니다. **코드를
고쳐도 이미지 재빌드는 필요 없습니다.** `requirements.txt`를 바꿨을 때만 재빌드하면 됩니다.

## 0. 최초 1회 준비

```bash
cp .env.example .env
```

## 1. 빌드 & 실행 (CPU)

```bash
docker compose build
docker compose run --rm dev bash
```

## 2. GPU 있는 학습 서버에서 실행할 때

서버에 [NVIDIA driver](https://www.nvidia.com/Download/index.aspx) +
[nvidia-container-toolkit](https://github.com/NVIDIA/nvidia-container-toolkit)이 설치되어
있어야 합니다.

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml run --rm dev bash
```

## 3. VS Code로 작업할 때 (Dev Containers)

1. [Dev Containers 확장](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   설치
2. `Cmd/Ctrl+Shift+P` → `Dev Containers: Reopen in Container`

컨테이너 안에 Node.js + Claude Code CLI도 같이 설치됩니다(`postCreateCommand`). VS Code 통합
터미널(컨테이너 안 터미널)에서 바로 `claude`를 실행하면, 코드 편집·실행이 전부 같은 셸에서
이뤄져 매 명령을 `docker compose exec`로 감쌀 필요가 없습니다.

### 왜 non-root `dev` 사용자로 도는가

Claude Code 로그인/플러그인 설정은 호스트의 `~/.claude`, `~/.claude.json`을 그대로
bind-mount해서 재사용합니다(`docker-compose.yml`). 이 마운트는 **컨테이너 경로가 호스트
경로와 완전히 같아야** 합니다 — Claude Code의 플러그인/마켓플레이스 설정(예:
`~/.claude/plugins/known_marketplaces.json`)이 절대경로를 그대로 저장하기 때문에, 경로가
다르면 플러그인/skill이 "설치는 됐는데 로드가 안 되는" 상태가 됩니다. 그래서
`docker-compose.yml`은 `${HOME}/.claude:${HOME}/.claude`처럼 호스트의 `$HOME`을 그대로 컨테이너
경로에도 써서 마운트하고, `HOME=${HOME}` 환경변수로 컨테이너 프로세스의 `$HOME`도 강제로
맞춥니다.

문제는 컨테이너가 **root로 돌면**, 이 마운트 경로 아래에서 root가 새로 만드는 모든
파일(세션 로그, 설정 캐시 등)이 호스트에 root 소유로 그대로 남는다는 것 — 즉 호스트의
진짜 `~/.claude`가 오염됩니다. 그래서 `.devcontainer/devcontainer.json`은 root가 아니라
`common-utils` feature로 만든 non-root `dev` 사용자로 돌고, `updateRemoteUserUID: true`가
컨테이너 시작 시 그 사용자의 UID/GID를 호스트 사용자에 자동으로 맞춰줍니다(하드코딩 없이
이식 가능). `onCreateCommand`의 `sudo mkdir -p "$HOME" && sudo chown dev:dev "$HOME"`는,
Docker가 마운트 대상 상위 디렉터리(`$HOME`)를 root 소유로 자동 생성해버리는 걸 다시
`dev` 소유로 되돌리는 보정 — 이게 없으면 `dev` 사용자가 `$HOME` 아래에 새 파일(npm 캐시
등)을 못 씁니다.

사용자 이름(`dev`)은 호스트 사용자 이름과 다를 수 있습니다 — `$HOME` 환경변수 오버라이드가
경로를 맞춰주기 때문에 리눅스 계정 이름/UID 자체는 임의값(고정 `dev`)이어도 됩니다.

호스트에 `~/.claude`가 아직 없으면(Claude Code를 host에서 써본 적 없으면) 빈 폴더가 자동
생성되고 컨테이너 안에서 최초 1회 로그인하면 됩니다. 단 `~/.claude.json`은 파일 하나를
바로 마운트하는 거라, 호스트에 그 파일이 아예 없는 상태로 컨테이너를 띄우면 Docker가 그
경로에 빈 디렉터리를 만들어버려 컨테이너 안 Claude Code가 깨질 수 있습니다 — 이 경우 호스트
에서 `claude`를 한 번 실행해 파일을 만든 뒤 컨테이너를 다시 띄우면 됩니다.

## 4. GUI 쓰기

호스트(Linux)에서 컨테이너의 X11 접근을 한 번 허용해야 합니다:

```bash
xhost +local:docker
```

그 다음 평소처럼 `docker compose run`하면 `DISPLAY`가 자동으로 전달됩니다.

## 5. 새 패키지가 필요할 때

컨테이너 안에서 바로 `pip install <패키지>`를 해도 그 컨테이너가 살아있는 동안만 유효합니다.
계속 쓸 패키지는 `requirements.txt`에 버전을 명시해서 추가한 뒤 `docker compose build`로
재빌드하세요.
