#!/usr/bin/env python3
"""
Structure Layer — Bounds Propagation Over the Existing Claim Graph
=====================================================================

FLF names three pipeline stages: Ingestion, Structure, Assessment. The
submission formalized two of them in code (ingest.py's ingest_claim()/
assess_claim()). Structure existed only as a real, hand-checked graph in
SYNTHESIS/structure-layer-worked-example-v1.md -- 21 within-case pairs
checked across all 12 claims, a closed four-tag vocabulary, every edge
and every explicit non-edge reasoned out -- but nothing computed with it.
This script closes that gap: it reads the existing graph directly (no
re-typing it), seeds each claim with a real reliability bounds pair, and
propagates that seed through the graph's typed edges using the same
bounds-pair machinery (combine_bounds_and/or, bounds_state) already
proven in ingest.py's neuro-symbolic pilot.

SEEDING, two real sources, honestly distinct:

    10 of 12 claims: inverted circular_argument_bounds from the 2026-08-17
    neuro-symbolic batch run (NEURO_SYMBOLIC_RUNS/). circular_argument_bounds
    measures confidence a SPECIFIC FALLACY (circular argument) is present --
    the inverse of what a Structure Layer node wants (confidence the claim
    is reliable). This script inverts it (1 - bounds) to get a reliability
    seed. Real limitation, stated plainly rather than hidden: this only
    reflects the absence of ONE fallacy category out of 26 -- not general
    evidentiary strength, sample size, or source quality. A partial proxy,
    not a truth score.

    2 of 12 claims (eggs-001, eggs-002): excluded from circular-argument
    screening entirely (2026-08-17, Jay's call -- see
    CIRCULAR_SCREEN_OUT_OF_SCOPE in run_local_neuro_symbolic_batch.py,
    both are bare single-clause claims with no premise/conclusion structure
    for that check to apply to). Seeded instead from the Assessment Layer's
    confidence_assessment (1-5 int, self-assessed rewrite robustness against
    motivated misreading) via CORPUS/*20260813-172904.jsonl, linearly mapped
    to a bounds pair. A weaker, differently-scoped proxy than the other 10 --
    measures something else entirely (rewrite robustness, not fallacy
    absence) and is labeled as such in every output record.

PROPAGATION FORMULAS, reasoned from what each tag in the existing graph
actually means, not assumed by default:

    supports            -> OR-combine (max) with the supporting claim's
                            seed. Corroboration should pull the supported
                            claim's bounds UP toward the stronger source,
                            not dilute toward the weaker one -- which
                            AND/min (the wrong tool here) would do.
    argues_against       -> OR-combine with the INVERTED contesting claim's
                            seed. Same logic, opposite direction: strong
                            counter-evidence pulls the contested claim's
                            bounds down.
    combines_with        -> AND-combine (min). Genuinely joint evidence --
                            both components must hold together for the
                            combined verdict, matching how
                            circular_argument_screen() already uses AND
                            for two subconditions that must both hold.
                            Symmetric: both claims in the pair get the same
                            combined bounds, reported once per pair, not
                            silently written into each node as if
                            independently derived.
    shares_open_question_with -> no-op. Explicitly logged as such --
                            neither claim resolves the other, so nothing
                            propagates.

Single-pass, order-dependent propagation over the edge list as given in
the source file -- NOT an iterated fixed-point. A real simplification,
named here rather than implied away: a claim with multiple incoming edges
gets them applied in file order, so the final bounds can depend on edge
order in principle. Not observed to matter for this graph's actual density
(most claims have 0-2 incoming edges), but stated honestly as a scope
limit, not a proven-irrelevant one.

USAGE (run from this directory on the real Mac -- no model calls, no
network, pure local computation over existing data):

    python3 structure_layer.py

Output writes to STRUCTURE_LAYER_RUNS/propagated-<timestamp>.json and
prints a summary table to stdout.
"""

import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ingest import combine_bounds_and, combine_bounds_or, bounds_state

import yaml

ROOT = Path(__file__).parent
STRUCTURE_DOC = ROOT / "SYNTHESIS" / "structure-layer-worked-example-v1.md"
NEURO_SYMBOLIC_RUN = ROOT / "NEURO_SYMBOLIC_RUNS" / "Qwen2.5-14B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0-circular-batch-20260817-173925.json"
CORPUS_FALLBACK = ROOT / "CORPUS" / "Qwen2.5-7B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0-20260813-172904.jsonl"
OUTPUT_DIR = ROOT / "STRUCTURE_LAYER_RUNS"

YAML_BLOCK_PATTERN = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)


def load_graph() -> dict:
    """Parse the real edge graph directly out of
    structure-layer-worked-example-v1.md's own ```yaml block -- no
    re-typing the graph into this script, so the graph and its
    documentation can never silently drift apart."""
    text = STRUCTURE_DOC.read_text(encoding="utf-8")
    match = YAML_BLOCK_PATTERN.search(text)
    if not match:
        print(f"No ```yaml block found in {STRUCTURE_DOC}", file=sys.stderr)
        sys.exit(1)
    graph = yaml.safe_load(match.group(1))
    return graph


def invert_bounds(bounds: list) -> list:
    """1 - bounds, reversed. Used both to convert 'confidence a fallacy is
    present' into 'confidence the claim is reliable' (seeding), and to
    invert a contesting claim's seed before OR-combining it into an
    argues_against target (propagation). Rounded to 3 decimals -- plain
    1.0 - x subtraction on values like 0.7 produces float noise
    (0.30000000000000004) with no real meaning; rounding avoids
    displaying false precision without changing any actual threshold
    decision (bounds_state()'s 0.7/0.3 cutoffs sit nowhere near this
    noise floor)."""
    lower, upper = bounds
    return [round(1.0 - upper, 3), round(1.0 - lower, 3)]


def load_neuro_symbolic_seeds() -> dict:
    """Load the 10 in-scope claims' circular_argument_bounds and invert
    them into reliability seeds. Records the raw (pre-inversion) bounds
    too, so the inversion is auditable, not silently applied."""
    seeds = {}
    data = json.loads(NEURO_SYMBOLIC_RUN.read_text(encoding="utf-8"))
    for record in data:
        if not record.get("in_scope", True):
            continue
        raw_bounds = record["result"]["circular_argument_bounds"]
        seeds[record["claim_id"]] = {
            "seed_bounds": invert_bounds(raw_bounds),
            "seed_source": "neuro-symbolic circular-argument bounds, inverted",
            "raw_circular_argument_bounds": raw_bounds,
            "seed_caveat": (
                "Partial proxy -- reflects only the absence of ONE fallacy "
                "category (circular argument) out of 26 tracked. Not a "
                "general evidentiary-strength or truth score."
            ),
        }
    return seeds


def load_confidence_proxy_seeds(claim_ids: list) -> dict:
    """Load confidence_assessment for claims excluded from circular-argument
    screening (currently eggs-001, eggs-002), linearly mapped from the 1-5
    scale to a bounds pair centered on (c-1)/4 with a fixed +/-0.15 margin,
    clipped to [0, 1]. A materially different, weaker proxy than the
    neuro-symbolic seeds above -- confidence_assessment measures rewrite
    robustness against motivated misreading, not fallacy absence. Labeled
    as such in every output record, not blended silently with the other
    10 claims' seed source."""
    seeds = {}
    with CORPUS_FALLBACK.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            claim_id = record.get("claim_id")
            if claim_id not in claim_ids:
                continue
            confidence = record.get("assessment_layer", {}).get("confidence_assessment")
            if not isinstance(confidence, int):
                continue
            center = (confidence - 1) / 4.0
            seeds[claim_id] = {
                "seed_bounds": [max(0.0, center - 0.15), min(1.0, center + 0.15)],
                "seed_source": "confidence_assessment proxy (NOT neuro-symbolic -- different scope)",
                "raw_confidence_assessment": confidence,
                "seed_caveat": (
                    "Excluded from circular-argument screening (single-clause "
                    "claim, no premise/conclusion structure -- see "
                    "CIRCULAR_SCREEN_OUT_OF_SCOPE). This proxy measures "
                    "rewrite robustness against motivated misreading, a "
                    "materially different and weaker signal than the "
                    "neuro-symbolic seed used for the other 10 claims."
                ),
            }
    return seeds


def propagate(graph: dict, seeds: dict) -> dict:
    """Single-pass propagation over the edge list in file order. Returns
    per-claim records with seed bounds, applied edges, and final
    propagated bounds. combines_with pairs get a separate joint-bounds
    entry rather than being written into each node as if independently
    derived -- see module docstring."""
    nodes = {
        claim_id: {
            "claim_id": claim_id,
            **seeds.get(claim_id, {"seed_bounds": None, "seed_source": "MISSING", "seed_caveat": "No seed found."}),
            "current_bounds": seeds.get(claim_id, {}).get("seed_bounds"),
            "applied_edges": [],
        }
        for claim_id in graph["claims"]
    }

    joint_pairs = []
    no_ops = []

    for edge in graph["edges"]:
        frm, rel, to = edge["from"], edge["relation"], edge["to"]

        if rel == "shares_open_question_with":
            no_ops.append({"from": frm, "to": to, "relation": rel})
            continue

        if rel == "combines_with":
            a, b = nodes[frm]["current_bounds"], nodes[to]["current_bounds"]
            if a is None or b is None:
                continue
            joint = combine_bounds_and(a, b)
            joint_pairs.append({
                "pair": [frm, to],
                "relation": rel,
                "joint_bounds": joint,
                "state": bounds_state(joint),
            })
            continue

        target = nodes[to]
        source_bounds = nodes[frm]["current_bounds"]
        if source_bounds is None or target["current_bounds"] is None:
            continue

        if rel == "supports":
            new_bounds = combine_bounds_or(target["current_bounds"], source_bounds)
        elif rel == "argues_against":
            new_bounds = combine_bounds_or(target["current_bounds"], invert_bounds(source_bounds))
        else:
            print(f"Unknown relation type: {rel}", file=sys.stderr)
            continue

        target["applied_edges"].append({
            "from": frm, "relation": rel,
            "before": target["current_bounds"], "after": new_bounds,
        })
        target["current_bounds"] = new_bounds

    for node in nodes.values():
        node["final_bounds"] = node["current_bounds"]
        node["final_state"] = bounds_state(node["current_bounds"]) if node["current_bounds"] else "NO SEED"

    return {"nodes": nodes, "joint_pairs": joint_pairs, "no_op_edges": no_ops}


def main():
    graph = load_graph()

    neuro_seeds = load_neuro_symbolic_seeds()
    excluded_claims = [c for c in graph["claims"] if c not in neuro_seeds]
    proxy_seeds = load_confidence_proxy_seeds(excluded_claims)

    seeds = {**neuro_seeds, **proxy_seeds}

    missing = [c for c in graph["claims"] if c not in seeds]
    if missing:
        print(f"WARNING: no seed found for: {missing}", file=sys.stderr)

    result = propagate(graph, seeds)

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = OUTPUT_DIR / f"propagated-{timestamp}.json"

    serializable = {
        "nodes": list(result["nodes"].values()),
        "joint_pairs": result["joint_pairs"],
        "no_op_edges": result["no_op_edges"],
    }
    output_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n--- Structure Layer propagation, per claim ---", file=sys.stderr)
    for claim_id in graph["claims"]:
        node = result["nodes"][claim_id]
        n_edges = len(node["applied_edges"])
        print(
            f"  {claim_id:14s} seed={node['seed_bounds']}  "
            f"final={node['final_bounds']}  state={node['final_state']:12s}  "
            f"({n_edges} edge(s) applied, source: {node['seed_source']})",
            file=sys.stderr,
        )

    if result["joint_pairs"]:
        print("\n--- combines_with joint pairs (not written into individual nodes) ---", file=sys.stderr)
        for jp in result["joint_pairs"]:
            print(f"  {jp['pair']}  joint_bounds={jp['joint_bounds']}  state={jp['state']}", file=sys.stderr)

    if result["no_op_edges"]:
        print(f"\n--- {len(result['no_op_edges'])} shares_open_question_with edge(s), no propagation ---", file=sys.stderr)

    print(f"\nWritten to: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
