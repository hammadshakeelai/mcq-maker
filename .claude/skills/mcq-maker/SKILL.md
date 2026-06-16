---
name: mcq-maker
description: >-
  Generate a high-quality multiple-choice quiz from any document (PDF, DOCX,
  slides, lecture notes, textbook chapter, article). Produces an interactive
  single-file quiz website AND a Word (.docx) export. Use when asked to make
  MCQs / a quiz / test questions / practice questions from a file or topic, or
  to build, run, preview, or screenshot the quiz site. Questions test real
  understanding (theory / problem-solving / conceptual with Bloom levels),
  randomize answer positions with no streaks, and put the answer at the end of
  each MCQ. Verbs: make quiz, generate MCQs, build quiz, run quiz, export Word.
---

# mcq-maker

Turn a source document into a rigorous MCQ set, then ship it two ways:

1. **An interactive single-file quiz website** (`*_quiz.html`) — practice/exam
   modes, sidebar navigation, scoring by category and by conceptual level,
   localStorage progress, and a built-in **Word export** button.
2. **A Word `.docx`** — grouped by topic/category/level, answer at the end of
   each MCQ. Generated client-side in the browser (zero dependencies, works
   offline) or from the command line with `make_docx.py`.

The whole point is questions that test understanding, not recognition, and that
**cannot be gamed** by answer-position patterns or elimination tricks. The
engine guarantees the position rules; you supply good questions and distractors.

> **Paths below are relative to the repo root** (the `mcq-maker/` directory).
> The scripts live in `.claude/skills/mcq-maker/scripts/` and the template in
> `.claude/skills/mcq-maker/templates/`. Every command block here was run and
> works as written.

## The pipeline (agent path)

1. **Read the source document.** Plain text/Markdown: read directly. PDF:
   `python -c "import pypdf"` or `pdfplumber`; DOCX: `python-docx` (installed);
   PPTX: `python-pptx`. Extract the text — you only need the content, not
   layout.
2. **Identify topics/subtopics.** One `topics[]` entry each. **Never mix
   topics** in a single group.
3. **Author the questions** following
   [`references/authoring_guide.md`](references/authoring_guide.md) — three
   categories (`theory`, `problem_solving`, `conceptual`); conceptual split into
   3 Bloom `level`s. Plausible distractors, no giveaways, optional explanation.
4. **Write `questions.json`** to the schema in
   [`references/questions.schema.json`](references/questions.schema.json). Store
   options in any order with an `answer` index — **do not pre-shuffle**, the
   engine assigns balanced A/B/C/D positions for you.
5. **Validate**, then **build**. Fix every ERROR, review WARNs.

```bash
# from the repo root — swap in your own questions.json
python .claude/skills/mcq-maker/scripts/validate_mcqs.py path/to/questions.json
python .claude/skills/mcq-maker/scripts/build_quiz.py    path/to/questions.json path/to/quiz.html
```

`build_quiz.py` inlines the data into the template and writes a fully
self-contained HTML file (no server, no CDN needed to view or to export Word).

Optional command-line Word export (mirrors the in-browser button):

```bash
python .claude/skills/mcq-maker/scripts/make_docx.py path/to/questions.json path/to/quiz.docx
```

### Try it on the bundled demo

```bash
python .claude/skills/mcq-maker/scripts/validate_mcqs.py .claude/skills/mcq-maker/examples/sample_questions.json
python .claude/skills/mcq-maker/scripts/build_quiz.py    .claude/skills/mcq-maker/examples/sample_questions.json .claude/skills/mcq-maker/examples/sample_quiz.html
python .claude/skills/mcq-maker/scripts/make_docx.py     .claude/skills/mcq-maker/examples/sample_questions.json .claude/skills/mcq-maker/examples/sample_quiz.docx
```

## Run / preview / screenshot the quiz

The built HTML opens directly from `file://`, but serving it gives a clean URL
for browser automation:

```bash
# serve the folder containing the built HTML
cd .claude/skills/mcq-maker/examples && python -m http.server 8755 --bind 127.0.0.1
# then open http://127.0.0.1:8755/sample_quiz.html
```

Drive it with `chromium-cli` / Claude-in-Chrome: `navigate` to the URL,
`screenshot`, click a mode card, click options, use the sidebar chips. The page
exposes its internals as globals for headless checks — useful when the
screenshot pipe stalls (see Gotchas):

```js
// in the page console / javascript_tool — verify scoring without clicking
state.skipped = {};
QUESTIONS.forEach(q => state.answers[q.id] = shuffle[q.id].correct); // all correct
showResults();
computeScores();   // {correct, total, byCat, byLvl, pointsEarned, pointsMax}
```

```js
// verify the balanced shuffle: re-randomize and inspect distribution + streaks
buildShuffle();
const pos = QUESTIONS.map(q => 'ABCD'[shuffle[q.id].correct]);
// counts should be ~even and no run is longer than 2
```

**Verify the Word export without a real download** (a real download can trip
Chrome's "ask where to save" native dialog — see Gotchas):

```js
const CT='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>';
const RELS='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>';
const blob = zipStore([{name:"[Content_Types].xml",data:CT},{name:"_rels/.rels",data:RELS},{name:"word/document.xml",data:buildDocXml()}]);
const head = new Uint8Array(await blob.slice(0,2).arrayBuffer());
({size: blob.size, sig: String.fromCharCode(head[0],head[1])});  // sig === "PK" => valid
```

## What the quiz website has

- **Start screen**: pick **Practice** (instant feedback + explanations) or
  **Exam** (score only at the end) *before* any question; optional timer.
- **Navigation**: Next / Previous / Skip; sidebar to jump by topic → category →
  conceptual level → number, with per-question status (unanswered / answered /
  skipped / flagged) and filter pills.
- **Scoring screen**: overall, **by category**, and **by conceptual level scored
  independently** (configurable `levelPoints`, default L1=1/L2=2/L3=3); practice
  mode adds a full review list.
- **Word export** button (and one on the results screen).
- **Progress bar + counter**, **flag/bookmark** + flagged filter, **optional
  timer**, **retry/reshuffle** (re-randomizes positions), **keyboard shortcuts**
  (`1`–`4` select, `←`/`→` navigate, `F` flag, `S` skip), **localStorage**
  resume, **answer-key toggle** (hidden by default, never inline).

## Gotchas (things that actually bit during development)

- **The `.docx` export is a dependency-free pure-JS ZIP writer** (CRC32 + stored
  zip + minimal WordprocessingML), *not* a CDN library. It works fully offline.
  If you change `buildDocXml`/`zipStore` in the template, re-verify with the
  blob-signature snippet above — a malformed central directory makes Word
  silently refuse to open the file.
- **Chrome "Ask where to save each file"** turns the export button's download
  into a **native Save-As dialog that freezes all browser automation** (the
  extension disconnects until it's dismissed). Don't click the real download
  button in headless/automated runs — verify with the in-page blob snippet
  instead.
- **CDP `Page.captureScreenshot` can wedge on a tab** after heavy DOM work even
  while page JS stays responsive. Fix: open a **fresh tab** and re-navigate; the
  new tab resumes from localStorage and screenshots fine.
- **The balanced-position algorithm is implemented twice** — `balanced_targets`
  in `scripts/mcqlib.py` and `balancedTargets` in the HTML template. Keep them
  in sync; both guarantee even A/B/C/D counts with no run longer than 2.
- **Windows console mangles the em-dash** (shows `�`) in script output — the
  written UTF-8 files are correct; it's only the terminal echo.
- `validate_mcqs.py` WARNs on **absolute words** (always/never/all/none) in *any*
  option. That's fine when they sit in distractors; only worry if they cluster
  on, or are absent from, the correct answer in a telling way.

## Files

```
.claude/skills/mcq-maker/
  SKILL.md                       # this file
  scripts/
    mcqlib.py                    # shared: load, flatten, balanced shuffle, scoring
    validate_mcqs.py             # quality-bar self-check (run before building)
    build_quiz.py                # questions.json -> single-file quiz HTML
    make_docx.py                 # questions.json -> Word .docx (CLI, python-docx)
  templates/
    quiz_template.html           # the quiz engine (data injected at build time)
  references/
    authoring_guide.md           # how to write non-gameable MCQs (read this)
    questions.schema.json        # the questions.json contract
  examples/
    sample_questions.json        # demo input
    sample_quiz.html / .docx     # demo outputs (regenerable)
```

## Reuse on any document

Point the pipeline at a new `questions.json` you authored from the document.
To make `/mcq-maker` available outside this repo, copy
`.claude/skills/mcq-maker/` into `~/.claude/skills/mcq-maker/`.
