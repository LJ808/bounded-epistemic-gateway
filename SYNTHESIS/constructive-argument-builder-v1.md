---
title: Constructive Argument Building — The Other Direction, and a Comparison to WFF 'N PROOF
type: synthesis
status: written up, prototype built — construct_argument() lives in ingest.py, reachable via --construct-argument. ast.parse clean, simulated-call verification confirms the pass and fail paths.
vault: TRC
date: 2026-08-11
tags: [resilience]
---

# Building a Sound Position — The Missing Other Half, and What WFF 'N PROOF Actually Offers Here

## Why this file exists

Everything in this project, up through [[meta-fallacy-construction-v1]], runs one direction: given an argument, find what breaks in it. `README.md` states the project's whole shape plainly — "a writing rule to catch hidden assumptions." Nothing built so far takes a target conclusion and helps build a sound case for it. This file names that gap, builds a prototype that closes part of it, and compares the result honestly against WFF 'N PROOF — a real, decades-old constructive logic tool this project already evaluated once, for a different purpose, in an earlier session.

## The insight already sitting in the detection code

`REASONING_MOVE_TYPES`, built for [[meta-fallacy-construction-v1]]'s detection prototype, pairs each reasoning move with its own licensing question. That table only ran backward there: given a finished argument, identify its move, then check whether the licensing condition got violated. The same table runs forward just as well: given a target conclusion and the evidence someone actually has, pick the move type that fits, then check whether the evidence satisfies that move's own licensing question *before* the argument gets written. Same data, opposite direction — detection asks "did this move fail," construction asks "will this move succeed, and if not, what's missing."

## What got built: `construct_argument()`

Takes two inputs instead of one: a target conclusion, and a description of the evidence actually in hand. Runs two stages, mirroring `generative_fallacy_check()`'s shape:

1. **`recommend_reasoning_move()`** — given the conclusion and the evidence, recommends which move type (from the same `REASONING_MOVE_TYPES` table, or a model-named "other") best connects the two.
2. **A prospective licensing check** — asks that move's own licensing question against the evidence actually available, scored as a bounds pair where high bounds mean the condition holds (the construction succeeds), not violated (the reversed framing from the detection side, named explicitly in the code to avoid confusing the two directions). If the condition doesn't hold, the result names the specific gap — what evidence would need to exist for this move to actually work — instead of either writing an unsupported argument anyway or refusing to say anything useful.

Demo case: target conclusion "regular exercise reduces cardiovascular disease risk," evidence "a single case study of one patient who started exercising and had improved cholesterol." Stage 1 recommends generalization. Stage 2 correctly finds the licensing condition unmet — one case can't represent a population — and names the real gap: a larger, representative sample, not a stronger restatement of the same one case.

## Comparison to WFF 'N PROOF

This project evaluated WFF 'N PROOF once already, in an earlier session, alongside IBM's LNN, without a stated application. Building a real constructive tool gives that comparison an actual target.

**What WFF 'N PROOF actually does.** Players roll dice bearing propositional variables (p, q, r, s, t) and operators (K=and, A=or, N=not, C=implies, E=equals, in prefix Polish notation). One player sets a Goal — a well-formed formula (WFF) to derive. Every other player tries to construct a complete, checkable proof of that Goal from stated Premises using stated Rules of inference. A completed proof stands or falls by mechanical, syntactic checking — any player at the table can verify each step against the fixed rule set, with no interpretive judgment involved.

**Where the two systems actually differ, not just in application:**

- **Formal validity versus material soundness.** WFF 'N PROOF only ever proves validity — does the conclusion follow from the stated premises by the stated rules? It never asks whether the premises hold true in the world, because its premises are just symbols, stipulated for the game, not real claims about anything. `construct_argument()` does the opposite: it never checks formal derivability (natural-language arguments don't reduce to K/A/N/C/E), and instead checks whether real evidence satisfies a real-world condition — does this sample represent that population, does this correlation rule out that alternative cause. A WFF 'N PROOF game can produce a perfectly valid proof from false premises. This tool can't accept a move at all without evidence that actually holds up.
- **Mechanical certainty versus bounded judgment.** A WFF 'N PROOF proof gets checked step by step, deterministically — right or wrong, no middle state. `construct_argument()`'s licensing check returns a bounds pair, because whether real-world evidence satisfies a real-world condition genuinely admits uncertainty, the same reason [[neuro-symbolic-fallacy-screen-v1]] built bounds instead of a flat yes/no in the first place. This tool never claims WFF 'N PROOF's kind of certainty, because the problem it addresses doesn't have that kind of certainty available.
- **Closed symbol set versus open natural language.** WFF 'N PROOF's entire universe is five operators and five variables — complete, fixed, and exhaustively defined by the rulebook. This tool works over open natural-language claims, which is exactly why it needs an LLM's judgment rather than a syntax checker, and exactly why it can't offer WFF 'N PROOF's guarantee.
- **Both genuinely constructive, at different layers of the same overall problem.** WFF 'N PROOF teaches the layer beneath this whole project: what does a valid inference step actually look like, stripped of any real-world content at all. This project's whole apparatus — E-Prime rewriting, fallacy detection, and now argument construction — operates one layer up, on real claims with real evidence, where validity alone was never the question. A perfectly valid deduction from a false or unsupported premise stays exactly as useless as a fallacious one; WFF 'N PROOF has no way to say so, because saying so requires stepping outside the symbols into the world the symbols supposedly describe. That step is this entire project's actual subject.

**The honest upshot:** WFF 'N PROOF doesn't compete with `construct_argument()` and doesn't inform its design beyond the general observation that both aim at construction rather than only critique. They solve genuinely disjoint problems — formal validity in a closed system, versus material soundness in an open one — and a tool built for one wouldn't transfer usefully to the other without losing exactly what makes each one work.

## Verification, run against the real inserted code

`ast.parse()` confirms the file compiles clean. A simulated run (mock `_call_model`, matching the standing rule against live calls) confirmed both paths: the exercise/cholesterol demo case correctly identifies generalization as the recommended move and correctly finds the licensing condition unmet, naming the real gap (sample size and representativeness) rather than either accepting the weak evidence or returning nothing useful; a second simulated case with genuinely sufficient evidence correctly returns a satisfied condition and no gap.

## Where this stands, honestly

Same standing call as everything else in this thread: no live model call runs against this code. Every result here came from simulated stand-in output.

Two further open limits, named plainly. First, `construct_argument()` only recommends and checks one move at a time — a real position often needs several moves chained together (a generalization feeding into a causal-inference step, for instance), and this prototype doesn't yet handle that composition. Second, a satisfied licensing condition tells you a move is defensible, not that the resulting argument reads well, connects to the rest of a real document, or survives `generative_fallacy_check()` run against the argument once actually written — construction and detection stay separate tools here, not yet closed into a loop where a constructed argument automatically gets screened before being trusted.
