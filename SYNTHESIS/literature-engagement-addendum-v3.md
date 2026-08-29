---
synthesis_type: literature_engagement_addendum
addendum_to: [neuro-symbolic-fallacy-screen-v1, structure-layer-mapping-v1, insight-contribution-v1]
trigger: artificial-hivemind-arxiv-2510.22954-2026-08-18
claims_tested: 0
date_executed: "2026-08-18"
status: addendum — Extension 1's `review_priority()` confirmed wired into a live run's own output (2026-08-23, DeepSeek 14B's PRIORITY REVIEW QUEUE block); Extension 2 ran to full completion against Phi-3-mini, real cross-family comparison data exists; Extension 3 ran to full completion 2026-08-24 against three more models (DeepSeek 14B, NextCoder-7B, Qwen3-4B), full cross-family comparison against the original Qwen2.5-14B baseline computed directly from all four progress files -- a fourth candidate (Qwen3.5-0.8B) closed as a real, unrecoverable infrastructure failure, documented as a negative result rather than omitted; Extension 5 (2026-08-26/27) ran a sixth model (Qwen2.5-7B-Instruct, same lineage as the baseline) to full completion -- 70.1% exact-state agreement with the 14B baseline, far higher than any cross-lineage pairing tested, real evidence that lineage predicts agreement more strongly than parameter count -- and closed a second model (DeepSeek-R1-Distill-Qwen-7B) on real behavioral failure under both ENABLE_THINKING settings, a different failure shape than Qwen3.5-0.8B's load-time crash
written_in_e_prime: true
tags: [model-routing, architecture]
---

# A Fourth Outside Paper — What Judge-Calibration Data Means for the Gateway

A fourth real paper now speaks directly to a mechanism the Gateway depends on every time it runs.

Jiang, Chai, Li, and others (2026), "Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond)," NeurIPS 2025 (arXiv:2510.22954), measures two things: how much a single model repeats itself across independent samples of the same query, and how well LM judges, reward models, and LM-perplexity scores track human ratings on open-ended responses. Full independent screen of the paper's own claims runs in `CLAUDE_INDEPENDENT_RUNS/artificial-hivemind-decomp-report-20260818.md`, in this same directory tree.

Our standing rule here: new evidence that speaks to our project's mechanisms gets stated plainly, not folded in quietly. This document states exactly what the paper's judge-calibration finding means for the Gateway's own scoring calls, where it sharpens output the Gateway already produces, and two concrete build items it motivates. Extension 1 carries real, working code but awaits wiring into a live batch run. Extension 2 ran to full completion against Phi-3-mini, delivering real cross-family comparison data.

---

## What the paper actually found, stated plainly

Two findings, not one:

**Repetition.** A single model, sampled repeatedly at high-temperature settings meant to encourage variety, still produces responses that cluster tightly — pairwise similarity above 0.8 in the large majority of cases.

**Judge miscalibration.** LM judges, reward models, and perplexity-based scores track human ratings worse specifically on two kinds of cases: responses humans rate as comparably good, and responses where human raters disagree most. Both cases sit exactly where a scoring model most needs to get things right, and exactly where the paper's data says it does worst.

---

## Where this bears on the Gateway directly

The Gateway calls a language model to score bounds pairs for each fallacy subcondition, then reads the combined bounds into one of four states: known-true, known-false, unknown, contradictory. That scoring call functions as a judge call in the paper's exact sense — an LM asked to rate something against a rubric, with no single ground-truth answer available for most real claims.

The paper's finding maps onto the Gateway's own state space with unusual precision. "Unknown" names the state the bounds combine to when the underlying subcondition scores land in real, unresolved territory — not confidently true, not confidently false. That occupies structurally the same territory the paper describes as hardest for a judge model to calibrate: cases lacking a single, clear-cut answer. The paper gives no reason to doubt "known-true" or "known-false" results specifically, since those correspond to the paper's less-contested, higher-agreement cases. It gives a specific, data-backed reason to treat "unknown" and "contradictory" results as less certain than the state label alone conveys.

None of this gives a reason to distrust the Gateway. The four-state bounds design, built before this paper existed, already answers the paper's stated critique of reward models and LM judges — that they "assume a single, consensus notion of quality" and fail on genuinely contested cases. Preserving "unknown" as a first-class output instead of forcing a verdict matches exactly the structural move the paper's data now justifies. Real, independent validation of a design choice already made.

What the paper adds: a concrete argument for treating the four states unevenly downstream, rather than as four equally-trustworthy readings.

---

## Structural validation, stated for citation

This section states the point above in full, on its own, in the form it needs to take if it ever gets quoted to a grant reviewer or judge — not folded into a paragraph about something else.

Artificial Hivemind's stated critique of current reward models and LM judges: they "assume a single, consensus notion of quality" and, by that assumption, fail specifically on genuinely contested cases — the ones where quality doesn't collapse to one number. The paper's own annotation data backs this: LM judges, reward models, and perplexity scores all correlate worse with human ratings exactly on the subset of responses humans themselves rate as comparably good or disagree about most.

The Gateway's four-state bounds design does not force a verdict. Every scoring call returns a `[lower, upper]` interval, not a scalar, and that interval reads into one of four states — known-true, known-false, unknown, contradictory — with "unknown" and "contradictory" standing as first-class outputs, not error states or fallback cases. A claim that genuinely sits in contested territory comes back reading as contested. Nothing in the pipeline collapses that toward a false single verdict the way a scalar reward score or a forced-binary judge call would.

This design predates the paper. `combine_bounds_and()`, `combine_bounds_or()`, and `bounds_state()` existed in this codebase before Artificial Hivemind's arXiv posting, built from first-principles reasoning about what a fallacy-screen bounds pair needed to represent, not built in response to any external critique of judge calibration. The paper did not motivate the design. The paper independently arrived at the empirical case for why the design's core choice — preserving genuine uncertainty as an output state rather than resolving it into a forced answer — matters. Two separate lines of reasoning, one architectural and one empirical, landing on the same structural principle without either informing the other.

Stated as plainly as the claim allows: a system that already refuses to force verdicts on contested cases does not need to change in response to a finding that judges which force verdicts on contested cases get those cases wrong. It already built around that exact failure mode. What changes, per Extension 1 above, concerns how much downstream attention each of the four states earns — not what the four states mean or how they combine.

---

## Extension 1 — review-priority flag

**Proposal:** every bounds-screen result carries a `review_priority` field, computed directly from `bounds_state()`'s output:

```python
def review_priority(state: str) -> str:
    """Maps a four-state bounds read to a review-priority label. 'unknown'
    and 'contradictory' get 'high' -- Artificial Hivemind (arXiv:2510.22954)
    finds LM judges miscalibrate specifically on contested, non-clear-cut
    cases, which is the same territory these two states describe. 'known-
    true' and 'known-false' get 'standard' -- the paper gives no data-backed
    reason to distrust confidently-resolved reads specifically."""
    return {
        "known-true": "standard",
        "known-false": "standard",
        "unknown": "high",
        "contradictory": "high",
    }[state]
```

Attached to every `circular_argument_screen()` and `fallacy_bounds_screen()` result, this costs nothing extra at call time — no new model call, no new prompt, pure post-processing on data the Gateway already produces.

**Batch-runner surfacing:** `run_all_26_rkllama.py` and `run_local_neuro_symbolic_batch.py` currently print a flat summary table as results land. Add a `PRIORITY REVIEW QUEUE` block at the top of both the console summary and the saved JSON — every `high`-priority result listed first, grouped by claim, before the `standard`-priority results. A human reviewing output spends their attention where the paper's own data marks a model as least trustworthy, not spread evenly across all 26 categories regardless of state.

**Independent-eval precedent:** the Artificial Hivemind decomposition report already does this by hand — six flagged checks surfaced in a table before the full 156-entry appendix. This extension formalizes that pattern into the tool itself, rather than redoing it manually on every future run.

---

## Extension 2 — cross-family model diversity for the Gateway's own scoring calls, local-only

The paper's inter-model finding (cross-model similarity 71–82%, sometimes exceeding intra-model similarity) raises a question about the Gateway specifically: every live scoring call currently routes to one model family. RKLLama on Board 2 serves Qwen2.5 (7B or 14B) exclusively — same lineage, same training pipeline, regardless of which size runs.

**Correction, 2026-08-18, same day:** the original version of this section named Ling and Kimi via OpenRouter as the real, already-available cross-family path. Jay's direct call, same day: not used for the Gateway's own scoring calls — local-only, the same principle already governing Doppelganger's render pipeline. Struck here rather than left standing as a live option. The Session 100 vault-mapping precedent (Opus/Ling/Kimi divergence, `in/SYSTEM/vault-maps/run-01/02/03`) stays real and worth knowing about, but it doesn't license using those models for this project's own scoring calls.

**Update, 2026-08-19 — installed and live.** Phi-3-mini-4k-instruct-w8a8 (GatekeeperZA on HuggingFace, matched to Board 2's confirmed v1.2.3 runtime) sits downloaded, byte-verified (3,946,316,324 bytes), and confirmed real via a live `GET /v1/models` call, at `/opt/rkllama/src/rkllama/config/models/Phi-3-mini-4k-instruct-w8a8/` on Board 2. Real path used a pre-converted community build, not Rockchip toolkit conversion — no Rockchip toolkit access exists on any machine in this stack (Mac mini, Board 1, Board 2), and none ever ran. This session's install happened inside the in/ vault's application-level MoE router build (`in/SYSTEM/moe_router.py`), where Phi-3 now serves as `DIVERSITY_MODEL`, alongside NextCoder-7B (`CODE_MODEL`) and Qwen3-1.7B (`CLASSIFIER_MODEL`). A genuinely different lineage (Microsoft, not Alibaba) now runs fully local on Board 2, inside the same trust boundary IMST and Doppelganger already operate under.

**What this buys, concretely, now that Phi-3 exists and loads:** running the same claim through `fallacy_bounds_screen()` against RKLLama-Qwen and against RKLLama-Phi-3, then comparing bounds pairs, tests directly whether the Gateway's own scoring exhibits the same convergent-judgment risk the paper measures across models generally — rather than assuming a single model's score functions as ground truth. Genuine cross-family agreement on a bounds read would carry more weight than any single model's read alone. Genuine cross-family disagreement would itself carry a signal worth surfacing — likely warranting `high` review priority regardless of what any individual model's state read says. **Run to completion, 2026-08-19 — real results below, see "Extension 2 real-run confirmation."**

**Not proposed, either before or after this correction:** Opus, Fable, or any other Anthropic-hosted model for this purpose. The standing rule closing off live runs against a real Anthropic API key applies to those regardless of the calibration case made here.

---

## Real-run confirmation (2026-08-18, same day) — topic-dependent and category-dependent hedging, found in the actual data

The full 78-call live run (`run_all_26_rkllama.py`, RKLLama Qwen2.5-14B, three pilot claims) completed the same day this addendum first went up, 0 failures after `strip_markdown_fences()`'s mid-document fix. Real output confirms Extension 1's premise directly and sharpens Extension 2's case beyond what the addendum originally proposed.

**Unknown rate varies nearly 3x by topic, same model, same 26-category screen:** `covid-003` (virology, furin cleavage site) lands unknown on 77% of its 26 calls; `eggs-003` (clinical statistics) on 54%; `blackhole-002` (physics) on 27%. This narrows the addendum's original framing of RKLLama's hedging as a general calibration-width property — that direction holds, but the magnitude depends heavily on subject matter, not just on the model's general tendency to hedge.

**Six categories run unknown on all three claims regardless of topic:** `appeal_to_ignorance`, `double_counting`, `false_equivalence`, `no_true_scotsman`, `part_to_whole_mixup`, `word_shift`. A second, separate mechanism from the topic effect above — something about how these six subconditions get asked produces wide bounds independent of what claim sits underneath them. Full breakdown: `CLAUDE_INDEPENDENT_RUNS/rkllama-78-run-analysis-20260818.md`.

Both findings sharpen Extension 2's test beyond "do different models converge on the same bounds." The real question for a second, local-only model (Phi-3, once converted) now has two specific, checkable shapes: does it show the same skew toward `covid-003` specifically, and does it hedge on the same six categories regardless of claim. Agreement or divergence on *which* claims and categories draw uncertainty carries more signal than agreement on raw bounds-pair values alone. Not run yet — blocked on Phi-3 conversion, not on Jay's timing call this time.

---

## Extension 2 real-run confirmation (2026-08-19) — Phi-3 comparison complete, a genuine and specific disagreement pattern found

`cross_family_comparison_rkllama.py` (new file) ran the full 78-call circular-argument + 25-category bounds screen against Phi-3-mini-4k-instruct-w8a8, reusing Qwen2.5-14B's already-complete 78 calls directly rather than re-running them. Real work reaching a clean 156/156 required four real fixes: two genuine model-install gaps (neither Phi-3 nor NextCoder-7B carried a working Modelfile until this session, despite both showing byte-verified weights and a confirmed `GET /v1/models` string — a live `/load_model` call now confirms both load-capable for real, not merely downloaded), a wrong JSON field-name assumption on the first live `/load_model` attempt, and three further real RKLLama YAML-formatting shapes Phi-3 produces that Qwen never triggered — an unindented block-scalar body, a dropped `_bounds` suffix on a subcondition key, and an orphaned continuation paragraph spanning a blank line under an inline value. `strip_markdown_fences()` now carries seven total real-failure passes, six from Qwen's original run plus this session's three, each confirmed against the exact captured text that broke it, plus a full regression suite covering every prior shape before any fix landed. Full technical detail: TRC's own ERRORS.md and MEMORY.md, 2026-08-19.

**Real comparison, 78/78 clean, 29.5% cross-family agreement.** Two specific, checkable questions the prior entry named now carry real answers:

**Phi-3 does not reproduce the six systemically-hedging categories.** The six categories (`appeal_to_ignorance`, `double_counting`, `false_equivalence`, `no_true_scotsman`, `part_to_whole_mixup`, `word_shift`) hedged unknown on all three claims, every time, for Qwen. Phi-3 hedges unknown on those same six categories only 17% of the time — where Qwen consistently could not commit, Phi-3 mostly resolves, usually to `known-true` at high confidence (typically 0.75–1.0 bounds).

**The topic-skew Qwen showed runs in reverse for Phi-3.** Qwen's unknown rate ran `covid-003` 77%, `eggs-003` 54%, `blackhole-002` 27% — covid read hardest for Qwen. Phi-3's unknown rate ran `eggs-003` 50%, `covid-003` 27%, `blackhole-002` 8% — covid read easiest for Phi-3, relatively speaking. Same three claims, opposite direction of relative difficulty between the two families.

**The dominant shape across the 55 real disagreements: Qwen sits at unknown while Phi-3 commits to a confident state, either direction, far more often than the reverse.** Phi-3 resolves; Qwen hedges. A consistent behavioral asymmetry under the identical prompt, not scattered noise.

**Real caveat, stated directly rather than left implicit:** Phi-3-mini runs at roughly a quarter of Qwen2.5-14B's parameter count. Some or much of this disagreement plausibly reflects a raw capability gap rather than genuinely independent judgment on comparably-difficult reasoning — the addendum's own reasoning for treating cross-family agreement as a meaningful signal assumed comparable capability between the two models compared, an assumption this specific pairing does not meet. The 29.5% agreement rate measures something real about these two specific models; it does not, on its own, measure the convergent-judgment risk Artificial Hivemind names for comparably-capable models generally.

**Practical implication for Extension 1's `review_priority()` flag, run against this real pairing:** 70.5% of the 78 comparisons would flag `high` under a cross-family-disagreement rule. Genuine structural finding regardless of the capability-gap caveat above — this specific pairing offers weak corroboration value as a diversity check, not because the mechanism fails, but because a 3.8B and a 14B model read the same fallacy-screen prompts too differently for agreement itself to carry much weight. A same-capability-class second model (a different ~14B lineage, if one becomes available for this board) would test the addendum's original question more cleanly than this pairing does.

Full raw data: `NEURO_SYMBOLIC_RUNS/cross-family-comparison-raw.json` (156 calls) and `cross-family-comparison-report.json` (the full 78-row comparison, every state, bounds pair, and review-priority flag from both models, side by side).

---

## Extension 3 — three more models run to completion, full cross-family comparison against the original Qwen2.5-14B baseline, one model closed as a real infrastructure dead end

DeepSeek-R1-Distill-Qwen-14B (78-call run complete 2026-08-23), NextCoder-7B (2026-08-24), and Qwen3-4B-Instruct-2507 (2026-08-24, after a real reproducible YAML-parsing bug found and fixed mid-run — full detail TRC's own ERRORS.md/MEMORY.md 2026-08-24) all reached genuine 78/78, 0-failed completion. A fourth candidate, Qwen3.5-0.8B, never produced a scoring result at all — its first call hit a real, unrecoverable native RKLLM runtime failure at model load (`Failed to initialize RKLLM model: -1`), diagnosed to the closed-source runtime binary itself after ruling out every externally-checkable cause (file integrity, Modelfile/toolkit version, kernel/driver). Closed and dropped 2026-08-24, same disposition as the earlier-rejected Qwen3.5-9B-HighIQ candidate. That closure counts as a real result in its own right — a documented infrastructure boundary, distinct in kind from the behavioral findings below, not a gap in this write-up.

**Real correction to a figure stated in TRC's own session memory:** Qwen3-4B's own unknown-rate reads 2/78 (2.6%), not the 3/78 (3.8%) figure logged at the 2026-08-24 session wrap. Recomputed directly from `NEURO_SYMBOLIC_RUNS/all-26-rkllama-progress-qwen3-4b.json` for this write-up: exactly two `unknown` states appear (`blackhole-002/motte_and_bailey`, `covid-003/rushed_conclusion`); the third call named in the earlier count, `covid-003/ignoring_base_rate`, resolved to `known-false` once the YAML bug's fix let it parse — the earlier figure appears to have counted it twice, once as the pre-fix failure and once after. Corrected here rather than left standing.

**Own-model unknown-rate, all four completed models, recomputed directly from each progress file for this write-up (not from memory):**

| Model | Params | Overall unknown | blackhole-002 | covid-003 | eggs-003 |
|---|---|---|---|---|---|
| Qwen2.5-14B (original baseline) | 14B | 41/78 (52.6%) | 26.9% | 76.9% | 53.8% |
| DeepSeek-R1-Distill-Qwen-14B | 14B | 15/78 (19.2%) | 30.8% | 23.1% | 3.8% |
| Phi-3-mini-4k-instruct | 3.8B | — (Extension 2) | 8% | 27% | 50% |
| NextCoder-7B | 7B | 8/78 (10.3%) | 7.7% | 3.8% | 19.2% |
| Qwen3-4B-Instruct-2507 | 4B | 2/78 (2.6%) | 3.8% | 3.8% | 0.0% |

Two structural findings jump directly out of this table, both real and checkable against the files themselves, not narrative smoothing:

**The topic-skew from the original pilot run does not generalize as a claim-difficulty property — it reverses, flattens, or points a different direction for every other model.** Qwen2.5-14B's original run named `covid-003` hardest by a wide margin (76.9%) and `blackhole-002` easiest (26.9%). DeepSeek reverses it (`blackhole-002` hardest at 30.8%, `eggs-003` easiest at 3.8%). Phi-3 (Extension 2) reversed it a different way (`eggs-003` hardest, `blackhole-002` easiest). NextCoder-7B names `eggs-003` hardest. Qwen3-4B shows no meaningful skew at all — its total unknown count (2) sits too low to support a difficulty ranking. Five models, at least three genuinely different "hardest topic" answers. The addendum's original framing treated topic difficulty as something the claim itself carries; the real data across five independent runs says it's model-specific, not claim-specific.

**Every model after the original Qwen2.5-14B baseline hedges dramatically less, and the six systemically-hedging categories named in the first real-run confirmation reflected a Qwen2.5-14B-specific pattern, not a category-shape property.** `appeal_to_ignorance`, `double_counting`, `false_equivalence`, `no_true_scotsman`, `part_to_whole_mixup`, `word_shift` scored `unknown` on all three claims, every time, for Qwen2.5-14B (18/18, 100%). Recomputed for the same six categories against every other model: DeepSeek 1/18 (5.6%), NextCoder-7B 1/18 (5.6%), Qwen3-4B 0/18 (0%) — matching Phi-3's own 17% from Extension 2 in direction if not exact magnitude. Four independent models, four confirmations that this didn't concern how those six subconditions get asked; it concerned how Qwen2.5-14B specifically answers them.

**No model, across all 312 calls in these four runs, ever produced the fourth bounds state, `contradictory`.** Worth stating plainly since the architecture's four-state design treats it as a first-class output, not a hypothetical — in practice, across five separate models now (including Phi-3), the state space in live use collapses to three, not four. Not a design flaw; a real empirical fact about how these models' bounds pairs actually combine under `combine_bounds_and()`/`combine_bounds_or()`, worth knowing rather than assuming.

**Cross-family exact-state agreement, computed directly across all four models on the same 78 (claim, category) pairs: 17/78 (21.8%) agree across all four simultaneously.** Pairwise breakdown, all six pairs:

| Pair | Agreement |
|---|---|
| DeepSeek-14B vs Qwen3-4B | 46/78 (59.0%) |
| DeepSeek-14B vs NextCoder-7B | 34/78 (43.6%) |
| Qwen2.5-14B vs Qwen3-4B | 34/78 (43.6%) |
| Qwen2.5-14B vs DeepSeek-14B | 32/78 (41.0%) |
| NextCoder-7B vs Qwen3-4B | 31/78 (39.7%) |
| Qwen2.5-14B vs NextCoder-7B | 24/78 (30.8%) |

**Extension 2 named an unmet need — a same-capability-class second model, since Phi-3's 3.8B against Qwen2.5-14B's 14B left the 29.5% agreement figure confounded by a real capability gap. DeepSeek-R1-Distill-Qwen-14B answers that need directly: same 14B parameter count as the original baseline, genuinely different lineage (DeepSeek's own distillation pipeline, not an Alibaba release) and genuinely different training approach (reasoning-distilled, not instruction-tuned the same way).** Its agreement rate with Qwen2.5-14B, 41.0%, sits meaningfully higher than Phi-3's 29.5% — consistent with capability match reducing spurious disagreement, as the capability-gap caveat in Extension 2 predicted it would. It does not close the gap to anywhere near full agreement. Two models at matched parameter count, asked the identical 78 questions, land on the identical four-state read only 41% of the time. Whatever drives the remaining 59% disagreement, raw capacity doesn't explain it — architecture, training data, or training method do, and the paper's convergent-judgment concern applies to this pairing with real force, not with the capability-gap discount Extension 2 had to apply to Phi-3.

**Directionality confirms and sharpens the same asymmetric pattern Extension 2 found with Phi-3, replicated three more times, with one further real asymmetry only visible now:** when Qwen2.5-14B reads `unknown` (41 cases), DeepSeek resolves to a confident state in 34/41 (83%), NextCoder-7B in 37/41 (90%), Qwen3-4B in 41/41 (100%). Qwen2.5-14B hedges; every other model in this comparison mostly commits. But the reverse check, run only for the matched-capability DeepSeek pairing, shows something Extension 2 couldn't test with Phi-3's capability gap in the way: when DeepSeek itself reads `unknown` (15 cases, a much smaller and more selective set than Qwen2.5-14B's 41), Qwen2.5-14B agrees `unknown` in 7/15 (46.7%) — nearly half. DeepSeek's own hedges concentrate disproportionately on cases the original baseline also finds genuinely hard, even though DeepSeek hedges far less often overall. Not just "one model hedges more than another" — the smaller set of cases DeepSeek chooses to hedge on carries real informational overlap with the larger set Qwen2.5-14B hedges on, which sits closer to the kind of calibrated uncertainty the paper's own framing treats as meaningful, versus uncertainty that only reads noisier or more permissive across the board.

**Practical implication for Extension 1's `review_priority()` flag, computed both ways:** under the flag's actual own-state rule (`unknown`/`contradictory` = high), the four models flag at wildly different rates on the identical 78 calls — Qwen2.5-14B 52.6%, DeepSeek 19.2%, NextCoder-7B 10.3%, Qwen3-4B 2.6%. Under a cross-family-disagreement rule instead (flag anything where the four models don't all agree), 61/78 (78.2%) would flag high — nearly the inverse of Qwen3-4B's own confidence in itself. The two rules measure genuinely different things: one flags a single model's self-reported uncertainty, the other flags convergent-judgment risk across models regardless of any single model's confidence. A `high` flag under the second rule can and does occur even when every individual model reports a confident state — the paper's own point, now demonstrated directly in this project's own data rather than argued abstractly.

**Real caveat, stated as directly as Extension 2's own:** NextCoder-7B (7B) and Qwen3-4B-Instruct-2507 (4B) both sit well below Qwen2.5-14B's 14B, the same capability-gap caveat Extension 2 applied to Phi-3 applies to both here — their high agreement with each other (39.7%) and with DeepSeek (43.6%, 59.0%) plausibly reflects convergent "small confident model" behavior as much as genuine independent judgment. DeepSeek-14B alone among pairings in this comparison avoids that specific confound, and its 41.0% agreement with Qwen2.5-14B stands as the number in this document that comes closest to isolating the paper's actual convergent-judgment question from a simple capability story.

Full raw data behind every number above: `NEURO_SYMBOLIC_RUNS/all-26-rkllama-progress.json` (Qwen2.5-14B baseline), `all-26-rkllama-progress-deepseek14b.json`, `all-26-rkllama-progress-nextcoder7b.json`, `all-26-rkllama-progress-qwen3-4b.json`. No new comparison script proved necessary — `cross_family_comparison_rkllama.py`'s existing per-call JSON shape already carries everything this write-up computed; the analysis above ran directly against the four progress files, keyed on `(claim_id, category)`, matching Extension 2's own comparison method.

---

## Extension 5 — a sixth model, same lineage as the original baseline, and a real behavioral closure distinct in kind from Qwen3.5-0.8B's infrastructure failure

Qwen2.5-7B-Instruct reached genuine 78/78 completion 2026-08-26, 77 real parses and one genuine content-omission (`covid-003/appeal_to_nature` returned no scoreable content, not a parsing failure — the same distinction Extension 3 drew for its own single omission). Two real `ingest.py` fixes landed the same session: a ninth defensive pass (an orphaned trailing paragraph after a bulleted list) and a hardened eighth pass (the already-quoted check broadened to catch colon-prefixed incomplete values regardless of leading character), both confirmed against the exact failed captures that exposed them.

**Own-model unknown rate: 44/77 (57.1%) — the highest of any model tested in this series, Qwen2.5-14B's own 52.6% included.** Recomputed directly from `NEURO_SYMBOLIC_RUNS/all-26-rkllama-progress-qwen257b.json` for this write-up. Per-topic: `eggs-003` 13/26 (50.0%), `covid-003` 17/25 (68.0%), `blackhole-002` 14/26 (53.8%).

**The topic-skew question Extension 3 left open now has a real answer: lineage predicts topic-skew direction, not size.** Every model in Extension 3 reversed, flattened, or redirected Qwen2.5-14B's original `covid-003`-hardest finding — DeepSeek named `blackhole-002` hardest, Phi-3 named `eggs-003` hardest, NextCoder-7B named `eggs-003` hardest, Qwen3-4B showed no meaningful skew. Qwen2.5-7B breaks that pattern: `covid-003` reads hardest for it too (68.0%, versus the baseline's 76.9%), the only tested model besides the 14B baseline itself to land on that same claim as hardest. The one variable Qwen2.5-7B shares with the baseline and no other tested model shares: same lineage, same training pipeline, different parameter count.

**The six systemically-hedging categories from the original pilot run (`appeal_to_ignorance`, `double_counting`, `false_equivalence`, `no_true_scotsman`, `part_to_whole_mixup`, `word_shift`) reproduce far more strongly here than in any other tested model.** Qwen2.5-14B hedged all 18/18 (100%) on these six, across all other tested models the rate dropped to 0–17%. Qwen2.5-7B hedges 16/18 (88.9%) — `appeal_to_ignorance` 3/3, `double_counting` 3/3, `part_to_whole_mixup` 3/3, `word_shift` 3/3, `false_equivalence` 2/3, `no_true_scotsman` 2/3. Extension 3 named this pattern Qwen2.5-14B-specific, not category-shape-specific. The real data now says more precisely: Qwen2.5-*lineage*-specific, largely independent of which size in that lineage runs.

**Exact-state agreement with the Qwen2.5-14B baseline, computed directly against the same 78 (claim, category) pairs: 54/77 (70.1%) — nearly 30 points higher than the best cross-lineage pairing in this entire series (DeepSeek-14B's 41.0%, same parameter count as the baseline, different lineage).** This sharpens Extension 3's own capability-gap caveat into a real, checkable claim rather than a plausible-sounding hedge: parameter count doesn't predict agreement with the baseline nearly as well as lineage does. A 7B model from the same family agrees with its 14B sibling almost twice as often as a 14B model from a different family agrees with it.

**Directionality confirms the lineage-agreement finding from a second angle.** Every cross-lineage model in Extension 3 mostly resolved cases the baseline hedged on — DeepSeek 83%, NextCoder-7B 90%, Qwen3-4B 100%. Qwen2.5-7B resolves only 10/41 (24.4%) of the baseline's hedge cases — it hedges alongside its sibling far more than it commits past it. The reverse check runs the same direction: of the 44 cases Qwen2.5-7B itself hedges on, the 14B baseline agrees `unknown` on 13 (29.5%), a real overlap, though smaller than the forward direction and worth reading as a real number rather than a round one.

**Real infrastructure boundary, distinct in kind from Qwen3.5-0.8B's closure: DeepSeek-R1-Distill-Qwen-7B-w8a8 closed 2026-08-27, both `ENABLE_THINKING` settings tested and both genuinely failed the task.** Where Qwen3.5-0.8B never produced a single scoreable call (a load-time runtime crash, `Failed to initialize RKLLM model: -1`), DeepSeek-7B loaded and ran — the failure showed up in its output, not its startup. `ENABLE_THINKING=False`: all 4 attempted calls stopped mid-sentence at 30.1–30.5s elapsed, `finish_reason: "stop"`, no answer, no `</think>` tag — confirmed via direct capture, not inferred. `ENABLE_THINKING=True`: a single-call diagnostic passed clean, but the full rerun hit a genuine infinite repetition loop on the first call, the same conclusion repeated verbatim across 8+ cycles, confirmed via `journalctl`, never converging past a 400s timeout. Both settings tested, both failed, for two different and unrelated reasons — a real model/task mismatch, not a tunable config problem. Model deleted from Board 2, including two root-owned subdirectories. `moe_router.py`'s `FAST_REASONING_MODEL` now points at `REASONING_MODEL` (the 14B) rather than a dedicated fast tier, until a genuine replacement gets tested and confirmed real.

**State-space finding extends to a sixth model:** across all six real completed runs in this series now (Qwen2.5-14B, Phi-3-mini, DeepSeek-14B, NextCoder-7B, Qwen3-4B, Qwen2.5-7B — 467 real parsed classifications, one genuine omission each in the Qwen2.5-14B and Qwen2.5-7B runs, 468 calls attempted), the fourth bounds state, `contradictory`, still never once appears. Six independent models, zero occurrences — the state space in live use collapses to three in practice, a real empirical fact this series keeps confirming rather than a one-run artifact.

Full raw data: `NEURO_SYMBOLIC_RUNS/all-26-rkllama-progress-qwen257b.json` (77 parsed results), `all-26-rkllama-progress-qwen257b-priority-queue.json` (review-priority flags), `all-26-rkllama-progress-deepseek7b.json` (4 real stopped-early captures, preserved as closure evidence rather than discarded).

---

## What this document does not do

Rewrite the Gateway's core architecture, take back any prior claim about the four-state bounds design, or claim "unknown" results as wrong. The paper gives a reason to weight review attention unevenly across states that already exist — not a reason to change what those states mean or how they combine.

All extensions above now carry real code and real execution behind them, not just proposals in name. Extension 1 has real, working code (`review_priority()`, above), confirmed wired into a live run's own printed output (2026-08-23). Extension 2 has real, working code, run to full completion against Phi-3-mini — see "Extension 2 real-run confirmation" above: 29.5% cross-family agreement, Phi-3 does not reproduce Qwen's six-category hedge pattern, and a real capability-gap caveat on how much weight the disagreement rate itself deserves. Extension 3 stands complete against three further models, one of them (DeepSeek-R1-Distill-Qwen-14B) genuinely matched in capability to the original Qwen2.5-14B baseline — see "Extension 3" above: 21.8% four-way exact-state agreement, a same-capability-class agreement rate of 41.0% that comes closer than any other cross-lineage pairing in this document to isolating the paper's actual convergent-judgment question from a raw capability gap, and a fourth model candidate (Qwen3.5-0.8B) closed as a genuine infrastructure dead end rather than a behavioral result. Extension 5 adds a sixth model and a real, sharper finding than either prior extension reached alone: lineage, not parameter count, predicts agreement with the baseline most strongly across every pairing tested so far, and a second, behaviorally distinct closure (DeepSeek-R1-Distill-Qwen-7B) shows a model can load, run, and still fail a task genuinely, a different failure shape than Qwen3.5-0.8B's load-time crash. Jay's call on whether `review_priority()`'s cross-family-disagreement variant (78.2% flag rate, computed in Extension 3) gets built into a real batch runner alongside the existing own-state rule, and on whether a genuinely different, matched-lineage-to-nobody-tested-yet model gets pursued to test the lineage-agreement finding against a case this document hasn't yet covered.
