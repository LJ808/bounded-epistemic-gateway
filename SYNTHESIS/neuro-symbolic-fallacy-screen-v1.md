---
title: Neuro-Symbolic Structure for the Fallacy-Screen Layer
type: synthesis
status: pilot built — circular argument only, wired into ingest.py as circular_argument_screen(), demo-verified against eggs-003/covid-003/blackhole-002. Stops at demo-verified scope, Jay's call 2026-08-11 — see note at file end.
vault: TRC
date: 2026-08-11
tags: [resilience]
---

# Neuro-Symbolic Structure — A Way to Make Fallacy-Screen's Judgments Show Their Work

## Why this file exists

[[fallacy-screen-layer-v1]] built a real check: one model call takes a rewrite, tests it against twenty-six named categories, and returns a flat yes/no plus a category name. This works. [[fallacy-screen-worked-examples-v1]] proved it catches real gaps, including one the original list missed entirely. But the check itself stays opaque. One call goes in, one judgment comes out, and nothing in between stays visible or checkable. This file names a different way to build the same check, borrowed from a neuro-symbolic architecture called Logical Neural Networks (LNN), and points to exactly where it would close a real gap in the current design.

## What LNN adds that a single model call doesn't

An LNN structures a neural network so each neuron maps directly onto one piece of a logical formula — one neuron computes AND, another computes OR, another computes NOT. Truth doesn't collapse to a single number. Each neuron holds a bounds pair, a lower bound and an upper bound, so the network can distinguish four states instead of two: known-true, known-false, unknown (wide bounds, no evidence yet), and contradictory (bounds cross). Inference runs in either direction through the same neuron — a rule proves a conclusion from a premise, or a negated premise from a negated conclusion, using one structure rather than two.

Two gaps in the current Fallacy-Screen design map directly onto these two properties.

## Gap one: no bounded uncertainty

`screen_claim()` returns `fallacy_found: yes` or `fallacy_found: no`. [[fallacy-screen-worked-examples-v1]]'s own blackhole-002 result didn't fit cleanly into either box — the check caught a real pattern (later named double-counting, added as category twenty-six) that sat between "no fallacy" and "a fallacy from the existing list." The current schema forced that finding into a workaround: adding a new category, rather than representing the actual state, which sat closer to "flagged, unresolved, outside the current list" than to a clean yes or no.

An LNN-shaped version would return a bounds pair instead of one word. A rewrite with strong, unambiguous support for a fallacy gets bounds near (1, 1). A clean rewrite gets bounds near (0, 0). A genuinely unresolved case — evidence pointing toward a problem, but not conclusively — gets wide bounds, honestly representing the gap between "we found nothing" and "we found something definite." This gives the twenty-seventh, uncatalogued case [[fallacy-screen-layer-v1]] already warned about a place to land, instead of forcing it into a binary that hides the uncertainty.

## Gap two: no compositional structure

Each of the twenty-six categories gets tested by one model call against one flat prompt. The call either recognizes the pattern or it doesn't — nothing in the design breaks a category down into checkable parts. Circular argument, for instance, decomposes into two separate conditions: the conclusion appears again as a premise, AND no independent support exists anywhere else in the argument. Right now, one call judges both conditions at once, in one step, with no way to check which condition (if either) actually failed.

An LNN-shaped version would build each category as a small network of logical neurons, one neuron per condition, combined through an explicit AND, OR, or NOT gate matching the fallacy's real logical shape. This makes each finding auditable at the sub-condition level — a person (or a later check) could ask not just "did this rewrite trip the circular-argument neuron," but "which of the two conditions actually failed, and by how much."

## Where Direction of Error already assumes bidirectional inference

[[fallacy-screen-layer-v1]]'s schema already asks a bidirectional question without naming it as one: does the fallacy push toward over-confidence in the claim, or over-confidence in a rebuttal of the claim? Right now, one model call answers this as a second free-text field, generated in the same prompt as the fallacy-found judgment. An LNN-shaped version would compute Direction of Error as a real inference over the same structure that computed fallacy_found — proving the direction from the same neurons that proved the finding, rather than asking a second, separately-generated question about a result the first question already produced.

## Connection to Priority Three

[[next-steps-v1]]'s third priority, wired but not yet run for real, asks one open-ended question beneath the fixed list: does the conclusion actually follow from its stated reasons, whether or not any gap matches one of the twenty-six named categories? An LNN-shaped Fallacy-Screen doesn't close this gap by itself — it still needs a named category before it builds a neuron for it. But it changes what adding a twenty-seventh category costs. Right now, a new category means writing a new prompt and hoping the model recognizes the pattern consistently. Under an LNN structure, a new category means composing one new neuron from already-existing logical pieces (the AND/OR/NOT gates the network already holds), auditable the same way as every other category from day one.

## Where this stands, honestly

This file named the shape and the reasoning first, then a real pilot followed. `ingest.py` gained `circular_argument_screen()`, scoped to one category (circular argument), plus its supporting bounds functions (`combine_bounds_and()`, `bounds_state()`) and a `--circular-pilot` CLI flag covering the same three claims [[fallacy-screen-worked-examples-v1]] first tested. Not IBM's actual LNN library — a documented, plain-Python Godel/min-based simplification of AND, stated as such in the code's own comments. `ast.parse()` confirms the file compiles clean; `--demo --circular-pilot` confirms the CLI path runs and prints correctly-shaped bounds output for all three claims.

One real, open engineering question stays open regardless: IBM's LNN library targets general logical-inference tasks, not language-model output classification directly — wiring the actual library against `screen_claim()`'s pipeline (rewrite text in, categorical judgment out) would need real design work, not just a citation. This pilot doesn't attempt that; it tests the two structural ideas (bounds instead of binary, composed subconditions instead of one flat judgment) using plain Python standing in for the library.

Jay's call, 2026-08-11: this pilot stops here, at demo-verified scope. No live model call against a real API key runs against this code, and this file names that as a closed decision, not an open next step. The demo output above came from reasoning through the three claims' already-known ground truth, not from a live call — stated plainly, not implied. Whether an LNN-shaped version catches anything a live flat-schema call would miss stays a real, honestly-unanswered question this file doesn't resolve and isn't attempting to resolve going forward.
