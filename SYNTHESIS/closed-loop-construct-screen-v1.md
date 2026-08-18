---
title: Closing the Construct-Screen Loop — Why Iteration Doesn't Close the Symbolic System
type: synthesis
status: written up, prototype built — iterative_argument_refinement() lives in ingest.py, reachable via --iterative-refine. ast.parse clean, simulated-call verification confirms all four termination conditions.
vault: TRC
date: 2026-08-11
tags: [resilience]
---

# Closing the Loop — What Actually Changes, and What Doesn't

## Why this file exists

Jay asked directly: does closing `construct_argument()` and `generative_fallacy_check()` into a loop turn this project's apparatus into a closed symbolic system, the kind WFF 'N PROOF already is? The honest answer runs no, and the reasoning matters more than the answer — it names exactly what a closed symbolic system requires, and shows that iteration changes none of it. This file states that reasoning formally, then builds the loop anyway, because a real, bounded, honestly-terminating loop still adds real value even though it never becomes what WFF 'N PROOF already is.

## What a closed symbolic system actually requires

Five properties, together, not any one alone:

1. **A fixed, finite alphabet.** WFF 'N PROOF's entire vocabulary: five variables, five operators. Ten symbols, forever.
2. **Syntax rules for well-formedness that don't depend on meaning.** A WFF either parses under the grammar or it doesn't — no judgment call, no context.
3. **A fixed, finite set of inference rules.** The rulebook names every legal move in advance.
4. **Mechanical, non-interpretive checking of every step.** Any player can verify any proof by following the rules, with zero interpretation required anywhere.
5. **No reference outward, to anything beyond the symbols themselves.** A WFF 'N PROOF premise never needs to hold true in the world — it's stipulated for the game, checked only against other symbols.

## What looping construct_argument() and generative_fallacy_check() actually changes

Nothing on that list. Looping adds iteration — a control-flow property. None of the five properties above concern control flow.

- **The alphabet stays open.** Natural language, unbounded, the same reason this whole project needed an LLM rather than a parser from its first line of `ingest.py`.
- **"Well-formedness" stays semantic.** Whether a sample represents a population, whether a correlation rules out alternative causes — these depend on what the evidence actually says about the world, not on a grammar.
- **Every step still returns a bounds pair, not a binary.** [[neuro-symbolic-fallacy-screen-v1]] built bounds specifically to represent genuine uncertainty. Running a check twice instead of once doesn't remove that uncertainty from either run.
- **The loop still reaches outward, constantly.** Every round asks whether real evidence satisfies a real condition — exactly the outward reference property 5 forbids.

**One real, partial exception, worth naming precisely.** `REASONING_MOVE_TYPES` — eight move types, each with one fixed licensing question — genuinely is a small, closed, finite table, structurally close to a WFF 'N PROOF-style rulebook. Looping does apply that closed table repeatedly. But the table only decides *which question gets asked*. It never decides the answer — that stays an open, evidence-dependent, LLM-judged call every single pass through the loop. A closed rulebook wrapped around an open evaluator doesn't close the system it wraps; the closed part lives only in the dispatch logic, never in the verdict.

## The real cost the loop introduces that WFF 'N PROOF specifically avoids

WFF 'N PROOF games always terminate. Finite dice, finite symbol combinations, a stated Goal either gets proven from the available Premises and Rules, or the game ends — no other outcome exists. A construct-then-screen loop carries no equivalent guarantee. Nothing formally stops the two stages from oscillating: construct produces an argument, screen flags one fallacy, the next draft fixes that fallacy while reintroducing an earlier one, indefinitely. No proof of convergence exists anywhere in this loop, because none can exist for an open-ended, LLM-judged process the way one trivially exists for a finite symbol game.

**The more accurate description:** a bounded fixed-point search over argument-space, not a closed deductive system. It hunts for a draft that survives both checks at once, the way gradient descent hunts for a minimum — no guarantee of finding one, no guarantee of stopping cleanly if it doesn't. WFF 'N PROOF proves; this loop searches.

## What got built: `iterative_argument_refinement()`

A real, bounded loop, honest about its own lack of convergence guarantee:

1. **Stage 0 — gate on real evidence first.** Calls `construct_argument()` once. If the licensing condition doesn't hold (`state != known-true`), the loop stops immediately, before writing anything — no argument gets drafted from evidence that already failed its own licensing check. Returns `stopped_reason: insufficient_evidence`.
2. **Stage 1 — draft.** `write_argument_draft()` writes an actual E-Prime argument connecting the evidence to the conclusion via the confirmed move, incorporating any issues flagged by a prior round (a real revision attempt, not a blind re-generation).
3. **Stage 2 — screen.** The draft feeds into `generative_fallacy_check()` unchanged — same function, same contract, no special-casing for loop-generated input.
4. **Termination, checked every round, in this order:**
   - **Clean pass** (`screen_state == known-false`): the draft survives screening. `converged: True`.
   - **Oscillation detected**: this round's flagged issue matches an issue already flagged in an earlier round. Stops rather than looping blindly on a problem the loop has already failed to fix once.
   - **Max rounds exhausted** (default 3): stops with the real, unresolved state — not a forced success.

No fifth, hidden termination path exists. A loop that hits `max_rounds_exhausted` reports exactly that, with its full round-by-round history, rather than silently returning its best attempt as if it were a clean pass.

## Verification, run against the real inserted code

`ast.parse()` confirms the file compiles clean. Simulated runs (mock stage calls, matching the standing rule against live calls) confirmed all four termination paths fire correctly: insufficient evidence stops the loop before any draft gets written; a clean first-round pass converges immediately; a repeated flagged issue across two rounds triggers oscillation detection rather than a third blind attempt; and a loop that never resolves within the round cap reports `max_rounds_exhausted` honestly, carrying its full history rather than hiding the failure.

## Where this stands, honestly

Same standing call as everything else in this thread: no live model call runs against this code. Every verification result came from simulated stand-in output.

Two further limits, named plainly. First, oscillation detection here catches only exact repeats of the same flagged issue — a loop that cycles through three or four distinct-looking issues before returning to the first would exhaust its round cap before the simple repeat-check ever fires, a real gap this prototype doesn't close. Second, `write_argument_draft()`'s revision step hands the model a list of prior issues and trusts it to actually address them — nothing in this loop verifies that a "revised" draft differs meaningfully from its predecessor beyond what `generative_fallacy_check()` itself catches, which means a model that reworks surface wording without fixing the underlying gap could still consume a full round without real progress, indistinguishable from progress until the round cap forces the question.
