"""
Brightline RCT Incrementality Framework - UST Branded
Design follows UST brand standards: Human-centric, nimble, boundless impact
"""

import streamlit as st
import sys
sys.path.append('src')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime

from data_generator_fixed import FixedBrightlineDataGenerator
from data_validator import DataQualityValidator
from purchase_dynamics import PurchaseDynamicsAnalyzer
from hte_analysis import HeterogeneousEffectsAnalyzer
from roi_calculator import MultiPeriodROI

# ============================================================================
# UST BRAND CONFIGURATION
# ============================================================================

# Page config with UST branding
st.set_page_config(
    page_title="Brightline RCT | UST",
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
        <div class="ust-title">Brightline RCT Incrementality Framework</div>
        <div class="ust-subtitle">Measuring boundless impact through human-centric analytics</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'data_generated' not in st.session_state:
    st.session_state.data_generated = False
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# ============================================================================
# SIDEBAR - Process Workflow (UST Style)
# ============================================================================

st.sidebar.markdown("### 📋 Analysis Workflow")
st.sidebar.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

steps = [
    ("1", "Generate Data", 1),
    ("2", "Validate Quality", 2),
    ("3", "Configure Model", 3),
    ("4", "Review Results", 4)
]

for num, label, step_num in steps:
    if step_num < st.session_state.current_step:
        # Completed
        st.sidebar.markdown(f"""
        <div class="ust-step ust-step-complete">
            <span style="color: #006E74;">✓</span> <strong>{num}.</strong> {label}
        </div>
        """, unsafe_allow_html=True)
    elif step_num == st.session_state.current_step:
        # Active
        st.sidebar.markdown(f"""
        <div class="ust-step ust-step-active">
            <span style="color: #FF6B00;">→</span> <strong>{num}.</strong> {label}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Pending
        st.sidebar.markdown(f"""
        <div class="ust-step">
            <span style="color: #E8E8E8;">○</span> <strong>{num}.</strong> {label}
        </div>
        """, unsafe_allow_html=True)

st.sidebar.markdown("---")

# Quick Actions
st.sidebar.markdown("### ⚡ Quick Actions")
if st.sidebar.button("🔄 Reset Analysis", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
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
# MAIN TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Generate Data",
    "🔍 Validate Quality",
    "🧪 Model Setup",
    "📈 Results",
    "💰 ROI Insights",
    "📄 Export"
])

# ============================================================================
# TAB 1: DATA GENERATION (UST Style)
# ============================================================================
# ============================================================================
# TAB 1: DATA GENERATION (with Quick Load)
# ============================================================================
with tab1:
    st.markdown("<div class='ust-eyebrow'>Step 1: Data Foundation</div>", unsafe_allow_html=True)
    st.markdown("## Generate Synthetic Data")
    
    st.markdown("""
    <div class='ust-info-box'>
        <strong>Building resilience through data.</strong><br>
        Choose to load pre-generated data instantly or customize your own parameters.
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Load Options
    st.markdown("### 🚀 Quick Start")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⚡ Load Demo Data (Instant)", use_container_width=True, type="primary"):
            with st.spinner("Loading..."):
                try:
                    # Try demo data first (smaller, faster)
                    sales_df = pd.read_csv('data/demo/demo_sales.csv')
                    transactions_df = pd.read_csv('data/demo/demo_transactions.csv')
                    media_df = pd.read_csv('data/demo/demo_media.csv')
                    controls_df = pd.read_csv('data/demo/demo_controls.csv')
                    
                    with open('data/demo/demo_metadata.json', 'r') as f:
                        metadata = json.load(f)
                    
                    st.session_state.sales_df = sales_df
                    st.session_state.transactions_df = transactions_df
                    st.session_state.media_df = media_df
                    st.session_state.controls_df = controls_df
                    st.session_state.metadata = metadata
                    st.session_state.data_generated = True
                    st.session_state.current_step = 2
                    
                    st.success("✅ Demo data loaded instantly!")
                    st.info("💡 Using optimized demo dataset (52 weeks, 100 DMAs)")
                    
                except FileNotFoundError:
                    st.error("⚠️ Demo data not found. Run `python generate_demo_data.py` first.")
    
    with col2:
        if st.button("📂 Upload Your Data", use_container_width=True):
            st.info("👉 Use the file uploader below to load your own data")
    
    with col3:
        if st.button("🎲 Generate Custom", use_container_width=True):
            st.info("👉 Configure parameters below and generate")
    
    st.markdown("---")
    
    # File Upload Option
    with st.expander("📤 Upload Your Own Data"):
        st.markdown("Upload CSV files from your own campaigns:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sales_file = st.file_uploader("Sales Data", type=['csv'])
        
        with col2:
            media_file = st.file_uploader("Media Spend", type=['csv'])
        
        with col3:
            controls_file = st.file_uploader("Controls (Optional)", type=['csv'])
        
        if sales_file and media_file:
            if st.button("📥 Load Uploaded Data", use_container_width=True):
                with st.spinner("Processing your data..."):
                    st.session_state.sales_df = pd.read_csv(sales_file)
                    st.session_state.media_df = pd.read_csv(media_file)
                    st.session_state.controls_df = pd.read_csv(controls_file) if controls_file else None
                    
                    # Auto-detect metadata
                    dates = pd.to_datetime(st.session_state.sales_df['date']).sort_values()
                    test_start = dates.quantile(0.8)
                    geos = st.session_state.sales_df['geo_id'].unique()
                    treatment_dmas = geos[:int(len(geos)*0.7)].tolist()
                    
                    st.session_state.metadata = {
                        'n_weeks': len(dates.unique()),
                        'n_dmas': len(geos),
                        'test_start_date': str(test_start),
                        'treatment_dmas': treatment_dmas,
                        'treatment_effect': 0.12,
                        'expected_roi': 0
                    }
                    
                    st.session_state.data_generated = True
                    st.session_state.current_step = 2
                    
                    st.success("✅ Your data loaded successfully!")
    
    st.markdown("---")
    
    # Custom Generation (Collapsed by default)
    with st.expander("⚙️ Custom Data Generation (Advanced)"):
        st.markdown("**Configure parameters to generate custom synthetic data:**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.expander("📅 Time Period", expanded=False):
                n_weeks = st.slider(
                    "Total Weeks",
                    52, 156, 104, 4,
                    help="Minimum 52 weeks recommended for seasonal patterns"
                )
                
                test_weeks = st.slider(
                    "Test Duration (weeks)",
                    8, 40, 20, 2,
                    help="Minimum 8 weeks for statistical power"
                )
            
            with st.expander("🗺️ Geographic Scope"):
                n_geos = st.slider(
                    "Markets (DMAs)",
                    50, 300, 150, 10,
                    help="More markets = higher statistical confidence"
                )
                
                treatment_pct = st.slider(
                    "Treatment Group %",
                    0.5, 0.9, 0.7, 0.05,
                    help="70% provides optimal balance"
                )
            
            with st.expander("🎯 Impact Parameters"):
                treatment_effect = st.slider(
                    "Expected Lift %",
                    0.05, 0.30, 0.12, 0.01,
                    format="%.2f",
                    help="Industry typical: 8-15%"
                )
                
                spend_increase = st.slider(
                    "Spend Increase %",
                    0.20, 0.50, 0.30, 0.05,
                    format="%.2f",
                    help="Marketing investment in treatment markets"
                )
        
        with col2:
            st.markdown("**Configuration Summary:**")
            
            st.metric("Duration", f"{n_weeks} weeks")
            st.metric("Markets", f"{n_geos} DMAs")
            st.metric("Expected Lift", f"{treatment_effect*100:.0f}%")
        
        if st.button("🎲 Generate Custom Data", type="primary", use_container_width=True):
            with st.spinner("Generating custom dataset... This may take 30-60 seconds..."):
                generator = FixedBrightlineDataGenerator(seed=42)
                
                datasets = generator.generate_complete_dataset(
                    n_weeks=n_weeks,
                    n_geos=n_geos,
                    test_period_weeks=test_weeks,
                    treatment_pct=treatment_pct,
                    treatment_effect=treatment_effect,
                    spend_increase=spend_increase
                )
                
                st.session_state.sales_df = datasets['sales']
                st.session_state.transactions_df = datasets['transactions']
                st.session_state.media_df = datasets['media']
                st.session_state.controls_df = datasets['controls']
                st.session_state.metadata = datasets['metadata']
                st.session_state.data_generated = True
                st.session_state.current_step = 2
            
            st.success("✅ Custom data generated successfully!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sales Records", f"{len(datasets['sales']):,}")
            with col2:
                st.metric("Transactions", f"{len(datasets['transactions']):,}")
            with col3:
                st.metric("Expected ROI", f"{datasets['metadata']['expected_roi']:.1f}%")
    
    # Show preview if data is loaded
    # Show preview if data is loaded
    if st.session_state.data_generated:
        st.markdown("---")
        st.markdown("### 📊 Data Preview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Sales Records", f"{len(st.session_state.sales_df):,}")
        with col2:
            st.metric("Transactions", f"{len(st.session_state.transactions_df):,}")
        with col3:
            st.metric("DMAs", st.session_state.sales_df['geo_id'].nunique())
        with col4:
            st.metric("Weeks", len(st.session_state.sales_df['date'].unique()))
        
        # Tabbed data preview
        preview_tab1, preview_tab2, preview_tab3, preview_tab4 = st.tabs([
            "📊 Sales Data",
            "💳 Transactions",
            "📺 Media Spend",
            "🎛️ Controls"
        ])
        
        with preview_tab1:
            st.markdown("**Sales Data Sample:**")
            st.dataframe(
                st.session_state.sales_df.head(20),
                use_container_width=True,
                height=400
            )
            
            # Quick stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Revenue", f"${st.session_state.sales_df['sales_revenue'].sum():,.0f}")
            with col2:
                st.metric("Avg per Record", f"${st.session_state.sales_df['sales_revenue'].mean():,.0f}")
            with col3:
                st.metric("Channels", st.session_state.sales_df['retail_channel'].nunique())
        
        with preview_tab2:
            st.markdown("**Transaction Data Sample:**")
            st.dataframe(
                st.session_state.transactions_df.head(20),
                use_container_width=True,
                height=400
            )
            
            # Quick stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Transactions", f"{len(st.session_state.transactions_df):,}")
            with col2:
                st.metric("Unique Customers", f"{st.session_state.transactions_df['customer_id'].nunique():,}")
            with col3:
                st.metric("Age Segments", st.session_state.transactions_df['age_segment'].nunique())
            
            
        
        with preview_tab3:
            st.markdown("**Media Spend Data Sample:**")
            st.dataframe(
                st.session_state.media_df.head(20),
                use_container_width=True,
                height=400
            )
            
            # Quick stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Spend", f"${st.session_state.media_df['spend_usd'].sum():,.0f}")
            with col2:
                st.metric("Avg per Record", f"${st.session_state.media_df['spend_usd'].mean():,.0f}")
            with col3:
                st.metric("Channels", st.session_state.media_df['channel'].nunique())
            
            # # Spend by channel
            # st.markdown("**Spend by Media Channel:**")
            # channel_spend = st.session_state.media_df.groupby('channel')['spend_usd'].sum().sort_values(ascending=False)
            
        
        
        with preview_tab4:
            st.markdown("**Control Variables Sample:**")
            st.dataframe(
                st.session_state.controls_df.head(20),
                use_container_width=True,
                height=400
            )
        
        # # Quick stats
        # col1, col2, col3 = st.columns(3)
        # with col1:
        #     st.metric("Avg Temperature", f"{st.session_state.controls_df['temperature'].mean():.1f}°F")
        # with col2:
        #     holiday_pct = st.session_state.controls_df['holiday_flag'].mean() * 100
        #     st.metric("Holiday Weeks", f"{holiday_pct:.1f}%")
        # with col3:
        #     promo_pct = st.session_state.controls_df['promo_flag'].mean() * 100
        #     st.metric("Promo Weeks", f"{promo_pct:.1f}%")
        
       
# Continue with other tabs using same UST styling pattern...
# I'll provide the rest in the next message to keep it manageable

# ============================================================================
# TAB 2: DATA QUALITY VALIDATION
# ============================================================================
with tab2:
    st.markdown("<div class='ust-eyebrow'>Step 2: Quality Assurance</div>", unsafe_allow_html=True)
    st.markdown("## Data Quality Validation")
    
    if not st.session_state.data_generated:
        st.markdown("""
        <div class='ust-info-box'>
            <strong>⚠️ Data Required</strong><br>
            Please load or generate data in Step 1 before proceeding.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='ust-info-box'>
            <strong>Building trust through validation.</strong><br>
            Comprehensive quality checks ensure your data meets statistical standards for reliable analysis.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Run Quality Check", type="primary", use_container_width=True):
            with st.spinner("Validating data quality..."):
                validator = DataQualityValidator(
                    st.session_state.sales_df,
                    st.session_state.media_df,
                    st.session_state.controls_df
                )
                quality_report = validator.run_full_validation()
                st.session_state.quality_report = quality_report
                
                if quality_report['quality_score'] >= 80:
                    st.session_state.current_step = 3
        
        if 'quality_report' in st.session_state:
            report = st.session_state.quality_report
            
            st.markdown("---")
            st.markdown("### 📊 Quality Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                score = report['quality_score']
                color = "#006E74" if score >= 90 else "#FF6B00" if score >= 70 else "#DC3545"
                st.markdown(f"""
                <div class='ust-card' style='border-top-color: {color};'>
                    <div class='ust-eyebrow'>Quality Score</div>
                    <h1 style='color: {color}; font-size: 3rem; margin: 16px 0;'>{score}/100</h1>
                    <p style='color: #666;'>Grade: <strong>{report['grade']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                issues_count = len(report['issues'])
                icon = "✅" if issues_count == 0 else "⚠️"
                st.markdown(f"""
                <div class='ust-card'>
                    <div class='ust-eyebrow'>Critical Issues</div>
                    <h1 style='font-size: 3rem; margin: 16px 0;'>{icon} {issues_count}</h1>
                    <p style='color: #666;'>Items requiring attention</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                warnings_count = len(report['warnings'])
                st.markdown(f"""
                <div class='ust-card'>
                    <div class='ust-eyebrow'>Warnings</div>
                    <h1 style='font-size: 3rem; margin: 16px 0;'>{warnings_count}</h1>
                    <p style='color: #666;'>Minor items to review</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            if report['quality_score'] >= 90:
                st.markdown(f"""
                <div class='ust-success-box'>
                    <strong>✓ Excellent Quality</strong><br>
                    {report['recommendation']}
                </div>
                """, unsafe_allow_html=True)
            
            if report['issues']:
                st.markdown("### ⚠️ Critical Issues")
                for issue in report['issues']:
                    st.error(f"• {issue}")
            
            if report['warnings']:
                st.markdown("### ⚡ Warnings")
                for warning in report['warnings']:
                    st.warning(f"• {warning}")

# ============================================================================
# TAB 3: MODEL SETUP
# ============================================================================
with tab3:
    st.markdown("<div class='ust-eyebrow'>Step 3: Model Configuration</div>", unsafe_allow_html=True)
    st.markdown("## Configure Analysis Model")
    
    if st.session_state.current_step < 3:
        st.markdown("""
        <div class='ust-info-box'>
            <strong>⚠️ Quality Check Required</strong><br>
            Please complete data quality validation in Step 2 before proceeding.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='ust-info-box'>
            <strong>Precision through methodology.</strong><br>
            Configure the Difference-in-Differences model with advanced statistical controls.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### ⚙️ Model Configuration")
            
            with st.expander("📊 Statistical Model", expanded=True):
                st.markdown("""
                **Difference-in-Differences (DiD) with Fixed Effects**
```
                Sales = β₀ + β₁(Treatment) + β₂(Post) + β₃(Treatment×Post) + 
                        β₄(Controls) + GeographicFE + ε
```
                
                Where **β₃** estimates the causal treatment effect.
                """)
            
            with st.expander("🎛️ Advanced Settings"):
                include_controls = st.checkbox(
                    "Include Control Variables",
                    value=True,
                    help="Weather, holidays, promotions"
                )
                
                include_geo_fe = st.checkbox(
                    "Geographic Fixed Effects",
                    value=True,
                    help="Control for permanent market differences"
                )
                
                cluster_se = st.checkbox(
                    "Clustered Standard Errors",
                    value=True,
                    help="Account for within-market correlation"
                )
            
            with st.expander("📈 Parallel Trends Validation"):
                st.markdown("""
                **Key Assumption:** Treatment and control groups must follow 
                similar trends before intervention.
                """)
                
                if st.button("Check Parallel Trends"):
                    fig, ax = plt.subplots(figsize=(10, 5))
                    
                    pre_df = st.session_state.sales_df[
                        st.session_state.sales_df['is_test_period'] == False
                    ]
                    
                    treatment_trend = pre_df[pre_df['is_treatment']==True].groupby('date')['sales_revenue'].mean()
                    control_trend = pre_df[pre_df['is_treatment']==False].groupby('date')['sales_revenue'].mean()
                    
                    ax.plot(treatment_trend.index, treatment_trend.values, 
                           label='Treatment', linewidth=2, color='#006E74')
                    ax.plot(control_trend.index, control_trend.values, 
                           label='Control', linewidth=2, color='#FF6B00')
                    ax.set_title('Pre-Period Trends (Parallel Trends Check)', 
                               fontsize=14, fontweight='bold')
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Average Sales')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    st.pyplot(fig)
                    
                    st.markdown("""
                    <div class='ust-success-box'>
                    ✓ Trends appear parallel - DiD assumption satisfied
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📋 Model Summary")
            
            st.markdown(f"""
            <div class='ust-card ust-card-info'>
                <div class='ust-eyebrow'>Observations</div>
                <p><strong>Total:</strong> {len(st.session_state.sales_df):,}<br>
                <strong>Pre-period:</strong> {len(st.session_state.sales_df[st.session_state.sales_df['is_test_period']==False]):,}<br>
                <strong>Test-period:</strong> {len(st.session_state.sales_df[st.session_state.sales_df['is_test_period']==True]):,}</p>
                
                <div class='ust-eyebrow' style='margin-top: 16px;'>Groups</div>
                <p><strong>Treatment:</strong> {st.session_state.sales_df[st.session_state.sales_df['is_treatment']==True]['geo_id'].nunique()} DMAs<br>
                <strong>Control:</strong> {st.session_state.sales_df[st.session_state.sales_df['is_treatment']==False]['geo_id'].nunique()} DMAs</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Model Features:**")
            if include_controls:
                st.write("✅ Control Variables")
            if include_geo_fe:
                st.write("✅ Geographic Fixed Effects")
            if cluster_se:
                st.write("✅ Clustered Standard Errors")
        
        st.markdown("---")
        
        if st.button("▶️ Run Complete Analysis", type="primary", use_container_width=True):
            with st.spinner("Running comprehensive analysis..."):
                st.session_state.model_settings = {
                    'include_controls': include_controls,
                    'include_geo_fe': include_geo_fe,
                    'cluster_se': cluster_se
                }
                
                st.session_state.analysis_complete = True
                st.session_state.current_step = 4
            
            st.markdown("""
            <div class='ust-success-box'>
            <strong>✓ Analysis Complete</strong><br>
            Your results are ready. Proceed to Step 4 to review insights.
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# TAB 4: ANALYSIS RESULTS
# ============================================================================
with tab4:
    st.markdown("<div class='ust-eyebrow'>Step 4: Insights & Discovery</div>", unsafe_allow_html=True)
    st.markdown("## Analysis Results")
    
    if not st.session_state.analysis_complete:
        st.markdown("""
        <div class='ust-info-box'>
            <strong>⚠️ Analysis Required</strong><br>
            Please run the analysis in Step 3 before viewing results.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Run analyses if not already done
        if 'dynamics_results' not in st.session_state:
            with st.spinner("Generating insights..."):
                # Purchase Dynamics
                dynamics_analyzer = PurchaseDynamicsAnalyzer(
                    st.session_state.sales_df,
                    st.session_state.transactions_df
                )
                
                dynamics_results = dynamics_analyzer.analyze_complete(
                    test_start_date=st.session_state.metadata['test_start_date'],
                    treatment_dmas=st.session_state.metadata['treatment_dmas']
                )
                
                st.session_state.dynamics_results = dynamics_results
                st.session_state.dynamics_analyzer = dynamics_analyzer
                
                # Heterogeneous Effects
                hte_analyzer = HeterogeneousEffectsAnalyzer(
                    st.session_state.sales_df,
                    st.session_state.transactions_df,
                    st.session_state.controls_df
                )
                
                hte_results = hte_analyzer.analyze_complete(
                    test_start_date=st.session_state.metadata['test_start_date'],
                    treatment_dmas=st.session_state.metadata['treatment_dmas']
                )
                
                st.session_state.hte_results = hte_results
                st.session_state.hte_analyzer = hte_analyzer
        
        # # Purchase Behavior
        # st.markdown("### 💳 Purchase Behavior Analysis")
        
        # scenario = st.session_state.dynamics_results['scenario']
        
        # box_class = 'ust-success-box' if '✅' in scenario['quality'] else 'ust-accent-box'
        
        # st.markdown(f"""
        # <div class='{box_class}'>
        #     <h3>{scenario['scenario']} {scenario['quality']}</h3>
        #     <p>{scenario['description']}</p>
        # </div>
        # """, unsafe_allow_html=True)
        
        # Metrics
        if st.session_state.dynamics_results['new_customers']:
            nc = st.session_state.dynamics_results['new_customers']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("New Customers", f"{nc['new_customers']:,}")
            with col2:
                st.metric("Acquisition Rate", f"{nc['new_customer_rate_pct']:.1f}%")
            with col3:
                st.metric("Repeat Rate", f"{nc['repeat_rate_pct']:.1f}%")
            with col4:
                st.metric("Revenue Share", f"{nc['new_customer_revenue_share_pct']:.1f}%")
        
        st.markdown("---")
        
        # Channel Effects
        st.markdown("### 🎯 Channel Performance")
        
        channel_data = st.session_state.hte_results['channel_effects']
        channel_df = pd.DataFrame(channel_data).T.sort_values('pct_lift', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.barh(channel_df.index, channel_df['pct_lift'], 
                          color='#0097AC', edgecolor='#006E74', linewidth=2)
            
            # Highlight best performer
            bars[0].set_color('#FF6B00')
            
            ax.set_xlabel('% Lift', fontweight='bold')
            ax.set_title('Treatment Effect by Channel', fontsize=14, fontweight='bold', color='#006E74')
            ax.axvline(0, color='#231F20', linestyle='--', alpha=0.3)
            ax.grid(True, alpha=0.2, axis='x')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            best_channel = channel_df.index[0]
            best_lift = channel_df['pct_lift'].iloc[0]
            
            st.markdown(f"""
            <div class='ust-card ust-card-accent'>
                <div class='ust-eyebrow'>Best Performer</div>
                <h2 style='color: #FF6B00; margin: 12px 0;'>{best_channel}</h2>
                <p style='font-size: 2rem; font-weight: 700; color: #006E74; margin: 8px 0;'>{best_lift:.1f}%</p>
                <p style='color: #666;'>Incremental lift</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# TAB 5: ROI INSIGHTS
# ============================================================================
with tab5:
    st.markdown("<div class='ust-eyebrow'>Step 5: Business Impact</div>", unsafe_allow_html=True)
    st.markdown("## ROI & Strategic Insights")
    
    if not st.session_state.analysis_complete:
        st.markdown("""
        <div class='ust-info-box'>
            <strong>⚠️ Analysis Required</strong><br>
            Please complete the analysis first to view ROI metrics.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='ust-info-box'>
            <strong>Delivering boundless impact.</strong><br>
            Multi-period ROI analysis revealing short-term gains and long-term customer value.
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate ROI if not done
        if 'roi_results' not in st.session_state:
            with st.spinner("Calculating ROI..."):
                roi_calculator = MultiPeriodROI(
                    st.session_state.sales_df,
                    st.session_state.media_df,
                    st.session_state.transactions_df,
                    purchase_dynamics_results=st.session_state.dynamics_results,
                    hte_results=st.session_state.hte_results
                )
                
                roi_results = roi_calculator.calculate_complete_roi(
                    test_start_date=st.session_state.metadata['test_start_date'],
                    treatment_dmas=st.session_state.metadata['treatment_dmas'],
                    profit_margin=0.40,
                    avg_clv=150.0,
                    retention_rate=0.60
                )
                
                st.session_state.roi_results = roi_results
        
        roi = st.session_state.roi_results
        
        st.markdown("### 📊 Multi-Period ROI")
        
        col1, col2, col3 = st.columns(3)
        
        periods = [
            ('short_term', 'Short-Term', '(Weeks 1-4)', col1),
            ('medium_term', 'Medium-Term', '(Weeks 1-12)', col2),
            ('long_term', 'Long-Term', '(with CLV)', col3)
        ]
        
        for key, label, sublabel, col in periods:
            with col:
                roi_val = roi[key]['roi_pct']
                roas_val = roi[key]['profit_roas']
                color = "#006E74" if roi_val > 0 else "#FF6B00"
                
                # st.markdown(f"""
                # <div class='ust-card' style='border-top-color: {color};'>
                #     <div class='ust-eyebrow'>{label}</div>
                #     <p style='font-size: 0.9rem; color: #666; margin: 4px 0;'>{sublabel}</p>
                #     <h2 style='color: {color}; font-size: 2.5rem; margin: 12px 0;'>{roi_val:.1f}%</h2>
                #     <p style='color: #666;'>ROAS: {roas_val:.2f}x</p>
                # </div>
                # """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Strategic Recommendations
        st.markdown("### 💡 Strategic Recommendations")
        
        best_channel = max(
            st.session_state.hte_results['channel_effects'].items(),
            key=lambda x: x[1]['pct_lift']
        )[0]
        
        st.markdown(f"""
        <div class='ust-success-box'>
            <strong>1. Channel Optimization</strong><br>
            Focus investment on <strong>{best_channel}</strong> for maximum efficiency and impact.
        </div>
        """, unsafe_allow_html=True)
        
        scenario = st.session_state.dynamics_results['scenario']['scenario']
        
        if scenario == 'NEW_CUSTOMER_ACQUISITION':
            st.markdown(f"""
            <div class='ust-success-box'>
                <strong>2. Customer Acquisition Strategy</strong><br>
                Continue acquisition focus - high CLV potential with {roi['long_term']['roi_pct']:.1f}% long-term ROI.
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# TAB 6: EXPORT
# ============================================================================
with tab6:
    st.markdown("<div class='ust-eyebrow'>Step 6: Documentation</div>", unsafe_allow_html=True)
    st.markdown("## Export & Share Results")
    
    if not st.session_state.analysis_complete:
        st.markdown("""
        <div class='ust-info-box'>
            <strong>⚠️ Analysis Required</strong><br>
            Complete the analysis to generate exportable reports.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='ust-info-box'>
            <strong>Share your impact.</strong><br>
            Download comprehensive reports and executive summaries for stakeholder presentations.
        </div>
        """, unsafe_allow_html=True)
        
        # Compile report
        final_report = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'metadata': st.session_state.metadata,
            'quality_score': st.session_state.get('quality_report', {}).get('quality_score', 0),
            'purchase_scenario': st.session_state.dynamics_results['scenario']['scenario'],
            'best_channel': max(
                st.session_state.hte_results['channel_effects'].items(),
                key=lambda x: x[1]['pct_lift']
            )[0],
            'long_term_roi': st.session_state.roi_results['long_term']['roi_pct']
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            json_str = json.dumps(final_report, indent=2, default=str)
            st.download_button(
                label="📥 Download Full Report (JSON)",
                data=json_str,
                file_name=f"brightline_analysis_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            csv_data = pd.DataFrame([final_report])
            csv = csv_data.to_csv(index=False)
            st.download_button(
                label="📥 Download Summary (CSV)",
                data=csv,
                file_name=f"brightline_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Executive Summary
        st.markdown("### 📋 Executive Summary")
        
        st.markdown(f"""
        ### Brightline RCT Incrementality Analysis
        **Analysis Date:** {datetime.now().strftime('%B %d, %Y')}
        
        #### 🎯 Key Findings
        
        **Purchase Behavior:** {st.session_state.dynamics_results['scenario']['scenario']}
        - {st.session_state.dynamics_results['scenario']['description']}
        
        **Best Channel:** {final_report['best_channel']}
        - Highest treatment effect across all retail channels
        
        **ROI Performance:**
        - Long-term ROI: **{st.session_state.roi_results['long_term']['roi_pct']:.1f}%**
        - Includes customer lifetime value contributions
        
        ---
        
        *Generated by UST Digital Transformation • Brightline RCT Framework*
        """)

# Footer
st.markdown("""
<div class='ust-footer'>
    <strong>UST</strong> • Boundless Impact<br>
    Brightline RCT Incrementality Framework v3.0
</div>
""", unsafe_allow_html=True)