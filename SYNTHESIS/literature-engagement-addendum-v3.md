---
synthesis_type: literature_engagement_addendum
addendum_to: [neuro-symbolic-fallacy-screen-v1, structure-layer-mapping-v1, insight-contribution-v1]
trigger: artificial-hivemind-arxiv-2510.22954-2026-08-18
claims_tested: 0
date_executed: "2026-08-18"
status: addendum — core Gateway architecture unchanged; two concrete extensions proposed, neither built yet
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

## Extension 2 — cross-family model diversity for the Gateway's own scoring calls

The paper's inter-model finding (cross-model similarity 71–82%, sometimes exceeding intra-model similarity) raises a question about the Gateway specifically: every live scoring call currently routes to one model family. RKLLama on Board 2 serves Qwen2.5 (7B or 14B) exclusively — same lineage, same training pipeline, regardless of which size runs.

**Real, already-available alternatives exist in this exact project, not hypothetical ones:**

- **Ling** (`inclusionai/ling-2.6-1t`) and **Kimi** (`moonshotai/kimi-k2.6`), both configured in `~/.claude/settings.json` for Claude Code CLI, routed through OpenRouter — not a direct Anthropic API key, so this sits outside the standing rule closing off live runs against Anthropic API directly. Worth Jay's explicit confirmation that this reading of the rule holds, since it's his rule to interpret, not mine to assume past a plain reading.
- **Documented, real divergence on a comparable task already exists.** Session 100 (2026-07-02) ran Opus, Ling, and Kimi independently against the same vault-mapping task and found real behavioral differences: Kimi surfaced three live bugs Opus and Ling both missed; Opus produced the stronger architectural inference from structure alone. Not the Gateway's own task, but a real precedent for cross-family divergence inside this exact system, on file at `in/SYSTEM/vault-maps/run-01-opus-2026-06-05/`, `run-02-ling-2026-07-01/`, `run-03-kimi-2026-07-01/`.
- **Phi-3**, named in an earlier session as one of the model families (alongside Qwen) that converts reliably to `.rkllm` format for local NPU serving. A genuinely different lineage (Microsoft, not Alibaba) running fully local on Board 2 or Board 1, inside the same trust boundary IMST and Doppelganger already operate under. Not installed; would need conversion via Rockchip's toolkit and a serving slot, possibly requiring a model swap given RAM headroom constraints already documented for this board.

**What this buys, concretely:** running the same claim through `fallacy_bounds_screen()` against RKLLama-Qwen and against OpenRouter-Ling or OpenRouter-Kimi, then comparing bounds pairs, tests directly whether the Gateway's own scoring exhibits the same convergent-judgment risk the paper measures across models generally — rather than assuming a single model's score functions as ground truth. Genuine cross-family agreement on a bounds read would carry more weight than any single model's read alone. Genuine cross-family disagreement would itself be a signal worth surfacing — likely warranting `high` review priority regardless of what any individual model's state read says.

**Not proposed:** Opus, Fable, or any other Anthropic-hosted model for this purpose. The standing rule closing off live runs against a real Anthropic API key applies to those regardless of the calibration case made here.

---

## Real-run confirmation (2026-08-18, same day) — topic-dependent and category-dependent hedging, found in the actual data

The full 78-call live run (`run_all_26_rkllama.py`, RKLLama Qwen2.5-14B, three pilot claims) completed the same day this addendum first went up, 0 failures after `strip_markdown_fences()`'s mid-document fix. Real output confirms Extension 1's premise directly and sharpens Extension 2's case beyond what the addendum originally proposed.

**Unknown rate varies nearly 3x by topic, same model, same 26-category screen:** `covid-003` (virology, furin cleavage site) lands unknown on 77% of its 26 calls; `eggs-003` (clinical statistics) on 54%; `blackhole-002` (physics) on 27%. This narrows the addendum's original framing of RKLLama's hedging as a general calibration-width property — that direction holds, but the magnitude depends heavily on subject matter, not just on the model's general tendency to hedge.

**Six categories run unknown on all three claims regardless of topic:** `appeal_to_ignorance`, `double_counting`, `false_equivalence`, `no_true_scotsman`, `part_to_whole_mixup`, `word_shift`. A second, separate mechanism from the topic effect above — something about how these six subconditions get asked produces wide bounds independent of what claim sits underneath them. Full breakdown: `CLAUDE_INDEPENDENT_RUNS/rkllama-78-run-analysis-20260818.md`.

Both findings sharpen Extension 2's test beyond "do different models converge on the same bounds." The real question for a second model (Ling or Kimi via OpenRouter) now has two specific, checkable shapes: does it show the same skew toward `covid-003` specifically, and does it hedge on the same six categories regardless of claim. Agreement or divergence on *which* claims and categories draw uncertainty carries more signal than agreement on raw bounds-pair values alone. Not run yet — Jay's call on timing, same as the rest of Extension 2.

---

## What this document does not do

Rewrite the Gateway's core architecture, take back any prior claim about the four-state bounds design, or assert that "unknown" results are wrong. The paper gives a reason to weight review attention unevenly across states that already exist — not a reason to change what those states mean or how they combine.

Both extensions above stay proposals. Neither has code written yet beyond the `review_priority()` function sketched here. Jay's call on build order and whether the OpenRouter reading needs confirmation before any cross-family call actually fires.
