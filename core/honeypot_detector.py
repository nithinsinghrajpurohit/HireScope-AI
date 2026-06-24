"""
Honeypot Detector Module.

Detects candidates with subtly impossible profiles (honeypots) in the
Redrob hackathon dataset. Multiple heuristic checks are combined to flag
suspicious candidates.

Honeypot indicators:
1. Salary min > salary max
2. Signup date after last-active date
3. Career-history title mismatches with current_title
4. Impossibly high skill counts with low experience
5. Profile completeness anomalies
6. Career history duration vs years_of_experience mismatch
7. Unrealistic endorsement patterns
"""

from datetime import datetime
from typing import Optional


def detect_honeypot(candidate: dict) -> tuple[bool, list[str]]:
    """Detect if a candidate is a honeypot.

    Parameters
    ----------
    candidate : dict
        A single candidate record from the JSONL dataset.

    Returns
    -------
    tuple[bool, list[str]]
        (is_honeypot, list_of_reasons)
    """
    reasons = []
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    career = candidate.get("career_history", [])
    skills = candidate.get("skills", [])
    education = candidate.get("education", [])

    # ── Check 1: Salary min > max ────────────────────────────────────
    salary = signals.get("expected_salary_range_inr_lpa", {})
    sal_min = salary.get("min", 0)
    sal_max = salary.get("max", 0)
    if sal_min > 0 and sal_max > 0 and sal_min > sal_max:
        reasons.append(f"Salary range inverted: min={sal_min} > max={sal_max}")

    # ── Check 2: Signup date after last-active date ──────────────────
    signup = signals.get("signup_date", "")
    last_active = signals.get("last_active_date", "")
    if signup and last_active:
        try:
            signup_dt = datetime.strptime(signup, "%Y-%m-%d")
            active_dt = datetime.strptime(last_active, "%Y-%m-%d")
            if signup_dt > active_dt:
                reasons.append(
                    f"Signup date ({signup}) is after last active date ({last_active})"
                )
        except ValueError:
            pass

    # ── Check 3: Career history total months vs years_of_experience ──
    total_career_months = sum(
        role.get("duration_months", 0) for role in career
    )
    stated_years = profile.get("years_of_experience", 0)
    if stated_years > 0 and total_career_months > 0:
        career_years = total_career_months / 12.0
        # If career years exceeds stated experience by >2x or is <0.3x
        if career_years > stated_years * 2.5:
            reasons.append(
                f"Career months ({total_career_months}) vastly exceed stated years ({stated_years})"
            )
        elif stated_years > 3 and career_years < stated_years * 0.2:
            reasons.append(
                f"Career months ({total_career_months}) much less than stated years ({stated_years})"
            )

    # ── Check 4: Education dates impossibility ───────────────────────
    for edu in education:
        start_y = edu.get("start_year", 0)
        end_y = edu.get("end_year", 0)
        if start_y > 0 and end_y > 0 and start_y > end_y:
            reasons.append(
                f"Education start year ({start_y}) > end year ({end_y})"
            )
        if end_y > 0 and start_y > 0:
            duration = end_y - start_y
            if duration > 12:
                reasons.append(
                    f"Education duration impossibly long: {duration} years"
                )
            elif duration < 0:
                reasons.append(
                    f"Education duration negative: {duration} years"
                )

    # ── Check 5: Skill endorsements anomaly ──────────────────────────
    # Beginner skills with very high endorsements (>40)
    for skill in skills:
        prof = skill.get("proficiency", "")
        endorsements = skill.get("endorsements", 0)
        duration = skill.get("duration_months", 0)
        if prof == "beginner" and endorsements > 40:
            reasons.append(
                f"Skill '{skill['name']}' is beginner but has {endorsements} endorsements"
            )
        # Expert skill with 0 months duration
        if prof in ("advanced", "expert") and duration == 0:
            reasons.append(
                f"Skill '{skill['name']}' is {prof} but has 0 months duration"
            )

    # ── Check 6: Profile completeness inconsistencies ────────────────
    completeness = signals.get("profile_completeness_score", 0)
    # Very high completeness (>90) but no verified email/phone
    if completeness > 95:
        if not signals.get("verified_email", True) and not signals.get("verified_phone", True):
            reasons.append(
                "Very high completeness score but no verified contact info"
            )

    # ── Check 7: Title mismatch in career history ────────────────────
    current_title = profile.get("current_title", "").lower()
    if career:
        latest_role = career[0]  # First entry should be current/most recent
        latest_title = latest_role.get("title", "").lower()
        if latest_role.get("is_current", False) and current_title and latest_title:
            # Simple check: if titles are completely different domains
            if current_title != latest_title:
                # This alone isn't a honeypot — many legitimate reasons
                pass

    # ── Check 8: Overlapping career dates ────────────────────────────
    sorted_career = sorted(
        [r for r in career if r.get("start_date")],
        key=lambda r: r["start_date"]
    )
    for i in range(len(sorted_career) - 1):
        end_date = sorted_career[i].get("end_date")
        next_start = sorted_career[i + 1].get("start_date")
        if end_date and next_start:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                start_dt = datetime.strptime(next_start, "%Y-%m-%d")
                overlap_days = (end_dt - start_dt).days
                if overlap_days > 180:  # More than 6 months overlap
                    reasons.append(
                        f"Career overlap of {overlap_days} days between roles"
                    )
            except ValueError:
                pass

    # ── Check 9: Future dates ────────────────────────────────────────
    ref_date = datetime(2026, 6, 7)  # Approximate current date
    for role in career:
        start = role.get("start_date", "")
        if start:
            try:
                start_dt = datetime.strptime(start, "%Y-%m-%d")
                if start_dt > ref_date:
                    reasons.append(
                        f"Career start date ({start}) is in the future"
                    )
            except ValueError:
                pass

    # ── Decision: a candidate is a honeypot if ≥1 strong signal ──────
    is_honeypot = len(reasons) >= 1
    return is_honeypot, reasons


def batch_detect_honeypots(candidates: list[dict]) -> dict[str, list[str]]:
    """Run honeypot detection on a batch of candidates.

    Returns
    -------
    dict[str, list[str]]
        Mapping of candidate_id -> list of honeypot reasons.
        Only includes candidates flagged as honeypots.
    """
    honeypots = {}
    for cand in candidates:
        cid = cand.get("candidate_id", "")
        is_hp, reasons = detect_honeypot(cand)
        if is_hp:
            honeypots[cid] = reasons
    return honeypots
