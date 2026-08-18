#!/usr/bin/env python3
"""
Local Neuro-Symbolic Bounds Pass — Batch, All 12 Claims
==========================================================

Extends the neuro-symbolic circular-argument screen from its original
3-claim pilot (eggs-003, covid-003, blackhole-002 — fallacy-screen-
worked-examples-v1.md) to all 12 claims in the FLF corpus, against
Board 2's local RKLLama model. Reuses run_local_neuro_symbolic.py's
local_circular_argument_screen() unmodified — this file adds no new
prompt wording or scoring logic of its own, only the batch loop and
the input-sourcing decision documented below.

INPUT SOURCING, real and deliberate:

    original_quote  <- pulled fresh from CLAIMS/*.md via
                        build_local_corpus.py's extract_quote(),
                        verbatim by construction, independent of any
                        prior corpus run's fidelity state.

    e_prime_rewrite  <- pulled from the most complete existing corpus
                        run covering all 12 claims (the 2026-08-13
                        full run). No existing single corpus file
                        combines full 12-claim coverage with the
                        2026-08-15 quote-fidelity fix confirmed against
                        it — the fix's confirming rerun only covered
                        black-holes (3 claims). Rather than wait on a
                        fresh 12-claim Ingestion run this script
                        doesn't need, this script sources the rewrite
                        from existing generated data and the quote
                        directly from the primary source file, sidestepping
                        the fidelity question entirely for original_quote
                        (it never touches model-generated original_quote
                        at all).

This script makes no Ingestion Layer model calls. It extends the
Assessment-adjacent neuro-symbolic bounds pass only — the piece
next-steps-v1.md and TRC MEMORY.md (2026-08-13) named as covering
3 of 12 claims, unextended until now.

USAGE (run from this directory, on the real Mac — Board 2 must be
reachable at 172.16.100.11:8080):

    python3 run_local_neuro_symbolic_batch.py \\
        --model Qwen2.5-7B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0 \\
        --rewrite-source CORPUS/Qwen2.5-7B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0-20260813-172904.jsonl

Output writes to NEURO_SYMBOLIC_RUNS/<model>-circular-batch-<timestamp>.json,
one record per claim, plus prints a summary table to stdout.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from build_local_corpus import find_claim_files, extract_quote, CLAIMS_DIR
from run_local_neuro_symbolic import local_circular_argument_screen, RUNS_DIR

import yaml


# Out-of-scope exclusions for circular-argument screening, Jay's call
# 2026-08-17 after checking the model's own explanation text against a
# real run. circular_argument_screen() tests whether an argument's
# conclusion restates one of its own premises -- a check that presupposes
# the input actually has a premise and a conclusion as separate parts.
# eggs-001 and eggs-002 are bare single-clause statistical claims ("there
# is a dose-response positive association...") with no such structure --
# nothing for a premise to restate. The 2026-08-17 14B run scored both
# known-true [0.8, 1.0], and both explanations show the same conflation:
# the model compared original_quote against e_prime_rewrite (which are
# SUPPOSED to closely track each other -- that's the Ingestion Layer
# working as designed) and mistook that expected similarity for internal
# premise-restates-conclusion circularity. eggs-002's own
# premise_restated_location field quotes the same sentence twice, once
# from each field, as its own evidence -- the category mismatch stated
# directly in the model's output. Excluded here rather than silently
# rescored; a documented exclusion is real rigor, a hidden one is a gap.
CIRCULAR_SCREEN_OUT_OF_SCOPE = {
    "eggs-001": (
        "Single-clause statistical claim, no separate premise/conclusion "
        "structure for circular argument to consist of. 2026-08-17 14B run "
        "scored known-true [0.8, 1.0]; the model's own explanation conflated "
        "original_quote-vs-e_prime_rewrite similarity (expected by design) "
        "with premise-restates-conclusion circularity -- a category mismatch, "
        "not a real finding. Excluded from circular-argument screening."
    ),
    "eggs-002": (
        "Single-clause statistical claim, no separate premise/conclusion "
        "structure for circular argument to consist of. 2026-08-17 14B run "
        "scored known-true [0.8, 1.0]; premise_restated_location quoted the "
        "same sentence from original_quote and e_prime_rewrite as its own "
        "evidence -- the same category mismatch as eggs-001. Excluded from "
        "circular-argument screening."
    ),
}


def load_rewrites(rewrite_source: Path) -> dict:
    """Load claim_id -> e_prime_rewrite from an existing corpus JSONL.
    Only the rewrite field gets used from this file — original_quote
    comes from CLAIMS/*.md directly, per this script's docstring."""
    rewrites = {}
    with rewrite_source.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            claim_id = record.get("claim_id")
            rewrite = record.get("ingestion_layer", {}).get("e_prime_rewrite")
            if claim_id and isinstance(rewrite, str):
                rewrites[claim_id] = rewrite
    return rewrites


def main():
    parser = argparse.ArgumentParser(
        description="Run the neuro-symbolic circular-argument bounds screen "
        "against all 12 claims via Board 2's local RKLLama model."
    )
    parser.add_argument("--model", required=True, help="RKLlama model name, exactly as it appears in /models on Board 2.")
    parser.add_argument(
        "--rewrite-source",
        required=True,
        type=Path,
        help="Existing CORPUS/*.jsonl file to pull e_prime_rewrite from "
        "for each claim. Must cover all 12 claims (the 2026-08-13 full "
        "run does). original_quote is NOT read from this file -- it "
        "comes fresh from CLAIMS/*.md instead, see script docstring.",
    )
    parser.add_argument(
        "--case",
        help="Limit to one case subdirectory under CLAIMS/ (e.g. black-holes). Omit to run all 12.",
    )
    args = parser.parse_args()

    if not args.rewrite_source.exists():
        print(f"--rewrite-source not found: {args.rewrite_source}", file=sys.stderr)
        sys.exit(1)

    rewrites = load_rewrites(args.rewrite_source)
    claim_files = find_claim_files(args.case)

    if not claim_files:
        print("No claim files found.", file=sys.stderr)
        sys.exit(1)

    missing_rewrite = [p.stem for p in claim_files if p.stem not in rewrites]
    if missing_rewrite:
        print(
            f"WARNING: {len(missing_rewrite)} claim(s) have no rewrite in "
            f"--rewrite-source, will be skipped: {missing_rewrite}",
            file=sys.stderr,
        )

    results = []
    for i, claim_path in enumerate(claim_files, 1):
        claim_id = claim_path.stem
        if claim_id not in rewrites:
            continue

        if claim_id in CIRCULAR_SCREEN_OUT_OF_SCOPE:
            print(f"[{i}/{len(claim_files)}] {claim_id}... SKIPPED (out of scope)", file=sys.stderr)
            results.append({
                "claim_id": claim_id,
                "source_file": str(claim_path.relative_to(CLAIMS_DIR)),
                "in_scope": False,
                "exclusion_reason": CIRCULAR_SCREEN_OUT_OF_SCOPE[claim_id],
            })
            continue

        print(f"[{i}/{len(claim_files)}] {claim_id}...", file=sys.stderr)

        source_quote = extract_quote(claim_path)
        ingestion_output = {
            "original_quote": source_quote,
            "e_prime_rewrite": rewrites[claim_id],
        }

        check_result = local_circular_argument_screen(args.model, ingestion_output)

        results.append({
            "claim_id": claim_id,
            "source_file": str(claim_path.relative_to(CLAIMS_DIR)),
            "in_scope": True,
            "ingestion_layer": ingestion_output,
            "result": check_result,
        })

        if "_parse_error" in check_result or "_network_error" in check_result:
            print(f"  -> ERROR: {check_result}", file=sys.stderr)
        else:
            print(f"  -> state={check_result.get('state')} bounds={check_result.get('circular_argument_bounds')}", file=sys.stderr)

    RUNS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_model_name = args.model.replace("/", "_")
    output_path = RUNS_DIR / f"{safe_model_name}-circular-batch-{timestamp}.json"
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n--- Summary, {len(results)}/{len(claim_files)} claims scored ---", file=sys.stderr)
    for r in results:
        if not r.get("in_scope", True):
            print(f"  {r['claim_id']:16s} {'OUT-OF-SCOPE':14s}", file=sys.stderr)
            continue
        state = r["result"].get("state", "ERROR")
        bounds = r["result"].get("circular_argument_bounds", "n/a")
        print(f"  {r['claim_id']:16s} {state:14s} {bounds}", file=sys.stderr)

    print(f"\nWritten to: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
