#!/usr/bin/env python3
"""
현재 Claude Code 세션을 감지해, 세션 리셋 시각에 이어서 실행을 예약한다.

시각 인자가 없으면 `claude -p "/usage"` 로 **공식 리셋 시각을 조회**해 그대로 쓴다
(추정이 아니라 Claude Code가 알려주는 실제 값). 직접 지정도 가능하다.

자동 조회로 예약 (세션 리셋 시각에):
    python3 scripts/schedule_continuation.py

상대시간으로 예약:
    python3 scripts/schedule_continuation.py --in 2h30m

절대시각으로 예약:
    python3 scripts/schedule_continuation.py --reset-at 14:30

프롬프트 파일을 지정하려면:
    python3 scripts/schedule_continuation.py --prompt-file continuation_plan.md
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEDULER = Path(__file__).resolve().parent / "scheduler.py"
SESSIONS_DIR = Path.home() / ".claude" / "sessions"
CONTINUATION_PLAN_FILE = ROOT / "continuation_plan.md"

DEFAULT_PROMPT = """\
이전 세션에서 작업을 이어서 진행합니다.
continuation_plan.md 파일이 있으면 읽고, 중단된 지점부터 계속 진행하세요.
"""


def find_current_session() -> str | None:
    """환경변수에서 현재 세션 ID를 찾는다."""
    return os.environ.get("CLAUDE_CODE_SESSION_ID")


_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}


def _parse_usage_reset(text: str) -> tuple[int | None, datetime.datetime | None]:
    """`/usage` 출력에서 현재 세션 사용률(%)과 리셋 시각을 파싱한다.

    예: "Current session: 31% used · resets Jun 10, 7:10pm (Asia/Seoul)"
    파싱 실패 시 (None, None).
    """
    import re
    m = re.search(
        r"current session:\s*(\d+)%\s*used.*?resets\s+([A-Za-z]{3})\w*\s+(\d+),\s*"
        r"(\d+)(?::(\d+))?\s*([ap]m)",
        text, re.IGNORECASE | re.DOTALL)
    if not m:
        return None, None
    pct = int(m.group(1))
    month = _MONTHS.get(m.group(2).lower())
    day = int(m.group(3))
    hour = int(m.group(4))
    minute = int(m.group(5) or 0)
    if m.group(6).lower() == "pm" and hour != 12:
        hour += 12
    if m.group(6).lower() == "am" and hour == 12:
        hour = 0
    if month is None:
        return pct, None
    now = datetime.datetime.now()
    year = now.year
    reset = datetime.datetime(year, month, day, hour, minute)
    # 연말 경계: 파싱 결과가 과거면 내년으로 (예: Dec→Jan)
    if reset < now - datetime.timedelta(hours=1):
        reset = reset.replace(year=year + 1)
    return pct, reset


def fetch_usage_reset() -> tuple[int | None, datetime.datetime | None]:
    """`claude -p "/usage"` 를 실행해 현재 세션 사용률·리셋 시각을 조회한다.

    Claude Code가 알려주는 공식 값이다(추정 아님). 실패 시 (None, None).
    """
    try:
        r = subprocess.run(
            ["claude", "-p", "/usage"],
            capture_output=True, text=True, timeout=60,
        )
    except Exception:
        return None, None
    if r.returncode != 0:
        return None, None
    return _parse_usage_reset(r.stdout)


def detect_permission_mode() -> str | None:
    """현재 세션을 띄운 프로세스의 cmdline에서 --permission-mode 를 읽는다.

    세션이 `claude --permission-mode X` 로 시작됐을 때만 감지 가능하다.
    플래그 없이 시작했거나 런타임에 shift+tab으로 바꿨다면 디스크에 없어 None을 반환한다.
    """
    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session_id:
        return None
    pid = None
    for f in SESSIONS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            if data.get("sessionId") == session_id:
                pid = data.get("pid")
                break
        except Exception:
            continue
    if not pid:
        return None
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
        args = raw.split(b"\x00")
        for i, a in enumerate(args):
            if a == b"--permission-mode" and i + 1 < len(args):
                return args[i + 1].decode(errors="replace") or None
    except Exception:
        pass
    return None


def parse_duration(text: str) -> datetime.timedelta:
    """'2h30m', '90m', '45m', '1h' 형식의 상대시간을 timedelta로 변환한다."""
    import re
    m = re.fullmatch(r"\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*", text, re.IGNORECASE)
    if not m or (m.group(1) is None and m.group(2) is None):
        raise ValueError(f"잘못된 시간 형식: '{text}' (예: 2h30m, 90m, 1h)")
    return datetime.timedelta(hours=int(m.group(1) or 0), minutes=int(m.group(2) or 0))


def parse_args():
    p = argparse.ArgumentParser(description="세션 한도 해제 시각에 Claude 재시작을 예약한다.")
    p.add_argument("--reset-at", metavar="HH:MM",
                   help="한도 해제 시각 (자동 계산 불가 시 직접 지정)")
    p.add_argument("--in", dest="in_after", metavar="DURATION",
                   help="지금부터 상대시간 (예: 2h30m, 90m). --reset-at·자동계산보다 우선")
    p.add_argument("--prompt", metavar="TEXT",
                   help="재시작 시 전달할 프롬프트 (기본: continuation_plan.md 읽기 안내)")
    p.add_argument("--prompt-file", metavar="PATH",
                   help="프롬프트를 읽어올 파일 경로")
    p.add_argument("--model", metavar="MODEL",
                   help="모델 (sonnet | opus | haiku)")
    p.add_argument("--permission-mode", metavar="MODE",
                   choices=["auto", "plan", "acceptEdits", "dontAsk"],
                   help="권한 모드")
    return p.parse_args()


def main():
    cli = parse_args()

    session_id = find_current_session()

    # 세션 ID
    if not session_id:
        print("  ERROR: CLAUDE_CODE_SESSION_ID 환경변수를 찾을 수 없습니다.")
        print("  Claude Code 세션 안에서 실행하세요.")
        sys.exit(1)

    # 예약 시각 결정: 사용자 명시값(--in/--reset-at)이 우선.
    # 둘 다 없으면 `/usage`로 공식 리셋 시각을 조회해 그대로 쓴다 (추정 아님).
    if cli.in_after:
        try:
            delta = parse_duration(cli.in_after)
        except ValueError as e:
            print(f"  ERROR: {e}")
            sys.exit(1)
        reset_time = datetime.datetime.now() + delta
        time_source = f"상대시간 (+{cli.in_after})"
    elif cli.reset_at:
        t = datetime.datetime.strptime(cli.reset_at, "%H:%M").time()
        reset_time = datetime.datetime.combine(datetime.date.today(), t)
        if reset_time <= datetime.datetime.now():
            reset_time += datetime.timedelta(days=1)
        time_source = "직접 지정"
    else:
        print("  /usage 로 현재 세션 리셋 시각을 조회합니다...")
        pct, reset_time = fetch_usage_reset()
        if reset_time is None:
            print("  ERROR: /usage 조회/파싱에 실패했습니다. 시각을 직접 지정하세요.")
            print("  상대시간:  python3 scripts/schedule_continuation.py --in 2h30m")
            print("  절대시각:  python3 scripts/schedule_continuation.py --reset-at HH:MM")
            sys.exit(1)
        pct_str = f"{pct}% 사용 중, " if pct is not None else ""
        time_source = f"/usage 조회 ({pct_str}공식값)"

    # 프롬프트 결정
    if cli.prompt:
        prompt = cli.prompt
    elif cli.prompt_file:
        try:
            prompt = Path(cli.prompt_file).read_text()
        except FileNotFoundError:
            print(f"  ERROR: 프롬프트 파일 {cli.prompt_file} 을 찾을 수 없습니다.")
            sys.exit(1)
    elif CONTINUATION_PLAN_FILE.exists():
        plan = CONTINUATION_PLAN_FILE.read_text().strip()
        prompt = f"이전 세션에서 작업을 이어서 진행합니다.\n\n[중단 시점 계획]\n{plan}"
    else:
        prompt = DEFAULT_PROMPT

    # scheduler.py 호출
    # --in(상대시간)은 그대로 전달한다. HH:MM으로 변환하면 scheduler의 next_target이
    # 24시간 이내 다음 발생으로 해석해 24h 이상 예약이 틀어지기 때문.
    cmd = [
        sys.executable, str(SCHEDULER),
        "--resume", session_id,
        "--prompt", prompt,
        "--yes",
    ]
    if cli.in_after:
        cmd += ["--in", cli.in_after]
    else:
        cmd += ["--time", reset_time.strftime("%H:%M")]
    if cli.model:
        cmd += ["--model", cli.model]

    # permission mode: 명시값 우선, 없으면 현재 세션에서 best-effort 감지
    perm_mode = cli.permission_mode or detect_permission_mode()
    perm_source = "직접 지정" if cli.permission_mode else ("현재 세션 감지" if perm_mode else "감지 불가 → CC 기본값")
    if perm_mode:
        cmd += ["--permission-mode", perm_mode]

    remaining = reset_time - datetime.datetime.now()
    h, rem = divmod(int(remaining.total_seconds()), 3600)
    m = rem // 60
    remaining_str = f"{h}시간 {m}분 후" if h else f"{m}분 후"

    print(f"\n  세션 연속 예약")
    print(f"  세션 ID : {session_id}")
    print(f"  실행 시각: {reset_time.strftime('%H:%M')}  ({remaining_str}, {time_source})")
    print(f"  모델    : {cli.model or '(CC 기본값)'}")
    print(f"  권한 모드: {perm_mode or '(CC 기본값)'}  ({perm_source})")
    if CONTINUATION_PLAN_FILE.exists():
        print(f"  계획 파일: continuation_plan.md")
    print(f"  프롬프트: {prompt[:80].strip()}{'...' if len(prompt) > 80 else ''}")
    print()

    subprocess.run(cmd)


if __name__ == "__main__":
    main()
