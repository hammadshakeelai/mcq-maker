# mcq-maker

A reusable **Claude Skill** that turns any document (PDF, DOCX, slides, lecture
notes, textbook chapter, article) into a high-quality multiple-choice quiz —
delivered as both an **interactive single-file quiz website** and a **Word
(.docx) export**.

The questions are designed to test *real understanding*, not cramming, and the
quiz engine makes them impossible to game by answer-position patterns or
elimination tricks.

## What it produces

- **`*_quiz.html`** — one self-contained file (no server, no CDN). Practice and
  exam modes, sidebar navigation by topic/category/level, progress saving,
  keyboard shortcuts, a reshuffle/retry, and a one-click **Word export**.
- **`*.docx`** — questions grouped by topic → category → conceptual level, with
  the correct answer printed at the end of each MCQ and optional explanations.
  Exportable from the website (offline, dependency-free) or via `make_docx.py`.

## Question design

| Category | What it tests |
|---|---|
| **Theory** | definitions/principles, phrased for comprehension not recall |
| **Problem Solving** | apply a formula, calculate, trace logic, debug, solve a scenario |
| **Conceptual** | why / what-if / compare / find-the-flaw — split into 3 Bloom levels, **each scored independently** |

Answer positions are randomized and balanced across A/B/C/D with no streaks; the
correct option is never longer, marked, or hinted inline.

## Quick start

```bash
# 1. validate a question set    2. build the quiz site    3. (optional) Word doc
python .claude/skills/mcq-maker/scripts/validate_mcqs.py .claude/skills/mcq-maker/examples/sample_questions.json
python .claude/skills/mcq-maker/scripts/build_quiz.py    .claude/skills/mcq-maker/examples/sample_questions.json out_quiz.html
python .claude/skills/mcq-maker/scripts/make_docx.py     .claude/skills/mcq-maker/examples/sample_questions.json out.docx
```

Open `out_quiz.html` in any browser. Requirements: Python 3 (and `python-docx`
only for the optional CLI Word export — the in-browser export needs nothing).

## Using it as a skill

Working anywhere inside this repo, Claude Code auto-discovers the
`/mcq-maker` skill. Ask it to "make a quiz from `<file>`" and it follows
[`.claude/skills/mcq-maker/SKILL.md`](.claude/skills/mcq-maker/SKILL.md):
read the doc → identify topics → author non-gameable MCQs
(per [`authoring_guide.md`](.claude/skills/mcq-maker/references/authoring_guide.md))
→ write `questions.json` → validate → build the site and the docx.

To use it from any project, copy `.claude/skills/mcq-maker/` to
`~/.claude/skills/mcq-maker/`.

See the skill's `SKILL.md` for the full pipeline, the data schema, how to
preview/screenshot the quiz, and the development gotchas.
