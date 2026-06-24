"""
Constants and configuration for HireScope AI.
Centralized configuration for scoring weights, matching modes, and application settings.
"""

APP_TITLE = "HireScope AI"
APP_ICON = "🎯"
APP_DESCRIPTION = "Intelligent Candidate Discovery & Ranking System"

# ---------------------------------------------------------------------------
# Scoring Weights (must sum to 1.0)
# ---------------------------------------------------------------------------
SKILL_MATCH_WEIGHT = 0.40
SEMANTIC_SIMILARITY_WEIGHT = 0.25
EXPERIENCE_WEIGHT = 0.20
EDUCATION_WEIGHT = 0.10
BONUS_WEIGHT = 0.05

# ---------------------------------------------------------------------------
# Matching Modes
# ---------------------------------------------------------------------------
MODE_TFIDF = "TF-IDF (Phase 1)"
MODE_SEMANTIC = "Semantic (Phase 2)"

# ---------------------------------------------------------------------------
# Supported File Types
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = [".pdf", ".txt"]

# ---------------------------------------------------------------------------
# Education Levels (ranked by level for scoring)
# ---------------------------------------------------------------------------
EDUCATION_LEVELS = {
    "phd": 5,
    "doctorate": 5,
    "master": 4,
    "mba": 4,
    "bachelor": 3,
    "associate": 2,
    "diploma": 1,
    "high school": 0,
}

# ---------------------------------------------------------------------------
# Results Directory
# ---------------------------------------------------------------------------
RESULTS_DIR = "results"

# ---------------------------------------------------------------------------
# Resume Section Headers (regex-friendly)
# ---------------------------------------------------------------------------
SECTION_PATTERNS = {
    "skills": [
        r"(?i)\b(technical\s+skills|skills|core\s+competencies|competencies|technologies|tech\s+stack)\b"
    ],
    "experience": [
        r"(?i)\b(work\s+experience|experience|professional\s+experience|employment\s+history|work\s+history)\b"
    ],
    "education": [
        r"(?i)\b(education|academic|qualifications|degrees?|university|college)\b"
    ],
    "projects": [
        r"(?i)\b(projects?|personal\s+projects?|academic\s+projects?|key\s+projects?)\b"
    ],
    "certifications": [
        r"(?i)\b(certifications?|certificates?|accreditations?|licenses?)\b"
    ],
    "summary": [
        r"(?i)\b(summary|objective|profile|about\s+me|professional\s+summary)\b"
    ],
}

# ---------------------------------------------------------------------------
# Contact Info Patterns
# ---------------------------------------------------------------------------
EMAIL_PATTERN = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"(?:\+?\d{1,3}[\s\-]?)?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}"
LINKEDIN_PATTERN = r"(?:linkedin\.com/in/|linkedin:\s*)([a-zA-Z0-9\-]+)"

