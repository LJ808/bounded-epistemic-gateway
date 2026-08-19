---
title: Neuro-Symbolic Fallacy-Screen — Shape Classification for the Remaining 24 Categories
type: synthesis
status: built — FALLACY_SHAPE_DATA and the generalized bounds engine (build_bounds_prompt(), fallacy_bounds_screen(), demo_bounds_output()) live in ingest.py, wired via --bounds-pilot. ast.parse and demo-mode verified against all 24 categories.
vault: TRC
date: 2026-08-11
tags: [resilience]
---

# Shape Classification — Approach C for the Remaining 24 Fallacy Categories

## Why this file exists

[[neuro-symbolic-fallacy-screen-v1]] built and demo-verified one category — circular argument — as a pilot. Twenty-four categories remained from the original 25 (double-counting, the 26th, sits outside this framework entirely — see the note at this file's end). Three approaches existed for extending the pilot: generalize the engine first and fill in data after, copy circular argument's exact pattern 24 more times, or classify every category by its actual logical shape before writing any code. This file records that third pass, chosen because circular argument's shape — two subconditions, both required — doesn't fit every fallacy honestly. Appeal to ignorance needs an either-suffices structure, not a both-required one. Forcing every category into one shape would mean either bad subcondition design or silently reverting to a flat call for the categories that don't fit — defeating the reason this pilot exists.

## The three shapes found

**AND (22 of 24).** Both subconditions must hold together for the fallacy to register. This is circular argument's own shape, generalized. Almost every category in the original 25-item list decomposes this way once broken into its two real components — a claim about the argument's structure, plus a claim about what that structure leaves out or fails to justify.

**OR (1 of 24) — appeal to ignorance.** Two genuinely alternative manifestations, either one sufficient on its own: treating an absence of disproof as proof, or treating an absence of proof as disproof. These aren't two conditions that both need to hold — they're two different ways the same fallacy can show up, and checking for "both" would misrepresent what the fallacy actually is.

**Single condition (1 of 24) — non sequitur.** One holistic judgment — does the conclusion fail to follow from the stated reasons — that doesn't cleanly split into two independently checkable subconditions the way the others do. Scored directly, no combination step.

## Full breakdown by group

**structural_and_formal** (4 remaining, circular argument already piloted separately):
- False choice — AND: presents exactly two options as exhaustive; more options genuinely exist
- Part-to-whole mixup — AND: assumes a property of parts holds for the whole (or the reverse); gives no separate justification for that transfer
- Word-shift — AND: a key term repeats; its meaning actually differs between occurrences
- Non sequitur — single: conclusion fails to follow from stated reasons

**causal_and_statistical** (6):
- False cause — AND: correlation established; causation asserted without ruling out alternatives
- Rushed conclusion — AND: evidence base is narrow or atypical; conclusion claims general applicability
- Survivorship bias — AND: only surviving cases examined; failed cases exist and go unaccounted for
- Ignoring the base rate — AND: relies on a vivid exceptional example; a known typical base rate goes contradicted or ignored
- Texas sharpshooter — AND: pattern identified after the fact; framed as if predicted in advance
- Gambler's fallacy — AND: cites past independent outcomes; claims they change the odds of the next independent outcome

**persuasion_instead_of_evidence** (7):
- Appeal to authority — AND: invokes status or credentials; offers no evidence alongside that status
- Personal attack — AND: attacks the source's character; leaves the actual argument unaddressed
- Origin attack — AND: dismisses a claim by its origin; leaves the claim's current merits unevaluated
- Straw man — AND: restates an opposing position; that restatement runs weaker than the real one
- Red herring — AND: introduces an irrelevant topic; that topic substitutes for addressing the real question
- Bandwagon — AND: cites popularity or widespread acceptance; offers that popularity as the actual support for truth
- Tu quoque — AND: points to the opponent's own inconsistency; leaves the opponent's actual point unaddressed

**shifting_the_boundaries** (7):
- Slippery slope — AND: claims one small step leads to a long chain of consequences; fails to justify each link in that chain
- No true Scotsman — AND: a counterexample to a general claim appears; the definition then narrows ad hoc to exclude it
- Motte-and-bailey — AND: advances a bold claim; retreats to a much weaker one under challenge while treating the two as equivalent
- Appeal to nature — AND: calls something natural; equates that with safe or good without independent support
- Sunk cost — AND: cites an amount already invested; uses that past investment to justify the decision going forward
- False equivalence — AND: identifies one trait two things share; treats them as equivalent while other relevant differences go unaddressed
- Appeal to ignorance — OR: absence of disproof treated as proof, or absence of proof treated as disproof

## What got built from this classification

`ingest.py` gained a generalized engine rather than 24 bespoke functions:

- `FALLACY_SHAPE_DATA` — one dict entry per category, holding its display name, its `FALLACY_CATEGORIES` group tag, its shape (`and`/`or`/`single`), and its subcondition question(s).
- `build_bounds_prompt()` — builds one bounds-pair prompt from any entry's shape and subconditions, generalizing `CIRCULAR_ARGUMENT_PROMPT`'s format.
- `fallacy_bounds_screen()` — calls the model once per category, combines the returned subcondition bounds under the category's assigned shape (`combine_bounds_and()` or the new `combine_bounds_or()`, or a straight pass-through for the single-condition case), and reads the result into one of the four states [[neuro-symbolic-fallacy-screen-v1]] already defined.
- `demo_bounds_output()` — generates a pre-recorded demo result for any category against the standard demo claim, without hand-authoring 24 separate dicts.
- `--bounds-pilot {category}` and `--claim {eggs-003,covid-003,blackhole-002}` — new CLI flags, paired the same way `--circular-pilot` already worked.

Circular argument's own dedicated function stayed untouched rather than getting folded into the generic engine — it already worked, already carried its own demo verification, and rewriting a working piece to fit a new abstraction risked the vault's own standing rule against touching what isn't part of the current task.

## Verification, run against the real inserted code

`ast.parse()` confirms the file compiles clean after all edits. A full sweep confirmed all 24 categories produce valid demo output through `demo_bounds_output()`, and all 24 build a fully-resolved prompt (no leftover `{original_quote}`/`{e_prime_rewrite}` placeholders) through `build_bounds_prompt()`. The AND and OR combination rules were checked directly against known inputs: AND correctly takes the tighter (minimum) bounds pair, OR correctly takes the looser (maximum) bounds pair, confirmed against hand-computed examples before being trusted in the pilot.

## What stays honestly open

Per Jay's standing call (2026-08-11, logged in [[neuro-symbolic-fallacy-screen-v1]]): no live model call runs against any of this code, for any category. Every result shown anywhere in this project from `fallacy_bounds_screen()` or `demo_bounds_output()` comes from demo-mode reasoning against known ground truth, not from a live API call — and this file names that as a closed decision, not an open next step, matching the same framing already locked in [[neuro-symbolic-fallacy-screen-v1]].

Two further honest gaps, unresolved by this pass: first, whether the AND/OR/single classification above holds up against real argument text, rather than just describing each fallacy's dictionary definition, stays untested — a real argument might trip a category's subconditions in ways this classification didn't anticipate. Second, double-counting — the 26th category [[fallacy-screen-worked-examples-v1]] found empirically on blackhole-002 — sits outside `FALLACY_SHAPE_DATA` entirely. It came from evidence-reasoning tradition (non-independent evidence), not the classical fallacy tradition the other 25 draw from, and doesn't share their subject-predicate shape closely enough to force into an AND/OR/single template without real, separate design work. Left unbuilt here, named plainly rather than forced in to round the count to 25.

## Addendum, 2026-08-17: double-counting added, 26/26 now covered

The gap named directly above closed the same day it got re-examined. Re-checked against blackhole-002 — its own real, empirical instance of this category — double-counting decomposes the same AND way as 22 of the other 25 categories: a shared premise feeding two or more conclusions, plus the argument treating those conclusions as independently corroborating. The earlier framing ("doesn't share their subject-predicate shape") assumed double-counting needed a two-claim, cross-source comparison to check; blackhole-002's own case argues against that — the shared premise and the independence treatment both show up inside one argument's own text, the same single-quote contract every other `FALLACY_SHAPE_DATA` entry already uses. Added as `double_counting` in `ingest.py`, `group_tag: causal_and_statistical` (matching [[fallacy-screen-layer-v1]]'s own grouping of this category under "Bad use of data"). `FALLACY_SHAPE_DATA` now holds 25 entries; combined with `circular_argument_screen()`'s dedicated function, all 26 named categories now have a built neuro-symbolic bounds-pair check. Verified real, not assumed: `ast.parse()` against the actual edited file, `build_bounds_prompt('double_counting', ...)` confirmed fully resolved (no leftover placeholders), and `demo_bounds_output('double_counting')` confirmed the AND-combine rule against a hand-computed expectation — all checked directly against the live file on the Mac vault, copied over for verification, not inferred from the edit diff alone.

What this addendum does NOT close: the standing rule from this file's original text stays exactly as locked — no live model call runs against any of this code, for any category, per Jay's 2026-08-11 ruling. Every result from `fallacy_bounds_screen()` including this new category comes from demo-mode reasoning against known ground truth or `ast.parse`/logic verification, not a live API call. Coverage now reads 26/26 built; it does not read 26/26 tested against real argument text beyond the three original pilot claims — that gap, named two paragraphs above this addendum, stays open exactly as stated.
