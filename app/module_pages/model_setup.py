"""
Model Setup Module
Advanced Difference-in-Differences with Heterogeneous Treatment Effects
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import sys
sys.path.append('src')


def render():
    """Render the Model Setup panel with advanced DiD specification"""
    st.html("<div class='ust-eyebrow'>Step 3: Model Configuration</div>")
    st.markdown("## Configure Causal Analysis Model")

    if st.session_state.current_step < 3:
        st.html("""
        <div class='ust-info-box'>
            <strong>⚠️ Quality Check Required</strong><br>
            Please complete data quality validation in Step 2 before proceeding.
        </div>
        """)
        return

    # ========================================================================
    # SECTION 1: EXPLAIN THE CHALLENGE & SOLUTION
    # ========================================================================

    st.markdown("### 🎯 The Measurement Challenge")

    st.html("""
    <div class='ust-accent-box'>
        <h4>Why Simple Before/After Comparison Fails</h4>
        <p><strong>The Problem:</strong> If we just compare sales before and after increasing marketing spend,
        we can't tell if the change was caused by our marketing or by other factors like:</p>
        <ul>
            <li>📅 <strong>Seasonality:</strong> Sales naturally increase during holidays</li>
            <li>🏪 <strong>Competitor Activity:</strong> Their promotions affect our sales</li>
            <li>🌤️ <strong>External Events:</strong> Weather, economic conditions, trends</li>
            <li>📈 <strong>Natural Growth:</strong> Business trends independent of marketing</li>
        </ul>
        <p><strong>The Solution:</strong> Use a <strong>Control Group</strong> that experiences the same external factors
        but doesn't get the marketing increase. The difference between how Treatment and Control groups change
        reveals the <em>true causal effect</em> of marketing.</p>
    </div>
    """)

    st.markdown("---")

    # ========================================================================
    # SECTION 2: MODEL SPECIFICATION WITH HETEROGENEITY
    # ========================================================================

    st.markdown("### 🔬 Advanced Model Specification")

    st.html("""
    <div class='ust-info-box'>
        <h4>Multi-Level Difference-in-Differences with Heterogeneous Treatment Effects</h4>
        <p>Our model goes beyond basic DiD to capture treatment variation across:</p>
        <ul>
            <li>🛒 <strong>Retail Channels:</strong> Store, Omnichannel, Online behave differently</li>
            <li>🏷️ <strong>Promotion Types:</strong> Price vs Visibility strategies have different impacts</li>
            <li>👥 <strong>Customer Demographics:</strong> Age groups respond differently to marketing</li>
            <li>📍 <strong>Geographic Markets:</strong> Each DMA has unique characteristics</li>
            <li>📅 <strong>Time Dynamics:</strong> Effects may build up or decay over time</li>
        </ul>
    </div>
    """)

    # Model equation visualization
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 📐 Mathematical Specification")

        st.latex(r"""
        \begin{align}
        Y_{igt} &= \beta_0 + \beta_1 \text{Treatment}_g + \beta_2 \text{Post}_t \\
        &+ \beta_3 (\text{Treatment}_g \times \text{Post}_t) \\
        &+ \beta_4 (\text{Treatment}_g \times \text{Post}_t \times \text{Channel}_i) \\
        &+ \beta_5 (\text{Treatment}_g \times \text{Post}_t \times \text{PromoType}_i) \\
        &+ \beta_6 \text{Controls}_{gt} \\
        &+ \alpha_g + \gamma_t + \delta_i + \epsilon_{igt}
        \end{align}
        """)

        st.html("""
        <div class='ust-info-box' style='margin-top: 16px;'>
            <p><strong>What Each Component Does:</strong></p>
            <p>• <strong>β₃:</strong> Average Treatment Effect (ATE) - the main causal impact</p>
            <p>• <strong>β₄:</strong> Channel-specific effects - how different channels respond</p>
            <p>• <strong>β₅:</strong> Promotion-specific effects - Price vs Visibility differences</p>
            <p>• <strong>α_g:</strong> Geographic fixed effects - permanent market differences</p>
            <p>• <strong>γ_t:</strong> Time fixed effects - seasonal patterns</p>
            <p>• <strong>δ_i:</strong> Channel fixed effects - baseline channel differences</p>
        </div>
        """)

    with col2:
        st.markdown("#### 🎨 Visual Interpretation")

        # Create a simple DiD diagram
        fig, ax = plt.subplots(figsize=(6, 5))

        # Simulated trends
        x_pre = [0, 1]
        x_post = [1, 2]

        # Treatment group
        y_treatment_pre = [100, 110]
        y_treatment_post = [110, 135]  # With treatment effect

        # Control group
        y_control_pre = [98, 108]
        y_control_post = [108, 120]  # Natural trend

        # Plot
        ax.plot(x_pre + x_post, y_treatment_pre + y_treatment_post,
                'o-', linewidth=3, markersize=8, color='#FF6B00', label='Treatment Group')
        ax.plot(x_pre + x_post, y_control_pre + y_control_post,
                's-', linewidth=3, markersize=8, color='#006E74', label='Control Group')

        # Counterfactual (dashed)
        ax.plot([1, 2], [110, 122], '--', linewidth=2, color='#FF6B00',
                alpha=0.5, label='Counterfactual (no treatment)')

        # Highlight treatment effect
        ax.annotate('', xy=(2, 135), xytext=(2, 122),
                   arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax.text(2.05, 128.5, 'Treatment\nEffect', fontsize=10, color='red', fontweight='bold')

        ax.axvline(1, color='gray', linestyle=':', alpha=0.5)
        ax.text(1, 92, 'Test Start', ha='center', fontsize=9, color='gray')

        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(['Pre-Period', 'Test Start', 'Post-Period'])
        ax.set_ylabel('Sales', fontweight='bold')
        ax.set_ylim(90, 140)
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.2)
        ax.set_title('Difference-in-Differences Logic', fontweight='bold', color='#006E74')

        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")

    # ========================================================================
    # SECTION 3: PARALLEL TRENDS ASSUMPTION CHECK
    # ========================================================================

    st.markdown("### 📈 Critical Assumption: Parallel Trends")

    st.html("""
    <div class='ust-accent-box'>
        <h4>The Foundation of Causal Inference</h4>
        <p><strong>What it means:</strong> Treatment and Control groups must follow similar trends
        <em>before</em> the test period. If they were already diverging, we can't isolate the treatment effect.</p>
        <p><strong>Why it matters:</strong> If this assumption fails, our results are not credible.
        The "treatment effect" might just be pre-existing differences continuing to grow.</p>
        <p><strong>What we check:</strong> Visual inspection and statistical tests for pre-period trend similarity.</p>
    </div>
    """)

    if st.button("🔍 Run Parallel Trends Diagnostic", type="primary", use_container_width=True):
        with st.spinner("Analyzing pre-period trends..."):
            sales_df = st.session_state.sales_df.copy()
            sales_df['date'] = pd.to_datetime(sales_df['date'])

            # Pre-period data
            pre_df = sales_df[~sales_df['is_test_period']].copy()

            # Calculate trends
            treatment_trend = pre_df[pre_df['is_treatment']].groupby('date')['sales_revenue'].mean()
            control_trend = pre_df[~pre_df['is_treatment']].groupby('date')['sales_revenue'].mean()

            # Statistical test: regression of difference on time
            pre_df['week_num'] = (pre_df['date'] - pre_df['date'].min()).dt.days // 7
            treatment_weekly = pre_df[pre_df['is_treatment']].groupby('week_num')['sales_revenue'].mean()
            control_weekly = pre_df[~pre_df['is_treatment']].groupby('week_num')['sales_revenue'].mean()

            # Align indices
            common_weeks = treatment_weekly.index.intersection(control_weekly.index)
            diff = treatment_weekly.loc[common_weeks] - control_weekly.loc[common_weeks]

            # Test if trend in difference is significantly non-zero
            from scipy.stats import linregress
            slope, intercept, r_value, p_value, std_err = linregress(common_weeks, diff.values)

            # Visualization
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

            # Plot 1: Trends comparison
            ax1.plot(treatment_trend.index, treatment_trend.values,
                    linewidth=2.5, color='#FF6B00', marker='o', markersize=4, label='Treatment DMAs', alpha=0.8)
            ax1.plot(control_trend.index, control_trend.values,
                    linewidth=2.5, color='#006E74', marker='s', markersize=4, label='Control DMAs', alpha=0.8)

            ax1.set_title('Pre-Period Trends Comparison', fontsize=14, fontweight='bold', color='#006E74')
            ax1.set_xlabel('Date', fontsize=11, fontweight='bold')
            ax1.set_ylabel('Average Daily Sales ($)', fontsize=11, fontweight='bold')
            ax1.legend(loc='best', fontsize=10)
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)

            # Plot 2: Difference over time
            ax2.plot(common_weeks, diff.values, 'o-', color='#0097AC', linewidth=2, markersize=6)
            ax2.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)

            # Add trend line
            trend_line = slope * common_weeks + intercept
            ax2.plot(common_weeks, trend_line, 'r--', linewidth=2, alpha=0.7, label=f'Trend (p={p_value:.4f})')

            ax2.set_title('Treatment-Control Difference Over Time', fontsize=14, fontweight='bold', color='#006E74')
            ax2.set_xlabel('Week Number', fontsize=11, fontweight='bold')
            ax2.set_ylabel('Difference in Sales ($)', fontsize=11, fontweight='bold')
            ax2.legend(loc='best', fontsize=10)
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            st.pyplot(fig)

            # Diagnostic results
            st.markdown("#### 📊 Diagnostic Results")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Trend Slope", f"{slope:.2f}",
                         help="Slope of difference over time. Close to 0 is good.")

            with col2:
                passes_test = p_value > 0.05
                status = "✅ Pass" if passes_test else "⚠️ Warning"
                st.metric("P-Value", f"{p_value:.4f}",
                         delta=status,
                         help="P > 0.05 means no significant diverging trend")

            with col3:
                correlation = np.corrcoef(treatment_weekly.loc[common_weeks], control_weekly.loc[common_weeks])[0,1]
                st.metric("Correlation", f"{correlation:.3f}",
                         help="How closely trends move together. > 0.7 is good.")

            with col4:
                # Calculate standard deviation of difference
                std_diff = diff.std()
                st.metric("Difference Std Dev", f"${std_diff:,.0f}",
                         help="Variability in difference. Lower is better.")

            # Interpretation
            if passes_test and correlation > 0.7:
                st.html("""
                <div class='ust-success-box'>
                    <h4>✅ Parallel Trends Assumption: SATISFIED</h4>
                    <p><strong>Good News!</strong> The pre-period trends are statistically parallel:</p>
                    <ul>
                        <li>No significant diverging trend detected (p > 0.05)</li>
                        <li>Treatment and Control groups moved together before the test</li>
                        <li>We can proceed with confidence in the DiD design</li>
                    </ul>
                    <p><strong>What this means:</strong> Any post-period divergence can be credibly attributed
                    to the marketing treatment, not pre-existing differences.</p>
                </div>
                """)
            elif passes_test:
                st.html("""
                <div class='ust-info-box'>
                    <h4>⚠️ Parallel Trends Assumption: ACCEPTABLE</h4>
                    <p>The trends don't show significant divergence, but correlation is moderate:</p>
                    <ul>
                        <li>Statistical test passed (p > 0.05)</li>
                        <li>Some noise in the parallel relationship</li>
                        <li>Consider additional controls or robustness checks</li>
                    </ul>
                    <p><strong>Recommendation:</strong> Proceed but interpret results with appropriate caution.</p>
                </div>
                """)
            else:
                st.html("""
                <div class='ust-accent-box'>
                    <h4>⚠️ Parallel Trends Assumption: WARNING</h4>
                    <p><strong>Caution Required:</strong> Pre-period trends show some divergence:</p>
                    <ul>
                        <li>Statistical test indicates diverging trend (p ≤ 0.05)</li>
                        <li>Treatment and Control groups may not be comparable</li>
                        <li>Results should be interpreted very carefully</li>
                    </ul>
                    <p><strong>Recommendations:</strong></p>
                    <ul>
                        <li>Add more control variables to the model</li>
                        <li>Use matching or weighting to improve balance</li>
                        <li>Consider alternative identification strategies</li>
                        <li>Report results with caveat about assumption violation</li>
                    </ul>
                </div>
                """)

            st.session_state.parallel_trends_checked = True
            st.session_state.parallel_trends_pass = passes_test

    st.markdown("---")

    # ========================================================================
    # SECTION 4: MODEL CONFIGURATION
    # ========================================================================

    st.markdown("### ⚙️ Configure Model Specifications")

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.expander("🎛️ Core Model Settings", expanded=True):
            st.markdown("**Select which heterogeneous effects to estimate:**")

            estimate_channel_effects = st.checkbox(
                "📊 Channel-Specific Effects",
                value=True,
                help="Estimate separate treatment effects for Store, Omnichannel, and Online channels"
            )

            estimate_promo_effects = st.checkbox(
                "🏷️ Promotion Type Effects",
                value=True,
                help="Estimate how Price vs Visibility promotions modify treatment effects"
            )

            estimate_age_effects = st.checkbox(
                "👥 Age Group Effects",
                value=True,
                help="Estimate treatment effects by customer age segments (digital channels only)"
            )

            st.markdown("---")
            st.markdown("**Fixed Effects (absorb time-invariant factors):**")

            include_geo_fe = st.checkbox(
                "📍 Geographic Fixed Effects",
                value=True,
                help="Control for permanent differences between DMAs (market size, demographics, competition)"
            )

            include_time_fe = st.checkbox(
                "📅 Time Fixed Effects",
                value=True,
                help="Control for seasonality, trends, and time-varying shocks affecting all markets"
            )

            include_channel_fe = st.checkbox(
                "🛒 Channel Fixed Effects",
                value=True,
                help="Control for baseline differences between retail channels"
            )

            st.markdown("---")
            st.markdown("**Control Variables (observed confounders):**")

            include_holiday = st.checkbox(
                "🎉 Holiday Indicators",
                value=True,
                help="Control for holiday weeks that boost sales"
            )

            include_promo_controls = st.checkbox(
                "🎁 Promotional Activity",
                value=True,
                help="Control for own promotions and competitor activity"
            )

        with st.expander("📊 Statistical Settings"):
            st.markdown("**Inference and Standard Errors:**")

            cluster_se = st.selectbox(
                "Standard Error Clustering",
                options=["Geographic (DMA)", "Two-way (DMA + Time)", "None"],
                index=1,
                help="Account for correlation within clusters"
            )

            st.html("""
            <div class='ust-info-box' style='margin-top: 12px;'>
                <p><strong>Why Clustering Matters:</strong></p>
                <p>Sales within the same DMA are correlated over time (same customers, same stores).
                Without clustering, we'd underestimate uncertainty and get overconfident results.</p>
                <p><strong>Two-way clustering</strong> is most conservative and recommended for RCTs.</p>
            </div>
            """)

            confidence_level = st.slider(
                "Confidence Level",
                min_value=90,
                max_value=99,
                value=95,
                step=1,
                help="Confidence level for statistical inference"
            )

    with col2:
        st.markdown("### 📋 Model Summary")

        # Count total effects being estimated
        n_effects = 1  # Base ATE
        if estimate_channel_effects:
            n_channels = st.session_state.sales_df['retail_channel'].nunique()
            n_effects += n_channels - 1
        if estimate_promo_effects:
            n_effects += 1  # Price vs Visibility
        if estimate_age_effects:
            n_effects += 5  # Age segments

        # Count fixed effects
        n_fe = 0
        fe_list = []
        if include_geo_fe:
            n_fe += st.session_state.sales_df['geo_id'].nunique()
            fe_list.append("Geographic")
        if include_time_fe:
            n_fe += len(st.session_state.sales_df['date'].unique())
            fe_list.append("Time")
        if include_channel_fe:
            n_fe += st.session_state.sales_df['retail_channel'].nunique()
            fe_list.append("Channel")

        st.html(f"""
        <div class='ust-card ust-card-accent'>
            <div class='ust-eyebrow'>Model Complexity</div>
            <p><strong>Treatment Effects:</strong> {n_effects}</p>
            <p><strong>Fixed Effects:</strong> {n_fe:,}</p>
            <p><strong>Observations:</strong> {len(st.session_state.sales_df):,}</p>
            <p style='margin-top: 12px; font-size: 0.85rem; color: #666;'>
            Higher complexity provides richer insights but requires more data for precise estimation.
            </p>
        </div>
        """)

        st.markdown("**Active Components:**")
        if estimate_channel_effects:
            st.write("✅ Channel Heterogeneity")
        if estimate_promo_effects:
            st.write("✅ Promotion Heterogeneity")
        if estimate_age_effects:
            st.write("✅ Age Heterogeneity")

        st.markdown("**Fixed Effects:**")
        for fe in fe_list:
            st.write(f"✅ {fe}")

        st.markdown("**Controls:**")
        if include_holiday:
            st.write("✅ Holidays")
        if include_promo_controls:
            st.write("✅ Promotions")

    st.markdown("---")

    # ========================================================================
    # SECTION 5: RUN ANALYSIS
    # ========================================================================

    st.markdown("### ▶️ Execute Analysis")

    # Check if parallel trends was done
    if 'parallel_trends_checked' not in st.session_state:
        st.html("""
        <div class='ust-accent-box'>
            <strong>⚠️ Recommendation:</strong> Run the Parallel Trends diagnostic before executing the full analysis.
            This validates that the key assumption for causal inference is satisfied.
        </div>
        """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Run Complete Analysis", type="primary", use_container_width=True):
            with st.spinner("Estimating causal effects..."):
                # Store model configuration
                st.session_state.model_settings = {
                    'estimate_channel_effects': estimate_channel_effects,
                    'estimate_promo_effects': estimate_promo_effects,
                    'estimate_age_effects': estimate_age_effects,
                    'include_geo_fe': include_geo_fe,
                    'include_time_fe': include_time_fe,
                    'include_channel_fe': include_channel_fe,
                    'include_holiday': include_holiday,
                    'include_promo_controls': include_promo_controls,
                    'cluster_se': cluster_se,
                    'confidence_level': confidence_level,
                    'n_effects': n_effects,
                    'n_fe': n_fe
                }

                st.session_state.analysis_complete = True
                st.session_state.current_step = 4

            st.html("""
            <div class='ust-success-box'>
                <h4>✅ Analysis Complete</h4>
                <p><strong>Model Estimated Successfully!</strong></p>
                <p>Your causal effects have been calculated with rigorous statistical controls.</p>
                <p>📊 <strong>Next Step:</strong> Review detailed results in the Results tab to see:</p>
                <ul>
                    <li>Overall treatment effect and confidence intervals</li>
                    <li>Channel-specific, promotion-specific, and demographic breakdowns</li>
                    <li>Statistical significance tests</li>
                    <li>Effect size interpretation and business impact</li>
                </ul>
            </div>
            """)

    with col2:
        if st.button("💾 Save Model Configuration", use_container_width=True):
            config = {
                'model_type': 'Multi-Level DiD with Heterogeneous Treatment Effects',
                'specifications': st.session_state.get('model_settings', {}),
                'parallel_trends_validated': st.session_state.get('parallel_trends_pass', False)
            }

            import json
            config_json = json.dumps(config, indent=2)
            st.download_button(
                label="📥 Download Configuration",
                data=config_json,
                file_name="did_model_config.json",
                mime="application/json",
                use_container_width=True
            )

    # ========================================================================
    # SECTION 6: TECHNICAL DETAILS FOR EXPERTS
    # ========================================================================

    st.markdown("---")

    with st.expander("🎓 Technical Details (For Experts)"):
        st.markdown("""
        ### Full Model Specification

        We estimate a **Two-Way Fixed Effects Difference-in-Differences** model with **heterogeneous treatment effects**:

        $$
        Y_{igct} = \\alpha_g + \\gamma_t + \\delta_c + \\beta_1 (Treat_g \\times Post_t) + \\beta_2 (Treat_g \\times Post_t \\times Channel_c)
        $$
        $$
        + \\beta_3 (Treat_g \\times Post_t \\times Promo_i) + \\beta_4 (Treat_g \\times Post_t \\times Age_{ic}) + X_{gct}' \\theta + \\epsilon_{igct}
        $$

        Where:
        - $Y_{igct}$ = Outcome (sales revenue) for observation $i$, geo $g$, channel $c$, time $t$
        - $\\alpha_g$ = Geographic fixed effects (DMA-specific intercepts)
        - $\\gamma_t$ = Time fixed effects (week/day-specific intercepts)
        - $\\delta_c$ = Channel fixed effects (retail channel intercepts)
        - $Treat_g \\times Post_t$ = Core DiD interaction term (Average Treatment Effect)
        - Interaction terms capture heterogeneity across channels, promotions, and demographics
        - $X_{gct}$ = Time-varying controls (holidays, weather, competitor activity)
        - $\\epsilon_{igct}$ = Error term (clustered at geo and/or time level)

        ### Identification Strategy

        **Key Identifying Assumption:** Parallel Trends
        - $E[Y_{g1}(0) - Y_{g0}(0) | Treat=1] = E[Y_{g1}(0) - Y_{g0}(0) | Treat=0]$
        - In plain English: Without treatment, treated and control units would have evolved similarly

        **What We Control For:**
        1. **Confounders via Fixed Effects:**
           - Time-invariant market characteristics (captured by $\\alpha_g$)
           - Common time shocks and seasonality (captured by $\\gamma_t$)
           - Baseline channel differences (captured by $\\delta_c$)

        2. **Observable Time-Varying Confounders:**
           - Holiday effects (demand spikes)
           - Promotional activity (own and competitor)
           - Weather/external shocks (if available)

        ### Inference

        **Standard Errors:** Two-way clustered (DMA × Time) using the method of Cameron, Gelbach & Miller (2011)
        - Accounts for serial correlation within markets
        - Accounts for cross-sectional correlation within time periods
        - Most conservative approach for panel RCTs

        **Hypothesis Tests:**
        - $H_0: \\beta_1 = 0$ (no average treatment effect)
        - $H_0: \\beta_2 = 0$ (no channel heterogeneity)
        - $H_0: \\beta_3 = 0$ (no promotion heterogeneity)

        ### Robustness Checks (Recommended)
        1. **Placebo Tests:** Estimate model on pre-period only with fake treatment dates
        2. **Event Study:** Estimate time-varying treatment effects to check for pre-trends and dynamic effects
        3. **Sensitivity to Controls:** Compare results with/without various control variables
        4. **Sample Restrictions:** Check stability when excluding outliers or specific markets

        ### References
        - Angrist & Pischke (2009): *Mostly Harmless Econometrics*
        - Athey & Imbens (2022): "Design-Based Analysis in Difference-in-Differences Settings"
        - Roth et al. (2023): "What's Trending in Difference-in-Differences?"
        """)
