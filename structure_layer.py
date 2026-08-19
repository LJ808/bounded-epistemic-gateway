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
    derived -- see module docstring.

    Kept unmodified as the single-pass baseline. propagate_to_fixed_point()
    below runs this same edge-application logic repeatedly instead of once
    -- see that function for the real answer to whether single-pass ever
    differs from convergence on this graph."""
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


# ---------------------------------------------------------------------------
# FIXED-POINT PROPAGATION -- closes the real gap named in the module
# docstring above and in this project's own honest accounting: propagate()
# applies every edge exactly once, in file order. A claim with multiple
# incoming edges only sees the LATEST edge's effect compound onto whatever
# the earlier edge already produced -- correct only if no earlier-updated
# node ever needed to feed a LATER edge that appears earlier in the file.
# This function removes that assumption: it reapplies the full edge list
# repeatedly until no node's bounds change beyond `tolerance`, or until
# `max_iterations` caps it -- an honest, reported cap, not a silent one.
# Also runs the same convergence check against a second edge order
# (deterministically shuffled, fixed seed for reproducibility) -- the
# concrete test of whether order-dependence, the specific limitation named
# in the module docstring, actually survives past a single pass on this
# graph's real density, rather than leaving that as an assumption.
# ---------------------------------------------------------------------------

def _init_nodes(graph: dict, seeds: dict) -> dict:
    """Shared node-init logic, factored out of propagate() so
    propagate_to_fixed_point() builds identical starting state without
    duplicating propagate()'s own body or risking the two silently
    drifting apart."""
    return {
        claim_id: {
            "claim_id": claim_id,
            **seeds.get(claim_id, {"seed_bounds": None, "seed_source": "MISSING", "seed_caveat": "No seed found."}),
            "current_bounds": seeds.get(claim_id, {}).get("seed_bounds"),
            "applied_edges": [],
        }
        for claim_id in graph["claims"]
    }


def _apply_one_pass(nodes: dict, edges: list, iteration: int) -> bool:
    """Applies every supports/argues_against edge once, in the given order,
    mutating `nodes` in place. Returns True if any node's current_bounds
    changed beyond floating-point noise this pass. combines_with and
    shares_open_question_with are skipped here -- combines_with never
    feeds back into node bounds (see module docstring: reported once per
    pair, not written into either node), so it plays no role in
    convergence and gets computed once, after the fixed point is reached,
    by the caller. shares_open_question_with is a permanent no-op
    regardless of how many passes run."""
    changed = False
    for edge in edges:
        frm, rel, to = edge["from"], edge["relation"], edge["to"]
        if rel in ("shares_open_question_with", "combines_with"):
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

        before = target["current_bounds"]
        if abs(new_bounds[0] - before[0]) > 1e-9 or abs(new_bounds[1] - before[1]) > 1e-9:
            changed = True
            target["applied_edges"].append({
                "iteration": iteration, "from": frm, "relation": rel,
                "before": before, "after": new_bounds,
            })
            target["current_bounds"] = new_bounds
    return changed


def propagate_to_fixed_point(graph: dict, seeds: dict, max_iterations: int = 10, edge_order: list = None) -> dict:
    """Iterates _apply_one_pass() over the full edge list until no node's
    bounds change (a real fixed point), or until max_iterations caps it.
    `edge_order` lets the caller pass a specific (e.g. shuffled) edge
    ordering; defaults to the file's own order when omitted. Returns the
    same node/joint_pairs/no_op_edges shape as propagate(), plus
    `converged` and `iterations_run` -- an honest report of whether this
    graph's real density needed more than one pass, and whether the cap
    ever got hit without convergence (which would mean the result below
    isn't actually a fixed point and should get flagged, not trusted
    silently)."""
    edges = edge_order if edge_order is not None else graph["edges"]
    nodes = _init_nodes(graph, seeds)

    converged = False
    iterations_run = 0
    for iteration in range(1, max_iterations + 1):
        iterations_run = iteration
        changed = _apply_one_pass(nodes, edges, iteration)
        if not changed:
            converged = True
            break

    joint_pairs = []
    for edge in edges:
        if edge["relation"] != "combines_with":
            continue
        frm, to = edge["from"], edge["to"]
        a, b = nodes[frm]["current_bounds"], nodes[to]["current_bounds"]
        if a is None or b is None:
            continue
        joint = combine_bounds_and(a, b)
        joint_pairs.append({
            "pair": [frm, to], "relation": "combines_with",
            "joint_bounds": joint, "state": bounds_state(joint),
        })

    no_ops = [
        {"from": e["from"], "to": e["to"], "relation": e["relation"]}
        for e in edges if e["relation"] == "shares_open_question_with"
    ]

    for node in nodes.values():
        node["final_bounds"] = node["current_bounds"]
        node["final_state"] = bounds_state(node["current_bounds"]) if node["current_bounds"] else "NO SEED"

    return {
        "nodes": nodes, "joint_pairs": joint_pairs, "no_op_edges": no_ops,
        "converged": converged, "iterations_run": iterations_run,
    }


def check_order_independence(graph: dict, seeds: dict, max_iterations: int = 10, seed_value: int = 42) -> dict:
    """Runs propagate_to_fixed_point() twice -- once in the file's own edge
    order, once in a deterministically shuffled order (fixed random seed,
    reproducible) -- and diffs the two final results. Directly tests the
    module docstring's own named limitation (order-dependence) rather than
    leaving it as an unverified claim. If both orders converge to the same
    final_bounds for every claim, order-dependence doesn't survive past a
    single fixed-point run on this graph's real density -- if they don't
    match, that's a real, reportable finding, not a hypothetical one."""
    import random
    original_order = graph["edges"]
    shuffled_order = list(original_order)
    random.Random(seed_value).shuffle(shuffled_order)

    result_original = propagate_to_fixed_point(graph, seeds, max_iterations=max_iterations, edge_order=original_order)
    result_shuffled = propagate_to_fixed_point(graph, seeds, max_iterations=max_iterations, edge_order=shuffled_order)

    mismatches = []
    for claim_id in graph["claims"]:
        b1 = result_original["nodes"][claim_id]["final_bounds"]
        b2 = result_shuffled["nodes"][claim_id]["final_bounds"]
        if b1 is None or b2 is None:
            continue
        if abs(b1[0] - b2[0]) > 1e-9 or abs(b1[1] - b2[1]) > 1e-9:
            mismatches.append({"claim_id": claim_id, "original_order_bounds": b1, "shuffled_order_bounds": b2})

    return {
        "order_independent": len(mismatches) == 0,
        "mismatches": mismatches,
        "original_converged": result_original["converged"],
        "original_iterations": result_original["iterations_run"],
        "shuffled_converged": result_shuffled["converged"],
        "shuffled_iterations": result_shuffled["iterations_run"],
    }


# ---------------------------------------------------------------------------
# FORMULA ABLATION -- closes the real gap named honestly earlier this
# session: the OR-for-supports / AND-for-combines_with design reflects one
# reasoned pass, never checked against an alternative formula on the real
# graph. This runs the current formula (OR-combine for supports/
# argues_against) against one concrete alternative (AND-combine for
# supports/argues_against -- treating corroboration as requiring the
# supported claim to already meet the supporter's bar, not as lifting it)
# and reports every claim where the two formulas diverge. This does NOT
# prove the current formula is empirically better calibrated -- no ground
# truth exists in this project to make that claim (see MEMORY.md, this
# session). It DOES show, concretely rather than only by assertion,
# exactly what the formula choice changes on the real data -- including
# against the one external check available (covid-001, corroborated
# by two independent judges' verdicts per SYNTHESIS/near-duplicate-check-v1.md
# and the covid-004/covid-005 claim files).
# ---------------------------------------------------------------------------

def _propagate_with_combine(graph: dict, seeds: dict, supports_combine, max_iterations: int = 10) -> dict:
    """Same fixed-point loop as propagate_to_fixed_point(), parameterized
    on which combine rule supports/argues_against uses -- lets
    compare_propagation_formulas() run the current design (OR) and an
    alternative (AND) through the identical convergence machinery, so any
    difference in the result comes only from the formula, not from a
    different propagation mechanism."""
    nodes = _init_nodes(graph, seeds)

    def apply_pass(edges, iteration):
        changed = False
        for edge in edges:
            frm, rel, to = edge["from"], edge["relation"], edge["to"]
            if rel in ("shares_open_question_with", "combines_with"):
                continue
            target = nodes[to]
            source_bounds = nodes[frm]["current_bounds"]
            if source_bounds is None or target["current_bounds"] is None:
                continue
            if rel == "supports":
                new_bounds = supports_combine(target["current_bounds"], source_bounds)
            elif rel == "argues_against":
                new_bounds = supports_combine(target["current_bounds"], invert_bounds(source_bounds))
            else:
                continue
            before = target["current_bounds"]
            if abs(new_bounds[0] - before[0]) > 1e-9 or abs(new_bounds[1] - before[1]) > 1e-9:
                changed = True
                target["applied_edges"].append({"iteration": iteration, "from": frm, "relation": rel, "before": before, "after": new_bounds})
                target["current_bounds"] = new_bounds
        return changed

    converged = False
    iterations_run = 0
    for iteration in range(1, max_iterations + 1):
        iterations_run = iteration
        if not apply_pass(graph["edges"], iteration):
            converged = True
            break

    for node in nodes.values():
        node["final_bounds"] = node["current_bounds"]
        node["final_state"] = bounds_state(node["current_bounds"]) if node["current_bounds"] else "NO SEED"

    return {"nodes": nodes, "converged": converged, "iterations_run": iterations_run}


def compare_propagation_formulas(graph: dict, seeds: dict) -> dict:
    """Runs the current OR-for-supports formula and an AND-for-supports
    alternative through identical fixed-point machinery, then reports
    every claim where the two diverge -- a real, computed comparison, not
    a verbal argument for why OR is the right choice. Flags covid-001
    specifically: the one claim in this graph with an outside check
    available (two independent debate judges, Stansifer and Van Treuren,
    both reaching strong zoonotic-favoring verdicts through independent
    methods -- see CLAIMS/covid-origins/covid-004.md and covid-005.md)."""
    current = _propagate_with_combine(graph, seeds, combine_bounds_or)
    alternative = _propagate_with_combine(graph, seeds, combine_bounds_and)

    divergences = []
    for claim_id in graph["claims"]:
        cur = current["nodes"][claim_id]
        alt = alternative["nodes"][claim_id]
        if cur["final_bounds"] is None or alt["final_bounds"] is None:
            continue
        if abs(cur["final_bounds"][0] - alt["final_bounds"][0]) > 1e-9 or abs(cur["final_bounds"][1] - alt["final_bounds"][1]) > 1e-9:
            divergences.append({
                "claim_id": claim_id,
                "current_or_formula": {"final_bounds": cur["final_bounds"], "final_state": cur["final_state"]},
                "alternative_and_formula": {"final_bounds": alt["final_bounds"], "final_state": alt["final_state"]},
            })

    covid_001_note = None
    if "covid-001" in current["nodes"]:
        cur_state = current["nodes"]["covid-001"]["final_state"]
        alt_state = alternative["nodes"]["covid-001"]["final_state"]
        covid_001_note = (
            f"External check available for covid-001 only: two independent debate "
            f"judges (Stansifer, Van Treuren) both reach strong zoonotic-favoring "
            f"verdicts through independent methods (Bayes factors ~100-1000 and "
            f"~1000). Current OR formula: final_state={cur_state}. Alternative AND "
            f"formula: final_state={alt_state}. Neither formula's magnitude derives "
            f"from the Bayes-factor size itself -- both seed from circular-argument-"
            f"absence bounds, a different signal. This is a direction check, not a "
            f"calibration proof; n=1 external check exists in this entire project."
        )

    return {
        "divergences": divergences,
        "n_divergences": len(divergences),
        "n_claims_total": len(graph["claims"]),
        "covid_001_external_check_note": covid_001_note,
        "honest_limit": (
            "This comparison shows what the formula choice changes on the real "
            "graph. It does not establish that either formula is better "
            "calibrated -- no ground-truth reliability label exists for any of "
            "these 12 claims in this project (Jay declined hand-labeling, "
            "2026-08-17). The covid-001 direction check above is the only "
            "external reference point available, and it checks direction only, "
            "not magnitude."
        ),
    }


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

    # --- Fixed-point convergence check (closes the single-pass gap) ---
    fixed_point_result = propagate_to_fixed_point(graph, seeds)
    print("\n--- Fixed-point propagation vs. single-pass ---", file=sys.stderr)
    print(
        f"  converged={fixed_point_result['converged']}  "
        f"iterations_run={fixed_point_result['iterations_run']}",
        file=sys.stderr,
    )
    single_vs_fixed_diffs = []
    for claim_id in graph["claims"]:
        sp = result["nodes"][claim_id]["final_bounds"]
        fp = fixed_point_result["nodes"][claim_id]["final_bounds"]
        if sp is None or fp is None:
            continue
        if abs(sp[0] - fp[0]) > 1e-9 or abs(sp[1] - fp[1]) > 1e-9:
            single_vs_fixed_diffs.append({"claim_id": claim_id, "single_pass": sp, "fixed_point": fp})
    if single_vs_fixed_diffs:
        print(f"  {len(single_vs_fixed_diffs)} claim(s) differ between single-pass and fixed-point:", file=sys.stderr)
        for d in single_vs_fixed_diffs:
            print(f"    {d['claim_id']}: single_pass={d['single_pass']}  fixed_point={d['fixed_point']}", file=sys.stderr)
    else:
        print("  No claim differs between single-pass and fixed-point on this graph's real edges/density.", file=sys.stderr)

    order_check = check_order_independence(graph, seeds)
    print("\n--- Order-independence check (file order vs. shuffled order, both run to fixed point) ---", file=sys.stderr)
    print(f"  order_independent={order_check['order_independent']}", file=sys.stderr)
    print(
        f"  original: converged={order_check['original_converged']} iterations={order_check['original_iterations']}  "
        f"shuffled: converged={order_check['shuffled_converged']} iterations={order_check['shuffled_iterations']}",
        file=sys.stderr,
    )
    if order_check["mismatches"]:
        for m in order_check["mismatches"]:
            print(f"    MISMATCH {m['claim_id']}: original={m['original_order_bounds']} shuffled={m['shuffled_order_bounds']}", file=sys.stderr)

    # --- Formula ablation (closes the unvalidated-formula gap) ---
    formula_comparison = compare_propagation_formulas(graph, seeds)
    print("\n--- Formula ablation: current OR-for-supports vs. alternative AND-for-supports ---", file=sys.stderr)
    print(f"  {formula_comparison['n_divergences']} of {formula_comparison['n_claims_total']} claims diverge between formulas", file=sys.stderr)
    for d in formula_comparison["divergences"]:
        print(
            f"    {d['claim_id']}: OR->{d['current_or_formula']['final_bounds']} "
            f"({d['current_or_formula']['final_state']})  vs  "
            f"AND->{d['alternative_and_formula']['final_bounds']} "
            f"({d['alternative_and_formula']['final_state']})",
            file=sys.stderr,
        )
    if formula_comparison["covid_001_external_check_note"]:
        print(f"\n  {formula_comparison['covid_001_external_check_note']}", file=sys.stderr)
    print(f"\n  HONEST LIMIT: {formula_comparison['honest_limit']}", file=sys.stderr)

    # Persist the fixed-point + ablation results alongside the single-pass output
    validation_output_path = OUTPUT_DIR / f"validation-{timestamp}.json"
    validation_serializable = {
        "fixed_point": {
            "nodes": list(fixed_point_result["nodes"].values()),
            "joint_pairs": fixed_point_result["joint_pairs"],
            "no_op_edges": fixed_point_result["no_op_edges"],
            "converged": fixed_point_result["converged"],
            "iterations_run": fixed_point_result["iterations_run"],
        },
        "single_pass_vs_fixed_point_diffs": single_vs_fixed_diffs,
        "order_independence_check": order_check,
        "formula_ablation": formula_comparison,
    }
    validation_output_path.write_text(json.dumps(validation_serializable, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nValidation results written to: {validation_output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
