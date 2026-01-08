"""
Brightline RCT Incrementality Framework - UST Branded
Design follows UST brand standards: Human-centric, nimble, boundless impact
"""

import streamlit as st
import sys
sys.path.append('src')
sys.path.append('app')

# Import module pages
from module_pages import generate_data, eda, validate_quality, model_setup, results, roi_insights, export

# ============================================================================
# UST BRAND CONFIGURATION
# ============================================================================

# Page config with UST branding
st.set_page_config(
    page_title="RCT App | UST",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# UST Brand Colors & Styles
UST_CSS = """
<style>
    /* Import UST-compatible fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Root Variables - UST Design System */
    :root {
        --ust-teal-dark: #006E74;
        --ust-teal-light: #0097AC;
        --ust-black: #231F20;
        --ust-white: #FFFFFF;
        --ust-orange: #FF6B00;
        --ust-gray-bg: #F4F4F4;
        --ust-gray-light: #E8E8E8;

        --font-primary: 'Inter', 'Aptos', sans-serif;
        --border-radius-card: 8px;
        --shadow-card: 0 4px 20px rgba(0,0,0,0.08);
    }

    /* Global Overrides */
    .main {
        background-color: var(--ust-white);
        font-family: var(--font-primary);
    }

    /* Header Section */
    .ust-header {
        background: linear-gradient(135deg, var(--ust-teal-dark) 0%, var(--ust-teal-light) 100%);
        padding: 40px 0;
        margin: -80px -80px 40px -80px;
        color: var(--ust-white);
        border-bottom: 4px solid var(--ust-orange);
    }

    .ust-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--ust-white);
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }

    .ust-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        color: rgba(255,255,255,0.9);
        letter-spacing: 0.5px;
    }

    .ust-eyebrow {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--ust-orange);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }

    /* Cards & Containers */
    .ust-card {
        background: var(--ust-white);
        border-radius: var(--border-radius-card);
        padding: 24px;
        box-shadow: var(--shadow-card);
        border-top: 4px solid var(--ust-teal-light);
        margin: 16px 0;
        transition: all 0.3s ease;
    }

    .ust-card:hover {
        border-top-color: var(--ust-orange);
        box-shadow: 0 6px 30px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }

    .ust-card-success {
        background: linear-gradient(to right, rgba(0, 110, 116, 0.05), rgba(255, 255, 255, 1));
        border-top-color: var(--ust-teal-dark);
    }

    .ust-card-info {
        background: var(--ust-gray-bg);
        border-top-color: var(--ust-teal-light);
    }

    .ust-card-accent {
        border-top-color: var(--ust-orange);
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: var(--ust-gray-bg);
        border-right: 2px solid var(--ust-gray-light);
    }

    /* Step Progress */
    .ust-step {
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 6px;
        background: var(--ust-white);
        border-left: 4px solid var(--ust-gray-light);
        transition: all 0.2s ease;
    }

    .ust-step-active {
        border-left-color: var(--ust-orange);
        background: linear-gradient(to right, rgba(255, 107, 0, 0.08), var(--ust-white));
        font-weight: 600;
    }

    .ust-step-complete {
        border-left-color: var(--ust-teal-dark);
        opacity: 0.7;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--ust-teal-dark) 0%, var(--ust-teal-light) 100%);
        color: var(--ust-white);
        border: none;
        border-radius: 6px;
        padding: 12px 32px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 110, 116, 0.3);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--ust-teal-light) 0%, var(--ust-orange) 100%);
        box-shadow: 0 4px 16px rgba(255, 107, 0, 0.4);
        transform: translateY(-2px);
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--ust-teal-dark);
        font-weight: 700;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: var(--ust-gray-bg);
        border-radius: 6px;
        font-weight: 600;
        color: var(--ust-teal-dark);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--ust-gray-bg);
        padding: 8px;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: var(--ust-black);
        border-radius: 6px;
        padding: 12px 20px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--ust-teal-dark) 0%, var(--ust-teal-light) 100%);
        color: var(--ust-white);
    }

    /* Info Boxes */
    .ust-info-box {
        background: linear-gradient(to right, rgba(0, 151, 172, 0.08), rgba(255, 255, 255, 0));
        border-left: 4px solid var(--ust-teal-light);
        padding: 20px;
        border-radius: 6px;
        margin: 16px 0;
    }

    .ust-success-box {
        background: linear-gradient(to right, rgba(0, 110, 116, 0.08), rgba(255, 255, 255, 0));
        border-left: 4px solid var(--ust-teal-dark);
        padding: 20px;
        border-radius: 6px;
        margin: 16px 0;
    }

    .ust-accent-box {
        background: linear-gradient(to right, rgba(255, 107, 0, 0.08), rgba(255, 255, 255, 0));
        border-left: 4px solid var(--ust-orange);
        padding: 20px;
        border-radius: 6px;
        margin: 16px 0;
    }

    /* Section Headers */
    h1, h2, h3 {
        color: var(--ust-teal-dark);
        font-weight: 700;
        letter-spacing: -0.3px;
    }

    /* Links */
    a {
        color: var(--ust-teal-light);
        text-decoration: none;
        border-bottom: 2px solid transparent;
        transition: border-color 0.2s ease;
    }

    a:hover {
        color: var(--ust-orange);
        border-bottom-color: var(--ust-orange);
    }

    /* Dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(to right, var(--ust-teal-light), transparent);
        margin: 32px 0;
    }

    /* Footer */
    .ust-footer {
        text-align: center;
        padding: 32px;
        color: rgba(35, 31, 32, 0.6);
        font-size: 0.85rem;
        border-top: 2px solid var(--ust-gray-light);
        margin-top: 48px;
    }
</style>
"""

st.markdown(UST_CSS, unsafe_allow_html=True)

# ============================================================================
# HEADER - UST Branded
# ============================================================================

st.markdown("""
<div class="ust-header">
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 40px;">
        <div class="ust-eyebrow">Digital Transformation • Data Analytics</div>
        <div class="ust-title">RCT Incrementality Framework</div>
        <div class="ust-subtitle">Measuring boundless impact through human-centric analytics</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'data_generated' not in st.session_state:
    st.session_state.data_generated = False
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Data Load"

# ============================================================================
# SIDEBAR - Navigation & Workflow
# ============================================================================

st.sidebar.markdown("### 🎯 Navigation")
st.sidebar.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Page navigation
page_options = [
    "📊 Data Load",
    "🔬 Explore Data (EDA)",
    "🔍 Validate Quality",
    "🧪 Model Setup",
    "📈 Results",
    "💰 ROI Insights",
    "📄 Export"
]

selected_page = st.sidebar.radio(
    "Select Module:",
    page_options,
    index=page_options.index(st.session_state.current_page) if st.session_state.current_page in page_options else 0,
    label_visibility="collapsed"
)

# Update session state
st.session_state.current_page = selected_page

# st.sidebar.markdown("---")

# # Workflow Progress
# st.sidebar.markdown("### 📋 Analysis Workflow")
# st.sidebar.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# steps = [
#     ("1", "Generate Data", 1),
#     ("2", "Validate Quality", 2),
#     ("3", "Configure Model", 3),
#     ("4", "Review Results", 4)
# ]

# for num, label, step_num in steps:
#     if step_num < st.session_state.current_step:
#         # Completed
#         st.sidebar.markdown(f"""
#         <div class="ust-step ust-step-complete">
#             <span style="color: #006E74;">✓</span> <strong>{num}.</strong> {label}
#         </div>
#         """, unsafe_allow_html=True)
#     elif step_num == st.session_state.current_step:
#         # Active
#         st.sidebar.markdown(f"""
#         <div class="ust-step ust-step-active">
#             <span style="color: #FF6B00;">→</span> <strong>{num}.</strong> {label}
#         </div>
#         """, unsafe_allow_html=True)
#     else:
#         # Pending
#         st.sidebar.markdown(f"""
#         <div class="ust-step">
#             <span style="color: #E8E8E8;">○</span> <strong>{num}.</strong> {label}
#         </div>
#         """, unsafe_allow_html=True)

st.sidebar.markdown("---")

# Quick Actions
st.sidebar.markdown("### ⚡ Quick Actions")
if st.sidebar.button("🔄 Reset Analysis", use_container_width=True):
    for key in list(st.session_state.keys()):
        if key != 'current_page':  # Preserve current page
            del st.session_state[key]
    st.session_state.current_step = 1
    st.session_state.data_generated = False
    st.session_state.analysis_complete = False
    st.rerun()

st.sidebar.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

# UST Branding
st.sidebar.markdown("""
<div style='text-align: center; padding: 20px 0; border-top: 2px solid #E8E8E8;'>
    <div style='color: #006E74; font-weight: 700; font-size: 1.2rem; margin-bottom: 4px;'>UST</div>
    <div style='color: #0097AC; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;'>Boundless Impact</div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN PANEL - Render Selected Module
# ============================================================================

# Route to appropriate module based on selection
if selected_page == "📊 Data Load":
    generate_data.render()
elif selected_page == "🔬 Explore Data (EDA)":
    eda.render()
elif selected_page == "🔍 Validate Quality":
    validate_quality.render()
elif selected_page == "🧪 Model Setup":
    model_setup.render()
elif selected_page == "📈 Results":
    results.render()
elif selected_page == "💰 ROI Insights":
    roi_insights.render()
elif selected_page == "📄 Export":
    export.render()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div class='ust-footer'>
    <strong>UST</strong> • Boundless Impact<br>
    RCT Incrementality Framework v3.0
</div>
""", unsafe_allow_html=True)
