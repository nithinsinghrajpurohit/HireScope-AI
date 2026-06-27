import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.resume_parser import ResumeParser
from core.jd_analyzer import analyze_jd
from core.scoring_engine import rank_candidates

class MockUploadedFile:
    def __init__(self, file_path):
        self.path = Path(file_path)
        self.name = self.path.name
    def read(self):
        with open(self.path, "rb") as file:
            return file.read()

# Define test JD
jd_text = """
JOB TITLE: Machine Learning Engineer
We are looking for a Machine Learning Engineer with 3+ years of experience.
REQUIRED SKILLS: Python, Machine Learning, TensorFlow, PyTorch, Scikit-Learn, SQL
EDUCATION: Master's degree in Computer Science, Data Analytics, or related field.
"""

parser = ResumeParser()
demo_dir = Path("data/sample_resumes")
txt_files = list(demo_dir.glob("*.txt"))

# Parse resumes
parsed_resumes = []
for path in txt_files:
    mock_file = MockUploadedFile(path)
    resume = parser.parse_file(mock_file)
    parsed_resumes.append(resume)

# Analyze JD
jd_req = analyze_jd(jd_text)

# Rank candidates
ranked = rank_candidates(parsed_resumes, jd_req)

print(f"Ranking results for: {jd_req.title}")
print(f"Required Education: {jd_req.education_level}")
print("-" * 80)
for idx, c in enumerate(ranked, start=1):
    edu_text = c.resume_data.sections.get("education", "Not found").replace('\n', ' | ')
    print(f"#{idx} Name: {c.candidate_name}")
    print(f"    File: {c.file_name}")
    print(f"    Score: {c.overall_score}%")
    print(f"    Exp: {c.experience_years} years (Score: {c.experience_score}%)")
    print(f"    Edu: {edu_text[:80]}")
    print(f"    Edu Score: {c.education_score}%")
    print(f"    Matched Skills: {c.matched_skills}")
    print("-" * 80)
