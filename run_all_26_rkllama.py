#!/usr/bin/env python3
"""
Run all 26 fallacy categories against RKLLama on Board 2 -- live, real
model calls, against every claim this project actually has an Ingestion
Layer output for. Uses RKLLama (Qwen2.5-14B, port 8080), NOT the Anthropic
API -- this is the path already open per standing project rules.

RUN THIS FROM /Users/jaygreathouse/Desktop/flf-epistemic-submission
(needs ingest.py in the same directory, or on sys.path):

    cd ~/Desktop/flf-epistemic-submission
    python3 run_all_26_rkllama.py

Before running, confirm RKLLama is loaded with the 14B model (service
restart needed when switching model sizes -- standing rule):

    ssh control@172.16.100.11 "systemctl status rkllama"

If it's not serving 14B, restart it first:

    ssh control@172.16.100.11 "systemctl restart rkllama"

Output writes to NEURO_SYMBOLIC_RUNS/all-26-rkllama-<timestamp>.json
and prints a live summary table as it runs.
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
    review_priority,
    strip_markdown_fences,
)

RKLLAMA_URL = "http://172.16.100.11:8080/v1/chat/completions"
RKLLAMA_MODEL = "Qwen2.5-14B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0"  # confirmed via GET /v1/models, 2026-08-17
TIMEOUT_SECONDS = 200  # raised from 120, 2026-08-18 -- appeal_to_ignorance/covid-003
# needed 365s across two dead 120s waits before a real response landed on
# attempt 3; RKLLama itself confirmed alive and responsive throughout via
# systemctl log, not hung. 200s gives real headroom above the slowest clean
# call observed tonight (108s) without matching this run's proven worst case.

OUTPUT_DIR = Path(__file__).parent / "NEURO_SYMBOLIC_RUNS"


def call_rkllama(prompt: str, max_retries: int = 3) -> dict:
    """Same contract as ingest.py's _call_model() -- takes a prompt, returns
    a parsed dict. Hits RKLLama's OpenAI-compatible chat completions
    endpoint on Board 2 instead of the Anthropic API.

    Retries on network-level failures (dropped connection, timeout) up to
    max_retries times with a short backoff -- a network blip no longer
    kills the whole run. Still returns None (not a crash) if every retry
    fails, or if RKLLama itself returns a non-2xx or unparseable response --
    the caller logs that as CALL_FAILED and the run continues to the next
    category instead of dying."""
    payload = {
        "model": RKLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": 0.0,
    }

    resp = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(RKLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
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
        print(f"    Raw response: {text[:500]}", file=sys.stderr)
        return None
    if not isinstance(parsed, dict):
        print(f"    Parsed but not a dict: {type(parsed).__name__}", file=sys.stderr)
        return None
    return parsed


def run_circular_argument(claim_id: str, ingestion_output: dict) -> dict:
    prompt = CIRCULAR_ARGUMENT_PROMPT.format(
        original_quote=ingestion_output["original_quote"],
        e_prime_rewrite=ingestion_output["e_prime_rewrite"],
        reference_passage_section="",
    )
    result = call_rkllama(prompt)
    if result is None:
        return None
    combined = combine_bounds_and(
        result["premise_restated_bounds"], result["no_independent_support_bounds"]
    )
    result["circular_argument_bounds"] = combined
    result["state"] = bounds_state(combined)
    result["review_priority"] = review_priority(result["state"])
    return result


def run_shape_category(category_key: str, claim_id: str, ingestion_output: dict) -> dict:
    entry = FALLACY_SHAPE_DATA[category_key]
    prompt = build_bounds_prompt(category_key, ingestion_output)
    result = call_rkllama(prompt)
    if result is None:
        return None
    subs = entry["subconditions"]
    try:
        if entry["shape"] == "single":
            combined = result[f"{subs[0]['key']}_bounds"]
        else:
            a = result[f"{subs[0]['key']}_bounds"]
            b = result[f"{subs[1]['key']}_bounds"]
            combined = combine_bounds_or(a, b) if entry["shape"] == "or" else combine_bounds_and(a, b)
    except KeyError as e:
        print(f"    Schema mismatch: RKLLama response missing key {e}. Raw parsed response:", file=sys.stderr)
        print(f"    {result}", file=sys.stderr)
        return None
    result[f"{category_key}_bounds"] = combined
    result["state"] = bounds_state(combined)
    result["review_priority"] = review_priority(result["state"])
    return result


def record_result(all_results, claim_id, category, result, elapsed):
    """Write one call's result into all_results. Overwrites an existing
    CALL_FAILED entry for this (claim_id, category) pair in place on a
    retry, rather than appending a second row for the same pair --
    all_results stays one entry per (claim_id, category) always, matching
    the file's own stated intent (reruns resume from this same file).
    Appends fresh only when no prior entry exists for this pair at all."""
    for i, r in enumerate(all_results):
        if r["claim_id"] == claim_id and r["category"] == category:
            all_results[i] = {"claim_id": claim_id, "category": category, "result": result, "elapsed_s": elapsed}
            return
    all_results.append({"claim_id": claim_id, "category": category, "result": result, "elapsed_s": elapsed})


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    # Fixed filename, not timestamped -- reruns resume from this same file
    # instead of starting a fresh timestamped one every time. Rename it
    # yourself once the run finishes if you want it archived under a
    # timestamp.
    output_path = OUTPUT_DIR / "all-26-rkllama-progress.json"

    all_results = []
    done = set()
    if output_path.exists():
        try:
            all_results = json.loads(output_path.read_text(encoding="utf-8"))
            # Only a real, non-None result counts as done -- a prior CALL_FAILED
            # entry (result is None) stays in all_results for the historical
            # record but must not block a retry on rerun. Real bug found and
            # fixed 2026-08-18: the old version built `done` from every entry
            # regardless of result, so a failed call locked in as permanently
            # skipped despite the end-of-run message telling you rerun would
            # retry it.
            done = {(r["claim_id"], r["category"]) for r in all_results if r["result"] is not None}
            failed_carried = len(all_results) - len(done)
            print(f"Resuming from {output_path}: {len(done)} call(s) already done, {failed_carried} prior failure(s) will retry.", file=sys.stderr)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Existing progress file unreadable ({e}) -- starting fresh.", file=sys.stderr)
            all_results = []
            done = set()

    def save():
        output_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")

    total_calls = len(PILOT_CLAIM_INGESTION_OUTPUTS) * 26
    call_num = len(done)

    for claim_id, ingestion_output in PILOT_CLAIM_INGESTION_OUTPUTS.items():
        print(f"\n=== {claim_id} ===", file=sys.stderr)

        if (claim_id, "circular_argument") not in done:
            call_num += 1
            print(f"  [{call_num}/{total_calls}] circular_argument...", file=sys.stderr)
            t0 = time.time()
            result = run_circular_argument(claim_id, ingestion_output)
            elapsed = time.time() - t0
            state = result["state"] if result else "CALL_FAILED"
            print(f"    -> {state}  ({elapsed:.1f}s)", file=sys.stderr)
            record_result(all_results, claim_id, "circular_argument", result, elapsed)
            save()

        for category_key in sorted(FALLACY_SHAPE_DATA.keys()):
            if (claim_id, category_key) in done:
                continue
            call_num += 1
            print(f"  [{call_num}/{total_calls}] {category_key}...", file=sys.stderr)
            t0 = time.time()
            result = run_shape_category(category_key, claim_id, ingestion_output)
            elapsed = time.time() - t0
            state = result["state"] if result else "CALL_FAILED"
            print(f"    -> {state}  ({elapsed:.1f}s)", file=sys.stderr)
            record_result(all_results, claim_id, category_key, result, elapsed)
            save()

    failed = [r for r in all_results if r["result"] is None]

    # PRIORITY REVIEW QUEUE -- Extension 1, SYNTHESIS/literature-engagement-
    # addendum-v3.md. Groups every high-review_priority result by claim,
    # printed before the plain done/failed summary so a human's attention
    # lands first where the Artificial Hivemind paper's own data says a
    # model judge is least trustworthy (unknown/contradictory states) --
    # not spread evenly across all 26 categories regardless of state.
    high_priority = [
        r for r in all_results
        if r["result"] is not None and r["result"].get("review_priority") == "high"
    ]
    print(f"\n=== PRIORITY REVIEW QUEUE: {len(high_priority)} high-priority result(s) ===", file=sys.stderr)
    if high_priority:
        by_claim = {}
        for r in high_priority:
            by_claim.setdefault(r["claim_id"], []).append(r)
        for claim_id in sorted(by_claim):
            print(f"  {claim_id}:", file=sys.stderr)
            for r in by_claim[claim_id]:
                print(f"    {r['category']:28s} {r['result']['state']}", file=sys.stderr)
    else:
        print("  none -- every scored result landed known-true or known-false.", file=sys.stderr)

    queue_path = output_path.with_name(output_path.stem + "-priority-queue.json")
    queue_path.write_text(
        json.dumps(
            [
                {"claim_id": r["claim_id"], "category": r["category"], "state": r["result"]["state"]}
                for r in high_priority
            ],
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\n--- Done: {len(all_results)} calls, {len(failed)} failed ---", file=sys.stderr)
    if failed:
        for f in failed:
            print(f"  FAILED: {f['claim_id']} / {f['category']}", file=sys.stderr)
        print("  Rerun this script to retry only the failed/missing calls -- already-done calls are skipped.", file=sys.stderr)
    print(f"\nWritten to: {output_path}", file=sys.stderr)
    print(f"Priority review queue written to: {queue_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
