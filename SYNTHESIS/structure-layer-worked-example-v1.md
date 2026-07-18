---
title: Structure Layer — Worked Example (All Three Cases)
type: synthesis
status: active — real structured output, all three cases covered, every within-case pair checked, updated after covid-004's, blackhole-003's, covid-005's, and covid-006's additions
vault: TRC
date: 2026-07-17
tags: [resilience]
---

# Structure Layer — A Real Structured Output, All Three Cases

## Why this file exists

[[structure-layer-mapping-v1]] names real "structure" work this project already does, but states plainly that none of it exists as a separate, clean output — only as prose links inside each claim's "Related Claims" section. This file builds that missing output for real, across all three cases, instead of leaving it as a stated gap.

**Revision note:** this file originally covered the eggs-health case only, extended to covid-origins and black-holes the same session on direct request. Four later additions, [[covid-004]] and [[blackhole-003]] (this session), then [[covid-005]] and [[covid-006]] (Van Treuren's independent verdict, a later same-day session), each closed part of a gap named in [[crux-analysis-v1]] and required re-checking every pair in their respective cases. Wiring covid-005 and covid-006 in also surfaced a real gap in this file's own vocabulary, closed the same day — see **combines_with** below.

## The fixed format

Four tags, the first three of which [[structure-layer-mapping-v1]] names as an example, locked as the actual working vocabulary:

- **supports** — claim A's evidence strengthens claim B's conclusion
- **argues_against** — claim A's evidence directly contests claim B's conclusion
- **shares_open_question_with** — neither claim resolves a question the other one also leaves open
- **combines_with** — claim A and claim B function as separate components of one single author's combined calculation or verdict, rather than as independently corroborating arguments; the conclusion depends on both together, not on either strengthening a separately-arrived-at conclusion. Symmetric by nature, unlike the other three tags, since neither component is prior to or derived from the other — stated from-A-to-B here only to match this file's table format.

Added 2026-07-17, later same day, once [[covid-005]] and [[covid-006]] showed a real relationship the original three tags couldn't describe accurately — see the note below the edge list.

Every edge below states a direction (A relates to B, not the reverse, except combines_with, which is symmetric) and a one-sentence reason, drawn only from what the two claim files already say. A pair with no real relationship gets stated as such, not silently omitted.

## Structured output — all three cases, every within-case pair checked

```yaml
claims: [eggs-001, eggs-002, eggs-003, covid-001, covid-002, covid-003, covid-004, covid-005, covid-006, blackhole-001, blackhole-002, blackhole-003]
relation_vocabulary: [supports, argues_against, shares_open_question_with, combines_with]

edges:
  # --- eggs-health (3 of 3 pairs have a relation) ---
  - from: eggs-002
    relation: argues_against
    to: eggs-001
    reason: >
      Covariate-adjusted cohort analysis (215,618 subjects, up to 32 years
      follow-up) finds no CVD association after adjustment for lifestyle and
      dietary factors, directly contesting eggs-001's pooled positive
      association (RR 1.19, CI 1.02-1.38).
  - from: eggs-001
    relation: shares_open_question_with
    to: eggs-003
    reason: >
      Whether eggs-003's diabetic-subgroup HR (1.33, CI 0.72-2.46) corroborates
      or undermines eggs-001's diabetes-specific RR (1.68, CI 1.41-2.00) stays
      unresolved -- neither study's numbers settle the question either way.
  - from: eggs-002
    relation: shares_open_question_with
    to: eggs-003
    reason: >
      Both report a null or non-significant result. Neither study's design
      distinguishes "no true effect exists" from "this sample lacks power to
      detect the effect" -- the same underpowered-vs-absent ambiguity sits
      underneath both.

  # --- covid-origins (2 of 6 pairs have a relation) ---
  - from: covid-002
    relation: shares_open_question_with
    to: covid-001
    reason: >
      Both bear on the same disputed pre-market timing question from
      different argument types -- covid-001's aggregate growth-rate math
      versus covid-002's single-case anecdote (Mr. Chen) -- and neither
      claim's own rewrite resolves what the other one leaves open.
  - from: covid-004
    relation: supports
    to: covid-001
    reason: >
      An independent judge's own population-distance model (Bayes factor
      100-1000 favoring zoonotic spillover) reaches the same directional
      conclusion as covid-001's case-count back-extrapolation, through a
      completely different mechanism and from a completely different source
      type (a judge's verdict, not a debater's argument) -- corroboration,
      not restatement.
  - from: covid-005
    relation: supports
    to: covid-001
    reason: >
      The debate's second independent judge (Van Treuren), via a
      market-visit traffic-share model (factor of 1000 favoring zoonotic
      spillover), reaches the same directional conclusion as covid-001's
      case-count back-extrapolation, through a third independent mechanism.
  - from: covid-005
    relation: supports
    to: covid-004
    reason: >
      Both of the debate's two independent judges reach the same conclusion
      -- HSM/market epicenter favors zoonotic origin -- through formally
      distinct models: Stansifer's population-distance radius calculation
      (covid-004) versus Van Treuren's market-visit traffic-share
      calculation (covid-005). Corroboration through independent method,
      not restatement.
  - from: covid-005
    relation: combines_with
    to: covid-006
    reason: >
      Both come from Van Treuren's decision. He does not treat these as
      independently corroborating arguments -- his own document multiplies
      this claim's HSM-traffic-share Bayes factor into the same final
      verdict that covid-006's prior-odds calculation feeds as its starting
      point. Two components of one combined calculation, not two separate
      claims that happen to agree.

  # --- black-holes (2 of 3 pairs have a relation, after blackhole-003's addition) ---
  - from: blackhole-001
    relation: shares_open_question_with
    to: blackhole-002
    reason: >
      Together the two claims cover CERN's full safety case (formation-energy
      equivalence and evaporation), but which argument actually carries the
      real safety weight stays unresolved in the public FAQ alone.
  - from: blackhole-003
    relation: supports
    to: blackhole-002
    reason: >
      CERN's full LSAG report confirms directly, in its own words ("in
      addition to"), that the same-theory argument and the astrophysical
      check function as two additive, independent lines of defense -- not
      one argument restated, exactly the question blackhole-002 raised
      without access to this document. Does not resolve blackhole-002's
      deeper question of which argument carries more weight.
```

## Same output, readable table

| From | Relation | To | One-line reason |
|---|---|---|---|
| eggs-002 | argues_against | eggs-001 | Adjusted cohort finds no CVD link; contests eggs-001's pooled positive association |
| eggs-001 | shares_open_question_with | eggs-003 | Diabetic-subgroup HR neither confirms nor refutes the diabetes-specific RR |
| eggs-002 | shares_open_question_with | eggs-003 | Both null results share one unresolved question: underpowered, or a true absence of effect? |
| covid-002 | shares_open_question_with | covid-001 | Same disputed timing question, two different argument types, neither resolves the other |
| covid-004 | supports | covid-001 | Independent judge's model reaches the same conclusion by a different route |
| covid-005 | supports | covid-001 | Second independent judge's model reaches the same conclusion by a third route |
| covid-005 | supports | covid-004 | Both independent judges reach the same epicenter conclusion via distinct models |
| covid-005 | combines_with | covid-006 | Two components of Van Treuren's own single combined calculation, not independent corroboration |
| blackhole-001 | shares_open_question_with | blackhole-002 | Which argument actually carries the real safety weight stays open |
| blackhole-003 | supports | blackhole-002 | Full report confirms two independent arguments, not one restated |

## Pairs checked, no edge found

Not every pair has a relation, and forcing one into the three-tag vocabulary would misrepresent what the claim files actually say. Five pairs get stated here as explicitly checked and unconnected, rather than omitted silently:

- **covid-001 / covid-003** — covid-003's own Related Claims section states this directly: "This claim sits independent of [[covid-001]] and [[covid-002]] ... it belongs to the separate viral-genetics evidentiary track in the same debate." No forced edge.
- **covid-002 / covid-003** — same independence, same source statement. No forced edge.
- **covid-002 / covid-004** — Stansifer's document (covid-004's source) does mention a "Mr Chen" case in passing, in a figure caption outside the section actually ingested here. covid-004's claim file states its own scope plainly: only Section 4 (the location-distance model) and the abstract got ingested, not the passing Mr. Chen mention elsewhere in the document. No edge drawn from a passage never actually rewritten or assessed.
- **covid-003 / covid-004** — covid-004's own claim file states this directly: its ingested scope never touches the furin-cleavage-site genetics argument; Stansifer's separate genetic-evidence discussion (his Section 5) remains uningested. No edge.
- **blackhole-001 / blackhole-003** — blackhole-003 discusses the same collision-geometry question blackhole-001 raised, and LSAG's report acknowledges the gap exists ("there is one significant difference between cosmic-ray collisions with a body at rest and collisions at the LHC... [particles] tend to have low velocities, whereas cosmic-ray collisions would produce them with high velocities"), but defers the actual resolution to a separate, uningested paper. Naming the same open question without resolving it doesn't meet the bar for "shares_open_question_with" here, since blackhole-003's own scope (Section 4 and the Conclusions) never engages the geometry argument directly enough to check it against blackhole-001's specific claim — it only acknowledges the gap exists in passing. No edge, stated conservatively rather than stretched to fit.
- **covid-006 / covid-003** — both bear on WIV's capacity to have engineered SARS-CoV-2, but covid-006's own claim file states its scope precisely: whether WIV held a suitable genetic backbone at all, a precondition question distinct from covid-003's question of whether the FCS's specific sequence looked achievable to a 2019 engineer. Same reasoning as the covid-004/covid-003 no-edge case above — same general genetics track, distinct specific sub-arguments. No edge.
- **covid-006 / covid-001, covid-006 / covid-002** — different evidentiary tracks entirely (prior-odds/capability calculation versus epidemiological timing). No edge, same reasoning as covid-004's own no-edge pairing with these two claims.
- **covid-006 / covid-004** — different mechanism entirely (prior-odds/capability calculation versus location-distance modeling), and not the same author's combined calculation the way covid-005 and covid-006 are. No edge.

This matters as a finding in its own right: a case can have real internal structure alongside a genuinely separate track that stays disconnected — confirmed now across twelve claims, not just eight.

## A fourth relation type, added to close a real gap: combines_with

[[covid-005]] and [[covid-006]] both come from Van Treuren's decision, and the original three-tag vocabulary (supports / argues_against / shares_open_question_with) had no accurate way to describe their relationship. Van Treuren doesn't present these as two independently corroborating arguments — his own document combines them multiplicatively into one final verdict (prior odds × the product of his Bayesian evidence updates, which includes the HSM-epicenter factor covid-005 covers). "Supports" implies one claim's evidence strengthens a separately-arrived-at conclusion; "shares_open_question_with" implies neither claim resolves a shared open question. Neither described two terms in the same author's single combined calculation. Rather than force a stretch or leave the relationship unstated, this file adds a fourth tag, **combines_with**, and applies it as the covid-005/covid-006 edge above. First use of this tag anywhere in the project — worth revisiting if a future addition shows the definition needs sharpening, but sufficient for the one real case that prompted it.

## What this adds beyond the existing "Related Claims" sections

The twelve claim files already name these same relationships, in prose, one file at a time. A reader has to open every file and piece the map together by hand. This file puts all of it in one place, tagged from a closed, four-item vocabulary, readable in one pass without opening any claim file first — including the pairs that turn out to have no relation at all, which the prose-only version never states explicitly anywhere in one place.

## Two honest findings worth naming

**"Supports" appears exactly four times and "combines_with" exactly once, across all twelve claims — every instance from a claim added after the original eight.** Every relationship among the original eight claims either contests or shares an open question; not one straightforwardly backs up another, and none needed a fourth tag. All five real corroboration/combination edges came from adding a genuinely new kind of source — two independent judges' verdicts and a full technical report — rather than from re-reading the original eight differently. Worth stating plainly: the tags sat unused not because they couldn't apply, but because this project's original eight sources — debates, contested studies, an institution defending a safety case — happen to select for contested or open relationships over corroborating or combined ones. New sources of a different kind (verdicts and full reports, not combatants' arguments or short summaries) produced every real supports/combines_with edge found so far.

**Every case now connects more densely than it first appeared, but unevenly.** eggs-health: 3/3 pairs connected. black-holes: 2/3, up from 1/1 of a smaller set (blackhole-003's new pair connects, but the geometry question between blackhole-001 and blackhole-003 stays unresolved even in the full report). covid-origins: 5/15 (up from 2/6 before covid-005 and covid-006 joined) — still the sparsest of the three by proportion, though the least-connected claim by count. covid-003 remains fully disconnected from every other covid claim, and covid-006 connects only to covid-005 (via combines_with, not an independent relation), exactly as their own claim files say. Density varies by how much of a case sits on one continuous argument thread versus genuinely separate tracks, not by how thoroughly each case got checked.

## Where this stands, honestly

This file builds the real, structured, checkable output [[structure-layer-mapping-v1]] said this project lacked — now covering all three cases, all twelve claims, all twenty-one within-case pairs checked (eggs 3, covid 15, blackhole 3) — not just the ten that turned out to have an edge. Cross-case pairs (eggs claims against covid claims, covid against black-hole, and so on) never got checked here at all; this file follows [[near-duplicate-check-v1]]'s own reasoning that a structural relation across three unrelated subject domains and three unrelated source pools has no realistic chance of existing, but that reasoning stayed unverified rather than tested pair-by-pair the way [[near-duplicate-check-v1]] tested it. Worth naming plainly rather than assuming it away. It does not yet catch near-duplicate claims within a single case the way [[near-duplicate-check-v1]] catches them across the whole project — that's a related but separate check. The vocabulary itself grew from three tags to four this same day, once a real pair (covid-005/covid-006) showed the original three didn't cover every relationship type this project's own sources actually produce — stated here as a real extension, not assumed complete going forward either.
