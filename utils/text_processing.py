"""
Text Processing Utilities for HireScope AI.
Handles text cleaning, tokenization, and information extraction from resumes.
"""

import re
import string

# ---------------------------------------------------------------------------
# NLTK Setup — automatic download of required data packages
# ---------------------------------------------------------------------------
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
except ImportError:
    raise ImportError("NLTK is required. Install it with: pip install nltk")


def _ensure_nltk_data():
    """Download required NLTK data packages if not already available."""
    resources = {
        "punkt": "tokenizers/punkt",
        "punkt_tab": "tokenizers/punkt_tab",
        "stopwords": "corpora/stopwords",
        "averaged_perceptron_tagger": "taggers/averaged_perceptron_tagger",
    }
    for name, path in resources.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=True)


_ensure_nltk_data()

# Cache stopwords for performance
_STOP_WORDS = set(stopwords.words("english"))


# ---------------------------------------------------------------------------
# Text Cleaning
# ---------------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Clean and normalize text for processing.

    - Convert to lowercase
    - Remove special characters (keep letters, numbers, spaces, common punctuation)
    - Collapse multiple whitespace into single space
    - Strip leading/trailing whitespace

    Args:
        text: Raw input text

    Returns:
        Cleaned text string
    """
    if not text or not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove special characters but keep letters, numbers, spaces, and common punctuation
    text = re.sub(r"[^a-z0-9\s\.,;:\-\'\"@/+#&()]", " ", text)

    # Collapse multiple whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Tokenization
# ---------------------------------------------------------------------------
def tokenize_text(text: str) -> list[str]:
    """Tokenize text and remove stopwords.

    Args:
        text: Input text (ideally already cleaned)

    Returns:
        List of meaningful tokens
    """
    if not text or not isinstance(text, str):
        return []

    cleaned = clean_text(text)

    try:
        tokens = word_tokenize(cleaned)
    except Exception:
        # Fallback to simple split if word_tokenize fails
        tokens = cleaned.split()

    # Remove stopwords, punctuation-only tokens, and very short tokens
    tokens = [
        token
        for token in tokens
        if token not in _STOP_WORDS
        and len(token) > 1
        and not all(c in string.punctuation for c in token)
    ]

    return tokens


# ---------------------------------------------------------------------------
# Information Extraction
# ---------------------------------------------------------------------------
def extract_email(text: str) -> str:
    """Extract the first email address found in text.

    Args:
        text: Input text to search

    Returns:
        Email address string or empty string if not found
    """
    if not text:
        return ""

    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Extract the first phone number found in text.

    Handles multiple formats:
    - (123) 456-7890
    - 123-456-7890
    - 123.456.7890
    - +1 123 456 7890
    - 1234567890
    - +91-9876543210

    Args:
        text: Input text to search

    Returns:
        Phone number string or empty string if not found
    """
    if not text:
        return ""

    patterns = [
        r"\+?\d{1,3}[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}",
        r"\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}",
        r"\+?\d{1,3}[\s\-]?\d{4,5}[\s\-]?\d{4,6}",
        r"\d{10,12}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()

    return ""


def extract_years_of_experience(text: str) -> float:
    """Extract years of experience from text.

    Handles patterns like:
    - "3+ years of experience"
    - "3 years experience"
    - "experience: 3 years"
    - "over 5 years"
    - "3.5 years"
    - "three years"

    Args:
        text: Input text to search

    Returns:
        Maximum years of experience found, or 0.0
    """
    if not text:
        return 0.0

    text_lower = text.lower()
    years_found: list[float] = []

    # Number word mapping
    number_words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20,
    }

    # Numeric patterns
    patterns = [
        r"(\d+\.?\d*)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp|work)",
        r"(?:experience|exp)\s*(?:of|:)?\s*(\d+\.?\d*)\+?\s*(?:years?|yrs?)",
        r"(?:over|more than|approximately|approx|nearly|about|around)\s*(\d+\.?\d*)\+?\s*(?:years?|yrs?)",
        r"(\d+\.?\d*)\+?\s*(?:years?|yrs?)\s*(?:in|of|working)",
        r"(\d+\.?\d*)\+?\s*(?:years?|yrs?)\s*(?:professional|industry|total)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                years_found.append(float(match))
            except (ValueError, TypeError):
                continue

    # Word-based patterns ("three years of experience")
    for word, num in number_words.items():
        pattern = rf"{word}\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp|work|in)"
        if re.search(pattern, text_lower):
            years_found.append(float(num))

    return max(years_found) if years_found else 0.0


def extract_name(text: str) -> str:
    """Extract candidate name from resume text.

    Heuristic: Take the first non-empty, non-header line as name.
    Common in resume formats where the name appears at the top.

    Args:
        text: Full resume text

    Returns:
        Extracted name or 'Unknown'
    """
    if not text:
        return "Unknown"

    lines = text.strip().split("\n")

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip lines that look like headers or metadata
        skip_patterns = [
            r"^(resume|curriculum vitae|cv|page|http|www)",
            r"^\d+$",           # Pure numbers
            r"^[\-=_*]{3,}$",   # Separator lines
        ]

        should_skip = False
        for pattern in skip_patterns:
            if re.match(pattern, line.lower()):
                should_skip = True
                break

        if should_skip:
            continue

        # Clean up the name — remove trailing info after separators
        name = re.sub(r"[|\-\u2013\u2014].*$", "", line)
        name = re.sub(
            r"\s*[,.]\s*(phd|md|mba|cpa|pe|esq)\.?\s*$",
            "",
            name,
            flags=re.IGNORECASE,
        )
        name = name.strip()

        if 1 < len(name) < 60:
            return name

    return "Unknown"


def extract_education_level(text: str) -> str:
    """Extract the highest education level mentioned in text.

    Args:
        text: Input text to search

    Returns:
        Highest education level found (e.g., 'phd', 'master', 'bachelor') or 'unknown'
    """
    if not text:
        return "unknown"

    text_lower = text.lower()

    # Education patterns ordered by level (highest first)
    education_patterns = [
        (r"\b(?:ph\.?d|doctorate|doctoral|doctor of philosophy)\b", "phd"),
        (r"\b(?:master|m\.?s\.?|m\.?a\.?|m\.?sc|m\.?eng|mba|m\.?tech|m\.?phil)\b", "master"),
        (r"\b(?:bachelor|b\.?s\.?|b\.?a\.?|b\.?sc|b\.?eng|b\.?tech|b\.?com|undergraduate)\b", "bachelor"),
        (r"\b(?:associate|a\.?s\.?|a\.?a\.?)\s*(?:degree|of|in)\b", "associate"),
        (r"\b(?:diploma|certification|certificate)\b", "diploma"),
        (r"\b(?:high school|secondary|ged|hsc|ssc)\b", "high school"),
    ]

    for pattern, level in education_patterns:
        if re.search(pattern, text_lower):
            return level

    return "unknown"


# ---------------------------------------------------------------------------
# Skill Extraction Helper
# ---------------------------------------------------------------------------
def extract_skills_from_text(text: str, skills_list: list[str]) -> list[str]:
    """Extract known skills mentioned in text.

    Args:
        text: Input text to search
        skills_list: List of skill names to look for

    Returns:
        List of skills found in text
    """
    if not text or not skills_list:
        return []

    text_lower = text.lower()
    found_skills: list[str] = []

    for skill in skills_list:
        # Use word boundary matching for skills
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return list(set(found_skills))


# ---------------------------------------------------------------------------
# Text Chunking
# ---------------------------------------------------------------------------
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for processing.

    Args:
        text: Input text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of overlapping words between chunks

    Returns:
        List of text chunks
    """
    if not text:
        return []

    words = text.split()
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1

        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            # Keep overlap words
            overlap_words = current_chunk[-overlap:] if overlap > 0 else []
            current_chunk = overlap_words
            current_length = sum(len(w) + 1 for w in current_chunk)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
