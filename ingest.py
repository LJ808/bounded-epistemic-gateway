#!/usr/bin/env python3
# ---
# title: Ingest
# type: code
# status: active
# vault: TRC
# date: 2026-06-30
# tags: []
# ---
"""
E-Prime Ingestion + Assessment Tool — FLF Submission
=====================================================

Two-layer architecture (revised 2026-06-30, after FLF early-feedback review
named the original single-pass version "rhetoric linting" -- ingestion and
assessment fused with no separable structure or checking step):

    Ingestion Layer  -- ingest_claim()  -- mechanical E-Prime rewrite only
    Assessment Layer -- assess_claim()  -- takes Ingestion Layer output as
                                            its required input, runs the
                                            checkable analysis/ambiguity/
                                            adversarial pass against it

See SYNTHESIS/two-layer-architecture-v1.md for the assessment-layer criteria
each Assessment output must satisfy.

NOTE ON A SECOND, DIFFERENT "TWO-LAYER" PROPOSAL: literature-engagement-
addendum-v1.md separately proposes a generation/disclosure split -- a shallow
filler-word ban for generation-stage synthesis (per Jehu-Appiah 2026), E-Prime
reserved for disclosure-stage rewriting. That split cuts along a different
axis than the Ingestion/Assessment split above, and the addendum named it as
an untested, falsifiable proposal, not yet built. This file's
COMPARE-FILLER-BAN HARNESS section below builds the apparatus for that test --
it does not run it. No ANTHROPIC_API_KEY exists in the environment that wrote
this; running the comparison and reporting a real result counts as next-steps work,
named explicitly in the submission as something this proposal would execute
if it advances.

QUICK START:

    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=your_key_here
    python3 ingest.py "There is a positive association between egg consumption and CVD risk"

    # Run the Ingestion Layer alone, no Assessment Layer call:
    python3 ingest.py --ingest-only "There is a positive association..."

    # Run the generation/disclosure comparison harness (needs a real API key --
    # the falsifiable test literature-engagement-addendum-v1.md names
    # as unresolved; --demo shows pre-recorded illustrative output instead):
    python3 ingest.py --compare-filler-ban "There is a positive association..."

No API key? Run with --demo to see pre-recorded output from all modes
without making a live call.
"""

import argparse
import os
import re
import sys

import yaml

# ---------------------------------------------------------------------------
# INGESTION LAYER -- mechanical only. No interpretation, no flagged ambiguity,
# no adversarial reading. Same prompt, zero per-source tuning.
# ---------------------------------------------------------------------------

INGESTION_PROMPT = """You are an E-Prime ingestion system. Given an original claim or quote from a source, produce only:

1. The verbatim original quote
2. An E-Prime rewrite that eliminates "is/are/was/were/be/being/been" and forces numerical/structural specificity into the sentence

Do not analyze, flag ambiguity, or interpret. This is a mechanical pass only --
the rewrite must preserve the source's actual content while removing every
form of "to be."

Output as valid YAML only. No markdown fences. No preamble.

Schema:
-------
original_quote: |
  [verbatim source text]

e_prime_rewrite: |
  [rewritten without any form of "to be", with numbers and specifics forced into view]
"""

DEMO_INGESTION_OUTPUT = {
    "original_quote": "There is a dose-response positive association between egg consumption and the risk of CVD and diabetes",
    "e_prime_rewrite": "Egg intake correlates with CVD risk at RR 1.19 (CI 1.02-1.38) and diabetes at RR 1.68 (CI 1.41-2.00), pooled across 14 studies, n=320,778.",
}

# ---------------------------------------------------------------------------
# ASSESSMENT LAYER -- takes an Ingestion Layer output as required input.
# Runs the checkable analysis/ambiguity/adversarial pass against it. See
# SYNTHESIS/two-layer-architecture-v1.md for the three pass/fail criteria
# this prompt encodes.
#
# Two prompt variants exist: an unconstrained default, and a filler-word-
# banned variant for the comparison harness below. The Assessment Layer's
# prose counts as generation-stage work under literature-engagement-
# addendum-v1.md's framing (new synthesis, not a rewrite of an existing
# claim) -- which is exactly why the addendum's generation/disclosure
# distinction applies here and not to the Ingestion Layer above.
# ---------------------------------------------------------------------------

ASSESSMENT_PROMPT = """You are an E-Prime assessment system. You receive an
Ingestion Layer output (an original quote plus its E-Prime rewrite) and run
three checks against it. You do not alter the ingestion output. Produce:

1. Analysis -- name the specific word or phrase the E-Prime constraint forced
   out of the original sentence, then state what that word was hiding (a
   missing number, mechanism, or direction of causation). Gesturing at "more
   nuance" without naming the hidden item fails this check.
2. Ambiguity Flags -- state what neither the original source nor the rewrite
   resolves. A gap the rewrite itself already answers does not belong here.
3. Adversarial Interpretation -- give two readings: how a reader motivated to
   dismiss the claim could misuse the rewrite, and how a reader motivated to
   accept it could misuse the rewrite. One-sided answers fail this check.
4. Confidence Assessment -- integer 1-5. 5 = motivated misreading now requires
   visibly adding language. 1 = rewrite barely changes readability.

Output as valid YAML only. No markdown fences. No preamble.

Schema:
-------
analysis: |
  [names the specific hidden item; 2-3 sentences]

ambiguity_flags: |
  [gaps surviving the rewrite intact, not gaps the rewrite already closed]

adversarial_interpretation: |
  [both a dismiss-motivated and an accept-motivated misreading]

confidence_assessment: |
  [integer 1-5]

Ingestion Layer output to assess:
---------------------------------
original_quote: {original_quote}

e_prime_rewrite: {e_prime_rewrite}
"""

# Filler-word list matches Jehu-Appiah (2026)'s description of its weakest-
# logical-content condition: words carrying no logical-inference role at all
# (the paper names "very" and "just" directly as examples; the rest below
# extend the same category -- intensifiers/hedges with no inferential work).
FILLER_BAN_WORDS = (
    "very", "just", "really", "actually", "basically",
    "literally", "essentially", "simply", "quite", "rather",
)

ASSESSMENT_PROMPT_FILLER_BANNED = ASSESSMENT_PROMPT + """

Additional constraint on this response: do not use any of the following
words anywhere in your output: """ + ", ".join(f'"{w}"' for w in FILLER_BAN_WORDS) + """.
This is a vocabulary ban only -- it does not require E-Prime. Write naturally
within that restriction.
"""

DEMO_ASSESSMENT_OUTPUT = {
    "analysis": "The rewrite forces a number into a sentence that originally needed none. 'There is an association' cannot survive E-Prime without specifying direction, magnitude, and confidence interval, which become mandatory rather than optional once 'is' disappears.",
    "ambiguity_flags": "'Association' leaves causal direction unaddressed -- neither the source nor the rewrite resolves whether egg consumption causes CVD or reflects a shared upstream factor.",
    "adversarial_interpretation": "A reader motivated to dismiss this finding could note the pooled analysis lacks the same covariate adjustment as competing cohort studies. A reader motivated to accept it could ignore that 'dose-response' oversells what a highest-vs-lowest comparison shows.",
    "confidence_assessment": 4,
}

DEMO_ASSESSMENT_OUTPUT_FILLER_BANNED = {
    "analysis": "The rewrite replaces 'there is an association' with a directional, numbered claim. The original sentence stated no magnitude and no confidence interval; the rewrite supplies both, because E-Prime cannot carry 'is' without naming what stands behind it.",
    "ambiguity_flags": "Causal direction remains unstated. Neither the source nor the rewrite specifies whether egg consumption produces the CVD risk or whether both track a shared upstream factor.",
    "adversarial_interpretation": "A reader who wants to dismiss this finding can point to the missing covariate adjustment, absent here and present in the competing cohort study. A reader who wants to accept it can overlook how much the dose-response framing claims, given a two-point comparison rather than a full dose curve.",
    "confidence_assessment": 4,
}


FALLACY_CATEGORIES = {
    "structural_and_formal": [
        "Circular argument", "False choice", "Part-to-whole mixup",
        "Word-shift", "Non sequitur",
    ],
    "causal_and_statistical": [
        "False cause", "Rushed conclusion", "Survivorship bias",
        "Ignoring the base rate", "Texas sharpshooter", "Gambler's fallacy",
    ],
    "persuasion_instead_of_evidence": [
        "Appeal to authority", "Personal attack", "Origin attack",
        "Straw man", "Red herring", "Bandwagon", "Tu quoque",
    ],
    "shifting_the_boundaries": [
        "Slippery slope", "No true Scotsman", "Motte-and-bailey",
        "Appeal to nature", "Sunk cost", "False equivalence",
        "Appeal to ignorance",
    ],
}

SCREEN_PROMPT = "You are a Fallacy-Screen system checking an Ingestion Layer output for a broken argument in the rewrite, against 25 named categories across 4 groups (structural_and_formal, causal_and_statistical, persuasion_instead_of_evidence, shifting_the_boundaries). Output YAML with fallacy_found, category, group_tag, location, direction_of_error, explanation. Ingestion Layer output: original_quote={original_quote} e_prime_rewrite={e_prime_rewrite}"

DEMO_SCREEN_OUTPUT = {
    "fallacy_found": "no",
    "category": "none",
    "group_tag": "not applicable",
    "location": "not applicable",
    "direction_of_error": "not applicable",
    "explanation": "The rewrite states a correlation with a magnitude and a confidence interval, and does not assert causation, independence, or authority beyond what the pooled sample supports. Checked against all 25 categories; none apply.",
}

# ---------------------------------------------------------------------------
# OPEN-ENDED CHECK -- next-steps-v1.md's third priority. Fallacy-Screen above
# only catches the 25 named categories. This step asks one further, unbound
# question regardless of category match: does the conclusion actually follow
# from its stated reasons? A fixed list, no matter how long, stays closed by
# definition -- this question exists to catch what the list can't yet name.
# ---------------------------------------------------------------------------

OPEN_ENDED_PROMPT = "You are an Open-Ended Argument Check, the step named third in SYNTHESIS/next-steps-v1.md. Fallacy-Screen already checked this rewrite against 25 named categories -- this step asks one further, unbound question, independent of that list: does the stated conclusion actually follow from the stated reasons, whether or not the gap matches any named category? A fixed list, no matter how long, stays closed by definition -- this question exists to catch what the list can't yet name. Output YAML with argument_holds (yes/no), issue_found (state the actual gap in the reasoning in your own words if argument_holds is no, or 'none' if yes -- do not force it into one of the 25 named categories even if it resembles one), direction_of_error (whether the gap makes the claim look more convincing than it should, or a rebuttal of the claim look more convincing than it should, or 'not applicable' if argument_holds is yes), explanation. Ingestion Layer output: original_quote={original_quote} e_prime_rewrite={e_prime_rewrite}"

DEMO_OPEN_ENDED_OUTPUT = {
    "argument_holds": "yes",
    "issue_found": "none",
    "direction_of_error": "not applicable",
    "explanation": "The rewrite's conclusion (a correlation of stated magnitude and confidence interval) follows directly from its stated reasons (pooled sample size, dose-response pattern). No unnamed reasoning gap found underneath the 25 named categories already checked.",
}


def strip_markdown_fences(text: str) -> str:
    """Defensively strip a fenced-code wrapper (triple backtick + optional yaml tag)
    if the model adds one despite the prompt explicitly forbidding it. No-op on
    already-clean YAML."""
    text = text.strip()
    match = re.match(r"^```(?:yaml|yml)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if match:
        return match.group(1)
    return text


def count_filler_words(text: str, word_list=FILLER_BAN_WORDS) -> dict:
    """Compliance check for the filler-ban condition -- counts whether any
    banned word actually leaked into a generated output, case-insensitive,
    whole-word match only. Used by the comparison harness to verify the
    constraint held, not assumed from the prompt alone."""
    counts = {}
    for word in word_list:
        pattern = r"\b" + re.escape(word) + r"\b"
        hits = len(re.findall(pattern, text, re.IGNORECASE))
        if hits:
            counts[word] = hits
    return counts


def _call_model(prompt: str) -> dict:
    """Shared API call + YAML parse, used by both layers."""
    try:
        import anthropic
    except ImportError:
        print(
            "Missing dependency. Run: pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "No ANTHROPIC_API_KEY set. Run with --demo to see example output "
            "without an API key, or set:\n  export ANTHROPIC_API_KEY=your_key_here",
            file=sys.stderr,
        )
        sys.exit(1)

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text
    cleaned_text = strip_markdown_fences(response_text)

    try:
        result = yaml.safe_load(cleaned_text)
    except yaml.YAMLError as e:
        print(f"YAML parse error even after fence-stripping: {e}", file=sys.stderr)
        print(f"Raw model response (unmodified):\n{response_text}", file=sys.stderr)
        print(
            "\nThe model didn't return parseable YAML. Try re-running -- "
            "this is a model-output issue, not a script bug.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not isinstance(result, dict):
        print(
            f"Parsed YAML but got {type(result).__name__}, not a dict. "
            f"Raw model response:\n{response_text}",
            file=sys.stderr,
        )
        sys.exit(1)

    return result


def ingest_claim(source_text: str) -> dict:
    """Ingestion Layer. Mechanical rewrite only -- no analysis, no ambiguity
    flags, no adversarial reading. Returns original_quote + e_prime_rewrite."""
    return _call_model(f"{INGESTION_PROMPT}\n\nSource claim to ingest:\n\n{source_text}")


def assess_claim(ingestion_output: dict, filler_ban: bool = False) -> dict:
    """Assessment Layer. Requires an Ingestion Layer output as input -- refuses
    to run on raw source text directly, since the assessment pass checks the
    rewrite, not the original. Returns analysis + ambiguity_flags +
    adversarial_interpretation + confidence_assessment.

    filler_ban=True selects the constrained prompt variant -- the generation-
    stage constraint literature-engagement-addendum-v1.md proposes, distinct
    from the Ingestion Layer's E-Prime constraint above."""
    if "original_quote" not in ingestion_output or "e_prime_rewrite" not in ingestion_output:
        print(
            "assess_claim() requires an Ingestion Layer output "
            "(original_quote + e_prime_rewrite). Run ingest_claim() first.",
            file=sys.stderr,
        )
        sys.exit(1)

    template = ASSESSMENT_PROMPT_FILLER_BANNED if filler_ban else ASSESSMENT_PROMPT
    prompt = template.format(
        original_quote=ingestion_output["original_quote"],
        e_prime_rewrite=ingestion_output["e_prime_rewrite"],
    )
    return _call_model(prompt)


def screen_claim(ingestion_output: dict) -> dict:
    """Fallacy-Screen Layer. Requires an Ingestion Layer output as input --
    same contract as assess_claim() -- and sits between Ingestion and
    Assessment in the pipeline, per SYNTHESIS/fallacy-screen-layer-v1.md.
    Checks the rewrite (not the raw source) for a broken argument across 25
    named categories in 4 groups. Returns fallacy_found + category +
    group_tag + location + direction_of_error + explanation.

    Honest limitation, stated in the same file: this only catches the 25
    named categories. An uncatalogued 26th form would still slip through."""
    if "original_quote" not in ingestion_output or "e_prime_rewrite" not in ingestion_output:
        print(
            "screen_claim() requires an Ingestion Layer output "
            "(original_quote + e_prime_rewrite). Run ingest_claim() first.",
            file=sys.stderr,
        )
        sys.exit(1)

    prompt = SCREEN_PROMPT.format(
        original_quote=ingestion_output["original_quote"],
        e_prime_rewrite=ingestion_output["e_prime_rewrite"],
    )
    return _call_model(prompt)


def open_check_claim(ingestion_output: dict) -> dict:
    """Open-Ended Check. Requires an Ingestion Layer output as input -- same
    contract as screen_claim() and assess_claim() -- and sits after
    Fallacy-Screen in the pipeline, per SYNTHESIS/next-steps-v1.md step
    three. Fallacy-Screen only catches the 25 named categories; this step
    asks one further, unbound question regardless of category match: does
    the conclusion actually follow from its stated reasons? Returns
    argument_holds + issue_found + direction_of_error + explanation.

    This step exists specifically to catch what a fixed list, by
    definition, can never fully cover -- see fallacy-screen-layer-v1.md's
    stated limitation, and next-steps-v1.md's framing of this exact step."""
    if "original_quote" not in ingestion_output or "e_prime_rewrite" not in ingestion_output:
        print(
            "open_check_claim() requires an Ingestion Layer output "
            "(original_quote + e_prime_rewrite). Run ingest_claim() first.",
            file=sys.stderr,
        )
        sys.exit(1)

    prompt = OPEN_ENDED_PROMPT.format(
        original_quote=ingestion_output["original_quote"],
        e_prime_rewrite=ingestion_output["e_prime_rewrite"],
    )
    return _call_model(prompt)


def compare_filler_ban(ingestion_output: dict) -> dict:
    """COMPARE-FILLER-BAN HARNESS -- the falsifiable test literature-
    engagement-addendum-v1.md names as unresolved: does a generation-stage
    filler-word ban change what the Assessment Layer surfaces, compared to
    an unconstrained run against the same Ingestion Layer output?

    Runs assess_claim() twice against the same ingestion output -- once
    unconstrained, once filler-banned -- and returns both outputs plus a
    compliance check confirming the ban actually held (not assumed from the
    prompt instruction alone). This function makes two live API calls; it
    requires ANTHROPIC_API_KEY and is not exercised by --demo, which prints
    pre-recorded illustrative output instead."""
    unconstrained = assess_claim(ingestion_output, filler_ban=False)
    filler_banned = assess_claim(ingestion_output, filler_ban=True)

    compliance = {}
    for key, text in filler_banned.items():
        if isinstance(text, str):
            hits = count_filler_words(text)
            if hits:
                compliance[key] = hits

    return {
        "unconstrained": unconstrained,
        "filler_banned": filler_banned,
        "filler_ban_compliance_check": compliance or "clean -- no banned words found in filler_banned output",
    }


def main():
    parser = argparse.ArgumentParser(
        description="E-Prime ingestion + assessment: two separately-callable layers matching the flf-vault schema."
    )
    parser.add_argument(
        "source_text",
        nargs="?",
        help="The original claim or quote to ingest (wrap in quotes).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Print pre-recorded example output from both layers, no API key needed.",
    )
    parser.add_argument(
        "--ingest-only",
        action="store_true",
        help="Run the Ingestion Layer alone and stop -- demonstrates the layers run independently.",
    )
    parser.add_argument(
        "--compare-filler-ban",
        action="store_true",
        help="Run the generation/disclosure comparison harness from literature-engagement-addendum-v1.md (2 live API calls). Use with --demo to see illustrative output without a key.",
    )
    parser.add_argument(
        "--no-screen",
        action="store_true",
        help="Skip the Fallacy-Screen Layer and run only Ingestion + Assessment (the pre-existing two-layer pipeline).",
    )
    parser.add_argument(
        "--no-open-check",
        action="store_true",
        help="Skip the Open-Ended Check and run only Ingestion + Fallacy-Screen + Assessment.",
    )
    args = parser.parse_args()

    if args.demo:
        if args.ingest_only:
            print(yaml.dump(DEMO_INGESTION_OUTPUT, default_flow_style=False, sort_keys=False))
        elif args.compare_filler_ban:
            print("--- Ingestion Layer ---")
            print(yaml.dump(DEMO_INGESTION_OUTPUT, default_flow_style=False, sort_keys=False))
            print("--- Assessment Layer: unconstrained ---")
            print(yaml.dump(DEMO_ASSESSMENT_OUTPUT, default_flow_style=False, sort_keys=False))
            print("--- Assessment Layer: filler-banned ---")
            print(yaml.dump(DEMO_ASSESSMENT_OUTPUT_FILLER_BANNED, default_flow_style=False, sort_keys=False))
            print("--- Compliance check (filler-banned output) ---")
            print("(demo mode -- not computed against real model output)")
        else:
            print("--- Ingestion Layer ---")
            print(yaml.dump(DEMO_INGESTION_OUTPUT, default_flow_style=False, sort_keys=False))
            if not args.no_screen:
                print("--- Fallacy-Screen Layer ---")
                print(yaml.dump(DEMO_SCREEN_OUTPUT, default_flow_style=False, sort_keys=False))
            if not args.no_open_check:
                print("--- Open-Ended Check ---")
                print(yaml.dump(DEMO_OPEN_ENDED_OUTPUT, default_flow_style=False, sort_keys=False))
            print("--- Assessment Layer ---")
            print(yaml.dump(DEMO_ASSESSMENT_OUTPUT, default_flow_style=False, sort_keys=False))
        return

    if not args.source_text:
        parser.print_help()
        sys.exit(1)

    print("Running Ingestion Layer...", file=sys.stderr)
    ingestion_result = ingest_claim(args.source_text)
    print(yaml.dump(ingestion_result, default_flow_style=False, sort_keys=False))

    if args.ingest_only:
        return

    if args.compare_filler_ban:
        print("Running Assessment Layer comparison (unconstrained + filler-banned)...", file=sys.stderr)
        comparison = compare_filler_ban(ingestion_result)
        print("--- Assessment Layer: unconstrained ---")
        print(yaml.dump(comparison["unconstrained"], default_flow_style=False, sort_keys=False))
        print("--- Assessment Layer: filler-banned ---")
        print(yaml.dump(comparison["filler_banned"], default_flow_style=False, sort_keys=False))
        print("--- Compliance check (filler-banned output) ---")
        print(comparison["filler_ban_compliance_check"])
        return

    if not args.no_screen:
        print("Running Fallacy-Screen Layer...", file=sys.stderr)
        screen_result = screen_claim(ingestion_result)
        print(yaml.dump(screen_result, default_flow_style=False, sort_keys=False))

    if not args.no_open_check:
        print("Running Open-Ended Check...", file=sys.stderr)
        open_check_result = open_check_claim(ingestion_result)
        print(yaml.dump(open_check_result, default_flow_style=False, sort_keys=False))

    print("Running Assessment Layer...", file=sys.stderr)
    assessment_result = assess_claim(ingestion_result)
    print(yaml.dump(assessment_result, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()
