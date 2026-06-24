"""
Explainability module.

Generates human-readable explanations for candidate rankings, including
per-candidate reasoning, comparative analysis across candidates, and
actionable improvement suggestions.
"""

from core import MatchExplanation, CandidateScore, JDRequirements


def generate_explanation(
    candidate: CandidateScore,
    jd_req: JDRequirements,
    rank: int,
) -> MatchExplanation:
    """Generate a detailed, human-readable explanation for a candidate's ranking.

    The ``MatchExplanation`` is partially built during scoring; this function
    enriches it with the ``ranking_reason`` and any additional comparative
    context.
    """
    explanation = candidate.explanation

    # Enrich the ranking reason if not already set
    if not explanation.ranking_reason:
        explanation.ranking_reason = generate_ranking_reason(candidate, rank, 0)

    # Augment improvement areas with JD-specific suggestions
    suggestions = generate_improvement_suggestions(candidate, jd_req)
    if suggestions and explanation.improvement_areas == ["No significant gaps identified."]:
        explanation.improvement_areas = suggestions
    elif suggestions:
        # Merge without duplicates
        existing = set(explanation.improvement_areas)
        for s in suggestions:
            if s not in existing:
                explanation.improvement_areas.append(s)

    # ───────────────────────────────────────────────────────────────────────
    # Hackathon high-score features: Recommendation, Summary, Questions, Red flags
    # ───────────────────────────────────────────────────────────────────────
    rec_text, rec_style = get_recommendation(candidate.overall_score)
    candidate.recommendation = rec_text
    candidate.recommendation_style = rec_style
    explanation.recommendation = rec_text
    explanation.recommendation_style = rec_style

    summary = generate_candidate_summary(candidate, jd_req)
    candidate.summary = summary
    explanation.summary = summary

    red_flags = detect_red_flags(candidate, candidate.resume_data, jd_req)
    candidate.red_flags = red_flags
    explanation.red_flags = red_flags

    questions = generate_interview_questions(candidate)
    candidate.interview_questions = questions
    explanation.interview_questions = questions

    return explanation


def generate_ranking_reason(
    candidate: CandidateScore,
    rank: int,
    total: int,
) -> str:
    """Generate a natural-language explanation of why a candidate is at this rank.

    Examples
    --------
    "Candidate ranked #1 because of strong skill overlap (92%), 3 years of
    relevant experience meeting the 2+ year requirement, and demonstrated
    expertise in Machine Learning and Python."

    Parameters
    ----------
    candidate : CandidateScore
        Scored candidate.
    rank : int
        1-based rank.
    total : int
        Total number of candidates (0 if unknown).

    Returns
    -------
    str
    """
    parts: list[str] = []

    # Opening
    if total > 0:
        parts.append(f"Candidate ranked #{rank} of {total}")
    else:
        parts.append(f"Candidate ranked #{rank}")

    # Skill match rationale
    reasons: list[str] = []

    if candidate.skill_match_score >= 80:
        reasons.append(
            f"strong skill overlap ({candidate.skill_match_score:.0f}%)"
        )
    elif candidate.skill_match_score >= 50:
        reasons.append(
            f"moderate skill overlap ({candidate.skill_match_score:.0f}%)"
        )
    elif candidate.skill_match_score > 0:
        reasons.append(
            f"limited skill overlap ({candidate.skill_match_score:.0f}%)"
        )

    # Experience rationale
    if candidate.experience_years > 0:
        reasons.append(
            f"{candidate.experience_years:.1f} years of relevant experience"
        )

    # Semantic relevance
    if candidate.semantic_similarity >= 70:
        reasons.append("high semantic alignment with the job description")
    elif candidate.semantic_similarity >= 45:
        reasons.append("reasonable semantic alignment with the job description")

    # Key matched skills
    if candidate.matched_skills:
        top_skills = candidate.matched_skills[:4]
        reasons.append(
            f"demonstrated expertise in {_join_with_and(top_skills)}"
        )

    # Assemble
    if reasons:
        parts.append("because of " + ", ".join(reasons) + ".")
    else:
        parts.append(
            f"with an overall score of {candidate.overall_score:.1f}%."
        )

    return " ".join(parts)


def generate_comparative_analysis(
    candidates: list[CandidateScore],
    jd_req: JDRequirements,
) -> str:
    """Generate a summary comparing the top candidates.

    Example
    -------
    "Alice (92%) leads with the strongest skill match and ideal experience
    level. Bob (87%) shows strong semantic relevance but uses different
    terminology. Carol (75%) has partial skill overlap with growth potential."

    Parameters
    ----------
    candidates : list[CandidateScore]
        Ranked candidates (best first).
    jd_req : JDRequirements
        JD requirements.

    Returns
    -------
    str
        Multi-sentence comparative analysis.
    """
    if not candidates:
        return "No candidates to compare."

    if len(candidates) == 1:
        c = candidates[0]
        return (
            f"{c.candidate_name} ({c.overall_score:.0f}%) is the only candidate. "
            f"{_single_candidate_summary(c, jd_req)}"
        )

    paragraphs: list[str] = []
    top_n = min(len(candidates), 5)  # Analyse up to the top 5

    for i, c in enumerate(candidates[:top_n]):
        rank = i + 1
        paragraph = _build_candidate_paragraph(c, rank, candidates, jd_req)
        paragraphs.append(paragraph)

    # Add an overall summary
    best = candidates[0]
    if len(candidates) >= 2:
        runner_up = candidates[1]
        gap = best.overall_score - runner_up.overall_score
        if gap < 5:
            summary = (
                f"The top {min(3, len(candidates))} candidates are closely matched "
                f"(within {gap:.0f}% of each other). "
                "Interviews are recommended to differentiate further."
            )
        else:
            summary = (
                f"{best.candidate_name} stands out as the clear frontrunner "
                f"with a {gap:.0f}% lead over {runner_up.candidate_name}."
            )
        paragraphs.append(summary)

    return " ".join(paragraphs)


def generate_improvement_suggestions(
    candidate: CandidateScore,
    jd_req: JDRequirements,
) -> list[str]:
    """Suggest how a candidate could improve their fit for this role.

    Examples
    --------
    - "Gain experience with SQL databases"
    - "Add 1-2 more years of industry experience"

    Parameters
    ----------
    candidate : CandidateScore
        Scored candidate.
    jd_req : JDRequirements
        JD requirements.

    Returns
    -------
    list[str]
        Actionable suggestions, may be empty.
    """
    suggestions: list[str] = []

    # ── Missing skills ───────────────────────────────────────────────
    if candidate.missing_skills:
        for skill in candidate.missing_skills[:5]:
            suggestions.append(f"Gain experience with {skill}.")

    # ── Experience gap ───────────────────────────────────────────────
    if jd_req.min_experience > 0 and candidate.experience_years < jd_req.min_experience:
        gap = jd_req.min_experience - candidate.experience_years
        if gap <= 1:
            suggestions.append(
                "Acquire approximately 1 more year of relevant industry experience."
            )
        else:
            suggestions.append(
                f"Acquire approximately {gap:.0f} more years of relevant industry experience."
            )

    # ── Education gap ────────────────────────────────────────────────
    if candidate.education_score < 70 and jd_req.education_level:
        suggestions.append(
            f"Consider pursuing a {jd_req.education_level} degree or equivalent certification."
        )

    # ── Semantic alignment ───────────────────────────────────────────
    if candidate.semantic_similarity < 40:
        suggestions.append(
            "Tailor resume language to match the job description more closely "
            "(use similar terminology and keywords)."
        )

    # ── Bonus skills ─────────────────────────────────────────────────
    if jd_req.preferred_skills:
        missing_preferred = [
            s for s in jd_req.preferred_skills
            if s not in candidate.matched_skills and s not in candidate.extra_skills
        ]
        if missing_preferred:
            top_preferred = missing_preferred[:3]
            suggestions.append(
                f"Build proficiency in preferred skills: {', '.join(top_preferred)}."
            )

    return suggestions


# ── Private helpers ──────────────────────────────────────────────────────

def _join_with_and(items: list[str]) -> str:
    """Join a list of strings with commas and 'and' before the last item."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _single_candidate_summary(c: CandidateScore, jd_req: JDRequirements) -> str:
    """Build a summary sentence for a single candidate."""
    parts: list[str] = []
    if c.matched_skills:
        parts.append(
            f"Shows strength in {_join_with_and(c.matched_skills[:3])}"
        )
    if c.experience_years > 0:
        parts.append(f"with {c.experience_years:.1f} years of experience")
    if c.missing_skills:
        parts.append(f"but is missing {_join_with_and(c.missing_skills[:3])}")

    return ". ".join(parts) + "." if parts else "No additional details available."


def _build_candidate_paragraph(
    c: CandidateScore,
    rank: int,
    all_candidates: list[CandidateScore],
    jd_req: JDRequirements,
) -> str:
    """Build a comparative paragraph for a single candidate."""
    parts: list[str] = [f"{c.candidate_name} ({c.overall_score:.0f}%)"]

    if rank == 1:
        # Leader
        strongest = _strongest_dimension(c)
        parts.append(f"leads with the {strongest}")
    elif rank == 2:
        # Runner-up: contrast with the leader
        leader = all_candidates[0]
        advantage = _find_advantage_over(c, leader)
        if advantage:
            parts.append(f"is a strong contender with {advantage}")
        else:
            parts.append("is a close runner-up")
    else:
        # Lower ranks
        if c.overall_score >= 70:
            parts.append("is a solid candidate")
        elif c.overall_score >= 50:
            parts.append("shows potential with room for growth")
        else:
            parts.append("has limited alignment with the role")

    # Add a detail
    if c.matched_skills:
        key_skill = c.matched_skills[0]
        parts.append(f"(notable skill: {key_skill})")

    if c.missing_skills and rank > 1:
        parts.append(f"but is missing {c.missing_skills[0]}")

    return " ".join(parts) + "."


def _strongest_dimension(c: CandidateScore) -> str:
    """Identify the candidate's strongest scoring dimension in words."""
    dimensions = {
        "strongest skill match": c.skill_match_score,
        "highest semantic relevance": c.semantic_similarity,
        "most experience": c.experience_score,
        "best educational qualifications": c.education_score,
    }
    best_label = max(dimensions, key=dimensions.get)
    return best_label


def _find_advantage_over(candidate: CandidateScore, leader: CandidateScore) -> str:
    """Find a dimension where *candidate* outperforms the *leader*."""
    comparisons = [
        ("stronger skill match", candidate.skill_match_score, leader.skill_match_score),
        ("higher semantic relevance", candidate.semantic_similarity, leader.semantic_similarity),
        ("more experience", candidate.experience_score, leader.experience_score),
        ("better education fit", candidate.education_score, leader.education_score),
    ]
    for label, cand_val, lead_val in comparisons:
        if cand_val > lead_val:
            return label
    return ""


# ───────────────────────────────────────────────────────────────────────────
# Hackathon High-Score Helper Functions
# ───────────────────────────────────────────────────────────────────────────

def get_recommendation(score: float) -> tuple[str, str]:
    """Return recommendation label and CSS styling based on overall score."""
    if score >= 85:
        return "Highly Recommended", "background-color: rgba(16, 185, 129, 0.12); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.35);"
    elif score >= 70:
        return "Recommended", "background-color: rgba(6, 182, 212, 0.12); color: #06B6D4; border: 1px solid rgba(6, 182, 212, 0.35);"
    elif score >= 50:
        return "Consider", "background-color: rgba(245, 158, 11, 0.12); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.35);"
    else:
        return "Not Recommended", "background-color: rgba(239, 68, 68, 0.12); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.35);"


def generate_candidate_summary(candidate: CandidateScore, jd_req: JDRequirements) -> str:
    """Generate a recruiter-friendly candidate fit summary paragraph."""
    score = candidate.overall_score
    if score >= 85:
        recommendation = "highly recommended"
        suitability = "is an excellent fit for the role, demonstrating a high degree of technical alignment and meeting or exceeding key requirements. They are highly suitable for a technical interview."
    elif score >= 70:
        recommendation = "recommended"
        suitability = "is a strong match for this role, showing good competency overlap and relevant qualifications. They are recommended for further screening or technical assessment."
    elif score >= 50:
        recommendation = "suitable for consideration"
        suitability = "meets some core requirements but exhibits some notable skill or experience gaps. They could be considered for screening if additional context aligns."
    else:
        recommendation = "not recommended"
        suitability = "has limited alignment with the core requirements of this role at this time, showing significant gaps in required skills or experience."

    matched_top = candidate.matched_skills[:4]
    matched_str = f" possessing core skills in {', '.join(matched_top)}" if matched_top else ""

    exp_str = f"With {candidate.experience_years:.1f} years of relevant experience"
    if jd_req.min_experience > 0:
        if candidate.experience_years >= jd_req.min_experience:
            exp_str += f" (meeting the required {jd_req.min_experience:.0f}+ years)"
        else:
            exp_str += f" (which is slightly below the required {jd_req.min_experience:.0f}+ years)"

    summary = f"{candidate.candidate_name} is {recommendation} for the {jd_req.title} position. {exp_str}{matched_str}, their profile {suitability}"

    if candidate.education_score >= 90:
        summary += " Their educational background aligns well with the position's requirements."

    if candidate.missing_skills:
        missing_top = candidate.missing_skills[:3]
        summary += f" Key areas for potential development include {', '.join(missing_top)}."

    return summary


def detect_red_flags(candidate: CandidateScore, resume_data, jd_req: JDRequirements) -> list[str]:
    """Analyze the candidate score and resume data to identify potential concerns or red flags."""
    red_flags = []

    # 1. Check if contact info is missing
    email = getattr(resume_data, "email", "")
    phone = getattr(resume_data, "phone", "")
    if not email:
        red_flags.append("Missing email address.")
    if not phone:
        red_flags.append("Missing phone number.")
    if not getattr(resume_data, "linkedin", ""):
        red_flags.append("No LinkedIn profile detected.")

    # 2. Check if experience section or projects is missing
    sections = getattr(resume_data, "sections", {})
    if not sections.get("experience"):
        red_flags.append("No explicit Work Experience section found.")
    if not sections.get("projects"):
        red_flags.append("No Projects section found in the resume.")

    # 3. Check for low years of experience
    if jd_req.min_experience > 0 and candidate.experience_years < jd_req.min_experience:
        red_flags.append(f"Experience level ({candidate.experience_years:.1f} yrs) is below the minimum required ({jd_req.min_experience:.0f}+ yrs).")

    # 4. Check for low skills match
    if candidate.skill_match_score < 40:
        red_flags.append("Very low skills overlap with required JD keywords.")

    if not red_flags:
        red_flags.append("No critical concerns detected.")

    return red_flags


def generate_interview_questions(candidate: CandidateScore) -> list[str]:
    """Tailor three high-quality interview questions based on candidate's matched skills."""
    skill_questions = {
        "python": [
            "What is the difference between list and tuple in Python?",
            "Explain decorators and how they are used in Python.",
            "How does memory management work in Python (garbage collection)?"
        ],
        "machine learning": [
            "Explain the trade-off between bias and variance.",
            "What is overfitting and how do you prevent it?",
            "Describe how a Random Forest classifier works."
        ],
        "tensorflow": [
            "What is a tensor and how does it differ from a NumPy array?",
            "Explain the purpose of the compile and fit methods in Keras/TensorFlow.",
            "What is transfer learning and how do you implement it in TensorFlow?"
        ],
        "pytorch": [
            "Explain the concept of autograd (automatic differentiation) in PyTorch.",
            "What is the difference between Dataset and DataLoader in PyTorch?",
            "How do you move a tensor or model to GPU in PyTorch?"
        ],
        "scikit-learn": [
            "How do you perform cross-validation using Scikit-Learn?",
            "What is the difference between fit, transform, and fit_transform in Scikit-Learn?",
            "Explain how you would handle missing data using Scikit-Learn's SimpleImputer."
        ],
        "sql": [
            "What is the difference between INNER JOIN, LEFT JOIN, and outer joins?",
            "Explain database normalization (1NF, 2NF, 3NF).",
            "What are database indexes and how do they speed up query execution?"
        ],
        "react": [
            "Explain the Virtual DOM and how React reconciles differences.",
            "What is the difference between state and props in React?",
            "How do React hooks like useEffect and useState work?"
        ],
        "node.js": [
            "What is the event loop in Node.js and how does it handle asynchronous operations?",
            "Explain the difference between setImmediate() and process.nextTick().",
            "How do you configure error handling in Express middleware?"
        ],
        "devops": [
            "What is Infrastructure as Code (IaC) and why is it important?",
            "Explain the differences between Docker containerization and virtualization.",
            "What is a CI/CD pipeline and how do you configure automated deployments?"
        ],
        "kubernetes": [
            "What is a Pod in Kubernetes and how does it relate to Containers?",
            "Explain the purpose of a ReplicaSet and a Deployment in Kubernetes.",
            "How does service discovery and load balancing work within a Kubernetes cluster?"
        ],
        "aws": [
            "Explain the differences between EC2, S3, and Lambda on AWS.",
            "What is an IAM role and how is it used to secure AWS resources?",
            "Describe how you would design a highly available architecture on AWS."
        ]
    }

    general_questions = [
        "Describe a challenging technical project you worked on and how you resolved issues.",
        "Explain the difference between SQL and NoSQL databases, and when to use which.",
        "What is Git and how do you resolve merge conflicts?"
    ]

    selected_questions = []
    matched_lower = [s.lower() for s in candidate.matched_skills]

    # Pull 1 question from up to 3 matched skills
    for skill_key, questions in skill_questions.items():
        if skill_key in matched_lower:
            selected_questions.append(questions[len(selected_questions) % len(questions)])
            if len(selected_questions) >= 3:
                break

    # If we still have less than 3 questions, fill with general ones
    while len(selected_questions) < 3:
        next_q = general_questions[len(selected_questions) % len(general_questions)]
        if next_q not in selected_questions:
            selected_questions.append(next_q)
        else:
            break

    return selected_questions

