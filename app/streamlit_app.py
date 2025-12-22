"""
Brightline RCT Incrementality Measurement - Streamlit Dashboard
Interactive web application for running and visualizing DiD analysis
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

from data_generator import BrightlineSyntheticDataGenerator
from data_validator import DataQualityValidator
from analysis_did import SimpleDiDAnalysis

# Page config
st.set_page_config(
    page_title="Brightline RCT Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🎯 Brightline RCT Incrementality Measurement</p>', unsafe_allow_html=True)
st.markdown("### Interactive Difference-in-Differences Analysis")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Configuration")

# Data Source Selection
data_source = st.sidebar.radio(
    "Data Source",
    ["Generate Synthetic Data", "Upload Real Data"],
    help="Choose to generate demo data or upload your own"
)

# Initialize session state
if 'analysis_run' not in st.session_state:
    st.session_state.analysis_run = False

# Synthetic Data Parameters
if data_source == "Generate Synthetic Data":
    st.sidebar.subheader("📊 Data Generation Parameters")
    
    n_weeks = st.sidebar.slider("Number of Weeks", 52, 156, 104)
    n_dmas = st.sidebar.slider("Number of DMAs", 50, 300, 150)
    test_weeks = st.sidebar.slider("Test Period (weeks)", 10, 40, 20)
    treatment_pct = st.sidebar.slider("Treatment %", 0.5, 0.9, 0.7)
    true_effect = st.sidebar.slider("True Effect %", 0.0, 0.30, 0.12, 0.01)
    
    generate_button = st.sidebar.button("🎲 Generate Data", type="primary")
    
    if generate_button:
        with st.spinner("Generating synthetic data..."):
            generator = BrightlineSyntheticDataGenerator(seed=42)
            datasets = generator.generate_complete_dataset(
                n_weeks=n_weeks,
                n_dmas=n_dmas,
                test_period_weeks=test_weeks,
                treatment_pct=treatment_pct,
                true_effect_size=true_effect
            )
            
            st.session_state.sales_df = datasets['sales']
            st.session_state.media_df = datasets['media']
            st.session_state.controls_df = datasets['controls']
            st.session_state.metadata = datasets['metadata']
            st.session_state.data_loaded = True
            
            st.sidebar.success("✅ Data generated!")

else:
    st.sidebar.subheader("📤 Upload Data Files")
    
    sales_file = st.sidebar.file_uploader("Sales Data (CSV)", type=['csv'])
    media_file = st.sidebar.file_uploader("Media Data (CSV)", type=['csv'])
    controls_file = st.sidebar.file_uploader("Controls Data (CSV)", type=['csv'])
    
    if sales_file and media_file:
        st.session_state.sales_df = pd.read_csv(sales_file)
        st.session_state.media_df = pd.read_csv(media_file)
        st.session_state.controls_df = pd.read_csv(controls_file) if controls_file else None
        st.session_state.data_loaded = True
        st.sidebar.success("✅ Data uploaded!")

# Analysis Parameters
if 'data_loaded' in st.session_state and st.session_state.data_loaded:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔬 Analysis Settings")
    
    profit_margin = st.sidebar.slider("Profit Margin %", 0.0, 1.0, 0.40, 0.05)
    
    run_analysis = st.sidebar.button("▶️ Run Analysis", type="primary")

# Main Content
if 'data_loaded' not in st.session_state or not st.session_state.data_loaded:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("""
        ### 👋 Welcome to Brightline RCT Analysis
        
        **Get started by:**
        1. Choose data source in the sidebar
        2. Configure parameters
        3. Generate or upload data
        4. Run analysis
        
        **Features:**
        - 📊 Data quality validation
        - 📈 Difference-in-Differences analysis
        - 💰 ROAS calculation
        - 📉 Interactive visualizations
        """)

else:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Overview", "🔍 Quality Check", "📈 Analysis Results", "📄 Report"])
    
    with tab1:
        st.header("Data Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Sales Records", f"{len(st.session_state.sales_df):,}")
        
        with col2:
            st.metric("Media Records", f"{len(st.session_state.media_df):,}")
        
        with col3:
            st.metric("Geographic Units", st.session_state.sales_df['geo_id'].nunique())
        
        st.subheader("Sales Data Sample")
        st.dataframe(st.session_state.sales_df.head(10))
    
    with tab2:
        st.header("Data Quality Validation")
        
        if st.button("🔍 Run Quality Check"):
            with st.spinner("Validating..."):
                validator = DataQualityValidator(
                    st.session_state.sales_df,
                    st.session_state.media_df,
                    st.session_state.controls_df
                )
                quality_report = validator.run_full_validation()
                st.session_state.quality_report = quality_report
        
        if 'quality_report' in st.session_state:
            report = st.session_state.quality_report
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Quality Score", f"{report['quality_score']}/100")
            
            with col2:
                st.metric("Grade", report['grade'])
            
            with col3:
                st.metric("Issues", len(report['issues']))
            
            if not report['issues'] and not report['warnings']:
                st.success("✅ " + report['recommendation'])
    
    with tab3:
        st.header("Analysis Results")
        
        if run_analysis or st.session_state.analysis_run:
            with st.spinner("Running analysis..."):
                did = SimpleDiDAnalysis(
                    st.session_state.sales_df,
                    st.session_state.media_df,
                    st.session_state.controls_df
                )
                
                if 'metadata' in st.session_state:
                    test_start = st.session_state.metadata['test_start_date']
                    treatment_dmas = st.session_state.metadata['treatment_dmas']
                else:
                    dates = pd.to_datetime(st.session_state.sales_df['date']).sort_values()
                    test_start = dates.quantile(0.8)
                    geos = st.session_state.sales_df['geo_id'].unique()
                    treatment_dmas = geos[:int(len(geos)*0.7)].tolist()
                
                did.prepare_data(test_start, treatment_dmas)
                
                simple_results = did.estimate_effect_simple()
                regression_results = did.estimate_effect_regression()
                roas_results = did.calculate_roas(regression_results)
                
                st.session_state.did = did
                st.session_state.regression_results = regression_results
                st.session_state.roas_results = roas_results
                st.session_state.analysis_run = True
            
            results = st.session_state.regression_results
            roas = st.session_state.roas_results
            
            st.subheader("📊 Key Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Treatment Effect", f"${results['treatment_effect']:,.2f}", 
                         delta=f"{results['pct_lift']:.2f}%")
            
            with col2:
                st.metric("P-value", f"{results['p_value']:.4f}")
            
            with col3:
                incremental_profit = roas['total_incremental_sales'] * profit_margin
                profit_roas = incremental_profit / roas['total_spend']
                st.metric("Profit ROAS", f"{profit_roas:.2f}x")
            
            with col4:
                st.metric("Model R²", f"{results['model'].rsquared:.3f}")
            
            st.subheader("📈 Visualization")
            fig = st.session_state.did.plot_trends(save_path=None)
            st.pyplot(fig)
        
        else:
            st.info("👈 Click 'Run Analysis' in sidebar")
    
    with tab4:
        st.header("📄 Export Report")
        
        if st.session_state.analysis_run:
            results = st.session_state.regression_results
            roas = st.session_state.roas_results
            
            st.markdown(f"""
            **Treatment Effect:** ${results['treatment_effect']:,.2f} ({results['pct_lift']:.2f}% lift)
            
            **P-value:** {results['p_value']:.4f}
            
            **Total Incremental Sales:** ${roas['total_incremental_sales']:,.2f}
            
            **ROAS:** {roas['roas']:.2f}x
            """)
        else:
            st.info("Run analysis first")

st.sidebar.markdown("---")
st.sidebar.markdown("**Brightline RCT Analysis v1.0**")