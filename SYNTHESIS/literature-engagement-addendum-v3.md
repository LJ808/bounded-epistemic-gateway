---
synthesis_type: literature_engagement_addendum
addendum_to: [neuro-symbolic-fallacy-screen-v1, structure-layer-mapping-v1, insight-contribution-v1]
trigger: artificial-hivemind-arxiv-2510.22954-2026-08-18
claims_tested: 0
date_executed: "2026-08-18"
status: addendum — Extension 1 exists as real code, not yet wired into a live run; Extension 2 ran to full completion against Phi-3-mini, real cross-family comparison data now exists
written_in_e_prime: true
tags: [model-routing, architecture]
---

# A Fourth Outside Paper — What Judge-Calibration Data Means for the Gateway

A fourth real paper now speaks directly to a mechanism the Gateway depends on every time it runs.

Jiang, Chai, Li, and others (2026), "Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond)," NeurIPS 2025 (arXiv:2510.22954), measures two things: how much a single model repeats itself across independent samples of the same query, and how well LM judges, reward models, and LM-perplexity scores track human ratings on open-ended responses. Full independent screen of the paper's own claims runs in `CLAUDE_INDEPENDENT_RUNS/artificial-hivemind-decomp-report-20260818.md`, in this same directory tree.

Our standing rule here: new evidence that speaks to our project's mechanisms gets stated plainly, not folded in quietly. This document states exactly what the paper's judge-calibration finding means for the Gateway's own scoring calls, where it sharpens output the Gateway already produces, and two concrete build items it motivates — neither built yet.

---

## What the paper actually found, stated plainly

Two findings, not one:

**Repetition.** A single model, sampled repeatedly at high-temperature settings meant to encourage variety, still produces responses that cluster tightly — pairwise similarity above 0.8 in the large majority of cases.

**Judge miscalibration.** LM judges, reward models, and perplexity-based scores track human ratings worse specifically on two kinds of cases: responses humans rate as comparably good, and responses where human raters disagree most. Both cases sit exactly where a scoring model most needs to get things right, and exactly where the paper's data says it does worst.

---

## Where this bears on the Gateway directly

The Gateway calls a language model to score bounds pairs for each fallacy subcondition, then reads the combined bounds into one of four states: known-true, known-false, unknown, contradictory. That scoring call is a judge call in the paper's exact sense — an LM asked to rate something against a rubric, with no single ground-truth answer available for most real claims.

The paper's finding maps onto the Gateway's own state space with unusual precision. "Unknown" is the state the bounds combine to when the underlying subcondition scores land in real, unresolved territory — not confidently true, not confidently false. That is structurally the same territory the paper describes as hardest for a judge model to calibrate: cases lacking a single, clear-cut answer. The paper gives no reason to doubt "known-true" or "known-false" results specifically, since those correspond to the paper's less-contested, higher-agreement cases. It gives a specific, data-backed reason to treat "unknown" and "contradictory" results as less certain than the state label alone conveys.

This isn't a reason to distrust the Gateway. The four-state bounds design, built before this paper existed, already answers the paper's stated critique of reward models and LM judges — that they "assume a single, consensus notion of quality" and fail on genuinely contested cases. Preserving "unknown" as a first-class output instead of forcing a verdict is exactly the structural move the paper's data now justifies. Real, independent validation of a design choice already made.

What the paper adds: a concrete argument for treating the four states unevenly downstream, rather than as four equally-trustworthy readings.

---

## Structural validation, stated for citation

This section states the point above in full, on its own, in the form it needs to take if it ever gets quoted to a grant reviewer or judge — not folded into a paragraph about something else.

Artificial Hivemind's stated critique of current reward models and LM judges: they "assume a single, consensus notion of quality" and, by that assumption, fail specifically on genuinely contested cases — the ones where quality doesn't collapse to one number. The paper's own annotation data backs this: LM judges, reward models, and perplexity scores all correlate worse with human ratings exactly on the subset of responses humans themselves rate as comparably good or disagree about most.

The Gateway's four-state bounds design does not force a verdict. Every scoring call returns a `[lower, upper]` interval, not a scalar, and that interval reads into one of four states — known-true, known-false, unknown, contradictory — with "unknown" and "contradictory" standing as first-class outputs, not error states or fallback cases. A claim that genuinely sits in contested territory comes back reading as contested. Nothing in the pipeline collapses that toward a false single verdict the way a scalar reward score or a forced-binary judge call would.

This design predates the paper. `combine_bounds_and()`, `combine_bounds_or()`, and `bounds_state()` existed in this codebase before Artificial Hivemind's arXiv posting, built from first-principles reasoning about what a fallacy-screen bounds pair needed to represent, not built in response to any external critique of judge calibration. The paper did not motivate the design. The paper independently arrived at the empirical case for why the design's core choice — preserving genuine uncertainty as an output state rather than resolving it into a forced answer — matters. Two separate lines of reasoning, one architectural and one empirical, landing on the same structural principle without either informing the other.

Stated as plainly as the claim allows: a system that already refuses to force verdicts on contested cases does not need to change in response to a finding that judges which force verdicts on contested cases get those cases wrong. It already built around that exact failure mode. What changes, per Extension 1 above, is how much downstream attention each of the four states earns — not what the four states mean or how they combine.

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

**Batch-runner surfacing:** `run_all_26_rkllama.py` and `run_local_neuro_symbolic_batch.py` currently print a flat summary table as results land. Add a `PRIORITY REVIEW QUEUE` block at the top of both the console summary and the saved JSON — every `high`-priority result listed first, grouped by claim, before the `standard`-priority results. A human reviewing output spends their attention where the paper's own data says a model is least trustworthy, not spread evenly across all 26 categories regardless of state.

**Independent-eval precedent:** the Artificial Hivemind decomposition report already does this by hand — six flagged checks surfaced in a table before the full 156-entry appendix. This extension formalizes that pattern into the tool itself, rather than redoing it manually on every future run.

---

## Extension 2 — cross-family model diversity for the Gateway's own scoring calls, local-only

The paper's inter-model finding (cross-model similarity 71–82%, sometimes exceeding intra-model similarity) raises a question about the Gateway specifically: every live scoring call currently routes to one model family. RKLLama on Board 2 serves Qwen2.5 (7B or 14B) exclusively — same lineage, same training pipeline, regardless of which size runs.

**Correction, 2026-08-18, same day:** the original version of this section named Ling and Kimi via OpenRouter as the real, already-available cross-family path. Jay's direct call, same day: not used for the Gateway's own scoring calls — local-only, the same principle already governing Doppelganger's render pipeline. Struck here rather than left standing as a live option. The Session 100 vault-mapping precedent (Opus/Ling/Kimi divergence, `in/SYSTEM/vault-maps/run-01/02/03`) stays real and worth knowing about, but it doesn't license using those models for this project's own scoring calls.

**Update, 2026-08-19 — installed and live.** Phi-3-mini-4k-instruct-w8a8 (GatekeeperZA on HuggingFace, matched to Board 2's confirmed v1.2.3 runtime) sits downloaded, byte-verified (3,946,316,324 bytes), and confirmed real via a live `GET /v1/models` call, at `/opt/rkllama/src/rkllama/config/models/Phi-3-mini-4k-instruct-w8a8/` on Board 2. Real path used a pre-converted community build, not Rockchip toolkit conversion — no Rockchip toolkit access exists on any machine in this stack (Mac mini, Board 1, Board 2), and none ever ran. This session's install happened inside the in/ vault's application-level MoE router build (`in/SYSTEM/moe_router.py`), where Phi-3 now serves as `DIVERSITY_MODEL`, alongside NextCoder-7B (`CODE_MODEL`) and Qwen3-1.7B (`CLASSIFIER_MODEL`). A genuinely different lineage (Microsoft, not Alibaba) now runs fully local on Board 2, inside the same trust boundary IMST and Doppelganger already operate under.

**What this buys, concretely, now that Phi-3 exists and loads:** running the same claim through `fallacy_bounds_screen()` against RKLLama-Qwen and against RKLLama-Phi-3, then comparing bounds pairs, tests directly whether the Gateway's own scoring exhibits the same convergent-judgment risk the paper measures across models generally — rather than assuming a single model's score functions as ground truth. Genuine cross-family agreement on a bounds read would carry more weight than any single model's read alone. Genuine cross-family disagreement would itself be a signal worth surfacing — likely warranting `high` review priority regardless of what any individual model's state read says. **Run to completion, 2026-08-19 — real results below, see "Extension 2 real-run confirmation."**

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

## What this document does not do

Rewrite the Gateway's core architecture, take back any prior claim about the four-state bounds design, or assert that "unknown" results are wrong. The paper gives a reason to weight review attention unevenly across states that already exist — not a reason to change what those states mean or how they combine.

Both extensions above stay proposals in name, though both now carry real code and real execution behind them. Extension 1 has real, working code (`review_priority()`, above), not yet wired into a live run's own output. Extension 2 has real, working code, run to full completion against Phi-3-mini — see "Extension 2 real-run confirmation" above for the actual result: 29.5% cross-family agreement, Phi-3 does not reproduce Qwen's six-category hedge pattern, and a real capability-gap caveat on how much weight the disagreement rate itself deserves. Jay's call on whether a same-capability-class second model gets pursued next, and on wiring Extension 1's flag into a real batch runner.
