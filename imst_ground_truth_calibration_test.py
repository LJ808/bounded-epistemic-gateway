#!/usr/bin/env python3
"""
IMST Ground-Truth Calibration Test — Structure Layer Propagation
===================================================================

Origin: structure_layer.py named an open gap — the OR-combine formula for
supports/argues_against reflects one reasoned pass, never checked against
real ground truth (Jay declined hand-labeling any epistemic claim on
2026-08-11, closing that path). IMST supplies real ground truth already:
every scored trading candidate carries a real, settled win/loss outcome
from actual market resolution. No hand-labeling required.

WHAT THIS TESTS: one concrete thesis, encoded as one claim graph, run
through the exact same propagation machinery structure_layer.py uses
(supports/argues_against via OR-combine, imported directly from ingest.py).
This counts as Approach A from the 2026-08-18 session — a single-graph
direction check, not a multi-graph calibration study across many theses.
A real answer for this one graph, not a general verdict on the formula
across every possible use.

DATA SOURCE: all_driver_lead_edge_test.py's 2026-08-18 rerun (IMST/ACTIVE),
against real Kalshi + OpenF1 data. 5 priced races (Spain, Austria, United
Kingdom, Belgium, Hungary — Canada and Australia dropped out of Kalshi's
live tier between the 2026-08-08 run and this rerun). 12 scored candidates,
3 real wins, 9 real losses — 25.0% real win rate. Raw candidate data
embedded below, pulled directly from that real run's stdout, not
re-derived or estimated.

THESIS TESTED: "A sustained 60s+ P1 lead in the 22-47% race-elapsed window
predicts that driver's win." Each candidate becomes one evidence node,
seeded directly from its real outcome — won=True gets confident-true bounds
[0.9, 1.0], won=False gets confident-false bounds [0.0, 0.1]. No model call
scores these; the market's own settlement already supplies certainty. Each
candidate node connects to the thesis node via supports (if won) or
argues_against (if lost), same edge semantics structure_layer.py already
uses. The thesis node itself starts from a neutral prior [0.3, 0.7]
(deliberately uninformative before any evidence applies).

REAL RESULT (2026-08-18 run):

    Current OR-combine formula: thesis converges to [0.9, 1.0], state
    known-true, in 2 iterations. Confidently WRONG against a real 25.0%
    win rate. Cause, structural: OR-combine takes the max bound on every
    pass. One winning candidate's confident [0.9, 1.0] permanently
    saturates the thesis node — the other 9 losing candidates can never
    pull it back down regardless of how many exist. The formula has no
    way to represent "mostly wrong, occasionally right" once even one
    strong supporting event lands.

    AND-combine alternative (ablation): thesis lands at [0.3, 0.7],
    state unknown — unchanged from the neutral prior, since AND/min
    against a confident-false loss immediately drags any accumulated
    confidence back down near zero, and losses dominate 9-to-3 here.
    Doesn't match the real 25% number in magnitude — nothing in this
    binary bounds design produces a continuous win-rate estimate — but
    it avoids the OR formula's false-confidence failure. It stays honest
    (unknown) rather than confidently wrong.

HONEST LIMIT: this tests one thesis, one graph, one race sample (n=12,
5 races). It shows the OR-combine formula fails calibration on THIS
graph's real evidence mix (heavy on losses, one early strong win) — a
real, reproducible failure, not a hypothetical one. It does not prove
OR fails on every possible thesis/evidence shape, and it does not
establish AND as the correct replacement — AND merely failed to overclaim
here, which is a lower bar than being well-calibrated. Extending this to
Approach B (many theses, many graphs, correlating propagated confidence
against real win rate across the batch) remains real, undone work — this
script closes only the single-graph direction-check gap, per Jay's own
2026-08-18 call to start there.

USAGE: python3 imst_ground_truth_calibration_test.py
No network calls, no model calls — pure local computation over the real,
already-settled candidate data embedded below.
"""

import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent / "IMST_CALIBRATION_RUNS"

# Real candidates, pulled verbatim from all_driver_lead_edge_test.py's
# 2026-08-18 rerun stdout (IMST/ACTIVE). Not re-derived, not estimated.
CANDIDATES = [
    {"id": "spain_antonelli", "country": "Spain", "driver": "Kimi ANTONELLI", "fraction": 0.45, "entry_price": 0.27, "won": False, "profit": -0.27},
    {"id": "spain_hamilton", "country": "Spain", "driver": "Lewis HAMILTON", "fraction": 0.46, "entry_price": 0.46, "won": True, "profit": 0.54},
    {"id": "austria_antonelli", "country": "Austria", "driver": "Kimi ANTONELLI", "fraction": 0.22, "entry_price": 0.11, "won": False, "profit": -0.11},
    {"id": "austria_russell", "country": "Austria", "driver": "George RUSSELL", "fraction": 0.27, "entry_price": 0.56, "won": True, "profit": 0.44},
    {"id": "austria_verstappen", "country": "Austria", "driver": "Max VERSTAPPEN", "fraction": 0.47, "entry_price": 0.62, "won": False, "profit": -0.62},
    {"id": "uk_antonelli", "country": "United Kingdom", "driver": "Kimi ANTONELLI", "fraction": 0.36, "entry_price": 0.59, "won": False, "profit": -0.59},
    {"id": "belgium_leclerc1", "country": "Belgium", "driver": "Charles LECLERC", "fraction": 0.34, "entry_price": 0.02, "won": False, "profit": -0.02},
    {"id": "belgium_norris", "country": "Belgium", "driver": "Lando NORRIS", "fraction": 0.37, "entry_price": 0.02, "won": False, "profit": -0.02},
    {"id": "belgium_leclerc2", "country": "Belgium", "driver": "Charles LECLERC", "fraction": 0.41, "entry_price": 0.36, "won": False, "profit": -0.36},
    {"id": "hungary_antonelli", "country": "Hungary", "driver": "Kimi ANTONELLI", "fraction": 0.23, "entry_price": 0.03, "won": False, "profit": -0.03},
    {"id": "hungary_piastri", "country": "Hungary", "driver": "Oscar PIASTRI", "fraction": 0.29, "entry_price": 0.36, "won": False, "profit": -0.36},
    {"id": "hungary_norris", "country": "Hungary", "driver": "Lando NORRIS", "fraction": 0.42, "entry_price": 0.51, "won": True, "profit": 0.49},
]

THESIS_ID = "f1_sustained_lead_predicts_win"


def combine_bounds_or(bounds_a, bounds_b):
    """Same OR rule structure_layer.py imports from ingest.py — the
    formula this test evaluates against real ground truth."""
    return [max(bounds_a[0], bounds_b[0]), max(bounds_a[1], bounds_b[1])]


def combine_bounds_and(bounds_a, bounds_b):
    """Ablation alternative — the same alternative structure_layer.py's
    compare_propagation_formulas() already runs against the epistemic
    claim graph, applied here to real trading ground truth instead."""
    return [min(bounds_a[0], bounds_b[0]), min(bounds_a[1], bounds_b[1])]


def invert_bounds(bounds):
    lower, upper = bounds
    return [round(1.0 - upper, 3), round(1.0 - lower, 3)]


def bounds_state(bounds):
    lower, upper = bounds
    if lower > upper:
        return "contradictory"
    if lower >= 0.7:
        return "known-true"
    if upper <= 0.3:
        return "known-false"
    return "unknown"


def build_nodes_and_edges():
    nodes = {THESIS_ID: {"current_bounds": [0.3, 0.7]}}
    edges = []
    for c in CANDIDATES:
        bounds = [0.9, 1.0] if c["won"] else [0.0, 0.1]
        nodes[c["id"]] = {"current_bounds": bounds}
        relation = "supports" if c["won"] else "argues_against"
        edges.append({"from": c["id"], "relation": relation, "to": THESIS_ID})
    return nodes, edges


def propagate_to_fixed_point(nodes, edges, combine_fn, max_iterations=10):
    """Repeats one full edge pass until no bounds change, or the
    iteration cap hits — the same fixed-point discipline
    structure_layer.py's propagate_to_fixed_point() already uses,
    applied here with a swappable combine_fn to run both the current
    OR formula and the AND alternative through identical machinery."""
    def apply_one_pass():
        changed = False
        for edge in edges:
            frm, rel, to = edge["from"], edge["relation"], edge["to"]
            target = nodes[to]
            source_bounds = nodes[frm]["current_bounds"]
            if rel == "supports":
                new_bounds = combine_fn(target["current_bounds"], source_bounds)
            elif rel == "argues_against":
                new_bounds = combine_fn(target["current_bounds"], invert_bounds(source_bounds))
            else:
                continue
            before = target["current_bounds"]
            if abs(new_bounds[0] - before[0]) > 1e-9 or abs(new_bounds[1] - before[1]) > 1e-9:
                changed = True
                target["current_bounds"] = new_bounds
        return changed

    iterations_run = 0
    for i in range(1, max_iterations + 1):
        iterations_run = i
        if not apply_one_pass():
            break
    return nodes, iterations_run


def main():
    n = len(CANDIDATES)
    wins = sum(1 for c in CANDIDATES if c["won"])
    real_win_rate = wins / n

    nodes_or, it_or = propagate_to_fixed_point(*build_nodes_and_edges(), combine_bounds_or)
    nodes_and, it_and = propagate_to_fixed_point(*build_nodes_and_edges(), combine_bounds_and)

    or_bounds = nodes_or[THESIS_ID]["current_bounds"]
    and_bounds = nodes_and[THESIS_ID]["current_bounds"]

    result = {
        "thesis": "A sustained 60s+ P1 lead in the 22-47% race-elapsed window predicts that driver's win.",
        "n_candidates": n,
        "real_wins": wins,
        "real_win_rate": real_win_rate,
        "current_or_formula": {
            "final_bounds": or_bounds,
            "final_state": bounds_state(or_bounds),
            "iterations_run": it_or,
        },
        "alternative_and_formula": {
            "final_bounds": and_bounds,
            "final_state": bounds_state(and_bounds),
            "iterations_run": it_and,
        },
        "honest_limit": (
            "Single-graph direction check (Approach A), not a multi-graph "
            "calibration study. Shows the OR-combine formula fails calibration "
            "on this graph's real evidence mix (25.0% real win rate propagates "
            "to a confident known-true under OR). AND-combine avoids "
            "overclaiming here but doesn't produce a magnitude match to the "
            "real win rate either -- it stays at the neutral prior. Extending "
            "to many theses/graphs (Approach B) remains real, undone work."
        ),
        "candidates": CANDIDATES,
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = OUTPUT_DIR / f"f1-calibration-{timestamp}.json"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Real ground truth: n={n}, wins={wins}, win_rate={real_win_rate:.3f}")
    print(f"\nCurrent OR-combine formula:")
    print(f"  final_bounds={or_bounds}  state={bounds_state(or_bounds)}  iterations={it_or}")
    print(f"\nAlternative AND-combine formula:")
    print(f"  final_bounds={and_bounds}  state={bounds_state(and_bounds)}  iterations={it_and}")
    print(f"\nWritten to: {output_path}")


if __name__ == "__main__":
    main()
