---
title: Development Log
type: reference
status: active
vault: TRC
date: 2026-08-17
tags: [resilience]
---

# Development Log — Post-Submission Technical Record

Chronological, dated, real. Every entry below traces to an actual session, an actual bug, or an actual ruling — nothing summarized away or smoothed over. For the readable version of this same history, see [`POST-SUBMISSION.md`](POST-SUBMISSION.md).

---

## 2026-08-11 — Reopened; neuro-symbolic toolkit built

The 2026-07-17 zero-mention rule (governing session reporting on the closed competition entry) got scoped correctly: it covers the frozen submission itself, not new engineering work directed at the same repo under a separate goal. That distinction, drawn explicitly this session, is what allows this entire document to exist.

Five new files landed in `SYNTHESIS/`, plus a first version of bounds-pair scoring in `ingest.py`:

- `circular_argument_screen()` — pilot function, one fallacy category (circular argument), bounds-pair scoring instead of flat yes/no. Two subconditions (`premise_restated`, `no_independent_support`), each a `[lower, upper]` interval, combined under a documented Gödel/min-based AND rule — not IBM's LNN library, a plain simplification, stated as such.
- `combine_bounds_and()`, `combine_bounds_or()`, `bounds_state()` — the shared bounds-combination primitives every later function reuses unmodified.
- Tested against three claims already covered by hand (`eggs-003`, `covid-003`, `blackhole-002`) via `--circular-pilot`. Verified with `ast.parse()` and mocked model calls — no live API call ran against any of it, per the standing no-Anthropic-API rule already in force.

## 2026-08-12 — Local corpus builder; first real model-output failures

`build_local_corpus.py` built to drive `ingest.py`'s real Ingestion/Assessment templates against a local RKLLama model instead of the Anthropic API — first-ever local-inference path for this codebase.

Real failures found and fixed, same session:
- The 1.7B model (`Qwen3-1.7B`) reversed a source's stated causal direction and invented a statistic absent from the source, on its first, unfixed run. `ANTI_FABRICATION_SUFFIX` added, local to `build_local_corpus.py` only — `ingest.py`'s own `INGESTION_PROMPT` stays untouched.
- Full 8-claim run against the 7B model: 6/8 initial errors, all in the Assessment Layer — the model echoing the prompt's own input block back after its real answer (breaks YAML every time), and wrapping phrases in markdown bold (YAML reads `**` as an alias reference, not literal text). Fixed via `ASSESSMENT_FORMAT_SUFFIX` plus defensive `strip_echoed_input()`/`strip_markdown_bold()` backstops that run regardless of whether the suffix instruction holds.
- A third case found same session: valid YAML with every field null — a parse success that isn't a real answer.
- `blackhole-001` twice produced malformed Ingestion Layer output — nested dicts instead of scalar strings, once a corrupted key name (`ororiginal_quote`). Not root-caused this session; flagged to watch.

**Decision, same session:** the 7B model stands as the corpus-building model. The 1.7B model stays useful for fast exact-match sanity checks, not corpus content — it never went clean on fabrication across either test run.

## 2026-08-13 — Generic regex fallback; shape-retry loop; full 12-claim run; quote-fidelity gap (partial)

Four distinct YAML-parsing collisions had surfaced across three full-batch runs by this point (prompt-echo, markdown-bold-as-alias, valid-but-null, document markers) — each fixed individually, each fix improving the clean-run rate (2/8 → 6/8 → 7/8), but each run surfacing a new quirk. **Ruling: stop chasing individual bugs.** `extract_fields_via_regex()` built as a generic fallback — locates each expected field by name directly in raw text, sidestepping YAML's strict syntax entirely rather than out-guessing the model's next formatting failure.

Two further, genuinely reproducible misshapes found, neither caught by the regex fallback (which only triggers on parse *failure* — both of these parse successfully, into the wrong type):
- `blackhole-001`'s colon-collision: a scalar field containing an unescaped colon parses as a single-key mapping instead of a string. Reproduced 3/3 independent generations. Fixed via `repair_split_scalars()`.
- List-bulleting: the model sometimes writes an answer as a real YAML list instead of one text block, in three sub-shapes (plain strings, single-key dicts, an int wrapped in a one-item list). Fixed via `repair_list_wrapped_scalars()` and a widened `normalize_record_fields()`.

**Ruling, Jay's call: regenerate on shape mismatch, capped at 2 extra attempts.** `call_with_shape_retry()` built; `find_malformed_fields()` extended to check both scalar and int field types after `eggs-002`'s `confidence_assessment` came back as a real integer followed by ~400 repeated garbage tokens — parseable, wrong.

**Full 12-claim run, later same session: 12/12 records structurally clean**, read directly from the JSONL, not the console line. 4/12 correctly flagged `e_prime_compliant: false` — real to-be-form survivals, `verify_corpus.py`'s logic working as intended, not a defect.

**Real gap found, not fixed this session:** neither `check_e_prime_compliance()` nor `check_fabricated_numbers()` ever tested whether `original_quote` itself stayed verbatim against `source_quote` — both test the rewrite field only. First concrete instance: the model's own `original_quote` silently returned "correlates to" where the source read "corresponds to." Named honestly as an unaddressed gap, not fixed yet.

Separately: `circular_argument_screen()`/`fallacy_bounds_screen()` never had a local-inference path — both hardcoded to `_call_model()`, the Anthropic API function. `run_local_neuro_symbolic.py` built to close this, reusing `ingest.py`'s real prompts and `build_local_corpus.py`'s proven `call_local_model()` unmodified. First confirmed live use, no `ANTHROPIC_API_KEY` anywhere in the path, against a real Deruelle 2024 paper (arbitrary new input, not one of the three hardcoded pilot claims).

**Real limitation found, not fixed:** every neuro-symbolic function took exactly one quote/rewrite pair — no way to test whether a claim's conclusion restates a premise stated *elsewhere* in the same source document. `build_reference_passage_section()` built same session as the mechanism to close this (optional second passage, forwarded to the relevant prompts) — the gap itself stayed real until this addition.

`fallacy_bounds_screen()` generalized from the circular-argument-only pilot to 24 of the remaining 25 categories via `FALLACY_SHAPE_DATA` (AND/OR/single-subcondition shapes classified per category). `double-counting`, the 26th category (from evidence-reasoning tradition, not classical fallacy tradition), doesn't decompose the same way — left unbuilt, named honestly.

Two vault copies of the same project (`flf-vault/` and canonical `flf-epistemic-submission/`) consolidated into the canonical path same session — `build_local_corpus.py`, `verify_corpus.py`, `CORPUS/` moved; `requirements.txt` merged. Discovery made during the move: canonical's `CLAIMS/` held 12 claims, flf-vault's stale snapshot held only 8 — four claims (`covid-004/005/006`, `blackhole-003`) never made it into the older copy.

## 2026-08-14 — 14B model pull; capacity-scaling test

Real infrastructure discovery: RKLLama had run as an active systemd service for three weeks, undiscovered, with an empty `models/` directory until this track of work started using it.

14B pull: first attempt ran foreground in an interactive SSH session instead of the standing backgrounded pattern, dropped at 77% via broken pipe — no partial-resume in RKLLama's `/pull` handler, forced a full restart. Retry launched correctly via `setsid nohup ... & disown`, confirmed via a fresh-session `pgrep`.

Real cross-passage circular-argument test: same input run against both 7B and 14B. 14B's explanation directly engaged the reference passage's own language; 7B's didn't. The circular-argument score itself stayed inconclusive on both (bounds `[0.3, 0.7]`, state unknown) — the capacity difference showed in reasoning quality, not in the final score. **Ruling: one run counts as sufficient evidence, log and close.**

## 2026-08-15/16 — Quote-fidelity gap closed structurally; RKLLama operational fix

Started from one flagged case (`"corresponds to"` → `"correlates to"`). `check_quote_fidelity()` built and wired into both `build_local_corpus.py` (live path) and `verify_corpus.py` (retroactive path).

**Retroactive scan against every existing CORPUS file found the gap far more pervasive than the single known case** — drift recurring in roughly 1 of 5 records across every full 12-claim run. Three-tiered classification built to separate signal from noise: case-only drift (a sentence-boundary lowercasing habit), punctuation-only drift (a dropped comma, `"..."` → `";"`), and substantive word drift (real content change).

One deterministic pattern root-caused: `blackhole-003`'s `"that"` → `"which"` swap, present in 4/4 full runs, traced to a genuine minor grammar irregularity in the primary source itself (a non-restrictive clause using "that" after a comma — formal style calls for "which," and the model kept "fixing" it). `VERBATIM_ENFORCEMENT_SUFFIX` tried first — a targeted prompt addition naming the exact failure. **Confirmed NOT to hold on a real rerun**, same drift, same case, post-suffix.

**Real fix, structural rather than requested:** `process_claim()` in `build_local_corpus.py` now overwrites `ingestion_result["original_quote"]` with the already-verified `source_quote` directly, once the model's response clears its shape checks. The model never needed to reproduce source text character-for-character — that operation was the actual failure mode, independent of prompt wording, model size, or the next formatting quirk. Confirmed on a real 14B rerun (first-ever use of `build_local_corpus.py` against 14B): 3/3 verbatim, zero drift of any tier, including `blackhole-003`.

Separate, unrelated finding same session: RKLLama on Board 2 doesn't release its NPU allocation between requests. A model-size swap needs `systemctl restart rkllama` first — confirmed as a new standing rule.

## 2026-08-17 — Full session: batch bounds extension, anchoring bug found and fixed, Structure Layer built

**Batch extension to all 12 claims.** `run_local_neuro_symbolic_batch.py` built — extends `circular_argument_screen` from its original 3-claim pilot coverage to all 12, sourcing `original_quote` fresh from `CLAIMS/*.md` directly (bypassing the fidelity question entirely) and `e_prime_rewrite` from the existing 2026-08-13 full-coverage corpus run. No Ingestion Layer model calls. First run: 7 of 12 claims scored the combined bounds pair `[0.3, 0.7]` — 5 with both subconditions landing on that exact value.

**Anchoring bug found and fixed.** That number is the literal example given in `CIRCULAR_ARGUMENT_PROMPT`'s own instruction text ("genuine uncertainty gets wide bounds, for example [0.3, 0.7]"). Explanation text for the affected claims confirmed it directly — the model stated its own uncertainty, then returned the textbook number rather than an independently-reasoned interval. Fixed by removing the literal example from all four bounds-scoring prompt sites in `ingest.py` (`CIRCULAR_ARGUMENT_PROMPT`, `build_bounds_prompt()`, `build_licensing_prompt()`, `build_construction_prompt()`) — replaced with an instruction to reason to an independent interval rather than default to any standard range. Verified via `ast.parse()` on the live-edited file; zero occurrences of the literal example remained after the fix.

**Rerun, post-fix: real spread, no repeated defaults.** 8 states now varied meaningfully (`known-true`, `known-false`, `unknown` at genuinely different bounds) — but a new, different problem surfaced: `eggs-001` and `eggs-002` both scored `known-true` `[0.8, 1.0]` on circular argument.

**Category-mismatch false positive found and fixed.** Both claims are bare single-clause statistical statements with no separate premise and conclusion for circularity to consist of. `eggs-002`'s own `premise_restated_location` field quoted the same sentence twice — once from `original_quote`, once from `e_prime_rewrite` — as its own evidence, revealing the actual mechanism: the model compared the Ingestion Layer's rewrite against its source (expected to closely match, by design) and mistook that expected similarity for internal restatement. `CIRCULAR_SCREEN_OUT_OF_SCOPE` added to the batch script, documented inline, skipping both claims on any future run rather than re-scoring them. The existing run's output file annotated in place (`in_scope: false` plus the full reasoning) rather than silently rescored or deleted — the false-positive scores stay visible for audit.

**Structure Layer formalized.** `structure_layer.py` built — parses the real edge graph directly out of `SYNTHESIS/structure-layer-worked-example-v1.md`'s own YAML block (no re-typing it, so graph and documentation can't silently drift apart), seeds each claim's reliability bounds from two honestly distinct sources (10 claims: inverted `circular_argument_bounds`, a partial one-fallacy-category proxy; 2 excluded claims: `confidence_assessment`, a materially weaker and differently-scoped proxy, labeled as such), and propagates seeds through the graph's four typed relations using reasoned, non-default formulas — OR-combine for `supports`/`argues_against` (corroboration should pull toward the stronger source, not dilute toward the weaker one, which AND would do), AND-combine for `combines_with` (genuinely joint evidence, both components must hold together), explicit no-op for `shares_open_question_with`.

Tested against a full local mirror of real data before ever running on the actual machine — output verified by hand against the propagation math (`covid-001`'s two `supports` edges, the `combines_with` joint pair) before pushing. One cosmetic float-precision bug found and fixed in the same pass (`invert_bounds()` rounding). Confirmed identical output on the real machine after the fix.

**Repository renamed:** `flf-epistemic-submission` → `bounded-epistemic-gateway`, GitHub-side rename plus local `git remote set-url`, both run by Jay per standing practice (git commands stay his). `README.md` restructured around a two-tier framing (frozen competition entry, preserved verbatim below a clear boundary; active gateway work above it) — this document and `POST-SUBMISSION.md` written same session to give that framing real, dated content underneath it.
