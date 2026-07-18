---
claim_id: covid-004
case: covid-origins
subtopic: judge-verdict-location-model
source_ref: "[[stansifer-2024-covid-decision]]"
confidence_score: 4
rewrite_confidence: high
methodology: independent_judge_bayesian_location_distance_model
relation_type: supports
tags: [resilience]
---
# Judge Stansifer's independent verdict — location-distance model favors zoonotic spillover

## Ingestion Layer
*Mechanical pass. No interpretation below this point — only the source quote and its forced E-Prime rewrite.*

### Original Quote
"I find with high confidence that zoonotic spillover is the more likely origin of sars-cov-2. The most important basis for this decision is the relative epidemiological proximity of the earliest indicators of covid to a plausible animal source rather than a potential laboratory source. While Rootclaim identified unusual characteristics of the genetics of sars-cov-2 and the potential for laboratory work to create a similar virus, I found this insufficient to overcome the proximity evidence and the prior against a laboratory origin."

### E-Prime Rewrite
Stansifer's independent location-distance model, built separately from either debater's framework, computes a Bayes factor of 100 to 1000 favoring zoonotic spillover over lab-leak, comparing the epidemiological distance from the earliest known covid cases to a plausible animal source at HSM versus a laboratory source at WIV; this factor outweighs Rootclaim's genetic-evidence arguments in his verdict.

## Assessment Layer
*Checkable pass, run against the ingestion output above. See [[two-layer-architecture-v1]] for the assessment criteria each subsection below must satisfy.*

### Analysis
"Is the more likely origin" and "I find with high confidence" read as a verdict statement — a conclusion reached, not a calculation shown. Forcing the rewrite requires naming the actual mechanism: not a review of the debaters' own numbers, but an independently constructed model comparing how large a population radius each hypothesis requires to explain the observed index case, yielding a specific factor (100 to 1000, narrowing to 10000 under one restricted framing) rather than a bare assertion of confidence.

This matters directly for [[covid-001]]: Peter's argument (this vault's covid-001) reaches a zoonotic-favoring conclusion through case-count back-extrapolation (a 256x growth-rate mismatch). Stansifer's model reaches the same directional conclusion through an entirely independent method — population-distance modeling, not epidemic-curve doubling. Two different mechanisms, same direction, from an independent judge who explicitly built his own model rather than adopting either debater's framing.

### Ambiguity Flags
- Stansifer states his own numbers stay sensitive to a modeling choice he names directly: whether "Z" (zoonotic spillover) gets scoped narrowly (HSM specifically) or broadly (any market or restaurant, anywhere) changes his Bayes factor by orders of magnitude (100 to 1000 broad, 10000 narrow). He names this instability himself rather than picking the number that best supports his conclusion and moving on.
- This claim covers only his location-distance argument (Section 4) and his top-line verdict (abstract). His separate genetic-evidence discussion (Section 5) and his critique of Rootclaim's own Bayesian calculation (Section 3) remain uningested — his full verdict rests on more than this one argument alone.

### Adversarial Interpretation
A reader motivated to dismiss this finding could note that Stansifer explicitly names his own model's sensitivity to scope choice as a real weakness, not a footnote — his own Bayes factor swings by two orders of magnitude depending on how "Z" gets defined, which a motivated reader could read as the model being too malleable to trust. A reader motivated to accept the zoonotic conclusion could note that this instability runs in the same direction across every scope choice Stansifer tried (100, 1000, and 10000 all favor zoonotic) — the magnitude varies, but the direction doesn't flip, a different and stronger property than an estimate straddling both directions.

## Related Claims
- [[covid-001]] — both claims argue for the same directional conclusion (zoonotic timing, against early/lab-leak circulation) through independent methods: covid-001 via case-count back-extrapolation, this claim via population-distance modeling from an independent judge who built his own framework rather than adopting either debater's
- [[covid-003]] — this claim doesn't address the furin-cleavage-site genetics argument at all; Stansifer's genetic-evidence discussion (Section 5) remains uningested, so no direct relation established here
- [[covid-005]] — the debate's other independent judge (Van Treuren) reaches the same directional conclusion (HSM/market epicenter favors zoonotic origin) through a formally distinct model: market-visit traffic-share estimation rather than population-distance radius calculation. Corroboration through independent method, not restatement — see the near-duplicate check in `SYNTHESIS/near-duplicate-check-v1.md`.
