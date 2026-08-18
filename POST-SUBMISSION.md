---
title: Post-Submission
type: reference
status: active
vault: TRC
date: 2026-08-17
tags: [resilience]
---

# Post-Submission: From Closed Entry to Working Gateway

This page picks up exactly where the FLF competition entry left off — July 19, 2026, submitted and frozen — and tells the story of everything built after, in one sitting. For the full dated, bug-by-bug technical record, see [`DEVELOPMENT.md`](DEVELOPMENT.md). This page stays readable.

---

## Why this work exists at all

FLF's ruling on the submission itself stood simple: complete, judged, closed. Nothing about it stayed open as a task. But the underlying question the submission raised — can a system check what a claim rests on, not just rewrite it — never got answered by the competition's own scope. The submission tested one mechanical rule (E-Prime) against three fixed case studies. It never tested whether the same discipline could evaluate a claim it had never seen before, without a human reading every output, and without ever trusting a model's *memory* of a source over the source itself.

That gap reopened as new engineering work on August 11, 2026 — deliberately scoped apart from the closed competition entry, under its own goal: build toward something that could genuinely generalize.

## The constraint that shaped everything: no cloud API

One ruling governs every line of code built after the submission closed: nothing in this codebase calls the Anthropic API, ever, for any reason. Local inference on dedicated hardware (an RKLLama server running Qwen2.5, 7B and 14B variants) stays the only path. This never functioned as a cost-saving afterthought — it stood as the design constraint from day one of the new work, and it shaped every choice that followed: no per-call cost at scale, no data leaving the machine, and a real test of whether a smaller, self-hosted model could do this work at all.

Real infrastructure existed already, undiscovered until the reopening session — an RKLLama service had run quietly on the hardware for three weeks before anyone found it.

## The first real problem: the model couldn't quote itself accurately

The earliest version of the local pipeline asked the model to reproduce a source quote verbatim in its own output — a field called `original_quote`, whose entire contract forbade rewriting. It failed. Not dramatically — a comma here, a "that" silently corrected to "which" there — but *systematically*, roughly one record in five across full runs, once someone actually checked instead of trusting the field name.

Two rounds of prompt engineering tried to fix this by naming the failure mode directly: don't correct grammar, don't fix punctuation, copy character-for-character. Both held briefly, then failed on rerun — one case, a real grammatical irregularity in a primary source, survived four separate correction attempts in a row.

The fix that actually worked stopped trying to make the model behave, and instead removed the operation that kept failing. The real source text already sat in memory, pulled directly from the claim file, before any model call ran. Once the model's response passed its own shape checks — real signal it attempted the task correctly — its `original_quote` field got overwritten with the actual known-good text. The model never needed to reproduce anything verbatim at all. Confirmed clean: 3 for 3, zero drift, including the case that broke every prior attempt.

This became the template for every fix that followed: don't ask a probabilistic system to reliably do something a deterministic operation can do instead.

## Extending the reasoning, not just the rewrite

A separate track of work, running in parallel, built a genuinely new capability rather than fixing an existing one: bounds-pair reasoning instead of flat yes/no fallacy detection. Where the original submission's fallacy screen returned a single verdict, the new neuro-symbolic layer scores each subcondition of a fallacy on a `[lower, upper]` truth interval — known-true, known-false, unknown, or contradictory — and combines subconditions using documented logical rules (AND for "both must hold," OR for "either suffices").

This started as a pilot against three claims already tested by hand. Extending it to the full twelve-claim set surfaced a real, checkable pattern worth naming honestly: several claims scored bounds that matched, to the decimal, the example numbers written directly into the prompt's own instructions — not because those claims genuinely warranted maximal uncertainty, but because the model appeared to anchor on the example rather than reason independently. Caught by checking the model's own stated explanation against the score, not by trusting a clean-looking result. Fixed by removing every literal example number from every bounds-scoring prompt in the codebase — four separate functions, one shared root cause.

A second, narrower finding came from the same full-set run: two claims — bare single-clause statistical statements with no separate premise and conclusion — scored a confident false positive on circular-argument detection. The model's own evidence for the score, read directly, showed it comparing the source quote against its own E-Prime rewrite (expected to closely match, by design) and mistaking that expected similarity for internal circularity. A category mismatch, not a real finding. Excluded from that specific check, explicitly, with the reasoning kept visible rather than the failure hidden.

## The third layer: Structure, made real

FLF's own framework names three pipeline stages: Ingestion, Structure, Assessment. The submission formalized two of them in code. Structure existed only as a real, hand-checked relationship graph — twenty-one within-case pairs, all twelve claims, a closed four-tag vocabulary (`supports`, `argues_against`, `combines_with`, `shares_open_question_with`) — built during the submission itself, but never connected to anything that computed with it.

Closing that gap meant answering a real design question first: what does each relationship type actually *do* to a claim's reliability? The answer came from reasoning about each tag's own definition, not from a default. Corroborating evidence should pull confidence toward the stronger source, which argues for combining bounds under OR rather than AND — the more common default, but the wrong one here, since AND dilutes toward the weaker input instead of strengthening toward the better one. Contesting evidence works the same way, inverted. Genuinely joint evidence — two components of one single combined calculation, not two claims that happen to agree — combines under AND, since both halves must hold together for the joint verdict to mean anything.

The seeds feeding that graph come from two honestly distinct sources. Ten of twelve claims draw from the neuro-symbolic circular-argument bounds, inverted (absence of a fallacy converted into a reliability signal) — a real but partial proxy, reflecting only one fallacy category out of twenty-six tracked, not general evidentiary strength. The two excluded claims draw instead from the Assessment Layer's own self-reported confidence score, a materially weaker and differently-scoped signal, labeled as such in every output record rather than blended in silently.

## Where this stands

All three of FLF's named layers now exist as working, computed code — not two formalized and one merely proposed, as the submission itself left it. The gateway takes an arbitrary claim, guarantees its source quote never drifts, screens it for specific reasoning failures without anchoring on its own examples, and propagates the result through a real relationship graph toward every connected claim — entirely on local hardware, no cloud dependency, every limitation named in the same place as the result it qualifies.

What hasn't happened yet, stated plainly rather than implied away: the bounds-propagation formulas above reflect one reasoned pass, not an empirically validated one — nothing has checked whether OR-combining supports against known ground truth actually produces better-calibrated confidence than the alternative. The neuro-symbolic bounds pass covers one fallacy category (circular argument) of twenty-six the original submission's fallacy screen tracks; extending coverage to the rest stands as real, undone work, not a hidden gap. And propagation runs single-pass over the edge list as written, not iterated to a fixed point — a real simplification, not a proven-irrelevant one.
