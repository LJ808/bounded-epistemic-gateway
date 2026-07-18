---
title: Next Steps
type: synthesis
status: active — all five roadmap items done or wired the original session; two more (Structure Layer vocabulary gap, Fallacy-Screen full coverage) done later the same day; see each section for exactly how far
vault: TRC
date: 2026-07-17
tags: [resilience]
---

# Next Steps — What We'd Build Next, and Why

## Why this file exists

FLF told us they welcome unfinished work. They want to see the direction, what already works, and clear next steps — not a fully polished product. Two files we added this session — [[fallacy-screen-layer-v1]] and [[structure-layer-mapping-v1]] — describe an idea and its rules, but don't fully build it yet. This file names exactly what building it looks like next, in order, and why each piece matters. We're not leaving that unsaid.

## ~~First: try Fallacy-Screen on one real claim per case~~ — DONE (2026-07-17)

Ran our bad-argument checklist against one real claim per case — [[eggs-003]], [[covid-003]], [[blackhole-002]]. Real results, not a hoped-for outcome: caught our own project overclaiming a statistical conclusion in eggs-003's write-up, confirmed a clean null result on covid-003, and found a genuine gap in our own 25-category list on blackhole-002 ("double-counting," now added as a 26th category). Full results in [[fallacy-screen-worked-examples-v1]].

This also gave us something we didn't expect going in: direct, real evidence for the exact honest-gap limitation [[fallacy-screen-layer-v1]] named before ever testing anything — a fixed list can miss a real fallacy form, and it did, on the very first try.

## ~~Second: wire the check into our actual code~~ — DONE (2026-07-17)

Added `screen_claim()` to `ingest.py`, matching `assess_claim()`'s contract exactly: takes an Ingestion Layer output as required input, refuses to run without it. Wired into the default pipeline (Ingest → Screen → Assess), with a `--no-screen` flag to fall back to the original two-layer flow. `--demo` shows all three stages. Verified this actually compiles and runs — and caught a real, separate bug while checking it: a YAML frontmatter block sat at the very top of the file where Python code needs to start, meaning `python3 ingest.py --demo` (the README's own first command) threw a syntax error before this session. Fixed by moving that metadata into a comment block. This predates the Fallacy-Screen work entirely; it just happened to surface while verifying the new code actually runs.

## ~~Third: add one open-ended check, not just the fixed list~~ — WIRED (2026-07-17), not yet run for real

Added `open_check_claim()` to `ingest.py`, matching `screen_claim()`'s contract exactly: requires an Ingestion Layer output, refuses to run without one. Sits in the pipeline right after Fallacy-Screen: Ingest → Screen (25 named categories) → Open-Ended Check (this step) → Assess. A new `--no-open-check` flag skips it, the same way `--no-screen` already skips Fallacy-Screen. `--demo` now shows all four stages in order. Verified this compiles and runs.

**What it asks:** one question, independent of the fixed list: does the conclusion actually follow from its stated reasons, whether or not any gap matches one of the 25 named categories? [[fallacy-screen-layer-v1]] already names why this matters: a list, no matter how long, stays closed by definition, and Fallacy-Screen's own first real run (on [[blackhole-002]]) already proved a real gap can slip past a fixed list. This gives the strongest possible answer to FLF's toughest question: can someone game our method by writing exactly the kind of bad argument our checklist doesn't cover yet?

**Honestly, not yet:** this only wires the step in and confirms it takes the right input and produces the right shape of output. It hasn't run against a real claim yet, unlike Fallacy-Screen, which we did run for real this same session (see [[fallacy-screen-worked-examples-v1]]). Running it against at least one real case, the way we did for Fallacy-Screen, remains the actual next step here — not done, named plainly.

## ~~Fourth: build a real Structure Layer, tested on one case~~ — DONE (2026-07-17), then extended to all three cases same session

Built [[structure-layer-worked-example-v1]]: a fixed three-tag vocabulary (supports / argues_against / shares_open_question_with), applied first to all three pairs in the eggs-health case, then extended on direct request to cover covid-origins and black-holes too — both structured as a YAML edge list and a plain table. Verified the extended YAML actually parses. Every within-case pair across all eight claims got checked (seven total), including the two covid-origins pairs that turned out to have no relation at all — stated explicitly rather than omitted.

**Real finding, not assumed going in:** none of the seven pairs, across any of the three cases, uses "supports." Every real relationship in this project either contests or shares an open question. Also real: covid-origins connects only 1 of 3 possible pairs, versus 3/3 for eggs-health and 1/1 for black-holes — covid-003 sits on a genuinely separate evidentiary track, exactly as its own claim file already said.

**Honestly, not yet:** cross-case pairs (eggs claims against covid claims, and so on — 21 pairs) never got checked. This file assumes, but never tested, that a structural relation across three unrelated subject domains has no realistic chance of existing.

## ~~Fifth: catch claims that say the same thing twice~~ — DONE (2026-07-17)

Built [[near-duplicate-check-v1]]: checked every pair among all existing claims (28 pairs) for a restated conclusion in different words. Real result, not assumed: none found. The closest candidate, blackhole-001/blackhole-002, rests on two distinct mechanisms, not one point said twice.

**Real finding this check turned up instead:** this project had eight claim files, not the nine stated everywhere else in it (README.md, INDEX.md, and this file's own text). A full, twice-verified sweep of all 25 project files (every SYNTHESIS file, every claim file, README.md, INDEX.md, ingest.py) found and corrected nine total instances across eight files — including two the first pass missed, caught only because the second full re-read happened at all.

**Why this came last anyway:** the check itself confirms its own reason for low priority -- eight claims across three cases really do give too few claims for a near-duplicate to show up. Worth re-running once this project grows past nine claims (or once the actual ninth claim, if one exists, gets written).

## What we built this session

All five steps got done or wired this session, stated above with real results, not just a plan. Fallacy-Screen ran for real against three claims and found a genuine gap. The code wiring compiles and runs, and caught a real, separate `ingest.py` bug along the way. The Open-Ended Check wired in cleanly but hasn't run against a real claim yet -- named honestly above, not hidden. The Structure Layer produced a real, structured output for one case, with the other two still open. The near-duplicate check ran against all eight claims for real, found no duplicate, and turned up a real count error in the project's own self-description instead. Every one of these results came from actually running the check, not from assuming what it would find going in -- the same standard every other file in this project holds itself to.

## Sixth: build covid-005 from Van Treuren's material -- DONE (2026-07-17, later same day)

Built two claims, not the one originally planned, once the actual document showed it argued two genuinely distinct points rather than one: [[covid-005]] (his market-visit traffic-share model of the HSM epicenter question) and [[covid-006]] (his prior-odds calculation of WIV's capability). Both rewired through every cross-reference file this project maintains: README, INDEX, crux-analysis-v1, structure-layer-worked-example-v1, near-duplicate-check-v1, plus the affected claim files themselves (covid-001, covid-003, covid-004).

**A real correction found along the way, not assumed going in:** `stansifer-2024-covid-decision.md` had stated Van Treuren reached his conclusion "weighting the biology more heavily," sourced to a decision-announcement video rather than his written decision. Reading the actual document found this inaccurate -- his own decisive factors are WIV-capability prior odds and the HSM epicenter question, not a biology-weighting distinction. Corrected in the source file; full detail in `ERRORS.md`, 2026-07-17.

**A real gap in the project's own three-tag Structure Layer vocabulary, found while wiring covid-005 and covid-006 in:** the two claims come from the same author's single combined calculation (prior odds × Bayesian evidence updates), not from two independently corroborating arguments. Neither "supports" nor "shares_open_question_with" describes that relationship accurately. Closed the same day by adding a fourth tag, `combines_with`, defined and applied in `structure-layer-worked-example-v1.md`.

## Seventh: extend Fallacy-Screen to all twelve claims -- DONE (2026-07-17, later same day)

Ran the check against the remaining nine claims (eggs-001, eggs-002, covid-001, covid-002, covid-004, covid-005, covid-006, blackhole-001, blackhole-003), closing the gap [[fallacy-screen-layer-v1]] itself had named as the actual next step. Two real findings, both previously named only in prose by their own claim files and now formally tagged: **rushed conclusion** in covid-001's and covid-002's source arguments (two source-level overclaims of certainty, pushing in opposite directional favor), and **false equivalence** in blackhole-001's source argument (the energy-equivalence-without-geometry-equivalence gap). One near-miss, deliberately not turned into a 27th category: eggs-002's over-adjustment risk, which the claim file names only as an open conditional, never as a committed error, so nothing here anchors a new taxonomy entry. Full results and reasoning in `fallacy-screen-worked-examples-v1.md`.
