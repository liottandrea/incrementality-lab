"""
Validate Quality Module
Handles data quality validation and checks
"""

import streamlit as st
import sys
sys.path.append('src')

from data_validator import DataQualityValidator


def render():
    """Render the Validate Quality panel"""
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
