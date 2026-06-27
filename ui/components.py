"""
Reusable Streamlit UI components for HireScope AI.
"Resume Checker" edition — clean, high-contrast text hierarchy inspired by
professional ATS/resume scanner dashboards. Uses crisp labels, color-coded
status indicators (✅/⚠️/❌), bold section headers, and readable data-first
formatting with clear visual weight differences.
"""

import streamlit as st
from data.skills_database import get_skill_info
from utils.constants import APP_TITLE, APP_ICON, APP_DESCRIPTION


def header_banner():
    """Render the main application header banner with Resume Checker styling."""
    logo_svg = '''
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 14px;">
        <rect x="2" y="2" width="44" height="44" rx="12" stroke="#D4AF37" stroke-width="2.5" fill="rgba(212,175,55,0.06)"/>
        <path d="M16 16h16M16 24h12M16 32h8" stroke="#F3E5AB" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="36" cy="32" r="6" stroke="#D4AF37" stroke-width="2" fill="rgba(212,175,55,0.1)"/>
        <path d="M39 35l3 3" stroke="#D4AF37" stroke-width="2" stroke-linecap="round"/>
    </svg>
    '''
    st.markdown(
        f"""
        <div class="header-container">
            <div class="header-title">{logo_svg}{APP_TITLE}</div>
            <div class="header-subtitle">{APP_DESCRIPTION}</div>
            <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 0.6rem;">
                <span class="status-chip" style="background: rgba(212, 175, 55, 0.12); color: #F3E5AB; border: 1px solid rgba(212, 175, 55, 0.25);">✦ AI-Powered v2.0</span>
                <span class="status-chip" style="background: rgba(197, 160, 89, 0.12); color: #C5A059; border: 1px solid rgba(197, 160, 89, 0.25);">⚡ Redrob Hackathon</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, column):
    """Render a metric card with clear label/value hierarchy."""
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
        display_name = display_name.upper()

    return f'<span class="skill-tag {css_class}">{display_name}</span>'


def render_skill_tags(skills: list[str]) -> str:
    """Convert a list of skills into a contiguous string of HTML tags."""
    if not skills:
        return '<span class="rc-dim">None detected</span>'
    return "".join(render_skill_tag(s) for s in skills)


def render_candidate_card(rank: int, name: str, score: float, file_name: str, matched: list[str], exp_years: float, rec_text: str = "", rec_style: str = "") -> str:
    """Generate HTML for a candidate rank listing card — resume checker style."""
    skills_slice = matched[:3]
    skills_html = render_skill_tags(skills_slice)
    if len(matched) > 3:
        skills_html += f'<span class="rc-dim" style="margin-left: 0.3rem;">+{len(matched)-3} more</span>'

    exp_text = f"{exp_years:.1f} yr{'s' if exp_years != 1 else ''}" if exp_years > 0 else "Entry Level"

    badge_class = ""
    if rank == 1:
        badge_class = " rank-badge-gold"
    elif rank == 2:
        badge_class = " rank-badge-silver"
    elif rank == 3:
        badge_class = " rank-badge-bronze"

    # Score-based status color
    if score >= 75:
        score_class = "score-high"
    elif score >= 50:
        score_class = "score-mid"
    else:
        score_class = "score-low"

    rec_badge = f'<span class="rec-badge" style="{rec_style}">{rec_text}</span>' if rec_text else ""

    return f"""
    <div class="candidate-rank-card">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="rank-badge{badge_class}">#{rank}</div>
            <div>
                <div class="rc-name">{name}</div>
                <div class="rc-meta">
                    <span class="rc-label">File:</span> <span class="rc-value">{file_name}</span>
                    <span class="rc-sep">|</span>
                    <span class="rc-label">Exp:</span> <span class="rc-value">{exp_text}</span>
                </div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.8rem;">
            {skills_html}
            {rec_badge}
            <div class="score-pill {score_class}">{score:.1f}%</div>
        </div>
    </div>
    """


def score_breakdown_bars(score_dict: dict):
    """Render score breakdown with resume-checker-style labeled progress bars."""
    dimensions = [
        ("skill_match",  "Skill Match",    "40%", "🎯"),
        ("semantic",     "Semantic Fit",   "25%", "🧠"),
        ("experience",   "Experience",     "20%", "💼"),
        ("education",    "Education",      "10%", "🎓"),
        ("bonus",        "Bonus Skills",   "5%",  "⭐"),
    ]

    for key, label, weight, icon in dimensions:
        val = score_dict.get(key, 0.0)

        if val >= 70:
            bar_color = "#22C55E"
            status = "PASS"
            status_class = "status-pass"
        elif val >= 40:
            bar_color = "#F59E0B"
            status = "FAIR"
            status_class = "status-warn"
        else:
            bar_color = "#EF4444"
            status = "LOW"
            status_class = "status-fail"

        st.markdown(
            f"""
            <div class="rc-bar-row">
                <div class="rc-bar-header">
                    <span class="rc-bar-label">{icon} {label} <span class="rc-weight">{weight}</span></span>
                    <span class="rc-bar-score">
                        <span class="rc-score-num">{val:.1f}%</span>
                        <span class="status-chip {status_class}" style="font-size: 0.6rem; padding: 0.1rem 0.4rem;">{status}</span>
                    </span>
                </div>
                <div class="rc-bar-track">
                    <div class="rc-bar-fill" style="width: {val}%; background: {bar_color};"></div>
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
    """Render a tabular comparison of candidates — resume checker style."""
    if not ranked_candidates:
        return

    table_rows = []
    for rank, c in enumerate(ranked_candidates, start=1):
        matched_str = ", ".join(c.matched_skills[:5])
        if len(c.matched_skills) > 5:
            matched_str += f" (+{len(c.matched_skills)-5})"

        edu = c.resume_data.sections.get("education", "")
        edu_line = "Not found"
        if edu:
            lines = [l.strip() for l in edu.split("\n") if l.strip()]
            if lines:
                edu_line = lines[0]
                if len(edu_line) > 35:
                    edu_line = edu_line[:32] + "..."

        # Score status
        sc = c.overall_score
        if sc >= 75:
            score_html = f'<span class="status-chip status-pass">{sc:.1f}%</span>'
        elif sc >= 50:
            score_html = f'<span class="status-chip status-warn">{sc:.1f}%</span>'
        else:
            score_html = f'<span class="status-chip status-fail">{sc:.1f}%</span>'

        table_rows.append(
            f"""
            <tr>
                <td><span class="rc-rank">#{rank}</span></td>
                <td><span class="rc-name-sm">{c.candidate_name}</span></td>
                <td>{score_html}</td>
                <td class="rc-value">{c.experience_years:.1f} Yrs</td>
                <td class="rc-dim">{edu_line}</td>
                <td class="rc-dim">{matched_str or '<span class="status-chip status-fail">None</span>'}</td>
            </tr>
            """
        )

    rows_html = "".join(table_rows)

    render_html_table(
        f"""
        <table class="compare-table">
            <thead>
                <tr>
                    <th style="width: 8%">#</th>
                    <th style="width: 22%">Candidate</th>
                    <th style="width: 15%">Score</th>
                    <th style="width: 12%">Experience</th>
                    <th style="width: 23%">Education</th>
                    <th style="width: 20%">Matched Skills</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """
    )


def compare_two_candidates_matrix(c1, c2):
    """Render a side-by-side comparison table — resume checker style."""
    def score_chip(val):
        if val >= 75:
            return f'<span class="status-chip status-pass">{val:.1f}%</span>'
        elif val >= 50:
            return f'<span class="status-chip status-warn">{val:.1f}%</span>'
        else:
            return f'<span class="status-chip status-fail">{val:.1f}%</span>'

    rec_badge1 = f'<span class="rec-badge" style="{c1.recommendation_style}">{c1.recommendation}</span>'
    rec_badge2 = f'<span class="rec-badge" style="{c2.recommendation_style}">{c2.recommendation}</span>'

    matched1_html = render_skill_tags(c1.matched_skills[:12])
    if len(c1.matched_skills) > 12:
        matched1_html += f'<br><span class="rc-dim">+{len(c1.matched_skills)-12} more</span>'

    matched2_html = render_skill_tags(c2.matched_skills[:12])
    if len(c2.matched_skills) > 12:
        matched2_html += f'<br><span class="rc-dim">+{len(c2.matched_skills)-12} more</span>'

    missing1_html = "".join(f'<span class="skill-tag tag-missing">{s.upper()}</span>' for s in c1.missing_skills[:8]) if c1.missing_skills else '<span class="status-chip status-pass">None</span>'
    if len(c1.missing_skills) > 8:
        missing1_html += f'<br><span class="rc-dim">+{len(c1.missing_skills)-8} more</span>'

    missing2_html = "".join(f'<span class="skill-tag tag-missing">{s.upper()}</span>' for s in c2.missing_skills[:8]) if c2.missing_skills else '<span class="status-chip status-pass">None</span>'
    if len(c2.missing_skills) > 8:
        missing2_html += f'<br><span class="rc-dim">+{len(c2.missing_skills)-8} more</span>'

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
                    <th style="width: 30%">Criteria</th>
                    <th style="width: 35%">{c1.candidate_name}</th>
                    <th style="width: 35%">{c2.candidate_name}</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><span class="rc-label-bold">Overall Score</span></td>
                    <td>{score_chip(c1.overall_score)}</td>
                    <td>{score_chip(c2.overall_score)}</td>
                </tr>
                <tr>
                    <td><span class="rc-label-bold">Recommendation</span></td>
                    <td>{rec_badge1}</td>
                    <td>{rec_badge2}</td>
                </tr>
                <tr>
                    <td><span class="rc-label-bold">Experience</span></td>
                    <td class="rc-value">{c1.experience_years:.1f} Years</td>
                    <td class="rc-value">{c2.experience_years:.1f} Years</td>
                </tr>
                <tr>
                    <td><span class="rc-label-bold">Education</span></td>
                    <td class="rc-dim">{get_edu_line(c1)}</td>
                    <td class="rc-dim">{get_edu_line(c2)}</td>
                </tr>
                <tr>
                    <td><span class="rc-label-bold">Skill Match</span> <span class="rc-weight">40%</span></td>
                    <td>{score_chip(c1.skill_match_score)}</td>
                    <td>{score_chip(c2.skill_match_score)}</td>
                </tr>
                <tr>
                    <td><span class="rc-label-bold">Semantic Fit</span> <span class="rc-weight">25%</span></td>
                    <td>{score_chip(c1.semantic_similarity)}</td>
                    <td>{score_chip(c2.semantic_similarity)}</td>
                </tr>
                <tr>
                    <td><span class="rc-label-bold">Experience Fit</span> <span class="rc-weight">20%</span></td>
                    <td>{score_chip(c1.experience_score)}</td>
                    <td>{score_chip(c2.experience_score)}</td>
                </tr>
                <tr>
                    <td><span class="rc-label-bold">Education Fit</span> <span class="rc-weight">10%</span></td>
                    <td>{score_chip(c1.education_score)}</td>
                    <td>{score_chip(c2.education_score)}</td>
                </tr>
                <tr>
                    <td><span class="rc-label-bold">Matched Skills</span></td>
                    <td>{matched1_html}</td>
                    <td>{matched2_html}</td>
                </tr>
                <tr>
                    <td><span class="rc-label-bold">Missing Required Skills</span></td>
                    <td>{missing1_html}</td>
                    <td>{missing2_html}</td>
                </tr>
            </tbody>
        </table>
        """
    )
