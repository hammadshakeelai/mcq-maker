#!/usr/bin/env python3
"""Build the deployable demo site in web/.

Regenerates the live demo that gets deployed to Vercel:
  - web/quiz.html  <- built from the bundled sample question set
  - web/banner.svg <- copied from assets/banner.svg

Run from the repo root (or anywhere — paths are resolved relative to this file):

    python scripts/build_site.py

Then deploy web/ as a static site (see DEPLOY.md). Re-run this whenever the
quiz template, the sample questions, or the banner change.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".claude" / "skills" / "mcq-maker"
SAMPLE = SKILL / "examples" / "sample_questions.json"
BUILD_QUIZ = SKILL / "scripts" / "build_quiz.py"
BANNER = ROOT / "assets" / "banner.svg"
WEB = ROOT / "web"


def main() -> int:
    WEB.mkdir(exist_ok=True)
    if not SAMPLE.exists():
        raise SystemExit(f"missing sample questions: {SAMPLE}")
    if not BANNER.exists():
        raise SystemExit(f"missing banner: {BANNER}")

    quiz_out = WEB / "quiz.html"
    subprocess.run(
        [sys.executable, str(BUILD_QUIZ), str(SAMPLE), str(quiz_out)],
        check=True,
    )
    shutil.copyfile(BANNER, WEB / "banner.svg")

    index = WEB / "index.html"
    print("Site ready in web/:")
    for f in sorted(WEB.iterdir()):
        print(f"  {f.name}  ({f.stat().st_size} bytes)")
    if not index.exists():
        print("  NOTE: web/index.html is missing — it is the landing page and "
              "should be committed alongside this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
