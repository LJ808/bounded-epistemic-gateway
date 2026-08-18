---
title: Meta-Fallacy Construction — A Generative Pattern for Detecting Unknown Fallacy Types
type: synthesis
status: written up, prototype built — generative_fallacy_check() lives in ingest.py alongside open_check_claim() (unchanged), reachable via --generative-check. ast.parse clean, simulated-call verification confirms both the known-move-type path and the "other" candidate-category path.
vault: TRC
date: 2026-08-11
tags: [resilience]
---

# Meta-Fallacy Construction — Finding the Pattern Behind the 26 Named Categories

## Why this file exists

Twenty-six named categories cover what this project's own use turned up — the classical fallacy tradition, plus double-counting, found empirically on blackhole-002. Real argumentation carries more fallacy types than any fixed list names, named or not. [[next-steps-v1]]'s third priority (`open_check_claim()`) already exists to catch what the fixed list misses, but it asks one flat, holistic question — does the conclusion follow from the stated reasons — the same shape as non sequitur. Useful, but not generative: it can flag that something broke, but it gives no structure for naming what broke or why. This file looks for the pattern underneath the 26 categories that could generate new ones, rather than waiting for each new category to surface by accident the way double-counting did.

## The generative core: a legitimate move, missing its own licensing condition

Every AND-shape category in [[neuro-symbolic-fallacy-shapes-v1]] decomposes the same way once traced back to its two subconditions. Subcondition A names a reasoning move that works, sometimes. Subcondition B names the specific condition that move needs in order to actually work — and its absence.

- Appeal to authority: citing expertise works, sometimes. It needs evidence behind the credential. Missing that, it fails.
- False equivalence: reasoning by analogy works, sometimes. It needs the shared trait to outweigh the relevant differences. Missing that, it fails.
- Rushed conclusion: generalizing from a sample works, sometimes. It needs a representative sample. Missing that, it fails.
- Slippery slope: chaining consequences works, sometimes. It needs each link justified. Missing that, it fails.
- No true Scotsman: refining a definition works, sometimes. It needs to happen independent of the counterexample that just appeared. Missing that, it fails.

One shape, repeated: **valid move + missing licensing condition = fallacy.** Not two unrelated facts about an argument stitched together — one move, one broken precondition specific to that move.

This observation doesn't originate here. Argumentation theory already formalizes something close to this under the name argumentation schemes with critical questions — a catalog of reasoning patterns (argument from authority, from analogy, from cause, from example, from consequences, and others), each paired with the questions that must get answered for that specific pattern to hold. Douglas Walton's work builds this out in detail. Naming that prior work matters here: this file extends an existing framework into this project's own bounds-pair infrastructure, not a discovery built from nothing.

## Why this matters for finding categories nobody named yet

The 26 named categories enumerate specific (move, missing-condition) pairs the classical tradition already wrote down. But the generative pattern runs bigger than the list. Any legitimate reasoning move, paired with its own licensing condition left unmet, generates a fallacy — whether or not anyone already named it. The list samples a larger space. It doesn't define the space's boundary.

## A second axis: which condition-type gets violated

Cross the reasoning-move type against the type of condition that gets violated, and a grid appears:

- **Evidential sufficiency** — appeal to authority, appeal to ignorance, bandwagon: the move asserts something without enough backing
- **Relevance** — red herring, personal attack, tu quoque, origin attack: the move answers a different question than the one asked
- **Validity/structure** — circular argument, false choice, non sequitur: the move's logical shape breaks regardless of content
- **Independence of evidence** — double-counting: the move treats correlated support as if it came from separate sources
- **Boundary stability** — no true Scotsman, motte-and-bailey: the move quietly redraws its own terms mid-argument

The 26 named categories fill some cells in this grid. Others sit empty — not because no fallacy lives there, but because nobody built a name for that cell yet. Double-counting fills exactly one previously-empty cell: an evidence-aggregation move, violating independence, a condition-type the classical Latin-named tradition never built a category around because it came out of probability theory instead, a separate intellectual lineage.

## What this makes possible: a two-stage check instead of one flat question

`open_check_claim()` asks one question, all at once: does the conclusion follow? A generative version splits that into two real, separately-checkable stages:

1. **Identify the move.** What reasoning type does the argument actually use — authority, analogy, generalization, causal inference, chaining, redefinition, evidence aggregation, boundary shift, or something the fixed list doesn't name?
2. **Ask that move's own licensing question.** Not a generic "does this work" — the specific precondition that move's own logic requires.

A move that fails its licensing question, without matching any of the 26 named categories, becomes a real candidate for a new one — logged honestly, the same path double-counting took, not a shortcut around it.

## What got built: `generative_fallacy_check()`

Lives in `ingest.py` alongside `open_check_claim()`, which stays wired into the default pipeline unchanged. The prototype runs as two model calls:

- `identify_reasoning_move()` — Stage 1. Classifies the argument's move against eight named types (`REASONING_MOVE_TYPES`, each carrying its own licensing question) or an `"other"` the model names and licenses itself.
- `build_licensing_prompt()` + the Stage 2 call inside `generative_fallacy_check()` — asks the identified move's specific licensing question, scored as a bounds pair (reusing the same bounds-pair, four-state infrastructure [[neuro-symbolic-fallacy-screen-v1]] and [[neuro-symbolic-fallacy-shapes-v1]] already built), and separately asks whether a violation matches one of the 26 named categories or warrants a candidate new one.

Reachable via `--generative-check`, paired with `--claim` the same way `--bounds-pilot` already works. Kept as a separate function rather than overwriting `open_check_claim()` in place — the original stays exactly as it was, until a real decision gets made about replacing it.

## Verification, run against the real inserted code

`ast.parse()` confirms the file compiles clean. A simulated run (mock `_call_model` standing in for the live API, matching the same standing rule against live calls) confirmed both paths work: a known move type (`generalization`) produces a correctly-shaped result with `matches_existing_category: none` and no candidate category proposed, since the licensing condition holds; a forced `"other"` branch, with a genuinely violated licensing condition, correctly proposes a candidate new category name and definition, and correctly reads into `state: unknown` rather than a false clean pass.

## Where this stands, honestly

Per the same standing call already locked in [[neuro-symbolic-fallacy-screen-v1]]: no live model call runs against this code. Every result shown here came from simulated stand-in output, not a real API call, and this file names that plainly rather than implying otherwise.

Two further open questions this prototype doesn't resolve. First, the eight named move types in `REASONING_MOVE_TYPES` came from this write-up's own reasoning about what generates the existing 26 categories — they haven't been checked against a wider argumentation-theory source (Walton's own scheme catalog runs longer than eight), and a fuller pass might reveal move types this file's shorter list missed or mis-grouped. Second, and more basic: this entire generative framework — move + missing condition — describes AND-shape fallacies well, because that's exactly the shape it grew out of. It doesn't obviously extend to appeal to ignorance's OR-shape or non sequitur's single-condition shape without real, separate thought about what "a move's licensing question" even means for those shapes. Named here rather than smoothed over.
