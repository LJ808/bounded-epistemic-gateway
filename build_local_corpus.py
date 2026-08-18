#!/usr/bin/env python3
"""
Local-Model Corpus Builder — drives ingest.py's real Ingestion + Assessment
templates against a local RKLlama model on Board 2 instead of the Anthropic
API. No ANTHROPIC_API_KEY anywhere in this path. Existing claim files under
CLAIMS/ supply the source quotes; this script never touches their existing
human-authored Ingestion/Assessment sections, since those stand as reference
output, not input.

Templates come straight from ingest.py via import — this file adds no new
prompt wording of its own for the Ingestion/Assessment calls.

USAGE:

    # Point at the 1.7B model (fast, exact runtime match):
    python3 build_local_corpus.py --model Qwen3-1.7B-w8a8-rk3588

    # Point at the 7B model (version-skew accepted, richer output):
    python3 build_local_corpus.py --model Qwen2.5-7B-Instruct-rk3588-w8a8-opt-1-hybrid-ratio-0.0

    # Limit to one case while testing:
    python3 build_local_corpus.py --model Qwen3-1.7B-w8a8-rk3588 --case eggs-cvd-diabetes

Output writes to CORPUS/<model>-<timestamp>.jsonl, one JSON line per claim,
each line carrying claim_id, source quote, and both local-model layer outputs.
"""

import argparse
import datetime
import difflib
import json
import re
import sys
from pathlib import Path

import requests
import yaml

# Import the real templates directly from the submission's own file.
# ingest.py sits in the same directory as this script.
sys.path.insert(0, str(Path(__file__).parent))
from ingest import INGESTION_PROMPT, ASSESSMENT_PROMPT, strip_markdown_fences

# Anti-fabrication constraint, local to this script only. ingest.py's own
# INGESTION_PROMPT stays untouched -- the submission's actual template
# carries no trace of this addition. A 2026-08-12 pilot run against
# Qwen3-1.7B produced a rewrite that reversed a source's stated causal
# direction and invented percentages absent from the original quote.
# This suffix names that failure mode directly rather than trusting the
# base prompt's "preserve the source's actual content" line to prevent it.
ANTI_FABRICATION_SUFFIX = """

Additional constraint: if the source quote names no specific number,
statistic, or percentage, the rewrite must not invent one. State the
relationship in qualitative terms instead (e.g. "correlates with", "shows
no association with"), and preserve the source's stated direction exactly --
positive stays positive, null stays null, negative stays negative. Inventing
a plausible-sounding number not present in the source counts as a failure
of this task, worse than leaving the rewrite without a number at all.
"""

LOCAL_INGESTION_PROMPT = INGESTION_PROMPT + ANTI_FABRICATION_SUFFIX

# Anti-correction constraint, local to this script only, same posture as
# ANTI_FABRICATION_SUFFIX above. Real gap root-caused 2026-08-15 (TRC
# MEMORY.md): blackhole-003's source quote carries a minor real grammar
# irregularity -- a non-restrictive clause using "that" after a comma,
# where formal style calls for "which." The model silently corrected
# exactly that one occurrence to "which" in the original_quote field,
# every single time it ran, across every full corpus run that exists --
# while leaving five other "that"s in the same passage untouched, since
# those either function as complementizers (ungrammatical to swap) or
# already read as standard restrictive clauses (no correction pressure).
# The base prompt's "verbatim" instruction alone didn't stop this --
# same lesson as ANTI_FABRICATION_SUFFIX: name the specific failure mode
# directly rather than trust a general instruction to cover it.
VERBATIM_ENFORCEMENT_SUFFIX = """

Additional constraint: copy original_quote character-for-character from
the source text, including any grammar, punctuation, spelling, or style
that reads as nonstandard or awkward. Do not correct "that" to "which"
or "which" to "that," do not add or remove commas, do not fix anything
that looks like an error in the source. original_quote exists to capture
what the source actually says, not an edited or improved version of it --
any correction, however minor or well-intentioned, counts as a failure of
this task equal in severity to inventing a number that isn't there.
"""

LOCAL_INGESTION_PROMPT = LOCAL_INGESTION_PROMPT + VERBATIM_ENFORCEMENT_SUFFIX

# Assessment Layer local fix, same pattern as the Ingestion fix above.
# ingest.py's own ASSESSMENT_PROMPT stays untouched. Found 2026-08-12 on the
# full 8-claim run: the model echoes the prompt's own "Ingestion Layer
# output to assess" section back after its real answer (breaks YAML every
# time), and wraps phrases in markdown bold, which YAML reads as an alias
# reference rather than literal text. This suffix names both directly.
ASSESSMENT_FORMAT_SUFFIX = """

Additional constraint: do not repeat, echo, or restate the "Ingestion Layer
output to assess" block shown above -- your response contains only the four
schema fields (analysis, ambiguity_flags, adversarial_interpretation,
confidence_assessment) and nothing else, no separator lines, no repeated
input. Do not use markdown bold (** **) or any markdown formatting inside
field values -- plain text only.
"""

LOCAL_ASSESSMENT_PROMPT = ASSESSMENT_PROMPT + ASSESSMENT_FORMAT_SUFFIX

# Marks the start of the echoed input block the model sometimes appends
# after its real answer. Text from this marker onward gets discarded before
# YAML parsing runs, rather than trusting the suffix instruction alone to
# prevent it -- a defensive backstop, same posture as strip_markdown_fences.
ECHO_MARKER = "Ingestion Layer output to assess"


def strip_echoed_input(text: str) -> str:
    """Discard everything from the first occurrence of ECHO_MARKER onward.
    No-op if the marker never appears."""
    index = text.find(ECHO_MARKER)
    if index == -1:
        return text
    return text[:index].rstrip()


def strip_markdown_bold(text: str) -> str:
    """Remove markdown bold markers before YAML parsing. Found 2026-08-12:
    the ASSESSMENT_FORMAT_SUFFIX instruction against markdown bold didn't
    hold on blackhole-001 -- the model used ** anyway, and YAML reads a
    leading * as an alias reference, not literal text. Stripping ** outright
    is a defensive backstop, same posture as strip_echoed_input: don't trust
    instruction-following alone to prevent a known parser collision."""
    return text.replace("**", "")


def strip_document_markers(text: str) -> str:
    """Strip a leading and/or trailing '---' YAML document marker. Found
    2026-08-12 on eggs-003: the model wrapped its answer in '---' at both
    start and end (echoing the schema block's own '-------' divider style),
    which yaml.safe_load reads as two separate documents in one stream --
    a fourth distinct formatting collision found this session, none of the
    prior three backstops catch it."""
    text = text.strip()
    if text.startswith("---"):
        text = text[3:].lstrip("\n")
    if text.endswith("---"):
        text = text[:-3].rstrip("\n")
    return text


def truncate_duplicate_block(raw_text: str, field_names: list[str]) -> str:
    """Fifth backstop, 2026-08-13, Jay's call after eggs-001 hit a third
    distinct failure shape on the same claim across three sessions: the
    model sometimes writes its whole answer, then writes all four fields
    a second time verbatim right after. ECHO_MARKER/strip_echoed_input
    only catch echoing the *prompt's* input block -- this is the model
    echoing its *own* output, no marker text in common with that case.
    Finds whichever expected field starts the answer, and if that same
    field name appears a second time later in the text, cuts everything
    from that second occurrence onward. Without this, extract_fields_via_regex()
    has no way to know a field's second copy isn't real content -- it has
    no next expected-field boundary to stop at, so the whole duplicate
    tail lands inside whichever field happened to run last (eggs-001,
    2026-08-13: the entire repeated block landed inside
    confidence_assessment). Runs before both yaml.safe_load and the regex
    fallback, so a clean duplicate never reaches either parser."""
    earliest = None
    for name in field_names:
        pattern = re.compile(r"(?:^|\n)\s*" + re.escape(name) + r"\s*:", re.MULTILINE)
        match = pattern.search(raw_text)
        if match and (earliest is None or match.start() < earliest[0]):
            earliest = (match.start(), match.end(), pattern)
    if earliest is None:
        return raw_text
    _, first_end, pattern = earliest
    second_match = pattern.search(raw_text, first_end)
    if second_match:
        return raw_text[:second_match.start()].rstrip()
    return raw_text


def extract_fields_via_regex(raw_text: str, field_names: list[str]) -> dict:
    """Generic fallback field extractor, used when yaml.safe_load still
    fails after all four cleanup passes above. Four distinct formatting
    collisions surfaced in one session (echo, markdown bold, empty content,
    document markers) -- chasing each new quirk with its own targeted fix
    doesn't converge, since the model's failure modes look stochastic
    rather than traceable to one root cause. Every failure seen so far kept
    the real answer text intact right up until the point of collision; this
    function locates each expected field by name directly in the raw text
    and captures everything up to the next expected field, sidestepping
    YAML's strict document/alias/mapping syntax entirely rather than trying
    to out-guess the next way the model might violate it."""
    positions = []
    for name in field_names:
        pattern = re.compile(r"(?:^|\n)\s*" + re.escape(name) + r"\s*:", re.MULTILINE)
        match = pattern.search(raw_text)
        if match:
            positions.append((match.start(), match.end(), name))

    if not positions:
        return {}

    positions.sort()
    results = {}
    for i, (_, end, name) in enumerate(positions):
        next_start = positions[i + 1][0] if i + 1 < len(positions) else len(raw_text)
        content = raw_text[end:next_start].strip()
        content = re.sub(r"^\|-?\s*\n", "", content)  # leading YAML block-scalar indicator
        content = re.sub(r"\n?-{3,}\s*$", "", content)  # trailing document marker, last field only
        content = content.replace("**", "").strip()
        results[name] = content if content else None

    return results

# Verification pass -- catches what prompt wording alone couldn't prevent.
# Runs after both layers complete, flags problems rather than fixing them
# silently, so a human (or a later filtering pass) decides what to do with
# a flagged record.
TO_BE_FORMS = ("is", "are", "was", "were", "be", "being", "been")
TO_BE_PATTERN = re.compile(r"\b(" + "|".join(TO_BE_FORMS) + r")\b", re.IGNORECASE)
NUMBER_PATTERN = re.compile(r"\d[\d,.]*%?")


def check_e_prime_compliance(rewrite: str) -> list[str]:
    """Return every to-be form found in a rewrite. Empty list means clean.
    The Ingestion Layer's entire purpose consists of removing these forms --
    a rewrite that still carries one has failed its one job, independent of
    whether the content itself reads accurately."""
    return sorted(set(match.lower() for match in TO_BE_PATTERN.findall(rewrite)))


def check_fabricated_numbers(source_quote: str, rewrite: str) -> list[str]:
    """Return every number in the rewrite absent from the source quote.
    A number appearing in the rewrite but nowhere in the source counts as
    invented, not extracted -- exact string match, since a real figure
    carried over from the source should appear verbatim, not paraphrased
    into a different number. Strips a trailing '.' or ',' from every match
    before comparing -- fixed 2026-08-13 after covid-001 and covid-006 both
    false-flagged a real, unaltered source number as fabricated purely
    because NUMBER_PATTERN's own '[\\d,.]*' greedily swallows a sentence-
    ending period on whichever side happens to end a sentence there (source
    for covid-001's "11.", rewrite for covid-006's "1000."), breaking the
    exact-string match against the other side's clean digits. A genuine
    trailing '.'/',' in a real number is vanishingly rare and not worth
    the false-positive rate this caused."""
    def clean(numbers: list[str]) -> list[str]:
        return [n.rstrip(".,") for n in numbers]

    source_numbers = set(clean(NUMBER_PATTERN.findall(source_quote)))
    rewrite_numbers = clean(NUMBER_PATTERN.findall(rewrite))
    return [n for n in rewrite_numbers if n not in source_numbers]


WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_whitespace(text: str) -> str:
    """Collapse any run of whitespace (spaces, newlines, tabs) into one
    space and strip the ends. Used only to absorb real formatting noise
    (a YAML block-literal's own line wrapping) before a verbatim check --
    never to absorb an actual wording change."""
    return WHITESPACE_PATTERN.sub(" ", text).strip()


PUNCTUATION_STRIP_PATTERN = re.compile(r"[^\w]+")


def _diff_word_lists(align_source, align_original, display_source, display_original) -> list:
    """Shared word-level diff helper for check_quote_fidelity()'s three
    passes. Aligns on align_source/align_original (which may be normalized
    -- lowercased, punctuation-stripped) but always reports spans pulled
    from display_source/display_original, so a flagged difference always
    shows the real original-case, original-punctuation text, never a
    normalized echo of it."""
    matcher = difflib.SequenceMatcher(None, align_source, align_original)
    diffs = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        source_span = " ".join(display_source[i1:i2]) or "(nothing)"
        original_span = " ".join(display_original[j1:j2]) or "(nothing)"
        diffs.append({"source": source_span, "original_quote": original_span})
    return diffs


def check_quote_fidelity(source_quote: str, original_quote: str) -> dict:
    """Checks whether the Ingestion Layer's 'original_quote' field stays
    genuinely verbatim against the real source_quote it was built from.
    Real gap found 2026-08-13 (TRC MEMORY.md): the model's own
    original_quote field silently edited the source's "corresponds to"
    into "correlates to" -- a fidelity slip inside the one field whose
    entire contract forbids rewriting. check_e_prime_compliance() and
    check_fabricated_numbers() both test the *rewrite* field; neither one
    ever tested whether original_quote actually matches its source
    string-for-string. This closes that gap.

    Normalizes whitespace only (collapses line-wrap/indent noise from the
    YAML block-literal style) before comparing -- any other difference
    counts as real drift. Returns whether the two strings match exactly
    after normalization, plus the specific word-level differences when
    they don't, via a word-level SequenceMatcher diff.

    Three-tiered, 2026-08-15, Jay's call across two rounds. Round 1: a real
    retroactive run against every existing CORPUS/ file showed drift
    recurring in ~1 of 5 records across every full 12-claim run -- far from
    the single isolated case this check originally closed, most of it one
    systematic pattern (the model lowercasing words at sentence boundaries
    -- "The LHC" -> "the lhc"). Split case_only_drift out from real
    wording drift. Round 2: a second real run against the tiered version
    showed a further pattern hiding inside "substantive": pure punctuation
    drops -- "us..." -> "us;", a trailing comma vanishing ("existence," ->
    "existence") -- reading as identical severity to real wording swaps
    ("that" -> "which", "were" -> "are") and outright content deletions
    ("(arbitrary)" dropped clean, a full sentence dropped clean). A third
    diff pass, case-AND-punctuation-insensitive, now isolates true wording
    drift from punctuation noise the same way the second pass isolated case
    noise -- and cleans a real side effect along the way: a punctuation-only
    difference riding alongside a genuine wording change (blackhole-003's
    "existence," next to its real "that"->"which" swap) no longer clutters
    substantive_word_diff; only the real problem remains in that list.

    Returns four severity signals, each computed from a progressively more
    forgiving diff pass over the same word lists:
      - word_diff: the raw, fully case-and-punctuation-sensitive diff.
      - case_only_drift / case_normalized_word_diff: True / the remaining
        diff once case differences alone get ignored. If this diff is
        empty, every difference in word_diff was pure case.
      - punctuation_only_drift: True once case AND punctuation both get
        ignored and nothing real remains, but case_only_drift was False --
        i.e. the real difference was punctuation (possibly combined with
        case), not wording.
      - substantive_word_diff: whatever survives stripping both case and
        punctuation -- the real content drift this check exists to catch.
    """
    norm_source = normalize_whitespace(source_quote)
    norm_original = normalize_whitespace(original_quote)

    if norm_source == norm_original:
        return {
            "verbatim": True,
            "case_only_drift": False,
            "punctuation_only_drift": False,
            "word_diff": [],
            "case_normalized_word_diff": [],
            "substantive_word_diff": [],
        }

    source_words = norm_source.split()
    original_words = norm_original.split()

    word_diff = _diff_word_lists(source_words, original_words, source_words, original_words)

    # Second pass, case-insensitive: any difference that survives lowercasing
    # is not pure case noise.
    src_lower = [w.lower() for w in source_words]
    orig_lower = [w.lower() for w in original_words]
    case_normalized_word_diff = _diff_word_lists(src_lower, orig_lower, source_words, original_words)
    case_only_drift = len(case_normalized_word_diff) == 0

    # Third pass, case-AND-punctuation-insensitive: strips every non-word
    # character (commas, ellipses, semicolons, parens) plus case from each
    # token before comparing. Whatever still differs after this pass is
    # real wording drift, not formatting -- "us..." and "us;" both reduce
    # to "us" and drop out here; "that" and "which" don't, and stay.
    src_cp = [PUNCTUATION_STRIP_PATTERN.sub("", w).lower() for w in source_words]
    orig_cp = [PUNCTUATION_STRIP_PATTERN.sub("", w).lower() for w in original_words]
    substantive_word_diff = _diff_word_lists(src_cp, orig_cp, source_words, original_words)
    punctuation_only_drift = (not case_only_drift) and len(substantive_word_diff) == 0

    return {
        "verbatim": False,
        "case_only_drift": case_only_drift,
        "punctuation_only_drift": punctuation_only_drift,
        "word_diff": word_diff,
        "case_normalized_word_diff": case_normalized_word_diff,
        "substantive_word_diff": substantive_word_diff,
    }


def verify_record(record: dict) -> dict:
    """Run both checks against a completed record's Ingestion Layer output.
    Adds a 'verification' block; adds nothing if the Ingestion Layer itself
    never produced a rewrite to check (an already-errored record), and flags
    -- rather than crashes on -- a rewrite that came back as something other
    than a plain string. Found 2026-08-12: a colon inside generated text can
    make yaml.safe_load parse e_prime_rewrite as a nested mapping instead of
    a scalar, same schema-fragility class as the Assessment Layer's
    trailing-junk parse failure found earlier in this session."""
    ingestion = record.get("ingestion_layer", {})
    rewrite = ingestion.get("e_prime_rewrite")
    original_quote = ingestion.get("original_quote")
    source_quote = record.get("source_quote")

    if not rewrite or not source_quote:
        return record

    if not isinstance(rewrite, str):
        record["verification"] = {
            "e_prime_compliant": None,
            "to_be_forms_found": None,
            "fabricated_numbers": None,
            "quote_verbatim": None,
            "quote_word_diff": None,
            "verification_error": f"e_prime_rewrite came back as {type(rewrite).__name__}, not a string -- checks skipped.",
        }
        return record

    to_be_hits = check_e_prime_compliance(rewrite)
    fabricated = check_fabricated_numbers(source_quote, rewrite)

    # Quote-fidelity check, real gap found 2026-08-13 (TRC MEMORY.md): the
    # e_prime_rewrite checks above never tested whether original_quote
    # itself stayed verbatim against source_quote. Guards for the same
    # non-string failure shape rewrite already guards against above.
    if isinstance(original_quote, str):
        fidelity = check_quote_fidelity(source_quote, original_quote)
        quote_verbatim = fidelity["verbatim"]
        quote_case_only_drift = fidelity["case_only_drift"]
        quote_punctuation_only_drift = fidelity["punctuation_only_drift"]
        quote_word_diff = fidelity["word_diff"]
        quote_substantive_word_diff = fidelity["substantive_word_diff"]
    elif original_quote is None:
        quote_verbatim = None
        quote_case_only_drift = None
        quote_punctuation_only_drift = None
        quote_word_diff = "original_quote missing -- fidelity check skipped."
        quote_substantive_word_diff = None
    else:
        quote_verbatim = None
        quote_case_only_drift = None
        quote_punctuation_only_drift = None
        quote_word_diff = f"original_quote came back as {type(original_quote).__name__}, not a string -- fidelity check skipped."
        quote_substantive_word_diff = None

    record["verification"] = {
        "e_prime_compliant": len(to_be_hits) == 0,
        "to_be_forms_found": to_be_hits,
        "fabricated_numbers": fabricated,
        "quote_verbatim": quote_verbatim,
        "quote_case_only_drift": quote_case_only_drift,
        "quote_punctuation_only_drift": quote_punctuation_only_drift,
        "quote_word_diff": quote_word_diff,
        "quote_substantive_word_diff": quote_substantive_word_diff,
    }
    return record


BOARD2_URL = "http://172.16.100.11:8080/api/chat"
CLAIMS_DIR = Path(__file__).parent / "CLAIMS"
CORPUS_DIR = Path(__file__).parent / "CORPUS"

QUOTE_PATTERN = re.compile(
    r"### Original Quote\s*\n\"(.+?)\"", re.DOTALL
)


def find_claim_files(case: str = None) -> list[Path]:
    """Locate every claim markdown file under CLAIMS/, optionally filtered
    to one case subdirectory."""
    if case:
        search_root = CLAIMS_DIR / case
        if not search_root.exists():
            print(f"No case directory named '{case}' under {CLAIMS_DIR}", file=sys.stderr)
            sys.exit(1)
    else:
        search_root = CLAIMS_DIR
    return sorted(search_root.rglob("*.md"))


def extract_quote(claim_path: Path) -> str:
    """Pull the Original Quote text out of an existing claim file. Returns
    the verbatim source quote the human-authored ingestion ran against —
    this script reuses that same starting point for the local-model run,
    so results stay directly comparable claim-for-claim."""
    text = claim_path.read_text(encoding="utf-8")
    match = QUOTE_PATTERN.search(text)
    if not match:
        raise ValueError(f"No Original Quote section found in {claim_path.name}")
    return match.group(1)


def call_local_model(model_name: str, prompt: str, expected_fields: list[str] = None) -> dict:
    """Send a prompt to Board 2's RKLlama server and parse the YAML response.
    Mirrors ingest.py's _call_model() shape so downstream code stays
    identical between the API path and this local path. Found 2026-08-12:
    the eggs-cvd-diabetes claims (short quotes) finished in ~13s, but the
    longer black-holes claims exceeded a 120s timeout outright, with no
    handling -- one slow claim crashed the entire batch. Timeout raised to
    300s, and the network failure itself now returns an error dict instead
    of propagating an unhandled exception.

    expected_fields, when given, triggers extract_fields_via_regex() as a
    last resort if YAML parsing still fails after all cleanup passes --
    a generic fallback covering any future formatting quirk, not just the
    four found this session."""
    try:
        response = requests.post(
            BOARD2_URL,
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=300,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"_network_error": str(e)}

    payload = response.json()
    raw_text = payload["message"]["content"]
    if expected_fields:
        raw_text = truncate_duplicate_block(raw_text, expected_fields)
    cleaned_text = strip_markdown_fences(raw_text)
    cleaned_text = strip_echoed_input(cleaned_text)
    cleaned_text = strip_markdown_bold(cleaned_text)
    cleaned_text = strip_document_markers(cleaned_text)

    try:
        result = yaml.safe_load(cleaned_text)
        if isinstance(result, dict):
            return result
        parse_error = f"Got {type(result).__name__}, not a dict"
    except yaml.YAMLError as e:
        parse_error = str(e)

    if expected_fields:
        fallback = extract_fields_via_regex(raw_text, expected_fields)
        if fallback:
            fallback["_fallback_extraction"] = True
            return fallback

    return {"_parse_error": parse_error, "_raw_output": raw_text}


# Shape-mismatch retry, Jay's ruling 2026-08-13. Both blackhole-001's
# malformed nested-dict rewrite (a colon inside generated text makes
# yaml.safe_load parse a scalar field as a mapping instead of a string)
# and eggs-002's list-wrapped scalars survived extract_fields_via_regex()
# untouched -- that fallback only triggers on a YAML *parse* failure, and
# both of these cases parse successfully, just into the wrong Python type.
# Presented three options after the 2026-08-13 full-batch run (normalize/
# coerce the bad shape, regenerate on mismatch, filter bad records at
# training time instead of fixing them here); Jay chose regenerate.
# Capped at two extra attempts per layer -- unbounded retry risks masking
# a genuinely reproducible model quirk (e.g. a source quote whose own
# punctuation reliably triggers the same YAML collision) as a transient one.
MAX_SHAPE_RETRIES = 2


def repair_split_scalars(result: dict, field_names: list[str]) -> None:
    """Repair YAML's colon-collision misparse in place: a scalar field
    containing an unescaped colon parses as a single-key mapping instead
    of a string. blackhole-001 hit this on 3/3 independent generations
    (2026-08-13) -- genuinely reproducible for a source quote whose own
    colon lands mid-sentence, not a transient sampling fluke retrying can
    fix on its own. Rejoins a single-key dict back into "key: value" before
    any malformed-field check runs, so a repairable case never burns a
    retry attempt it doesn't need."""
    for name in field_names:
        value = result.get(name)
        if isinstance(value, dict) and len(value) == 1:
            key, val = next(iter(value.items()))
            result[name] = f"{key}: {val}".strip()


def repair_list_wrapped_scalars(result: dict, field_names: list[str]) -> None:
    """Repair the model's other reproducible misshape: bulleting an answer
    into a real YAML list instead of writing one text block. First
    confirmed 2026-08-13 on eggs-001/eggs-002 as a list of plain strings;
    widened same day after covid-001 produced a list of single-key dicts
    (each list item itself hitting the colon-collision shape
    repair_split_scalars targets) -- the same bulleting habit, just
    combined with the other misparse in one field. Each list item gets
    normalized the same way repair_split_scalars normalizes a whole field
    (single-key dict -> "key: value") before joining every item with a
    blank line into one string. A list containing anything else (a
    multi-key dict, a nested list) stays untouched -- that's a genuine
    malformed-shape case for the retry loop, not something safe to
    collapse here."""
    for name in field_names:
        value = result.get(name)
        if not (isinstance(value, list) and value):
            continue
        parts = []
        for item in value:
            if isinstance(item, str):
                parts.append(item.strip())
            elif isinstance(item, dict) and len(item) == 1:
                key, val = next(iter(item.items()))
                parts.append(f"{key}: {val}".strip())
            else:
                parts = None
                break
        if parts is not None:
            result[name] = "\n\n".join(parts)


def find_malformed_fields(result: dict, scalar_fields: list[str] = (), int_fields: list[str] = ()) -> list[str]:
    """Return every field present in result but typed wrong: scalar_fields
    expects str (dict/list are the two bad shapes seen so far, post-repair);
    int_fields expects int -- added 2026-08-13 after eggs-002's
    confidence_assessment came back as a degenerate repeated-token string
    ("3" followed by ~400 repeated "---" tokens) that extract_fields_via_regex()
    faithfully captured as valid-looking text, silently passing the old
    str-only check while carrying obvious garbage."""
    malformed = [name for name in scalar_fields if name in result and not isinstance(result[name], str)]
    malformed += [name for name in int_fields if name in result and not isinstance(result[name], int)]
    return malformed


def call_with_shape_retry(
    model_name: str,
    prompt: str,
    expected_fields: list[str],
    scalar_fields: list[str],
    required_fields: list[str],
    int_fields: list[str] = (),
    max_retries: int = MAX_SHAPE_RETRIES,
) -> dict:
    """Call the local model, retrying up to max_retries additional times
    when the result comes back with any scalar_fields/int_fields typed
    wrong (repaired first via repair_split_scalars, so only a genuinely
    unrepairable shape burns a retry) or with every field in
    required_fields empty (the eggs-002 all-null-fields failure class this
    file already handled once for the Assessment Layer specifically --
    generalized here to cover both layers the same way). A genuine parse
    or network error breaks the loop immediately; retrying against those
    duplicates call_local_model's own internal handling for no benefit.
    Records the real attempt count on the returned dict as '_attempts', so
    a record that only succeeded on a retry stays visible as such."""
    attempts = 0
    result = {}
    while attempts <= max_retries:
        attempts += 1
        result = call_local_model(model_name, prompt, expected_fields=expected_fields)
        normalize_record_fields(result)
        repair_split_scalars(result, scalar_fields)
        repair_list_wrapped_scalars(result, scalar_fields)
        normalize_record_fields(result)
        if "_parse_error" in result or "_network_error" in result:
            break
        malformed = find_malformed_fields(result, scalar_fields, int_fields)
        empty = not any(result.get(f) for f in required_fields)
        if not malformed and not empty:
            break
    result["_attempts"] = attempts
    return result


def process_claim(model_name: str, claim_path: Path) -> dict:
    """Run one claim through both layers against the local model. Returns
    a corpus record even on partial failure, with error fields marking
    which layer broke, so one bad claim never halts the batch."""
    claim_id = claim_path.stem
    record = {"claim_id": claim_id, "source_file": str(claim_path.relative_to(CLAIMS_DIR))}

    try:
        source_quote = extract_quote(claim_path)
    except ValueError as e:
        record["error"] = str(e)
        return record

    record["source_quote"] = source_quote

    ingestion_prompt = f"{LOCAL_INGESTION_PROMPT}\n\nSource claim to ingest:\n\n{source_quote}"
    INGESTION_FIELDS = ["original_quote", "e_prime_rewrite"]
    ingestion_result = call_with_shape_retry(
        model_name, ingestion_prompt,
        expected_fields=INGESTION_FIELDS,
        scalar_fields=INGESTION_FIELDS,
        required_fields=INGESTION_FIELDS,
    )
    record["ingestion_layer"] = ingestion_result

    if "_network_error" in ingestion_result:
        record["error"] = f"Ingestion Layer network failure: {ingestion_result['_network_error']}"
        return record

    if "_parse_error" in ingestion_result:
        record["error"] = "Ingestion Layer produced unparseable output; Assessment Layer skipped."
        return record

    if "original_quote" not in ingestion_result or "e_prime_rewrite" not in ingestion_result:
        record["error"] = "Ingestion Layer output missing required fields; Assessment Layer skipped."
        return record

    if find_malformed_fields(ingestion_result, INGESTION_FIELDS):
        record["error"] = f"Ingestion Layer fields stayed non-scalar after {ingestion_result.get('_attempts')} attempt(s); Assessment Layer skipped."
        return record

    # Ground-truth override, 2026-08-15, after VERBATIM_ENFORCEMENT_SUFFIX
    # alone failed to hold on blackhole-003's real 4/5 rerun (still drifted
    # "that" -> "which" post-suffix -- TRC MEMORY.md). Real insight: the
    # model never needed to *reproduce* source_quote at all -- it's already
    # sitting right here, pulled verbatim from the claim file by
    # extract_quote() before this function ever called the model. Asking a
    # generative model to copy text character-for-character is exactly the
    # operation that kept failing (case drift, punctuation drift, silent
    # grammar "correction"), no matter how the prompt got worded. Once the
    # model's response passes its shape checks above (a real signal it
    # attempted the schema correctly), original_quote gets overwritten with
    # the actual known-good source_quote -- not trusted from model output.
    # This closes the entire quote-fidelity gap at the source for every
    # record generated from here forward, independent of prompt wording,
    # model size, or any future formatting quirk this class of bug could
    # still take. The Assessment Layer below runs against this corrected
    # value, so its own reasoning stays grounded in the real quote too.
    # VERBATIM_ENFORCEMENT_SUFFIX stays in the prompt -- harmless, and
    # still useful signal to the model -- but no longer load-bearing.
    ingestion_result["original_quote"] = source_quote

    assessment_prompt = LOCAL_ASSESSMENT_PROMPT.format(
        original_quote=ingestion_result["original_quote"],
        e_prime_rewrite=ingestion_result["e_prime_rewrite"],
    )
    ASSESSMENT_FIELDS = ["analysis", "ambiguity_flags", "adversarial_interpretation", "confidence_assessment"]
    ASSESSMENT_SCALAR_FIELDS = ["analysis", "ambiguity_flags", "adversarial_interpretation"]
    ASSESSMENT_INT_FIELDS = ["confidence_assessment"]
    assessment_result = call_with_shape_retry(
        model_name, assessment_prompt,
        expected_fields=ASSESSMENT_FIELDS,
        scalar_fields=ASSESSMENT_SCALAR_FIELDS,
        required_fields=["analysis"],
        int_fields=ASSESSMENT_INT_FIELDS,
    )
    record["assessment_layer"] = assessment_result

    # Fix for the gap found in the 2026-08-12 7B run: a parse failure here
    # previously sat silently inside assessment_layer._parse_error with no
    # top-level record["error"] set, so a broken Assessment Layer looked
    # identical to a clean one at a glance.
    if "_network_error" in assessment_result:
        record["error"] = f"Assessment Layer network failure: {assessment_result['_network_error']}"
    elif "_parse_error" in assessment_result:
        record["error"] = "Assessment Layer produced unparseable output."
    elif find_malformed_fields(assessment_result, ASSESSMENT_SCALAR_FIELDS, ASSESSMENT_INT_FIELDS):
        record["error"] = f"Assessment Layer fields stayed non-scalar after {assessment_result.get('_attempts')} attempt(s)."
    elif not assessment_result.get("analysis"):
        record["error"] = f"Assessment Layer returned empty/null content after {assessment_result.get('_attempts')} attempt(s)."

    record = verify_record(record)
    return record


def normalize_record_fields(result: dict) -> None:
    """Fix formatting inconsistencies observed in the 2026-08-12/13 runs, in
    place: strip trailing whitespace/newlines the YAML block-literal style
    leaves on string fields, and coerce a confidence_assessment string to a
    real integer. The coercion originally required the whole string to be
    pure digits; widened 2026-08-13 after eggs-001 returned
    'confidence_assessment: "3 = The rewrite slightly changes..."' -- the
    model explaining its score inline instead of giving a bare number. Now
    matches a leading integer and takes just that, so real cases like this
    coerce cleanly instead of retrying three times against a shape
    retrying can't fix (the explanation isn't a formatting accident, it's
    what the model actually generated). Widened again same day after
    eggs-002 returned 'confidence_assessment: [3]' -- an int wrapped in a
    single-item list, the same bulleting habit repair_list_wrapped_scalars
    handles for the string fields, just never unwrapped for this one
    because it expects int, not str."""
    for key, value in result.items():
        if isinstance(value, str):
            result[key] = value.strip()

    confidence = result.get("confidence_assessment")
    if isinstance(confidence, list) and len(confidence) == 1:
        confidence = confidence[0]
        result["confidence_assessment"] = confidence
    if isinstance(confidence, str):
        match = re.match(r"\s*(\d+)", confidence)
        if match:
            result["confidence_assessment"] = int(match.group(1))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True, help="RKLlama model name, exactly as it appears in /models on Board 2.")
    parser.add_argument("--case", help="Limit to one case subdirectory under CLAIMS/ (e.g. eggs-cvd-diabetes). Omit to run all cases.")
    args = parser.parse_args()

    claim_files = find_claim_files(args.case)
    if not claim_files:
        print("No claim files found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(claim_files)} claim file(s). Running against model: {args.model}", file=sys.stderr)

    CORPUS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_model_name = args.model.replace("/", "_")
    output_path = CORPUS_DIR / f"{safe_model_name}-{timestamp}.jsonl"

    error_count = 0
    with output_path.open("w", encoding="utf-8") as f:
        for i, claim_path in enumerate(claim_files, 1):
            print(f"[{i}/{len(claim_files)}] {claim_path.stem}...", file=sys.stderr)
            record = process_claim(args.model, claim_path)
            if "error" in record:
                error_count += 1
                print(f"  -> ERROR: {record['error']}", file=sys.stderr)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nDone. {len(claim_files) - error_count}/{len(claim_files)} claims processed cleanly.", file=sys.stderr)
    print(f"Corpus written to: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
