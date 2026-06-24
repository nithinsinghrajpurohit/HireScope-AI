"""
Weighted scoring system and results persistence.

Scores candidates against a job description using a weighted combination of:
- Skill match (40%)
- Semantic / TF-IDF similarity (25%)
- Experience (20%)
- Education (10%)
- Bonus skills (5%)

Also provides functions to rank candidates, save results, and convert to DataFrames.
"""

import json
import os
from datetime import datetime
from typing import Optional

import pandas as pd

from core import CandidateScore, MatchExplanation, ResumeData, JDRequirements
from core.skill_extractor import (
    extract_skills_from_resume,
    get_skill_overlap,
    calculate_skill_match_score,
)
from core.matching_engine import tfidf_match, semantic_match
from utils.text_processing import extract_years_of_experience, extract_education_level
from utils.constants import (
    SKILL_MATCH_WEIGHT,
    SEMANTIC_SIMILARITY_WEIGHT,
    EXPERIENCE_WEIGHT,
    EDUCATION_WEIGHT,
    BONUS_WEIGHT,
    EDUCATION_LEVELS,
    RESULTS_DIR,
    MODE_TFIDF,
    MODE_SEMANTIC,
)


def score_candidate(
    resume_data: ResumeData,
    jd_req: JDRequirements,
    semantic_sim: float,
    tfidf_sim: float,
    mode: str = MODE_SEMANTIC,
) -> CandidateScore:
    """Score a single candidate against a job description.

    Parameters
    ----------
    resume_data : ResumeData
        Parsed resume data.
    jd_req : JDRequirements
        Parsed JD requirements.
    semantic_sim : float
        Pre-computed semantic similarity (0–1).
    tfidf_sim : float
        Pre-computed TF-IDF similarity (0–1).
    mode : str
        Matching mode — determines which similarity score to weight.

    Returns
    -------
    CandidateScore
        Complete scoring result.
    """
    # ── 1. Extract skills from resume ────────────────────────────────
    resume_skill_dicts = extract_skills_from_resume(resume_data)
    resume_skill_names = [s["skill"] for s in resume_skill_dicts]

    # ── 2. Compare with JD required/preferred skills ─────────────────
    all_jd_skills = jd_req.required_skills + jd_req.preferred_skills
    matched_skills, missing_skills, extra_skills = get_skill_overlap(
        resume_skill_names, all_jd_skills
    )

    # ── 3. Calculate skill match score (0-100) ───────────────────────
    skill_score = calculate_skill_match_score(
        matched_skills, missing_skills, jd_req.required_skills
    )

    # ── 4. Similarity score (0-100) ──────────────────────────────────
    if mode == MODE_TFIDF:
        sim_score = tfidf_sim * 100.0
    else:
        sim_score = semantic_sim * 100.0

    # ── 5. Experience score (0-100) ──────────────────────────────────
    resume_years = _extract_candidate_experience(resume_data)
    experience_score = _compute_experience_score(resume_years, jd_req.min_experience)

    # ── 6. Education score (0-100) ───────────────────────────────────
    education_score = _compute_education_score(resume_data, jd_req.education_level)

    # ── 7. Bonus score for extra relevant skills (0-100) ─────────────
    bonus_score = _compute_bonus_score(extra_skills, jd_req)

    # ── 8. Weighted final score ──────────────────────────────────────
    overall_score = (
        skill_score * SKILL_MATCH_WEIGHT
        + sim_score * SEMANTIC_SIMILARITY_WEIGHT
        + experience_score * EXPERIENCE_WEIGHT
        + education_score * EDUCATION_WEIGHT
        + bonus_score * BONUS_WEIGHT
    )
    overall_score = round(min(100.0, max(0.0, overall_score)), 2)

    # ── 9. Generate explanation ──────────────────────────────────────
    experience_assessment = _build_experience_assessment(resume_years, jd_req.min_experience)
    strengths = _identify_strengths(
        skill_score, sim_score, experience_score, education_score, matched_skills
    )
    improvement_areas = _identify_improvement_areas(
        missing_skills, resume_years, jd_req
    )

    score_breakdown = {
        "skill_match": round(skill_score, 2),
        "semantic": round(semantic_sim * 100.0, 2),
        "experience": round(experience_score, 2),
        "education": round(education_score, 2),
        "bonus": round(bonus_score, 2),
    }

    explanation = MatchExplanation(
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        extra_skills=extra_skills,
        experience_assessment=experience_assessment,
        strengths=strengths,
        improvement_areas=improvement_areas,
        ranking_reason="",  # Will be filled in during ranking
        score_breakdown=score_breakdown,
    )

    # ── 10. Return CandidateScore ────────────────────────────────────
    return CandidateScore(
        candidate_name=resume_data.name,
        file_name=resume_data.file_name,
        overall_score=overall_score,
        skill_match_score=round(skill_score, 2),
        semantic_similarity=round(semantic_sim * 100.0, 2),
        experience_score=round(experience_score, 2),
        education_score=round(education_score, 2),
        bonus_score=round(bonus_score, 2),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        extra_skills=extra_skills,
        experience_years=resume_years,
        explanation=explanation,
        resume_data=resume_data,
    )


def rank_candidates(
    resume_data_list: list[ResumeData],
    jd_req: JDRequirements,
    mode: str = MODE_SEMANTIC,
    model=None,
) -> list[CandidateScore]:
    """Score and rank all candidates against a JD.

    Parameters
    ----------
    resume_data_list : list[ResumeData]
        Parsed resumes.
    jd_req : JDRequirements
        Parsed JD.
    mode : str
        ``MODE_TFIDF`` or ``MODE_SEMANTIC``.
    model : SentenceTransformer, optional
        Pre-loaded model for semantic mode.

    Returns
    -------
    list[CandidateScore]
        Candidates sorted by ``overall_score`` descending.
    """
    if not resume_data_list:
        return []

    resume_texts = [r.raw_text for r in resume_data_list]
    jd_text = jd_req.raw_text

    # ── Batch compute similarities ───────────────────────────────────
    tfidf_scores = tfidf_match(jd_text, resume_texts)

    if mode == MODE_SEMANTIC:
        try:
            semantic_scores = semantic_match(jd_text, resume_texts, model=model)
        except Exception:
            # Fall back to TF-IDF if semantic model fails
            semantic_scores = [0.0] * len(resume_texts)
    else:
        semantic_scores = [0.0] * len(resume_texts)

    # ── Score each candidate ─────────────────────────────────────────
    scored: list[CandidateScore] = []
    for i, resume_data in enumerate(resume_data_list):
        try:
            candidate_score = score_candidate(
                resume_data=resume_data,
                jd_req=jd_req,
                semantic_sim=semantic_scores[i],
                tfidf_sim=tfidf_scores[i],
                mode=mode,
            )
            scored.append(candidate_score)
        except Exception:
            # Create a minimal score for candidates that fail scoring
            fallback = _create_fallback_score(resume_data)
            scored.append(fallback)

    # ── Sort by overall_score descending ─────────────────────────────
    scored.sort(key=lambda c: c.overall_score, reverse=True)

    # ── Fill in ranking reasons ──────────────────────────────────────
    total = len(scored)
    for rank, candidate in enumerate(scored, start=1):
        candidate.explanation.ranking_reason = _generate_ranking_reason_text(
            candidate, rank, total
        )

    return scored


def save_results(
    ranked_candidates: list[CandidateScore],
    jd_req: JDRequirements,
    output_dir: str = None,
) -> str:
    """Save ranking results to CSV and JSON files.

    Creates:
    - ``<output_dir>/ranking_YYYYMMDD_HHMMSS.csv``  — tabular summary
    - ``<output_dir>/ranking_YYYYMMDD_HHMMSS.json`` — full details

    Parameters
    ----------
    ranked_candidates : list[CandidateScore]
        Ranked candidates.
    jd_req : JDRequirements
        JD requirements (included in JSON output).
    output_dir : str, optional
        Output directory.  Defaults to ``RESULTS_DIR``.

    Returns
    -------
    str
        Path to the output directory.
    """
    if output_dir is None:
        output_dir = RESULTS_DIR

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(output_dir, f"ranking_{timestamp}.csv")
    json_path = os.path.join(output_dir, f"ranking_{timestamp}.json")

    # ── CSV (tabular summary) ────────────────────────────────────────
    df = results_to_dataframe(ranked_candidates)
    df.to_csv(csv_path, index=False, encoding="utf-8")

    # ── JSON (full details) ──────────────────────────────────────────
    json_data = {
        "timestamp": datetime.now().isoformat(),
        "job_description": {
            "title": jd_req.title,
            "required_skills": jd_req.required_skills,
            "preferred_skills": jd_req.preferred_skills,
            "min_experience": jd_req.min_experience,
            "education_level": jd_req.education_level,
            "seniority": jd_req.seniority,
        },
        "total_candidates": len(ranked_candidates),
        "candidates": [],
    }

    for rank, candidate in enumerate(ranked_candidates, start=1):
        candidate_data = {
            "rank": rank,
            "name": candidate.candidate_name,
            "file_name": candidate.file_name,
            "overall_score": candidate.overall_score,
            "scores": {
                "skill_match": candidate.skill_match_score,
                "semantic_similarity": candidate.semantic_similarity,
                "experience": candidate.experience_score,
                "education": candidate.education_score,
                "bonus": candidate.bonus_score,
            },
            "matched_skills": candidate.matched_skills,
            "missing_skills": candidate.missing_skills,
            "extra_skills": candidate.extra_skills,
            "experience_years": candidate.experience_years,
            "explanation": {
                "experience_assessment": candidate.explanation.experience_assessment,
                "strengths": candidate.explanation.strengths,
                "improvement_areas": candidate.explanation.improvement_areas,
                "ranking_reason": candidate.explanation.ranking_reason,
                "score_breakdown": candidate.explanation.score_breakdown,
            },
        }
        json_data["candidates"].append(candidate_data)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    return output_dir


def results_to_dataframe(ranked_candidates: list[CandidateScore]) -> pd.DataFrame:
    """Convert ranked candidates to a pandas DataFrame for display.

    Returns
    -------
    pd.DataFrame
        Columns: Rank, Candidate, File, Overall Score, Skill Match,
        Semantic Similarity, Experience Score, Education Score,
        Matched Skills, Missing Skills, Experience (Years).
    """
    if not ranked_candidates:
        return pd.DataFrame(columns=[
            "Rank", "Candidate", "File", "Overall Score", "Skill Match",
            "Semantic Similarity", "Experience Score", "Education Score",
            "Matched Skills", "Missing Skills", "Experience (Years)",
        ])

    rows = []
    for rank, c in enumerate(ranked_candidates, start=1):
        rows.append({
            "Rank": rank,
            "Candidate": c.candidate_name,
            "File": c.file_name,
            "Overall Score": c.overall_score,
            "Skill Match": c.skill_match_score,
            "Semantic Similarity": c.semantic_similarity,
            "Experience Score": c.experience_score,
            "Education Score": c.education_score,
            "Matched Skills": ", ".join(c.matched_skills) if c.matched_skills else "None",
            "Missing Skills": ", ".join(c.missing_skills) if c.missing_skills else "None",
            "Experience (Years)": c.experience_years,
        })

    return pd.DataFrame(rows)


# ── Private helpers ──────────────────────────────────────────────────────

def _extract_candidate_experience(resume_data: ResumeData) -> float:
    """Extract years of experience from resume text."""
    # Try the experience section first, then full text
    sources = []
    if resume_data.sections.get("experience"):
        sources.append(resume_data.sections["experience"])
    sources.append(resume_data.raw_text)

    for text in sources:
        try:
            years = extract_years_of_experience(text)
            if years is not None and years > 0:
                return years
        except Exception:
            continue

    return 0.0


def _compute_experience_score(resume_years: float, required_years: float) -> float:
    """Compute experience score (0-100).

    - >= required → 100
    - >= 70% of required → 70
    - else → proportional, capped at 100
    """
    if required_years <= 0:
        # No experience requirement — give full marks if candidate has any experience
        return 100.0 if resume_years > 0 else 50.0

    if resume_years >= required_years:
        return 100.0
    elif resume_years >= required_years * 0.7:
        return 70.0
    else:
        score = (resume_years / required_years) * 100.0
        return min(round(score, 2), 100.0)


def _compute_education_score(resume_data: ResumeData, required_level: str) -> float:
    """Compute education score (0-100) based on EDUCATION_LEVELS mapping."""
    if not required_level:
        return 75.0  # No requirement → neutral score

    # Extract candidate's education level
    education_text = resume_data.sections.get("education", "") or resume_data.raw_text
    candidate_level = ""
    try:
        candidate_level = extract_education_level(education_text)
    except Exception:
        pass

    if not candidate_level:
        return 40.0  # Unable to determine → below average

    # Compare using EDUCATION_LEVELS ranking
    required_rank = EDUCATION_LEVELS.get(required_level.lower(), 0)
    candidate_rank = EDUCATION_LEVELS.get(candidate_level.lower(), 0)

    if candidate_rank == 0 and required_rank == 0:
        return 75.0  # Both unknown → neutral
    elif candidate_rank >= required_rank:
        return 100.0
    elif candidate_rank == required_rank - 1:
        return 70.0  # One level below
    else:
        # Further below: proportional
        if required_rank > 0:
            return max(20.0, (candidate_rank / required_rank) * 100.0)
        return 40.0


def _compute_bonus_score(extra_skills: list[str], jd_req: JDRequirements) -> float:
    """Compute bonus score for extra relevant skills (0-100).

    Extra skills that are in the preferred list or are generally desirable
    add to the bonus.
    """
    if not extra_skills:
        return 0.0

    preferred_lower = {s.lower() for s in jd_req.preferred_skills}
    bonus_count = 0

    for skill in extra_skills:
        if skill.lower() in preferred_lower:
            bonus_count += 3  # Higher weight for preferred skills
        else:
            bonus_count += 1  # Any extra skill is somewhat valuable

    # Scale: 5+ bonus-worthy skills → 100
    score = min(100.0, (bonus_count / 5.0) * 100.0)
    return round(score, 2)


def _build_experience_assessment(resume_years: float, required_years: float) -> str:
    """Build a human-readable experience assessment string."""
    if required_years <= 0:
        if resume_years > 0:
            return f"Candidate has {resume_years:.1f} years of experience (no specific requirement)."
        return "No experience information found; no specific requirement stated."

    if resume_years >= required_years:
        return (
            f"Meets experience requirement: {resume_years:.1f} years "
            f"(required: {required_years:.0f}+ years)."
        )
    elif resume_years >= required_years * 0.7:
        return (
            f"Slightly below experience requirement: {resume_years:.1f} years "
            f"(required: {required_years:.0f}+ years), but within acceptable range."
        )
    else:
        return (
            f"Below experience requirement: {resume_years:.1f} years "
            f"(required: {required_years:.0f}+ years)."
        )


def _identify_strengths(
    skill_score: float,
    sim_score: float,
    exp_score: float,
    edu_score: float,
    matched_skills: list,
) -> list[str]:
    """Identify the candidate's key strengths."""
    strengths = []

    if skill_score >= 80:
        strengths.append(f"Strong skill match ({skill_score:.0f}%) with {len(matched_skills)} matching skills.")
    elif skill_score >= 60:
        strengths.append(f"Good skill overlap ({skill_score:.0f}%) with key requirements.")

    if sim_score >= 80:
        strengths.append("High semantic relevance — resume language closely aligns with the JD.")
    elif sim_score >= 60:
        strengths.append("Good semantic relevance to the job description.")

    if exp_score >= 90:
        strengths.append("Experience level meets or exceeds requirements.")

    if edu_score >= 90:
        strengths.append("Education qualification meets or exceeds requirements.")

    if matched_skills:
        top_skills = matched_skills[:5]
        strengths.append(f"Key matched skills: {', '.join(top_skills)}.")

    if not strengths:
        strengths.append("Candidate shows potential with some relevant qualifications.")

    return strengths


def _identify_improvement_areas(
    missing_skills: list,
    resume_years: float,
    jd_req: JDRequirements,
) -> list[str]:
    """Identify areas where the candidate could improve."""
    areas = []

    if missing_skills:
        if len(missing_skills) <= 3:
            areas.append(f"Missing skills: {', '.join(missing_skills)}.")
        else:
            areas.append(
                f"Missing {len(missing_skills)} required skills including: "
                f"{', '.join(missing_skills[:3])}."
            )

    if jd_req.min_experience > 0 and resume_years < jd_req.min_experience:
        gap = jd_req.min_experience - resume_years
        areas.append(f"Needs approximately {gap:.0f} more year(s) of experience.")

    if not areas:
        areas.append("No significant gaps identified.")

    return areas


def _generate_ranking_reason_text(
    candidate: CandidateScore,
    rank: int,
    total: int,
) -> str:
    """Generate a natural-language ranking reason."""
    parts = [f"Candidate ranked #{rank} of {total}"]

    # Highlight the strongest dimension
    scores = {
        "skill match": candidate.skill_match_score,
        "semantic relevance": candidate.semantic_similarity,
        "experience": candidate.experience_score,
        "education": candidate.education_score,
    }
    strongest = max(scores, key=scores.get)
    strongest_val = scores[strongest]

    parts.append(
        f"with an overall score of {candidate.overall_score:.1f}%."
    )

    if strongest_val >= 70:
        parts.append(
            f"Strongest area: {strongest} ({strongest_val:.0f}%)."
        )

    if candidate.matched_skills:
        top = candidate.matched_skills[:3]
        parts.append(f"Key matched skills: {', '.join(top)}.")

    if candidate.experience_years > 0:
        parts.append(f"Experience: {candidate.experience_years:.1f} years.")

    return " ".join(parts)


def _create_fallback_score(resume_data: ResumeData) -> CandidateScore:
    """Create a minimal CandidateScore for candidates that fail scoring."""
    explanation = MatchExplanation(
        matched_skills=[],
        missing_skills=[],
        extra_skills=[],
        experience_assessment="Unable to fully assess candidate.",
        strengths=["Resume was parsed but scoring encountered an issue."],
        improvement_areas=["Unable to determine improvement areas."],
        ranking_reason="Scored with fallback due to processing error.",
        score_breakdown={
            "skill_match": 0.0,
            "semantic": 0.0,
            "experience": 0.0,
            "education": 0.0,
            "bonus": 0.0,
        },
    )
    return CandidateScore(
        candidate_name=resume_data.name,
        file_name=resume_data.file_name,
        overall_score=0.0,
        skill_match_score=0.0,
        semantic_similarity=0.0,
        experience_score=0.0,
        education_score=0.0,
        bonus_score=0.0,
        matched_skills=[],
        missing_skills=[],
        extra_skills=[],
        experience_years=0.0,
        explanation=explanation,
        resume_data=resume_data,
    )
