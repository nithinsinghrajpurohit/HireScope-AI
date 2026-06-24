"""
Job Description analyzer module.

Parses raw job description text and produces a structured ``JDRequirements``
object containing title, skills, experience, education, and seniority.
"""

import re
from typing import Optional

from core import JDRequirements
from core.skill_extractor import extract_skills
from utils.text_processing import extract_years_of_experience, extract_education_level


# ── Section-boundary patterns for JDs ────────────────────────────────────

_REQUIRED_HEADERS = re.compile(
    r"(?:required|must[\s-]*have|minimum|essential|key)\s*(?:skills|qualifications|requirements|competencies|experience)?",
    re.IGNORECASE,
)
_PREFERRED_HEADERS = re.compile(
    r"(?:preferred|nice[\s-]*to[\s-]*have|desirable|bonus|good[\s-]*to[\s-]*have|optional|additional)\s*(?:skills|qualifications|requirements)?",
    re.IGNORECASE,
)

_TITLE_PATTERNS = [
    re.compile(r"(?:job\s*title|position|role)\s*[:–—-]\s*(.+)", re.IGNORECASE),
    re.compile(r"^(?:hiring|we(?:'re| are)\s+(?:looking|hiring)\s+(?:for\s+)?(?:a\s+)?)\s*(.+)", re.IGNORECASE),
]

_SENIORITY_KEYWORDS = {
    "junior": ["junior", "jr", "intern", "entry level", "entry-level", "graduate", "fresher", "trainee"],
    "mid": ["mid", "mid-level", "mid level", "associate", "intermediate"],
    "senior": ["senior", "sr", "lead", "staff", "principal"],
    "lead": ["director", "vp", "vice president", "head of", "chief", "cto", "cio", "architect"],
}

_EXPERIENCE_RANGE = re.compile(
    r"(\d+)\s*[-–—to]+\s*(\d+)\s*(?:\+)?\s*(?:years?|yrs?)",
    re.IGNORECASE,
)
_EXPERIENCE_MIN = re.compile(
    r"(\d+)\s*\+?\s*(?:years?|yrs?)",
    re.IGNORECASE,
)


def analyze_jd(jd_text: str) -> JDRequirements:
    """Parse and analyze a job description.

    Steps
    -----
    1. Extract job title.
    2. Split into required vs. preferred skill sections.
    3. Extract skills from each section.
    4. Extract experience requirement.
    5. Extract education requirement.
    6. Determine seniority level.

    Parameters
    ----------
    jd_text : str
        Raw job description text.

    Returns
    -------
    JDRequirements
    """
    if not jd_text or not jd_text.strip():
        return JDRequirements(
            title="Unknown Position",
            required_skills=[],
            preferred_skills=[],
            min_experience=0.0,
            education_level="",
            raw_text="",
            seniority="mid",
        )

    title = _extract_title(jd_text)
    required_text, preferred_text = _split_requirement_sections(jd_text)

    # Extract skills from the separated sections
    required_skill_dicts = extract_skills(required_text)
    preferred_skill_dicts = extract_skills(preferred_text) if preferred_text else []

    required_skills = _deduplicate_skill_names(
        [s["skill"] for s in required_skill_dicts]
    )
    preferred_skills = _deduplicate_skill_names(
        [s["skill"] for s in preferred_skill_dicts if s["skill"] not in required_skills]
    )

    # If no preferred/required split was found, treat everything as required
    if not required_skills and not preferred_skills:
        all_skills = extract_skills(jd_text)
        required_skills = _deduplicate_skill_names([s["skill"] for s in all_skills])

    min_experience = _extract_experience(jd_text)
    education_level = _safe_call(extract_education_level, jd_text)
    seniority = _determine_seniority(title, jd_text, min_experience)

    return JDRequirements(
        title=title,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        min_experience=min_experience,
        education_level=education_level,
        raw_text=jd_text,
        seniority=seniority,
    )


# ── Private helpers ──────────────────────────────────────────────────────

def _extract_title(text: str) -> str:
    """Extract job title from the JD text.

    Tries explicit patterns first (``Job Title: …``), then falls back to the
    first non-empty line as a heuristic.
    """
    for pattern in _TITLE_PATTERNS:
        m = pattern.search(text)
        if m:
            title = m.group(1).strip().rstrip(".")
            if 3 <= len(title) <= 120:
                return title

    # Fallback: first non-empty, non-trivial line
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and len(stripped) < 120 and not stripped.startswith(("http", "www")):
            # Skip lines that look like company names / dates
            if re.match(r"^\d", stripped):
                continue
            return stripped.rstrip(".")

    return "Unknown Position"


def _split_requirement_sections(text: str) -> tuple[str, str]:
    """Split the JD into required-skills text and preferred-skills text.

    If no clear split is found, the entire text is returned as the
    required section and the preferred section is empty.
    """
    lines = text.split("\n")
    required_lines: list[str] = []
    preferred_lines: list[str] = []
    current_bucket: Optional[list[str]] = None

    for line in lines:
        stripped = line.strip()

        if _REQUIRED_HEADERS.search(stripped):
            current_bucket = required_lines
            continue
        elif _PREFERRED_HEADERS.search(stripped):
            current_bucket = preferred_lines
            continue

        if current_bucket is not None:
            current_bucket.append(stripped)

    required_text = "\n".join(required_lines).strip()
    preferred_text = "\n".join(preferred_lines).strip()

    # If nothing was captured in the required bucket, use the whole text
    if not required_text:
        required_text = text

    return required_text, preferred_text


def _extract_experience(text: str) -> float:
    """Extract minimum years of experience from JD text.

    Handles patterns like:
    - "3+ years"
    - "3-5 years of experience"
    - "minimum 2 years"
    """
    # Try range first ("3-5 years")
    m = _EXPERIENCE_RANGE.search(text)
    if m:
        return float(m.group(1))

    # Try the utility function
    try:
        years = extract_years_of_experience(text)
        if years and years > 0:
            return years
    except Exception:
        pass

    # Try simple pattern
    m = _EXPERIENCE_MIN.search(text)
    if m:
        return float(m.group(1))

    return 0.0


def _determine_seniority(title: str, text: str, min_experience: float) -> str:
    """Determine seniority level from title keywords and experience.

    Priority: explicit keywords in the title > keywords in the full text >
    experience-based heuristic.
    """
    combined = (title + " " + text).lower()

    # Check title first (more reliable)
    title_lower = title.lower()

    # Check from most senior to least
    for level in ("lead", "senior", "mid", "junior"):
        for keyword in _SENIORITY_KEYWORDS[level]:
            if keyword in title_lower:
                return level

    # Check the broader text
    for level in ("lead", "senior", "mid", "junior"):
        for keyword in _SENIORITY_KEYWORDS[level]:
            # Use word boundary matching to avoid false positives
            if re.search(r"\b" + re.escape(keyword) + r"\b", combined):
                return level

    # Fall back to experience-based heuristic
    if min_experience >= 10:
        return "lead"
    elif min_experience >= 5:
        return "senior"
    elif min_experience >= 2:
        return "mid"
    elif min_experience > 0:
        return "junior"

    return "mid"  # Default


def _deduplicate_skill_names(skills: list[str]) -> list[str]:
    """Remove duplicate skill names (case-insensitive), preserving order."""
    seen: set[str] = set()
    result: list[str] = []
    for s in skills:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            result.append(s)
    return result


def _safe_call(func, text: str) -> str:
    """Call a function safely, returning empty string on failure."""
    try:
        result = func(text)
        return result if result else ""
    except Exception:
        return ""
