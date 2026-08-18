#!/usr/bin/env python3
"""
Local Neuro-Symbolic Fallacy Screen — Board 2, RKLLama Only
=============================================================

Runs circular_argument_screen()'s and fallacy_bounds_screen()'s actual
prompts (ingest.py) against Board 2's local RKLLama model, using
build_local_corpus.py's proven call_local_model() unmodified. Neither
neuro-symbolic function ever had a local path before this file — ingest.py
only ever called _call_model(), hardcoded to the Anthropic API. This closes
that gap; it does not touch or loosen the standing rule.

Standing rule (2026-08-11, narrowed 2026-08-12): the Anthropic API stays
permanently blocked against every function in this framework, no exception.
Local inference on Board 2's NPU stays open — this script uses only that
path, same as build_local_corpus.py already does for Ingestion/Assessment.
No ANTHROPIC_API_KEY anywhere in this file.

USAGE (run from this directory, on the real Mac — Board 2 must be reachable
at 172.16.100.11:8080):

    python3 run_local_neuro_symbolic.py \\
        --model Qwen2.5-7B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0 \\
        --source-quote "Consequently, the harmfulness of guidelines is intentional, and biological effects are not collateral damage." \\
        --check circular

    python3 run_local_neuro_symbolic.py \\
        --model Qwen2.5-7B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0 \\
        --source-quote "..." \\
        --check bounds --category false_equivalence

Output prints to stdout and writes to NEURO_SYMBOLIC_RUNS/<model>-<timestamp>.json.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ingest import (
    CIRCULAR_ARGUMENT_PROMPT,
    FALLACY_SHAPE_DATA,
    build_bounds_prompt,
    build_reference_passage_section,
    combine_bounds_and,
    combine_bounds_or,
    bounds_state,
)
from build_local_corpus import (
    call_local_model,
    LOCAL_INGESTION_PROMPT,
    repair_split_scalars,
    repair_list_wrapped_scalars,
    normalize_record_fields,
    find_malformed_fields,
    MAX_SHAPE_RETRIES,
)

import yaml

RUNS_DIR = Path(__file__).parent / "NEURO_SYMBOLIC_RUNS"


def coerce_bounds_field(result: dict, bounds_fields: list[str]) -> None:
    """New backstop, first needed here: a bounds field can come back as the
    string "[0.9, 1.0]" instead of a real YAML list -- most likely via
    extract_fields_via_regex()'s fallback, which captures every field as
    raw text regardless of the field's intended type. Tries a second parse
    of just that field's text before giving up on it as malformed."""
    for name in bounds_fields:
        value = result.get(name)
        if isinstance(value, str):
            try:
                parsed = yaml.safe_load(value)
                if isinstance(parsed, list) and len(parsed) == 2:
                    result[name] = parsed
            except yaml.YAMLError:
                pass


def find_malformed_bounds_fields(result: dict, bounds_fields: list[str]) -> list[str]:
    """Bounds-pair counterpart to find_malformed_fields() in
    build_local_corpus.py -- that function only checks str/int shapes, and
    every neuro-symbolic prompt returns [lower, upper] pairs, a shape it
    was never asked to validate."""
    malformed = []
    for name in bounds_fields:
        value = result.get(name)
        ok = (
            isinstance(value, list)
            and len(value) == 2
            and all(isinstance(x, (int, float)) for x in value)
        )
        if not ok:
            malformed.append(name)
    return malformed


def call_neuro_symbolic(
    model_name: str,
    prompt: str,
    scalar_fields: list[str],
    bounds_fields: list[str],
    required_fields: list[str],
    max_retries: int = MAX_SHAPE_RETRIES,
) -> dict:
    """Same retry posture as build_local_corpus.py's call_with_shape_retry(),
    extended to also validate bounds-pair fields via
    find_malformed_bounds_fields() -- the neuro-symbolic prompts are the
    first local-model callers to return [lower, upper] pairs instead of
    scalars, a shape the existing retry loop was never built to check."""
    attempts = 0
    result = {}
    all_fields = list(scalar_fields) + list(bounds_fields)
    while attempts <= max_retries:
        attempts += 1
        result = call_local_model(model_name, prompt, expected_fields=all_fields)
        if "_parse_error" in result or "_network_error" in result:
            break
        normalize_record_fields(result)
        repair_split_scalars(result, scalar_fields)
        repair_list_wrapped_scalars(result, scalar_fields)
        coerce_bounds_field(result, bounds_fields)
        normalize_record_fields(result)
        malformed_scalar = find_malformed_fields(result, scalar_fields)
        malformed_bounds = find_malformed_bounds_fields(result, bounds_fields)
        empty = not any(result.get(f) for f in required_fields)
        if not malformed_scalar and not malformed_bounds and not empty:
            break
    result["_attempts"] = attempts
    return result


def local_ingest(model_name: str, source_text: str) -> dict:
    """Local Ingestion Layer call -- same LOCAL_INGESTION_PROMPT
    build_local_corpus.py already uses, so a claim run through this script
    stays directly comparable to anything in CORPUS/."""
    prompt = f"{LOCAL_INGESTION_PROMPT}\n\nSource claim to ingest:\n\n{source_text}"
    fields = ["original_quote", "e_prime_rewrite"]
    return call_neuro_symbolic(
        model_name, prompt,
        scalar_fields=fields, bounds_fields=[], required_fields=fields,
    )


def local_circular_argument_screen(model_name: str, ingestion_output: dict, reference_passage: str = None) -> dict:
    """Local counterpart to ingest.py's circular_argument_screen() --
    identical prompt, identical bounds-combination logic
    (combine_bounds_and, bounds_state), only the model-calling path
    differs: call_neuro_symbolic() -> Board 2, not _call_model() -> the
    Anthropic API.

    reference_passage, when given, supplies a second passage from elsewhere
    in the same source document -- closes the real single-quote scope gap
    logged 2026-08-13 (MEMORY.md). Forwarded straight through to
    build_reference_passage_section(), same as ingest.py's own function."""
    prompt = CIRCULAR_ARGUMENT_PROMPT.format(
        original_quote=ingestion_output["original_quote"],
        e_prime_rewrite=ingestion_output["e_prime_rewrite"],
        reference_passage_section=build_reference_passage_section(reference_passage),
    )
    scalar_fields = ["premise_restated_location", "no_independent_support_location", "explanation"]
    bounds_fields = ["premise_restated_bounds", "no_independent_support_bounds"]
    result = call_neuro_symbolic(
        model_name, prompt,
        scalar_fields=scalar_fields, bounds_fields=bounds_fields,
        required_fields=["explanation"],
    )
    if "_parse_error" in result or "_network_error" in result:
        return result
    combined = combine_bounds_and(
        result["premise_restated_bounds"], result["no_independent_support_bounds"]
    )
    result["circular_argument_bounds"] = combined
    result["state"] = bounds_state(combined)
    return result


def local_fallacy_bounds_screen(model_name: str, category_key: str, ingestion_output: dict, reference_passage: str = None) -> dict:
    """Local counterpart to ingest.py's fallacy_bounds_screen() -- identical
    prompt (build_bounds_prompt()) and combination logic, Board 2 instead
    of the Anthropic API.

    reference_passage, when given, forwards straight to build_bounds_prompt()
    -- see local_circular_argument_screen()'s docstring for the real gap
    this closes."""
    entry = FALLACY_SHAPE_DATA[category_key]
    prompt = build_bounds_prompt(category_key, ingestion_output, reference_passage=reference_passage)
    subs = entry["subconditions"]

    scalar_fields = [f"{s['key']}_location" for s in subs] + ["explanation"]
    bounds_fields = [f"{s['key']}_bounds" for s in subs]

    result = call_neuro_symbolic(
        model_name, prompt,
        scalar_fields=scalar_fields, bounds_fields=bounds_fields,
        required_fields=["explanation"],
    )
    if "_parse_error" in result or "_network_error" in result:
        return result

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
    result[f"{category_key}_bounds"] = combined
    result["state"] = bounds_state(combined)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run the neuro-symbolic bounds-pair fallacy gates against Board 2's local RKLLama model."
    )
    parser.add_argument("--model", required=True, help="RKLlama model name, exactly as it appears in /models on Board 2.")
    parser.add_argument("--source-quote", required=True, help="Verbatim source text to test.")
    parser.add_argument(
        "--reference-passage",
        default=None,
        help="Optional second passage from elsewhere in the same source "
        "document -- closes the real single-quote scope gap logged "
        "2026-08-13 (MEMORY.md). Lets circular_argument_screen()/"
        "fallacy_bounds_screen() judge whether --source-quote restates "
        "something already established there as a premise, instead of "
        "scoring --source-quote in total isolation. Omit for the original "
        "single-quote behavior.",
    )
    parser.add_argument("--check", choices=["circular", "bounds"], required=True)
    parser.add_argument("--category", choices=sorted(FALLACY_SHAPE_DATA.keys()), help="Required with --check bounds.")
    args = parser.parse_args()

    if args.check == "bounds" and not args.category:
        print("--check bounds requires --category", file=sys.stderr)
        sys.exit(1)

    print("Running local Ingestion Layer...", file=sys.stderr)
    ingestion_result = local_ingest(args.model, args.source_quote)
    if "_parse_error" in ingestion_result or "_network_error" in ingestion_result:
        print("Ingestion Layer failed:", ingestion_result, file=sys.stderr)
        sys.exit(1)

    if args.check == "circular":
        print("Running local circular-argument screen...", file=sys.stderr)
        check_result = local_circular_argument_screen(args.model, ingestion_result, reference_passage=args.reference_passage)
    else:
        print(f"Running local bounds screen: {args.category}...", file=sys.stderr)
        check_result = local_fallacy_bounds_screen(args.model, args.category, ingestion_result, reference_passage=args.reference_passage)

    record = {
        "model": args.model,
        "check": args.check,
        "category": args.category,
        "ingestion_layer": ingestion_result,
        "result": check_result,
    }

    print(yaml.dump(record, default_flow_style=False, sort_keys=False))

    RUNS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_model_name = args.model.replace("/", "_")
    check_label = args.check if args.check == "circular" else f"bounds-{args.category}"
    output_path = RUNS_DIR / f"{safe_model_name}-{check_label}-{timestamp}.json"
    output_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWritten to: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
