#!/usr/bin/env python3
"""Quality-bar self-check for a question set.

Usage:  python validate_mcqs.py path/to/questions.json

ERRORs must be fixed before building. WARNs are judgement calls to review.
Exit code is non-zero if any ERROR is found.
"""
from __future__ import annotations

import json
import re
import sys

import mcqlib

ABSOLUTE_WORDS = re.compile(r"\b(always|never|all|none|only|every|no)\b", re.IGNORECASE)
ALLOFABOVE = re.compile(r"\b(all|none)\s+of\s+the\s+above\b", re.IGNORECASE)


def main(path):
    data = mcqlib.load(path)
    errors, warns = [], []
    ids = set()

    topics = data.get("topics") or []
    if not topics:
        errors.append("no topics found")

    for topic in topics:
        tname = topic.get("name", "<unnamed>")
        cats_here = set()
        for q in topic.get("questions", []):
            qid = q.get("id", "<no-id>")
            tag = f"[{tname} / {qid}]"

            if qid in ids:
                errors.append(f"{tag} duplicate id")
            ids.add(qid)

            cat = q.get("category")
            cats_here.add(cat)
            if cat not in mcqlib.CATEGORY_ORDER:
                errors.append(f"{tag} bad category {cat!r}")

            lvl = q.get("level")
            if cat == "conceptual":
                if lvl not in (1, 2, 3):
                    errors.append(f"{tag} conceptual question needs level 1/2/3, got {lvl!r}")
            elif lvl not in (None, 0):
                warns.append(f"{tag} non-conceptual question has a level ({lvl}) — it is ignored")

            opts = q.get("options") or []
            if len(opts) != 4:
                errors.append(f"{tag} must have exactly 4 options, has {len(opts)}")
                continue
            if len(set(o.strip().lower() for o in opts)) != 4:
                errors.append(f"{tag} has duplicate options")

            ans = q.get("answer")
            if not isinstance(ans, int) or not (0 <= ans < 4):
                errors.append(f"{tag} answer index out of range: {ans!r}")
                continue

            # giveaway: correct option much longer than distractor average
            correct_len = len(opts[ans])
            distractor_lens = [len(o) for i, o in enumerate(opts) if i != ans]
            avg_d = sum(distractor_lens) / len(distractor_lens)
            if correct_len > 1.6 * avg_d and correct_len - avg_d > 25:
                warns.append(
                    f"{tag} correct option is much longer ({correct_len} vs avg {avg_d:.0f}) "
                    "— may be guessable"
                )

            # absolute words
            for i, o in enumerate(opts):
                if ABSOLUTE_WORDS.search(o):
                    warns.append(f"{tag} option {mcqlib.LETTERS[i]} uses an absolute word: {o!r}")
            if ALLOFABOVE.search(" ".join(opts)):
                warns.append(f"{tag} uses 'all/none of the above' — use sparingly, only if truly correct")

            if not q.get("explanation"):
                warns.append(f"{tag} no explanation (recommended, esp. conceptual)")

        if len(cats_here) < 2:
            warns.append(f"[{tname}] only covers categories {sorted(cats_here)} — consider more variety")

    # demonstrate the balanced shuffle on the whole set and report distribution
    flat = mcqlib.flatten(data)
    pos_report = ""
    if flat and not errors:
        shuffled = mcqlib.shuffle_set(flat, seed=12345)
        positions = [q["answer"] for q in shuffled]
        dist = {mcqlib.LETTERS[p]: positions.count(p) for p in range(4)}
        max_run = 1
        run = 1
        for i in range(1, len(positions)):
            run = run + 1 if positions[i] == positions[i - 1] else 1
            max_run = max(max_run, run)
        pos_report = f"position distribution {dist}, longest streak {max_run}"
        if max_run > 2:
            errors.append(f"balanced shuffle produced a streak of {max_run} (>2) — algorithm bug")

    print(f"Validated: {path}")
    print(f"  topics: {len(topics)}  questions: {len(flat)}")
    if pos_report:
        print(f"  balance: {pos_report}")
    for w in warns:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    print(f"  => {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
