#!/usr/bin/env python3
"""
Extension 6 (continued, tier-gap round) -- appeal_to_authority bounds test,
baseline vs. source-tier-stated, run against 3 claims chosen specifically
to fill gaps in the sampled epistemic-tier spectrum left after the first
four claims (CFR pilot, Treason, Evangelical Nationalism, Benson):
  - journalism (untested tier): Regime_Change (Haberman/Swan)
  - academic tier, opposite ideological direction from Evangelical
    Nationalism: gramsci-prison-notebooks
  - contested-within-academic-tier: How Democracies Die
Mirrors extension6_appeal_to_authority.py's exact prompt-construction
logic (same AND-shape, same subcondition wording) so results compare
directly against all five prior runs.

Runs directly on Board 2 against RKLLama's own localhost endpoint --
no MCP bridge dependency for the call itself.
"""
import sys
import requests
import yaml

RKLLAMA_URL = "http://127.0.0.1:8080/v1/chat/completions"
RKLLAMA_MODEL = "Qwen2.5-14B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0"
TIMEOUT_SECONDS = 200

CLAIMS = {
    "regime_change": {
        "label": "Regime Change (2026, journalism)",
        "original_quote": (
            "Deep-background reporting confirms the administration's "
            "'Enemy Within' rhetoric functions as governing doctrine, "
            "not rhetorical excess."
        ),
        "e_prime_rewrite": (
            "Swan and Haberman's deep-background reporting establishes "
            "that the administration's 'Enemy Within' rhetoric operates "
            "as governing doctrine, distinct from mere rhetorical "
            "excess."
        ),
        "source_tier_context": (
            "\nAdditional context on this claim's source, real and "
            "relevant to this check: this claim comes from Jonathan "
            "Swan and Maggie Haberman's Regime Change (2026), classified "
            "by this project as journalism -- drawn from over a thousand "
            "deep-background interviews, fact-checked to mainstream "
            "newsroom standards, but not academic or peer-reviewed. "
            "Deep-background sourcing means specific claims trace to "
            "named or anonymous insiders whose motives cannot be "
            "independently verified.\n"
        ),
    },
    "gramsci": {
        "label": "Prison Notebooks (Gramsci, academic -- opposite ideological direction from Evangelical Nationalism)",
        "original_quote": (
            "Ruling-class power in modern societies rests primarily on "
            "winning ideological consent through civil society rather "
            "than on coercive force."
        ),
        "e_prime_rewrite": (
            "Gramsci's theory of cultural hegemony holds that ruling-"
            "class power in modern societies depends primarily on "
            "winning genuine ideological consent through civil society, "
            "not on coercive force alone."
        ),
        "source_tier_context": (
            "\nAdditional context on this claim's source, real and "
            "relevant to this check: this claim comes from Antonio "
            "Gramsci's Prison Notebooks (written 1929-1935), classified "
            "by this project as foundational academic political theory "
            "-- widely-taught and highly influential regardless of "
            "one's own position on Gramsci's underlying Marxism, but "
            "written from an explicit Marxist political commitment, not "
            "a claimed-neutral academic standpoint.\n"
        ),
    },
    "how_democracies_die": {
        "label": "How Democracies Die (Levitsky/Ziblatt, academic tier -- contested-within-tier claim)",
        "original_quote": (
            "American political parties' historical gatekeeping "
            "function -- screening out demagogic candidates before "
            "they could win a national nomination -- broke down "
            "decisively in 2016."
        ),
        "e_prime_rewrite": (
            "Levitsky and Ziblatt argue American political parties' "
            "historical gatekeeping function, which screened out "
            "demagogic candidates before they could win a national "
            "nomination, broke down decisively in 2016."
        ),
        "source_tier_context": (
            "\nAdditional context on this claim's source, real and "
            "relevant to this check: this claim comes from Harvard "
            "political scientists Levitsky and Ziblatt's How "
            "Democracies Die (2018), classified by this project as "
            "mainstream academic political science grounded in "
            "comparative-historical research -- but this specific "
            "claim, the book's application of its framework to the "
            "2016 U.S. election, has been disputed on specifics by "
            "some reviewers and scholars, distinct from the book's "
            "broader comparative-historical framework which is "
            "well-grounded.\n"
        ),
    },
}

AUTHORITY_INVOKED_Q = (
    "Does the argument invoke someone's status, title, or credentials?"
)
NO_EVIDENCE_GIVEN_Q = (
    "Is that status offered in place of evidence, with no supporting "
    "evidence given alongside it?"
)

SUB_INSTR = (
    "1. authority_invoked -- {q1} Score as [lower, upper], each 0.0-1.0. "
    "A confident \"yes\" scores close to [0.9, 1.0]. A confident \"no\" "
    "scores close to [0.0, 0.1]. Genuine uncertainty about THIS specific "
    "question warrants a wide interval reflecting the real balance of "
    "evidence you find -- reason to your own bounds rather than "
    "defaulting to any standard or example range.\n"
    "2. no_evidence_given -- {q2} Score as [lower, upper], each 0.0-1.0. "
    "A confident \"yes\" scores close to [0.9, 1.0]. A confident \"no\" "
    "scores close to [0.0, 0.1]. Genuine uncertainty about THIS specific "
    "question warrants a wide interval reflecting the real balance of "
    "evidence you find -- reason to your own bounds rather than "
    "defaulting to any standard or example range."
).format(q1=AUTHORITY_INVOKED_Q, q2=NO_EVIDENCE_GIVEN_Q)

SCHEMA = (
    "authority_invoked_bounds: [lower, upper]\n\n"
    "authority_invoked_location: |\n"
    "  [the exact phrase carrying this, or \"not applicable\"]\n\n"
    "no_evidence_given_bounds: [lower, upper]\n\n"
    "no_evidence_given_location: |\n"
    "  [the exact phrase carrying this, or \"not applicable\"]\n\n"
)


def build_prompt(claim, tiered):
    header = (
        "You are testing an Ingestion Layer output for one specific "
        "fallacy: Appeal to authority. The fallacy holds only if BOTH "
        "subconditions hold together.\n\n"
    )
    tail = (
        "\n\nOutput as valid YAML only. No markdown fences. No preamble.\n\n"
        "Schema:\n-------\n" + SCHEMA +
        "explanation: |\n  [2-3 sentences on what drove each score]\n\n"
        "Ingestion Layer output to check:\n"
        "---------------------------------\n"
        f"original_quote: {claim['original_quote']}\n\n"
        f"e_prime_rewrite: {claim['e_prime_rewrite']}\n"
    )
    if tiered:
        tail = claim["source_tier_context"] + tail
    return header + SUB_INSTR + tail


def strip_think(text):
    if "</think>" in text:
        text = text.split("</think>", 1)[1].strip()
    return text


def call_rkllama(prompt):
    payload = {
        "model": RKLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.0,
    }
    resp = requests.post(RKLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
    resp.raise_for_status()
    text = strip_think(resp.json()["choices"][0]["message"]["content"])
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("yaml"):
            text = text[4:]
    return yaml.safe_load(text)


def bounds_state(bounds):
    lower, upper = bounds
    if lower > upper:
        return "contradictory"
    if lower >= 0.7:
        return "known-true"
    if upper <= 0.3:
        return "known-false"
    return "unknown"


def combine_and(a, b):
    return [min(a[0], b[0]), min(a[1], b[1])]


def main():
    for key, claim in CLAIMS.items():
        print(f"\n=== {claim['label']} ===", file=sys.stderr)

        print("--- baseline (no source tier stated) ---", file=sys.stderr)
        base_prompt = build_prompt(claim, tiered=False)
        base = call_rkllama(base_prompt)
        base_combined = combine_and(base["authority_invoked_bounds"], base["no_evidence_given_bounds"])
        base_state = bounds_state(base_combined)
        print(f"baseline combined_bounds={base_combined} state={base_state}", file=sys.stderr)
        print(yaml.dump(base, default_flow_style=False, sort_keys=False))

        print("--- source tier stated ---", file=sys.stderr)
        tiered_prompt = build_prompt(claim, tiered=True)
        tiered = call_rkllama(tiered_prompt)
        tiered_combined = combine_and(tiered["authority_invoked_bounds"], tiered["no_evidence_given_bounds"])
        tiered_state = bounds_state(tiered_combined)
        print(f"tiered combined_bounds={tiered_combined} state={tiered_state}", file=sys.stderr)
        print(yaml.dump(tiered, default_flow_style=False, sort_keys=False))

        print(f"\n>>> {key}: baseline={base_state} ({base_combined})  tiered={tiered_state} ({tiered_combined})  shift={'YES' if base_state != tiered_state else 'no'}", file=sys.stderr)


if __name__ == "__main__":
    main()
