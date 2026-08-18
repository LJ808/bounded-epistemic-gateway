#!/usr/bin/env python3
"""
Retroactive Corpus Verifier — runs the same E-Prime-compliance and
fabricated-number checks build_local_corpus.py now applies automatically,
against .jsonl corpus files already written before the checks existed.
Adds no new model calls -- pure re-analysis of saved text.

USAGE:

    # Check one file, print a summary:
    python3 verify_corpus.py CORPUS/Qwen3-1.7B-w8a8-rk3588-20260812-182351.jsonl

    # Check every corpus file in the directory:
    python3 verify_corpus.py --all
"""

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

CORPUS_DIR = Path(__file__).parent / "CORPUS"

TO_BE_FORMS = ("is", "are", "was", "were", "be", "being", "been")
TO_BE_PATTERN = re.compile(r"\b(" + "|".join(TO_BE_FORMS) + r")\b", re.IGNORECASE)
NUMBER_PATTERN = re.compile(r"\d[\d,.]*%?")


def check_e_prime_compliance(rewrite: str) -> list[str]:
    return sorted(set(match.lower() for match in TO_BE_PATTERN.findall(rewrite)))


def check_fabricated_numbers(source_quote: str, rewrite: str) -> list[str]:
    source_numbers = set(NUMBER_PATTERN.findall(source_quote))
    rewrite_numbers = NUMBER_PATTERN.findall(rewrite)
    return [n for n in rewrite_numbers if n not in source_numbers]


WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_whitespace(text: str) -> str:
    """Collapse whitespace before a verbatim comparison -- absorbs a YAML
    block-literal's own line-wrap noise, never an actual wording change.
    Mirrors build_local_corpus.py's function of the same name so both files
    apply the identical fidelity standard."""
    return WHITESPACE_PATTERN.sub(" ", text).strip()


PUNCTUATION_STRIP_PATTERN = re.compile(r"[^\w]+")


def _diff_word_lists(align_source, align_original, display_source, display_original) -> list:
    """Shared word-level diff helper for check_quote_fidelity()'s three
    passes -- mirrors build_local_corpus.py's helper of the same name."""
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
    """Retroactive quote-fidelity check -- closes the real gap logged
    2026-08-13 (TRC MEMORY.md): a corpus record's Ingestion Layer
    'original_quote' field is supposed to stay verbatim against
    source_quote, but nothing ever checked that against files already
    written before this check existed. check_e_prime_compliance() and
    check_fabricated_numbers() both test the rewrite; this tests the
    quote field itself.

    Three-tiered, 2026-08-15, Jay's call across two real rounds against
    this file's own --all output. Round 1: drift recurred in ~1 of 5
    records across every full 12-claim run, most of it one systematic
    pattern (case lowercasing at sentence boundaries) sharing one flag
    with rare, severe wording drift -- split into case_only_drift vs
    substantive. Round 2: a further pattern hid inside "substantive" --
    pure punctuation drops ("us..." -> "us;", a dropped trailing comma)
    reading as identical severity to real wording swaps ("that" ->
    "which") and outright deletions. A third, case-AND-punctuation-
    insensitive diff pass now isolates true wording drift from
    punctuation noise, same logic as build_local_corpus.py's version,
    duplicated here rather than imported, matching this file's existing
    pattern of standalone duplicate checks."""
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

    src_lower = [w.lower() for w in source_words]
    orig_lower = [w.lower() for w in original_words]
    case_normalized_word_diff = _diff_word_lists(src_lower, orig_lower, source_words, original_words)
    case_only_drift = len(case_normalized_word_diff) == 0

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


def verify_file(path: Path) -> None:
    print(f"\n=== {path.name} ===")
    total = 0
    compliant = 0
    clean_numbers = 0
    verbatim_quotes = 0
    case_only_drift_count = 0
    punctuation_only_drift_count = 0
    substantive_drift_count = 0
    quote_checked = 0

    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            total += 1

            ingestion = record.get("ingestion_layer", {})
            rewrite = ingestion.get("e_prime_rewrite")
            original_quote = ingestion.get("original_quote")
            source_quote = record.get("source_quote")

            if not rewrite or not source_quote:
                print(f"  {record.get('claim_id', '?')}: SKIPPED (no rewrite to check -- Ingestion Layer errored)")
                continue

            if not isinstance(rewrite, str):
                print(f"  {record['claim_id']}: SKIPPED (e_prime_rewrite came back as {type(rewrite).__name__}, not a string)")
                continue

            to_be_hits = check_e_prime_compliance(rewrite)
            fabricated = check_fabricated_numbers(source_quote, rewrite)

            fidelity = None
            if isinstance(original_quote, str):
                fidelity = check_quote_fidelity(source_quote, original_quote)
                quote_checked += 1
                if fidelity["verbatim"]:
                    verbatim_quotes += 1
                elif fidelity["case_only_drift"]:
                    case_only_drift_count += 1
                elif fidelity["punctuation_only_drift"]:
                    punctuation_only_drift_count += 1
                else:
                    substantive_drift_count += 1

            if not to_be_hits:
                compliant += 1
            if not fabricated:
                clean_numbers += 1

            status_parts = []
            if to_be_hits:
                status_parts.append(f"E-PRIME VIOLATION ({', '.join(to_be_hits)})")
            if fabricated:
                status_parts.append(f"FABRICATED NUMBERS ({', '.join(fabricated)})")
            if fidelity is not None and not fidelity["verbatim"]:
                if fidelity["case_only_drift"]:
                    diff_str = "; ".join(
                        f"\"{d['source']}\" -> \"{d['original_quote']}\"" for d in fidelity["word_diff"]
                    )
                    status_parts.append(f"QUOTE DRIFT, CASE ONLY ({diff_str})")
                elif fidelity["punctuation_only_drift"]:
                    diff_str = "; ".join(
                        f"\"{d['source']}\" -> \"{d['original_quote']}\"" for d in fidelity["case_normalized_word_diff"]
                    )
                    status_parts.append(f"QUOTE DRIFT, PUNCTUATION ONLY ({diff_str})")
                else:
                    diff_str = "; ".join(
                        f"\"{d['source']}\" -> \"{d['original_quote']}\"" for d in fidelity["substantive_word_diff"]
                    )
                    status_parts.append(f"QUOTE DRIFT, SUBSTANTIVE ({diff_str})")
            elif fidelity is None:
                status_parts.append("QUOTE FIDELITY UNCHECKED (original_quote not a string)")
            status = " | ".join(status_parts) if status_parts else "clean"

            print(f"  {record['claim_id']}: {status}")

    print(
        f"  --- {compliant}/{total} E-Prime compliant, {clean_numbers}/{total} free of fabricated numbers, "
        f"{verbatim_quotes}/{quote_checked} quotes verbatim, {case_only_drift_count} case-only drift, "
        f"{punctuation_only_drift_count} punctuation-only drift, {substantive_drift_count} substantive drift "
        f"({quote_checked}/{total} checkable)"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", nargs="?", help="Path to one .jsonl corpus file.")
    parser.add_argument("--all", action="store_true", help="Check every .jsonl file under CORPUS/.")
    args = parser.parse_args()

    if args.all:
        files = sorted(CORPUS_DIR.glob("*.jsonl"))
        if not files:
            print(f"No .jsonl files found under {CORPUS_DIR}", file=sys.stderr)
            sys.exit(1)
        for f in files:
            verify_file(f)
    elif args.file:
        verify_file(Path(args.file))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
