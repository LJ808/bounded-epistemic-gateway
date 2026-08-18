---
title: Readme
type: reference
status: active
vault: TRC
date: 2026-08-17
tags: [resilience]
---

# Bounded Epistemic Gateway

*Formerly the FLF Epistemic Case Study Submission. This repository now holds two distinct things — read this page in full before assuming either one.*

---

## Two things live here

**1. A closed competition submission.** The original FLF entry — twelve claims across three case studies, testing whether a strict writing rule (E-Prime) surfaces hidden assumptions in confident-sounding sentences. Complete, submitted July 19, 2026, frozen since. Nothing below the "Original Submission" section changed after that date, and nothing in it should.

**2. An active tool, built after the submission closed.** Once the competition ended, the underlying question stayed open: can a system evaluate an arbitrary claim's reliability, not just rewrite it — and can it do so without ever needing to *trust* the model's memory of what a source actually said? The Bounded Epistemic Gateway answers that with three real guarantees, described below, extending FLF's own three-layer framework (Ingestion, Structure, Assessment) to a working state none of the three reached during the competition itself.

The full build history from close to now lives in [`POST-SUBMISSION.md`](POST-SUBMISSION.md) — a readable narrative. The complete, dated, bug-by-bug technical log lives in [`DEVELOPMENT.md`](DEVELOPMENT.md).

---

## Applied Purposeful Epistemology

The gateway operationalizes a simple discipline: knowledge only earns use once someone checks what it rests on, how reliable that rest is, and what it's for. Five questions govern every claim that passes through the pipeline —

- What do we know?
- How do we know it?
- How reliable does that knowledge stay?
- What purpose will it serve?
- How should it guide action or a decision?

The three layers below answer these in order. Ingestion answers the first two. Assessment answers the third. Structure answers the last two — a claim's reliability doesn't mean much sitting alone; it means something once it's weighed against, corroborated by, or contested by the other claims around it.

---

## What the gateway guarantees

**Verbatim quote fidelity, structurally enforced, not requested.** Early runs found the model's own "verbatim" quote field silently drifting from its source — a dropped comma, a corrected "that" into "which," once a full sentence gone. Prompt instructions naming the failure directly didn't hold across reruns. The real fix removes the failure mode instead of asking the model to avoid it: `original_quote` gets overwritten with the actual source text, pulled directly from the claim file, after the model's response clears its own shape checks. The model never needs to *reproduce* a quote character-for-character — the one operation that kept failing regardless of prompt wording. Confirmed clean on a real run: 3/3 verbatim, zero drift, including the one case that survived four earlier attempts.

**Local inference only — no data leaves the machine, no per-call cost.** Every check here runs against a local RKLLama model on dedicated hardware, not a cloud API. The neuro-symbolic bounds pass alone ran 12 real model calls in one session at zero marginal cost.

**Bounds-pair reasoning, not flat yes/no.** Every check returns a `[lower, upper]` truth interval — known-true, known-false, unknown, or contradictory — instead of collapsing genuine uncertainty into a forced binary. An early version of this check anchored on the prompt's own example numbers instead of reasoning independently; found by checking the model's own explanation text against the pattern, not just trusting a clean-looking result, then fixed at the prompt level across all four bounds-scoring functions in the codebase.

**A real, computed Structure Layer**, not a documented gap. Twelve claims, twenty-one checked pairs, a closed four-tag relation vocabulary (`supports`, `argues_against`, `combines_with`, `shares_open_question_with`), each with a defined bounds-propagation formula reasoned from what the tag actually means — corroboration pulls confidence up, contestation pulls it down, joint evidence combines rather than dilutes, and an unresolved shared question propagates nothing at all, honestly.

---

## Try it yourself

```
pip install -r requirements.txt
python3 ingest.py --demo
```

No account or key needed for `--demo`. The local pipeline (`build_local_corpus.py`, `run_local_neuro_symbolic.py`, `structure_layer.py`) needs no `ANTHROPIC_API_KEY` at all — see [`POST-SUBMISSION.md`](POST-SUBMISSION.md) for why that's a deliberate, permanent constraint on this codebase, not a temporary limitation.

---

## What's in this project

```
bounded-epistemic-gateway/
├── README.md                                  ← this file
├── POST-SUBMISSION.md                         ← readable narrative, competition close to now
├── DEVELOPMENT.md                             ← full dated technical log
├── ingest.py                                  ← original submission's two-layer pipeline + the
│                                                 neuro-symbolic bounds engine built after
├── build_local_corpus.py                      ← drives Ingestion/Assessment against a local model
├── verify_corpus.py                           ← retroactive quote-fidelity + E-Prime compliance checks
├── run_local_neuro_symbolic.py                ← single-claim bounds screening, local inference only
├── run_local_neuro_symbolic_batch.py          ← extends bounds screening to the full 12-claim set
├── structure_layer.py                         ← propagates bounds through the real claim graph
├── requirements.txt
├── CLAIMS/
│   ├── eggs-cvd-diabetes/{eggs-001,002,003}.md
│   ├── covid-origins/{covid-001,...,006}.md
│   └── black-holes/{blackhole-001,002,003}.md
├── SOURCES/                                    ← primary documents, including both COVID debate
│                                                 judges' full written decisions and CERN's full
│                                                 2008 LSAG safety report, not just summaries
├── CORPUS/                                     ← local-model-generated Ingestion/Assessment records
├── NEURO_SYMBOLIC_RUNS/                        ← bounds-screening output, per claim
├── STRUCTURE_LAYER_RUNS/                       ← propagated bounds, per claim, per run
└── SYNTHESIS/                                  ← the reasoning behind every layer, every fix,
                                                   every honestly-named limitation
```

---

## Original Submission

*Frozen July 19, 2026. Preserved below exactly as submitted — this section describes the competition entry, not the gateway built afterward.*

### Using a Writing Rule to Catch Hidden Assumptions

"Epistemic" means about how we know things. Not what we believe. How we check it.

**Case studies:** Eggs and heart disease. COVID's origin. Whether the world's largest particle collider could make a black hole.

**The main idea:** We use a strict writing rule called E-Prime. E-Prime bans every form of the word "to be" — no "is," no "are," no "was," no "were." That one rule forces a sentence to say what it actually rests on, instead of hiding behind a confident-sounding word like "is."

**How the pipeline worked:** Every claim passed through two steps.

Step one: rewrite the sentence in E-Prime. No interpretation yet. Just the mechanical rewrite.

Step two: check what the rewrite reveals. What did the original sentence hide? What stays unclear even after the rewrite? How could someone misuse it?

FLF reviewer Oly Sourbut suggested this two-step split. See [`SYNTHESIS/two-layer-architecture-v1.md`](SYNTHESIS/two-layer-architecture-v1.md) for the exact rules each step follows.

### Our main claim, stated plainly

**Rewriting a sentence in E-Prime makes a hidden assumption visible. It does not make lying or misreading impossible.**

Consider the problem this solves. A sentence like "eggs cause heart disease" sounds like a plain fact. It actually rests on a specific study, a specific group of people, and a specific way of adjusting the numbers. The word "cause" hides all of that. E-Prime forces the sentence to name what it rests on, because it can't use "cause" (or "is," or "means") to skip past that step.

Someone determined to mislead can still try. But now they have to add extra words to hide the gap, or leave a gap a careful reader can actually spot. Before E-Prime, they could hide the same gap inside one small, confident word.

We tested this claim two ways: ten different ways a reader could misread each of the original eight claims, and three ways a source could try to game the method. [`SYNTHESIS/adversarial-robustness-criterion-6.md`](SYNTHESIS/adversarial-robustness-criterion-6.md) holds the full results, including where the method falls short.

### What we got wrong or left unfinished, stated honestly

- **We used secondhand sources for two of three cases at first; closed by submission close.** All three cases originally worked from a summary, a write-up of a debate, or an FAQ page. By close, both COVID-debate judges' own written decisions and CERN's full 2008 LSAG safety report sat in the vault directly — not just the summaries that pointed to them. One secondhand gap remained at submission: the paper LSAG itself cites for collision-geometry detail (Giddings & Mangano, arXiv:0806.3381), never ingested.
- **Three open questions named; one partly answered by submission close.** Does one study's null result mean no effect exists, or just that the study lacked power to detect one? Does a post-2019 method's existence tell us anything about what a scientist could have done before 2019? Both stayed fully open. Which part of CERN's safety argument carries the most real weight got partly answered by reading the primary source directly — the two arguments run independently, not as one restated — but which one matters more stayed unstated anywhere we'd read.
- **One claim we caught and fixed.** We once wrote that this method gets better just by adding more computing power. We caught that we never actually tested it, and corrected the file to say so honestly.

### Contact

James Greathouse — james@senecacommons.com
Submitted: July 19, 2026
