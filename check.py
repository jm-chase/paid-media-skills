"""check.py — run before pushing. This repo is public.

A skill written while working on a live account picks up the account's details: a
client name in an example, a real customer id in a command, a path with a username
in it. None of that is recoverable once pushed, because a public repo exposes every
commit it ever had, not just the current files.

    py check.py

The client denylist lives in an untracked file, not in here. Written inline it would
publish the very names it exists to keep out — the check would become the leak.
Create `.check-denylist`, one name per line, and keep it out of git.
"""

from __future__ import annotations

import io
import pathlib
import re
import sys

DENYLIST_FILE = ".check-denylist"
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}

PATTERNS = {
    "secret": re.compile(
        r"sk-ant-[A-Za-z0-9_-]{8,}|AIza[0-9A-Za-z_-]{20,}|GOCSPX-[A-Za-z0-9_-]{8,}"
        r"|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}|gh[ops]_[A-Za-z0-9]{20,}"
        r"|pplx-[A-Za-z0-9]{20,}|1//0[A-Za-z0-9_-]{20,}"),
    "local path": re.compile(r"[A-Za-z]:\\+Users\\+[^\\\s\"']+"),
    "real email": re.compile(r"[\w.+-]+@(?!example\.|test\.)[\w-]+\.[a-z]{2,}"),
}

# Ten digits in a row is a Google Ads customer id. These four are the documented
# placeholders; anything else is probably someone's account.
PLACEHOLDER_IDS = {"1234567890", "1234567809", "0123456789", "9999999999"}
CUSTOMER_ID = re.compile(r"\b\d{10}\b")


def denylist() -> re.Pattern | None:
    path = pathlib.Path(DENYLIST_FILE)
    if not path.exists():
        print(f"  note: no {DENYLIST_FILE} — client names are NOT being checked")
        return None
    names = [ln.strip() for ln in io.open(path, encoding="utf-8")
             if ln.strip() and not ln.startswith("#")]
    return re.compile("|".join(re.escape(n) for n in names), re.I) if names else None


def main() -> int:
    clients = denylist()
    findings: list[str] = []
    checked = 0

    for path in sorted(pathlib.Path(".").rglob("*")):
        if not path.is_file() or any(p in SKIP_DIRS for p in path.parts):
            continue
        if path.name == pathlib.Path(__file__).name:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        checked += 1
        lines = text.splitlines()

        for label, pattern in PATTERNS.items():
            for m in pattern.finditer(text):
                n = text[:m.start()].count("\n") + 1
                findings.append(f"{path}:{n}: {label} — {lines[n - 1].strip()[:90]}")

        for m in CUSTOMER_ID.finditer(text):
            if m.group(0) in PLACEHOLDER_IDS:
                continue
            n = text[:m.start()].count("\n") + 1
            findings.append(f"{path}:{n}: customer id {m.group(0)} — use a placeholder")

        if clients:
            for m in clients.finditer(text):
                n = text[:m.start()].count("\n") + 1
                findings.append(f"{path}:{n}: client name — {lines[n - 1].strip()[:90]}")

    for f in findings:
        print(f"  {f}")
    print(f"\n{checked} files checked — "
          + (f"{len(findings)} to fix before pushing" if findings else "clean"))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
