---
title: Bounded Epistemic Gateway — Real 78-Call RKLLama Run, Priority-Flagged Analysis
type: run-report
status: complete
vault: TRC
date: 2026-08-18
tags: [bounded-epistemic-gateway, rkllama, review-priority, live-run]
---

# Real 78-Call RKLLama Run — Analysis and Comparison

**Run type:** Live, not reasoning-based. 78/78 calls complete, 0 failures, RKLLama Qwen2.5-14B on Board 2. Real data — first complete picture of what the gateway itself produces, as distinct from `artificial-hivemind-decomp-claude-eval-20260818.json`'s Claude-reasoning-only screen from earlier the same day.

**Claims tested:** `eggs-003` (egg/CVD dose-response), `covid-003` (furin cleavage site), `blackhole-002` (extra-dimension black hole formation) — the three pilot claims this project has tested since the original FLF submission, not the Artificial Hivemind decomposition from earlier today.

## State distribution

35 known-false, 41 unknown, 2 known-true. 0 contradictory.

| Claim | known-false | unknown | known-true | unknown rate |
|---|---|---|---|---|
| covid-003 | 5 | 20 | 1 | 77% |
| eggs-003 | 12 | 14 | 0 | 54% |
| blackhole-002 | 18 | 7 | 1 | 27% |

## Finding 1 — topic-dependent hedging, not uniform model behavior

Same model, same 26-category screen, same prompt structure across all three claims. The unknown rate varies by a factor of nearly 3x depending on which claim gets tested. `covid-003` — the virology claim, discussing the furin cleavage site and PRRAR sequence — draws far more hedged, wide-bounds responses than `blackhole-002`'s physics claim or `eggs-003`'s clinical-statistics claim.

This narrows an earlier read. A prior pass through the first 74 completed calls characterized the model's wide-bounds behavior as a general calibration-width property — the model runs wider than a tight human-reasoned screen would, full stop. That still holds directionally, but the magnitude depends heavily on subject matter. A general "this model hedges wide" statement undersells how much topic content itself drives the effect.

## Finding 2 — six categories run unknown regardless of topic

`appeal_to_ignorance`, `double_counting`, `false_equivalence`, `no_true_scotsman`, `part_to_whole_mixup`, `word_shift` land `unknown` on **all three claims**, independent of subject matter. This is a second, separate mechanism from Finding 1 — not topic-driven, category-driven. Something about how these six subconditions get asked, or what they ask the model to judge, produces wide bounds regardless of what claim sits underneath them.

Worth distinguishing going forward: a claim landing `unknown` on one of these six categories carries less specific signal about that claim than an `unknown` on a category that behaves cleanly elsewhere. The six categories may need their own prompt review — `build_bounds_prompt()`'s subcondition questions for these specifically, checked against whether they're inherently more ambiguous to score than the other twenty, or whether something in the phrasing invites hedging independent of content.

## Bound-width pattern (holds across full 78, consistent with the 74-entry partial)

known-false: mean width 0.151, range 0.1–0.3. unknown: mean width 0.39, range 0.1–1.0, with real overlap at the tight end. The overlap zone (0.1–0.3 width) is where a genuinely clean verdict and a genuinely uncertain one become hard to distinguish by width alone — explanation text remains the more reliable signal in that band than the bounds themselves.

## Review-priority breakdown (Extension 1 applied)

41 of 78 calls (53%) flag `high` under `review_priority()`. Full priority-tagged output: `NEURO_SYMBOLIC_RUNS/all-26-rkllama-with-priority.json`.

| Claim | High-priority count |
|---|---|
| covid-003 | 20 |
| eggs-003 | 14 |
| blackhole-002 | 7 |

Half the run's output now flags for closer review. Given Finding 1, that burden concentrates heavily on `covid-003` specifically rather than distributing evenly — a reviewer working through this run in priority order would spend the large majority of their attention on one claim, not spread evenly across three.

## What this changes about the addendum's Extension 2 case

The cross-family comparison proposed in `literature-engagement-addendum-v3.md` now has a sharper test than "do different models converge." With real topic-dependent and category-dependent hedging patterns established here, the real question for a second model (Ling or Kimi via OpenRouter) becomes: does it show the same topic skew toward `covid-003` specifically, and the same six systemically-hedging categories? Agreement on *which* claims and categories draw uncertainty — not just agreement on final states — would be the stronger signal, and either a match or a divergence on that specific pattern is more informative than a raw bounds-pair comparison alone.

## Thread closure — the two malformed field names

`blackhole-002/sunk_cost` and `blackhole-002/slippery_slope` both carried a garbled `*_location` field name in their raw output (`used_to_prime_rewrite_justify_forward_location`, `links_unjectedified_location`). Checked against `FALLACY_SHAPE_DATA` directly: the source code's own field keys are correct (`used_to_justify_forward`, `links_unjustified`) — the model itself typo'd the label when generating those two specific responses, not a prompt-construction bug. `fallacy_bounds_screen()` only reads `*_bounds` fields programmatically; `*_location` exists for human display only, so neither malformed key affected any computed state or bounds value. Closed — no code change needed, harmless model-output drift, distinct from the four YAML-breaking leaks fixed earlier tonight.

## Thread closure — why six categories hedge regardless of topic

Comparing subcondition question wording directly, real pattern: every category that lands `known-false` consistently asks whether a concrete, surface-detectable event occurred — "does the argument *cite* X," "*attack* Y," "*describe* Z as natural," "*introduce* topic W." Answerable from a literal surface read of two or three sentences.

All six systemically-hedging categories ask for an inferred relational or structural judgment instead: `appeal_to_ignorance` asks whether absence gets *treated as* proof; `double_counting` asks whether conclusions derive from *one shared* premise; `false_equivalence` asks whether a trait gets *identified* as shared; `no_true_scotsman` asks whether a counterexample *appears* against an implicit general claim; `part_to_whole_mixup` asks whether the argument *assumes* a property transfers; `word_shift` asks whether a repeated word's meaning *actually differs*. None of these six can be answered by detecting a marker — each requires the model to construct an interpretation of a relationship that the source text, at 2-3 sentences, often doesn't contain enough surface material to confidently rule in or out.

This reads as a genuine content-difficulty difference between category types, not a fixable prompt-wording defect. Two real options, not mutually exclusive, neither implemented: (1) route these six categories through `build_bounds_prompt()`'s existing `reference_passage` parameter more often, supplying more surrounding source text so the model has more material to judge the relational claim against; (2) accept the hedging as calibrated caution on a harder task type, and lean on `review_priority()` to route these six to human review by design rather than treating the hedge rate itself as a defect to fix. Jay's call on which, if either — this is a design decision about what these six categories should cost to run, not a bug fix.

## Comparison note against the earlier Claude-reasoning screen

Not a direct comparison — different claims (Artificial Hivemind's six decomposed claims vs. this run's three pilot claims). But one structural echo worth naming: the earlier reasoning-based screen landed 6 of 156 checks (3.8%) outside known-false. This live run lands 41 of 78 (53%) outside known-false. Different claim sets, different scale, but the gap is large enough to note plainly — Claude's own reasoning runs meaningfully tighter than RKLLama's 14B model does on comparable structural-fallacy screening. Whether that reflects better calibration or overconfidence stays an open question this comparison alone can't resolve; a real head-to-head on the *same* claims (running the Hivemind decomposition through RKLLama directly, or these three pilot claims through Claude's own reasoning) would answer it directly. Not done; a real next step if the question matters enough to spend the calls on it.
