import sys
import re
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.resume_parser import ResumeParser
from utils.constants import SECTION_PATTERNS

class MockUploadedFile:
    def __init__(self, file_path):
        self.path = Path(file_path)
        self.name = self.path.name
    def read(self):
        with open(self.path, "rb") as file:
            return file.read()

def detect_section_header_improved(line: str) -> str:
    if len(line) > 40:
        return None
        
    # If contains years, it's not a header
    if re.search(r'\b(19|20)\d{2}\b', line):
        return None
        
    clean_line = re.sub(r"[=\-_*#|:]+", "", line).strip()
    if not clean_line:
        return None
        
    for section_name, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            # Special check for university/college: must be <= 2 words
            if section_name == "education" and re.search(r'(?i)\b(university|college)\b', clean_line):
                if len(clean_line.split()) > 2:
                    continue
            if re.search(pattern, clean_line):
                return section_name
    return None

def extract_sections_improved(text: str) -> dict:
    lines = text.split("\n")
    sections = {}
    current_section = "summary"
    current_content = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_content.append("")
            continue

        detected_section = detect_section_header_improved(stripped)
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

demo_dir = Path("data/sample_resumes")
txt_files = list(demo_dir.glob("*.txt"))

print("Testing IMPROVED Section Extraction:")
for path in txt_files:
    mock_file = MockUploadedFile(path)
    with open(path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    sections = extract_sections_improved(raw_text)
    print(f"File: {path.name}")
    print(f"  Extracted Sections: {list(sections.keys())}")
    if "education" in sections:
        print(f"  Education section:\n{sections['education']}")
    else:
        print("  Education NOT FOUND!")
    print("-" * 50)
