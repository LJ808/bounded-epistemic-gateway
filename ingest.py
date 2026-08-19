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


# ---------------------------------------------------------------------------
# NEURO-SYMBOLIC PILOT -- SYNTHESIS/neuro-symbolic-fallacy-screen-v1.md's
# Approach C: no new logic-neuron library, no change to screen_claim()'s
# existing call pattern. Same one-call-per-check shape as every function
# above -- the only change is what the schema asks for, and how the two
# returned numbers combine. Scoped to one category only (circular argument),
# per that file's own "pilot one category first" plan. Not yet extended to
# the other 25 categories screen_claim() already covers.
#
# Circular argument decomposes into two checkable subconditions:
#   (1) the conclusion appears again, restated, as one of the premises
#   (2) no independent support for the conclusion exists anywhere else
# Both subconditions get their own bounds pair -- a [lower, upper] truth
# interval, not a single yes/no -- straight from the model. Combining them
# uses a plain, documented simplification (Godel/min-based AND: the
# combined lower bound is the smaller of the two lower bounds, same for
# upper) -- not IBM's actual LNN library or its full Lukasiewicz-style
# combination rules. This pilot tests whether bounded, two-subcondition
# output changes anything real about the check. It does not claim to
# reproduce LNN's real math.
# ---------------------------------------------------------------------------

def build_reference_passage_section(reference_passage: str = None) -> str:
    """Builds the optional cross-passage context block circular_argument_screen()
    and fallacy_bounds_screen() can now accept. Real gap found and logged
    2026-08-13 (MEMORY.md): every neuro-symbolic function took exactly one
    quote/rewrite pair, with no way to test whether that quote's conclusion
    restates a premise stated elsewhere in the same source document --
    exactly the shape a real circular-argument case can take across a
    multi-page source. When given, this section asks the model to score
    against the quote under test plus this passage together, not the quote
    alone. Returns an empty string (a no-op insertion) when no
    reference_passage is given, preserving every existing call site's exact
    prior behavior."""
    if not reference_passage:
        return ""
    return (
        "\nAdditional context, real and relevant to this check: elsewhere "
        "in the same source document (not part of the quote under test "
        "itself), the following passage appears. Use it only to judge "
        "whether the quote under test restates something already "
        "established there as a premise -- score against the quote under "
        "test plus this context together, not the quote alone.\n\n"
        "Reference passage from elsewhere in the source:\n"
        "-------------------------------------------------\n"
        + reference_passage + "\n"
    )


CIRCULAR_ARGUMENT_PROMPT = """You are testing an Ingestion Layer output for one specific fallacy: circular argument. A circular argument restates its conclusion as one of its own premises, offering no independent support.

Circular argument decomposes into two separate subconditions. Score each one on a bounds pair, not a single yes/no:

1. premise_restated -- does the conclusion appear again, restated in different words, as one of the argument's own premises? Score as [lower, upper], each 0.0-1.0. A confident "yes" scores close to [0.9, 1.0]. A confident "no" scores close to [0.0, 0.1]. Genuine uncertainty about a specific claim warrants a wide interval reflecting the real balance of evidence you find in THIS argument -- reason to your own bounds from what the text actually supports, rather than defaulting to any standard or example range.
2. no_independent_support -- does the argument offer zero evidence for its conclusion beyond the restated premise? Same bounds-pair scoring, same instruction against defaulting to a standard range.
{reference_passage_section}
Output as valid YAML only. No markdown fences. No preamble.

Schema:
-------
premise_restated_bounds: [lower, upper]

premise_restated_location: |
  [the exact phrase carrying this, or "not applicable"]

no_independent_support_bounds: [lower, upper]

no_independent_support_location: |
  [the exact phrase carrying this, or "not applicable"]

explanation: |
  [2-3 sentences on what drove each score]

Ingestion Layer output to check:
---------------------------------
original_quote: {original_quote}

e_prime_rewrite: {e_prime_rewrite}
"""


def combine_bounds_and(bounds_a, bounds_b):
    """Combine two [lower, upper] bounds pairs under AND, using a plain
    Godel/min-based rule -- a documented simplification, not IBM's LNN
    library or its full combination semantics. See
    SYNTHESIS/neuro-symbolic-fallacy-screen-v1.md."""
    lower = min(bounds_a[0], bounds_b[0])
    upper = min(bounds_a[1], bounds_b[1])
    return [lower, upper]


def combine_bounds_or(bounds_a, bounds_b):
    """Combine two [lower, upper] bounds pairs under OR, using a plain
    Godel/max-based rule -- the OR-shape counterpart to combine_bounds_and()
    above. Used only for categories FALLACY_SHAPE_DATA tags shape='or'
    (currently appeal_to_ignorance alone -- see
    SYNTHESIS/neuro-symbolic-fallacy-shapes-v1.md for the full
    shape-by-category breakdown)."""
    lower = max(bounds_a[0], bounds_b[0])
    upper = max(bounds_a[1], bounds_b[1])
    return [lower, upper]


def bounds_state(bounds):
    """Reads a [lower, upper] bounds pair into one of four states, per
    neuro-symbolic-fallacy-screen-v1.md's four-state framing: known-true,
    known-false, unknown, contradictory."""
    lower, upper = bounds
    if lower > upper:
        return "contradictory"
    if lower >= 0.7:
        return "known-true"
    if upper <= 0.3:
        return "known-false"
    return "unknown"


# Fixed Ingestion Layer output for the three claims
# fallacy-screen-worked-examples-v1.md originally tested, pulled verbatim
# from each claim file's own Ingestion Layer section -- lets --circular-pilot
# run in live mode without needing ingest_claim() re-run first.
PILOT_CLAIM_INGESTION_OUTPUTS = {
    "eggs-003": {
        "original_quote": "There was no evidence of interaction by diabetic status",
        "e_prime_rewrite": "The diabetic-subgroup HR (1.33, CI 0.72-2.46) and non-diabetic HR (0.96, CI 0.33-2.76) overlapped enough that the formal interaction test failed to reach significance.",
    },
    "covid-003": {
        "original_quote": "COVID's furin cleavage site is a mess... a bizarre furin cleavage site which no human has ever used before, and which virologists expected to work poorly.",
        "e_prime_rewrite": "No published gain-of-function study used the PRRAR sequence before COVID's emergence; computational modeling after COVID's emergence found PRRAR functions adequately as a furin cleavage site, a finding unavailable to any engineer working before 2019.",
    },
    "blackhole-002": {
        "original_quote": "All these theories predict that these particles would disintegrate immediately. Black holes, therefore, would have no time to start accreting matter and to cause macroscopic effects.",
        "e_prime_rewrite": "The same extra-dimension theoretical framework predicting microscopic black hole formation also predicts Hawking-radiation evaporation on a sub-accretion timescale.",
    },
}

DEMO_CIRCULAR_PILOT_OUTPUTS = {
    "eggs-003": {
        "premise_restated_bounds": [0.05, 0.15],
        "premise_restated_location": "not applicable",
        "no_independent_support_bounds": [0.1, 0.2],
        "no_independent_support_location": "not applicable",
        "circular_argument_bounds": [0.05, 0.15],
        "state": "known-false",
        "explanation": "The rewrite states a real interaction test result (HR 1.33 vs 0.96, overlapping CIs) -- the conclusion doesn't restate a premise, it derives from numbers stated once. This claim's already-known issue (rushed conclusion, per fallacy-screen-worked-examples-v1.md) sits outside this pilot's scope -- circular argument alone, tested here, comes back clean.",
    },
    "covid-003": {
        "premise_restated_bounds": [0.0, 0.1],
        "premise_restated_location": "not applicable",
        "no_independent_support_bounds": [0.1, 0.2],
        "no_independent_support_location": "not applicable",
        "circular_argument_bounds": [0.0, 0.1],
        "state": "known-false",
        "explanation": "The rewrite argues from a specific, checkable fact (no published pre-2019 study used the PRRAR sequence) toward a conclusion about knowability -- independent support exists, and the conclusion doesn't loop back into its own premise. Consistent with this claim's known clean result across all 26 existing categories.",
    },
    "blackhole-002": {
        "premise_restated_bounds": [0.2, 0.4],
        "premise_restated_location": "The same extra-dimension theoretical framework predicting microscopic black hole formation also predicts Hawking-radiation evaporation on a sub-accretion timescale.",
        "no_independent_support_bounds": [0.15, 0.3],
        "no_independent_support_location": "not applicable",
        "circular_argument_bounds": [0.15, 0.3],
        "state": "unknown",
        "explanation": "The two predictions share one theoretical source, which is real, but the argument doesn't restate its own conclusion as a premise -- it draws two distinct predictions from one shared premise, the exact shape this project already named double-counting, not circular argument. Bounds land in the unknown band rather than known-false, since the shared-premise structure sits close enough to circularity's shape to warrant real caution rather than a confident clean read.",
    },
}


def circular_argument_screen(ingestion_output: dict, reference_passage: str = None) -> dict:
    """Neuro-symbolic pilot -- Approach C from
    SYNTHESIS/neuro-symbolic-fallacy-screen-v1.md. Requires an Ingestion
    Layer output as input, same contract as screen_claim(). Scores two
    subconditions on bounds pairs, combines them under a documented
    Godel/min AND rule, and reads the result into one of four states
    (known-true / known-false / unknown / contradictory) instead of a flat
    yes/no. Scoped to circular argument only -- the other 25 categories in
    screen_claim() stay as-is, unpiloted.

    reference_passage, when given, supplies a second passage from elsewhere
    in the same source document -- closes the real single-quote scope gap
    logged 2026-08-13 (MEMORY.md): every call here previously tested the
    quote in total isolation, unable to represent "this conclusion restates
    a premise stated elsewhere." Optional; omitting it preserves the exact
    single-quote behavior every existing call site already depends on."""
    if "original_quote" not in ingestion_output or "e_prime_rewrite" not in ingestion_output:
        print(
            "circular_argument_screen() requires an Ingestion Layer output "
            "(original_quote + e_prime_rewrite). Run ingest_claim() first.",
            file=sys.stderr,
        )
        sys.exit(1)

    prompt = CIRCULAR_ARGUMENT_PROMPT.format(
        original_quote=ingestion_output["original_quote"],
        e_prime_rewrite=ingestion_output["e_prime_rewrite"],
        reference_passage_section=build_reference_passage_section(reference_passage),
    )
    result = _call_model(prompt)

    combined = combine_bounds_and(
        result["premise_restated_bounds"], result["no_independent_support_bounds"]
    )
    result["circular_argument_bounds"] = combined
    result["state"] = bounds_state(combined)
    return result


# ---------------------------------------------------------------------------
# SHAPE-GROUPED BOUNDS ENGINE -- generalizes circular_argument_screen()'s
# pattern to the other 25 categories in the full 26-category list (all of
# FALLACY_CATEGORIES above, plus double-counting, except circular argument,
# which keeps its own dedicated function above rather than getting folded
# in here). Per SYNTHESIS/neuro-symbolic-fallacy-shapes-v1.md's
# classification pass: almost every category decomposes into two
# AND-linked subconditions, one (appeal_to_ignorance) decomposes into two
# OR-linked alternatives, and one (non_sequitur) doesn't decompose at all
# -- one holistic subcondition. double-counting, the 26th category, came
# from evidence-reasoning tradition, not the classical fallacy tradition
# the other 25 draw from -- originally left unbuilt for that reason (see
# neuro-symbolic-fallacy-shapes-v1.md's original text). Added 2026-08-17,
# scored the same AND way as most of the other 25 (a shared premise across
# two or more conclusions, plus treating those conclusions as independent)
# once checked within one argument's own text, the same single-quote
# contract every other category here already uses -- not forced across two
# separate claims, which is what made it look like a genuinely different
# shape at first.
# ---------------------------------------------------------------------------

FALLACY_SHAPE_DATA = {
    "false_choice": {
        "display_name": "False choice",
        "group_tag": "structural_and_formal",
        "shape": "and",
        "subconditions": [
            {"key": "only_two_presented", "question": "Does the argument present exactly two options as if they exhaust all the real possibilities?"},
            {"key": "more_options_exist", "question": "Do genuine additional options exist that the argument doesn't acknowledge?"},
        ],
    },
    "part_to_whole_mixup": {
        "display_name": "Part-to-whole mixup",
        "group_tag": "structural_and_formal",
        "shape": "and",
        "subconditions": [
            {"key": "property_transferred", "question": "Does the argument assume a property true of the parts must hold for the whole, or the reverse?"},
            {"key": "transfer_unjustified", "question": "Does the argument give no separate justification for that transfer?"},
        ],
    },
    "word_shift": {
        "display_name": "Word-shift",
        "group_tag": "structural_and_formal",
        "shape": "and",
        "subconditions": [
            {"key": "term_repeats", "question": "Does a specific key word or phrase appear more than once in the argument?"},
            {"key": "meaning_shifts", "question": "Does that word's meaning actually differ between its occurrences?"},
        ],
    },
    "non_sequitur": {
        "display_name": "Non sequitur",
        "group_tag": "structural_and_formal",
        "shape": "single",
        "subconditions": [
            {"key": "gap_exists", "question": "Does the conclusion fail to follow from the stated reasons, even though each individual reason may sound true on its own?"},
        ],
    },
    "false_cause": {
        "display_name": "False cause",
        "group_tag": "causal_and_statistical",
        "shape": "and",
        "subconditions": [
            {"key": "correlation_established", "question": "Does the argument establish that two things co-occur or correlate?"},
            {"key": "causation_asserted", "question": "Does the argument then assert one caused the other without ruling out alternative explanations?"},
        ],
    },
    "rushed_conclusion": {
        "display_name": "Rushed conclusion",
        "group_tag": "causal_and_statistical",
        "shape": "and",
        "subconditions": [
            {"key": "narrow_evidence", "question": "Does the argument rely on a small or atypical case as its evidence base?"},
            {"key": "general_claim", "question": "Does the conclusion claim general applicability beyond that narrow case?"},
        ],
    },
    "survivorship_bias": {
        "display_name": "Survivorship bias",
        "group_tag": "causal_and_statistical",
        "shape": "and",
        "subconditions": [
            {"key": "only_survivors_examined", "question": "Does the argument examine only the surviving or successful cases?"},
            {"key": "failures_ignored", "question": "Do failed or non-surviving cases exist that the argument doesn't account for?"},
        ],
    },
    "ignoring_base_rate": {
        "display_name": "Ignoring the base rate",
        "group_tag": "causal_and_statistical",
        "shape": "and",
        "subconditions": [
            {"key": "vivid_example_relied_on", "question": "Does the argument lean on one vivid or exceptional example?"},
            {"key": "base_rate_ignored", "question": "Does a known, more typical base rate get contradicted or go unaddressed?"},
        ],
    },
    "texas_sharpshooter": {
        "display_name": "Texas sharpshooter",
        "group_tag": "causal_and_statistical",
        "shape": "and",
        "subconditions": [
            {"key": "pattern_found_after_fact", "question": "Was the pattern identified only after the data already existed?"},
            {"key": "framed_as_predicted", "question": "Does the argument frame the pattern as if predicted in advance?"},
        ],
    },
    "gamblers_fallacy": {
        "display_name": "Gambler's fallacy",
        "group_tag": "causal_and_statistical",
        "shape": "and",
        "subconditions": [
            {"key": "past_outcomes_cited", "question": "Does the argument cite a string of past, independent outcomes?"},
            {"key": "future_probability_claim", "question": "Does it claim those past outcomes change the odds of the next independent outcome?"},
        ],
    },
    "appeal_to_authority": {
        "display_name": "Appeal to authority",
        "group_tag": "persuasion_instead_of_evidence",
        "shape": "and",
        "subconditions": [
            {"key": "authority_invoked", "question": "Does the argument invoke someone's status, title, or credentials?"},
            {"key": "no_evidence_given", "question": "Is that status offered in place of evidence, with no supporting evidence given alongside it?"},
        ],
    },
    "personal_attack": {
        "display_name": "Personal attack",
        "group_tag": "persuasion_instead_of_evidence",
        "shape": "and",
        "subconditions": [
            {"key": "character_attacked", "question": "Does the argument attack the source's character or person?"},
            {"key": "argument_unaddressed", "question": "Does it leave the source's actual argument unaddressed?"},
        ],
    },
    "origin_attack": {
        "display_name": "Origin attack",
        "group_tag": "persuasion_instead_of_evidence",
        "shape": "and",
        "subconditions": [
            {"key": "origin_cited", "question": "Does the argument dismiss a claim by pointing to where it came from?"},
            {"key": "merits_unevaluated", "question": "Does it leave the claim's actual current merits unevaluated?"},
        ],
    },
    "straw_man": {
        "display_name": "Straw man",
        "group_tag": "persuasion_instead_of_evidence",
        "shape": "and",
        "subconditions": [
            {"key": "position_restated", "question": "Does the argument restate an opposing position?"},
            {"key": "restatement_weaker", "question": "Is that restatement weaker or more extreme than the real position?"},
        ],
    },
    "red_herring": {
        "display_name": "Red herring",
        "group_tag": "persuasion_instead_of_evidence",
        "shape": "and",
        "subconditions": [
            {"key": "irrelevant_topic_introduced", "question": "Does the argument introduce a topic irrelevant to the question at hand?"},
            {"key": "substitutes_for_real_question", "question": "Does that irrelevant topic substitute for actually addressing the real question?"},
        ],
    },
    "bandwagon": {
        "display_name": "Bandwagon",
        "group_tag": "persuasion_instead_of_evidence",
        "shape": "and",
        "subconditions": [
            {"key": "popularity_cited", "question": "Does the argument cite a claim's popularity or widespread acceptance?"},
            {"key": "popularity_as_proof", "question": "Is that popularity offered as the actual support for the claim's truth, not just as context?"},
        ],
    },
    "tu_quoque": {
        "display_name": "Tu quoque",
        "group_tag": "persuasion_instead_of_evidence",
        "shape": "and",
        "subconditions": [
            {"key": "inconsistency_pointed_out", "question": "Does the argument point to the opponent's own inconsistency or hypocrisy?"},
            {"key": "point_unaddressed", "question": "Does it leave the opponent's actual point unaddressed?"},
        ],
    },
    "slippery_slope": {
        "display_name": "Slippery slope",
        "group_tag": "shifting_the_boundaries",
        "shape": "and",
        "subconditions": [
            {"key": "chain_claimed", "question": "Does the argument claim one small step leads to a long chain of consequences?"},
            {"key": "links_unjustified", "question": "Does it fail to show how each step in that chain actually leads to the next?"},
        ],
    },
    "no_true_scotsman": {
        "display_name": "No true Scotsman",
        "group_tag": "shifting_the_boundaries",
        "shape": "and",
        "subconditions": [
            {"key": "counterexample_presented", "question": "Does a counterexample to a general claim appear?"},
            {"key": "definition_narrowed", "question": "Does the argument then narrow its own definition, ad hoc, specifically to exclude that counterexample?"},
        ],
    },
    "motte_and_bailey": {
        "display_name": "Motte-and-bailey",
        "group_tag": "shifting_the_boundaries",
        "shape": "and",
        "subconditions": [
            {"key": "bold_claim_advanced", "question": "Does the argument advance a bold or strong claim at some point?"},
            {"key": "retreats_under_challenge", "question": "Does it retreat to a much weaker, safer claim when challenged, while treating the two as equivalent?"},
        ],
    },
    "appeal_to_nature": {
        "display_name": "Appeal to nature",
        "group_tag": "shifting_the_boundaries",
        "shape": "and",
        "subconditions": [
            {"key": "called_natural", "question": "Does the argument describe something as natural?"},
            {"key": "equated_with_good", "question": "Does it equate that with safe or good, without independent support for that equation?"},
        ],
    },
    "sunk_cost": {
        "display_name": "Sunk cost",
        "group_tag": "shifting_the_boundaries",
        "shape": "and",
        "subconditions": [
            {"key": "investment_cited", "question": "Does the argument cite an amount already invested (time, money, effort)?"},
            {"key": "used_to_justify_forward", "question": "Does it use that past investment to justify the decision going forward, rather than the decision's actual forward-looking merit?"},
        ],
    },
    "false_equivalence": {
        "display_name": "False equivalence",
        "group_tag": "shifting_the_boundaries",
        "shape": "and",
        "subconditions": [
            {"key": "shared_trait_identified", "question": "Does the argument identify one trait two things share?"},
            {"key": "differences_ignored", "question": "Does it treat the two things as equivalent while other relevant differences between them go unaddressed?"},
        ],
    },
    "appeal_to_ignorance": {
        "display_name": "Appeal to ignorance",
        "group_tag": "shifting_the_boundaries",
        "shape": "or",
        "subconditions": [
            {"key": "absence_as_proof", "question": "Does the argument treat an absence of disproof as itself proof the claim holds?"},
            {"key": "absence_as_disproof", "question": "Does the argument treat an absence of proof as itself proof the claim fails?"},
        ],
    },
    "double_counting": {
        "display_name": "Double-counting",
        "group_tag": "causal_and_statistical",
        "shape": "and",
        "subconditions": [
            {"key": "shared_premise", "question": "Do two or more conclusions in the argument derive from one shared underlying premise or source, rather than from genuinely independent evidence?"},
            {"key": "treated_as_independent", "question": "Does the argument treat those conclusions as if they independently corroborate each other, without accounting for the shared premise underneath both?"},
        ],
    },
}


def build_bounds_prompt(category_key: str, ingestion_output: dict, reference_passage: str = None) -> str:
    """Builds a bounds-pair prompt for one fallacy category, per its shape
    entry in FALLACY_SHAPE_DATA. Mirrors CIRCULAR_ARGUMENT_PROMPT's format,
    generalized to any AND/OR/single shape instead of one hardcoded pair.

    reference_passage, when given, supplies a second passage from elsewhere
    in the same source document -- see circular_argument_screen()'s
    docstring for the real single-quote scope gap this closes. Optional;
    omitting it preserves every existing call site's exact prior
    single-quote behavior."""
    entry = FALLACY_SHAPE_DATA[category_key]
    label = entry["display_name"]
    subs = entry["subconditions"]

    shape_note = {
        "and": "The fallacy holds only if BOTH subconditions hold together.",
        "or": "The fallacy holds if EITHER subcondition holds on its own.",
        "single": "This fallacy has one subcondition. Score it directly.",
    }[entry["shape"]]

    sub_instructions = []
    schema_lines = []
    for i, sub in enumerate(subs, start=1):
        sub_instructions.append(
            f"{i}. {sub['key']} -- {sub['question']} Score as [lower, upper], "
            f"each 0.0-1.0. A confident \"yes\" scores close to [0.9, 1.0]. "
            f"A confident \"no\" scores close to [0.0, 0.1]. Genuine "
            f"uncertainty about THIS specific question warrants a wide "
            f"interval reflecting the real balance of evidence you find -- "
            f"reason to your own bounds rather than defaulting to any "
            f"standard or example range."
        )
        schema_lines.append(f"{sub['key']}_bounds: [lower, upper]")
        schema_lines.append("")
        schema_lines.append(f"{sub['key']}_location: |")
        schema_lines.append("  [the exact phrase carrying this, or \"not applicable\"]")
        schema_lines.append("")

    header = (
        f"You are testing an Ingestion Layer output for one specific "
        f"fallacy: {label}. {shape_note}\n\n"
    )
    body = "\n".join(sub_instructions)
    schema = "\n".join(schema_lines)

    template = (
        header + body +
        "\n{reference_passage_section}"
        "\n\nOutput as valid YAML only. No markdown fences. No preamble.\n\n"
        "Schema:\n-------\n" + schema +
        "explanation: |\n  [2-3 sentences on what drove each score]\n\n"
        "Ingestion Layer output to check:\n"
        "---------------------------------\n"
        "original_quote: {original_quote}\n\n"
        "e_prime_rewrite: {e_prime_rewrite}\n"
    )
    return template.format(
        original_quote=ingestion_output["original_quote"],
        e_prime_rewrite=ingestion_output["e_prime_rewrite"],
        reference_passage_section=build_reference_passage_section(reference_passage),
    )


def fallacy_bounds_screen(category_key: str, ingestion_output: dict, reference_passage: str = None) -> dict:
    """Generalized neuro-symbolic pilot -- Approach C, shape-grouped per
    SYNTHESIS/neuro-symbolic-fallacy-shapes-v1.md. Covers all 25 categories
    in FALLACY_SHAPE_DATA (the full 26-category list minus circular
    argument, which keeps its own dedicated circular_argument_screen()
    above). double_counting joined this table 2026-08-17, closing the
    prior 25/26 gap this docstring used to name.
    Combines each category's subcondition bounds under its assigned shape
    (AND, OR, or pass-through for the one single-subcondition category).

    reference_passage, when given, forwards to build_bounds_prompt() -- see
    circular_argument_screen()'s docstring for the real single-quote scope
    gap this closes."""
    if category_key not in FALLACY_SHAPE_DATA:
        print(f"Unknown category: {category_key}", file=sys.stderr)
        sys.exit(1)
    if "original_quote" not in ingestion_output or "e_prime_rewrite" not in ingestion_output:
        print(
            "fallacy_bounds_screen() requires an Ingestion Layer output "
            "(original_quote + e_prime_rewrite). Run ingest_claim() first.",
            file=sys.stderr,
        )
        sys.exit(1)

    entry = FALLACY_SHAPE_DATA[category_key]
    prompt = build_bounds_prompt(category_key, ingestion_output, reference_passage=reference_passage)
    result = _call_model(prompt)

    subs = entry["subconditions"]
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


def demo_bounds_output(category_key: str) -> dict:
    """Pre-recorded demo output for any category in FALLACY_SHAPE_DATA,
    scored against the standard DEMO_INGESTION_OUTPUT (the egg dose-response
    claim) -- not a live model call. Uniformly clean/known-false, matching
    the single generic DEMO_SCREEN_OUTPUT convention above rather than
    hand-authoring 24 separate demo dicts."""
    entry = FALLACY_SHAPE_DATA[category_key]
    subs = entry["subconditions"]
    result = {}
    if entry["shape"] == "single":
        bounds = [0.05, 0.15]
        result[f"{subs[0]['key']}_bounds"] = bounds
        result[f"{subs[0]['key']}_location"] = "not applicable"
        combined = bounds
    else:
        bounds_a = [0.05, 0.15]
        bounds_b = [0.1, 0.2]
        result[f"{subs[0]['key']}_bounds"] = bounds_a
        result[f"{subs[0]['key']}_location"] = "not applicable"
        result[f"{subs[1]['key']}_bounds"] = bounds_b
        result[f"{subs[1]['key']}_location"] = "not applicable"
        combined = (
            combine_bounds_or(bounds_a, bounds_b)
            if entry["shape"] == "or"
            else combine_bounds_and(bounds_a, bounds_b)
        )
    result[f"{category_key}_bounds"] = combined
    result["state"] = bounds_state(combined)
    result["explanation"] = (
        f"Demo placeholder: no {entry['display_name'].lower()} pattern found "
        "against the standard demo claim (egg dose-response). Pre-recorded, "
        "not a live model call."
    )
    return result


# ---------------------------------------------------------------------------
# GENERATIVE FALLACY CHECK -- prototype redesign of open_check_claim(), per
# SYNTHESIS/meta-fallacy-construction-v1.md. Kept as a separate function
# (generative_fallacy_check()) rather than replacing open_check_claim() in
# place -- open_check_claim() stays wired into the default pipeline exactly
# as before; this prototype sits alongside it, reachable only through its
# own --generative-check flag, until Jay decides whether it should replace
# the original.
#
# open_check_claim() asks one flat, holistic question: does the conclusion
# follow from the stated reasons? That's the same shape as non_sequitur
# above -- useful, but not generative. This prototype instead runs two
# stages: (1) identify which reasoning move the argument actually uses
# (authority, analogy, generalization, causal inference, chaining,
# redefinition, evidence aggregation, boundary shift, or an unlisted "other"
# the model names itself), then (2) ask that specific move's own licensing
# question -- the condition the move needs in order to work at all. A move
# that fails its licensing question, and doesn't match any of the 26 named
# categories, becomes a real, logged candidate for a new category -- the
# same honest path double-counting took, not a shortcut around it.
# ---------------------------------------------------------------------------

REASONING_MOVE_TYPES = {
    "authority": {
        "label": "Argument from authority",
        "licensing_question": "Does the argument supply evidence alongside the cited authority, not just the authority's status?",
    },
    "analogy": {
        "label": "Argument from analogy",
        "licensing_question": "Does the shared trait between the two things compared outweigh their other relevant differences?",
    },
    "generalization": {
        "label": "Argument from generalization",
        "licensing_question": "Does the sample the argument generalizes from actually represent the population it draws conclusions about?",
    },
    "causal_inference": {
        "label": "Argument from causal inference",
        "licensing_question": "Does the argument rule out plausible alternative explanations for the observed correlation?",
    },
    "chaining": {
        "label": "Argument from consequences (chaining)",
        "licensing_question": "Does the argument justify each individual link in the chain of consequences, not just the first and the last?",
    },
    "redefinition": {
        "label": "Argument from definitional refinement",
        "licensing_question": "Does any definitional change in the argument happen independent of a counterexample that just appeared?",
    },
    "evidence_aggregation": {
        "label": "Argument from combined evidence",
        "licensing_question": "Do the pieces of evidence the argument combines come from genuinely independent sources?",
    },
    "boundary_shift": {
        "label": "Argument that shifts claim strength",
        "licensing_question": "Does the argument's claim stay the same strength throughout, rather than retreating under challenge and expanding again once the challenge passes?",
    },
}

IDENTIFY_MOVE_PROMPT = """You are identifying which reasoning move an argument primarily uses, as Stage 1 of a two-stage generative fallacy check. This does not check whether the move works -- only what kind of move it is.

Known move types: authority, analogy, generalization, causal_inference, chaining, redefinition, evidence_aggregation, boundary_shift. If the argument's move doesn't fit any of these, choose "other" and name the move yourself, along with the one licensing question that move's own logic requires in order to work.

Output as valid YAML only. No markdown fences. No preamble.

Schema:
-------
move_type: |
  [one of: authority, analogy, generalization, causal_inference, chaining, redefinition, evidence_aggregation, boundary_shift, other]

move_location: |
  [the exact phrase where this move happens]

other_move_label: |
  [only if move_type is "other" -- name the move type yourself; otherwise "not applicable"]

other_licensing_question: |
  [only if move_type is "other" -- state the one licensing question this move's own logic requires; otherwise "not applicable"]

Ingestion Layer output to check:
---------------------------------
original_quote: {original_quote}

e_prime_rewrite: {e_prime_rewrite}
"""

DEMO_IDENTIFY_MOVE_OUTPUT = {
    "move_type": "generalization",
    "move_location": "pooled across 14 studies, n=320,778",
    "other_move_label": "not applicable",
    "other_licensing_question": "not applicable",
}

DEMO_GENERATIVE_CHECK_OUTPUT = {
    "move_type": "generalization",
    "move_label": "Argument from generalization",
    "move_location": "pooled across 14 studies, n=320,778",
    "licensing_question": "Does the sample the argument generalizes from actually represent the population it draws conclusions about?",
    "condition_violated_bounds": [0.1, 0.2],
    "condition_violated_location": "not applicable",
    "matches_existing_category": "none",
    "candidate_new_category_name": "not applicable",
    "candidate_new_category_definition": "not applicable",
    "state": "known-false",
    "explanation": "Demo placeholder: a 14-study, n=320,778 pooled sample gives real representativeness grounds for the generalization -- the licensing condition holds. Pre-recorded, not a live model call.",
}


def identify_reasoning_move(ingestion_output: dict) -> dict:
    """Stage 1 of generative_fallacy_check(). Identifies which reasoning
    move an argument uses, from REASONING_MOVE_TYPES or a model-named
    "other". Does not judge whether the move succeeds -- that's Stage 2."""
    prompt = IDENTIFY_MOVE_PROMPT.format(
        original_quote=ingestion_output["original_quote"],
        e_prime_rewrite=ingestion_output["e_prime_rewrite"],
    )
    return _call_model(prompt)


def build_licensing_prompt(move_result: dict, ingestion_output: dict) -> str:
    """Builds Stage 2's prompt from Stage 1's identified move -- asks that
    specific move's own licensing question, scored as a bounds pair (high
    bounds = the licensing condition is violated, i.e. a fallacy is
    present), plus whether any of the 26 named categories already covers
    this pattern."""
    if move_result["move_type"] == "other":
        move_label = move_result["other_move_label"]
        licensing_question = move_result["other_licensing_question"]
    else:
        entry = REASONING_MOVE_TYPES[move_result["move_type"]]
        move_label = entry["label"]
        licensing_question = entry["licensing_question"]

    header = (
        f"You are checking Stage 2 of a generative fallacy check. Stage 1 "
        f"identified this argument's reasoning move as: {move_label}. That "
        f"move's own licensing question: {licensing_question}\n\n"
        f"Score whether this licensing condition is VIOLATED (not whether "
        f"it holds) as a bounds pair [lower, upper], each 0.0-1.0. A "
        f"confident violation scores close to [0.9, 1.0]. A confident "
        f"clean pass (condition holds, no fallacy) scores close to "
        f"[0.0, 0.1]. Genuine uncertainty about THIS specific argument "
        f"warrants a wide interval reflecting the real balance of evidence "
        f"you find -- reason to your own bounds rather than defaulting to "
        f"any standard or example range.\n\n"
        f"Separately, state whether this specific pattern -- this move, "
        f"failing this specific condition -- already matches one of the 26 "
        f"named fallacy categories this project tracks (circular argument, "
        f"false choice, part-to-whole mixup, word-shift, non sequitur, "
        f"false cause, rushed conclusion, survivorship bias, ignoring the "
        f"base rate, Texas sharpshooter, gambler's fallacy, appeal to "
        f"authority, personal attack, origin attack, straw man, red "
        f"herring, bandwagon, tu quoque, slippery slope, no true Scotsman, "
        f"motte-and-bailey, appeal to nature, sunk cost, false equivalence, "
        f"appeal to ignorance, double-counting). If the condition is "
        f"violated and it doesn't cleanly match any of these 26, propose a "
        f"candidate new category name and a one-sentence definition -- do "
        f"not force a near-miss match just to avoid proposing something "
        f"new.\n\n"
    )

    template = (
        header +
        "Output as valid YAML only. No markdown fences. No preamble.\n\n"
        "Schema:\n-------\n"
        "condition_violated_bounds: [lower, upper]\n\n"
        "condition_violated_location: |\n"
        "  [the exact phrase carrying this, or \"not applicable\"]\n\n"
        "matches_existing_category: |\n"
        "  [one of the 26 category names above, or \"none\"]\n\n"
        "candidate_new_category_name: |\n"
        "  [only if matches_existing_category is \"none\" and the condition is violated; otherwise \"not applicable\"]\n\n"
        "candidate_new_category_definition: |\n"
        "  [one sentence, only if candidate_new_category_name is not \"not applicable\"]\n\n"
        "explanation: |\n  [2-3 sentences on what drove the score]\n\n"
        "Ingestion Layer output to check:\n"
        "---------------------------------\n"
        "original_quote: {original_quote}\n\n"
        "e_prime_rewrite: {e_prime_rewrite}\n"
    )
    return template.format(
        original_quote=ingestion_output["original_quote"],
        e_prime_rewrite=ingestion_output["e_prime_rewrite"],
    )


def generative_fallacy_check(ingestion_output: dict) -> dict:
    """Prototype redesign of open_check_claim(), per
    SYNTHESIS/meta-fallacy-construction-v1.md. Two model calls: Stage 1
    identifies the argument's reasoning move (identify_reasoning_move());
    Stage 2 asks that move's own licensing question, scored as a bounds
    pair, and checks whether a violation matches an existing category or
    warrants a candidate new one. Requires an Ingestion Layer output as
    input, same contract as every other check function above."""
    if "original_quote" not in ingestion_output or "e_prime_rewrite" not in ingestion_output:
        print(
            "generative_fallacy_check() requires an Ingestion Layer output "
            "(original_quote + e_prime_rewrite). Run ingest_claim() first.",
            file=sys.stderr,
        )
        sys.exit(1)

    move_result = identify_reasoning_move(ingestion_output)

    if move_result["move_type"] == "other":
        move_label = move_result["other_move_label"]
        licensing_question = move_result["other_licensing_question"]
    else:
        entry = REASONING_MOVE_TYPES[move_result["move_type"]]
        move_label = entry["label"]
        licensing_question = entry["licensing_question"]

    prompt = build_licensing_prompt(move_result, ingestion_output)
    licensing_result = _call_model(prompt)

    result = {
        "move_type": move_result["move_type"],
        "move_label": move_label,
        "move_location": move_result["move_location"],
        "licensing_question": licensing_question,
        **licensing_result,
    }
    result["state"] = bounds_state(result["condition_violated_bounds"])
    return result


# ---------------------------------------------------------------------------
# CONSTRUCTIVE ARGUMENT BUILDER -- the other direction from every check
# function above. Per SYNTHESIS/constructive-argument-builder-v1.md.
# generative_fallacy_check() runs REASONING_MOVE_TYPES backward: given a
# finished argument, identify its move, then check whether the licensing
# condition got violated. construct_argument() runs the same table forward:
# given a target conclusion and the evidence actually in hand, recommend a
# move, then check whether that evidence satisfies the move's licensing
# condition BEFORE any argument gets written. High bounds here mean the
# condition HOLDS (construction succeeds) -- the reverse of
# generative_fallacy_check()'s condition_violated_bounds, named explicitly
# to avoid confusing the two directions.
# ---------------------------------------------------------------------------

RECOMMEND_MOVE_PROMPT = """You are recommending which reasoning move best connects a target conclusion to the evidence someone actually has, as Stage 1 of a constructive argument check. This does not check whether the evidence succeeds -- only which move type fits the conclusion-evidence pair.

Known move types: authority, analogy, generalization, causal_inference, chaining, redefinition, evidence_aggregation, boundary_shift. If none fits, choose "other" and name the move yourself, along with the one licensing question that move's own logic requires in order to work.

Output as valid YAML only. No markdown fences. No preamble.

Schema:
-------
move_type: |
  [one of: authority, analogy, generalization, causal_inference, chaining, redefinition, evidence_aggregation, boundary_shift, other]

rationale: |
  [1-2 sentences on why this move fits the conclusion-evidence pair]

other_move_label: |
  [only if move_type is "other" -- name the move type yourself; otherwise "not applicable"]

other_licensing_question: |
  [only if move_type is "other" -- state the one licensing question this move's own logic requires; otherwise "not applicable"]

Target conclusion:
------------------
{target_conclusion}

Evidence available:
-------------------
{available_evidence}
"""

DEMO_CONSTRUCT_ARGUMENT_OUTPUT = {
    "target_conclusion": "Regular exercise reduces cardiovascular disease risk.",
    "available_evidence": "A single case study of one patient who started exercising and had improved cholesterol.",
    "move_type": "generalization",
    "move_label": "Argument from generalization",
    "rationale": "The conclusion claims a population-level effect; the only path from one case to a population claim is generalization.",
    "licensing_question": "Does the sample the argument generalizes from actually represent the population it draws conclusions about?",
    "condition_satisfied_bounds": [0.0, 0.1],
    "gap_description": "One case study of one patient cannot represent the population this conclusion claims about. A defensible generalization needs a larger sample with real demographic and health-status range, not a stronger restatement of this one case.",
    "state": "known-false",
    "explanation": "Demo placeholder: n=1 fails representativeness on its face, regardless of how positive that one result looks. Pre-recorded, not a live model call.",
}


def recommend_reasoning_move(target_conclusion: str, available_evidence: str) -> dict:
    """Stage 1 of construct_argument(). Recommends which reasoning move
    best connects a target conclusion to the evidence in hand, from
    REASONING_MOVE_TYPES or a model-named "other". Does not judge whether
    the evidence succeeds -- that's Stage 2."""
    prompt = RECOMMEND_MOVE_PROMPT.format(
        target_conclusion=target_conclusion,
        available_evidence=available_evidence,
    )
    return _call_model(prompt)


def build_construction_prompt(move_result: dict, target_conclusion: str, available_evidence: str) -> str:
    """Builds Stage 2's prompt from Stage 1's recommended move -- asks that
    move's own licensing question against the evidence actually available,
    scored as a bounds pair where HIGH bounds mean the condition HOLDS
    (opposite framing from build_licensing_prompt() above, which scores
    violation). Requests a specific gap description when the condition
    doesn't hold, naming what evidence would need to exist."""
    if move_result["move_type"] == "other":
        move_label = move_result["other_move_label"]
        licensing_question = move_result["other_licensing_question"]
    else:
        entry = REASONING_MOVE_TYPES[move_result["move_type"]]
        move_label = entry["label"]
        licensing_question = entry["licensing_question"]

    header = (
        f"You are checking Stage 2 of a constructive argument check. "
        f"Stage 1 recommended this move to connect the evidence to the "
        f"conclusion: {move_label}. That move's own licensing question: "
        f"{licensing_question}\n\n"
        f"Score whether this licensing condition HOLDS (not whether it's "
        f"violated) as a bounds pair [lower, upper], each 0.0-1.0, given "
        f"the evidence actually available. A confident pass scores close "
        f"to [0.9, 1.0]. A confident fail scores close to [0.0, 0.1]. "
        f"Genuine uncertainty about THIS specific evidence-conclusion pair "
        f"warrants a wide interval reflecting the real balance you find -- "
        f"reason to your own bounds rather than defaulting to any standard "
        f"or example range.\n\n"
        f"If the condition does not hold, name the specific gap -- what "
        f"additional evidence would need to exist for this move to "
        f"actually work, not just a restatement that the evidence falls "
        f"short.\n\n"
    )

    template = (
        header +
        "Output as valid YAML only. No markdown fences. No preamble.\n\n"
        "Schema:\n-------\n"
        "condition_satisfied_bounds: [lower, upper]\n\n"
        "gap_description: |\n"
        "  [the specific evidence needed if the condition doesn't hold, or \"not applicable\" if it does]\n\n"
        "explanation: |\n  [2-3 sentences on what drove the score]\n\n"
        "Target conclusion:\n------------------\n{target_conclusion}\n\n"
        "Evidence available:\n-------------------\n{available_evidence}\n"
    )
    return template.format(
        target_conclusion=target_conclusion,
        available_evidence=available_evidence,
    )


def construct_argument(target_conclusion: str, available_evidence: str) -> dict:
    """Constructive counterpart to generative_fallacy_check(), per
    SYNTHESIS/constructive-argument-builder-v1.md. Two model calls: Stage 1
    recommends a reasoning move to connect the evidence to the conclusion
    (recommend_reasoning_move()); Stage 2 checks that move's own licensing
    question against the evidence, scored as a bounds pair where high
    bounds mean the condition holds, and names the specific gap when it
    doesn't. Takes a target conclusion and evidence description directly --
    not an Ingestion Layer output, since there's no existing claim to
    rewrite here, only a position being built."""
    if not target_conclusion or not available_evidence:
        print(
            "construct_argument() requires both a target_conclusion and "
            "available_evidence.",
            file=sys.stderr,
        )
        sys.exit(1)

    move_result = recommend_reasoning_move(target_conclusion, available_evidence)

    if move_result["move_type"] == "other":
        move_label = move_result["other_move_label"]
        licensing_question = move_result["other_licensing_question"]
    else:
        entry = REASONING_MOVE_TYPES[move_result["move_type"]]
        move_label = entry["label"]
        licensing_question = entry["licensing_question"]

    prompt = build_construction_prompt(move_result, target_conclusion, available_evidence)
    licensing_result = _call_model(prompt)

    result = {
        "target_conclusion": target_conclusion,
        "available_evidence": available_evidence,
        "move_type": move_result["move_type"],
        "move_label": move_label,
        "rationale": move_result["rationale"],
        "licensing_question": licensing_question,
        **licensing_result,
    }
    result["state"] = bounds_state(result["condition_satisfied_bounds"])
    return result


# ---------------------------------------------------------------------------
# BOUNDED CONSTRUCT-SCREEN LOOP -- per
# SYNTHESIS/closed-loop-construct-screen-v1.md. Loops construct_argument()
# and generative_fallacy_check() together. This does NOT turn the system
# into a closed symbolic system the way WFF 'N PROOF is -- see that file's
# full reasoning. It's a bounded fixed-point search over argument-space,
# not a proof: no formal convergence guarantee exists, so this loop is
# honest about its own possible failure to converge, with four explicit
# termination conditions and no hidden fifth path that silently returns a
# best-effort draft as if it were a clean pass.
# ---------------------------------------------------------------------------

WRITE_DRAFT_PROMPT = """You are writing an argument in E-Prime -- no "is/are/was/were/be/being/been" -- connecting the evidence to the conclusion via the specified reasoning move. {revision_note}

Output as valid YAML only. No markdown fences. No preamble.

Schema:
-------
argument_text: |
  [the drafted argument, in E-Prime, one to three sentences]

Target conclusion:
------------------
{target_conclusion}

Evidence available:
-------------------
{available_evidence}

Reasoning move to use:
-----------------------
{move_label} -- {licensing_question}
"""

DEMO_DRAFT_OUTPUT = {
    "argument_text": "A pooled cohort spanning 12 studies and 200,000 participants, drawn across multiple age groups and regions, shows a measurable drop in cardiovascular events among regular exercisers.",
}

DEMO_ITERATIVE_REFINEMENT_OUTPUT = {
    "converged": True,
    "stopped_reason": "clean_pass",
    "rounds_run": 2,
    "history": [
        {
            "round": 1,
            "argument_text": "Regular exercisers show lower cardiovascular event rates, so exercise reduces cardiovascular disease risk.",
            "screen_state": "unknown",
            "flagged_issue": "rushed_conclusion",
        },
        {
            "round": 2,
            "argument_text": "A pooled cohort spanning 12 studies and 200,000 participants, drawn across multiple age groups and regions, shows a measurable drop in cardiovascular events among regular exercisers.",
            "screen_state": "known-false",
            "flagged_issue": "none",
        },
    ],
    "argument_text": "A pooled cohort spanning 12 studies and 200,000 participants, drawn across multiple age groups and regions, shows a measurable drop in cardiovascular events among regular exercisers.",
    "explanation": "Demo placeholder: round 1's draft stated the conclusion without naming its sample size or scope, flagged as a rushed-conclusion risk. Round 2's revision named the pooled sample directly and passed clean. Pre-recorded, not a live model call.",
}


def build_draft_prompt(
    target_conclusion: str,
    available_evidence: str,
    move_label: str,
    licensing_question: str,
    prior_issues=None,
) -> str:
    """Builds the prompt for write_argument_draft(). Includes a revision
    note naming prior rounds' flagged issues when this isn't the first
    draft -- a real attempt at addressing what actually got flagged,
    not a blind re-generation."""
    if prior_issues:
        revision_note = (
            "This is a revision. The previous draft's fallacy screen "
            "flagged: " + "; ".join(prior_issues) + ". Rewrite to address "
            "these specific issues, not just reword around the same problem."
        )
    else:
        revision_note = "This is the first draft."

    template = WRITE_DRAFT_PROMPT
    return template.format(
        revision_note=revision_note,
        target_conclusion=target_conclusion,
        available_evidence=available_evidence,
        move_label=move_label,
        licensing_question=licensing_question,
    )


def write_argument_draft(
    target_conclusion: str,
    available_evidence: str,
    move_label: str,
    licensing_question: str,
    prior_issues=None,
) -> dict:
    """Stage 1 of one loop round. Writes an actual E-Prime argument
    connecting the evidence to the conclusion via the confirmed move.
    Returns argument_text -- not an Ingestion Layer output, since nothing
    here gets rewritten from an external source; it's authored fresh,
    already in E-Prime."""
    prompt = build_draft_prompt(
        target_conclusion, available_evidence, move_label, licensing_question, prior_issues
    )
    return _call_model(prompt)


def iterative_argument_refinement(
    target_conclusion: str, available_evidence: str, max_rounds: int = 3
) -> dict:
    """Bounded construct<->screen loop, per
    SYNTHESIS/closed-loop-construct-screen-v1.md. Gates on
    construct_argument() first -- refuses to draft anything if the
    licensing condition doesn't already hold on the raw evidence. Then
    loops write_argument_draft() -> generative_fallacy_check() up to
    max_rounds times. Four termination conditions, checked in order each
    round: insufficient_evidence (gate fails before round 1), clean_pass
    (screen finds nothing), oscillation_detected (a flagged issue repeats
    across rounds), max_rounds_exhausted (cap hit with no resolution). No
    fifth, hidden path exists -- a loop that doesn't converge reports that
    honestly, with its full round history, rather than returning its last
    attempt as if it were a clean pass."""
    construct_result = construct_argument(target_conclusion, available_evidence)
    if construct_result["state"] != "known-true":
        return {
            "converged": False,
            "stopped_reason": "insufficient_evidence",
            "rounds_run": 0,
            "history": [],
            "construct_result": construct_result,
        }

    move_label = construct_result["move_label"]
    licensing_question = construct_result["licensing_question"]

    history = []
    prior_issues = []
    for round_num in range(1, max_rounds + 1):
        draft = write_argument_draft(
            target_conclusion, available_evidence, move_label, licensing_question,
            prior_issues=prior_issues or None,
        )
        draft_ingestion = {
            "original_quote": draft["argument_text"],
            "e_prime_rewrite": draft["argument_text"],
        }
        screen_result = generative_fallacy_check(draft_ingestion)

        flagged = screen_result.get("matches_existing_category")
        if flagged in (None, "none"):
            flagged = screen_result.get("candidate_new_category_name")

        round_record = {
            "round": round_num,
            "argument_text": draft["argument_text"],
            "screen_state": screen_result["state"],
            "flagged_issue": flagged,
        }
        history.append(round_record)

        if screen_result["state"] == "known-false":
            return {
                "converged": True,
                "stopped_reason": "clean_pass",
                "rounds_run": round_num,
                "history": history,
                "argument_text": draft["argument_text"],
                "construct_result": construct_result,
            }

        if flagged not in (None, "none", "not applicable") and any(
            h["flagged_issue"] == flagged for h in history[:-1]
        ):
            return {
                "converged": False,
                "stopped_reason": "oscillation_detected",
                "rounds_run": round_num,
                "history": history,
                "construct_result": construct_result,
            }

        prior_issues.append(screen_result.get("explanation", str(flagged)))

    return {
        "converged": False,
        "stopped_reason": "max_rounds_exhausted",
        "rounds_run": max_rounds,
        "history": history,
        "construct_result": construct_result,
    }


def strip_markdown_fences(text: str) -> str:
    """Defensively strip a fenced-code wrapper (triple backtick + optional yaml tag)
    if the model adds one despite the prompt explicitly forbidding it. No-op on
    already-clean YAML.

    Also strips a bare leading "yaml"/"yml" label line with no closing fence --
    real failure mode found 2026-08-18: RKLLama's 14B model sometimes opens a
    response with an unfenced "yaml" line (no triple backticks at all), which
    the fenced-block regex above never matches, so a bare label line slid
    straight into the parser and broke on line 2 instead of getting stripped.
    Only strips when the first line is exactly "yaml"/"yml" and nothing else,
    to avoid ever touching a real key that happens to start with that word.

    Also strips a bare leading dashes-only separator line (e.g. "-------") --
    second real failure mode found same day: build_bounds_prompt()'s own
    schema section is formatted as "Schema:\n-------\n<schema>", and the 14B
    model sometimes echoes that literal "-------" separator back as the first
    line of its response, same underlying leak-the-prompt-formatting behavior
    as the bare "yaml" line above, just a different literal string.

    Also truncates at any FURTHER standalone dash-line appearing anywhere
    after the leading strip above -- third and fourth real failure modes
    found 2026-08-18 during the first live 78-call run (all-26-rkllama):
    motte_and_bailey leaked build_bounds_prompt()'s "-------" separator
    again, but mid-response after real content, not as the first line, so
    the leading-anchor check above never caught it; sunk_cost leaked a
    second bare "---" document marker after a legitimate leading one,
    which PyYAML reads as "expected a single document in the stream".
    Real content never legitimately contains a standalone dash-only line,
    so truncating at the first one found anywhere in what remains is safe
    regardless of which of the two shapes produced it."""
    text = text.strip()
    match = re.match(r"^```(?:yaml|yml)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        match = re.match(r"^(?:yaml|yml)[ \t]*\n(.*)$", text, re.DOTALL)
        if match:
            text = match.group(1)
        else:
            match = re.match(r"^-{3,}[ \t]*\n(.*)$", text, re.DOTALL)
            if match:
                text = match.group(1)

    sep_match = re.search(r"\n-{3,}[ \t]*(?:\n|$)", text)
    if sep_match:
        text = text[:sep_match.start()]

    return text.strip()


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
    parser.add_argument(
        "--circular-pilot",
        choices=["eggs-003", "covid-003", "blackhole-002"],
        help="Run the neuro-symbolic circular-argument pilot (Approach C, "
        "SYNTHESIS/neuro-symbolic-fallacy-screen-v1.md) against one of the "
        "three claims fallacy-screen-worked-examples-v1.md originally tested. "
        "Bypasses the rest of the pipeline. Use with --demo to see "
        "pre-recorded output without an API key.",
    )
    parser.add_argument(
        "--bounds-pilot",
        choices=sorted(FALLACY_SHAPE_DATA.keys()),
        help="Run the generalized shape-grouped bounds pilot (Approach C, "
        "SYNTHESIS/neuro-symbolic-fallacy-shapes-v1.md) against one of the "
        "25 categories in FALLACY_SHAPE_DATA (all 26 except circular "
        "argument, which uses --circular-pilot instead). Pair with "
        "--claim to pick which of the three pilot claims to run against in "
        "live mode (default eggs-003); --demo scores against the standard "
        "demo claim regardless of --claim.",
    )
    parser.add_argument(
        "--claim",
        choices=["eggs-003", "covid-003", "blackhole-002"],
        default="eggs-003",
        help="Which pilot claim --bounds-pilot runs against in live mode. "
        "Ignored by --circular-pilot (which always runs all three) and by "
        "--demo mode.",
    )
    parser.add_argument(
        "--generative-check",
        action="store_true",
        help="Run the generative fallacy-check prototype (Stage 1: identify "
        "the argument's reasoning move; Stage 2: ask that move's own "
        "licensing question), per SYNTHESIS/meta-fallacy-construction-v1.md. "
        "A prototype redesign of open_check_claim(), reached only through "
        "this flag -- the default pipeline still uses open_check_claim() "
        "unchanged. Pair with --claim to pick which pilot claim to run "
        "against in live mode (default eggs-003); --demo shows pre-recorded "
        "output against the standard demo claim regardless of --claim.",
    )
    parser.add_argument(
        "--construct-argument",
        action="store_true",
        help="Run the constructive argument-builder prototype (Stage 1: "
        "recommend a reasoning move; Stage 2: check that move's licensing "
        "question against the evidence in hand), per "
        "SYNTHESIS/constructive-argument-builder-v1.md. The other direction "
        "from every check function above -- builds toward a conclusion "
        "instead of screening a finished one. Requires --target-conclusion "
        "and --available-evidence in live mode; --demo shows a pre-recorded "
        "example regardless of those flags.",
    )
    parser.add_argument(
        "--target-conclusion",
        help="The conclusion --construct-argument tries to build a case "
        "for. Required in live mode with --construct-argument.",
    )
    parser.add_argument(
        "--available-evidence",
        help="The evidence --construct-argument checks against its "
        "recommended move's licensing question. Required in live mode "
        "with --construct-argument.",
    )
    parser.add_argument(
        "--iterative-refine",
        action="store_true",
        help="Run the bounded construct<->screen loop (Stage 0: gate on "
        "construct_argument(); then loop write_argument_draft() -> "
        "generative_fallacy_check() up to --max-rounds times), per "
        "SYNTHESIS/closed-loop-construct-screen-v1.md. Four termination "
        "conditions: insufficient_evidence, clean_pass, "
        "oscillation_detected, max_rounds_exhausted -- no hidden fifth "
        "path. Requires --target-conclusion and --available-evidence in "
        "live mode; --demo shows a pre-recorded two-round example.",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=3,
        help="Round cap for --iterative-refine. Default 3.",
    )
    args = parser.parse_args()

    if args.demo:
        if args.iterative_refine:
            print("--- Bounded Construct-Screen Loop (demo case) ---")
            print(yaml.dump(DEMO_ITERATIVE_REFINEMENT_OUTPUT, default_flow_style=False, sort_keys=False))
        elif args.construct_argument:
            print("--- Constructive Argument Builder (demo case) ---")
            print(yaml.dump(DEMO_CONSTRUCT_ARGUMENT_OUTPUT, default_flow_style=False, sort_keys=False))
        elif args.generative_check:
            print("--- Generative Fallacy Check (demo claim) ---")
            print(yaml.dump(DEMO_GENERATIVE_CHECK_OUTPUT, default_flow_style=False, sort_keys=False))
        elif args.bounds_pilot:
            print(f"--- Neuro-Symbolic Bounds Pilot: {FALLACY_SHAPE_DATA[args.bounds_pilot]['display_name']} (demo claim) ---")
            print(yaml.dump(demo_bounds_output(args.bounds_pilot), default_flow_style=False, sort_keys=False))
        elif args.circular_pilot:
            print(f"--- Neuro-Symbolic Pilot: circular argument, {args.circular_pilot} ---")
            print(yaml.dump(DEMO_CIRCULAR_PILOT_OUTPUTS[args.circular_pilot], default_flow_style=False, sort_keys=False))
        elif args.ingest_only:
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

    if args.bounds_pilot:
        print(f"Running neuro-symbolic bounds pilot ({args.bounds_pilot}) against {args.claim}...", file=sys.stderr)
        bounds_result = fallacy_bounds_screen(args.bounds_pilot, PILOT_CLAIM_INGESTION_OUTPUTS[args.claim])
        print(yaml.dump(bounds_result, default_flow_style=False, sort_keys=False))
        return

    if args.construct_argument:
        if not args.target_conclusion or not args.available_evidence:
            print(
                "--construct-argument requires both --target-conclusion and "
                "--available-evidence in live mode.",
                file=sys.stderr,
            )
            sys.exit(1)
        print("Running constructive argument builder...", file=sys.stderr)
        construct_result = construct_argument(args.target_conclusion, args.available_evidence)
        print(yaml.dump(construct_result, default_flow_style=False, sort_keys=False))
        return

    if args.iterative_refine:
        if not args.target_conclusion or not args.available_evidence:
            print(
                "--iterative-refine requires both --target-conclusion and "
                "--available-evidence in live mode.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Running bounded construct-screen loop (max {args.max_rounds} rounds)...", file=sys.stderr)
        refine_result = iterative_argument_refinement(
            args.target_conclusion, args.available_evidence, max_rounds=args.max_rounds
        )
        print(yaml.dump(refine_result, default_flow_style=False, sort_keys=False))
        return

    if args.generative_check:
        print(f"Running generative fallacy check against {args.claim}...", file=sys.stderr)
        generative_result = generative_fallacy_check(PILOT_CLAIM_INGESTION_OUTPUTS[args.claim])
        print(yaml.dump(generative_result, default_flow_style=False, sort_keys=False))
        return

    if args.circular_pilot:
        print(f"Running neuro-symbolic circular-argument pilot against {args.circular_pilot}...", file=sys.stderr)
        pilot_result = circular_argument_screen(PILOT_CLAIM_INGESTION_OUTPUTS[args.circular_pilot])
        print(yaml.dump(pilot_result, default_flow_style=False, sort_keys=False))
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
