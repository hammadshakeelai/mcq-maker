"""Shared helpers for the mcq-maker skill.

Loads a question set, flattens it into the linear order the quiz uses
(topic -> theory/problem_solving/conceptual(L1,L2,L3)), and provides the
balanced, streak-free position shuffle that guarantees the answer-position
rules in references/authoring_guide.md.

The same balancing algorithm is reimplemented in JS inside the quiz template;
keep the two in sync if you change it.
"""
from __future__ import annotations

import json
import random

CATEGORY_ORDER = ["theory", "problem_solving", "conceptual"]
CATEGORY_LABEL = {
    "theory": "Theory",
    "problem_solving": "Problem Solving",
    "conceptual": "Conceptual Understanding",
}
LEVEL_LABEL = {
    1: "Level 1 — Understand & Apply",
    2: "Level 2 — Analyze",
    3: "Level 3 — Evaluate & Create",
}
LETTERS = ["A", "B", "C", "D"]


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def level_points(data):
    lp = (data.get("config") or {}).get("levelPoints") or {}
    out = {}
    for k in (1, 2, 3):
        out[k] = lp.get(str(k), lp.get(k, k))
    return out


def sort_key(q):
    cat = q.get("category")
    ci = CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else len(CATEGORY_ORDER)
    lvl = q.get("level") or 0
    return (ci, lvl)


def flatten(data):
    """Return questions in linear quiz order, each tagged with its topic name."""
    out = []
    for topic in data["topics"]:
        qs = sorted(topic["questions"], key=sort_key)
        for q in qs:
            item = dict(q)
            item["topic"] = topic["name"]
            out.append(item)
    return out


def balanced_targets(n, rng):
    """n target positions in 0..3: counts as even as possible, no run of 3+."""
    counts = [n // 4] * 4
    for i in range(n % 4):
        counts[i] += 1
    # randomise which positions get the remainder
    rng.shuffle(counts)
    result = []
    for _ in range(n):
        # candidates with stock left, excluding one that would form a run of 3
        avail = [p for p in range(4) if counts[p] > 0]
        if len(result) >= 2 and result[-1] == result[-2]:
            banned = result[-1]
            choices = [p for p in avail if p != banned] or avail
        else:
            choices = avail
        # prefer the highest remaining count to keep things balanced, break ties randomly
        top = max(counts[p] for p in choices)
        choices = [p for p in choices if counts[p] == top]
        pick = rng.choice(choices)
        result.append(pick)
        counts[pick] -= 1
    return result


def shuffle_question(options, answer, target, rng):
    """Return (new_options, new_answer_index) with the correct option at `target`."""
    others = [i for i in range(len(options)) if i != answer]
    rng.shuffle(others)
    slots = [None] * len(options)
    slots[target] = answer
    fill = iter(others)
    for s in range(len(options)):
        if slots[s] is None:
            slots[s] = next(fill)
    new_options = [options[i] for i in slots]
    return new_options, target


def shuffle_set(questions, seed=None):
    """Apply the balanced shuffle to a flattened list. Mutates copies, returns new list.

    Each returned question gains: shuffled `options`, correct `answer` index,
    and `answer_letter`.
    """
    rng = random.Random(seed)
    targets = balanced_targets(len(questions), rng)
    out = []
    for q, t in zip(questions, targets):
        nq = dict(q)
        opts, ans = shuffle_question(q["options"], q["answer"], t, rng)
        nq["options"] = opts
        nq["answer"] = ans
        nq["answer_letter"] = LETTERS[ans]
        out.append(nq)
    return out
