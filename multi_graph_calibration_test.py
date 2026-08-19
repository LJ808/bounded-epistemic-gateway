#!/usr/bin/env python3
"""
Multi-Graph Ground-Truth Calibration Study — Structure Layer Propagation
==========================================================================

Extends imst_ground_truth_calibration_test.py from Approach A (one thesis,
one graph, single-graph direction check) toward Approach B (many theses,
many graphs, correlating propagated confidence against real win rate across
the batch) -- the exact extension that script's own honest_limit field
names as real, undone work.

HONEST STATE OF THIS EXTENSION, stated plainly rather than implied away:
this file generalizes the MACHINERY into a real, reusable multi-graph
framework -- GRAPHS is a list, not a hardcoded single thesis, and every
function below operates over N graphs, not one. But it runs against exactly
ONE real graph as of this run, because that's how many exist in this vault
with real, settled ground truth. Checked directly before writing this:
IMST/ACTIVE/f1_edge_test_results.json holds the identical 12-candidate set
already embedded in the single-graph test, not a second graph. The WC
Kalshi orderbook (39.26M rows, real, confirmed) still needs real
settled-outcome data joined to it before it's usable here -- named as
not-yet-pulled in IMST's own 2026-08-18 banner. Brasileirão and the other
FIFA_Sprint_v2.md theses (mutex-arb convergence, late-goal repricing,
favorite-fade) are speced, not built. No synthetic or fabricated ground
truth gets added here to pad the graph count -- a calibration study built
on invented data would defeat its own purpose. Running this against a real
second and third graph requires that data getting pulled first; this file
is ready to take it the moment it exists (add a dict to GRAPHS, nothing
else changes).

USAGE: python3 multi_graph_calibration_test.py
No network calls, no model calls -- pure local computation over real,
already-settled candidate data.
"""

import json
import statistics
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent / "IMST_CALIBRATION_RUNS"


# ---------------------------------------------------------------------------
# GRAPHS -- one entry per real thesis with real, settled ground truth.
# Add a new dict here the moment a second real graph exists. Nothing else
# in this file needs to change to pick it up.
# ---------------------------------------------------------------------------

GRAPHS = [
    {
        "graph_id": "f1_sustained_lead_predicts_win",
        "thesis": "A sustained 60s+ P1 lead in the 22-47% race-elapsed window predicts that driver's win.",
        "source": "all_driver_lead_edge_test.py, 2026-08-18 rerun, IMST/ACTIVE, real Kalshi + OpenF1 data",
        "candidates": [
            {"id": "spain_antonelli", "won": False},
            {"id": "spain_hamilton", "won": True},
            {"id": "austria_antonelli", "won": False},
            {"id": "austria_russell", "won": True},
            {"id": "austria_verstappen", "won": False},
            {"id": "uk_antonelli", "won": False},
            {"id": "belgium_leclerc1", "won": False},
            {"id": "belgium_norris", "won": False},
            {"id": "belgium_leclerc2", "won": False},
            {"id": "hungary_antonelli", "won": False},
            {"id": "hungary_piastri", "won": False},
            {"id": "hungary_norris", "won": True},
        ],
    },
    # NEXT REAL GRAPH GOES HERE. Candidates for what it could be, from named
    # but not-yet-pulled work: WC mutex-arb convergence, late-goal
    # repricing, or favorite-fade (all speced in FIFA_Sprint_v2.md, all
    # blocked on the same real-settled-outcome join to the WC orderbook
    # named as not-yet-done in IMST's 2026-08-18 banner). Brasileirão,
    # mentioned as a possible batch partner in the same banner, is
    # unstarted. None fabricated here.
]


def combine_bounds_or(bounds_a, bounds_b):
    return [max(bounds_a[0], bounds_b[0]), max(bounds_a[1], bounds_b[1])]


def combine_bounds_and(bounds_a, bounds_b):
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


def build_nodes_and_edges(graph):
    thesis_id = graph["graph_id"]
    nodes = {thesis_id: {"current_bounds": [0.3, 0.7]}}
    edges = []
    for c in graph["candidates"]:
        bounds = [0.9, 1.0] if c["won"] else [0.0, 0.1]
        nodes[c["id"]] = {"current_bounds": bounds}
        relation = "supports" if c["won"] else "argues_against"
        edges.append({"from": c["id"], "relation": relation, "to": thesis_id})
    return nodes, edges


def propagate_to_fixed_point(nodes, edges, combine_fn, max_iterations=10):
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


def run_one_graph(graph):
    """Runs both formulas against one graph, returns a real result dict --
    the same computation the single-graph script did, generalized to take
    any graph dict with this shape."""
    n = len(graph["candidates"])
    wins = sum(1 for c in graph["candidates"] if c["won"])
    real_win_rate = wins / n

    nodes_or, it_or = propagate_to_fixed_point(*build_nodes_and_edges(graph), combine_bounds_or)
    nodes_and, it_and = propagate_to_fixed_point(*build_nodes_and_edges(graph), combine_bounds_and)

    or_bounds = nodes_or[graph["graph_id"]]["current_bounds"]
    and_bounds = nodes_and[graph["graph_id"]]["current_bounds"]

    return {
        "graph_id": graph["graph_id"],
        "thesis": graph["thesis"],
        "source": graph["source"],
        "n_candidates": n,
        "real_wins": wins,
        "real_win_rate": real_win_rate,
        "current_or_formula": {
            "final_bounds": or_bounds,
            "final_state": bounds_state(or_bounds),
            "iterations_run": it_or,
            "or_overclaims": bounds_state(or_bounds) == "known-true" and real_win_rate < 0.7,
        },
        "alternative_and_formula": {
            "final_bounds": and_bounds,
            "final_state": bounds_state(and_bounds),
            "iterations_run": it_and,
        },
    }


def aggregate(graph_results):
    """Real cross-graph aggregation -- correlation and overclaim rate --
    computed once N >= 2, since a single-point correlation is meaningless.
    With N == 1 (current real state), reports that plainly instead of
    computing a statistic that would misrepresent one data point as a
    trend."""
    n_graphs = len(graph_results)
    or_overclaim_count = sum(1 for g in graph_results if g["current_or_formula"]["or_overclaims"])

    if n_graphs < 2:
        return {
            "n_graphs": n_graphs,
            "status": "insufficient for cross-graph correlation -- need N>=2 real graphs, have 1",
            "or_overclaim_rate_on_available_graphs": f"{or_overclaim_count}/{n_graphs}",
            "next_real_step": (
                "Pull real settled-outcome data for at least one more thesis "
                "(WC mutex-arb/late-goal/favorite-fade via the orderbook join, "
                "or Brasileirão) and add it to GRAPHS -- no code change needed "
                "beyond that."
            ),
        }

    real_rates = [g["real_win_rate"] for g in graph_results]
    or_upper_bounds = [g["current_or_formula"]["final_bounds"][1] for g in graph_results]
    and_upper_bounds = [g["alternative_and_formula"]["final_bounds"][1] for g in graph_results]

    def pearson(xs, ys):
        n = len(xs)
        mx, my = statistics.mean(xs), statistics.mean(ys)
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
        sy = (sum((y - my) ** 2 for y in ys)) ** 0.5
        return cov / (sx * sy) if sx > 0 and sy > 0 else None

    return {
        "n_graphs": n_graphs,
        "or_overclaim_rate": f"{or_overclaim_count}/{n_graphs}",
        "or_upper_bound_vs_real_win_rate_correlation": pearson(real_rates, or_upper_bounds),
        "and_upper_bound_vs_real_win_rate_correlation": pearson(real_rates, and_upper_bounds),
        "interpretation": (
            "A well-calibrated formula's upper bound should track real win rate "
            "positively and closely across graphs. Correlation alone doesn't "
            "confirm magnitude match -- check final_bounds against real_win_rate "
            "per graph too, not just the correlation coefficient."
        ),
    }


def main():
    graph_results = [run_one_graph(g) for g in GRAPHS]
    agg = aggregate(graph_results)

    result = {
        "study_type": "multi_graph_calibration_study",
        "extends": "imst_ground_truth_calibration_test.py (Approach A, single-graph)",
        "approach": "Approach B per that script's honest_limit field -- generalized machinery, real data pending expansion",
        "graphs": graph_results,
        "aggregate": agg,
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = OUTPUT_DIR / f"multi-graph-calibration-{timestamp}.json"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Graphs run: {len(GRAPHS)}")
    for g in graph_results:
        print(f"\n{g['graph_id']}: n={g['n_candidates']}, real_win_rate={g['real_win_rate']:.3f}")
        print(f"  OR:  {g['current_or_formula']['final_bounds']}  {g['current_or_formula']['final_state']}"
              f"{'  [OVERCLAIMS]' if g['current_or_formula']['or_overclaims'] else ''}")
        print(f"  AND: {g['alternative_and_formula']['final_bounds']}  {g['alternative_and_formula']['final_state']}")

    print(f"\n--- Aggregate ({agg['n_graphs']} graph(s)) ---")
    print(json.dumps(agg, indent=2))
    print(f"\nWritten to: {output_path}")


if __name__ == "__main__":
    main()
