"""
Custom CSS styles and themes for the HireScope AI dashboard.
"Minimal Luxe" — Apple-inspired minimalism with rich charcoal backgrounds,
gold luxury accents, warm cream typography, and elegant micro-animations.
"""

import streamlit as st


def get_custom_css() -> str:
    """Return the custom CSS code for the Minimal Luxe premium dark theme."""
    return """
    <style>
        /* ── FONTS ───────────────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #E8E0D8;
        }

        /* ── GEOMETRIC GRID BACKGROUND ──────────────────────────────────── */
        .stApp {
            background:
                linear-gradient(rgba(212, 165, 116, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(212, 165, 116, 0.02) 1px, transparent 1px),
                linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #0f0f1a 100%);
            background-size: 60px 60px, 60px 60px, 100% 100%;
        }

        /* ── HEADER BANNER ──────────────────────────────────────────────── */
        .header-container {
            background: linear-gradient(135deg, rgba(26, 26, 46, 0.8) 0%, rgba(30, 25, 40, 0.9) 100%);
            border: 1px solid rgba(212, 165, 116, 0.2);
            border-radius: 20px;
            padding: 3rem 2.5rem;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow:
                0 16px 48px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(212, 165, 116, 0.08);
            position: relative;
            overflow: hidden;
        }

        .header-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: -50%;
            width: 200%;
            height: 100%;
            background: linear-gradient(
                to right,
                transparent,
                rgba(212, 165, 116, 0.04),
                transparent
            );
            transform: skewX(-25deg);
            animation: luxe-shine 10s infinite linear;
        }

        .header-container::after {
            content: '';
            position: absolute;
            top: -1px;
            left: 10%;
            right: 10%;
            height: 1px;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(212, 165, 116, 0.5),
                transparent
            );
        }

        @keyframes luxe-shine {
            0%   { left: -100%; }
            100% { left: 100%; }
        }

        .header-title {
            font-family: 'Playfair Display', Georgia, serif;
            background: linear-gradient(135deg, #F5E6D3 0%, #D4A574 50%, #C49660 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.2rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
            letter-spacing: 1px;
        }

        .header-subtitle {
            color: #A09890;
            font-size: 1.15rem;
            font-weight: 300;
            max-width: 550px;
            margin: 0 auto;
            letter-spacing: 0.3px;
        }

        /* ── GLASS CARD ─────────────────────────────────────────────────── */
        .glass-card {
            background: rgba(26, 26, 46, 0.55);
            border: 1px solid rgba(212, 165, 116, 0.1);
            border-radius: 16px;
            padding: 1.8rem;
            margin-bottom: 1.2rem;
            box-shadow:
                0 4px 24px rgba(0, 0, 0, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }

        .glass-card:hover {
            transform: translateY(-3px);
            border-color: rgba(212, 165, 116, 0.25);
            box-shadow:
                0 12px 40px rgba(0, 0, 0, 0.25),
                0 0 0 1px rgba(212, 165, 116, 0.08),
                inset 0 1px 0 rgba(255, 255, 255, 0.04);
        }

        /* ── CANDIDATE RANK CARD ────────────────────────────────────────── */
        .candidate-rank-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(26, 26, 46, 0.6);
            border: 1px solid rgba(212, 165, 116, 0.08);
            border-radius: 14px;
            padding: 1.1rem 1.6rem;
            margin-bottom: 0.8rem;
            transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }

        .candidate-rank-card:hover {
            border-color: rgba(212, 165, 116, 0.3);
            background: rgba(30, 25, 40, 0.5);
            transform: translateX(4px);
            box-shadow: 0 4px 20px rgba(212, 165, 116, 0.08);
        }

        /* ── RANK BADGE ─────────────────────────────────────────────────── */
        .rank-badge {
            background: linear-gradient(135deg, #D4A574 0%, #C49660 100%);
            color: #1a1a2e;
            width: 34px;
            height: 34px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.9rem;
            box-shadow: 0 2px 12px rgba(212, 165, 116, 0.3);
            margin-right: 1rem;
            flex-shrink: 0;
        }

        .rank-badge-gold {
            background: linear-gradient(135deg, #F5D78E 0%, #D4A574 100%);
            box-shadow: 0 2px 16px rgba(245, 215, 142, 0.35);
        }

        .rank-badge-silver {
            background: linear-gradient(135deg, #C0C0C0 0%, #9A9A9A 100%);
            box-shadow: 0 2px 12px rgba(192, 192, 192, 0.25);
        }

        .rank-badge-bronze {
            background: linear-gradient(135deg, #CD7F32 0%, #A0522D 100%);
            box-shadow: 0 2px 12px rgba(205, 127, 50, 0.25);
        }

        .score-circle-container {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* ── SCORE PILL ─────────────────────────────────────────────────── */
        .score-pill {
            background: rgba(212, 165, 116, 0.1);
            color: #D4A574;
            border: 1px solid rgba(212, 165, 116, 0.3);
            padding: 0.35rem 0.9rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
            letter-spacing: 0.3px;
        }

        /* ── SKILL TAG SYSTEM ───────────────────────────────────────────── */
        .skill-tag {
            display: inline-block;
            padding: 0.25rem 0.7rem;
            margin: 0.2rem 0.2rem;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 500;
            transition: all 0.25s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .skill-tag:hover {
            transform: translateY(-2px);
            filter: brightness(1.15);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        /* Luxury-palette skill categories */
        .tag-programming {
            background: rgba(212, 165, 116, 0.12);
            color: #D4A574;
            border: 1px solid rgba(212, 165, 116, 0.3);
        }
        .tag-frameworks {
            background: rgba(180, 145, 120, 0.12);
            color: #C9A88A;
            border: 1px solid rgba(180, 145, 120, 0.3);
        }
        .tag-datascience {
            background: rgba(168, 195, 160, 0.12);
            color: #A8C3A0;
            border: 1px solid rgba(168, 195, 160, 0.3);
        }
        .tag-databases {
            background: rgba(220, 200, 160, 0.12);
            color: #DCC8A0;
            border: 1px solid rgba(220, 200, 160, 0.3);
        }
        .tag-cloud {
            background: rgba(160, 180, 210, 0.12);
            color: #A0B4D2;
            border: 1px solid rgba(160, 180, 210, 0.3);
        }
        .tag-tools {
            background: rgba(200, 170, 180, 0.12);
            color: #C8AAB4;
            border: 1px solid rgba(200, 170, 180, 0.3);
        }
        .tag-softskills {
            background: rgba(180, 170, 200, 0.12);
            color: #B4AAC8;
            border: 1px solid rgba(180, 170, 200, 0.3);
        }
        .tag-devops {
            background: rgba(210, 180, 150, 0.12);
            color: #D2B496;
            border: 1px solid rgba(210, 180, 150, 0.3);
        }
        .tag-other {
            background: rgba(160, 152, 144, 0.12);
            color: #A09890;
            border: 1px solid rgba(160, 152, 144, 0.3);
        }

        /* ── METRIC CARD ────────────────────────────────────────────────── */
        .metric-card {
            background: rgba(26, 26, 46, 0.5);
            border: 1px solid rgba(212, 165, 116, 0.12);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            transition: all 0.35s ease;
            position: relative;
            overflow: hidden;
        }

        .metric-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(212, 165, 116, 0.4), transparent);
        }

        .metric-card:hover {
            border-color: rgba(212, 165, 116, 0.25);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }

        .metric-value {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #F5E6D3, #D4A574);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.2;
            margin-bottom: 0.3rem;
        }

        .metric-label {
            color: #A09890;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 500;
        }

        /* ── CHECK / CROSS MARKS ────────────────────────────────────────── */
        .match-icon-check {
            color: #A8C3A0;
            font-weight: bold;
            margin-right: 0.5rem;
        }

        .match-icon-cross {
            color: #D4756A;
            font-weight: bold;
            margin-right: 0.5rem;
        }

        /* ── COMPARISON TABLE ───────────────────────────────────────────── */
        .compare-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(212, 165, 116, 0.1);
        }

        .compare-table th {
            background-color: rgba(30, 25, 40, 0.8);
            color: #A09890;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 1px;
            padding: 0.85rem 1rem;
            text-align: left;
            border-bottom: 1px solid rgba(212, 165, 116, 0.1);
        }

        .compare-table td {
            padding: 0.8rem 1rem;
            font-size: 0.875rem;
            border-bottom: 1px solid rgba(212, 165, 116, 0.05);
            background-color: rgba(15, 15, 26, 0.3);
        }

        .compare-table tr:hover td {
            background-color: rgba(212, 165, 116, 0.04);
        }

        /* ── SCROLLBAR ──────────────────────────────────────────────────── */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(15, 15, 26, 0.5);
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(212, 165, 116, 0.2);
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(212, 165, 116, 0.35);
        }

        /* ── TABS ───────────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background-color: rgba(26, 26, 46, 0.5);
            padding: 6px;
            border-radius: 14px;
            border: 1px solid rgba(212, 165, 116, 0.08);
        }

        .stTabs [data-baseweb="tab"] {
            height: 42px;
            border-radius: 10px;
            background-color: transparent;
            border: none;
            color: #A09890;
            font-weight: 500;
            padding: 0 18px;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(212, 165, 116, 0.06);
            color: #E8E0D8;
        }

        .stTabs [aria-selected="true"] {
            background: rgba(212, 165, 116, 0.1) !important;
            color: #D4A574 !important;
            border: 1px solid rgba(212, 165, 116, 0.2) !important;
            font-weight: 600 !important;
        }

        /* Remove default tab underline */
        .stTabs [data-baseweb="tab-highlight-transformer"] {
            display: none;
        }

        /* ── SIDEBAR LUXE STYLING ───────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(20, 18, 30, 0.98) 0%, rgba(26, 26, 46, 0.98) 100%);
            border-right: 1px solid rgba(212, 165, 116, 0.1);
        }

        section[data-testid="stSidebar"] .stMarkdown h3 {
            font-family: 'Playfair Display', Georgia, serif;
            color: #D4A574;
            font-size: 1rem;
            letter-spacing: 0.5px;
        }

        /* ── BUTTONS ────────────────────────────────────────────────────── */
        .stButton > button {
            background: linear-gradient(135deg, #D4A574 0%, #C49660 100%) !important;
            color: #1a1a2e !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.6rem 1.5rem !important;
            letter-spacing: 0.5px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(212, 165, 116, 0.2) !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(212, 165, 116, 0.35) !important;
            filter: brightness(1.05) !important;
        }

        /* ── DOWNLOAD BUTTON ────────────────────────────────────────────── */
        .stDownloadButton > button {
            background: rgba(212, 165, 116, 0.1) !important;
            color: #D4A574 !important;
            border: 1px solid rgba(212, 165, 116, 0.25) !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }

        .stDownloadButton > button:hover {
            background: rgba(212, 165, 116, 0.18) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 16px rgba(212, 165, 116, 0.15) !important;
        }

        /* ── EXPANDER ───────────────────────────────────────────────────── */
        .streamlit-expanderHeader {
            background-color: rgba(26, 26, 46, 0.5) !important;
            border: 1px solid rgba(212, 165, 116, 0.08) !important;
            border-radius: 10px !important;
            color: #E8E0D8 !important;
            font-weight: 500 !important;
        }

        .streamlit-expanderHeader:hover {
            border-color: rgba(212, 165, 116, 0.2) !important;
        }

        /* ── SELECTBOX / INPUT STYLING ──────────────────────────────────── */
        .stSelectbox [data-baseweb="select"] > div {
            background-color: rgba(26, 26, 46, 0.6) !important;
            border-color: rgba(212, 165, 116, 0.15) !important;
            border-radius: 10px !important;
        }

        .stTextArea textarea {
            background-color: rgba(26, 26, 46, 0.6) !important;
            border-color: rgba(212, 165, 116, 0.12) !important;
            border-radius: 10px !important;
            color: #E8E0D8 !important;
        }

        .stTextArea textarea:focus {
            border-color: rgba(212, 165, 116, 0.35) !important;
            box-shadow: 0 0 0 2px rgba(212, 165, 116, 0.08) !important;
        }

        /* ── SUBHEADER STYLING ──────────────────────────────────────────── */
        .stApp h2, .stApp h3 {
            font-family: 'Playfair Display', Georgia, serif !important;
            color: #F5E6D3 !important;
        }

        /* ── INFO / SUCCESS / WARNING BOXES ─────────────────────────────── */
        .stAlert {
            border-radius: 12px !important;
        }

        /* ── RECOMMENDATION BADGES ──────────────────────────────────────── */
        .rec-badge-strong {
            background: rgba(168, 195, 160, 0.15);
            color: #A8C3A0;
            border: 1px solid rgba(168, 195, 160, 0.3);
        }
        .rec-badge-consider {
            background: rgba(220, 200, 160, 0.15);
            color: #DCC8A0;
            border: 1px solid rgba(220, 200, 160, 0.3);
        }
        .rec-badge-weak {
            background: rgba(212, 117, 106, 0.15);
            color: #D4756A;
            border: 1px solid rgba(212, 117, 106, 0.3);
        }

        /* ── ANIMATION KEYFRAMES ────────────────────────────────────────── */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(18px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 8px rgba(212,165,116,0.15), 0 4px 16px rgba(0,0,0,0.15); }
            50% { box-shadow: 0 0 20px rgba(212,165,116,0.3), 0 8px 32px rgba(0,0,0,0.2); }
        }
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        @keyframes floatUp {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-6px); }
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes borderGlow {
            0%, 100% { border-color: rgba(212,165,116,0.1); }
            50% { border-color: rgba(212,165,116,0.35); }
        }
        @keyframes countUp {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes ripple {
            0% { transform: scale(1); opacity: 0.4; }
            100% { transform: scale(2.5); opacity: 0; }
        }

        .glass-card, .candidate-rank-card, .metric-card {
            animation: fadeInUp 0.5s ease forwards;
        }

        /* Staggered animations for cards */
        .candidate-rank-card:nth-child(1) { animation-delay: 0s; }
        .candidate-rank-card:nth-child(2) { animation-delay: 0.08s; }
        .candidate-rank-card:nth-child(3) { animation-delay: 0.16s; }
        .candidate-rank-card:nth-child(4) { animation-delay: 0.24s; }
        .candidate-rank-card:nth-child(5) { animation-delay: 0.32s; }

        /* Pulsing glow on metric cards */
        .metric-card {
            animation: fadeInUp 0.5s ease forwards, pulseGlow 3s ease-in-out infinite;
        }
        .metric-card:nth-child(1) { animation-delay: 0s, 0s; }
        .metric-card:nth-child(2) { animation-delay: 0.1s, 0.5s; }
        .metric-card:nth-child(3) { animation-delay: 0.2s, 1s; }
        .metric-card:nth-child(4) { animation-delay: 0.3s, 1.5s; }

        /* Value counter pop-in */
        .metric-value {
            animation: countUp 0.6s cubic-bezier(0.34,1.56,0.64,1) forwards;
        }

        /* Shimmer effect on header title */
        .header-title {
            background-size: 200% auto;
            animation: shimmer 4s linear infinite;
        }

        /* Floating rank badge for #1 */
        .rank-badge-gold {
            animation: floatUp 2.5s ease-in-out infinite;
        }

        /* Neon hover borders on glass cards */
        .glass-card:hover {
            border-color: rgba(212,165,116,0.4) !important;
            box-shadow:
                0 12px 40px rgba(0,0,0,0.25),
                0 0 20px rgba(212,165,116,0.08),
                inset 0 1px 0 rgba(255,255,255,0.04) !important;
        }

        /* Score pill shimmer */
        .score-pill {
            position: relative;
            overflow: hidden;
        }
        .score-pill::after {
            content: '';
            position: absolute;
            top: 0; left: -100%; width: 200%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
            animation: shimmer 3s ease infinite;
        }

        /* ── FUNNEL / PIPELINE VIZ ─────────────────────────────────────── */
        .pipeline-stage {
            background: rgba(26, 26, 46, 0.55);
            border: 1px solid rgba(212,165,116,0.1);
            border-radius: 12px;
            padding: 1rem 1.2rem;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
        }
        .pipeline-stage:hover {
            border-color: rgba(212,165,116,0.3);
            transform: translateY(-2px);
        }
        .pipeline-stage .stage-number {
            font-size: 2rem; font-weight: 800;
            background: linear-gradient(135deg, #F5E6D3, #D4A574);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .pipeline-stage .stage-label {
            color: #A09890; font-size: 0.75rem;
            text-transform: uppercase; letter-spacing: 1.2px;
            margin-top: 0.3rem;
        }
        .pipeline-arrow {
            color: rgba(212,165,116,0.4);
            font-size: 1.5rem;
            display: flex; align-items: center; justify-content: center;
        }

        /* ── INSIGHT CARD ──────────────────────────────────────────────── */
        .insight-card {
            background: linear-gradient(135deg, rgba(26,26,46,0.7) 0%, rgba(30,25,40,0.8) 100%);
            border: 1px solid rgba(212,165,116,0.12);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.35s ease;
        }
        .insight-card:hover {
            border-color: rgba(212,165,116,0.3);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        }
        .insight-title {
            font-family: 'Playfair Display', Georgia, serif;
            color: #D4A574; font-size: 1rem;
            font-weight: 600; margin-bottom: 0.5rem;
        }
        .insight-value {
            font-size: 1.8rem; font-weight: 700;
            background: linear-gradient(135deg, #F5E6D3, #D4A574);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* ── EXECUTIVE SUMMARY BOX ─────────────────────────────────────── */
        .exec-summary {
            background: linear-gradient(135deg, rgba(168,195,160,0.06) 0%, rgba(26,26,46,0.5) 100%);
            border: 1px solid rgba(168,195,160,0.15);
            border-left: 4px solid #A8C3A0;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }

        /* ── PREFERS REDUCED MOTION ────────────────────────────────────── */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
    """


def apply_theme():
    """Apply the Minimal Luxe styling theme to the current Streamlit app page."""
    st.markdown(get_custom_css(), unsafe_allow_html=True)
