#!/usr/bin/env python3
"""
rank.py — Main CLI entry point for the Redrob Hackathon ranker.

Produces a submission CSV with top 100 candidates ranked best-fit for the JD.

Usage:
    python rank.py --candidates ./candidates.jsonl --out ./submission.csv
    python rank.py --candidates ./candidates.jsonl.gz --out ./submission.csv
    python rank.py  # Uses default paths

Constraints: 5 min, 16 GB RAM, CPU only, no network during ranking.
"""

import argparse
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.hackathon_ranker import (
    load_candidates,
    load_jd,
    parse_jd_text,
    rank_candidates_for_submission,
    write_submission_csv,
    extract_text_from_docx,
)
from core.honeypot_detector import batch_detect_honeypots


def find_file(candidates_list: list[str]) -> str:
    """Find the first existing file from a list of candidates."""
    for path in candidates_list:
        if os.path.exists(path):
            return path
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Redrob Hackathon — Intelligent Candidate Ranker"
    )
    parser.add_argument(
        "--candidates",
        type=str,
        default=None,
        help="Path to candidates.jsonl or candidates.jsonl.gz",
    )
    parser.add_argument(
        "--jd",
        type=str,
        default=None,
        help="Path to job_description.docx or .md/.txt",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="submission.csv",
        help="Output submission CSV path",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=100,
        help="Number of top candidates to rank (default: 100)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress",
    )

    args = parser.parse_args()
    start_time = time.time()

    # ── Find candidate file ──────────────────────────────────────────
    if args.candidates:
        candidates_path = args.candidates
    else:
        candidates_path = find_file([
            "candidates.jsonl",
            "candidates.jsonl.gz",
            "data/candidates.jsonl",
            "data/candidates.jsonl.gz",
            os.path.join(
                os.path.dirname(__file__),
                "..", "[PUB] India_runs_data_and_ai_challenge",
                "India_runs_data_and_ai_challenge", "candidates.jsonl"
            ),
            os.path.join(
                os.path.dirname(__file__),
                "..", "[PUB] India_runs_data_and_ai_challenge",
                "India_runs_data_and_ai_challenge", "candidates.jsonl.gz"
            ),
            # Also check the sample file for testing
            "sample_candidates.json",
            "data/sample_candidates.json",
            os.path.join(
                os.path.dirname(__file__),
                "..", "[PUB] India_runs_data_and_ai_challenge",
                "India_runs_data_and_ai_challenge", "sample_candidates.json"
            ),
        ])

    if not candidates_path or not os.path.exists(candidates_path):
        print("ERROR: Cannot find candidates file.")
        print("Specify with: python rank.py --candidates ./candidates.jsonl")
        sys.exit(1)

    # ── Find JD file ─────────────────────────────────────────────────
    if args.jd:
        jd_path = args.jd
    else:
        jd_path = find_file([
            "job_description.md",
            "job_description.docx",
            "data/job_description.md",
            "data/job_description.docx",
            os.path.join(
                os.path.dirname(__file__),
                "..", "[PUB] India_runs_data_and_ai_challenge",
                "India_runs_data_and_ai_challenge", "job_description.docx"
            ),
        ])

    print("=" * 70)
    print("  Redrob Hackathon — Intelligent Candidate Ranker")
    print("=" * 70)
    print(f"  Candidates: {candidates_path}")
    print(f"  JD:         {jd_path or '(using built-in JD parser)'}")
    print(f"  Output:     {args.out}")
    print(f"  Top N:      {args.top_n}")
    print("=" * 70)

    # ── Load JD ──────────────────────────────────────────────────────
    print("\n[1/5] Loading job description...")
    if jd_path and os.path.exists(jd_path):
        jd = load_jd(jd_path)
        print(f"  ✓ JD loaded: {jd['title']}")
        if args.verbose:
            print(f"  Required core skills: {len(jd['ai_ml_core'])}")
            print(f"  Preferred skills: {len(jd['preferred_skills'])}")
    else:
        print("  ⚠ JD file not found, using built-in AI/ML engineer requirements")
        jd = parse_jd_text("")

    # ── Load candidates ──────────────────────────────────────────────
    print("\n[2/5] Loading candidates...")
    load_start = time.time()
    candidates = load_candidates(candidates_path)
    load_time = time.time() - load_start
    print(f"  ✓ Loaded {len(candidates):,} candidates in {load_time:.1f}s")

    # ── Detect honeypots ─────────────────────────────────────────────
    print("\n[3/5] Detecting honeypots...")
    hp_start = time.time()
    honeypots = batch_detect_honeypots(candidates)
    hp_time = time.time() - hp_start
    honeypot_ids = set(honeypots.keys())
    print(f"  ✓ Detected {len(honeypots):,} honeypots in {hp_time:.1f}s")

    if args.verbose and honeypots:
        for cid, reasons in list(honeypots.items())[:5]:
            print(f"    🍯 {cid}: {reasons[0]}")
        if len(honeypots) > 5:
            print(f"    ... and {len(honeypots) - 5} more")

    # ── Score & rank ─────────────────────────────────────────────────
    print("\n[4/5] Scoring and ranking candidates...")
    rank_start = time.time()
    ranked = rank_candidates_for_submission(
        candidates, jd, honeypot_ids, top_n=args.top_n
    )
    rank_time = time.time() - rank_start
    print(f"  ✓ Ranked top {len(ranked)} candidates in {rank_time:.1f}s")

    if ranked:
        print("\ncandidate_id\trank\tscore\treasoning")
        for entry in ranked:
            print(
                f"{entry['candidate_id']}\t{entry['rank']}\t{entry['composite_score']:.4f}\t{entry['reasoning']}"
            )

    # ── Write submission ─────────────────────────────────────────────
    print(f"\n[5/5] Writing submission CSV...")
    write_submission_csv(ranked, args.out)

    total_time = time.time() - start_time
    print(f"\n{'=' * 70}")
    print(f"  ✅ Complete! Total time: {total_time:.1f}s")
    print(f"  📄 Submission saved to: {args.out}")
    print(f"  🏆 Top candidate: {ranked[0]['candidate_id']} "
          f"({ranked[0]['candidate_name']}) — "
          f"Score: {ranked[0]['composite_score']:.4f}")
    print(f"  📊 Score range: {ranked[0]['composite_score']:.4f} — "
          f"{ranked[-1]['composite_score']:.4f}")
    print(f"  🍯 Honeypots filtered: {len(honeypot_ids)}")
    print(f"{'=' * 70}")

    # Validate if validator is available
    validator_paths = [
        "validate_submission.py",
        os.path.join(
            os.path.dirname(__file__),
            "..", "[PUB] India_runs_data_and_ai_challenge",
            "India_runs_data_and_ai_challenge", "validate_submission.py"
        ),
    ]
    validator = find_file(validator_paths)
    if validator:
        print(f"\n  💡 Run validation: python \"{validator}\" {args.out}")


if __name__ == "__main__":
    main()
