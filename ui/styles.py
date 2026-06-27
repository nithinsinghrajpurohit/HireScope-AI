"""
Custom CSS styles and themes for the HireScope AI dashboard.
"Onyx Gold" Edition — A premium dark theme featuring deep obsidian blacks,
liquid gold gradients, refined glassmorphism, and smooth animations.
"Champagne Gold" Edition — A warm luxury light theme overrides system.
"""

import streamlit as st


def get_custom_css() -> str:
    """Return the custom CSS code for the Onyx Gold premium dark theme with unique animations."""
    return """
    <style>
        /* ── FONTS ───────────────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #F3F4F6;
        }

        /* ── APP BACKGROUND (Onyx Gold Flow) ──────────────────────────────── */
        .stApp {
            background: 
                radial-gradient(circle at 10% 20%, rgba(212, 175, 55, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 80% 80%, rgba(197, 160, 89, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.02) 0%, transparent 60%),
                linear-gradient(135deg, #070709 0%, #111116 50%, #0A0A0E 100%);
            background-size: 200% 200%;
            background-attachment: fixed;
            animation: onyxBackgroundFlow 25s ease infinite;
        }

        @keyframes onyxBackgroundFlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* ── HEADER BANNER ──────────────────────────────────────────────── */
        .header-container {
            background: linear-gradient(135deg, rgba(13, 13, 17, 0.85) 0%, rgba(26, 22, 15, 0.75) 50%, rgba(10, 10, 13, 0.85) 100%);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 24px;
            padding: 3rem 2rem;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow:
                0 25px 50px -12px rgba(0, 0, 0, 0.6),
                0 0 50px rgba(212, 175, 55, 0.08),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(20px);
        }

        .header-container::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 300%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.06), rgba(243, 229, 171, 0.04), transparent);
            animation: gold-sweep 15s infinite linear;
        }

        .header-container::after {
            content: '';
            position: absolute;
            top: -1px; left: 10%; right: 10%;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.7), rgba(243, 229, 171, 0.5), rgba(197, 160, 89, 0.7), transparent);
        }

        @keyframes gold-sweep {
            0%   { transform: translateX(-50%); }
            100% { transform: translateX(50%); }
        }

        .header-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: linear-gradient(135deg, #FFFFFF 0%, #F3E5AB 35%, #D4AF37 70%, #C5A059 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
            filter: drop-shadow(0 2px 10px rgba(212,175,55,0.25));
        }

        .header-subtitle {
            color: #A3A3A3;
            font-size: 1.1rem;
            font-weight: 400;
            max-width: 550px;
            margin: 0.5rem auto 0;
            letter-spacing: 0.1px;
            line-height: 1.6;
        }

        /* ── GLASS CARD ─────────────────────────────────────────────────── */
        .glass-card {
            background: rgba(15, 15, 20, 0.7);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: 24px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 
                0 10px 30px -10px rgba(0, 0, 0, 0.5),
                0 1px 1px rgba(255, 255, 255, 0.05) inset;
            backdrop-filter: blur(20px);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .glass-card:hover {
            transform: translateY(-6px);
            border-color: rgba(212, 175, 55, 0.3);
            box-shadow: 
                0 20px 40px -15px rgba(0, 0, 0, 0.7), 
                0 0 30px rgba(212, 175, 55, 0.12),
                0 1px 1px rgba(255, 255, 255, 0.08) inset;
        }

        /* ── CANDIDATE RANK CARD ────────────────────────────────────────── */
        .candidate-rank-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(15, 15, 20, 0.55);
            border: 1px solid rgba(212, 175, 55, 0.08);
            border-radius: 20px;
            padding: 1.2rem 1.8rem;
            margin-bottom: 0.85rem;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }

        .candidate-rank-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 3px; height: 100%;
            background: transparent;
            transition: all 0.3s ease;
        }

        .candidate-rank-card:hover {
            border-color: rgba(212, 175, 55, 0.3);
            background: rgba(26, 22, 15, 0.5);
            transform: translateY(-3px) scale(1.008);
            box-shadow: 
                0 12px 28px -10px rgba(0, 0, 0, 0.6),
                0 0 20px rgba(212, 175, 55, 0.08);
        }

        .candidate-rank-card:hover::before {
            background: linear-gradient(180deg, #D4AF37, #C5A059);
        }

        /* ── RANK BADGE ─────────────────────────────────────────────────── */
        .rank-badge {
            background: linear-gradient(135deg, #C5A059 0%, #D4AF37 100%);
            color: #000000;
            width: 38px; height: 38px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 0.9rem;
            box-shadow: 0 4px 16px rgba(212, 175, 55, 0.3);
            margin-right: 1rem;
            flex-shrink: 0;
            transition: all 0.3s ease;
        }

        .rank-badge-gold {
            background: linear-gradient(135deg, #FFF5C0 0%, #D4AF37 100%);
            color: #000000;
            box-shadow: 0 4px 20px rgba(212, 175, 55, 0.5);
            animation: badgeGlow 2.5s infinite alternate;
        }

        @keyframes badgeGlow {
            0% { box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3); }
            100% { box-shadow: 0 4px 25px rgba(212, 175, 55, 0.6); }
        }

        .rank-badge-silver {
            background: linear-gradient(135deg, #E2E8F0 0%, #94A3B8 100%);
            color: #111;
            box-shadow: 0 4px 16px rgba(148, 163, 184, 0.3);
        }

        .rank-badge-bronze {
            background: linear-gradient(135deg, #C5A059 0%, #8C6D31 100%);
            color: #fff;
            box-shadow: 0 4px 16px rgba(140, 109, 49, 0.3);
        }

        /* ── SCORE PILL ─────────────────────────────────────────────────── */
        .score-pill {
            background: rgba(212, 175, 55, 0.08);
            color: #F3E5AB;
            border: 1px solid rgba(212, 175, 55, 0.2);
            padding: 0.35rem 0.9rem;
            border-radius: 24px;
            font-weight: 600;
            font-size: 0.85rem;
            letter-spacing: 0.3px;
            position: relative; overflow: hidden;
        }

        .score-pill::after {
            content: '';
            position: absolute;
            top: 0; left: -100%; width: 200%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
            animation: shimmer 3.5s ease infinite;
        }

        /* ── SKILL TAG SYSTEM ───────────────────────────────────────────── */
        .skill-tag {
            display: inline-block;
            padding: 0.22rem 0.65rem;
            margin: 0.2rem;
            border-radius: 8px;
            font-size: 0.72rem;
            font-weight: 600;
            transition: all 0.25s ease;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }

        .skill-tag:hover {
            transform: translateY(-2px) scale(1.03);
            filter: brightness(1.2);
            box-shadow: 0 4px 14px rgba(212, 175, 55, 0.15);
        }

        .tag-programming { background: rgba(212, 175, 55, 0.08); color: #F3E5AB; border: 1px solid rgba(212, 175, 55, 0.2); }
        .tag-frameworks { background: rgba(212, 175, 55, 0.06); color: #C5A059; border: 1px solid rgba(212, 175, 55, 0.15); }
        .tag-datascience { background: rgba(16, 185, 129, 0.08); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.2); }
        .tag-databases { background: rgba(251, 191, 36, 0.08); color: #FCD34D; border: 1px solid rgba(251, 191, 36, 0.2); }
        .tag-cloud { background: rgba(56, 189, 248, 0.08); color: #7DD3FC; border: 1px solid rgba(56, 189, 248, 0.2); }
        .tag-tools { background: rgba(244, 114, 182, 0.08); color: #F9A8D4; border: 1px solid rgba(244, 114, 182, 0.2); }
        .tag-softskills { background: rgba(139, 92, 246, 0.08); color: #C4B5FD; border: 1px solid rgba(139, 92, 246, 0.2); }
        .tag-devops { background: rgba(245, 158, 11, 0.08); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.2); }
        .tag-other { background: rgba(148, 163, 184, 0.08); color: #CBD5E1; border: 1px solid rgba(148, 163, 184, 0.2); }

        /* ── METRIC CARD ────────────────────────────────────────────────── */
        .metric-card {
            background: rgba(15, 15, 20, 0.6);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            border-color: rgba(212, 175, 55, 0.25);
            transform: translateY(-3px);
        }

        .metric-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #FFFFFF 0%, #F3E5AB 50%, #D4AF37 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.25rem;
        }

        .metric-label {
            color: #A3A3A3;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.2px;
        }

        /* ── COMPARE TABLE ──────────────────────────────────────────────── */
        .compare-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 1.5rem 0;
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: 16px;
            overflow: hidden;
            background: rgba(15, 15, 20, 0.4);
        }

        .compare-table th {
            background-color: rgba(26, 22, 15, 0.7) !important;
            color: #F3E5AB !important;
            padding: 1rem 1.2rem;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-align: left;
            border-bottom: 1.5px solid rgba(212, 175, 55, 0.2) !important;
        }

        .compare-table td {
            padding: 1.1rem 1.2rem;
            border-bottom: 1px solid rgba(212, 175, 55, 0.08) !important;
            color: #E5E7EB;
            font-size: 0.88rem;
            background-color: transparent !important;
        }

        .compare-table tr:last-child td {
            border-bottom: none !important;
        }

        .compare-table tr:hover td {
            background-color: rgba(26, 22, 15, 0.3) !important;
        }

        /* ── PIPELINE FUNNEL ────────────────────────────────────────────── */
        .pipeline-stage {
            background: rgba(15, 15, 20, 0.6);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: 16px;
            padding: 1rem 1.2rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        .pipeline-stage:hover {
            border-color: rgba(212, 175, 55, 0.3);
            transform: translateY(-2px);
        }
        .pipeline-stage .stage-number {
            font-size: 2rem; font-weight: 800;
            background: linear-gradient(135deg, #FFFFFF, #F3E5AB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .pipeline-stage .stage-label {
            color: #A3A3A3; font-size: 0.72rem;
            text-transform: uppercase; letter-spacing: 1.4px;
            margin-top: 0.3rem; font-weight: 600;
        }
        .pipeline-arrow {
            color: rgba(212, 175, 55, 0.3);
            font-size: 1.5rem;
            display: flex; align-items: center; justify-content: center;
        }

        /* ── INSIGHT CARD ──────────────────────────────────────────────── */
        .insight-card {
            background: linear-gradient(135deg, rgba(15, 15, 20, 0.7) 0%, rgba(26, 22, 15, 0.5) 100%);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.35s ease;
            backdrop-filter: blur(8px);
        }
        .insight-card:hover {
            border-color: rgba(212, 175, 55, 0.3);
            transform: translateY(-3px);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
        }
        .insight-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #F3E5AB; font-size: 0.95rem;
            font-weight: 700; margin-bottom: 0.5rem;
        }
        .insight-value {
            font-size: 1.75rem; font-weight: 800;
            background: linear-gradient(135deg, #FFFFFF, #F3E5AB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* ── EXECUTIVE SUMMARY ─────────────────────────────────────────── */
        .exec-summary {
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.05) 0%, rgba(15, 15, 20, 0.6) 100%);
            border: 1px solid rgba(212, 175, 55, 0.15);
            border-left: 4px solid #D4AF37;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            backdrop-filter: blur(8px);
        }

        /* ── CUSTOM STREAMLIT COMPONENT OVERRIDES ─────────────────────────── */
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(15, 15, 20, 0.6) !important;
            border: 1px solid rgba(212, 175, 55, 0.1) !important;
            border-radius: 16px !important;
            padding: 6px 12px !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'Space Grotesk', sans-serif !important;
            color: #9CA3AF !important;
            background: transparent !important;
            border: none !important;
            font-weight: 600 !important;
        }
        .stTabs [aria-selected="true"] {
            color: #D4AF37 !important;
            background: rgba(212, 175, 55, 0.08) !important;
            border-radius: 8px !important;
        }

        /* Sidebar container */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #070709 0%, #0F0F14 100%) !important;
            border-right: 1px solid rgba(212, 175, 55, 0.1) !important;
        }

        /* Analyze Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #C5A059 0%, #D4AF37 100%) !important;
            color: #000000 !important;
            border: none !important;
            border-radius: 14px !important;
            padding: 0.65rem 1.8rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 4px 18px rgba(212, 175, 55, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 28px rgba(212, 175, 55, 0.45) !important;
            filter: brightness(1.08) !important;
        }

        /* Selectboxes & Textarea */
        .stSelectbox [data-baseweb="select"] > div {
            background-color: rgba(15, 15, 20, 0.7) !important;
            border-color: rgba(212, 175, 55, 0.12) !important;
            border-radius: 12px !important;
            color: #FFFFFF !important;
        }

        .stTextArea textarea {
            background-color: rgba(15, 15, 20, 0.7) !important;
            border-color: rgba(212, 175, 55, 0.12) !important;
            border-radius: 12px !important;
            color: #FFFFFF !important;
        }

        .stTextArea textarea:focus {
            border-color: rgba(212, 175, 55, 0.35) !important;
            box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.08) !important;
        }

        /* ── ANIMATIONS ────────────────────────────────────────────────── */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(16px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 8px rgba(212,175,55,0.06); }
            50%      { box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 20px rgba(212,175,55,0.12); }
        }
        @keyframes shimmer {
            0%   { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        @keyframes floatUp {
            0%, 100% { transform: translateY(0); }
            50%      { transform: translateY(-5px); }
        }

        .glass-card, .candidate-rank-card, .metric-card {
            animation: fadeInUp 0.5s ease forwards;
        }

        .candidate-rank-card:nth-child(1) { animation-delay: 0s; }
        .candidate-rank-card:nth-child(2) { animation-delay: 0.06s; }
        .candidate-rank-card:nth-child(3) { animation-delay: 0.12s; }
        .candidate-rank-card:nth-child(4) { animation-delay: 0.18s; }
        .candidate-rank-card:nth-child(5) { animation-delay: 0.24s; }

        .metric-card {
            animation: fadeInUp 0.5s ease forwards, pulseGlow 4s ease-in-out infinite;
        }

        .header-title { background-size: 200% auto; animation: shimmer 5s linear infinite; }

        /* ── RESUME CHECKER text classes ────────────────────────────── */
        .rc-name {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 700;
            font-size: 1.1rem;
            color: #F3F4F6;
            letter-spacing: -0.2px;
        }
        .rc-name-sm {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 600;
            font-size: 0.95rem;
            color: #E5E7EB;
        }
        .rc-label {
            color: #8C8C8C;
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        .rc-label-bold {
            color: #D4AF37;
            font-size: 0.85rem;
            font-weight: 700;
        }
        .rc-value {
            color: #E5E7EB;
            font-size: 0.88rem;
            font-weight: 500;
        }
        .rc-dim {
            color: #737373;
            font-size: 0.82rem;
            font-weight: 400;
            font-style: italic;
        }
        .rc-sep {
            color: rgba(212, 175, 55, 0.2);
            margin: 0 0.5rem;
            font-weight: 300;
        }
        .rc-meta {
            font-size: 0.8rem;
            margin-top: 0.2rem;
            display: flex;
            align-items: center;
            gap: 0.2rem;
            flex-wrap: wrap;
        }
        .rc-rank {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 800;
            font-size: 1rem;
            color: #D4AF37;
        }
        .rc-weight {
            color: #525252;
            font-size: 0.72rem;
            font-weight: 500;
        }
        .rc-score-num {
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            font-weight: 600;
            font-size: 0.9rem;
            color: #F3F4F6;
        }

        /* STATUS CHIPS */
        .status-chip {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .status-pass {
            background: rgba(16, 185, 129, 0.12);
            color: #6EE7B7;
            border: 1px solid rgba(16, 185, 129, 0.25);
        }
        .status-warn {
            background: rgba(212, 175, 55, 0.12);
            color: #F3E5AB;
            border: 1px solid rgba(212, 175, 55, 0.25);
        }
        .status-fail {
            background: rgba(239, 68, 68, 0.1);
            color: #EF4444;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
        .status-info {
            background: rgba(212, 175, 55, 0.06);
            color: #C5A059;
            border: 1px solid rgba(212, 175, 55, 0.15);
        }

        /* progress bars */
        .rc-bar-row { margin-bottom: 1rem; }
        .rc-bar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem; }
        .rc-bar-label { font-size: 0.85rem; font-weight: 600; color: #CBD5E1; }
        .rc-bar-score { display: flex; align-items: center; gap: 0.5rem; }
        .rc-bar-track { background: rgba(255, 255, 255, 0.04); height: 6px; border-radius: 3px; overflow: hidden; }
        .rc-bar-fill { height: 100%; border-radius: 3px; transition: width 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94); }

        /* Score Pills Tiers */
        .score-pill.score-high { background: rgba(16, 185, 129, 0.12); color: #6EE7B7; border-color: rgba(16, 185, 129, 0.3); }
        .score-pill.score-mid { background: rgba(212, 175, 55, 0.12); color: #F3E5AB; border-color: rgba(212, 175, 55, 0.25); }
        .score-pill.score-low { background: rgba(239, 68, 68, 0.1); color: #EF4444; border-color: rgba(239, 68, 68, 0.2); }

        .rec-badge { padding: 0.2rem 0.6rem; border-radius: 8px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; }
        .tag-missing { background: rgba(239, 68, 68, 0.08) !important; color: #EF4444 !important; border: 1px solid rgba(239, 68, 68, 0.2) !important; }

        .section-label { color: #D4AF37; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2.5px; margin-bottom: 0.4rem; display: block; }

        .labeled-divider { display: flex; align-items: center; gap: 1rem; margin: 1.5rem 0; }
        .labeled-divider::before, .labeled-divider::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.12), transparent); }
        .labeled-divider span { color: #8C8C8C; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2.5px; white-space: nowrap; }

        .stApp h1 { font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 800 !important; color: #FFFFFF !important; letter-spacing: -0.3px !important; }
        .stApp h2 { font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 1.4rem !important; font-weight: 700 !important; color: #F3E5AB !important; letter-spacing: -0.2px !important; padding-bottom: 0.3rem !important; }
        .stApp h3 { font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 1.1rem !important; font-weight: 600 !important; color: #CBD5E1 !important; }
        .stApp h5 { font-family: 'Plus Jakarta Sans', sans-serif !important; color: #8C8C8C !important; font-size: 0.78rem !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1.5px !important; }

        .stApp strong { color: #FFFFFF; font-weight: 600; }

        /* Legacy Classes */
        .kw { color: #F3E5AB; font-weight: 700; }
        .kw-glow { color: #D4AF37; font-weight: 700; }
        .kw-success { color: #6EE7B7; font-weight: 600; }
        .kw-warn { color: #F3E5AB; font-weight: 600; }
        .kw-danger { color: #EF4444; font-weight: 600; }
        .hl { background: rgba(212,175,55,0.08); color: #F3E5AB; padding: 0.1rem 0.45rem; border-radius: 4px; font-weight: 600; font-size: 0.88em; }
        .hl-emerald { background: rgba(16,185,129,0.08); color: #6EE7B7; padding: 0.1rem 0.45rem; border-radius: 4px; font-weight: 600; font-size: 0.88em; }
        .hl-amber { background: rgba(212,175,55,0.06); color: #C5A059; padding: 0.1rem 0.45rem; border-radius: 4px; font-weight: 600; font-size: 0.88em; }
        .hl-rose { background: rgba(239,68,68,0.08); color: #EF4444; padding: 0.1rem 0.45rem; border-radius: 4px; font-weight: 600; font-size: 0.88em; }
        .hl-violet { background: rgba(139,92,246,0.08); color: #C4B5FD; padding: 0.1rem 0.45rem; border-radius: 4px; font-weight: 600; font-size: 0.88em; }
        .text-muted { color: #8C8C8C; font-size: 0.82rem; }
        .text-secondary { color: #A3A3A3; font-size: 0.88rem; }
        .text-body { color: #E5E7EB; font-size: 0.9rem; line-height: 1.7; }
        .text-bright { color: #FFFFFF; font-weight: 600; }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
    """


def get_theme_detector_js() -> str:
    """Return JavaScript that detects Streamlit's active theme and adds a CSS class to the root."""
    return """
    <script>
    (function() {
        function detectTheme() {
            // Create a dummy element to read Streamlit's native styles
            const dummy = document.createElement('div');
            dummy.className = 'stMarkdown'; 
            dummy.style.display = 'none';
            document.body.appendChild(dummy);
            
            const color = window.getComputedStyle(dummy).color;
            document.body.removeChild(dummy);
            
            const match = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
            if (match) {
                const brightness = (parseInt(match[1]) * 299 + parseInt(match[2]) * 587 + parseInt(match[3]) * 114) / 1000;
                
                if (brightness < 128) {
                    // Dark Text = Light Theme
                    document.documentElement.classList.add('st-light');
                    document.documentElement.classList.remove('st-dark');
                } else {
                    // Light Text = Dark Theme
                    document.documentElement.classList.add('st-dark');
                    document.documentElement.classList.remove('st-light');
                }
            } else {
                if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
                    document.documentElement.classList.add('st-light');
                    document.documentElement.classList.remove('st-dark');
                } else {
                    document.documentElement.classList.add('st-dark');
                    document.documentElement.classList.remove('st-light');
                }
            }
        }
        detectTheme();
        const observer = new MutationObserver(detectTheme);
        const target = document.querySelector('.stApp');
        if (target) observer.observe(target, { attributes: true, attributeFilter: ['style', 'class'] });
        setTimeout(detectTheme, 500);
        setTimeout(detectTheme, 1500);
        setTimeout(detectTheme, 3000);
    })();
    </script>
    """


def get_light_mode_overrides() -> str:
    """Return CSS overrides for light mode using the .st-light class set by JS.
    A prestigious Champagne Gold and warm cream luxury brand design system.
    """
    return """
    <style>
        /* ══════════════════════════════════════════════════════════════════
           LIGHT MODE — Prestige Champagne Gold & Alabaster
           ══════════════════════════════════════════════════════════════════ */

        .st-light, .st-light body, .st-light [class*="css"] {
            color: #1A1A1A !important;
        }

        .st-light .stApp {
            background-color: #FAF8F5 !important;
            background-image: 
                radial-gradient(rgba(184, 144, 71, 0.05) 1.5px, transparent 1.5px), 
                radial-gradient(rgba(184, 144, 71, 0.05) 1.5px, #FAF8F5 1.5px) !important;
            background-size: 26px 26px !important;
            background-position: 0 0, 13px 13px !important;
            background-attachment: fixed !important;
            animation: none !important;
        }

        /* ── Header Container ──────────────────────────────────── */
        .st-light .header-container {
            background: linear-gradient(135deg, #FFFFFF 0%, #FCFAF7 100%) !important;
            border: 1px solid rgba(184, 144, 71, 0.25) !important;
            border-radius: 16px !important;
            box-shadow: 0 10px 30px rgba(184, 144, 71, 0.06) !important;
            padding: 2.8rem 2.2rem !important;
        }
        .st-light .header-container::after {
            display: none !important;
        }
        .st-light .header-title {
            background: linear-gradient(135deg, #1A1A1A 0%, #8C6D31 60%, #B89047 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            filter: none !important;
        }
        .st-light .header-subtitle {
            color: #5A5A5A !important;
            font-size: 1rem !important;
        }

        /* ── Cards & Containers ────────────────────────────────── */
        .st-light .glass-card,
        .st-light .candidate-rank-card,
        .st-light .metric-card,
        .st-light .insight-card {
            background: #FFFFFF !important;
            border: 1px solid rgba(184, 144, 71, 0.15) !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 20px rgba(184, 144, 71, 0.03) !important;
            backdrop-filter: none !important;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }

        .st-light .glass-card:hover,
        .st-light .insight-card:hover {
            transform: translateY(-4px) !important;
            border-color: rgba(184, 144, 71, 0.35) !important;
            box-shadow: 0 12px 28px rgba(184, 144, 71, 0.08) !important;
        }

        .st-light .candidate-rank-card:hover {
            transform: translateY(-2px) !important;
            background: #FDFCFB !important;
            border-color: rgba(184, 144, 71, 0.35) !important;
            box-shadow: 0 8px 20px rgba(184, 144, 71, 0.08) !important;
        }

        .st-light .candidate-rank-card:hover::before {
            background: linear-gradient(180deg, #B89047, #C5A059) !important;
        }

        .st-light .metric-card::after {
            display: none !important;
        }
        .st-light .metric-value {
            background: linear-gradient(135deg, #1A1A1A 0%, #8C6D31 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            font-weight: 800 !important;
        }

        .st-light .text-body { color: #2C2C2C !important; }
        .st-light .text-secondary { color: #4A4A4A !important; }
        .st-light .text-muted { color: #6A6A6A !important; }
        .st-light .text-bright { color: #111111 !important; }
        .st-light .section-label { color: #B89047 !important; font-weight: 700 !important; }
        .st-light strong { color: #1A1A1A !important; font-weight: 600 !important; }

        /* ── Highlights & Highlights Chips ─────────────────────── */
        .st-light .kw {
            background: none !important;
            color: #B89047 !important;
            -webkit-text-fill-color: initial !important;
            font-weight: 700 !important;
        }
        .st-light .kw-glow {
            background: none !important;
            color: #8C6D31 !important;
            -webkit-text-fill-color: initial !important;
            font-weight: 800 !important;
            text-shadow: none !important;
            filter: none !important;
        }
        .st-light .kw-success { color: #2E7D32 !important; text-shadow: none !important; }
        .st-light .kw-warn { color: #B89047 !important; text-shadow: none !important; }
        .st-light .kw-danger { color: #C62828 !important; text-shadow: none !important; }

        .st-light .hl { background: #FAF3E6 !important; color: #8C6D31 !important; border-color: rgba(184, 144, 71, 0.2) !important; }
        .st-light .hl-emerald { background: #E8F5E9 !important; color: #2E7D32 !important; border-color: #C8E6C9 !important; }
        .st-light .hl-amber { background: #FAF3E6 !important; color: #8C6D31 !important; border-color: rgba(184, 144, 71, 0.2) !important; }
        .st-light .hl-rose { background: #FFEBEE !important; color: #C62828 !important; border-color: #FFCDD2 !important; }
        .st-light .hl-violet { background: #FAF3E6 !important; color: #8C6D31 !important; border-color: rgba(184, 144, 71, 0.2) !important; }

        .st-light .score-pill {
            background: #F5F2EB !important;
            color: #2C2C2C !important;
            border-color: rgba(184, 144, 71, 0.25) !important;
        }
        
        /* Score Pill Tiers */
        .st-light .score-pill.score-high { background: #E8F5E9 !important; color: #2E7D32 !important; border-color: #C8E6C9 !important; }
        .st-light .score-pill.score-mid { background: #FAF3E6 !important; color: #8C6D31 !important; border-color: rgba(184, 144, 71, 0.25) !important; }
        .st-light .score-pill.score-low { background: #FFEBEE !important; color: #C62828 !important; border-color: #FFCDD2 !important; }

        /* Skill Tags */
        .st-light .tag-programming { background: rgba(184, 144, 71, 0.08) !important; color: #8C6D31 !important; border-color: rgba(184, 144, 71, 0.2) !important; }
        .st-light .tag-frameworks { background: rgba(184, 144, 71, 0.05) !important; color: #B89047 !important; border-color: rgba(184, 144, 71, 0.15) !important; }
        .st-light .tag-datascience { background: #E8F5E9 !important; color: #2E7D32 !important; border-color: #C8E6C9 !important; }
        .st-light .tag-databases { background: #FFF9E6 !important; color: #B89047 !important; border-color: #FDE68A !important; }
        .st-light .tag-cloud { background: rgba(184, 144, 71, 0.05) !important; color: #B89047 !important; border-color: rgba(184, 144, 71, 0.15) !important; }
        .st-light .tag-tools { background: rgba(184, 144, 71, 0.05) !important; color: #B89047 !important; border-color: rgba(184, 144, 71, 0.15) !important; }
        .st-light .tag-softskills { background: rgba(184, 144, 71, 0.05) !important; color: #B89047 !important; border-color: rgba(184, 144, 71, 0.15) !important; }
        .st-light .tag-devops { background: rgba(184, 144, 71, 0.05) !important; color: #B89047 !important; border-color: rgba(184, 144, 71, 0.15) !important; }
        .st-light .tag-other { background: #FAF8F5 !important; color: #5A5A5A !important; border-color: rgba(184, 144, 71, 0.15) !important; }

        /* Missing tag & rec badge */
        .st-light .tag-missing {
            background: #FFEBEE !important;
            color: #C62828 !important;
            border: 1px solid #FFCDD2 !important;
        }
        .st-light .rec-badge {
            border: 1px solid rgba(184, 144, 71, 0.2) !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        }
        
        .st-light .rec-badge-strong { color: #2E7D32 !important; background: #E8F5E9 !important; border-color: #C8E6C9 !important; }
        .st-light .rec-badge-consider { color: #8C6D31 !important; background: #FAF3E6 !important; border-color: rgba(184, 144, 71, 0.25) !important; }
        .st-light .rec-badge-weak { color: #C62828 !important; background: #FFEBEE !important; border-color: #FFCDD2 !important; }

        /* ── Compare Table ─────────────────────────────────────── */
        .st-light .compare-table {
            border: 1px solid rgba(184, 144, 71, 0.18) !important;
            box-shadow: 0 4px 12px rgba(184, 144, 71, 0.02) !important;
            border-radius: 12px !important;
        }
        .st-light .compare-table th {
            background-color: #FDFCFB !important;
            color: #5A5A5A !important;
            border-bottom: 2px solid rgba(184, 144, 71, 0.2) !important;
            font-weight: 700 !important;
        }
        .st-light .compare-table td {
            background-color: #FFFFFF !important;
            color: #2C2C2C !important;
            border-bottom: 1px solid #F5F2EB !important;
        }
        .st-light .compare-table tr:hover td {
            background-color: #FCFAF7 !important;
        }

        /* ── Pipeline Stages ───────────────────────────────────── */
        .st-light .pipeline-stage {
            background: #FFFFFF !important;
            border: 1px solid rgba(184, 144, 71, 0.15) !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
        }
        .st-light .pipeline-stage .stage-number {
            background: #8C6D31 !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
        }
        .st-light .pipeline-stage .stage-label { color: #5A5A5A !important; }
        .st-light .pipeline-arrow { color: rgba(184, 144, 71, 0.3) !important; }

        /* ── Exec summary ──────────────────────────────────────── */
        .st-light .exec-summary {
            background: #FDFCF9 !important;
            border: 1px solid rgba(184, 144, 71, 0.25) !important;
            border-left: 4px solid #B89047 !important;
        }

        /* ── Labeled divider ──────────────────────────────────── */
        .st-light .labeled-divider::before, .st-light .labeled-divider::after {
            background: rgba(184, 144, 71, 0.15) !important;
        }
        .st-light .labeled-divider span { color: #B89047 !important; }

        /* ── Tabs ──────────────────────────────────────────────── */
        .st-light .stTabs [data-baseweb="tab-list"] {
            background-color: #F5F2EB !important;
            border-radius: 12px !important;
            padding: 4px !important;
            border: 1px solid rgba(184, 144, 71, 0.18) !important;
        }
        .st-light .stTabs [data-baseweb="tab"] {
            color: #5A5A5A !important;
            border-radius: 8px !important;
        }
        .st-light .stTabs [aria-selected="true"] {
            background: #FFFFFF !important;
            color: #8C6D31 !important;
            box-shadow: 0 2px 4px rgba(184, 144, 71, 0.05) !important;
        }

        /* ── Sidebar ──────────────────────────────────────────── */
        .st-light section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid rgba(184, 144, 71, 0.15) !important;
        }
        .st-light section[data-testid="stSidebar"] .stMarkdown h3 { color: #1A1A1A !important; }

        /* ── Inputs ───────────────────────────────────────────── */
        .st-light .stSelectbox [data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            border-color: rgba(184, 144, 71, 0.25) !important;
        }
        .st-light .stTextArea textarea {
            background-color: #FFFFFF !important;
            border-color: rgba(184, 144, 71, 0.25) !important;
            color: #1A1A1A !important;
        }

        /* ── Buttons ──────────────────────────────────────────── */
        .st-light .stButton > button {
            background: linear-gradient(135deg, #C5A059 0%, #D4AF37 100%) !important;
            color: #000000 !important;
            border: none !important;
            box-shadow: 0 3px 12px rgba(184, 144, 71, 0.2) !important;
            border-radius: 12px !important;
        }
        .st-light .stButton > button:hover {
            box-shadow: 0 6px 20px rgba(184, 144, 71, 0.35) !important;
        }

        /* ── Headings ─────────────────────────────────────────── */
        .st-light h1 { color: #1A1A1A !important; }
        .st-light h2 { color: #8C6D31 !important; }
        .st-light h3 { color: #1A1A1A !important; }
        .st-light h5 { color: #B89047 !important; }

        /* ── Scrollbar ────────────────────────────────────────── */
        .st-light ::-webkit-scrollbar-track { background: #FAF8F5 !important; }
        .st-light ::-webkit-scrollbar-thumb { background: rgba(184, 144, 71, 0.2) !important; border-radius: 8px !important; }

        /* Status chips variants */
        .st-light .status-chip.status-pass { background: #E8F5E9 !important; color: #2E7D32 !important; border-color: #C8E6C9 !important; }
        .st-light .status-chip.status-warn { background: #FAF3E6 !important; color: #8C6D31 !important; border-color: rgba(184, 144, 71, 0.2) !important; }
        .st-light .status-chip.status-fail { background: #FFEBEE !important; color: #C62828 !important; border-color: #FFCDD2 !important; }
        .st-light .status-chip.status-info { background: #FAF3E6 !important; color: #8C6D31 !important; border-color: rgba(184, 144, 71, 0.2) !important; }

        /* Resume checker typography */
        .st-light .rc-name { color: #1A1A1A !important; }
        .st-light .rc-name-sm { color: #1A1A1A !important; }
        .st-light .rc-label { color: #5A5A5A !important; }
        .st-light .rc-label-bold { color: #8C6D31 !important; }
        .st-light .rc-value { color: #1A1A1A !important; }
        .st-light .rc-dim { color: #6A6A6A !important; }
        .st-light .rc-sep { color: rgba(184, 144, 71, 0.2) !important; }
        .st-light .rc-rank { color: #B89047 !important; }
        .st-light .rc-weight { color: #6A6A6A !important; }
        .st-light .rc-score-num { color: #1A1A1A !important; }
        .st-light .rc-bar-label { color: #2C2C2C !important; }
        .st-light .rc-bar-track { background: #F5F2EB !important; }

        /* ── Inline style color overrides for hardcoded styles ── */
        .st-light [style*="color: #E0E7FF"],
        .st-light [style*="color: #E2E8F0"],
        .st-light [style*="color: #CBD5E1"],
        .st-light [style*="color: #F1F5F9"] { color: #1A1A1A !important; }
        .st-light [style*="color: #A5B4FC"] { color: #B89047 !important; }
        .st-light [style*="color: #C4B5FD"] { color: #8C6D31 !important; }
        .st-light [style*="color: #94A3B8"] { color: #5A5A5A !important; }
        .st-light [style*="color: #64748B"] { color: #6A6A6A !important; }
        .st-light [style*="color: #6EE7B7"] { color: #2E7D32 !important; }
        .st-light [style*="color: #FCA5A5"] { color: #C62828 !important; }
        .st-light [style*="color: #FCD34D"] { color: #B89047 !important; }
        .st-light [style*="color: #7DD3FC"] { color: #8C6D31 !important; }
    </style>
    """


def apply_theme():
    """Apply the Midnight Aurora styling theme to the current Streamlit app page."""
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    st.markdown(get_theme_detector_js(), unsafe_allow_html=True)
    st.markdown(get_light_mode_overrides(), unsafe_allow_html=True)
