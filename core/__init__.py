"""
Core module for the Intelligent Candidate Discovery & Ranking System.

Defines all shared dataclasses used across the system:
- ResumeData: Structured resume information
- JDRequirements: Parsed job description requirements
- MatchExplanation: Detailed explanation of candidate-JD match
- CandidateScore: Complete scoring result for a candidate
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResumeData:
    """Structured representation of a parsed resume."""
    raw_text: str
    name: str
    email: str
    phone: str
    sections: dict  # keys: "skills", "experience", "education", "projects", "summary"
    file_name: str


@dataclass
class JDRequirements:
    """Parsed and structured job description requirements."""
    title: str
    required_skills: list  # list of str (canonical skill names)
    preferred_skills: list  # list of str
    min_experience: float  # years
    education_level: str
    raw_text: str
    seniority: str  # "junior", "mid", "senior", "lead"


@dataclass
class MatchExplanation:
    """Detailed explanation of why a candidate matched (or didn't) a JD."""
    matched_skills: list
    missing_skills: list
    extra_skills: list
    experience_assessment: str
    strengths: list
    improvement_areas: list
    ranking_reason: str
    score_breakdown: dict  # {"skill_match": float, "semantic": float, "experience": float, "education": float, "bonus": float}


@dataclass
class CandidateScore:
    """Complete scoring result for a single candidate."""
    candidate_name: str
    file_name: str
    overall_score: float  # 0-100
    skill_match_score: float  # 0-100
    semantic_similarity: float  # 0-100
    experience_score: float  # 0-100
    education_score: float  # 0-100
    bonus_score: float  # 0-100
    matched_skills: list
    missing_skills: list
    extra_skills: list
    experience_years: float
    explanation: MatchExplanation
    resume_data: ResumeData
