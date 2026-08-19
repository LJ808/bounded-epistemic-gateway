#!/usr/bin/env python3
"""
Run all 26 fallacy categories against RKLLama on Board 2 -- live, real model
calls -- against the six claims decomposed from Artificial Hivemind
(arXiv:2510.22954), the same way run_all_26_rkllama.py already does for the
three original pilot claims (eggs-003, covid-003, blackhole-002).

Uses RKLLama (Qwen2.5-14B, port 8080), NOT the Anthropic API -- same standing
rule, same path.

RUN THIS FROM /Users/jaygreathouse/Desktop/flf-epistemic-submission
(needs ingest.py in the same directory, or on sys.path):

    cd ~/Desktop/flf-epistemic-submission
    python3 run_hivemind_claims_rkllama.py

Before running, confirm RKLLama is loaded with the 14B model (service
restart needed when switching model sizes -- standing rule):

    ssh control@172.16.100.11 "systemctl status rkllama"

Output writes to NEURO_SYMBOLIC_RUNS/hivemind-26-rkllama-<timestamp>.json,
resumable exactly like run_all_26_rkllama.py -- rerun to retry only
failed/missing calls, already-done calls skipped.

Verbatim-quote note: every original_quote field below is a PARAPHRASE, not
verbatim text pulled from the paper -- reproducing extended verbatim text
from a copyrighted NeurIPS paper sits outside what Claude's responses can do.
Pulled directly from CLAUDE_INDEPENDENT_RUNS/artificial-hivemind-decomp-
claude-eval-20260818.json, same paraphrase already used for the reasoning-
based screen, not re-derived here.

review_priority() applied automatically to every result and surfaced in a
PRIORITY REVIEW QUEUE block at the end -- per literature-engagement-
addendum-v3.md Extension 1, baked into the runner this time rather than
applied as a separate post-processing pass.
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
    build_bounds_prompt,
    combine_bounds_and,
    combine_bounds_or,
    bounds_state,
    strip_markdown_fences,
)

RKLLAMA_URL = "http://172.16.100.11:8080/v1/chat/completions"
RKLLAMA_MODEL = "Qwen2.5-14B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0"  # confirmed via GET /v1/models, 2026-08-17
TIMEOUT_SECONDS = 200  # matches run_all_26_rkllama.py's tuned value

OUTPUT_DIR = Path(__file__).parent / "NEURO_SYMBOLIC_RUNS"

# Six claims decomposed from Artificial Hivemind (arXiv:2510.22954),
# 2026-08-18. Every original_quote is a PARAPHRASE -- see module docstring.
HIVEMIND_CLAIM_INGESTION_OUTPUTS = {
    "hivemind-A-intra-model-repetition": {
        "original_quote": "[paraphrase] Sampling the same model 50 times per query under high-temperature top-p decoding still produces responses whose pairwise embedding similarity exceeds 0.8 in most cases (79%).",
        "e_prime_rewrite": "Intra-model response similarity exceeds 0.8 for 79% of queries under top-p=0.9, temperature=1.0, across 25 models sampled 50x each on 100 queries.",
    },
    "hivemind-B-inter-model-homogeneity": {
        "original_quote": "[paraphrase] Different models across families and sizes produce responses to the same query with pairwise similarity from 71% to 82%, and the top-50 most similar responses to a query typically draw from about 8 distinct models rather than concentrating in one.",
        "e_prime_rewrite": "Cross-model response similarity spans 71-82% pairwise, with an average of ~8 unique contributing models per top-50 similarity cluster across 25 models.",
    },
    "hivemind-C-similar-quality-miscalibration": {
        "original_quote": "[paraphrase] LM perplexity scores, reward-model outputs, and LM-judge ratings correlate with human ratings less well specifically on response pairs where humans rate quality as comparably good, versus the full dataset.",
        "e_prime_rewrite": "Spearman/Pearson correlation with human ratings drops on similar-quality response subsets (Tukey's-fences filtered, k=0.5-3.0) relative to the unfiltered set, for both absolute and pairwise rating setups.",
    },
    "hivemind-D-disagreement-miscalibration": {
        "original_quote": "[paraphrase] The same three scoring methods correlate with human ratings less well specifically on response pairs where human annotators disagree most (highest Shannon entropy across 25 annotations).",
        "e_prime_rewrite": "Correlation with human ratings drops on the highest-entropy annotator-disagreement subsets (top 2-16% by entropy), for both absolute and pairwise rating setups.",
    },
    "hivemind-E-causal-speculation": {
        "original_quote": "[paraphrase] The paper offers several possible explanations for cross-model similarity -- shared data pipelines, training/alignment convergence, synthetic-data contamination -- while explicitly stating the exact causes remain unclear and a full causal analysis sits beyond this study's scope.",
        "e_prime_rewrite": "The paper lists candidate causes for cross-model homogeneity without asserting which one holds, and states that determining the real cause requires future work.",
    },
    "hivemind-F-motivating-premise": {
        "original_quote": "[paraphrase] The paper's motivation rests on a stated concern that repeated exposure to homogenized LM outputs risks a long-term homogenization of human thought itself -- a claim the paper attributes to prior work and does not itself test.",
        "e_prime_rewrite": "The paper cites prior literature for the premise that homogenized LM outputs pose a long-term risk to human thought diversity, without running its own test of that downstream societal effect.",
    },
}


def review_priority(state: str) -> str:
    """Per literature-engagement-addendum-v3.md Extension 1: 'unknown' and
    'contradictory' flag high, since Artificial Hivemind's own judge-
    miscalibration finding lands exactly on that contested territory.
    'known-true'/'known-false' flag standard."""
    return {
        "known-true": "standard",
        "known-false": "standard",
        "unknown": "high",
        "contradictory": "high",
    }.get(state, "unknown-state")


def call_rkllama(prompt: str, max_retries: int = 3) -> dict:
    """Same contract as run_all_26_rkllama.py's call_rkllama() -- takes a
    prompt, returns a parsed dict or None on failure. Retries network-level
    failures up to max_retries; returns None (CALL_FAILED) on a non-2xx
    response or unparseable output, never crashes the run."""
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
    try:
        combined = combine_bounds_and(
            result["premise_restated_bounds"], result["no_independent_support_bounds"]
        )
    except KeyError as e:
        print(f"    KeyError on circular_argument: missing {e}. Raw: {result}", file=sys.stderr)
        return None
    result["circular_argument_bounds"] = combined
    result["state"] = bounds_state(combined)
    return result


def run_shape_category(category_key: str, claim_id: str, ingestion_output: dict) -> dict:
    entry = FALLACY_SHAPE_DATA[category_key]
    prompt = build_bounds_prompt(category_key, ingestion_output, reference_passage=None)
    result = call_rkllama(prompt)
    if result is None:
        return None

    subs = entry["subconditions"]
    try:
        if entry["shape"] == "single":
            combined = result[f"{subs[0]['key']}_bounds"]
        else:
            bounds_a = result[f"{subs[0]['key']}_bounds"]
            bounds_b = result[f"{subs[1]['key']}_bounds"]
            combined = (
                combine_bounds_or(bounds_a, bounds_b)
                if entry["shape"] == "or"
                else combine_bounds_and(bounds_a, bounds_b)
            )
    except KeyError as e:
        print(f"    KeyError on {category_key}: missing {e}. Raw: {result}", file=sys.stderr)
        return None

    result[f"{category_key}_bounds"] = combined
    result["state"] = bounds_state(combined)
    return result


def record_result(all_results, claim_id, category, result, elapsed):
    """Overwrites an existing (claim_id, category) entry in place on retry
    instead of appending a duplicate -- same fix run_all_26_rkllama.py
    already carries."""
    for r in all_results:
        if r["claim_id"] == claim_id and r["category"] == category:
            r["result"] = result
            r["elapsed_s"] = elapsed
            return
    all_results.append({"claim_id": claim_id, "category": category, "result": result, "elapsed_s": elapsed})


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    progress_path = OUTPUT_DIR / "hivemind-26-rkllama-progress.json"

    all_results = []
    if progress_path.exists():
        all_results = json.loads(progress_path.read_text())
        done = {(r["claim_id"], r["category"]) for r in all_results if r.get("result") is not None}
        print(f"Resuming from {progress_path}: {len(done)} call(s) already done, "
              f"{len(all_results) - len(done)} prior failure(s) will retry.")
    else:
        done = set()

    categories = ["circular_argument"] + sorted(FALLACY_SHAPE_DATA.keys())
    total = len(HIVEMIND_CLAIM_INGESTION_OUTPUTS) * len(categories)
    call_num = 0

    for claim_id, ingestion_output in HIVEMIND_CLAIM_INGESTION_OUTPUTS.items():
        print(f"\n=== {claim_id} ===")
        for category in categories:
            call_num += 1
            if (claim_id, category) in done:
                continue
            print(f"  [{call_num}/{total}] {category}...")
            start = time.time()
            if category == "circular_argument":
                result = run_circular_argument(claim_id, ingestion_output)
            else:
                result = run_shape_category(category, claim_id, ingestion_output)
            elapsed = time.time() - start

            if result is not None:
                pri = review_priority(result["state"])
                result["review_priority"] = pri
                print(f"    -> {result['state']} ({pri})  ({elapsed:.1f}s)")
            else:
                print(f"    -> CALL_FAILED  ({elapsed:.1f}s)")

            record_result(all_results, claim_id, category, result, elapsed)
            progress_path.write_text(json.dumps(all_results, indent=2))

    failed = [r for r in all_results if r.get("result") is None]
    high_priority = [r for r in all_results if r.get("result") and r["result"].get("review_priority") == "high"]

    print(f"\n--- Done: {len(all_results)} calls, {len(failed)} failed ---")
    for r in failed:
        print(f"  FAILED: {r['claim_id']} / {r['category']}")
    if failed:
        print("  Rerun this script to retry only the failed/missing calls -- already-done calls are skipped.")

    print(f"\n--- PRIORITY REVIEW QUEUE: {len(high_priority)}/{len(all_results) - len(failed)} flag high ---")
    by_claim = {}
    for r in high_priority:
        by_claim.setdefault(r["claim_id"], []).append(r["category"])
    for claim_id, cats in by_claim.items():
        print(f"  {claim_id}: {len(cats)} high -- {', '.join(cats)}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    final_path = OUTPUT_DIR / f"hivemind-26-rkllama-{timestamp}.json"
    final_path.write_text(json.dumps(all_results, indent=2))
    print(f"\nWritten to: {progress_path}")
    print(f"Timestamped copy: {final_path}")


if __name__ == "__main__":
    main()
