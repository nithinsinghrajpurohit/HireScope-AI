"""
Reusable, visually-stunning Streamlit UI components.
"Minimal Luxe" edition — implements candidate summary cards, skill tag pills,
comparison tables, and other visual building blocks with a premium
gold-accented, Apple-inspired aesthetic.
"""

import streamlit as st
from data.skills_database import get_skill_info
from utils.constants import APP_TITLE, APP_ICON, APP_DESCRIPTION


def header_banner():
    """Render the main application header banner with Minimal Luxe styling and inline SVG logo."""
    # Inline SVG: A scope/crosshair + AI brain icon in gold
    logo_svg = '''
    <svg width="52" height="52" viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 12px; filter: drop-shadow(0 2px 8px rgba(212,165,116,0.35));">
        <!-- Outer ring -->
        <circle cx="26" cy="26" r="23" stroke="url(#gold_grad)" stroke-width="2.5" fill="none" opacity="0.9"/>
        <!-- Inner ring -->
        <circle cx="26" cy="26" r="14" stroke="url(#gold_grad)" stroke-width="1.5" fill="rgba(212,165,116,0.06)" opacity="0.8"/>
        <!-- Crosshair lines -->
        <line x1="26" y1="2" x2="26" y2="12" stroke="#D4A574" stroke-width="2" stroke-linecap="round" opacity="0.7"/>
        <line x1="26" y1="40" x2="26" y2="50" stroke="#D4A574" stroke-width="2" stroke-linecap="round" opacity="0.7"/>
        <line x1="2" y1="26" x2="12" y2="26" stroke="#D4A574" stroke-width="2" stroke-linecap="round" opacity="0.7"/>
        <line x1="40" y1="26" x2="50" y2="26" stroke="#D4A574" stroke-width="2" stroke-linecap="round" opacity="0.7"/>
        <!-- Center dot / AI core -->
        <circle cx="26" cy="26" r="4" fill="url(#gold_grad)"/>
        <!-- Neural dots -->
        <circle cx="20" cy="20" r="1.8" fill="#D4A574" opacity="0.6"/>
        <circle cx="32" cy="20" r="1.8" fill="#D4A574" opacity="0.6"/>
        <circle cx="20" cy="32" r="1.8" fill="#D4A574" opacity="0.6"/>
        <circle cx="32" cy="32" r="1.8" fill="#D4A574" opacity="0.6"/>
        <!-- Neural connections -->
        <line x1="22" y1="22" x2="24" y2="24" stroke="#D4A574" stroke-width="1" opacity="0.4"/>
        <line x1="30" y1="22" x2="28" y2="24" stroke="#D4A574" stroke-width="1" opacity="0.4"/>
        <line x1="22" y1="30" x2="24" y2="28" stroke="#D4A574" stroke-width="1" opacity="0.4"/>
        <line x1="30" y1="30" x2="28" y2="28" stroke="#D4A574" stroke-width="1" opacity="0.4"/>
        <defs>
            <linearGradient id="gold_grad" x1="0" y1="0" x2="52" y2="52">
                <stop offset="0%" stop-color="#F5E6D3"/>
                <stop offset="50%" stop-color="#D4A574"/>
                <stop offset="100%" stop-color="#C49660"/>
            </linearGradient>
        </defs>
    </svg>
    '''
    st.markdown(
        f"""
        <div class="header-container">
            <div class="header-title">{logo_svg}{APP_TITLE}</div>
            <div class="header-subtitle" style="font-family: 'Space Grotesk', sans-serif;">{APP_DESCRIPTION}</div>
            <div style="margin-top: 0.8rem;">
                <span style="background: rgba(168,195,160,0.12); color: #A8C3A0; border: 1px solid rgba(168,195,160,0.3); padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px;">v2.0 — AI-Powered</span>
                <span style="background: rgba(212,165,116,0.1); color: #D4A574; border: 1px solid rgba(212,165,116,0.25); padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px; margin-left: 0.5rem;">Redrob Hackathon</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, column):
    """Render a modern metric card with gold accents inside a streamlit column."""
    with column:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_skill_tag(skill_name: str) -> str:
    """Return the HTML representation of a skill tag, color-coded by category."""
    info = get_skill_info(skill_name)
    category = info.get("category", "Other") if info else "Other"

    # Class mapping based on CSS categories
    class_map = {
        "Programming": "tag-programming",
        "Frameworks": "tag-frameworks",
        "Data Science": "tag-datascience",
        "Databases": "tag-databases",
        "Cloud": "tag-cloud",
        "Tools": "tag-tools",
        "Soft Skills": "tag-softskills",
        "DevOps": "tag-devops",
        "Web Development": "tag-frameworks",
        "Mobile": "tag-other",
        "Other": "tag-other"
    }

    css_class = class_map.get(category, "tag-other")
    display_name = skill_name.title()
    if len(display_name) <= 4:
        display_name = display_name.upper()  # Keep acronyms caps

    return f'<span class="skill-tag {css_class}">{display_name}</span>'


def render_skill_tags(skills: list[str]) -> str:
    """Convert a list of skills into a contiguous string of HTML tags."""
    if not skills:
        return '<span style="color: #A09890; font-size: 0.85rem; font-style: italic;">None detected</span>'
    return "".join(render_skill_tag(s) for s in skills)


def render_candidate_card(rank: int, name: str, score: float, file_name: str, matched: list[str], exp_years: float, rec_text: str = "", rec_style: str = "") -> str:
    """Generate HTML for a candidate rank listing card with luxury styling."""
    # Build list of top 3 skills to display
    skills_slice = matched[:3]
    skills_html = render_skill_tags(skills_slice)
    if len(matched) > 3:
        skills_html += f'<span style="color: #A09890; font-size: 0.8rem; margin-left: 0.3rem;">+{len(matched)-3} more</span>'

    exp_text = f"{exp_years:.1f} yr{'s' if exp_years != 1 else ''}" if exp_years > 0 else "Entry Level"

    # Rank badge styling — gold for #1, silver for #2, bronze for #3
    badge_class = ""
    if rank == 1:
        badge_class = " rank-badge-gold"
    elif rank == 2:
        badge_class = " rank-badge-silver"
    elif rank == 3:
        badge_class = " rank-badge-bronze"

    rec_badge = f'<span style="padding: 0.25rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700; {rec_style}">{rec_text}</span>' if rec_text else ""

    return f"""
    <div class="candidate-rank-card">
        <div style="display: flex; align-items: center;">
            <div class="rank-badge{badge_class}">#{rank}</div>
            <div>
                <div style="font-weight: 600; font-size: 1.1rem; color: #F5E6D3; font-family: 'Playfair Display', Georgia, serif;">{name}</div>
                <div style="font-size: 0.8rem; color: #A09890; margin-top: 0.15rem;">
                    📄 {file_name} • 💼 {exp_text}
                </div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="display: none; @media(min-width: 768px){{ display: block; }}">{skills_html}</div>
            {rec_badge}
            <div class="score-pill">{score:.1f}% Match</div>
        </div>
    </div>
    """


def score_breakdown_bars(score_dict: dict):
    """Render a visual breakdown of scores as elegant progressive bars."""
    labels = {
        "skill_match": "🎯 Skill Overlap Match (40%)",
        "semantic": "🧠 Semantic Context Match (25%)",
        "experience": "💼 Experience Requirement Match (20%)",
        "education": "🎓 Education Level Fit (10%)",
        "bonus": "🎁 Nice-to-have / Bonus Skills (5%)",
    }

    for key, label in labels.items():
        val = score_dict.get(key, 0.0)

        # Luxury palette: emerald-sage for high, warm gold for mid, muted rose for low
        if val >= 70:
            color = "#A8C3A0"       # Sage green
            glow = "rgba(168, 195, 160, 0.3)"
        elif val >= 40:
            color = "#D4A574"       # Gold
            glow = "rgba(212, 165, 116, 0.3)"
        else:
            color = "#D4756A"       # Muted rose
            glow = "rgba(212, 117, 106, 0.3)"

        st.markdown(
            f"""
            <div style="margin-bottom: 0.9rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #A09890; margin-bottom: 0.25rem;">
                    <span>{label}</span>
                    <span style="font-weight: 600; color: #F5E6D3;">{val:.1f}%</span>
                </div>
                <div style="background-color: rgba(255, 255, 255, 0.04); height: 5px; border-radius: 3px; overflow: hidden;">
                    <div style="background: {color}; width: {val}%; height: 100%; border-radius: 3px; box-shadow: 0 0 8px {glow}; transition: width 0.6s ease;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_html_table(html_str: str):
    """Clean leading spaces from each line of HTML to prevent Streamlit from rendering it as a code block."""
    cleaned_html = "\n".join(line.strip() for line in html_str.split("\n"))
    st.markdown(cleaned_html, unsafe_allow_html=True)


def comparison_matrix(ranked_candidates):
    """Render a side-by-side tabular comparison of candidates."""
    if not ranked_candidates:
        return

    table_rows = []
    for rank, c in enumerate(ranked_candidates, start=1):
        matched_str = ", ".join(c.matched_skills[:5])
        if len(c.matched_skills) > 5:
            matched_str += f" (+{len(c.matched_skills)-5})"

        edu = c.resume_data.sections.get("education", "")
        # Extract first non-empty line of education for summary
        edu_line = "Not found"
        if edu:
            lines = [l.strip() for l in edu.split("\n") if l.strip()]
            if lines:
                edu_line = lines[0]
                if len(edu_line) > 35:
                    edu_line = edu_line[:32] + "..."

        table_rows.append(
            f"""
            <tr>
                <td><strong style="color: #D4A574;">#{rank}</strong></td>
                <td><span style="color: #F5E6D3; font-weight: 600; font-family: 'Playfair Display', Georgia, serif;">{c.candidate_name}</span></td>
                <td><span class="score-pill" style="padding: 0.1rem 0.5rem; font-size: 0.8rem;">{c.overall_score:.1f}%</span></td>
                <td>{c.experience_years:.1f} Yrs</td>
                <td>{edu_line}</td>
                <td>{matched_str or '<span style="color:#D4756A">None</span>'}</td>
            </tr>
            """
        )

    rows_html = "".join(table_rows)

    render_html_table(
        f"""
        <table class="compare-table">
            <thead>
                <tr>
                    <th style="width: 8%">Rank</th>
                    <th style="width: 22%">Candidate Name</th>
                    <th style="width: 15%">Overall Score</th>
                    <th style="width: 15%">Experience</th>
                    <th style="width: 20%">Education Level</th>
                    <th style="width: 20%">Top Matched Skills</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """
    )


def compare_two_candidates_matrix(c1, c2):
    """Render a side-by-side comparison table for two candidates."""
    rec_badge1 = f'<span style="padding: 0.25rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700; {c1.recommendation_style}">{c1.recommendation}</span>'
    rec_badge2 = f'<span style="padding: 0.25rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700; {c2.recommendation_style}">{c2.recommendation}</span>'

    # Format skills lists
    matched1_html = render_skill_tags(c1.matched_skills[:12])
    if len(c1.matched_skills) > 12:
        matched1_html += f'<br><small style="color: #A09890;">+{len(c1.matched_skills)-12} more</small>'

    matched2_html = render_skill_tags(c2.matched_skills[:12])
    if len(c2.matched_skills) > 12:
        matched2_html += f'<br><small style="color: #A09890;">+{len(c2.matched_skills)-12} more</small>'

    missing1_html = "".join(f'<span class="skill-tag" style="background: rgba(212, 117, 106, 0.1); color: #D4756A; border: 1px solid rgba(212, 117, 106, 0.3);">{s.upper()}</span>' for s in c1.missing_skills[:8]) if c1.missing_skills else "None"
    if len(c1.missing_skills) > 8:
        missing1_html += f'<br><small style="color: #A09890;">+{len(c1.missing_skills)-8} more</small>'

    missing2_html = "".join(f'<span class="skill-tag" style="background: rgba(212, 117, 106, 0.1); color: #D4756A; border: 1px solid rgba(212, 117, 106, 0.3);">{s.upper()}</span>' for s in c2.missing_skills[:8]) if c2.missing_skills else "None"
    if len(c2.missing_skills) > 8:
        missing2_html += f'<br><small style="color: #A09890;">+{len(c2.missing_skills)-8} more</small>'

    # Format education summary
    def get_edu_line(c):
        edu = c.resume_data.sections.get("education", "")
        if edu:
            lines = [l.strip() for l in edu.split("\n") if l.strip()]
            if lines:
                return lines[0][:50]
        return "Not specified"

    render_html_table(
        f"""
        <table class="compare-table">
            <thead>
                <tr>
                    <th style="width: 30%">Metric / Feature</th>
                    <th style="width: 35%; color: #D4A574; font-size: 0.95rem;">{c1.candidate_name}</th>
                    <th style="width: 35%; color: #C9A88A; font-size: 0.95rem;">{c2.candidate_name}</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Overall Match Score</strong></td>
                    <td><span class="score-pill">{c1.overall_score:.1f}% Match</span></td>
                    <td><span class="score-pill">{c2.overall_score:.1f}% Match</span></td>
                </tr>
                <tr>
                    <td><strong>Recruiter Recommendation</strong></td>
                    <td>{rec_badge1}</td>
                    <td>{rec_badge2}</td>
                </tr>
                <tr>
                    <td><strong>Relevant Experience</strong></td>
                    <td>{c1.experience_years:.1f} Years</td>
                    <td>{c2.experience_years:.1f} Years</td>
                </tr>
                <tr>
                    <td><strong>Education Background</strong></td>
                    <td>{get_edu_line(c1)}</td>
                    <td>{get_edu_line(c2)}</td>
                </tr>
                <tr>
                    <td><strong>Technical Skill Match (40%)</strong></td>
                    <td>{c1.skill_match_score:.1f}%</td>
                    <td>{c2.skill_match_score:.1f}%</td>
                </tr>
                <tr>
                    <td><strong>Semantic Relevance (25%)</strong></td>
                    <td>{c1.semantic_similarity:.1f}%</td>
                    <td>{c2.semantic_similarity:.1f}%</td>
                </tr>
                <tr>
                    <td><strong>Experience Alignment (20%)</strong></td>
                    <td>{c1.experience_score:.1f}%</td>
                    <td>{c2.experience_score:.1f}%</td>
                </tr>
                <tr>
                    <td><strong>Education Level Match (10%)</strong></td>
                    <td>{c1.education_score:.1f}%</td>
                    <td>{c2.education_score:.1f}%</td>
                </tr>
                <tr>
                    <td><strong>Matched Skills</strong></td>
                    <td>{matched1_html}</td>
                    <td>{matched2_html}</td>
                </tr>
                <tr>
                    <td><strong>Missing Required Skills</strong></td>
                    <td>{missing1_html}</td>
                    <td>{missing2_html}</td>
                </tr>
            </tbody>
        </table>
        """
    )
