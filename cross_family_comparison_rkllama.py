#!/usr/bin/env python3
"""
Extension 2 real test -- SYNTHESIS/literature-engagement-addendum-v3.md.
Compares Qwen2.5-14B's already-completed 78-call run
(NEURO_SYMBOLIC_RUNS/all-26-rkllama-progress.json, 78/78 done, 0 failures)
against a fresh 78-call run against Phi-3-mini. Real fix, 2026-08-19: an
earlier version of this script re-ran the Qwen2.5-14B calls from scratch
instead of reusing that completed run -- caught directly, wasted cycles
for no reason. Only Phi-3 gets fresh inference calls now;
seed_from_existing_qwen_run() pulls Qwen's 78 results straight from the
existing file.

Real question this tests, per the addendum: does the Gateway's own
scoring exhibit the same convergent-judgment risk Artificial Hivemind
(arXiv:2510.22954) measures across models generally -- or does a second,
genuinely different lineage (Phi-3, Microsoft) agree or disagree with
Qwen2.5-14B (Alibaba) in a way worth surfacing? Real-run confirmation
(2026-08-18) sharpened this into two specific, checkable shapes:
does Phi-3 show the same skew toward covid-003 specifically, and does
it hedge on the same six categories (appeal_to_ignorance, double_counting,
false_equivalence, no_true_scotsman, part_to_whole_mixup, word_shift)
regardless of claim.

RUN THIS FROM /Users/jaygreathouse/Desktop/flf-epistemic-submission
(needs ingest.py in the same directory, or on sys.path):

    cd ~/Desktop/flf-epistemic-submission
    python3 cross_family_comparison_rkllama.py

Only one real model swap happens (into Phi-3) -- Qwen2.5-14B needs no
swap at all since its results come from the existing file, not a fresh
call. RKLLama's confirmed swap mechanics used directly for Phi-3 (not
imported from moe_router.py -- this vault stays self-contained, matching
every other script here):

    GET  /current_models
    POST /unload_model  {"model_name": "<real current name>"}
    POST /load_model    {"model_name": "<real target name>"}

Output writes to NEURO_SYMBOLIC_RUNS/cross-family-comparison-<timestamp
of first run>.json, saved incrementally after every call (resumable on
rerun -- same pattern as run_all_26_rkllama.py), plus a live summary
table as it runs.
"""

import datetime
import json
import sys
import time
from pathlib import Path

import requests
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from ingest import (
    FALLACY_SHAPE_DATA,
    CIRCULAR_ARGUMENT_PROMPT,
    PILOT_CLAIM_INGESTION_OUTPUTS,
    build_bounds_prompt,
    combine_bounds_and,
    combine_bounds_or,
    bounds_state,
    strip_markdown_fences,
)

RKLLAMA_BASE = "http://172.16.100.11:8080"
RKLLAMA_CHAT_URL = f"{RKLLAMA_BASE}/v1/chat/completions"

# Confirmed real, 2026-08-19 -- in/SYSTEM/moe_router.py's GENERAL_MODEL,
# same string run_all_26_rkllama.py already uses for the original 78-call run.
MODELS = {
    "qwen2.5-14b": "Qwen2.5-14B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0",
    # Confirmed real, 2026-08-19 -- in/SYSTEM/moe_router.py's DIVERSITY_MODEL.
    # Installed via a pre-converted community build (GatekeeperZA on
    # HuggingFace, v1.2.3-matched), not Rockchip toolkit conversion -- no
    # Rockchip toolkit access exists anywhere in this stack.
    "phi-3-mini": "Phi-3-mini-4k-instruct-w8a8",
}

TIMEOUT_SECONDS = 200  # matches run_all_26_rkllama.py's confirmed real
# headroom above its slowest observed clean call (108s), 2026-08-18.
SWAP_TIMEOUT_SECONDS = 180  # cold load of a 7-14B model takes real time,
# matches moe_router.py's confirmed _swap_to() timeout.
MAX_TOKENS = 2000  # raised from 1000, 2026-08-19 -- real cause found for
# the majority of Phi-3's 19 real failures in the first full run: nearly
# every captured raw response cut off mid-word or mid-sentence
# ("attempt to g", "fits as a location s", "before 2:"), not a formatting
# quirk. Phi-3 writes measurably more verbose explanations than Qwen2.5-14B
# did under the identical prompt and hit the old 1000-token ceiling before
# its YAML document closed. Qwen's original 78-call run used the same
# 1000-token cap and hit 0 failures -- this is a real behavioral
# difference between the two model families, not a shared constraint.

OUTPUT_DIR = Path(__file__).parent / "NEURO_SYMBOLIC_RUNS"
FAILED_RAW_DIR = OUTPUT_DIR / "failed_raw"  # real fix, 2026-08-19: the
# YAML-error print below only ever showed the first 500 characters of a
# failed response -- that's a display truncation in this script's own
# print statement, not evidence of where the model's real output actually
# stopped. Several failures got misdiagnosed as model-side truncation
# based on that 500-char preview alone. Every failed call's FULL raw text
# now writes to its own file here, named by call index, so the real
# content is available for honest diagnosis instead of a guessed-at
# snippet.

# The six categories literature-engagement-addendum-v3.md's real-run
# confirmation (2026-08-18) found hedging unknown on all three claims
# regardless of topic, against Qwen2.5-14B alone. This script checks
# whether Phi-3 reproduces the same six or a different set.
KNOWN_HEDGE_CATEGORIES = {
    "appeal_to_ignorance", "double_counting", "false_equivalence",
    "no_true_scotsman", "part_to_whole_mixup", "word_shift",
}


def review_priority(state: str) -> str:
    """Maps a four-state bounds read to a review-priority label, per
    literature-engagement-addendum-v3.md's Extension 1. 'unknown' and
    'contradictory' get 'high' -- Artificial Hivemind (arXiv:2510.22954)
    finds LM judges miscalibrate specifically on contested, non-clear-cut
    cases, which is the same territory these two states describe.
    'known-true' and 'known-false' get 'standard'. Defined locally here
    rather than imported from ingest.py -- Extension 1's code sits in the
    addendum as a proposal, not yet merged into ingest.py itself."""
    return {
        "known-true": "standard",
        "known-false": "standard",
        "unknown": "high",
        "contradictory": "high",
    }[state]


# ---------------------------------------------------------------------------
# SWAP MECHANICS -- same confirmed-working endpoints moe_router.py uses,
# reimplemented locally so this vault's scripts stay self-contained.
# ---------------------------------------------------------------------------

def current_model() -> str | None:
    """Real currently-loaded model name, or None if nothing loaded."""
    resp = requests.get(f"{RKLLAMA_BASE}/current_models", timeout=15)
    resp.raise_for_status()
    data = resp.json()
    for m in data.get("models", []):
        name = m.get("name") or m.get("model")
        if name in MODELS.values():
            return name
    return None


def swap_to(target_model: str) -> None:
    """Unload whichever tracked model is currently loaded (if different
    from target), then load target_model. No-op if already loaded."""
    loaded = current_model()
    if loaded == target_model:
        print(f"  {target_model} already loaded, no swap needed.", file=sys.stderr)
        return

    if loaded is not None:
        print(f"  Unloading {loaded}...", file=sys.stderr)
        resp = requests.post(
            f"{RKLLAMA_BASE}/unload_model",
            json={"model_name": loaded},
            timeout=60,
        )
        resp.raise_for_status()

    print(f"  Loading {target_model}...", file=sys.stderr)
    t0 = time.time()
    resp = requests.post(
        f"{RKLLAMA_BASE}/load_model",
        json={"model_name": target_model},
        timeout=SWAP_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    print(f"  Loaded in {time.time() - t0:.1f}s.", file=sys.stderr)


# ---------------------------------------------------------------------------
# CALL + PARSE -- same contract as run_all_26_rkllama.py's call_rkllama(),
# parameterized by which model string to send.
# ---------------------------------------------------------------------------

def call_model(model_string: str, prompt: str, max_retries: int = 3, fail_tag: str = "unknown") -> dict | None:
    payload = {
        "model": model_string,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.0,
    }

    resp = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(RKLLAMA_CHAT_URL, json=payload, timeout=TIMEOUT_SECONDS)
            break
        except requests.exceptions.RequestException as e:
            print(f"    Network error (attempt {attempt}/{max_retries}): {e}", file=sys.stderr)
            if attempt < max_retries:
                time.sleep(5)
            else:
                print("    Giving up on this call after network retries exhausted.", file=sys.stderr)
                return None

    if not resp.ok:
        print(f"    RKLLama returned {resp.status_code}. Body:", file=sys.stderr)
        print(f"    {resp.text[:1000]}", file=sys.stderr)
        return None
    data = resp.json()
    text = data["choices"][0]["message"]["content"]
    cleaned = strip_markdown_fences(text)
    try:
        parsed = yaml.safe_load(cleaned)
    except yaml.YAMLError as e:
        print(f"    YAML parse error: {e}", file=sys.stderr)
        print(f"    Raw response (first 500 chars, see failed_raw/ for full text): {text[:500]}", file=sys.stderr)
        _save_failed_raw(fail_tag, text, str(e))
        return None
    if not isinstance(parsed, dict):
        print(f"    Parsed but not a dict: {type(parsed).__name__}", file=sys.stderr)
        _save_failed_raw(fail_tag, text, f"parsed to {type(parsed).__name__}, not a dict")
        return None
    return parsed


def _save_failed_raw(fail_tag: str, raw_text: str, error_note: str) -> None:
    """Writes a failed call's FULL raw response to its own file, real fix
    2026-08-19 -- see FAILED_RAW_DIR's comment above for why this exists.
    Never raises on its own failure (a logging problem shouldn't crash a
    real run); prints a warning to stderr instead."""
    try:
        FAILED_RAW_DIR.mkdir(parents=True, exist_ok=True)
        path = FAILED_RAW_DIR / f"{fail_tag}.txt"
        path.write_text(
            f"error: {error_note}\n\n--- full raw response below ---\n\n{raw_text}",
            encoding="utf-8",
        )
    except OSError as e:
        print(f"    (couldn't write full raw response to disk: {e})", file=sys.stderr)


def run_circular_argument(model_string: str, ingestion_output: dict, fail_tag: str = "unknown") -> dict | None:
    prompt = CIRCULAR_ARGUMENT_PROMPT.format(
        original_quote=ingestion_output["original_quote"],
        e_prime_rewrite=ingestion_output["e_prime_rewrite"],
        reference_passage_section="",
    )
    result = call_model(model_string, prompt, fail_tag=fail_tag)
    if result is None:
        return None
    combined = combine_bounds_and(
        result["premise_restated_bounds"], result["no_independent_support_bounds"]
    )
    result["circular_argument_bounds"] = combined
    result["state"] = bounds_state(combined)
    return result


def run_shape_category(model_string: str, category_key: str, ingestion_output: dict, fail_tag: str = "unknown") -> dict | None:
    entry = FALLACY_SHAPE_DATA[category_key]
    prompt = build_bounds_prompt(category_key, ingestion_output)
    result = call_model(model_string, prompt, fail_tag=fail_tag)
    if result is None:
        return None
    subs = entry["subconditions"]
    try:
        if entry["shape"] == "single":
            key = f"{subs[0]['key']}_bounds"
            combined = result[key] if key in result else result[subs[0]["key"]]
        else:
            key_a = f"{subs[0]['key']}_bounds"
            key_b = f"{subs[1]['key']}_bounds"
            # Real fallback, 2026-08-19: Phi-3's first full run dropped the
            # "_bounds" suffix on the first subcondition key twice
            # (texas_sharpshooter, word_shift) while still writing correct,
            # parseable YAML -- a schema deviation, not a syntax error. The
            # bare key ("pattern_found_after_fact" instead of
            # "pattern_found_after_fact_bounds") still carries the real
            # [lower, upper] value, so falling back to it recovers the call
            # instead of discarding real data over a naming slip.
            a = result[key_a] if key_a in result else result[subs[0]["key"]]
            b = result[key_b] if key_b in result else result[subs[1]["key"]]
            combined = combine_bounds_or(a, b) if entry["shape"] == "or" else combine_bounds_and(a, b)
    except KeyError as e:
        print(f"    Schema mismatch: response missing key {e}. Raw parsed response:", file=sys.stderr)
        print(f"    {result}", file=sys.stderr)
        return None
    result[f"{category_key}_bounds"] = combined
    result["state"] = bounds_state(combined)
    return result


def record_result(all_results, model_key, claim_id, category, result, elapsed):
    """Same overwrite-in-place-on-retry pattern as run_all_26_rkllama.py's
    record_result(), keyed on (model_key, claim_id, category) instead of
    just (claim_id, category) -- this run tracks two models' results in
    one file."""
    for i, r in enumerate(all_results):
        if r["model_key"] == model_key and r["claim_id"] == claim_id and r["category"] == category:
            all_results[i] = {
                "model_key": model_key, "claim_id": claim_id, "category": category,
                "result": result, "elapsed_s": elapsed,
            }
            return
    all_results.append({
        "model_key": model_key, "claim_id": claim_id, "category": category,
        "result": result, "elapsed_s": elapsed,
    })


def run_all_checks_for_model(model_key: str, model_string: str, all_results: list, done: set, save_fn) -> None:
    """Runs circular_argument + all 25 shape categories against all three
    pilot claims, for one model. Mirrors run_all_26_rkllama.py's main loop
    exactly, parameterized by model."""
    total_calls_this_model = len(PILOT_CLAIM_INGESTION_OUTPUTS) * 26
    call_num = sum(1 for k in done if k[0] == model_key)

    for claim_id, ingestion_output in PILOT_CLAIM_INGESTION_OUTPUTS.items():
        print(f"\n=== [{model_key}] {claim_id} ===", file=sys.stderr)

        if (model_key, claim_id, "circular_argument") not in done:
            call_num += 1
            print(f"  [{call_num}/{total_calls_this_model}] circular_argument...", file=sys.stderr)
            t0 = time.time()
            result = run_circular_argument(model_string, ingestion_output, fail_tag=f"{model_key}_{claim_id}_circular_argument")
            elapsed = time.time() - t0
            state = result["state"] if result else "CALL_FAILED"
            print(f"    -> {state}  ({elapsed:.1f}s)", file=sys.stderr)
            record_result(all_results, model_key, claim_id, "circular_argument", result, elapsed)
            save_fn()

        for category_key in sorted(FALLACY_SHAPE_DATA.keys()):
            if (model_key, claim_id, category_key) in done:
                continue
            call_num += 1
            print(f"  [{call_num}/{total_calls_this_model}] {category_key}...", file=sys.stderr)
            t0 = time.time()
            result = run_shape_category(model_string, category_key, ingestion_output, fail_tag=f"{model_key}_{claim_id}_{category_key}")
            elapsed = time.time() - t0
            state = result["state"] if result else "CALL_FAILED"
            print(f"    -> {state}  ({elapsed:.1f}s)", file=sys.stderr)
            record_result(all_results, model_key, claim_id, category_key, result, elapsed)
            save_fn()


# ---------------------------------------------------------------------------
# COMPARISON -- the real point of this script, once both models' raw
# results exist. Builds one row per (claim_id, category), reads both
# models' states side by side, flags disagreement, and checks the two
# specific real-run findings the addendum named: does Phi-3 skew toward
# covid-003 the way Qwen2.5-14B did, and does it hedge on the same six
# categories.
# ---------------------------------------------------------------------------

def build_comparison(all_results: list) -> dict:
    by_key = {}
    for r in all_results:
        by_key[(r["model_key"], r["claim_id"], r["category"])] = r

    categories = sorted(FALLACY_SHAPE_DATA.keys()) + ["circular_argument"]
    rows = []
    for claim_id in PILOT_CLAIM_INGESTION_OUTPUTS.keys():
        for category in categories:
            qwen_r = by_key.get(("qwen2.5-14b", claim_id, category))
            phi3_r = by_key.get(("phi-3-mini", claim_id, category))
            qwen_result = qwen_r["result"] if qwen_r else None
            phi3_result = phi3_r["result"] if phi3_r else None

            qwen_state = qwen_result["state"] if qwen_result else "CALL_FAILED"
            phi3_state = phi3_result["state"] if phi3_result else "CALL_FAILED"

            qwen_bounds = qwen_result.get(f"{category}_bounds") if qwen_result else None
            phi3_bounds = phi3_result.get(f"{category}_bounds") if phi3_result else None

            agree = qwen_state == phi3_state
            rows.append({
                "claim_id": claim_id,
                "category": category,
                "qwen_state": qwen_state,
                "qwen_bounds": qwen_bounds,
                "qwen_review_priority": review_priority(qwen_state) if qwen_result else "high",
                "phi3_state": phi3_state,
                "phi3_bounds": phi3_bounds,
                "phi3_review_priority": review_priority(phi3_state) if phi3_result else "high",
                "cross_family_agree": agree,
                "cross_family_disagreement_priority": "high" if not agree else "standard",
                "known_hedge_category": category in KNOWN_HEDGE_CATEGORIES,
            })

    total = len(rows)
    agreements = sum(1 for r in rows if r["cross_family_agree"])

    by_claim = {}
    for claim_id in PILOT_CLAIM_INGESTION_OUTPUTS.keys():
        claim_rows = [r for r in rows if r["claim_id"] == claim_id]
        by_claim[claim_id] = {
            "total": len(claim_rows),
            "agreements": sum(1 for r in claim_rows if r["cross_family_agree"]),
            "phi3_unknown_rate": sum(1 for r in claim_rows if r["phi3_state"] == "unknown") / len(claim_rows) if claim_rows else 0,
            "qwen_unknown_rate": sum(1 for r in claim_rows if r["qwen_state"] == "unknown") / len(claim_rows) if claim_rows else 0,
        }

    hedge_rows = [r for r in rows if r["known_hedge_category"]]
    phi3_reproduces_hedge_set = sum(
        1 for r in hedge_rows if r["phi3_state"] == "unknown"
    ) / len(hedge_rows) if hedge_rows else 0

    disagreement_rows = [r for r in rows if not r["cross_family_agree"]]

    return {
        "generated": datetime.datetime.now().isoformat(),
        "summary": {
            "total_comparisons": total,
            "cross_family_agreements": agreements,
            "cross_family_agreement_rate": agreements / total if total else 0,
            "by_claim": by_claim,
            "known_hedge_categories_checked": sorted(KNOWN_HEDGE_CATEGORIES),
            "phi3_unknown_rate_on_known_hedge_categories": phi3_reproduces_hedge_set,
        },
        "disagreements": disagreement_rows,
        "all_rows": rows,
    }


EXISTING_QWEN_RUN_PATH = OUTPUT_DIR / "all-26-rkllama-progress.json"


def seed_from_existing_qwen_run(all_results: list, done: set) -> None:
    """Real fix, 2026-08-19: this script originally re-ran all 78 calls
    against Qwen2.5-14B from scratch, duplicating a run that already
    completed clean (all-26-rkllama-progress.json, 78/78, 0 failures).
    Jay caught this directly -- real cycles wasted for no reason. Seeds
    all_results from that existing file instead, tagged with
    model_key='qwen2.5-14b', so the swap loop in main() sees Qwen's 78
    calls as already done and skips straight to Phi-3 -- the only model
    that actually needs fresh inference."""
    if not EXISTING_QWEN_RUN_PATH.exists():
        print(
            f"  Warning: {EXISTING_QWEN_RUN_PATH} not found -- Qwen2.5-14B "
            "calls will run fresh instead of reusing the existing run.",
            file=sys.stderr,
        )
        return

    already_seeded = any(r["model_key"] == "qwen2.5-14b" for r in all_results)
    if already_seeded:
        return

    existing = json.loads(EXISTING_QWEN_RUN_PATH.read_text(encoding="utf-8"))
    seeded = 0
    for r in existing:
        record_result(
            all_results, "qwen2.5-14b", r["claim_id"], r["category"],
            r["result"], r.get("elapsed_s", 0),
        )
        if r["result"] is not None:
            done.add(("qwen2.5-14b", r["claim_id"], r["category"]))
        seeded += 1
    print(
        f"  Seeded {seeded} Qwen2.5-14B call(s) from the existing "
        f"{EXISTING_QWEN_RUN_PATH.name} -- no fresh Qwen calls needed.",
        file=sys.stderr,
    )


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    # Fixed filename, not timestamped -- reruns resume from this same file,
    # same convention as run_all_26_rkllama.py.
    raw_path = OUTPUT_DIR / "cross-family-comparison-raw.json"
    comparison_path = OUTPUT_DIR / "cross-family-comparison-report.json"

    all_results = []
    done = set()
    if raw_path.exists():
        try:
            all_results = json.loads(raw_path.read_text(encoding="utf-8"))
            done = {
                (r["model_key"], r["claim_id"], r["category"])
                for r in all_results if r["result"] is not None
            }
            failed_carried = len(all_results) - len(done)
            print(f"Resuming from {raw_path}: {len(done)} call(s) already done, {failed_carried} prior failure(s) will retry.", file=sys.stderr)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Existing progress file unreadable ({e}) -- starting fresh.", file=sys.stderr)
            all_results = []
            done = set()

    def save():
        raw_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")

    seed_from_existing_qwen_run(all_results, done)
    save()

    for model_key, model_string in MODELS.items():
        remaining = [
            1 for claim_id in PILOT_CLAIM_INGESTION_OUTPUTS
            for category in list(FALLACY_SHAPE_DATA.keys()) + ["circular_argument"]
            if (model_key, claim_id, category) not in done
        ]
        if not remaining:
            print(f"\n{model_key}: all calls already done, skipping swap.", file=sys.stderr)
            continue

        print(f"\n### Swapping to {model_key} ({model_string}) ###", file=sys.stderr)
        swap_to(model_string)
        run_all_checks_for_model(model_key, model_string, all_results, done, save)
        done = {
            (r["model_key"], r["claim_id"], r["category"])
            for r in all_results if r["result"] is not None
        }

    failed = [r for r in all_results if r["result"] is None]
    print(f"\n--- Raw calls done: {len(all_results)}, {len(failed)} failed ---", file=sys.stderr)
    if failed:
        for f in failed:
            print(f"  FAILED: {f['model_key']} / {f['claim_id']} / {f['category']}", file=sys.stderr)
        print("  Rerun this script to retry only the failed/missing calls.", file=sys.stderr)

    print("\nBuilding comparison report...", file=sys.stderr)
    comparison = build_comparison(all_results)
    comparison_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")

    s = comparison["summary"]
    print(f"\n=== CROSS-FAMILY COMPARISON SUMMARY ===", file=sys.stderr)
    print(f"Total comparisons: {s['total_comparisons']}", file=sys.stderr)
    print(f"Agreement rate: {s['cross_family_agreement_rate']:.1%}", file=sys.stderr)
    for claim_id, stats in s["by_claim"].items():
        print(f"  {claim_id}: {stats['agreements']}/{stats['total']} agree, "
              f"Qwen unknown {stats['qwen_unknown_rate']:.0%}, "
              f"Phi-3 unknown {stats['phi3_unknown_rate']:.0%}", file=sys.stderr)
    print(f"Phi-3 unknown rate on the six known-hedge categories: "
          f"{s['phi3_unknown_rate_on_known_hedge_categories']:.0%}", file=sys.stderr)
    print(f"\nRaw results: {raw_path}", file=sys.stderr)
    print(f"Comparison report: {comparison_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
