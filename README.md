# 🧠 HireScope AI — Intelligent Candidate Discovery & Ranking System

HireScope AI is an advanced, AI-powered recruitment assistant designed to automate and optimize the process of screening and ranking candidates. The system parses resumes (PDF and TXT), extracts skills using an NLP-based multi-pass taxonomy matcher, evaluates candidates against Job Descriptions (JDs), and displays detailed matching scores and explanations via a premium Streamlit dashboard.

Additionally, HireScope AI includes a specialized, high-performance rule-based ranking engine and honeypot detector designed for processing large-scale candidate databases (e.g., the 100,000-candidate Redrob Hackathon pool) under strict execution and resource constraints.

---

## 🛠️ Architecture & Core Components

```
HireScope-AI/
├── app.py                      # Main Streamlit dashboard application (w/ Hackathon Mode)
├── rank.py                     # CLI Entrypoint for the Hackathon Ranker (100K candidates)
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
├── submission_metadata.yaml    # Hackathon Submission Metadata
│
├── core/
│   ├── __init__.py            # Shared data dataclasses
│   ├── resume_parser.py       # PDF/TXT text parser & metadata extractor
│   ├── skill_extractor.py     # Multi-pass NLP skill parser
│   ├── jd_analyzer.py         # Job description analyzer
│   ├── matching_engine.py     # TF-IDF lexical and Sentence Transformer semantic matching
│   ├── scoring_engine.py      # Weighted score calculator & results exporter
│   ├── explainer.py           # Natural-language comparative explanation generator
│   ├── hackathon_ranker.py    # specialised scoring & ranking logic for Redrob candidates
│   └── honeypot_detector.py   # Multi-heuristic consistency checking (~80 trap profiles)
│
├── data/
│   ├── __init__.py
│   ├── skills_database.py     # 500+ skills taxonomy with category & alias mappings
│   ├── generate_sample_pdfs.py# Utility to compile demo text resumes into formatted PDFs
│   └── sample_resumes/        # Directory containing 5 sample text resumes
│
├── ui/
│   ├── __init__.py
│   ├── components.py          # Modular, glassmorphic Streamlit layout elements
│   ├── styles.py              # Custom CSS rules for dark mode & animations
│   └── charts.py              # Plotly radar, horizontal bar, and gauge viz helpers
│
└── utils/
    ├── __init__.py
    ├── text_processing.py     # Text clean, tokenize, email, phone & experience parsers
    └── constants.py           # App configuration weights, paths, and modes
```

---

## ⚙️ How It Works

1. **Resume Parser**: Extracts raw text from uploaded files (supports `.pdf` via `pdfplumber` and plain `.txt`).
2. **Skill Extractor**: Matches terms in the parsed sections against a dictionary of 500+ core technical skills using exact matches, n-gram phrases, and aliases.
3. **JD Analyzer**: Parses job description text to establish minimum experience targets, desired education level, seniority, and distinct lists of required vs. preferred skillsets.
4. **Matching Engine**: Features a dual-mode alignment comparison:
   - **Phase 1 (TF-IDF)**: Calculates exact word overlap and lexical frequencies using TF-IDF vectorization and cosine similarity.
   - **Phase 2 (Sentence Transformer)**: Uses a local model (`all-MiniLM-L6-v2`) to capture conceptual equivalents (e.g., matching "Deep Learning" to "Neural Networks").
5. **Hackathon Ranker**: High-performance pipeline optimized to run within 5 minutes on CPU:
   - **Honeypot Filter**: Removes candidates exhibiting temporal inconsistencies, inverted salaries, bot-like endorsement spikes, and education date errors.
   - **Trust Multiplier**: Mitigates key-word stuffers by down-weighting skills with zero endorsements and short experience durations.
   - **Composite Score**: Weighs Skills (35%), Title/Career Alignment (25%), Experience Fit (15%), Education Fit (10%), and Behavioral Signals (15%).
6. **Explainability**: Generates a natural-language report summarizing a candidate's key strengths, missing keywords, experience gap, and comparative ranking.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
Ensure you have Python 3.10+ installed. Install the required python packages from the project root:
```bash
pip install -r requirements.txt
```

### 2. Download NLP Models & Corpora
Download the required NLTK tokenizer and stopword lists:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```

### 3. Run the CLI Hackathon Ranker
To rank the 100,000-candidate pool and generate your submission CSV:
```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv --verbose
```

### 4. Run the Streamlit Dashboard
Launch the web application local server:
```bash
streamlit run app.py
```
To run the hackathon dataset visually, select **"🏆 Hackathon Dataset (100K JSONL)"** in the sidebar under **Resume Source** and run the analysis.
