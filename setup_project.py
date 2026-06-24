import os
import shutil
import sys

def main():
    source_dir = r"c:\Users\nithi\Downloads\AI&DS CHALLENGE"
    target_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 80)
    print("  HireScope AI — Hackathon Project Setup Script")
    print("=" * 80)
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    print("=" * 80)

    if not os.path.exists(source_dir):
        print(f"ERROR: Source directory '{source_dir}' does not exist.")
        sys.exit(1)

    # Directories to copy
    subdirs = ["core", "data", "ui", "utils", ".streamlit"]
    # Files to copy directly
    files = ["app.py", "rank.py", "requirements.txt", "submission_metadata.yaml", "README.md"]

    # 1. Copy Subdirectories
    for subdir in subdirs:
        src_path = os.path.join(source_dir, subdir)
        dst_path = os.path.join(target_dir, subdir)
        
        if os.path.exists(src_path):
            if os.path.exists(dst_path):
                print(f"Cleaning existing target directory: {subdir}")
                shutil.rmtree(dst_path)
            
            # Custom copy to avoid copying __pycache__ or massive files
            def ignore_patterns(path, names):
                ignored = []
                for name in names:
                    if name == "__pycache__":
                        ignored.append(name)
                    elif name == "candidates.jsonl" or name == "candidates.jsonl.gz":
                        ignored.append(name)
                    elif name.endswith(".csv") and name != "sample_submission.csv":
                        ignored.append(name)
                return ignored

            print(f"Copying directory: {subdir} ...")
            shutil.copytree(src_path, dst_path, ignore=ignore_patterns)
        else:
            print(f"Warning: Source subdirectory '{subdir}' not found in source.")

    # 2. Copy Files (with dynamic patch for app.py)
    for file in files:
        src_file = os.path.join(source_dir, file)
        dst_file = os.path.join(target_dir, file)
        
        if os.path.exists(src_file):
            print(f"Copying file: {file} ...")
            if file == "app.py":
                # Read and patch bundle_dir detection
                with open(src_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Replace the relative path parent directory lookups
                old_str = 'bundle_dir = os.path.join(os.path.dirname(__file__), "..", "[PUB] India_runs_data_and_ai_challenge", "India_runs_data_and_ai_challenge")'
                new_str = 'bundle_dir = os.path.dirname(__file__)'
                
                if old_str in content:
                    content = content.replace(old_str, new_str)
                    print("  → Patched app.py bundle paths to point to current directory.")
                else:
                    print("  → Note: app.py bundle path string not found, copying unchanged.")
                
                with open(dst_file, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                shutil.copy2(src_file, dst_file)
        else:
            print(f"Warning: Source file '{file}' not found in source.")

    print("\n" + "=" * 80)
    print("  Project setup completed successfully!")
    print("=" * 80)
    print("\nNext steps to run on your local machine:")
    print("1. Install requirements:")
    print("   pip install -r requirements.txt")
    print("\n2. Generate candidate ranking (submission.csv):")
    print("   python rank.py --candidates ./candidates.jsonl --out ./submission.csv --verbose")
    print("\n3. Validate the submission:")
    print("   python validate_submission.py submission.csv")
    print("\n4. Run the visual interactive Streamlit app:")
    print("   streamlit run app.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
