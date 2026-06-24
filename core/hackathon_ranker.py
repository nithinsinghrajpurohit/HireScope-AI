"""
Hackathon Ranker — Core ranking logic for the Redrob JSONL candidate dataset.

Implements a multi-signal, rule-based ranking engine that scores 100K candidates
against a job description. Designed to run within 5 minutes on CPU with 16GB RAM.

Scoring dimensions:
1. Skill Match (35%)       - JD skills vs candidate skills (name, proficiency, duration)
2. Title/Career (25%)      - Current title + career trajectory alignment
3. Experience Fit (15%)    - Years of experience vs JD requirement
4. Education Fit (10%)     - Degree, field, institution tier
5. Behavioral Signals (15%) - Redrob platform engagement + trust signals

Anti-gaming:
- Keyword-stuffer detection via endorsement-duration trust multiplier
- Honeypot filtering via core.honeypot_detector
"""

import json
import gzip
import os
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional
from datetime import datetime


# ════════════════════════════════════════════════════════════════════════════
#  JD PARSING
# ════════════════════════════════════════════════════════════════════════════

import re
from data.skills_database import SKILLS_DB

# Build a lookup table from all aliases/names to the canonical lowercase skill name
SKILL_CANONICAL_MAP = {}
for canon_name, info in SKILLS_DB.items():
    SKILL_CANONICAL_MAP[canon_name.lower()] = canon_name.lower()
    for alias in info.get("aliases", []):
        SKILL_CANONICAL_MAP[alias.lower()] = canon_name.lower()

# If the JD docx can't be read, fall back to this extracted text.
# Contains all key characteristics of the challenge's JD.
FALLBACK_JD_TEXT = """
Job Title: AI/ML Engineer
Required Experience: 3 to 15 years
Required Education: Bachelor's degree in Computer Science, Data Science, or related field.
Seniority: Mid-Senior

We are looking for a Senior AI/ML Engineer to design and deploy large-scale machine learning models.
Key requirements and responsibilities:
- Build deep learning architectures using PyTorch and TensorFlow.
- Experience with Large Language Models (LLM), Transformers, Fine-tuning, RAG, and NLP.
- Deploy models using MLOps practices, Docker, Kubernetes, and cloud providers (AWS, GCP, Azure).
- Data engineering pipelines using SQL, Apache Spark, Pandas, and NumPy.
- Build REST APIs using FastAPI, Flask, and Django.
"""

def extract_text_from_docx(docx_path: str) -> str:
    """Extract text from .docx using only stdlib (zipfile + xml)."""
    text_parts = []
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            with z.open('word/document.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns_w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
                for para in root.iter(f'{{{ns_w}}}p'):
                    para_text = []
                    for run in para.iter(f'{{{ns_w}}}r'):
                        for t in run.iter(f'{{{ns_w}}}t'):
                            if t.text:
                                para_text.append(t.text)
                    text_parts.append(''.join(para_text))
    except Exception as e:
        print(f"Warning: Could not read docx at {docx_path}: {e}")
        return ""
    return '\n'.join(text_parts)


def load_jd(jd_path: str) -> dict:
    """Load and parse the job description into structured requirements.

    Returns a dict with keys:
        title, required_skills, preferred_skills, min_experience,
        education_level, seniority, raw_text, ai_core_skills
    """
    raw_text = ""

    if jd_path.endswith('.docx'):
        raw_text = extract_text_from_docx(jd_path)
    elif jd_path.endswith('.md') or jd_path.endswith('.txt'):
        with open(jd_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

    if not raw_text.strip():
        raw_text = FALLBACK_JD_TEXT

    return parse_jd_text(raw_text)


def parse_jd_text(text: str) -> dict:
    """Parse JD text into structured requirements.

    Uses heuristics to extract title, skills, experience, and education
    from the raw JD text.
    """
    text_lower = text.lower()

    # Default fallback lists (the AI/ML Engineer profile from the hackathon)
    default_ai_ml_core = {
        "Python", "TensorFlow", "PyTorch", "Machine Learning",
        "Deep Learning", "NLP", "Computer Vision", "LLM",
        "Transformers", "Fine-tuning LLMs", "RAG",
        "Prompt Engineering", "Neural Networks", "CNN", "RNN",
        "GANs", "Reinforcement Learning", "Scikit-Learn",
        "Image Classification", "Object Detection",
        "Speech Recognition", "Statistical Modeling",
        "Feature Engineering", "Hugging Face",
    }
    default_ml_infrastructure = {
        "MLOps", "Docker", "Kubernetes", "MLflow", "Kubeflow",
        "Airflow", "Weights & Biases", "BentoML", "ONNX",
        "TensorRT", "CI/CD", "Git",
    }
    default_data_engineering = {
        "SQL", "Spark", "Pandas", "NumPy", "Snowflake",
        "BigQuery", "Databricks", "Kafka", "Elasticsearch",
        "Data Engineering", "ETL", "Apache Beam", "Apache Flink",
        "dbt", "Redshift",
    }
    default_cloud_infra = {
        "AWS", "GCP", "Azure", "Linux", "Terraform",
    }
    default_backend_api = {
        "FastAPI", "Flask", "Django", "REST API",
        "gRPC", "GraphQL",
    }

    # 1. Title Extraction
    title = "Unknown Position"
    title_patterns = [
        re.compile(r"(?:job\s*title|position|role)\s*[:–—-]\s*(.+)", re.IGNORECASE),
        re.compile(r"^(?:hiring|we(?:'re| are)\s+(?:looking|hiring)\s+(?:for\s+)?(?:a\s+)?)\s*(.+)", re.IGNORECASE),
    ]
    for pattern in title_patterns:
        m = pattern.search(text)
        if m:
            title = m.group(1).strip().rstrip(".")
            break
    if title == "Unknown Position":
        # Fallback to the first non-empty, non-trivial line
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped and len(stripped) < 120 and not stripped.startswith(("http", "www")) and not re.match(r"^\d", stripped):
                title = stripped.rstrip(".")
                break

    # 2. Experience Extraction
    min_exp = 3.0
    max_exp = 15.0
    exp_range_pattern = re.compile(r"(\d+)\s*[-–—to]+\s*(\d+)\s*(?:\+)?\s*(?:years?|yrs?)", re.IGNORECASE)
    exp_min_pattern = re.compile(r"(\d+)\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE)
    
    m_range = exp_range_pattern.search(text)
    if m_range:
        min_exp = float(m_range.group(1))
        max_exp = float(m_range.group(2))
    else:
        m_min = exp_min_pattern.search(text)
        if m_min:
            min_exp = float(m_min.group(1))
            max_exp = max(min_exp + 5.0, 15.0)

    # 3. Education Extraction
    edu_level = "bachelor"
    edu_text = text.lower()
    if any(k in edu_text for k in ["phd", "ph.d", "doctorate"]):
        edu_level = "phd"
    elif any(k in edu_text for k in ["master", "m.tech", "m.s.", "m.sc", "m.e."]):
        edu_level = "master"
    elif any(k in edu_text for k in ["bachelor", "b.tech", "b.e.", "b.sc", "b.a."]):
        edu_level = "bachelor"

    # 4. Skill Extraction from SKILLS_DB
    found_skills = {}
    for skill_name, skill_info in SKILLS_DB.items():
        pattern_str = r"\b" + re.escape(skill_name.lower()) + r"\b"
        if re.search(pattern_str, text_lower):
            found_skills[skill_name] = skill_info.get("category", "")
            continue
        for alias in skill_info.get("aliases", []):
            alias_pattern = r"\b" + re.escape(alias.lower()) + r"\b"
            if re.search(alias_pattern, text_lower):
                found_skills[skill_name] = skill_info.get("category", "")
                break

    # Classify found skills into buckets
    ai_ml_core = set()
    ml_infrastructure = set()
    data_engineering = set()
    cloud_infra = set()
    backend_api = set()

    for skill, cat in found_skills.items():
        # Clean naming casing
        casing_map = {
            "python": "Python", "tensorflow": "TensorFlow", "pytorch": "PyTorch",
            "nlp": "NLP", "llm": "LLM", "sql": "SQL", "aws": "AWS", "gcp": "GCP",
            "azure": "Azure", "git": "Git", "ci/cd": "CI/CD", "api": "API",
            "rest api": "REST API", "fastapi": "FastAPI", "mongodb": "MongoDB",
        }
        skill_clean = casing_map.get(skill.lower(), skill.title() if len(skill) > 3 else skill.upper())

        if cat == "Data Science" or skill.lower() in ["python", "r", "matlab", "julia"]:
            ai_ml_core.add(skill_clean)
        elif cat == "DevOps" or skill.lower() in ["git", "github", "gitlab", "docker", "kubernetes", "mlflow", "airflow", "mlops"]:
            ml_infrastructure.add(skill_clean)
        elif cat == "Databases" or skill.lower() in ["spark", "hadoop", "kafka", "dbt", "pandas", "numpy", "data engineering", "etl"]:
            data_engineering.add(skill_clean)
        elif cat == "Cloud":
            cloud_infra.add(skill_clean)
        else:
            backend_api.add(skill_clean)

    # If we found no skills at all, use default AI/ML sets
    if not (ai_ml_core | ml_infrastructure | data_engineering | cloud_infra | backend_api):
        ai_ml_core = default_ai_ml_core
        ml_infrastructure = default_ml_infrastructure
        data_engineering = default_data_engineering
        cloud_infra = default_cloud_infra
        backend_api = default_backend_api

    all_core_skills = ai_ml_core | ml_infrastructure | data_engineering | cloud_infra | backend_api

    return {
        "title": title,
        "required_skills": list(ai_ml_core),
        "preferred_skills": list(ml_infrastructure | data_engineering | cloud_infra | backend_api),
        "min_experience": min_exp,
        "max_experience": max_exp,
        "education_level": edu_level,
        "preferred_education_fields": {
            "computer science", "data science", "artificial intelligence",
            "machine learning", "mathematics", "statistics",
            "computer engineering", "information technology",
            "electronics", "electrical engineering",
        },
        "seniority": "mid-senior" if min_exp >= 3 else "junior",
        "raw_text": text,
        "ai_core_skills": all_core_skills,
        "ai_ml_core": ai_ml_core,
        "ml_infrastructure": ml_infrastructure,
        "data_engineering": data_engineering,
        "cloud_infra": cloud_infra,
        "backend_api": backend_api,
    }


# ════════════════════════════════════════════════════════════════════════════
#  CANDIDATE LOADING
# ════════════════════════════════════════════════════════════════════════════

def load_candidates(path: str) -> list[dict]:
    """Load candidates from JSONL or gzipped JSONL.

    Parameters
    ----------
    path : str
        Path to candidates.jsonl or candidates.jsonl.gz

    Returns
    -------
    list[dict]
    """
    candidates = []
    if path.endswith('.gz'):
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    candidates.append(json.loads(line))
    elif path.endswith('.json') and not path.endswith('.jsonl'):
        # Regular JSON array (e.g., sample_candidates.json)
        with open(path, 'r', encoding='utf-8') as f:
            candidates = json.load(f)
    else:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    candidates.append(json.loads(line))
    return candidates


# ════════════════════════════════════════════════════════════════════════════
#  SCORING FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

SEMANTIC_GROUPS = {
    "deep learning": {"keras", "tensorflow", "pytorch", "neural networks", "cnn", "rnn", "deep learning"},
    "nlp": {"bert", "gpt", "transformers", "hugging face", "spacy", "nltk", "text mining", "nlp"},
    "mlops": {"mlflow", "kubeflow", "bentoml", "weights & biases", "model deployment", "mlops"},
    "computer vision": {"opencv", "yolo", "image segmentation", "object detection", "computer vision"},
}

def score_skills(candidate: dict, jd: dict) -> tuple[float, list[str], list[str]]:
    """Score candidate's skills against JD requirements.

    Returns (score_0_to_1, matched_skills, missing_skills)
    """
    cand_skills = candidate.get("skills", [])
    
    # ── 1. Create a Canonical Map of Candidate Skills ────────────────
    cand_skill_map = {}
    cand_skill_names = set()
    
    for s in cand_skills:
        name_lower = s["name"].lower()
        canon = SKILL_CANONICAL_MAP.get(name_lower, name_lower)
        cand_skill_names.add(canon)
        
        # Keep the best/highest proficiency skill if there are duplicates
        if canon not in cand_skill_map:
            cand_skill_map[canon] = s
        else:
            existing = cand_skill_map[canon]
            prof_weights = {"expert": 4, "advanced": 3, "intermediate": 2, "beginner": 1}
            s_prof = prof_weights.get(s.get("proficiency", "beginner"), 1)
            e_prof = prof_weights.get(existing.get("proficiency", "beginner"), 1)
            if s_prof > e_prof or (s_prof == e_prof and s.get("duration_months", 0) > existing.get("duration_months", 0)):
                cand_skill_map[canon] = s

    # ── 2. Canonicalize JD Skills ────────────────────────────────────
    ai_ml_core = {SKILL_CANONICAL_MAP.get(s.lower(), s.lower()) for s in jd["ai_ml_core"]}
    ml_infra = {SKILL_CANONICAL_MAP.get(s.lower(), s.lower()) for s in jd["ml_infrastructure"]}
    data_eng = {SKILL_CANONICAL_MAP.get(s.lower(), s.lower()) for s in jd["data_engineering"]}
    cloud = {SKILL_CANONICAL_MAP.get(s.lower(), s.lower()) for s in jd["cloud_infra"]}
    backend = {SKILL_CANONICAL_MAP.get(s.lower(), s.lower()) for s in jd["backend_api"]}

    # ── 3. Recency Text Compilation ─────────────────────────────────
    career = candidate.get("career_history", [])
    recent_descriptions = []
    current_year = 2026
    
    for role in career:
        end_date = role.get("end_date")
        is_recent = False
        if not end_date: # current job
            is_recent = True
        else:
            try:
                end_year = int(end_date.split("-")[0])
                if current_year - end_year <= 2:
                    is_recent = True
            except (ValueError, IndexError, AttributeError):
                pass
        if is_recent:
            recent_descriptions.append(role.get("description", "").lower() + " " + role.get("title", "").lower())
            
    recent_text = " ".join(recent_descriptions)

    matched = []
    partially_matched = set()
    total_weighted_score = 0.0
    max_possible_score = 0.0

    # Helper to calculate score for a specific skill bucket
    def process_bucket(skills_set, weight):
        nonlocal total_weighted_score, max_possible_score
        for skill in skills_set:
            max_possible_score += weight
            
            # Direct match
            if skill in cand_skill_names:
                info = cand_skill_map[skill]
                trust = _skill_trust_multiplier(info)
                
                # Apply Recency decay
                recency_mult = 1.0
                if recent_descriptions:
                    skill_words = [skill]
                    if skill.lower() in SKILLS_DB:
                        skill_words.extend(SKILLS_DB[skill.lower()].get("aliases", []))
                    if not any(w.lower() in recent_text for w in skill_words):
                        recency_mult = 0.85
                
                total_weighted_score += weight * trust * recency_mult
                matched.append(info["name"])
            
            # Semantic partial match expansion
            else:
                partial_match_found = False
                for group_name, group_set in SEMANTIC_GROUPS.items():
                    if group_name == skill.lower():
                        overlap = group_set & cand_skill_names
                        if overlap:
                            # Choose the candidate's highest quality skill in the overlap
                            best_subskill = None
                            best_subskill_trust = 0.0
                            for sub in overlap:
                                sub_info = cand_skill_map[sub]
                                t = _skill_trust_multiplier(sub_info)
                                if t > best_subskill_trust:
                                    best_subskill_trust = t
                                    best_subskill = sub
                            
                            if best_subskill:
                                info = cand_skill_map[best_subskill]
                                recency_mult = 1.0
                                if recent_descriptions:
                                    skill_words = [best_subskill]
                                    if best_subskill.lower() in SKILLS_DB:
                                        skill_words.extend(SKILLS_DB[best_subskill.lower()].get("aliases", []))
                                    if not any(w.lower() in recent_text for w in skill_words):
                                        recency_mult = 0.85
                                
                                # Partial match scaling factor: 0.7x
                                total_weighted_score += weight * best_subskill_trust * recency_mult * 0.7
                                matched.append(f"{info['name']} (partial match for {skill})")
                                partially_matched.add(skill)
                                partial_match_found = True
                                break
                
    process_bucket(ai_ml_core, 3.0)
    process_bucket(ml_infra, 2.0)
    process_bucket(data_eng, 1.5)
    process_bucket(cloud, 1.0)
    process_bucket(backend, 1.0)

    # Calculate missing core skills (omitting skills that are partially matched)
    missing = []
    for s in jd["ai_ml_core"]:
        canon_s = SKILL_CANONICAL_MAP.get(s.lower(), s.lower())
        if canon_s not in cand_skill_names and canon_s not in partially_matched:
            missing.append(s)

    score = total_weighted_score / max_possible_score if max_possible_score > 0 else 0.0
    return min(1.0, score), matched, missing



def _skill_trust_multiplier(skill_info: dict) -> float:
    """Compute a trust multiplier for a skill based on proficiency,
    endorsements, and duration. Catches keyword stuffers.

    Returns a value in [0.3, 1.0]:
    - Beginner + 0 endorsements + <3 months → 0.3 (low trust)
    - Advanced + many endorsements + long duration → 1.0 (high trust)
    """
    proficiency = skill_info.get("proficiency", "beginner")
    endorsements = skill_info.get("endorsements", 0)
    duration = skill_info.get("duration_months", 0)

    prof_scores = {
        "beginner": 0.3,
        "intermediate": 0.6,
        "advanced": 0.85,
        "expert": 1.0,
    }
    prof_score = prof_scores.get(proficiency, 0.3)

    # Duration trust: 0-6 months = low, 6-24 = medium, 24+ = high
    if duration >= 24:
        dur_score = 1.0
    elif duration >= 12:
        dur_score = 0.8
    elif duration >= 6:
        dur_score = 0.6
    else:
        dur_score = 0.4

    # Endorsement trust: 0 = low, 5-15 = medium, 15+ = high
    if endorsements >= 15:
        end_score = 1.0
    elif endorsements >= 5:
        end_score = 0.7
    elif endorsements >= 1:
        end_score = 0.5
    else:
        end_score = 0.3

    # Combine with emphasis on proficiency
    trust = 0.5 * prof_score + 0.25 * dur_score + 0.25 * end_score
    return max(0.3, min(1.0, trust))


def score_title_career(candidate: dict, jd: dict) -> float:
    """Score title and career trajectory alignment (0-1).

    Checks:
    - Current title relevance to AI/ML
    - Career progression logic
    - Industry relevance
    """
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])
    current_title = profile.get("current_title", "").lower()
    headline = profile.get("headline", "").lower()
    summary = profile.get("summary", "").lower()
    industry = profile.get("current_industry", "").lower()

    score = 0.0

    # ── Title relevance ──────────────────────────────────────────────
    high_relevance_titles = {
        "ml engineer", "machine learning engineer", "ai engineer",
        "data scientist", "deep learning engineer", "nlp engineer",
        "computer vision engineer", "research scientist",
        "applied scientist", "ml researcher", "ai researcher",
        "senior ml engineer", "senior machine learning engineer",
        "senior ai engineer", "lead ml engineer", "principal ml engineer",
        "staff ml engineer", "junior ml engineer",
    }
    medium_relevance_titles = {
        "data engineer", "software engineer", "backend engineer",
        "full stack developer", "data analyst", "analytics engineer",
        "platform engineer", "devops engineer", "cloud engineer",
        "qa engineer", "site reliability engineer",
    }
    low_relevance_titles = {
        "project manager", "product manager", "business analyst",
        "operations manager", "hr manager", "marketing manager",
        "sales executive", "content writer", "graphic designer",
        "accountant", "civil engineer", "mechanical engineer",
        "customer support",
    }

    # Check title match
    if any(t in current_title for t in high_relevance_titles):
        score += 0.5
    elif any(t in current_title for t in medium_relevance_titles):
        score += 0.3
    elif any(t in current_title for t in low_relevance_titles):
        score += 0.05
    else:
        score += 0.15  # Unknown titles get small benefit of doubt

    # ── Headline/Summary AI/ML keywords ──────────────────────────────
    ai_keywords = {
        "machine learning", "deep learning", "ai", "artificial intelligence",
        "ml", "nlp", "computer vision", "data science", "neural",
        "tensorflow", "pytorch", "model", "training", "inference",
        "llm", "transformer", "fine-tuning", "rag",
    }
    headline_matches = sum(1 for k in ai_keywords if k in headline)
    summary_matches = sum(1 for k in ai_keywords if k in summary)

    if headline_matches >= 2:
        score += 0.2
    elif headline_matches >= 1:
        score += 0.1

    if summary_matches >= 3:
        score += 0.15
    elif summary_matches >= 1:
        score += 0.05

    # ── Career trajectory: check if career descriptions mention AI/ML ─
    career_ai_score = 0.0
    for role in career:
        desc = role.get("description", "").lower()
        title = role.get("title", "").lower()
        ai_mentions = sum(1 for k in ai_keywords if k in desc)
        title_ai = sum(1 for k in high_relevance_titles if k in title)

        if title_ai > 0:
            career_ai_score += 0.1
        if ai_mentions >= 2:
            career_ai_score += 0.05

    score += min(0.15, career_ai_score)

    # ── Industry relevance ───────────────────────────────────────────
    tech_industries = {
        "software", "it services", "technology", "ai/ml",
        "data", "cloud", "saas", "fintech",
    }
    if any(ind in industry for ind in tech_industries):
        score += 0.05

    return min(1.0, score)


def score_experience(candidate: dict, jd: dict) -> float:
    """Score experience fit (0-1).

    Ideal range: min_experience to max_experience.
    Below min: proportional penalty.
    Above max: slight penalty for overqualification.
    """
    years = candidate.get("profile", {}).get("years_of_experience", 0)
    min_exp = jd.get("min_experience", 3.0)
    max_exp = jd.get("max_experience", 15.0)

    if years <= 0:
        return 0.05

    if min_exp <= years <= max_exp:
        return 1.0
    elif years < min_exp:
        # Below minimum: proportional
        if years >= min_exp * 0.7:
            return 0.6
        else:
            return max(0.1, (years / min_exp) * 0.6)
    else:
        # Above max: slight overqualification penalty
        overshoot = (years - max_exp) / max_exp
        return max(0.4, 0.8 - overshoot * 0.3)


def score_education(candidate: dict, jd: dict) -> float:
    """Score education fit (0-1).

    Considers degree level, field of study relevance, and institution tier.
    """
    education = candidate.get("education", [])
    if not education:
        return 0.2

    preferred_fields = jd.get("preferred_education_fields", set())

    degree_ranks = {
        "ph.d": 5, "phd": 5,
        "m.tech": 4, "m.s.": 4, "m.sc": 4, "m.e.": 4,
        "mba": 3.5, "m.a.": 3,
        "b.tech": 3, "b.e.": 3, "b.sc": 2.5,
        "b.a.": 2, "diploma": 1,
    }

    tier_scores = {
        "tier_1": 1.0,
        "tier_2": 0.8,
        "tier_3": 0.6,
        "tier_4": 0.4,
        "unknown": 0.5,
    }

    best_score = 0.0

    for edu in education:
        degree = edu.get("degree", "").lower()
        field = edu.get("field_of_study", "").lower()
        tier = edu.get("tier", "unknown")

        # Degree level score
        degree_score = 0.3  # default
        for deg_key, rank in degree_ranks.items():
            if deg_key in degree:
                degree_score = rank / 5.0
                break

        # Field relevance
        field_score = 0.3
        if any(f in field for f in preferred_fields):
            field_score = 1.0
        elif any(f in field for f in {"engineering", "science", "technology"}):
            field_score = 0.6

        # Institution tier
        tier_score = tier_scores.get(tier, 0.5)

        # Combined (degree weight: 40%, field: 40%, tier: 20%)
        edu_score = 0.4 * degree_score + 0.4 * field_score + 0.2 * tier_score
        best_score = max(best_score, edu_score)

    return min(1.0, best_score)


def score_behavioral_signals(candidate: dict, jd: dict) -> float:
    """Score behavioral/engagement signals (0-1).

    Uses Redrob platform signals as trust and engagement indicators.
    """
    signals = candidate.get("redrob_signals", {})

    scores = []

    # Profile completeness (normalized 0-1)
    completeness = signals.get("profile_completeness_score", 0) / 100.0
    scores.append(completeness * 0.15)

    # Open to work
    if signals.get("open_to_work_flag", False):
        scores.append(0.1)

    # Recruiter response rate
    response_rate = signals.get("recruiter_response_rate", 0)
    scores.append(response_rate * 0.15)

    # Response time (lower is better)
    resp_time = signals.get("avg_response_time_hours", 200)
    if resp_time <= 24:
        scores.append(0.1)
    elif resp_time <= 72:
        scores.append(0.07)
    elif resp_time <= 168:
        scores.append(0.03)

    # GitHub activity
    github = signals.get("github_activity_score", -1)
    if github > 0:
        scores.append(min(0.1, github / 100.0 * 0.1))

    # Skill assessment scores (AI-relevant ones)
    assessments = signals.get("skill_assessment_scores", {})
    if assessments:
        avg_assessment = sum(assessments.values()) / len(assessments) / 100.0
        scores.append(avg_assessment * 0.15)

    # Interview completion rate
    interview_rate = signals.get("interview_completion_rate", 0)
    scores.append(interview_rate * 0.1)

    # Verification signals
    verified_count = sum([
        signals.get("verified_email", False),
        signals.get("verified_phone", False),
        signals.get("linkedin_connected", False),
    ])
    scores.append(verified_count / 3.0 * 0.1)

    # Notice period preference (shorter is better for hiring)
    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        scores.append(0.05)
    elif notice <= 60:
        scores.append(0.03)
    elif notice <= 90:
        scores.append(0.01)

    total = sum(scores)
    return min(1.0, total)


# ════════════════════════════════════════════════════════════════════════════
#  COMPOSITE SCORING & RANKING
# ════════════════════════════════════════════════════════════════════════════

WEIGHTS = {
    "skills": 0.35,
    "title_career": 0.25,
    "experience": 0.15,
    "education": 0.10,
    "behavioral": 0.15,
}


def score_candidate(candidate: dict, jd: dict) -> dict:
    """Compute composite score for a single candidate.

    Returns a dict with all sub-scores and the final composite score.
    """
    skill_score, matched, missing = score_skills(candidate, jd)
    title_score = score_title_career(candidate, jd)
    exp_score = score_experience(candidate, jd)
    edu_score = score_education(candidate, jd)
    behav_score = score_behavioral_signals(candidate, jd)

    composite = (
        skill_score * WEIGHTS["skills"]
        + title_score * WEIGHTS["title_career"]
        + exp_score * WEIGHTS["experience"]
        + edu_score * WEIGHTS["education"]
        + behav_score * WEIGHTS["behavioral"]
    )

    return {
        "candidate_id": candidate.get("candidate_id", ""),
        "composite_score": round(composite, 6),
        "skill_score": round(skill_score, 4),
        "title_career_score": round(title_score, 4),
        "experience_score": round(exp_score, 4),
        "education_score": round(edu_score, 4),
        "behavioral_score": round(behav_score, 4),
        "matched_skills": matched,
        "missing_core_skills": missing,
        "candidate_name": candidate.get("profile", {}).get("anonymized_name", "Unknown"),
        "current_title": candidate.get("profile", {}).get("current_title", ""),
        "years_experience": candidate.get("profile", {}).get("years_of_experience", 0),
        "raw_candidate": candidate,
    }


def generate_reasoning(scored: dict) -> str:
    """Generate 1-2 sentence reasoning for ranking a candidate with specific signals."""
    title = scored["current_title"] or "Candidate"
    years = scored["years_experience"]
    matched = scored["matched_skills"]
    n_matched = len(matched)
    candidate = scored["raw_candidate"]
    
    # Experience and title
    exp_part = f"{title} ({years:.1f} yrs exp)"
    
    # Skills matched
    if n_matched > 0:
        skills_part = f"matched {n_matched} core skills (incl. {', '.join(matched[:3])})"
    else:
        skills_part = "no core skills matched"
        
    # Behavioral signals
    signals = candidate.get("redrob_signals", {})
    sig_parts = []
    
    resp_rate = signals.get("recruiter_response_rate", 0)
    if resp_rate > 0:
        sig_parts.append(f"response_rate={resp_rate:.2f}")
        
    github = signals.get("github_activity_score", -1)
    if github > 0:
        sig_parts.append(f"github_activity={github:.0f}")
        
    assessments = signals.get("skill_assessment_scores", {})
    if assessments:
        sig_parts.append(f"assessments={len(assessments)}")
        
    if signals.get("open_to_work_flag", False):
        sig_parts.append("open_to_work")
        
    if sig_parts:
        behavior_part = "Key signals: " + ", ".join(sig_parts[:3])
    else:
        behavior_part = "standard platform activity"
        
    return f"{exp_part} {skills_part}. {behavior_part}."


def rank_candidates_for_submission(
    candidates: list[dict],
    jd: dict,
    honeypot_ids: set[str],
    top_n: int = 100,
) -> list[dict]:
    """Score all candidates, filter honeypots, apply diversity check, and return top N.
    """
    all_scores = []

    for cand in candidates:
        cid = cand.get("candidate_id", "")
        if cid in honeypot_ids:
            continue  # Skip honeypots

        scored = score_candidate(cand, jd)
        all_scores.append(scored)

    # First sort by composite score descending
    all_scores.sort(key=lambda x: (-x["composite_score"], x["candidate_id"]))

    # Apply diversity pass: check for identical companies and high skill overlap (>80% Jaccard)
    for i in range(len(all_scores)):
        cand_i = all_scores[i]
        comp_i = cand_i["raw_candidate"].get("profile", {}).get("current_company", "").strip().lower()
        skills_i = set(cand_i["matched_skills"])
        if not comp_i or len(skills_i) == 0:
            continue
            
        for j in range(i):
            cand_j = all_scores[j]
            comp_j = cand_j["raw_candidate"].get("profile", {}).get("current_company", "").strip().lower()
            if comp_i == comp_j and comp_j:
                skills_j = set(cand_j["matched_skills"])
                if skills_j:
                    intersection = len(skills_i & skills_j)
                    union = len(skills_i | skills_j)
                    jaccard = intersection / union if union > 0 else 0
                    if jaccard > 0.8:
                        # Apply a 3% diversity penalty
                        cand_i["composite_score"] = round(cand_i["composite_score"] * 0.97, 6)
                        break

    # Round composite scores to 4 decimal places to match CSV precision and resolve tie-breaking discrepancies
    for scored in all_scores:
        scored["composite_score"] = round(scored["composite_score"], 4)

    # Re-sort after diversity penalty and rounding
    all_scores.sort(key=lambda x: (-x["composite_score"], x["candidate_id"]))

    # Take top N
    top = all_scores[:top_n]

    # Assign ranks and generate reasoning
    for rank, scored in enumerate(top, start=1):
        scored["rank"] = rank
        scored["reasoning"] = generate_reasoning(scored)

    return top


def write_submission_csv(ranked: list[dict], output_path: str) -> None:
    """Write the submission CSV in the required format.

    Format: candidate_id,rank,score,reasoning
    Scores are non-increasing, ties broken by candidate_id ascending.
    """
    import csv

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])

        for entry in ranked:
            writer.writerow([
                entry["candidate_id"],
                entry["rank"],
                f"{entry['composite_score']:.4f}",
                entry["reasoning"],
            ])

    print(f"Submission CSV written to: {output_path}")
    print(f"Total candidates ranked: {len(ranked)}")
