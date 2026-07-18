---
claim_id: covid-005
case: covid-origins
subtopic: judge-verdict-market-traffic-model
source_ref: "[[van-treuren-2024-covid-decision]]"
confidence_score: 4
rewrite_confidence: high
methodology: independent_judge_bayesian_market_traffic_model
relation_type: supports
tags: [resilience]
---
# Judge Van Treuren's independent verdict — market-traffic model favors zoonotic spillover

## Ingestion Layer
*Mechanical pass. No interpretation below this point — only the source quote and its forced E-Prime rewrite.*

### Original Quote
"Under the best case for LL I find plausible, I think that HSM absorbs maybe 1/1000th of all Hunan 'visits' per day. I don't think the cited HSM environmental conditions give it much of an advantage vs a bar, a karaoke spot, a crowded subway car, etc. Even under a 2x spreading advantage (as LL assigns in the simulation), I get 1/1000th the traffic * 2 = 1/500. I will discount the model by 5X (arbitrary) because the retrospective ILI swab/blood searches do not find evidence of any community transmission."

### E-Prime Rewrite
Van Treuren's own traffic-share model, built independently and separately from Stansifer's, assigns the Huanan Seafood Market (HSM) roughly 1/1000 of all Wuhan-area location visits per day even under the most lab-leak-favorable framing he finds plausible; applying LL's own claimed 2x spreading advantage and a further 5x downward adjustment for the absence of any positive result in retrospective ILI and blood-bank sampling yields P(HSM as first superspreader event | lab leak) = 0.0004, compared to his separately-derived P(HSM as first superspreader event | zoonotic origin) = 0.4 — a factor of 1000 favoring zoonotic origin, driven under zoonotic framing by HSM's documented wildlife-trade share (7 of 17 surveyed wildlife shops).

## Assessment Layer
*Checkable pass, run against the ingestion output above. See [[two-layer-architecture-v1]] for the assessment criteria each subsection below must satisfy.*

### Analysis
Van Treuren reaches a location-based conclusion favoring zoonotic origin through a mechanism entirely distinct from [[covid-004]]'s (Stansifer's population-distance radius model): a market-visit traffic-share estimate, built from HSM's rank among Wuhan locations by daily foot traffic and its documented wildlife-shop count, rather than a distance calculation between the earliest cases and a plausible animal or lab source. Two independent judges, working from the debate's own slide decks rather than each other's frameworks (per the debate's stated rule that judges decide without conferring), land on the same directional conclusion — HSM's location favors zoonotic origin over lab leak — through formally different calculations. This closes a specific gap [[crux-analysis-v1]] and [[stansifer-2024-covid-decision]] both named: Van Treuren's decision existed publicly but sat behind a Google Drive viewer this vault's tools couldn't render, so his reasoning entered this project only as a secondhand description ("weighting the biology more heavily") that this claim's own source reading found inaccurate — see [[van-treuren-2024-covid-decision]] and the correction logged in `ERRORS.md`, 2026-07-17.

### Ambiguity Flags
- Van Treuren names his own 5x downward adjustment as "arbitrary" in the same sentence he applies it — a self-acknowledged judgment call, not a value derived from the debate's own evidence. Removing it entirely would move P(HSM|LL) from 0.0004 to 0.002, still a 200-fold gap against lab leak, but the specific 1000x headline figure depends on this named-as-arbitrary step.
- The upstream input feeding this calculation, P(Wuhan is outbreak epicenter | LL from WIV), carries a stated range of 0.2–1.0 in Van Treuren's own spreadsheet (he used 0.5), and P(Wuhan is outbreak epicenter | ZO) carries a stated range of 0.001–0.1 (he used 0.01) — this claim ingests only his selected midpoint values, not the sensitivity across his own stated ranges.
- This claim covers only the HSM-traffic-share portion of Van Treuren's Bayesian analysis (Section 3, "bayes_factors" spreadsheet tab). His separate prior-odds/WIV-capability calculation — a distinct argument he treats as additive to this one — appears in [[covid-006]], not here.

### Adversarial Interpretation
A reader motivated to dismiss this finding could note that Van Treuren applies two separate downward adjustments to the lab-leak side (the 2x-then-discounted spreading model, and the named-arbitrary 5x factor) while applying no comparable named adjustment to the zoonotic side's 7/17 wildlife-shop estimate, raising a question of symmetry in how scrutiny gets distributed across the two hypotheses. A reader motivated to accept the zoonotic conclusion could note that Van Treuren states his own uncertainty ranges for the upstream inputs explicitly, in his own spreadsheet, rather than hiding them behind a single point estimate — and that even his most lab-leak-favorable stated boundary (0.2 for the epicenter-given-LL input, 0.1 for the epicenter-given-ZO input) still produces a ratio favoring zoonotic origin, not a reversal.

## Related Claims
- [[covid-001]] — this claim reaches the same directional conclusion (zoonotic timing/location, against lab-leak) as covid-001's case-count back-extrapolation, through a third independent mechanism (market-traffic-share modeling), matching the same supports pattern already established between [[covid-004]] and covid-001.
- [[covid-004]] — both claims argue for the same directional conclusion (HSM/market epicenter favors zoonotic origin) from two independent judges in the same debate, through two formally distinct models: Stansifer's population-distance radius calculation versus this claim's market-visit traffic-share calculation. Corroboration through independent method, not restatement — see the near-duplicate check logged in `SYNTHESIS/near-duplicate-check-v1.md`.
- [[covid-006]] — this vault's other Van Treuren claim, covering his separate prior-odds/WIV-capability calculation. Van Treuren himself treats these as two additive components of one combined verdict (prior odds × evidence updates), not as two independent corroborating claims — tagged `combines_with` in `SYNTHESIS/structure-layer-worked-example-v1.md`, a fourth relation type added specifically for this pair.
