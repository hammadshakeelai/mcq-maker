# MCQ Authoring Guide

This is the rulebook the agent follows when turning a document into a question set.
The goal is to test **real understanding** — questions that cannot be beaten by
answer-position patterns, elimination tricks, or guessing. Read this fully before
writing `questions.json`. The `validate_mcqs.py` script enforces the mechanical
parts; the judgement parts are on you.

## Categories (every topic should cover all three where the material allows)

1. **theory** — definitions, principles, factual understanding. Phrase so the student
   must *comprehend*, not merely *recognise* a sentence lifted from the source. Prefer
   "Which statement best describes X?" over "X is defined as ___" copied verbatim.
2. **problem_solving** — apply a formula, run a calculation, trace code/logic, debug,
   or solve a scenario. The work, not the recall, is the point.
3. **conceptual** — deep understanding beyond memorisation: *why*, *what happens if*,
   compare/contrast, find the flaw, predict the outcome, choose the best approach,
   transfer the idea to a new situation. Conceptual questions MUST carry a `level`.

## Conceptual difficulty levels (Bloom-ish) — `level` 1/2/3

- **Level 1 — Understand & Apply**: grasp a concept and use it in a straightforward,
  familiar case.
- **Level 2 — Analyze**: break down relationships, compare options, find the reason,
  spot the error in a worked example.
- **Level 3 — Evaluate & Create**: judge the best option, reason about trade-offs,
  handle a novel or edge scenario the source never spelled out.

Each level is scored **independently** with its own points (default L1=1, L2=2, L3=3,
configurable in `config.levelPoints`).

## Topic grouping (hard rule)

- Group every question under the topic/subtopic it comes from.
- **Never interleave topics.** All of Topic A's questions, then all of Topic B's.
- Within a topic the natural order is theory → problem_solving → conceptual(L1,L2,L3),
  but the engine handles ordering — just put each question under the right topic.

## Answer & option quality (strict, non-negotiable)

- **Exactly four options.** Set `answer` to the index of the correct one *as authored*.
  You do **not** need to pre-shuffle — the build step assigns balanced A/B/C/D positions
  across the whole set (uniform-ish, never more than two of the same position in a row)
  and the quiz re-shuffles on every attempt. Don't fight it by hand.
- **Plausible distractors.** Base each wrong option on a real misconception or a
  believable slip (off-by-one, swapped terms, right idea/wrong scope). A distractor a
  student can eliminate without knowing the material is a wasted option.
- **No giveaways:**
  - The correct option must **not** be the longest or most detailed. Keep all four
    options similar in length, grammar, and specificity. `validate_mcqs.py` flags a
    correct option much longer than the distractor average.
  - Avoid absolute words (**always / never / all / none / only**) — they telegraph
    true-vs-false. The validator warns on these.
  - Use **"All of the above" / "None of the above" rarely**, and only when genuinely
    correct. Don't use them as filler.
  - Don't let one option be grammatically the only one that fits the stem.
- **Never hint at the answer inline.** No bold, no "(correct)", no underlining, no
  trailing punctuation only on the right option. The stem and all four options are
  visually identical.
- **Answer goes at the END of each MCQ**, separated — the engine renders `Answer: C`
  after the four options (in the docx and the website answer-key view), never inline.
- **Explanation** (recommended, especially conceptual): one or two lines on why the
  answer is right *and* why the tempting distractors are wrong.

## Self-check before you finalise (the validator automates most of this)

- Run `python scripts/validate_mcqs.py <questions.json>`. Fix every ERROR; review WARNs.
- Confirm: 4 options each, valid `answer` index, conceptual has `level`, others don't.
- Confirm the printed correct-position distribution is balanced and streak-free.
- Eyeball a few questions: could a smart student who skipped the material still guess?
  If yes, the distractors are too weak — rewrite them.
