"""
Resume Parser — Extracts structured data from PDF and TXT resume files.
Handles section detection, contact info extraction, and text segmentation.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from utils.constants import SECTION_PATTERNS, EMAIL_PATTERN, PHONE_PATTERN, LINKEDIN_PATTERN
from utils.text_processing import clean_text


@dataclass
class ResumeData:
    """Structured representation of a parsed resume."""
    raw_text: str = ""
    name: str = "Unknown"
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    sections: dict = field(default_factory=dict)
    file_name: str = ""
    word_count: int = 0
    parse_errors: list = field(default_factory=list)

    @property
    def skills_text(self) -> str:
        return self.sections.get("skills", "")

    @property
    def experience_text(self) -> str:
        return self.sections.get("experience", "")

    @property
    def education_text(self) -> str:
        return self.sections.get("education", "")

    @property
    def projects_text(self) -> str:
        return self.sections.get("projects", "")

    @property
    def summary_text(self) -> str:
        return self.sections.get("summary", "")


class ResumeParser:
    """
    Parses PDF and TXT resume files into structured ResumeData objects.
    """

    def parse_file(self, uploaded_file) -> ResumeData:
        """
        Parse an uploaded file (Streamlit UploadedFile object).
        Supports .pdf and .txt files.
        """
        file_name = uploaded_file.name
        extension = Path(file_name).suffix.lower()

        try:
            if extension == ".pdf":
                raw_text = self._extract_pdf_text(uploaded_file)
            elif extension == ".txt":
                raw_text = self._extract_txt_text(uploaded_file)
            else:
                return ResumeData(
                    file_name=file_name,
                    parse_errors=[f"Unsupported file type: {extension}"],
                )

            if not raw_text or len(raw_text.strip()) < 20:
                return ResumeData(
                    file_name=file_name,
                    raw_text=raw_text or "",
                    parse_errors=["File appears to be empty or contains very little text."],
                )

            cleaned = clean_text(raw_text)
            resume = ResumeData(
                raw_text=cleaned,
                file_name=file_name,
                word_count=len(cleaned.split()),
            )

            # Extract structured info
            resume.name = self._extract_name(raw_text)
            if resume.name == "Unknown Candidate":
                resume.name = self._extract_name_from_filename(file_name)
            resume.email = self._extract_email(cleaned)
            resume.phone = self._extract_phone(cleaned)
            resume.linkedin = self._extract_linkedin(cleaned)
            resume.sections = self._extract_sections(raw_text)

            return resume

        except Exception as e:
            return ResumeData(
                file_name=file_name,
                parse_errors=[f"Parse error: {str(e)}"],
            )

    def _extract_pdf_text(self, uploaded_file) -> str:
        """Extract text from PDF using pdfplumber."""
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber is required for PDF parsing. Install it with: pip install pdfplumber")

        text_parts = []
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")

        return "\n\n".join(text_parts)

    def _extract_txt_text(self, uploaded_file) -> str:
        """Extract text from a plain text file."""
        try:
            content = uploaded_file.read()
            if isinstance(content, bytes):
                try:
                    return content.decode("utf-8")
                except UnicodeDecodeError:
                    return content.decode("latin-1")
            return content
        except Exception as e:
            raise ValueError(f"Failed to read text file: {str(e)}")

    def _extract_name_from_filename(self, file_name: str) -> str:
        """Extract a clean, capitalized candidate name from the file's name."""
        stem = Path(file_name).stem
        # Remove common prefixes like resume, cv, biodata
        stem = re.sub(r'^(resume|cv|biodata)[_\-\s]*', '', stem, flags=re.IGNORECASE)
        # Replace underscores and hyphens with spaces
        name = re.sub(r'[_\-]+', ' ', stem).strip()
        # Capitalize each word
        name = name.title()
        if name:
            return name
        return "Unknown Candidate"

    def _extract_name(self, text: str) -> str:
        """
        Extract candidate name from the resume.
        Assumes the name is typically in the first few lines.
        """
        lines = text.strip().split("\n")
        for line in lines[:5]:
            line = line.strip()
            if not line:
                continue
            if re.match(EMAIL_PATTERN, line):
                continue
            if re.match(PHONE_PATTERN, line):
                continue
            if any(
                re.search(pat, line)
                for patterns in SECTION_PATTERNS.values()
                for pat in patterns
            ):
                continue
            
            # Clean up the line — remove trailing info after separators
            line_clean = re.sub(r"[|\-\u2013\u2014].*$", "", line).strip()
            
            words = line_clean.split()
            if 1 <= len(words) <= 5:
                is_name = True
                for w in words:
                    # Strip leading quotes/parentheses
                    w_stripped = w.lstrip('\'"([')
                    if not w_stripped:
                        continue
                    if not (w_stripped[0].isupper() or w in ["de", "van", "von", "la", "del"]):
                        is_name = False
                        break
                if is_name and len(line_clean) < 50:
                    return line_clean
        return "Unknown Candidate"

    def _extract_email(self, text: str) -> str:
        """Extract email address from text."""
        match = re.search(EMAIL_PATTERN, text)
        return match.group(0) if match else ""

    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text."""
        match = re.search(PHONE_PATTERN, text)
        return match.group(0) if match else ""

    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn profile URL/username from text."""
        match = re.search(LINKEDIN_PATTERN, text)
        return match.group(0) if match else ""

    def _extract_sections(self, text: str) -> dict:
        """
        Detect and extract resume sections based on common headers.
        Returns a dict mapping section names to their text content.
        """
        lines = text.split("\n")
        sections = {}
        current_section = "summary"
        current_content = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                current_content.append("")
                continue

            detected_section = self._detect_section_header(stripped)
            if detected_section:
                if current_content:
                    content = "\n".join(current_content).strip()
                    if content:
                        sections[current_section] = content
                current_section = detected_section
                current_content = []
            else:
                current_content.append(stripped)

        if current_content:
            content = "\n".join(current_content).strip()
            if content:
                sections[current_section] = content

        return sections

    def _detect_section_header(self, line: str) -> Optional[str]:
        """
        Check if a line matches known section header patterns.
        Returns section name or None.
        """
        if len(line) > 40:
            return None

        # If the line contains years/dates, it's not a header
        if re.search(r'\b(19|20)\d{2}\b', line):
            return None

        clean_line = re.sub(r"[=\-_*#|:]+", "", line).strip()
        if not clean_line:
            return None

        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                # Safety check for education: if it matches university/college,
                # make sure it's a very short line (e.g., <= 2 words) to avoid school names
                if section_name == "education" and re.search(r'(?i)\b(university|college)\b', clean_line):
                    if len(clean_line.split()) > 2:
                        continue
                if re.search(pattern, clean_line):
                    return section_name
        return None
