# Harness Framework: Robot Behavior Intelligence

이 저장소는 로봇 행동 지능(Diffusion Policy, Flow Matching 등) 연구를 위한 **드롭인(drop-in) 코드 하네스 템플릿**입니다. 작업할 베이스라인 레포지토리에 아래 하네스 파일들을 복사해 넣으면, 클로드와 함께 구조화된 워크플로우(탐색 → step 설계 → 자가 교정 실행)로 코드를 이식하고 실험할 수 있습니다.

## 적용 방법
작업 레포지토리 루트에 다음 파일/폴더를 복사합니다:
```
CLAUDE.md        # 프로젝트 규칙 및 로봇 연구 프로토콜
.claude/         # 클로드 설정 및 커맨드 (harness, review)
docs/            # 아키텍처 가이드 (ARCHITECTURE, ADR, ROBOT_GUIDE)
scripts/         # 하네스 실행기 (execute.py — step 순차 실행 및 자가 교정)
experiments/     # 실험 결과 기록 (LOG_TEMPLATE 활용)
references/      # 외부 오픈소스를 분석용으로 Clone (Read-only)
.gitignore       # 대용량 데이터/체크포인트 제외 규칙
```

하네스 파일과 작업 코드는 동일한 레포지토리의 `.git` 이력으로 함께 관리됩니다. 워크플로우 실행 시 `phases/` 디렉토리가 생성되어 step 정의와 실행 기록을 담습니다.

## 시작하기
상세한 사용법 및 클로드와의 협업 워크플로우는 `docs/ROBOT_GUIDE.md`를 참고하십시오.
