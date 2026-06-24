"""
Skill extraction module.

Provides multi-pass skill extraction from free text and resume objects,
skill overlap computation, and skill-match scoring.
"""

import re
from typing import Optional

from data.skills_database import (
    SKILLS_DB,
    SKILL_ALIASES,
    normalize_skill,
    get_skill_category,
    get_all_skills,
)


def extract_skills(text: str) -> list[dict]:
    """Extract skills from arbitrary text using a multi-pass approach.

    Returns
    -------
    list[dict]
        Each dict has keys:
        - ``skill``  : str — canonical skill name
        - ``category``: str — skill category (e.g., "programming", "cloud")
        - ``source``  : str — how it was matched ("exact", "alias", or "ngram")

    Algorithm
    ---------
    1. Normalize the input text to lowercase.
    2. **Exact match pass** — check every skill in ``SKILLS_DB`` against the
       text.  Longer skill names are checked first so that "machine learning"
       is matched before "machine".
    3. **Alias match pass** — check every alias in ``SKILL_ALIASES``.
    4. **N-gram pass** — generate bigrams / trigrams from the text tokens and
       match them against the skills database.
    5. De-duplicate results by canonical skill name, keeping the first
       (highest-priority) source.
    """
    if not text or not text.strip():
        return []

    text_lower = text.lower()
    # Replace common separators with spaces so that "Python/Java" → "python java"
    text_normalized = re.sub(r"[/|•·,;]", " ", text_lower)
    text_normalized = re.sub(r"\s+", " ", text_normalized).strip()

    found: dict[str, dict] = {}  # canonical_name -> result dict

    # ── Pass 1: Exact matches (longest first) ────────────────────────
    all_skills = get_all_skills()
    # Sort by length descending so "machine learning" is tried before "machine"
    all_skills_sorted = sorted(all_skills, key=len, reverse=True)

    for skill_name in all_skills_sorted:
        if skill_name.lower() in found:
            continue
        pattern = _build_word_pattern(skill_name)
        if pattern.search(text_normalized):
            canonical = skill_name
            found[canonical.lower()] = {
                "skill": canonical,
                "category": get_skill_category(canonical),
                "source": "exact",
            }

    # ── Pass 2: Alias matches ────────────────────────────────────────
    aliases_sorted = sorted(SKILL_ALIASES.keys(), key=len, reverse=True)
    for alias in aliases_sorted:
        canonical = SKILL_ALIASES[alias]
        if canonical.lower() in found:
            continue
        pattern = _build_word_pattern(alias)
        if pattern.search(text_normalized):
            found[canonical.lower()] = {
                "skill": canonical,
                "category": get_skill_category(canonical),
                "source": "alias",
            }

    # ── Pass 3: N-gram matching ──────────────────────────────────────
    tokens = text_normalized.split()
    ngrams = _generate_ngrams(tokens, max_n=3)
    for ngram in ngrams:
        normalized = normalize_skill(ngram)
        if normalized and normalized.lower() not in found:
            found[normalized.lower()] = {
                "skill": normalized,
                "category": get_skill_category(normalized),
                "source": "ngram",
            }

    return list(found.values())


def extract_skills_from_resume(resume_data) -> list[dict]:
    """Extract skills from a ``ResumeData`` object.

    The skills section is given highest priority, but the experience and
    projects sections are also scanned to capture skills mentioned only in
    context.

    Parameters
    ----------
    resume_data : core.ResumeData
        Parsed resume data.

    Returns
    -------
    list[dict]
        Same format as :func:`extract_skills`.
    """
    found: dict[str, dict] = {}

    # Priority order: skills section first, then experience, then projects, then full text
    sections_to_scan = []

    if hasattr(resume_data, "sections") and isinstance(resume_data.sections, dict):
        skills_text = resume_data.sections.get("skills", "")
        if skills_text:
            sections_to_scan.append(skills_text)

        experience_text = resume_data.sections.get("experience", "")
        if experience_text:
            sections_to_scan.append(experience_text)

        projects_text = resume_data.sections.get("projects", "")
        if projects_text:
            sections_to_scan.append(projects_text)

    # Fallback: scan the full raw text if no sections yielded results
    if not sections_to_scan and hasattr(resume_data, "raw_text"):
        sections_to_scan.append(resume_data.raw_text)

    for section_text in sections_to_scan:
        results = extract_skills(section_text)
        for item in results:
            key = item["skill"].lower()
            if key not in found:
                found[key] = item

    # If we still found nothing, try the full raw text as a last resort
    if not found and hasattr(resume_data, "raw_text") and resume_data.raw_text:
        for item in extract_skills(resume_data.raw_text):
            key = item["skill"].lower()
            if key not in found:
                found[key] = item

    return list(found.values())


def get_skill_overlap(
    resume_skills: list[str],
    jd_skills: list[str],
) -> tuple[list[str], list[str], list[str]]:
    """Compare resume skills against job-description requirements.

    Uses the ``related`` field in ``SKILLS_DB`` for fuzzy matching:
    for example, if the JD requires "machine learning" and the resume has
    "deep learning", it counts as a partial match because they are related.

    Parameters
    ----------
    resume_skills : list[str]
        Canonical skill names found in the resume.
    jd_skills : list[str]
        Canonical skill names required/preferred in the JD.

    Returns
    -------
    tuple[list[str], list[str], list[str]]
        ``(matched_skills, missing_skills, extra_skills)``
    """
    if not jd_skills:
        return [], [], list(resume_skills)

    resume_set = {s.lower() for s in resume_skills}
    jd_set = {s.lower() for s in jd_skills}

    # Build a map from each JD skill to the resume skill that satisfies it
    matched: list[str] = []
    missing: list[str] = []

    for jd_skill in jd_skills:
        jd_lower = jd_skill.lower()

        # Direct match
        if jd_lower in resume_set:
            matched.append(jd_skill)
            continue

        # Related-skill match
        related_match = _find_related_match(jd_lower, resume_set)
        if related_match:
            matched.append(jd_skill)
            continue

        missing.append(jd_skill)

    # Extra skills = resume skills not in JD (direct or related)
    jd_expanded = set()
    for jd_skill in jd_skills:
        jd_lower = jd_skill.lower()
        jd_expanded.add(jd_lower)
        # Add related skills too
        info = SKILLS_DB.get(jd_lower, SKILLS_DB.get(jd_skill, {}))
        if isinstance(info, dict):
            for r in info.get("related", []):
                jd_expanded.add(r.lower())

    extra = [s for s in resume_skills if s.lower() not in jd_expanded]

    return matched, missing, extra


def calculate_skill_match_score(
    matched: list,
    missing: list,
    required_skills: list,
) -> float:
    """Calculate skill match percentage (0–100).

    Parameters
    ----------
    matched : list
        Skills that the candidate has which match the JD.
    missing : list
        Required JD skills not found in the candidate's resume.
    required_skills : list
        All required skills from the JD.

    Returns
    -------
    float
        Score from 0 to 100.
    """
    total = len(required_skills)
    if total == 0:
        return 100.0  # No requirements ⇒ perfect score

    score = (len(matched) / total) * 100.0
    return min(round(score, 2), 100.0)


# ── Private helpers ──────────────────────────────────────────────────────

def _build_word_pattern(skill: str) -> re.Pattern:
    """Build a regex that matches *skill* as a whole-word / phrase in text.

    Special characters in the skill name (e.g. ``C++``, ``C#``, ``.NET``)
    are properly escaped.
    """
    escaped = re.escape(skill.lower())
    # For very short tokens like 'R' or 'C', require strict word boundaries
    if len(skill) <= 2:
        return re.compile(r"(?<![a-zA-Z])" + escaped + r"(?![a-zA-Z])", re.IGNORECASE)
    return re.compile(r"\b" + escaped + r"\b", re.IGNORECASE)


def _generate_ngrams(tokens: list[str], max_n: int = 3) -> list[str]:
    """Generate n-grams (n = 2 … max_n) from a list of tokens."""
    ngrams: list[str] = []
    for n in range(2, max_n + 1):
        for i in range(len(tokens) - n + 1):
            ngrams.append(" ".join(tokens[i : i + n]))
    return ngrams


def _find_related_match(jd_skill_lower: str, resume_set: set[str]) -> Optional[str]:
    """Check if any skill in *resume_set* is related to *jd_skill_lower*.

    Looks up the ``related`` field in ``SKILLS_DB`` for the JD skill and
    checks if any of those related skills appear in the resume.  Also
    performs the reverse check: for each resume skill, see if the JD skill
    appears in *its* related list.
    """
    # Forward: JD skill → related skills → check resume
    info = SKILLS_DB.get(jd_skill_lower, {})
    if isinstance(info, dict):
        for related in info.get("related", []):
            if related.lower() in resume_set:
                return related

    # Reverse: resume skill → related skills → contains JD skill?
    for resume_skill in resume_set:
        info = SKILLS_DB.get(resume_skill, {})
        if isinstance(info, dict):
            related_lower = [r.lower() for r in info.get("related", [])]
            if jd_skill_lower in related_lower:
                return resume_skill

    return None
