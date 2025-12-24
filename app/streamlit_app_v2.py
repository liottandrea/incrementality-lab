"""
Brightline Enhanced RCT Analysis - Streamlit Dashboard v2
Includes: Multi-channel, Age segmentation, Purchase dynamics, HTE, Multi-period ROI
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

from data_generator import EnhancedBrightlineDataGenerator
from data_validator import DataQualityValidator
from purchase_dynamics import PurchaseDynamicsAnalyzer
from hte_analysis import HeterogeneousEffectsAnalyzer
from roi_calculator import MultiPeriodROI

# Page config
st.set_page_config(
    page_title="Brightline Enhanced RCT Analysis",
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
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🎯 Brightline Enhanced RCT Analysis</p>', unsafe_allow_html=True)
st.markdown("### Multi-Channel Incrementality Measurement with Advanced Analytics")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Configuration")

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'analysis_run' not in st.session_state:
    st.session_state.analysis_run = False

# Data Generation Parameters
st.sidebar.subheader("📊 Data Generation")

n_weeks = st.sidebar.slider("Number of Weeks", 52, 156, 104)
n_geos = st.sidebar.slider("Number of DMAs", 50, 300, 150)
test_weeks = st.sidebar.slider("Test Period (weeks)", 10, 40, 20)
treatment_pct = st.sidebar.slider("Treatment %", 0.5, 0.9, 0.7)
price_effect = st.sidebar.slider("Price Promo Effect %", 0.0, 0.30, 0.15, 0.01)
visibility_effect = st.sidebar.slider("Visibility Promo Effect %", 0.0, 0.20, 0.08, 0.01)

generate_button = st.sidebar.button("🎲 Generate Data", type="primary")

if generate_button:
    with st.spinner("Generating enhanced synthetic data..."):
        generator = EnhancedBrightlineDataGenerator(seed=42)
        datasets = generator.generate_complete_dataset(
            n_weeks=n_weeks,
            n_geos=n_geos,
            test_period_weeks=test_weeks,
            treatment_pct=treatment_pct,
            price_effect_size=price_effect,
            visibility_effect_size=visibility_effect
        )
        
        st.session_state.sales_df = datasets['sales']
        st.session_state.transactions_df = datasets['transactions']
        st.session_state.media_df = datasets['media']
        st.session_state.controls_df = datasets['controls']
        st.session_state.metadata = datasets['metadata']
        st.session_state.data_loaded = True
        
        st.sidebar.success("✅ Data generated!")

# Analysis Parameters
if st.session_state.data_loaded:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔬 Analysis Settings")
    
    profit_margin = st.sidebar.slider("Profit Margin %", 0.0, 1.0, 0.40, 0.05)
    avg_clv = st.sidebar.number_input("Avg Customer CLV ($)", 50, 500, 150, 10)
    retention_rate = st.sidebar.slider("Retention Rate", 0.0, 1.0, 0.60, 0.05)
    
    run_analysis = st.sidebar.button("▶️ Run Complete Analysis", type="primary")

# Main Content
if not st.session_state.data_loaded:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("""
        ### 👋 Welcome to Enhanced Brightline RCT Analysis
        
        **New Capabilities:**
        - 🏪 Multi-channel analysis (Store, Omnichannel, Online)
        - 👥 Age-based segmentation
        - 💰 Price vs Visibility promotion comparison
        - 📈 Purchase dynamics (Stockpiling detection)
        - 🎯 Heterogeneous treatment effects
        - 💵 Multi-period ROI with CLV
        
        **Get started:**
        1. Configure parameters in sidebar
        2. Generate synthetic data
        3. Run complete analysis
        4. Explore results across tabs
        """)

else:
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Data Overview",
        "🔍 Quality Check",
        "💰 Purchase Dynamics",
        "🎯 Heterogeneous Effects",
        "💵 Multi-Period ROI",
        "📊 Visualizations",
        "📄 Report"
    ])
    
    # TAB 1: Data Overview
    with tab1:
        st.header("Data Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Sales Records", f"{len(st.session_state.sales_df):,}")
        
        with col2:
            st.metric("Transaction Records", f"{len(st.session_state.transactions_df):,}")
        
        with col3:
            st.metric("Geographic Units", st.session_state.sales_df['geo_id'].nunique())
        
        with col4:
            total_revenue = st.session_state.sales_df['sales_revenue'].sum()
            st.metric("Total Revenue", f"${total_revenue:,.0f}")
        
        # Channel breakdown
        st.subheader("Sales by Retail Channel")
        channel_sales = st.session_state.sales_df.groupby('retail_channel')['sales_revenue'].sum().sort_values(ascending=False)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig, ax = plt.subplots(figsize=(10, 4))
            channel_sales.plot(kind='bar', ax=ax, color='steelblue', edgecolor='black')
            ax.set_title('Revenue by Channel', fontsize=14, fontweight='bold')
            ax.set_ylabel('Revenue ($)')
            ax.set_xlabel('Channel')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.dataframe(channel_sales.reset_index().rename(columns={
                'retail_channel': 'Channel',
                'sales_revenue': 'Revenue'
            }), use_container_width=True)
        
        # Age distribution (if available)
        if not st.session_state.transactions_df.empty:
            st.subheader("Customer Age Distribution")
            age_dist = st.session_state.transactions_df['age_segment'].value_counts()
            
            fig, ax = plt.subplots(figsize=(10, 4))
            age_dist.plot(kind='bar', ax=ax, color='coral', edgecolor='black')
            ax.set_title('Transactions by Age Segment', fontsize=14, fontweight='bold')
            ax.set_ylabel('Count')
            ax.set_xlabel('Age Segment')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    # TAB 2: Quality Check
    with tab2:
        st.header("Data Quality Validation")
        
        if st.button("🔍 Run Quality Check"):
            with st.spinner("Validating data quality..."):
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
                st.markdown('<div class="success-box">✅ ' + report['recommendation'] + '</div>', unsafe_allow_html=True)
            else:
                if report['issues']:
                    st.error("**Critical Issues:**")
                    for issue in report['issues']:
                        st.write(f"- {issue}")
                
                if report['warnings']:
                    st.warning("**Warnings:**")
                    for warning in report['warnings']:
                        st.write(f"- {warning}")
    
    # TAB 3: Purchase Dynamics
    with tab3:
        st.header("Purchase Dynamics Analysis")
        
        if run_analysis or st.session_state.analysis_run:
            if 'dynamics_results' not in st.session_state:
                with st.spinner("Analyzing purchase dynamics..."):
                    analyzer = PurchaseDynamicsAnalyzer(
                        st.session_state.sales_df,
                        st.session_state.transactions_df
                    )
                    
                    dynamics_results = analyzer.analyze_complete(
                        test_start_date=st.session_state.metadata['test_start_date'],
                        treatment_dmas=st.session_state.metadata['treatment_dmas']
                    )
                    
                    st.session_state.dynamics_results = dynamics_results
                    st.session_state.dynamics_analyzer = analyzer
            
            results = st.session_state.dynamics_results
            
            # Scenario classification
            scenario = results['scenario']
            
            if scenario['quality'] == '✅ Excellent':
                box_class = 'success-box'
            elif scenario['quality'] == '⚠️ Fair':
                box_class = 'warning-box'
            else:
                box_class = 'warning-box'
            
            st.markdown(f"""
            <div class="{box_class}">
                <h3>{scenario['scenario']} {scenario['quality']}</h3>
                <p>{scenario['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            
            # Stockpiling metrics
            if 'stockpiling' in results:
                stock = results['stockpiling']['Treatment']
                with col1:
                    st.metric(
                        "During-Period Lift",
                        f"{stock['during_lift_pct']:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Post-Period Change",
                        f"{stock['post_change_pct']:.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "Stockpiling Ratio",
                        f"{stock['stockpiling_ratio']:.2f}"
                    )
            
            # New customer metrics
            if results['new_customers']:
                st.subheader("New Customer Acquisition")
                nc = results['new_customers']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("New Customers", f"{nc['new_customers']:,}")
                
                with col2:
                    st.metric("New Customer Rate", f"{nc['new_customer_rate_pct']:.1f}%")
                
                with col3:
                    st.metric("Repeat Rate", f"{nc['repeat_rate_pct']:.1f}%")
                
                with col4:
                    st.metric("Revenue Share", f"{nc['new_customer_revenue_share_pct']:.1f}%")
            
            # Plot
            if 'dynamics_analyzer' in st.session_state:
                st.subheader("Purchase Dynamics Over Time")
                fig = st.session_state.dynamics_analyzer.plot_dynamics(
                    st.session_state.metadata['test_start_date'],
                    save_path=None
                )
                st.pyplot(fig)
        
        else:
            st.info("👈 Click 'Run Complete Analysis' in sidebar")
    
    # TAB 4: Heterogeneous Effects
    with tab4:
        st.header("Heterogeneous Treatment Effects")
        
        if run_analysis or st.session_state.analysis_run:
            if 'hte_results' not in st.session_state:
                with st.spinner("Analyzing heterogeneous effects..."):
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
            
            results = st.session_state.hte_results
            
            # Channel effects
            st.subheader("Effects by Retail Channel")
            channel_df = pd.DataFrame(results['channel_effects']).T
            channel_df = channel_df.sort_values('pct_lift', ascending=False)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.barh(channel_df.index, channel_df['pct_lift'], color='steelblue', edgecolor='black')
                ax.set_xlabel('% Lift')
                ax.set_title('Treatment Effect by Channel', fontsize=12, fontweight='bold')
                ax.axvline(0, color='red', linestyle='--', alpha=0.5)
                plt.tight_layout()
                st.pyplot(fig)
            
            with col2:
                st.dataframe(channel_df[['pct_lift', 'treatment_effect']], use_container_width=True)
            
            # Age effects (if available)
            if results['age_effects']:
                st.subheader("Effects by Age Segment")
                age_df = pd.DataFrame(results['age_effects']).T
                age_df = age_df.sort_values('pct_lift', ascending=False)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.barh(age_df.index, age_df['pct_lift'], color='coral', edgecolor='black')
                    ax.set_xlabel('% Lift')
                    ax.set_title('Treatment Effect by Age', fontsize=12, fontweight='bold')
                    ax.axvline(0, color='red', linestyle='--', alpha=0.5)
                    plt.tight_layout()
                    st.pyplot(fig)
                
                with col2:
                    st.dataframe(age_df[['pct_lift']], use_container_width=True)
            
            # Recommendations
            with st.expander("💡 Strategic Recommendations"):
                st.session_state.hte_analyzer.generate_recommendations(results)
        
        else:
            st.info("👈 Click 'Run Complete Analysis' in sidebar")
    
    # TAB 5: Multi-Period ROI
    with tab5:
        st.header("Multi-Period ROI Analysis")
        
        if run_analysis or st.session_state.analysis_run:
            if 'roi_results' not in st.session_state:
                with st.spinner("Calculating multi-period ROI..."):
                    dynamics = st.session_state.get('dynamics_results')
                    hte = st.session_state.get('hte_results')
                    
                    roi_calc = MultiPeriodROI(
                        st.session_state.sales_df,
                        st.session_state.media_df,
                        st.session_state.transactions_df,
                        purchase_dynamics_results=dynamics,
                        hte_results=hte
                    )
                    
                    roi_results = roi_calc.calculate_complete_roi(
                        test_start_date=st.session_state.metadata['test_start_date'],
                        treatment_dmas=st.session_state.metadata['treatment_dmas'],
                        profit_margin=profit_margin,
                        avg_clv=avg_clv,
                        retention_rate=retention_rate
                    )
                    
                    st.session_state.roi_results = roi_results
                    st.session_state.analysis_run = True
            
            results = st.session_state.roi_results
            
            # ROI Summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Short-term ROI",
                    f"{results['short_term']['roi_pct']:.1f}%",
                    delta=f"ROAS: {results['short_term']['profit_roas']:.2f}x"
                )
            
            with col2:
                st.metric(
                    "Medium-term ROI",
                    f"{results['medium_term']['roi_pct']:.1f}%",
                    delta=f"ROAS: {results['medium_term']['profit_roas']:.2f}x"
                )
            
            with col3:
                st.metric(
                    "Long-term ROI",
                    f"{results['long_term']['roi_pct']:.1f}%",
                    delta=f"ROAS: {results['long_term']['profit_roas']:.2f}x"
                )
            
            # Scenario Comparison
            st.subheader("Scenario Analysis")
            
            scenario_df = pd.DataFrame(results['scenarios']).T
            scenario_df = scenario_df.sort_values('roi', ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            colors = ['green' if v > 0 else 'red' for v in scenario_df['roi_pct']]
            ax.barh(scenario_df['name'], scenario_df['roi_pct'], color=colors, edgecolor='black', alpha=0.7)
            ax.set_xlabel('ROI (%)')
            ax.set_title('Scenario Comparison', fontsize=14, fontweight='bold')
            ax.axvline(0, color='black', linestyle='-', linewidth=1)
            plt.tight_layout()
            st.pyplot(fig)
            
            # Channel ROI
            if 'channel_roi' in results and results['channel_roi']:
                st.subheader("ROI by Channel")
                channel_roi_df = pd.DataFrame(results['channel_roi']).T
                channel_roi_df = channel_roi_df.sort_values('roi', ascending=False)
                st.dataframe(channel_roi_df[['profit_roas', 'roi_pct']], use_container_width=True)
        
        else:
            st.info("👈 Click 'Run Complete Analysis' in sidebar")
    
    # TAB 6: Visualizations
    with tab6:
        st.header("Analysis Visualizations")
        
        if st.session_state.analysis_run:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'dynamics_analyzer' in st.session_state:
                    st.subheader("Purchase Dynamics")
                    fig = st.session_state.dynamics_analyzer.plot_dynamics(
                        st.session_state.metadata['test_start_date'],
                        save_path=None
                    )
                    st.pyplot(fig)
            
            with col2:
                if 'hte_analyzer' in st.session_state:
                    st.subheader("Heterogeneous Effects")
                    fig = st.session_state.hte_analyzer.plot_hte_results(
                        st.session_state.hte_results,
                        save_path=None
                    )
                    st.pyplot(fig)
        else:
            st.info("Run analysis first to see visualizations")
    
    # TAB 7: Report
    with tab7:
        st.header("📄 Executive Report")
        
        if st.session_state.analysis_run:
            # Export options
            col1, col2 = st.columns(2)
            
            # Compile report
            report = {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_quality': st.session_state.get('quality_report', {}),
                'purchase_dynamics': st.session_state.get('dynamics_results', {}),
                'hte': st.session_state.get('hte_results', {}),
                'roi': st.session_state.get('roi_results', {})
            }
            
            with col1:
                json_str = json.dumps(report, indent=2, default=str)
                st.download_button(
                    "📥 Download Full Report (JSON)",
                    json_str,
                    file_name=f"brightline_analysis_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            # Executive summary
            st.subheader("Executive Summary")
            
            if 'quality_report' in st.session_state:
                st.write(f"**Data Quality:** {st.session_state.quality_report['grade']}")
            
            if 'dynamics_results' in st.session_state:
                scenario = st.session_state.dynamics_results['scenario']
                st.write(f"**Purchase Behavior:** {scenario['scenario']} {scenario['quality']}")
            
            if 'hte_results' in st.session_state:
                best_channel = max(
                    st.session_state.hte_results['channel_effects'].items(),
                    key=lambda x: x[1]['pct_lift']
                )
                st.write(f"**Best Channel:** {best_channel[0]} ({best_channel[1]['pct_lift']:.1f}% lift)")
            
            if 'roi_results' in st.session_state:
                roi = st.session_state.roi_results
                st.write(f"**Long-term ROI:** {roi['long_term']['roi_pct']:.1f}%")
        
        else:
            st.info("Run analysis to generate report")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Brightline Enhanced Analysis v2.0**")
st.sidebar.markdown("Multi-channel RCT Framework")