#!/usr/bin/env python3
"""
Extension 6 (continued) -- appeal_to_authority bounds test, baseline vs.
source-tier-stated, run against 3 more labeled Trumpian-folder claims
spanning three distinct epistemic tiers: movement propaganda (Treason),
peer-reviewed academic (Evangelical Nationalism), and tertiary/Wikipedia
reference (Benson). Mirrors extension6_appeal_to_authority.py's exact
prompt-construction logic (build_bounds_prompt() for appeal_to_authority,
same AND-shape, same subcondition wording) so results compare directly
against the original CFR-claim run.

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
    "treason": {
        "label": "None Dare Call It Treason (1964, movement propaganda)",
        "original_quote": (
            "The U.S. government has systematically retreated from "
            "confronting global communism, and this retreat amounts to "
            "institutional betrayal rather than legitimate policy "
            "disagreement."
        ),
        "e_prime_rewrite": (
            "John Stormer's 1964 tract frames decades of Cold War policy "
            "choices -- aid programs, diplomatic engagement, disarmament "
            "efforts -- as evidence of institutional betrayal, not as "
            "legitimate policy disagreement."
        ),
        "source_tier_context": (
            "\nAdditional context on this claim's source, real and "
            "relevant to this check: this claim comes from John Stormer's "
            "None Dare Call It Treason (1964), classified by this project "
            "as movement propaganda -- functioned as an electoral "
            "mobilization tool for the Goldwater insurgency, not neutral "
            "analysis. Its 'institutional betrayal' framing reflects a "
            "partisan political argument, not a documented historical "
            "finding.\n"
        ),
    },
    "evangelical": {
        "label": "American Evangelical Nationalism (2023, peer-reviewed academic)",
        "original_quote": (
            "Trump's 2016 election marks the moment evangelicalism "
            "shifted from a religiously conservative force into a full "
            "nationalist movement."
        ),
        "e_prime_rewrite": (
            "Zhou's 2023 peer-reviewed analysis identifies Trump's 2016 "
            "election as the specific inflection point where "
            "evangelicalism completed a transition from religious "
            "conservatism to full nationalism, rather than merely forming "
            "an alliance of convenience."
        ),
        "source_tier_context": (
            "\nAdditional context on this claim's source, real and "
            "relevant to this check: this claim comes from Shaoqing "
            "Zhou's peer-reviewed paper in the International Journal of "
            "Anthropology and Ethnology (2023), classified by this "
            "project as the most methodologically rigorous non-fiction "
            "source in its folder -- an academic analysis with a stated "
            "theoretical frame (civic vs. ethnic nationalism), not "
            "advocacy or movement propaganda.\n"
        ),
    },
    "benson": {
        "label": "George S. Benson (Wikipedia, tertiary reference)",
        "original_quote": (
            "Benson built and ran the National Education Program, a "
            "large-scale propaganda operation producing anticommunist "
            "cartoons, Freedom Forums for business audiences, and "
            "national lecture tours."
        ),
        "e_prime_rewrite": (
            "Benson's National Education Program, documented via "
            "Wikipedia's tertiary-source account, produced anticommunist "
            "cartoons, ran business-audience 'Freedom Forums,' and "
            "conducted national lecture tours as a coordinated propaganda "
            "operation."
        ),
        "source_tier_context": (
            "\nAdditional context on this claim's source, real and "
            "relevant to this check: this claim comes from a Wikipedia "
            "biographical article, classified by this project as a "
            "tertiary reference source -- the underlying biographical "
            "facts sit on reasonably solid documentary ground, though "
            "Benson himself (the subject) produced propaganda; treat his "
            "movement's own framing with appropriate caution, distinct "
            "from the fully-discounted treatment given a primary "
            "propaganda text.\n"
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
