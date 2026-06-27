import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.resume_parser import ResumeParser

class MockUploadedFile:
    def __init__(self, file_path):
        self.path = Path(file_path)
        self.name = self.path.name
    def read(self):
        with open(self.path, "rb") as file:
            return file.read()

parser = ResumeParser()
demo_dir = Path("data/sample_resumes")
txt_files = list(demo_dir.glob("*.txt"))

print("Testing Actual ResumeParser on Demo Resumes:")
for path in txt_files:
    mock_file = MockUploadedFile(path)
    resume = parser.parse_file(mock_file)
    print(f"File: {resume.file_name} => Parsed Candidate Name: {resume.name}")
