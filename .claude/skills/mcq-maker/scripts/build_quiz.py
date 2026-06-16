#!/usr/bin/env python3
"""Build a single-file quiz website from a question set.

Usage:
    python build_quiz.py <questions.json> [output.html]

Injects the JSON into templates/quiz_template.html (replacing the
__QUIZ_DATA__ placeholder inside the <script type="application/json"> tag)
and writes a fully self-contained HTML file. No server needed to view it.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "templates", "quiz_template.html")
PLACEHOLDER = "__QUIZ_DATA__"


def main(qpath, out=None):
    with open(qpath, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    with open(TEMPLATE, "r", encoding="utf-8") as fh:
        template = fh.read()
    if PLACEHOLDER not in template:
        raise SystemExit(f"placeholder {PLACEHOLDER} not found in template")

    # compact JSON, and keep it safe inside a <script> element
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace(PLACEHOLDER, payload)

    if out is None:
        base = os.path.splitext(os.path.basename(qpath))[0]
        out = os.path.join(os.path.dirname(os.path.abspath(qpath)), base + "_quiz.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Built quiz: {out}")
    print(f"  title: {data.get('title')}")
    n = sum(len(t['questions']) for t in data['topics'])
    print(f"  topics: {len(data['topics'])}  questions: {n}")
    print(f"  open it directly in a browser (file://) — no server required")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
