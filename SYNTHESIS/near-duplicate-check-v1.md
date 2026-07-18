---
title: Near-Duplicate Check — Worked Example (All Existing Claims)
type: synthesis
status: active — real check run against every existing claim pair; one real count error found and corrected along the way; re-run after covid-004's, blackhole-003's, covid-005's, and covid-006's additions
vault: TRC
date: 2026-07-17
tags: [resilience]
---

# Near-Duplicate Check — Do Any Two Claims Say the Same Thing Twice?

## Why this file exists

[[next-steps-v1]] names this as the fifth and lowest-priority item: go through the existing claims and flag any two that make basically the same point in different words or with different caveats. It also predicts, honestly, that too few claims exist yet for this to matter much. This file runs the check for real instead of leaving that prediction untested.

## A real count correction, found while running this check

Pulling one core-conclusion line per claim required listing every claim file directly. That listing turns up **8 claim files**, not the 9 this project states elsewhere (README.md, INDEX.md): 3 in eggs-cvd-diabetes, 3 in covid-origins, 2 in black-holes. We didn't go looking for this — it surfaced as a side effect of doing the actual count this check requires, the same way the fallacy-screen work surfaced the `ingest.py` syntax bug and the double-counting gap. Corrected everywhere the wrong count actually appeared: README.md, INDEX.md, six other SYNTHESIS files' frontmatter and body text (adversarial-robustness-criterion-6, crux-analysis-v1, literature-engagement-addendum-v1, literature-engagement-addendum-v2, per-claim-attack-vector-breakdown, two-layer-architecture-v1), structure-layer-mapping-v1, and one claim file itself (eggs-003.md). Verified clean with a full re-read of all 25 project files after the fixes, not assumed clean from the fix list alone — that re-read caught two more instances the first pass missed (README's own "nine claims" line in its main-claim section, and a table row in per-claim-attack-vector-breakdown.md), which is exactly why the re-read mattered.

## One core conclusion per claim, in plain words

| Claim | Core conclusion, one line |
|---|---|
| eggs-001 | Pooled unadjusted analysis: egg intake correlates positively with CVD and diabetes risk. |
| eggs-002 | Multivariable-adjusted cohort: no CVD association survives adjustment for lifestyle/diet factors. |
| eggs-003 | Diabetic and non-diabetic subgroup HRs overlap enough that the interaction test stays null. |
| covid-001 | Constant-doubling back-extrapolation implies an early start would show far more cases than observed. |
| covid-002 | A single anonymous-source claim, if accurate, places one case's infection outside the wet-market cluster. |
| covid-003 | The furin cleavage site looks unlike anything a 2019 engineer would have deliberately chosen. |
| blackhole-001 | Constant natural cosmic-ray collisions at LHC-equivalent energies constrain how dangerous LHC collisions can be. |
| blackhole-002 | The same theory predicting LHC black hole formation also predicts their near-instant evaporation. |

## The check itself

**Within-case pairs (7 total — the only pairs where duplication has any real chance of showing up, since every case covers an entirely different subject and source pool):**

- **eggs-001 vs eggs-002** — opposite conclusions (positive raw association vs. null after adjustment). Not a duplicate; a genuine disagreement.
- **eggs-001 vs eggs-003** — different subtopics (overall pooled association vs. one subgroup's interaction test). Not a duplicate.
- **eggs-002 vs eggs-003** — both land on a null-ish result, but for different reasons (adjustment removing signal vs. subgroup power). [[structure-layer-worked-example-v1]] already tags this pair `shares_open_question_with`, not `supports` — a shared *ambiguity*, not a restated conclusion. Not a duplicate.
- **covid-001 vs covid-002** — different argument types entirely (aggregate growth-curve math vs. one anecdotal case), even though both sit inside the same broader timing dispute. Not a duplicate.
- **covid-001 vs covid-003** — different evidentiary tracks (epidemiological timing vs. viral genetics), already noted as independent in covid-003's own Related Claims. Not a duplicate.
- **covid-002 vs covid-003** — same as above; different tracks. Not a duplicate.
- **blackhole-001 vs blackhole-002** — the closest real candidate. Both back the same overall safety conclusion, but each rests on a distinct mechanism (cosmic-ray energy equivalence vs. Hawking-radiation evaporation), with its own source excerpt and its own separate failure mode (a geometry-equivalence gap for -001; a same-theory chain-dependency gap for -002, per [[insight-contribution-v1]]). Restating one as the other would lose the actual argument. Not a duplicate.

**Cross-case pairs (21 total):** every claim's core conclusion above sits in a completely different subject domain and draws from a completely different source. No pair shares even a surface-level topic, let alone a restated conclusion. Checked explicitly rather than assumed; none found.

## Structured result

```yaml
claims_checked: 8
pairs_checked: 28
near_duplicates_found: "no"
closest_candidate:
  pair: [blackhole-001, blackhole-002]
  why_not_a_duplicate: >
    Same case, same overall safety conclusion, but each rests on a distinct
    mechanism (cosmic-ray energy-equivalence vs Hawking-radiation evaporation)
    with its own source excerpt and its own failure mode -- not the same point
    in different words.
count_correction_found:
  stated_elsewhere_in_project: 9
  actual_claim_file_count: 8
  verified_by: direct directory listing of CLAIMS/
```

## Where this stands, honestly

Every pair checked, real result: no near-duplicate exists among the current 8 claims. [[next-steps-v1]]'s own prediction — that too few claims exist yet for this to show up often — holds up under an actual check, not just an assumption. The one real find this check produced wasn't a duplicate claim; it turned out to be a wrong count of how many claims exist at all, corrected here. This check needs re-running any time a new claim gets added — a ninth claim (or the currently-missing true ninth, if one exists and simply never got written) could easily land close enough to an existing one to trip this check for real.

## Update, same session: covid-004 added, re-checked

[[covid-004]] entered the vault after this file's original run — a real primary source (an independent judge's own written verdict in the COVID debate), not a duplicate of any existing claim in either topic or method. Checked against all 8 existing claims (8 new pairs, bringing the project total to 36 possible pairs across 9 claims):

- Against eggs-001/002/003 and blackhole-001/002: no relation, different subject domain entirely, same reasoning as every other cross-case pair in the original run.
- Against covid-002 (Mr. Chen anecdote) and covid-003 (furin cleavage site genetics): different topic within the same case, not a duplicate.
- Against covid-001: closest candidate, and explicitly **not** a duplicate despite sharing a directional conclusion (zoonotic timing). covid-001 argues from case-count back-extrapolation; covid-004 argues from an independent judge's population-distance model. Same direction, different mechanism, different source type (a debater's argument versus a judge's verdict) — corroboration, not restatement. This is exactly the distinction [[structure-layer-worked-example-v1]]'s "supports" tag exists to capture, and it's the first real instance of that tag anywhere in this project.

**Updated result:** 9 claims, 36 possible pairs, near-duplicates found: still none.

## Update, same session: blackhole-003 added, re-checked

[[blackhole-003]] entered the vault after covid-004's addition — a real primary source (CERN's own full LSAG 2008 technical report), not a duplicate of any existing claim. Checked against all 9 existing claims (9 new pairs, bringing the project total to 45 possible pairs across 10 claims):

- Against eggs-001/002/003 and covid-001/002/003/004: no relation, different subject domain entirely.
- Against blackhole-001: not a duplicate. blackhole-003's ingested content (the white-dwarf/neutron-star argument, plus LSAG's own "one argument or two" framing) covers different specific material than blackhole-001's cosmic-ray energy-equivalence argument, even though both bear on overall LHC safety.
- Against blackhole-002: closest candidate, and explicitly **not** a duplicate despite the direct "supports" relation already recorded in [[structure-layer-worked-example-v1]]. blackhole-002 quotes and analyzes CERN's short FAQ; blackhole-003 quotes and analyzes LSAG's full technical report and adds a real finding blackhole-002 itself never had access to (that the two arguments run additive and independent, not ranked). Corroboration plus new information, not restatement.

**Updated result:** 10 claims, 45 possible pairs, near-duplicates found: still none.

## Update, later same day: covid-005 and covid-006 added, re-checked

[[covid-005]] and [[covid-006]] entered the vault after blackhole-003's addition — both real primary-source claims from the debate's second independent judge (Will van Treuren), previously blocked by a hosting format this vault's tools couldn't render. Checked against all 10 existing claims and against each other (21 new pairs, bringing the project total to 66 possible pairs across 12 claims):

- Against eggs-001/002/003 and blackhole-001/002/003: no relation, different subject domain entirely, same reasoning as every other cross-case pair checked so far.
- Against covid-002 (Mr. Chen anecdote): different topic within the same case, not a duplicate.
- **covid-005 against covid-001:** closest candidate for covid-005, and explicitly **not** a duplicate despite sharing a directional conclusion (zoonotic timing/location). covid-001 argues from case-count back-extrapolation; covid-005 argues from Van Treuren's market-visit traffic-share model. Same direction, different mechanism, different source type — a third instance of the corroboration-not-restatement pattern [[structure-layer-worked-example-v1]]'s "supports" tag exists to capture.
- **covid-005 against covid-004:** closest candidate overall, and the pair requiring the most scrutiny — both concern the same specific sub-topic (HSM/market epicenter) from two different judges in the same debate. Not a duplicate: Stansifer's claim rests on a population-distance radius calculation; Van Treuren's rests on a market-visit traffic-share calculation with entirely different inputs (visit-rank data and wildlife-shop counts, not distance-to-source modeling). Two judges reaching the same conclusion through two different formal models counts as corroboration, not restatement — the same standard applied to every other "supports" pair in this project.
- **covid-005 against covid-003:** different evidentiary track (epicenter/location versus furin-cleavage-site genetics). Not a duplicate.
- **covid-006 against covid-001, covid-002:** different evidentiary track (prior-odds/WIV-capability versus epidemiological timing). Not a duplicate.
- **covid-006 against covid-003:** closest candidate for covid-006 — both bear on WIV's capacity to have engineered SARS-CoV-2. Not a duplicate: covid-003 asks whether the FCS's specific sequence looked achievable to a 2019 engineer; covid-006 asks whether WIV held a suitable backbone virus to engineer from at all, a separate precondition question with its own separate evidence (disclosed relative-sequence data, not codon-choice analysis).
- **covid-006 against covid-004:** different mechanism entirely (prior-odds/capability calculation versus location-distance modeling). Not a duplicate.
- **covid-005 against covid-006:** both come from the same source and the same judge, which makes this the single closest pair in the whole project by source proximity. Not a duplicate by this check's actual test (a restated conclusion in different words) — the two claims cover entirely different calculations (market-traffic-share versus prior-odds/capability) with no overlapping numbers or reasoning. Worth naming precisely what this pair *is* instead, since "not a duplicate" undersells the relationship: tagged `combines_with` in [[structure-layer-worked-example-v1]] — a fourth relation type added the same day specifically because this pair showed the original three (supports / argues_against / shares_open_question_with) couldn't describe two components of one author's single combined calculation accurately.

**Updated result:** 12 claims, 66 possible pairs, near-duplicates found: still none.
