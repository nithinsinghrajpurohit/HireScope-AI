"""
HireScope AI — Main Streamlit Entrypoint.
Provides a premium recruitment assistant dashboard to parse resumes,
semantically rank candidates against JDs, and visualize matching analytics.
Also supports the Redrob Hackathon 100K JSONL candidate dataset.
"""

import streamlit as st
import os
import glob
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Core modules
from core.resume_parser import ResumeParser
from core.jd_analyzer import analyze_jd
from core.scoring_engine import rank_candidates, save_results, results_to_dataframe
from core.explainer import generate_explanation, generate_comparative_analysis

# Hackathon modules
from core.hackathon_ranker import (
    load_candidates as load_jsonl_candidates,
    parse_jd_text as parse_hackathon_jd,
    load_jd as load_hackathon_jd,
    rank_candidates_for_submission,
    write_submission_csv,
    extract_text_from_docx,
)
from core.honeypot_detector import batch_detect_honeypots

# UI Components
from ui.styles import apply_theme
from ui.components import (
    header_banner,
    metric_card,
    render_skill_tags,
    render_candidate_card,
    score_breakdown_bars,
    comparison_matrix,
    compare_two_candidates_matrix,
)
from ui.charts import radar_comparison_chart, breakdown_bar_chart, gauge_chart
from utils.constants import MODE_TFIDF, MODE_SEMANTIC

# Page configuration
st.set_page_config(
    page_title="HireScope AI - Recruitment Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply premium dark theme styles
apply_theme()

# Define Predefined JDs
JD_TEMPLATES = {
    "Select a Template...": "",
    "Machine Learning Engineer (Python/ML)": (
        "JOB TITLE: Machine Learning Engineer\n\n"
        "We are looking for a Machine Learning Engineer with 3+ years of experience.\n"
        "REQUIRED SKILLS: Python, Machine Learning, TensorFlow, PyTorch, Scikit-Learn, SQL\n"
        "PREFERRED SKILLS: FastAPI, Flask, Git, Docker, Databases, R\n"
        "EDUCATION: Master's degree in Computer Science, Data Analytics, or related field."
    ),
    "Full Stack Web Developer (JS/React/Node)": (
        "JOB TITLE: Full Stack Web Developer\n\n"
        "We are seeking a Full Stack Web Developer with 3 years of experience.\n"
        "REQUIRED SKILLS: React, Node.js, Express, JavaScript, TypeScript, CSS, SQL\n"
        "PREFERRED SKILLS: Next.js, Tailwind CSS, MongoDB, Git, GitHub Actions\n"
        "EDUCATION: Bachelor's degree in Software Engineering or Computer Science."
    ),
    "Cloud DevOps Architect (AWS/K8s/Terraform)": (
        "JOB TITLE: Cloud DevOps Architect\n\n"
        "Looking for a Principal Cloud DevOps Architect with 8+ years of experience.\n"
        "REQUIRED SKILLS: AWS, Kubernetes, Docker, Terraform, CI/CD, Ansible\n"
        "PREFERRED SKILLS: Linux, Go, Python, Bash, Jenkins, Redis, Cassandra\n"
        "EDUCATION: PhD or Master's degree in Computer Systems or Computer Engineering."
    ),
}


# Initialize Session State
if "ranked_results" not in st.session_state:
    st.session_state["ranked_results"] = None
if "jd_requirements" not in st.session_state:
    st.session_state["jd_requirements"] = None
if "selected_jd_text" not in st.session_state:
    st.session_state["selected_jd_text"] = ""
if "current_mode" not in st.session_state:
    st.session_state["current_mode"] = MODE_SEMANTIC
if "hackathon_results" not in st.session_state:
    st.session_state["hackathon_results"] = None
if "hackathon_honeypots" not in st.session_state:
    st.session_state["hackathon_honeypots"] = {}


# Render Header
header_banner()

# ───────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ───────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="section-label">Step 1</span>', unsafe_allow_html=True)
    st.markdown("### 📋 Job Description")
    
    # Template Selectbox
    selected_template = st.selectbox(
        "Load Predefined Template:",
        options=list(JD_TEMPLATES.keys()),
    )
    
    if selected_template != "Select a Template..." and JD_TEMPLATES[selected_template] != st.session_state["selected_jd_text"]:
        st.session_state["selected_jd_text"] = JD_TEMPLATES[selected_template]
        
    jd_input = st.text_area(
        "Edit Job Description Text:",
        value=st.session_state["selected_jd_text"],
        height=200,
        placeholder="Paste your JD here, including required skills, years of experience, and degree requirements..."
    )
    
    st.markdown("---")
    st.markdown('<span class="section-label">Step 2</span>', unsafe_allow_html=True)
    st.markdown("### 📁 Candidate Resumes")
    
    upload_source = st.radio(
        "Resume Source:",
        options=[
            "Upload Custom Resumes",
            "Load 5 Demo Resumes (Alice, Bob, Carol, Dave, Eve)",
            "🏆 Hackathon Dataset (100K JSONL)",
        ],
    )
    
    uploaded_files = []
    hackathon_candidate_path = ""
    hackathon_jd_path = ""
    
    if upload_source == "Upload Custom Resumes":
        uploaded_files = st.file_uploader(
            "Upload Resumes (PDF or TXT):",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            help="Upload one or multiple candidate resumes to rank them."
        )
    elif upload_source == "🏆 Hackathon Dataset (100K JSONL)":
        st.info("🏆 **Redrob Hackathon Mode** — Ranks 100K candidates from JSONL dataset.")
        
        # Auto-detect paths with fallback
        bundle_dir = os.path.dirname(__file__)
        if not os.path.exists(os.path.join(bundle_dir, "data", "sample_candidates.json")):
            parent_fallback = os.path.join(bundle_dir, "..", "[PUB] India_runs_data_and_ai_challenge", "India_runs_data_and_ai_challenge")
            if os.path.exists(parent_fallback):
                bundle_dir = parent_fallback
        bundle_dir = os.path.normpath(bundle_dir)
        
        default_cand = ""
        # Prioritize the inbuilt sample file
        repo_sample_path = os.path.join(bundle_dir, "data", "sample_candidates.json")
        if os.path.exists(repo_sample_path):
            default_cand = "data/sample_candidates.json"
        else:
            for p in [os.path.join(bundle_dir, "candidates.jsonl"), os.path.join(bundle_dir, "candidates.jsonl.gz"), os.path.join(bundle_dir, "sample_candidates.json")]:
                if os.path.exists(p):
                    default_cand = p
                    break
        
        # Fallback default so it is prefilled
        if not default_cand:
            default_cand = "data/sample_candidates.json"
        
        hackathon_candidate_path = st.text_input("Candidates file path:", value=default_cand, help="Path to candidates.jsonl, .jsonl.gz or sample_candidates.json")
        
        default_jd = os.path.join(bundle_dir, "job_description.docx")
        hackathon_jd_path = st.text_input("JD file path (optional):", value=default_jd if os.path.exists(default_jd) else "", help="Path to job_description.docx or .md")
        
        hackathon_top_n = st.slider("Top N candidates to rank:", min_value=10, max_value=500, value=100, step=10)
    
    st.markdown("---")
    st.markdown('<span class="section-label">Step 3</span>', unsafe_allow_html=True)
    st.markdown("### ⚙️ Engine Settings")
    
    if upload_source != "🏆 Hackathon Dataset (100K JSONL)":
        matching_mode = st.selectbox(
            "Matching Strategy Mode:",
            options=[MODE_SEMANTIC, MODE_TFIDF],
            help="Semantic (Sentence Transformers) matches concepts and synonyms. TF-IDF matches exact keyword overlap."
        )
    else:
        matching_mode = "Hackathon (Rule-Based)"
        st.markdown("**Mode**: Multi-Signal Rule-Based Ranker (Skills 35% + Title 25% + Experience 15% + Education 10% + Behavioral 15%)")
    
    # Run analysis trigger
    analyze_button = st.button("🚀 Analyze & Rank Candidates", use_container_width=True)
    
    # ── SIDEBAR FOOTER ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <div style="color: #64748B; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.4rem;">HireScope AI v2.0</div>
        <div style="color: rgba(99,102,241,0.5); font-size: 0.65rem;">NLP • Sentence Transformers • TF-IDF</div>
        <div style="color: rgba(148,163,184,0.4); font-size: 0.6rem; margin-top: 0.3rem;">Built for Redrob Hackathon 2026</div>
    </div>
    """, unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────────
# ANALYSIS PIPELINE
# ───────────────────────────────────────────────────────────────────────────
if analyze_button:
    # ── HACKATHON DATASET PIPELINE ────────────────────────────────────
    if upload_source == "🏆 Hackathon Dataset (100K JSONL)":
        if not hackathon_candidate_path or not os.path.exists(hackathon_candidate_path):
            st.error("⚠️ Please provide a valid path to the candidates file.")
        else:
            with st.spinner("Loading and ranking hackathon candidates... This may take a minute."):
                import time
                t0 = time.time()
                
                # Load JD
                if hackathon_jd_path and os.path.exists(hackathon_jd_path):
                    jd = load_hackathon_jd(hackathon_jd_path)
                else:
                    jd = parse_hackathon_jd(jd_input if jd_input.strip() else "")
                
                # Load candidates
                candidates = load_jsonl_candidates(hackathon_candidate_path)
                st.info(f"📦 Loaded {len(candidates):,} candidates in {time.time()-t0:.1f}s")
                
                # Detect honeypots
                t1 = time.time()
                honeypots = batch_detect_honeypots(candidates)
                honeypot_ids = set(honeypots.keys())
                st.info(f"🍯 Detected {len(honeypots):,} honeypots in {time.time()-t1:.1f}s")
                
                # Rank
                t2 = time.time()
                top_n = hackathon_top_n if 'hackathon_top_n' in dir() else 100
                ranked = rank_candidates_for_submission(candidates, jd, honeypot_ids, top_n=top_n)
                st.info(f"🏆 Ranked top {len(ranked)} candidates in {time.time()-t2:.1f}s")
                
                # Store results
                st.session_state["hackathon_results"] = ranked
                st.session_state["hackathon_honeypots"] = honeypots
                st.session_state["ranked_results"] = None  # Clear resume-based results
                
                # Save CSV
                out_path = os.path.join("results", "hackathon_submission.csv")
                os.makedirs("results", exist_ok=True)
                write_submission_csv(ranked, out_path)
                
                total_time = time.time() - t0
                st.success(f"✅ Hackathon ranking complete in {total_time:.1f}s! CSV saved to {out_path}")
    
    # ── STANDARD RESUME PIPELINE ─────────────────────────────────────
    elif not jd_input.strip():
        st.error("⚠️ Please enter a Job Description in the sidebar before running the analysis.")
    else:
        # Load resumes
        resumes_to_parse = []
        
        if upload_source == "Load 5 Demo Resumes (Alice, Bob, Carol, Dave, Eve)":
            demo_dir = Path("data/sample_resumes")
            if demo_dir.exists():
                txt_files = list(demo_dir.glob("*.txt"))
                if txt_files:
                    for path in txt_files:
                        with open(path, "rb") as f:
                            # Mimic Streamlit UploadedFile class using custom wrapper
                            class MockUploadedFile:
                                def __init__(self, file_path):
                                    self.path = file_path
                                    self.name = file_path.name
                                def read(self):
                                    with open(self.path, "rb") as file:
                                        return file.read()
                            resumes_to_parse.append(MockUploadedFile(path))
                else:
                    st.error("⚠️ Demo resume text files not found. Please verify they exist in data/sample_resumes/.")
            else:
                st.error("⚠️ Demo directory data/sample_resumes/ does not exist.")
        else:
            resumes_to_parse = uploaded_files
            
        if not resumes_to_parse:
            st.error("⚠️ Please upload at least one resume or select the Demo Resumes source.")
        else:
            with st.spinner("Processing resumes, analyzing requirements, and performing similarity computation..."):
                parser = ResumeParser()
                parsed_resumes = []
                
                # Parse all resumes
                for file_obj in resumes_to_parse:
                    parsed_resume = parser.parse_file(file_obj)
                    if parsed_resume.parse_errors:
                        st.warning(f"Skipped {file_obj.name} due to parse error: {parsed_resume.parse_errors[0]}")
                    else:
                        parsed_resumes.append(parsed_resume)
                        
                if not parsed_resumes:
                    st.error("❌ No resumes were parsed successfully. Check your files and try again.")
                else:
                    # Parse JD Requirements
                    jd_req = analyze_jd(jd_input)
                    
                    # Compute scores and rank
                    ranked_candidates = rank_candidates(
                        resume_data_list=parsed_resumes,
                        jd_req=jd_req,
                        mode=matching_mode,
                    )
                    
                    # Enrich each candidate with Hackathon High-Score features
                    for idx, c in enumerate(ranked_candidates, start=1):
                        c.explanation = generate_explanation(c, jd_req, idx)
                    
                    # Save results automatically
                    save_results(ranked_candidates, jd_req)
                    
                    # Store in session state
                    st.session_state["ranked_results"] = ranked_candidates
                    st.session_state["jd_requirements"] = jd_req
                    st.session_state["current_mode"] = matching_mode
                    st.session_state["hackathon_results"] = None  # Clear hackathon results
                    
                    st.success("✅ Candidates successfully analyzed and ranked!")

# ───────────────────────────────────────────────────────────────────────────
# DASHBOARD DISPLAY
# ───────────────────────────────────────────────────────────────────────────
results = st.session_state["ranked_results"]
jd_req = st.session_state["jd_requirements"]

if results is not None and jd_req is not None:
    # ── METRIC CARDS ──────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    
    total_candidates = len(results)
    best_candidate = results[0].candidate_name
    best_score = f"{results[0].overall_score:.1f}%"
    
    avg_score_val = sum(c.overall_score for c in results) / total_candidates
    avg_score = f"{avg_score_val:.1f}%"
    
    metric_card("Total Candidates", str(total_candidates), col1)
    metric_card("Top Match Candidate", f"{best_candidate} ({best_score})", col2)
    metric_card("Average Match Score", avg_score, col3)
    metric_card("Matching Engine Mode", st.session_state["current_mode"].split("(")[0].strip(), col4)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── QUICK INSIGHT CARDS ───────────────────────────────────────────────
    ic1, ic2, ic3, ic4 = st.columns(4)
    
    # Compute quick insights
    strong_count = sum(1 for c in results if c.overall_score >= 70)
    all_matched_skills = set()
    for c in results:
        all_matched_skills.update(c.matched_skills)
    score_spread = results[0].overall_score - results[-1].overall_score if len(results) > 1 else 0
    avg_exp = sum(c.experience_years for c in results) / total_candidates
    
    with ic1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Strong Matches (≥70%)</div>
            <div class="insight-value">{strong_count}/{total_candidates}</div>
        </div>
        """, unsafe_allow_html=True)
    with ic2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Unique Skills Detected</div>
            <div class="insight-value">{len(all_matched_skills)}</div>
        </div>
        """, unsafe_allow_html=True)
    with ic3:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Score Spread</div>
            <div class="insight-value">{score_spread:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with ic4:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Avg Experience</div>
            <div class="insight-value">{avg_exp:.1f} Yrs</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── MAIN TABS ─────────────────────────────────────────────────────────
    tab_overview, tab_rankings, tab_analytics, tab_compare, tab_deep_dive = st.tabs([
        "🏠 Overview Dashboard",
        "🏆 Candidate Rankings",
        "📊 Visual Analytics",
        "👥 Candidate Comparison",
        "🔍 Individual Deep Dive"
    ])
    
    # ── TAB 1: OVERVIEW ──
    with tab_overview:
        st.markdown('<div class="labeled-divider"><span>Job Requirements</span></div>', unsafe_allow_html=True)
        st.subheader("📋 Role Alignment Overview")
        
        # Display parsed requirements info
        st.markdown(
            f"""
            <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; margin: 0.8rem 0 1.2rem;">
                <div><span class="rc-label">Position</span><br><span class="rc-name">{jd_req.title}</span></div>
                <div><span class="rc-label">Seniority</span><br><span class="status-chip status-info">{jd_req.seniority.title()}</span></div>
                <div><span class="rc-label">Experience</span><br><span class="status-chip status-pass">{jd_req.min_experience:.0f}+ Years</span></div>
                <div><span class="rc-label">Education</span><br><span class="status-chip status-warn">{jd_req.education_level.title() if jd_req.education_level else "Any"}</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("##### Required Skills Taxonomy Matching:")
        st.markdown(render_skill_tags(jd_req.required_skills), unsafe_allow_html=True)
        
        if jd_req.preferred_skills:
            st.markdown("##### Preferred / Bonus Skills:")
            st.markdown(render_skill_tags(jd_req.preferred_skills), unsafe_allow_html=True)
            
        st.markdown('<div class="labeled-divider"><span>Comparative Analysis</span></div>', unsafe_allow_html=True)
        st.subheader("💡 Comparative Fit Summary")
        summary_text = generate_comparative_analysis(results, jd_req)
        st.info(summary_text)

        st.markdown('<div class="labeled-divider"><span>Ranking Matrix</span></div>', unsafe_allow_html=True)
        st.subheader("📊 Candidate Overview Matrix")
        comparison_matrix(results)
        
        # Download results buttons
        df_export = results_to_dataframe(results)
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Download Rankings Summary (CSV)",
            data=csv_data,
            file_name=f"hirescope_rankings_{jd_req.title.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        
    # ── TAB 2: RANKINGS ──
    with tab_rankings:
        st.subheader("🏆 Candidate Rank Leaderboard")
        st.markdown('<span class="rc-dim">Select a candidate to see their detailed matching breakdown.</span>', unsafe_allow_html=True)
        
        for idx, c in enumerate(results, start=1):
            rec_text = getattr(c, "recommendation", "")
            rec_style = getattr(c, "recommendation_style", "")
            st.markdown(render_candidate_card(
                rank=idx,
                name=c.candidate_name,
                score=c.overall_score,
                file_name=c.file_name,
                matched=c.matched_skills,
                exp_years=c.experience_years,
                rec_text=rec_text,
                rec_style=rec_style
            ), unsafe_allow_html=True)
            
            with st.expander(f"View Quick Scoring Details for {c.candidate_name}", expanded=(idx==1)):
                col_b1, col_b2 = st.columns([3, 2])
                with col_b1:
                    st.markdown("##### Weight Category Breakdown:")
                    score_breakdown_bars(c.explanation.score_breakdown)
                with col_b2:
                    st.markdown("##### Key Strengths:")
                    for s in c.explanation.strengths[:3]:
                        st.markdown(f'<span class="match-icon-check">✓</span> {s}', unsafe_allow_html=True)
                    if c.explanation.improvement_areas and c.explanation.improvement_areas != ["No significant gaps identified."]:
                        st.markdown("##### Critical Gaps:")
                        for gap in c.explanation.improvement_areas[:2]:
                            st.markdown(f'<span class="match-icon-cross">✗</span> {gap}', unsafe_allow_html=True)
                            
                # Link to deep dive
                st.info(f"💡 {c.explanation.ranking_reason}")

    # ── TAB 3: ANALYTICS ──
    with tab_analytics:
        st.subheader("📊 Matching Analytics")
        st.markdown('<span class="rc-dim">Visual breakdowns of candidate scoring and skill coverage across the pool.</span>', unsafe_allow_html=True)
        
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            st.markdown("##### Radar Comparison (Top 4 Candidates)")
            radar_fig = radar_comparison_chart(results)
            st.plotly_chart(radar_fig, use_container_width=True)
            
        with col_c2:
            st.markdown("##### Score Distribution Breakdown")
            
            # Simple bar chart of overall scores
            c_names = [c.candidate_name for c in results]
            c_scores = [c.overall_score for c in results]
            
            # Highlight colors
            colors_list = ["#6EE7B7" if score >= 75 else "#818CF8" if score >= 50 else "#FCA5A5" for score in c_scores]
            
            fig_bar = go.Figure(go.Bar(
                x=c_scores,
                y=c_names,
                orientation='h',
                marker_color=colors_list,
                text=[f"{s:.1f}%" for s in c_scores],
                textposition='inside'
            ))
            fig_bar.update_layout(
                xaxis=dict(title="Overall Score (%)", range=[0, 100], gridcolor="rgba(99,102,241,0.06)"),
                yaxis=dict(autorange="reversed"),
                margin=dict(l=20, r=20, t=10, b=10),
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("##### Skill Coverage Across All Candidates")
        
        # Aggregate all matched and missing skills to display distributions
        all_required = set(jd_req.required_skills)
        skill_stats = []
        for s in all_required:
            have_count = sum(1 for c in results if s in c.matched_skills)
            percent = (have_count / total_candidates) * 100
            skill_stats.append({"Skill": s, "Coverage (%)": percent, "Count": have_count})
            
        df_skills = pd.DataFrame(skill_stats).sort_values("Coverage (%)", ascending=False)
        
        fig_skills = px.bar(
            df_skills,
            x="Coverage (%)",
            y="Skill",
            text="Count",
            color="Coverage (%)",
            color_continuous_scale=[[0, "#1E1B4B"], [0.5, "#6366F1"], [1, "#E0E7FF"]],
            range_x=[0, 100]
        )
        fig_skills.update_layout(
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=10, b=10),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        fig_skills.update_traces(texttemplate='%{text} candidates', textposition='outside')
        st.plotly_chart(fig_skills, use_container_width=True)

    # ── TAB 4: COMPARE ──
    with tab_compare:
        st.subheader("👥 Side-by-Side Comparison")
        st.markdown('<span class="rc-dim">Select two candidates to compare scoring, skills, and recommendation tiers.</span>', unsafe_allow_html=True)
        
        col_comp_select1, col_comp_select2 = st.columns(2)
        with col_comp_select1:
            cand_a_name = st.selectbox(
                "Select Candidate A (Purple):",
                options=[c.candidate_name for c in results],
                index=0
            )
        with col_comp_select2:
            default_index = 1 if len(results) > 1 else 0
            cand_b_name = st.selectbox(
                "Select Candidate B (Cyan):",
                options=[c.candidate_name for c in results],
                index=default_index
            )
            
        if cand_a_name == cand_b_name:
            st.warning("💡 Select two different candidates to compare them side-by-side.")
        else:
            c_a = next(cand for cand in results if cand.candidate_name == cand_a_name)
            c_b = next(cand for cand in results if cand.candidate_name == cand_b_name)
            
            # Gauge charts side by side
            col_gauge1, col_gauge2 = st.columns(2)
            with col_gauge1:
                st.plotly_chart(gauge_chart(c_a.overall_score, c_a.candidate_name), use_container_width=True)
            with col_gauge2:
                st.plotly_chart(gauge_chart(c_b.overall_score, c_b.candidate_name), use_container_width=True)
                
            # Radar chart comparison
            st.markdown("##### Dimension Analysis Comparison")
            radar_fig_two = radar_comparison_chart([c_a, c_b])
            st.plotly_chart(radar_fig_two, use_container_width=True)
            
            # Side-by-side comparison table
            st.markdown("##### Detailed Comparison Matrix")
            compare_two_candidates_matrix(c_a, c_b)

    # ── TAB 5: DEEP DIVE ──
    with tab_deep_dive:
        st.subheader("🔍 Candidate Deep Dive Dossier")
        
        selected_name = st.selectbox(
            "Select Candidate to Profile:",
            options=[c.candidate_name for c in results]
        )
        
        # Get selected candidate score object
        c = next(cand for cand in results if cand.candidate_name == selected_name)
        
        # Layout columns
        col_d1, col_d2 = st.columns([1, 2])
        
        with col_d1:
            # Display name and contact details
            st.markdown(f"### {c.candidate_name}")
            st.markdown(f'<span class="rc-label">File:</span> <span class="rc-value">{c.file_name}</span>', unsafe_allow_html=True)
            
            # Circular Gauge
            gauge_fig = gauge_chart(c.overall_score, "Overall Match")
            st.plotly_chart(gauge_fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown("##### 📞 Contact Information")
            email_val = c.resume_data.email if hasattr(c.resume_data, "email") else "Not found"
            phone_val = c.resume_data.phone if hasattr(c.resume_data, "phone") else "Not found"
            linkedin_val = c.resume_data.linkedin if hasattr(c.resume_data, "linkedin") else "Not found"
            
            st.markdown(f"✉️ **Email**: {email_val or 'Not found'}")
            st.markdown(f"📞 **Phone**: {phone_val or 'Not found'}")
            st.markdown(f"🔗 **LinkedIn**: {linkedin_val or 'Not found'}")

        with col_d2:
            st.markdown('### 💬 AI Recruiter Assistant Report', unsafe_allow_html=True)
            
            rec_text = getattr(c, "recommendation", "Consider")
            rec_style = getattr(c, "recommendation_style", "")
            rec_badge = f'<span class="rec-badge" style="{rec_style}">{rec_text}</span>'
            
            st.markdown(f'<span class="rc-label">Recommendation</span> {rec_badge}', unsafe_allow_html=True)
            st.markdown(f"**Executive Fit Summary**:\n\n{getattr(c, 'summary', 'No summary generated.')}")
            
            col_report1, col_report2 = st.columns(2)
            with col_report1:
                st.markdown("##### ⚠️ Concerns & Red Flags:")
                red_flags_list = getattr(c, "red_flags", ["No critical concerns detected."])
                for flag in red_flags_list:
                    if flag == "No critical concerns detected.":
                        st.markdown(f'<span class="status-chip status-pass" style="margin-right:0.4rem;">✓ PASS</span> {flag}', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="status-chip status-warn" style="margin-right:0.4rem;">⚠️ FLAG</span> {flag}', unsafe_allow_html=True)
            with col_report2:
                st.markdown("##### 📋 Recommended Improvements:")
                suggestions_list = c.explanation.improvement_areas
                for sug in suggestions_list[:3]:
                    st.markdown(f'<span class="match-icon-check">✓</span> {sug}', unsafe_allow_html=True)
                    
            st.markdown("##### ❓ Tailored Technical Interview Questions:")
            questions_list = getattr(c, "interview_questions", [])
            for q_idx, q in enumerate(questions_list, start=1):
                st.markdown(f"**Q{q_idx}**: *{q}*")

            st.subheader("📋 Fit Assessment Summary")
            
            col_d2_1, col_d2_2 = st.columns(2)
            with col_d2_1:
                st.markdown(f'<span class="rc-label">Experience</span> <span class="status-chip status-pass">{c.experience_years:.1f} Years</span>', unsafe_allow_html=True)
                st.markdown(f'<span class="rc-dim">{c.explanation.experience_assessment}</span>', unsafe_allow_html=True)
            with col_d2_2:
                education_val = "Not found"
                if hasattr(c.resume_data, "sections") and c.resume_data.sections.get("education"):
                    education_val = c.resume_data.sections.get("education").split("\n")[0]
                elif hasattr(c.resume_data, "education_text") and c.resume_data.education_text:
                    education_val = c.resume_data.education_text.split("\n")[0]
                st.markdown(f'<span class="rc-label">Education</span> <span class="status-chip status-info">{education_val[:50] if education_val else "Not found"}</span>', unsafe_allow_html=True)
                st.markdown(f'<span class="rc-dim">Required: {jd_req.education_level.title() if jd_req.education_level else "Any"}</span>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("##### Detailed Fit Breakdown:")
            score_breakdown_bars(c.explanation.score_breakdown)

            st.subheader("💡 Strengths & Gap Analysis")
            
            col_d3_1, col_d3_2 = st.columns(2)
            
            with col_d3_1:
                st.markdown("##### 🟢 Key Strengths:")
                for strength in c.explanation.strengths[:4]:
                    st.markdown(f'<span class="match-icon-check">✓</span> {strength}', unsafe_allow_html=True)
                    
            with col_d3_2:
                st.markdown("##### 🔴 Gaps & Growth Areas:")
                for gap in c.explanation.improvement_areas[:4]:
                    st.markdown(f'<span class="match-icon-cross">✗</span> {gap}', unsafe_allow_html=True)

            st.subheader("🧠 Skills Mapping Details")
            
            # Matched Skills
            st.markdown("##### Matched Skills:")
            st.markdown(render_skill_tags(c.matched_skills), unsafe_allow_html=True)
            
            # Missing Skills
            if c.missing_skills:
                st.markdown("##### Missing Required Skills:")
                missing_html = "".join(f'<span class="skill-tag tag-missing">{s.upper()}</span>' for s in c.missing_skills)
                st.markdown(missing_html, unsafe_allow_html=True)
                
            # Extra/Bonus Skills
            if c.extra_skills:
                st.markdown("##### Extra/Bonus Skills:")
                st.markdown(render_skill_tags(c.extra_skills), unsafe_allow_html=True)
                
            # Outreach Email Generator
            st.markdown("---")
            st.subheader("✉️ Automated Outreach Assistant")
            with st.expander("Generate Personalized Recruiter Outreach Email", expanded=False):
                skills_str = ", ".join(c.matched_skills[:3]) if c.matched_skills else "matching skills"
                email_template = f"""Subject: Exciting Opportunity: AI/ML Engineer Role at HireScope AI

Hi {c.candidate_name},

I came across your profile and was impressed by your background.

Specifically, your expertise in {skills_str} aligns perfectly with the requirements for the position we are recruiting for.

Are you available for a brief 15-minute call this week to discuss?

Best regards,
[Your Name]
Talent Acquisition Team, HireScope AI
"""
                st.code(email_template, language="text")

            # Raw Resume text foldout
            with st.expander("📄 View Parsed Resume Raw Text", expanded=False):
                st.code(c.resume_data.raw_text, language="text")

else:
    hack_results = st.session_state.get("hackathon_results")
    if hack_results:
        st.markdown("## 🏆 Hackathon Ranking Results")
        col1, col2, col3, col4 = st.columns(4)
        metric_card("Total Ranked", str(len(hack_results)), col1)
        metric_card("Top Candidate", f"{hack_results[0]['candidate_name']}", col2)
        avg_score = sum(r['composite_score'] for r in hack_results) / len(hack_results)
        metric_card("Avg Score", f"{avg_score:.4f}", col3)
        hp_count = len(st.session_state.get("hackathon_honeypots", {}))
        metric_card("Honeypots Filtered", str(hp_count), col4)

        # ── HIRING FUNNEL PIPELINE ─────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🔄 Hiring Pipeline Funnel")
        total_loaded = len(hack_results) + hp_count
        p1, pa1, p2, pa2, p3, pa3, p4 = st.columns([2, 1, 2, 1, 2, 1, 2])
        with p1:
            st.markdown(f"""
            <div class="pipeline-stage">
                <div class="stage-number">{total_loaded:,}</div>
                <div class="stage-label">Total Loaded</div>
            </div>
            """, unsafe_allow_html=True)
        with pa1:
            st.markdown('<div class="pipeline-arrow">→</div>', unsafe_allow_html=True)
        with p2:
            st.markdown(f"""
            <div class="pipeline-stage">
                <div class="stage-number">{hp_count}</div>
                <div class="stage-label">Honeypots Caught</div>
            </div>
            """, unsafe_allow_html=True)
        with pa2:
            st.markdown('<div class="pipeline-arrow">→</div>', unsafe_allow_html=True)
        with p3:
            st.markdown(f"""
            <div class="pipeline-stage">
                <div class="stage-number">{total_loaded - hp_count:,}</div>
                <div class="stage-label">Valid Scored</div>
            </div>
            """, unsafe_allow_html=True)
        with pa3:
            st.markdown('<div class="pipeline-arrow">→</div>', unsafe_allow_html=True)
        with p4:
            st.markdown(f"""
            <div class="pipeline-stage" style="border-color: rgba(110,231,183,0.3);">
                <div class="stage-number" style="background: linear-gradient(135deg, #6EE7B7, #34D399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{len(hack_results)}</div>
                <div class="stage-label">Top Ranked</div>
            </div>
            """, unsafe_allow_html=True)
        
        # ── AI INSIGHTS ROW ────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        i1, i2, i3, i4 = st.columns(4)
        
        # Compute insights
        top_titles = {}
        for r in hack_results:
            t = r.get("current_title", "Unknown")
            top_titles[t] = top_titles.get(t, 0) + 1
        most_common_title = max(top_titles, key=top_titles.get) if top_titles else "N/A"
        
        avg_exp = sum(r.get("years_experience", 0) for r in hack_results) / len(hack_results)
        
        all_matched = set()
        for r in hack_results:
            all_matched.update(r.get("matched_skills", []))
        
        top_score = hack_results[0]["composite_score"] * 100
        
        with i1:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Most Common Title</div>
                <div style="color: #E2E8F0; font-weight: 600; font-size: 0.95rem;">{most_common_title}</div>
            </div>
            """, unsafe_allow_html=True)
        with i2:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Avg Experience</div>
                <div class="insight-value">{avg_exp:.1f} Yrs</div>
            </div>
            """, unsafe_allow_html=True)
        with i3:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Unique Skills Found</div>
                <div class="insight-value">{len(all_matched)}</div>
            </div>
            """, unsafe_allow_html=True)
        with i4:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Top Score</div>
                <div class="insight-value">{top_score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        tab_lb, tab_an, tab_hp, tab_cc, tab_dd, tab_dl = st.tabs(["🏆 Leaderboard", "📊 Analytics", "🍯 Honeypots", "👥 Candidate Comparison", "🔍 Individual Deep Dive", "📥 Download"])
        with tab_lb:
            st.subheader("Top 100 Candidate Rankings")
            df_hack = pd.DataFrame([{"Rank": r["rank"], "Percentile": f"Top {r['rank']/1000.0:.3f}%", "ID": r["candidate_id"], "Name": r["candidate_name"], "Title": r["current_title"], "Exp": f"{r['years_experience']:.1f}y", "Score": f"{r['composite_score']:.4f}", "Skills": f"{r['skill_score']:.2f}", "#Matched": len(r["matched_skills"]), "Reasoning": r["reasoning"]} for r in hack_results])
            st.dataframe(df_hack, use_container_width=True, height=600)
        with tab_an:
            col_an1, col_an2 = st.columns(2)
            with col_an1:
                st.subheader("📊 Score Distribution")
                scores_list = [r["composite_score"] for r in hack_results]
                fig_h = px.histogram(x=scores_list, nbins=20, labels={'x': 'Composite Score', 'y': 'Count'})
                fig_h.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=30, b=20), height=320)
                st.plotly_chart(fig_h, use_container_width=True)
            with col_an2:
                st.subheader("⚠️ Missing Skills Heatmap")
                missing_counts = {}
                for r in hack_results:
                    for skill in r.get("missing_core_skills", []):
                        missing_counts[skill] = missing_counts.get(skill, 0) + 1
                if missing_counts:
                    df_miss = pd.DataFrame([{"Skill": k, "Missing Count": v} for k, v in missing_counts.items()]).sort_values("Missing Count", ascending=False).head(10)
                    fig_miss = px.bar(df_miss, x="Missing Count", y="Skill", orientation='h', color="Missing Count", color_continuous_scale="Reds")
                    fig_miss.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=30, b=20), height=320)
                    st.plotly_chart(fig_miss, use_container_width=True)
                else:
                    st.info("No missing skills identified in the top candidates.")
            
            col_an3, col_an4 = st.columns(2)
            with col_an3:
                st.subheader("🧠 Skill Coverage Treemap")
                skill_freq = {}
                for r in hack_results:
                    for s in r.get("matched_skills", []):
                        skill_freq[s] = skill_freq.get(s, 0) + 1
                if skill_freq:
                    tree_data = pd.DataFrame([{"Skill": k, "Count": v} for k, v in skill_freq.items()]).sort_values("Count", ascending=False).head(20)
                    fig_tree = px.treemap(tree_data, path=["Skill"], values="Count", color="Count", color_continuous_scale=[[0, "#1E1B4B"], [0.5, "#6366F1"], [1, "#E0E7FF"]])
                    fig_tree.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10), height=320, coloraxis_showscale=False)
                    st.plotly_chart(fig_tree, use_container_width=True)
            with col_an4:
                st.subheader("💼 Experience Distribution")
                exp_vals = [r.get("years_experience", 0) for r in hack_results]
                fig_box = go.Figure(go.Box(y=exp_vals, marker_color="#818CF8", boxpoints="outliers", name="Years"))
                fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=30, b=20), height=320, yaxis=dict(title="Years", gridcolor="rgba(99,102,241,0.06)"))
                st.plotly_chart(fig_box, use_container_width=True)
            
            st.markdown(f"""
            <div class="exec-summary">
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; color: #6EE7B7; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">📋 Executive Summary</div>
                <div style="color: #E2E8F0; font-size: 0.9rem; line-height: 1.8;">
                    Analyzed <strong style="color: #818CF8;">{len(hack_results) + hp_count:,}</strong> candidates total.
                    Filtered <strong style="color: #FCA5A5;">{hp_count}</strong> honeypot profiles.
                    Top candidate <strong style="color: #E0E7FF;">{hack_results[0]['candidate_name']}</strong> scored 
                    <strong style="color: #6EE7B7;">{hack_results[0]['composite_score']*100:.1f}%</strong> composite match.
                    The talent pool averages <strong style="color: #818CF8;">{avg_exp:.1f} years</strong> experience with 
                    <strong style="color: #818CF8;">{len(all_matched)}</strong> unique skills represented.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab_hp:
            honeypots_data = st.session_state.get("hackathon_honeypots", {})
            st.subheader(f"🍯 Detected Honeypots ({len(honeypots_data)})")
            if honeypots_data:
                hp_df = pd.DataFrame([{"ID": cid, "Reasons": "; ".join(reasons)} for cid, reasons in list(honeypots_data.items())[:50]])
                st.dataframe(hp_df, use_container_width=True, height=400)
            else:
                st.info("No honeypots detected.")
        with tab_cc:
            st.subheader("👥 Side-by-Side Candidate Comparison")
            st.markdown("Contrast score cards and sub-score breakdowns for two hackathon candidates.")
            col_comp_select1, col_comp_select2 = st.columns(2)
            with col_comp_select1:
                cand_a_id = st.selectbox(
                    "Select Candidate A:",
                    options=[r["candidate_id"] for r in hack_results],
                    index=0,
                    key="comp_hack_a"
                )
            with col_comp_select2:
                default_index = 1 if len(hack_results) > 1 else 0
                cand_b_id = st.selectbox(
                    "Select Candidate B:",
                    options=[r["candidate_id"] for r in hack_results],
                    index=default_index,
                    key="comp_hack_b"
                )
            if cand_a_id == cand_b_id:
                st.warning("💡 Select two different candidates to compare them side-by-side.")
            else:
                c_a = next(r for r in hack_results if r["candidate_id"] == cand_a_id)
                c_b = next(r for r in hack_results if r["candidate_id"] == cand_b_id)
                
                col_gauge1, col_gauge2 = st.columns(2)
                with col_gauge1:
                    st.plotly_chart(gauge_chart(c_a["composite_score"] * 100.0, c_a["candidate_name"]), use_container_width=True)
                with col_gauge2:
                    st.plotly_chart(gauge_chart(c_b["composite_score"] * 100.0, c_b["candidate_name"]), use_container_width=True)
                
                st.markdown("##### Detailed Comparison Matrix")
                comparison_data = {
                    "Metric/Signal": ["Candidate ID", "Current Title", "Experience (Years)", "Skills Match Score", "Career Match Score", "Experience Fit Score", "Education Score", "Behavioral Score", "Overall Composite Score"],
                    c_a["candidate_name"]: [c_a["candidate_id"], c_a["current_title"], f"{c_a['years_experience']:.1f} Yrs", f"{c_a['skill_score']*100:.1f}%", f"{c_a['title_career_score']*100:.1f}%", f"{c_a['experience_score']*100:.1f}%", f"{c_a['education_score']*100:.1f}%", f"{c_a['behavioral_score']*100:.1f}%", f"{c_a['composite_score']*100:.1f}%"],
                    c_b["candidate_name"]: [c_b["candidate_id"], c_b["current_title"], f"{c_b['years_experience']:.1f} Yrs", f"{c_b['skill_score']*100:.1f}%", f"{c_b['title_career_score']*100:.1f}%", f"{c_b['experience_score']*100:.1f}%", f"{c_b['education_score']*100:.1f}%", f"{c_b['behavioral_score']*100:.1f}%", f"{c_b['composite_score']*100:.1f}%"]
                }
                st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)
        with tab_dd:
            st.subheader("🔍 Hackathon Candidate Profiler")
            sel_cand_id = st.selectbox("Select Candidate to Profile:", options=[r["candidate_id"] for r in hack_results])
            sel_r = next(r for r in hack_results if r["candidate_id"] == sel_cand_id)
            sel_cand = sel_r["raw_candidate"]
            
            col_dd1, col_dd2 = st.columns([1, 2])
            with col_dd1:
                st.markdown(f"### {sel_r['candidate_name']}")
                st.markdown(f"🆔 `{sel_r['candidate_id']}`")
                gauge_fig = gauge_chart(sel_r['composite_score'] * 100.0, "Composite Score")
                st.plotly_chart(gauge_fig, use_container_width=True)
            with col_dd2:
                st.markdown("### 📋 Candidate Profile & Signals")
                st.markdown(
                    f"""
                    **Current Title**: `{sel_r['current_title']}` &nbsp;|&nbsp;
                    **Experience**: `{sel_r['years_experience']:.1f} Yrs` &nbsp;|&nbsp;
                    **Company**: `{sel_cand.get('profile', {}).get('current_company', 'Unknown')}`
                    """
                )
                st.markdown("##### ⚙️ Sub-Score Breakdown:")
                breakdown = {
                    "Skills Match": sel_r["skill_score"],
                    "Title & Career": sel_r["title_career_score"],
                    "Experience Fit": sel_r["experience_score"],
                    "Education Fit": sel_r["education_score"],
                    "Behavioral Signals": sel_r["behavioral_score"],
                }
                score_breakdown_bars(breakdown)
        
            st.subheader("🧠 Skills Analysis")
            st.markdown("##### Matched Core Skills:")
            st.markdown(render_skill_tags(sel_r["matched_skills"]), unsafe_allow_html=True)
            if sel_r["missing_core_skills"]:
                st.markdown("##### Missing Core Skills:")
                missing_html = "".join(f'<span class="skill-tag tag-missing">{s.upper()}</span>' for s in sel_r["missing_core_skills"])
                st.markdown(missing_html, unsafe_allow_html=True)
    
            st.subheader("📞 Platform Behavioral Signals")
            sig = sel_cand.get("redrob_signals", {})
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.markdown(f"**Profile Completeness**: {sig.get('profile_completeness_score', 0)}%")
                st.markdown(f"**Open To Work**: {'Yes' if sig.get('open_to_work_flag') else 'No'}")
                st.markdown(f"**Notice Period**: {sig.get('notice_period_days', 0)} Days")
            with col_s2:
                st.markdown(f"**Recruiter Response Rate**: {sig.get('recruiter_response_rate', 0)*100.0:.0f}%")
                st.markdown(f"**Avg Response Time**: {sig.get('avg_response_time_hours', 0):.1f} Hours")
                st.markdown(f"**Interview Completion**: {sig.get('interview_completion_rate', 0)*100.0:.0f}%")
            with col_s3:
                st.markdown(f"**GitHub Activity Score**: {sig.get('github_activity_score', -1)}/100")
                st.markdown(f"**Expected Salary**: {sig.get('expected_salary_range_inr_lpa', {}).get('min', 0)} - {sig.get('expected_salary_range_inr_lpa', {}).get('max', 0)} LPA")
                st.markdown(f"**Verified Contacts**: Email: {sig.get('verified_email')}, Phone: {sig.get('verified_phone')}")

            # Outreach Email Generator
            st.markdown("---")
            st.subheader("✉️ Automated Outreach Assistant")
            with st.expander("Generate Personalized Recruiter Outreach Email", expanded=False):
                skills_str = ", ".join(sel_r["matched_skills"][:3]) if sel_r["matched_skills"] else "matching skills"
                email_template = f"""Subject: Exciting Opportunity: AI/ML Engineer Role at HireScope AI

Hi {sel_r['candidate_name']},

I came across your profile and was impressed by your background as a {sel_r['current_title']} with {sel_r['years_experience']:.1f} years of experience.

Specifically, your expertise in {skills_str} aligns perfectly with the requirements for the position we are recruiting for.

Are you available for a brief 15-minute call this week to discuss?

Best regards,
[Your Name]
Talent Acquisition Team, HireScope AI
"""
                st.code(email_template, language="text")

        with tab_dl:
            csv_path = os.path.join("results", "hackathon_submission.csv")
            if os.path.exists(csv_path):
                with open(csv_path, "r") as f:
                    csv_data = f.read()
                st.download_button("📥 Download submission.csv", csv_data, "submission.csv", "text/csv", use_container_width=True)
                st.code(csv_data[:2000], language="csv")

    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3.5rem 2rem;">
            <div class="rc-name" style="font-size: 2.2rem; font-weight: 800; margin-bottom: 0.5rem;">
                HireScope AI
            </div>
            <div class="rc-label" style="font-size: 0.85rem; letter-spacing: 3px; margin-bottom: 1.2rem;">
                Intelligent Candidate Discovery & Ranking System
            </div>
            <div class="rc-dim" style="max-width: 550px; margin: 0 auto; line-height: 1.8; font-style: normal; font-size: 0.92rem;">
                Select a <span class="status-chip status-info">Resume Source</span> in the sidebar and click
                <span class="status-chip status-pass">🚀 Analyze & Rank</span> to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ── FEATURE SHOWCASE ───────────────────────────────────────────────
        st.markdown('<div class="labeled-divider"><span>Platform Capabilities</span></div>', unsafe_allow_html=True)
        st.markdown("### ⚡ Platform Capabilities")
        
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown("""
            <div class="insight-card">
                <div class="insight-title">🧠 Dual AI Matching</div>
                <div class="text-body">
                    <span class="status-chip status-info">TF-IDF</span> keyword overlap +
                    <span class="status-chip status-info">Sentence Transformer</span> semantic matching for deep concept alignment.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown("""
            <div class="insight-card">
                <div class="insight-title">🍯 Honeypot Detection</div>
                <div class="text-body">
                    <span class="status-chip status-fail">9-Check</span> consistency filter catches
                    fake profiles via temporal, salary, career & endorsement anomalies.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown("""
            <div class="insight-card">
                <div class="insight-title">📊 Multi-Signal Scoring</div>
                <div class="text-body">
                    <span class="rc-label-bold">5-Dimension</span> weighted composite:
                    <span class="status-chip status-info">Skills 35%</span>
                    <span class="status-chip status-info">Title 25%</span>
                    <span class="status-chip status-pass">Exp 15%</span>
                    <span class="status-chip status-warn">Edu 10%</span>
                    <span class="status-chip status-fail">Behavioral 15%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        f4, f5, f6 = st.columns(3)
        with f4:
            st.markdown("""
            <div class="insight-card">
                <div class="insight-title">📄 Smart Resume Parser</div>
                <div class="text-body">
                    Extracts skills from <span class="status-chip status-info">PDF</span> & <span class="status-chip status-info">TXT</span> using
                    <span class="rc-name-sm">500+ skill taxonomy</span> with n-gram matching and alias resolution.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with f5:
            st.markdown("""
            <div class="insight-card">
                <div class="insight-title">💬 AI Explainability</div>
                <div class="text-body">
                    Natural-language reports with <span class="status-chip status-pass">strengths</span>,
                    <span class="status-chip status-fail">gaps</span>,
                    interview questions & automated outreach emails.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with f6:
            st.markdown("""
            <div class="insight-card">
                <div class="insight-title">🏆 100K Scale Ready</div>
                <div class="text-body">
                    Hackathon-optimized pipeline ranks <span class="rc-name-sm">100,000 candidates</span> in under
                    <span class="status-chip status-pass">5 minutes</span> on CPU-only hardware.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ── POWERED BY BADGES ──────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="color: #64748B; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 2.5px; margin-bottom: 0.8rem; font-weight: 700;">Powered By</div>
            <div style="display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap;">
                <span class="skill-tag tag-datascience">Sentence Transformers</span>
                <span class="skill-tag tag-programming">Scikit-Learn TF-IDF</span>
                <span class="skill-tag tag-frameworks">Streamlit</span>
                <span class="skill-tag tag-cloud">Plotly</span>
                <span class="skill-tag tag-tools">NLTK</span>
                <span class="skill-tag tag-devops">pdfplumber</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── CANDIDATE & DATASET EXPLORER ──────────────────────────────────
        st.markdown('<div class="labeled-divider"><span>Data Explorer</span></div>', unsafe_allow_html=True)
        st.subheader("📂 Explore Candidates & Datasets")
        st.markdown('Browse the <span class="kw">candidate pool</span> or <span class="kw">demo resumes</span> before running analysis.', unsafe_allow_html=True)

        explore_source = st.radio(
            "Select Source to Explore:",
            options=["🏆 Hackathon Dataset Preview", "📄 5 Demo Resumes"],
            horizontal=True
        )

        if explore_source == "📄 5 Demo Resumes":
            demo_dir = Path("data/sample_resumes")
            if demo_dir.exists():
                txt_files = sorted(list(demo_dir.glob("*.txt")))
                demo_resumes = {}
                for path in txt_files:
                    name_key = path.stem.replace("resume_", "").title()
                    with open(path, "r", encoding="utf-8") as f:
                        demo_resumes[name_key] = f.read()

                if demo_resumes:
                    col_dm1, col_dm2, col_dm3 = st.columns(3)
                    metric_card("Demo Resumes", str(len(demo_resumes)), col_dm1)
                    metric_card("Format", "Plain Text (.txt)", col_dm2)
                    metric_card("Target Profiles", "Engineers, PM, Designers", col_dm3)

                    st.markdown("<br>", unsafe_allow_html=True)

                    selected_demo = st.selectbox(
                        "Select a Demo Candidate to View:",
                        options=list(demo_resumes.keys())
                    )

                    st.markdown(f"#### 📄 Resume Profile: {selected_demo}")
                    st.code(demo_resumes[selected_demo], language="text")
                else:
                    st.info("No demo resumes found in `data/sample_resumes/`.")
            else:
                st.info("Demo resumes directory not found at `data/sample_resumes/`.")

        elif explore_source == "🏆 Hackathon Dataset Preview":
            dataset_path = os.path.join(os.path.dirname(__file__), "data", "sample_candidates.json")
            if os.path.exists(dataset_path):
                import json
                @st.cache_data
                def load_dataset_preview(path):
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    rows = []
                    for c in data:
                        p = c.get("profile", {})
                        skills_list = [s["name"] for s in c.get("skills", [])]
                        edu = c.get("education", [{}])[0] if c.get("education") else {}
                        sig = c.get("redrob_signals", {})
                        salary = sig.get("expected_salary_range_inr_lpa", {})
                        rows.append({
                            "ID": c.get("candidate_id", ""),
                            "Name": p.get("anonymized_name", "Unknown"),
                            "Headline": p.get("headline", ""),
                            "Title": p.get("current_title", ""),
                            "Company": p.get("current_company", ""),
                            "Experience (Yrs)": p.get("years_of_experience", 0),
                            "Location": p.get("location", ""),
                            "Country": p.get("country", ""),
                            "Industry": p.get("current_industry", ""),
                            "Education": f"{edu.get('degree', '')} {edu.get('field_of_study', '')}".strip(),
                            "Institution": edu.get("institution", ""),
                            "Skills": ", ".join(skills_list[:8]) + (f" (+{len(skills_list)-8})" if len(skills_list) > 8 else ""),
                            "Skill Count": len(skills_list),
                            "Salary (Min LPA)": salary.get("min", 0),
                            "Salary (Max LPA)": salary.get("max", 0),
                            "Open To Work": "Yes" if sig.get("open_to_work_flag") else "No",
                            "Profile Score": sig.get("profile_completeness_score", 0),
                            "GitHub Score": sig.get("github_activity_score", -1),
                            "Notice (Days)": sig.get("notice_period_days", 0),
                        })
                    return pd.DataFrame(rows)

                df_dataset = load_dataset_preview(dataset_path)

                # Summary metrics
                col_ds1, col_ds2, col_ds3, col_ds4 = st.columns(4)
                metric_card("Total Candidates", str(len(df_dataset)), col_ds1)
                metric_card("Avg Experience", f"{df_dataset['Experience (Yrs)'].mean():.1f} Yrs", col_ds2)
                metric_card("Unique Titles", str(df_dataset['Title'].nunique()), col_ds3)
                metric_card("Avg Skill Count", f"{df_dataset['Skill Count'].mean():.1f}", col_ds4)

                st.markdown("<br>", unsafe_allow_html=True)

                # Filters
                tab_table, tab_charts, tab_profile = st.tabs(["📋 Data Table", "📊 Dataset Analytics", "👤 Candidate Profile"])

                with tab_table:
                    st.markdown("##### Filter Candidates")
                    col_f1, col_f2, col_f3 = st.columns(3)

                    with col_f1:
                        title_filter = st.multiselect(
                            "Filter by Title:",
                            options=sorted(df_dataset["Title"].unique()),
                            default=[]
                        )
                    with col_f2:
                        exp_range = st.slider(
                            "Experience Range (Yrs):",
                            min_value=0.0,
                            max_value=float(df_dataset["Experience (Yrs)"].max()),
                            value=(0.0, float(df_dataset["Experience (Yrs)"].max())),
                            step=0.5
                        )
                    with col_f3:
                        country_filter = st.multiselect(
                            "Filter by Country:",
                            options=sorted(df_dataset["Country"].unique()),
                            default=[]
                        )

                    # Apply filters
                    df_filtered = df_dataset.copy()
                    if title_filter:
                        df_filtered = df_filtered[df_filtered["Title"].isin(title_filter)]
                    df_filtered = df_filtered[
                        (df_filtered["Experience (Yrs)"] >= exp_range[0]) &
                        (df_filtered["Experience (Yrs)"] <= exp_range[1])
                    ]
                    if country_filter:
                        df_filtered = df_filtered[df_filtered["Country"].isin(country_filter)]

                    st.markdown(f"**Showing {len(df_filtered)} of {len(df_dataset)} candidates**")
                    st.dataframe(df_filtered, use_container_width=True, height=500)

                with tab_charts:
                    st.markdown("##### Dataset Distribution Insights")
                    col_ch1, col_ch2 = st.columns(2)

                    with col_ch1:
                        st.markdown("**Experience Distribution**")
                        fig_exp = px.histogram(
                            df_dataset, x="Experience (Yrs)", nbins=20,
                            color_discrete_sequence=["#818CF8"]
                        )
                        fig_exp.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=20, r=20, t=10, b=20), height=280,
                            xaxis=dict(gridcolor="rgba(99,102,241,0.06)"),
                            yaxis=dict(gridcolor="rgba(99,102,241,0.06)")
                        )
                        st.plotly_chart(fig_exp, use_container_width=True)

                    with col_ch2:
                        st.markdown("**Top Job Titles**")
                        title_counts = df_dataset["Title"].value_counts().head(10).reset_index()
                        title_counts.columns = ["Title", "Count"]
                        fig_titles = px.bar(
                            title_counts, x="Count", y="Title", orientation="h",
                            color="Count",
                            color_continuous_scale=[[0, "#1E1B4B"], [0.5, "#6366F1"], [1, "#E0E7FF"]]
                        )
                        fig_titles.update_layout(
                            yaxis=dict(autorange="reversed"),
                            coloraxis_showscale=False,
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=20, r=20, t=10, b=20), height=280
                        )
                        st.plotly_chart(fig_titles, use_container_width=True)

                    col_ch3, col_ch4 = st.columns(2)

                    with col_ch3:
                        st.markdown("**Country Distribution**")
                        country_counts = df_dataset["Country"].value_counts().head(8).reset_index()
                        country_counts.columns = ["Country", "Count"]
                        fig_country = px.pie(
                            country_counts, values="Count", names="Country",
                            color_discrete_sequence=["#818CF8", "#6EE7B7", "#C4B5FD", "#FCD34D", "#7DD3FC", "#FCA5A5", "#F9A8D4", "#A5B4FC"]
                        )
                        fig_country.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=20, r=20, t=10, b=20), height=280,
                            legend=dict(font=dict(color="#E2E8F0"))
                        )
                        st.plotly_chart(fig_country, use_container_width=True)

                    with col_ch4:
                        st.markdown("**Skill Count Distribution**")
                        fig_skills_dist = px.histogram(
                            df_dataset, x="Skill Count", nbins=15,
                            color_discrete_sequence=["#6EE7B7"]
                        )
                        fig_skills_dist.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=20, r=20, t=10, b=20), height=280,
                            xaxis=dict(gridcolor="rgba(99,102,241,0.06)"),
                            yaxis=dict(gridcolor="rgba(99,102,241,0.06)")
                        )
                        st.plotly_chart(fig_skills_dist, use_container_width=True)

                with tab_profile:
                    st.markdown("##### Browse Individual Candidate Profiles")
                    sel_idx = st.selectbox(
                        "Select Candidate:",
                        options=df_dataset["ID"].tolist(),
                        format_func=lambda x: f"{x} — {df_dataset[df_dataset['ID']==x]['Name'].values[0]} ({df_dataset[df_dataset['ID']==x]['Title'].values[0]})"
                    )

                    # Load raw data for selected candidate
                    with open(dataset_path, "r", encoding="utf-8") as f:
                        raw_data = json.load(f)
                    sel_cand_raw = next((c for c in raw_data if c["candidate_id"] == sel_idx), None)

                    if sel_cand_raw:
                        p = sel_cand_raw.get("profile", {})
                        col_p1, col_p2 = st.columns([1, 2])

                        with col_p1:
                            st.markdown(f"### {p.get('anonymized_name', 'Unknown')}")
                            st.markdown(f"**{p.get('headline', '')}**")
                            st.markdown(f"📍 {p.get('location', 'N/A')}, {p.get('country', '')}")
                            st.markdown(f"🏢 {p.get('current_company', 'N/A')} • {p.get('current_industry', '')}")
                            st.markdown(f"💼 {p.get('years_of_experience', 0):.1f} Years Experience")
                            st.markdown("---")
                            st.markdown("##### 🎓 Education")
                            for edu in sel_cand_raw.get("education", []):
                                st.markdown(f"**{edu.get('degree', '')} in {edu.get('field_of_study', '')}**")
                                st.markdown(f"_{edu.get('institution', '')}_ ({edu.get('start_year', '')}-{edu.get('end_year', '')})")
                                if edu.get('grade'):
                                    st.markdown(f"Grade: {edu['grade']} | Tier: {edu.get('tier', 'N/A')}")

                        with col_p2:
                            st.markdown("##### 📝 Summary")
                            st.info(p.get("summary", "No summary available."))

                            st.markdown("##### 🧠 Skills")
                            skills_data = sel_cand_raw.get("skills", [])
                            skill_names = [s["name"] for s in skills_data]
                            st.markdown(render_skill_tags(skill_names), unsafe_allow_html=True)

                            if skills_data:
                                skills_df = pd.DataFrame([{
                                    "Skill": s["name"],
                                    "Proficiency": s.get("proficiency", "N/A"),
                                    "Endorsements": s.get("endorsements", 0),
                                    "Duration (Months)": s.get("duration_months", 0)
                                } for s in skills_data])
                                st.dataframe(skills_df, use_container_width=True, height=200)

                            st.markdown("##### 💼 Career History")
                            for job in sel_cand_raw.get("career_history", []):
                                status = "🟢 Current" if job.get("is_current") else "⚪"
                                st.markdown(f"**{status} {job.get('title', '')}** at _{job.get('company', '')}_")
                                st.markdown(f"_{job.get('start_date', '')} → {job.get('end_date', 'Present')}_ ({job.get('duration_months', 0)} months)")
                                with st.expander("View Description", expanded=False):
                                    st.markdown(job.get("description", "No description."))
            else:
                st.info("📂 No dataset file found at `data/sample_candidates.json`.")
