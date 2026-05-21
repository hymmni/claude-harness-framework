# Harness Framework: Robot Behavior Intelligence

이 저장소는 로봇 행동 지능(Diffusion Policy, Flow Matching 등) 코드를 효율적으로 이식하고 실험하기 위해 디자인된 **코드 하네스(Code Harness) 템플릿**입니다. 여러 개의 베이스라인 코드를 프로젝트 별로 관리하고, 오픈소스 레퍼런스를 참조하여 안전하게 코드를 이식(Porting)하는 워크플로우를 제공합니다.

## 구조 설명
```
harness_framework/
├── projects/      # 베이스라인 저장소를 Clone하여 개발하는 메인 작업 공간
├── references/    # 논문 등 외부 오픈소스를 분석용으로 Clone하는 공간 (Read-only)
├── experiments/   # 기능 이식 및 하이퍼파라미터 변경 등에 대한 실험 결과 기록 (LOG_TEMPLATE 활용)
├── docs/          # 하네스 사용 가이드 및 로봇 아키텍처 가이드 (ROBOT_GUIDE.md 참고)
└── scripts/       # 자동화 스크립트 도구 (클로드의 자가 교정 및 단위 실행기 등)
```

## 시작하기
상세한 사용법 및 클로드(Claude/Copilot)와의 협업 워크플로우에 대해서는 `docs/ROBOT_GUIDE.md`를 참고하십시오.
