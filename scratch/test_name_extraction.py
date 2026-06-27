import re
from pathlib import Path

# Mock constants from utils/constants
EMAIL_PATTERN = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"(?:\+?\d{1,3}[\s\-]?)?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}"
SECTION_PATTERNS = {
    "skills": [r"(?i)\b(technical\s+skills|skills|core\s+competencies|competencies|technologies|tech\s+stack)\b"],
    "experience": [r"(?i)\b(work\s+experience|experience|professional\s+experience|employment\s+history|work\s+history)\b"],
    "education": [r"(?i)\b(education|academic|qualifications|degrees?|university|college)\b"],
    "projects": [r"(?i)\b(projects?|personal\s+projects?|academic\s+projects?|key\s+projects?)\b"],
    "certifications": [r"(?i)\b(certifications?|certificates?|accreditations?|licenses?)\b"],
    "summary": [r"(?i)\b(summary|objective|profile|about\s+me|professional\s+summary)\b"],
}

def extract_name_from_filename(file_name: str) -> str:
    stem = Path(file_name).stem
    stem = re.sub(r'^(resume|cv|biodata)[_\-\s]*', '', stem, flags=re.IGNORECASE)
    name = re.sub(r'[_\-]+', ' ', stem).strip()
    name = name.title()
    if name:
        return name
    return "Unknown Candidate"

def extract_name_improved(text: str, file_name: str) -> str:
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
            
        line_clean = re.sub(r"[|\-\u2013\u2014].*$", "", line).strip()
        words = line_clean.split()
        if 1 <= len(words) <= 5:
            is_name = True
            for w in words:
                w_stripped = w.lstrip('\'"([')
                if not w_stripped:
                    continue
                if not (w_stripped[0].isupper() or w in ["de", "van", "von", "la", "del"]):
                    is_name = False
                    break
            if is_name and len(line_clean) < 50:
                return line_clean
                
    # Fallback to filename
    return extract_name_from_filename(file_name)

# Let's test it on sample resumes
resumes_dir = Path("data/sample_resumes")
txt_files = list(resumes_dir.glob("*.txt"))

print("Testing Name Extraction on Demo Resumes:")
for path in txt_files:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    extracted = extract_name_improved(text, path.name)
    print(f"File: {path.name} => Extracted Name: {extracted}")

# Test custom pdf filename too
pdf_filename = "Resume_B_Nithin_Singh_Rajpurohith.pdf"
print(f"File: {pdf_filename} => Extracted Name: {extract_name_from_filename(pdf_filename)}")
