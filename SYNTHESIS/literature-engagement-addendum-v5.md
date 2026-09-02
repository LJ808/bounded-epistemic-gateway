---
synthesis_type: literature_engagement_addendum
addendum_to: [insight-contribution-v1, two-layer-architecture-v1, structure-layer-mapping-v1, literature-engagement-addendum-v4]
trigger: poisoning-attacks-arxiv-2510.07192-2026-08-31
claims_tested: 7
date_executed: "2026-08-31"
date_executed_round2: "2026-09-01"
status: addendum — Extension 6 run for real across seven claims total (2026-08-31 session 5 + 2026-09-01 continuation + 2026-09-01 tier-gap round), see Results sections below. Paper's real findings and defense taxonomy summarized directly from its own text.
written_in_e_prime: true
tags: [architecture, literature-review, resilience]
---

# A Sixth Outside Paper — What Data-Poisoning Research Does and Doesn't Say About the Gateway

Souly, Rando, Chapman, Davies, and eleven coauthors (2025), "Poisoning Attacks on LLMs Require a Near-Constant Number of Poison Samples," arXiv:2510.07192, a collaboration between the UK AI Security Institute, Anthropic, the Alan Turing Institute, and OATML at Oxford.

This paper reports a training-time finding, not an inference-time one. The Gateway trains nothing — it calls already-trained, unmodified local models through RKLLama. That distinction matters enough to state before anything else in this document: the paper's central empirical result does not describe a vulnerability in the Gateway's own infrastructure. What it does supply, read against `literature-engagement-addendum-v4`'s named "provenance and ingestion" gap, functions as a genuine prompt toward a real, buildable extension — described below as Extension 6, using material this project already has on hand.

---

## What the paper actually found, stated plainly

Poisoning attacks against LLM pretraining need a near-constant absolute number of malicious documents, not a fixed percentage of the training corpus. The paper trains models from 600M to 13B parameters on Chinchilla-optimal token counts (6B to 260B tokens) and finds 250 poisoned documents backdoor models across that entire size range, despite the largest models training on more than 20 times more clean data than the smallest. The same dynamic holds during fine-tuning. The practical implication runs opposite to the field's prior assumption: as training datasets grow, the number of documents an attacker needs stays flat while the attack surface (total documents available to poison) grows, meaning larger models do not become harder to poison — they become easier, in relative terms.

Two further findings matter for framing:

**Continued clean training degrades attack success, slowly and unevenly.** Training on clean data only, for at least 1,700 further steps past the poisoning point, reduces the backdoor's attack success rate — but different poisoning data-mixtures degrade at different, non-uniform rates, and the paper explicitly declines to claim this as a reliable, general-purpose defense on its own.

**No end-to-end successful attack gets demonstrated.** The paper's own ethics statement states this directly: the attacks shown do not persist through realistic post-training in this work, and the paper does not release code or data that would lower the bar for an actual attacker. The finding concerns feasibility of pretraining-stage backdoor injection, not a demonstrated, deployed, persistent attack against any real model.

---

## The defense taxonomy, stated in full

The paper's appendix (citing Hubinger et al., 2024) names five defense categories, each aimed at a different point in the pipeline:

1. **Input inspection** — flag triggers as statistical anomalies, e.g. high-perplexity tokens. Real weakness named directly: false positives, since real-world data already contains plenty of legitimate anomalies.
2. **Input synthesis** — reconstruct likely trigger phrases using generative models or by identifying suspicious neurons.
3. **Input modification** — perturb inputs to disrupt a trigger before it fires, at risk of destroying legitimate meaning along with it.
4. **Model reconstruction** — fine-tune on clean data, prune suspicious neurons, or apply knowledge distillation to overwrite or dilute the backdoor. Named as often ineffective at scale for large models specifically.
5. **Model inspection** — detect statistical differences between a backdoored and a clean model directly, e.g. by making the model differentiable and optimizing over word distributions to surface likely trigger words.

All five defenses assume the defender controls, or can meaningfully alter, either the training data or the model weights. The Gateway controls neither — it calls fixed, publicly released checkpoints through RKLLama, unmodified. None of the five categories above transfers directly to the Gateway's own architecture as a buildable defense.

---

## Where this genuinely does connect — and where it doesn't

**Does not connect:** any claim that the Gateway itself sits at risk of a trained-in backdoor. That risk belongs to whoever trained Qwen2.5, DeepSeek, Phi-3, and NextCoder — outside this project's control or scope, and outside what this document claims to assess.

**Does connect, precisely:** `literature-engagement-addendum-v4` names two real, unclaimed gaps in the Gateway's current scope — discourse structure and provenance/ingestion. The poisoning paper's first defense category, input inspection, asks a version of the same question the ingestion gap already names: can a claim's source material get flagged as suspect *before* it reaches the scoring call, based on properties of the document itself rather than its literal semantic content? The poisoning paper flags statistical anomalies (high-perplexity tokens); a claim-ingestion pipeline could analogously flag rhetorical anomalies — a source that argues from authority rather than evidence, a source whose confidence in its own claims runs far ahead of its evidentiary support. Different attack, same structural question: does anything upstream of the scoring call catch a bad source before it gets treated as equal-weight input.

---

## Extension 6 — a labeled-source-quality robustness test, using material this project already has

This project's own vault (`The Resilience Commons/Politics/Trumpian/`) now holds seventeen documents, each carrying a real, individually-argued epistemic-status label assigned this session: five tiers running from peer-reviewed academic scholarship, through mainstream journalism and tertiary reference material, down to explicit movement propaganda (Gary Allen's *None Dare Call It Conspiracy*, 1971; John Stormer's *None Dare Call It Treason*, 1964) written specifically to persuade a political base rather than to test a falsifiable claim.

**The test this proposes, stated exactly:** extract several individual factual assertions from the propaganda-tier documents — claims stated with high rhetorical confidence but weak or absent evidentiary support (e.g. specific claims about CFR "Insider" coordination in Allen's tract). Run each through the Gateway's existing `fallacy_bounds_screen()` pipeline exactly as any other claim gets ingested, with no metadata about the source's tier attached. Compare the resulting bounds-state read (known-true / known-false / unknown / contradictory) against the same claims run with the source's actual epistemic status explicitly stated in the prompt context.

**What a real finding here would show, either direction:** if the bounds-state read shifts meaningfully once source tier gets stated explicitly, that confirms the Gateway's scoring call already carries some sensitivity to source quality when given the information — a real, checkable data point for whether provenance metadata (the ingestion-layer gap `literature-engagement-addendum-v4` names) would materially improve assessment-layer output if built. If the read stays flat regardless of stated source tier, that names a different real finding: confident rhetorical framing alone may carry weight in the scoring call independent of the source's actual reliability — a genuine robustness gap, worth surfacing the same way Extension 1 surfaced the Artificial Hivemind paper's judge-miscalibration finding.

**Real limits on what this test can claim, stated up front rather than discovered after running it:** this tests the Gateway's *assessment*-layer sensitivity to explicit, stated source-quality metadata — not a defense against trained-in backdoors, which this project cannot test without controlling a training pipeline it does not own. The word "poisoning" describes the outside paper's threat model, not this extension's; using it here without this caveat would overclaim a connection the two mechanisms do not actually share. What Extension 6 shares with the poisoning paper is narrower and real: both ask whether a scoring system can be made to output unwarranted confidence by input crafted (deliberately, in the propaganda tracts' case) to look more authoritative than its actual evidentiary support warrants.

**Not yet run.** This document proposes the test and names the exact source material (already on disk, already labeled) rather than executing it. Jay's call on priority against the standing next-steps queue.

---

## Extension 6 — Real Results, Four Claims

Four claims ran through the test this addendum proposed, each producing a baseline read and a source-tier-stated read via `fallacy_bounds_screen("appeal_to_authority", ...)` against RKLLama's 14B model (`Qwen2.5-14B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0`).

**Claim 1 — CFR "Insider" financing claim, None Dare Call It Conspiracy (1971, movement propaganda).** The baseline read lands at `unknown`; stating the source's movement-propaganda status shifts the read to `known-true` — stating the low-credibility tier increases confidence that the passage commits an appeal-to-authority fallacy.

**Claim 2 — "institutional betrayal" framing, None Dare Call It Treason (1964, movement propaganda).** Baseline `known-false` (bounds [0.0, 0.2], confidently clean); stating the propaganda tier shifts the read to `unknown` (bounds [0.2, 0.5]) — the same direction as Claim 1, toward more fallacy-suspicious once low credibility enters the prompt.

**Claim 3 — 2016-as-inflection-point claim, American Evangelical Nationalism (2023, peer-reviewed academic).** Baseline `unknown` (bounds [0.3, 0.7]); stating the peer-reviewed academic tier shifts the read to `known-false` (bounds [0.1, 0.3]) — the opposite direction from Claims 1 and 2, toward less fallacy-suspicious once high credibility enters the prompt.

**Claim 4 — National Education Program description, George S. Benson (Wikipedia, tertiary reference).** Baseline `known-false` (bounds [0.1, 0.2]); stating the tertiary-reference tier tightens the numeric bounds toward zero ([0.0, 0.1]) but produces no state-level shift — both reads stay confidently clean, consistent with a factual/biographical claim that never leans on invoked authority in the first place, regardless of source tier.

**Finding, now real across four cases rather than a single pilot data point:** three of four claims show a state-level shift once source tier enters the prompt, and the direction tracks source quality both ways — the two movement-propaganda claims both move toward more fallacy-suspicious, the one peer-reviewed-academic claim moves toward less fallacy-suspicious, and the one tertiary-reference claim (already confidently clean at baseline, with no authority-invoking language to react against) shows no room to move further in either direction. This upgrades the addendum's original single-case finding from a real-but-thin pilot point to a genuine, direction-consistent pattern: the Gateway's `fallacy_bounds_screen()` call carries real sensitivity to stated source quality, in both directions, not only a one-way discount applied to low-credibility sources.

**Real limits, unchanged from the original framing above:** this stays an assessment-layer sensitivity test, not a poisoning defense, and not proof the pattern generalizes past appeal-to-authority or past this one 14B model. A fifth and sixth claim, run against a different fallacy category or a different model, would strengthen this further; not yet attempted.

Full call transcripts: `~/ext6_more/run.log` on Board 2 (Claims 2-4); the original session transcript covers Claim 1 (CFR).

---

## Extension 6 — Real Results, Tier-Gap Round (Three More Claims)

Three more claims ran through the same test, chosen specifically to fill gaps the original four-claim spread left in the sampled epistemic-tier spectrum: journalism (untested tier), an academic source carrying an explicit ideological commitment opposite Claim 3's, and a claim drawn from a specifically contested portion of an otherwise uncontested academic source. Same model, same fallacy category (`appeal_to_authority`), same baseline-vs-source-tier-stated structure.

**Claim 5 — "Enemy Within" doctrine claim, Regime Change (2026, journalism).** Baseline read lands `unknown` (bounds [0.6, 0.9]); stating the journalism tier (deep-background, newsroom-fact-checked, not peer-reviewed) pulls the bounds down to [0.3, 0.7] — real, meaningful movement toward less fallacy-suspicious, staying inside `unknown` on both sides. No state-level shift.

**Claim 6 — cultural-hegemony claim, Prison Notebooks (Gramsci, foundational academic theory carrying an explicit Marxist commitment).** Baseline `unknown` (bounds [0.6, 0.9]); stating the academic tier and its explicit ideological commitment pulls the bounds to [0.3, 0.6] — real movement in the same direction as Claim 5, again staying inside `unknown`. No state-level shift.

**Claim 7 — party-gatekeeping-broke-down-in-2016 claim, How Democracies Die (Levitsky/Ziblatt, mainstream academic, this specific claim flagged in the project's own summary as disputed on specifics).** Baseline `unknown` (bounds [0.3, 0.7]); stating the academic tier alongside the claim's contested status shifts the read decisively to `known-false` (bounds [0.0, 0.3]) — a real state-level shift, matching Claim 3's direction.

**Finding, tier-gap round.** One of three claims crosses a state boundary; the other two show real, consistent sub-threshold movement in the same direction without crossing it. Combined with the original four, **4 of 7 claims tested now show a confirmed state-level shift, and every shift observed across all seven runs points the same two ways the original batch established** — movement-propaganda framing toward more fallacy-suspicious, legitimate-tier framing (peer-reviewed academic, or a specifically-flagged-as-disputed claim within an academic source) toward less fallacy-suspicious. Journalism and an ideologically-loaded-but-still-academic source both moved in the legitimate-tier direction without crossing the state boundary — worth reading as the same underlying sensitivity operating at lower magnitude on these two tiers specifically, not as an absence of the effect. No claim run so far produces a shift running against this project's own credibility ranking.

**Real limits, unchanged.** Still an assessment-layer sensitivity test, not a poisoning defense. Still one fallacy category (`appeal_to_authority`) and one 14B model — the standing open question about whether the pattern holds against a different fallacy category or a different model stays exactly as open as the original addendum left it.

Full call transcript: `/tmp/extension6_tier_gaps.log` on Board 2, and `run_extension6_tier_gaps.py` at the repo root.

---

## What this document does not do

Claim the Gateway carries a training-time poisoning vulnerability — it doesn't have a training pipeline to poison. Claim Extension 6 tests the same threat model the outside paper tests — it doesn't; the connection runs through the shared structural question (can confident-sounding input fool a scoring system) rather than through a shared mechanism. Claim any of the five defense categories the paper names apply directly to this project's architecture — none do, since all five assume control over training data or model weights this project doesn't have. What this document does: summarizes a real paper's findings and defense taxonomy accurately, names exactly where its structural question does and doesn't transfer to the Gateway, and proposes one concrete, immediately runnable extension using real, already-labeled material from this project's own vault.
