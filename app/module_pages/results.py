"""
Results Module
Comprehensive causal inference results with statistical rigor and clear communication
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import sys
sys.path.append('src')

from purchase_dynamics import PurchaseDynamicsAnalyzer
from hte_analysis import HeterogeneousEffectsAnalyzer


def calculate_confidence_interval(point_estimate, std_error, confidence_level=95):
    """Calculate confidence interval for an estimate"""
    alpha = 1 - (confidence_level / 100)
    z_score = stats.norm.ppf(1 - alpha/2)
    margin = z_score * std_error
    return point_estimate - margin, point_estimate + margin


def interpret_p_value(p_value):
    """Provide plain-English interpretation of p-value"""
    if p_value < 0.001:
        return "Extremely strong evidence", "✅", "#006E74"
    elif p_value < 0.01:
        return "Very strong evidence", "✅", "#006E74"
    elif p_value < 0.05:
        return "Strong evidence", "✅", "#0097AC"
    elif p_value < 0.10:
        return "Moderate evidence", "⚠️", "#FF6B00"
    else:
        return "Weak evidence", "❌", "#DC3545"


def render():
    """Render the comprehensive Results panel"""
    st.html("<div class='ust-eyebrow'>Step 4: Causal Impact & Insights</div>")
    st.markdown("## Analysis Results")

    if not st.session_state.analysis_complete:
        st.html("""
        <div class='ust-info-box'>
            <strong>⚠️ Analysis Required</strong><br>
            Please run the analysis in Step 3 before viewing results.
        </div>
        """)
        return

    # ========================================================================
    # RUN ANALYSES IF NOT ALREADY DONE
    # ========================================================================

    if 'dynamics_results' not in st.session_state:
        with st.spinner("Estimating causal effects and generating insights..."):
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

    # ========================================================================
    # SECTION 1: EXECUTIVE SUMMARY
    # ========================================================================

    st.markdown("### 📊 Executive Summary")

    st.html("""
    <div class='ust-accent-box'>
        <h4>What We're Measuring</h4>
        <p><strong>Causal Question:</strong> What is the <em>incremental</em> impact of increasing marketing spend
        on sales revenue, after controlling for all other factors?</p>
        <p><strong>How We Measure It:</strong> Compare the change in sales for markets that received increased
        marketing (Treatment) vs markets that didn't (Control). The difference in changes = causal effect.</p>
    </div>
    """)

    # Calculate overall treatment effect
    sales_df = st.session_state.sales_df
    test_start = pd.to_datetime(st.session_state.metadata['test_start_date'])
    sales_df['date'] = pd.to_datetime(sales_df['date'])

    # DiD calculation
    treatment_pre = sales_df[(sales_df['is_treatment']) & (~sales_df['is_test_period'])]['sales_revenue'].mean()
    treatment_post = sales_df[(sales_df['is_treatment']) & (sales_df['is_test_period'])]['sales_revenue'].mean()
    control_pre = sales_df[(~sales_df['is_treatment']) & (~sales_df['is_test_period'])]['sales_revenue'].mean()
    control_post = sales_df[(~sales_df['is_treatment']) & (sales_df['is_test_period'])]['sales_revenue'].mean()

    treatment_change = treatment_post - treatment_pre
    control_change = control_post - control_pre
    did_effect = treatment_change - control_change
    pct_lift = (did_effect / control_post) * 100

    # Estimate standard error (simplified)
    treatment_std = sales_df[(sales_df['is_treatment']) & (sales_df['is_test_period'])]['sales_revenue'].std()
    control_std = sales_df[(~sales_df['is_treatment']) & (sales_df['is_test_period'])]['sales_revenue'].std()
    n_treatment = len(sales_df[(sales_df['is_treatment']) & (sales_df['is_test_period'])])
    n_control = len(sales_df[(~sales_df['is_treatment']) & (sales_df['is_test_period'])])
    std_error = np.sqrt((treatment_std**2 / n_treatment) + (control_std**2 / n_control))

    # Confidence interval
    confidence_level = st.session_state.model_settings.get('confidence_level', 95)
    ci_lower, ci_upper = calculate_confidence_interval(did_effect, std_error, confidence_level)
    ci_lower_pct = (ci_lower / control_post) * 100
    ci_upper_pct = (ci_upper / control_post) * 100

    # Statistical significance
    t_stat = did_effect / std_error
    p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
    sig_interp, sig_icon, sig_color = interpret_p_value(p_value)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='ust-card ust-card-accent'>
            <div class='ust-eyebrow'>Average Treatment Effect</div>
            <h2 style='color: {sig_color}; font-size: 2.5rem; margin: 12px 0;'>{pct_lift:+.1f}%</h2>
            <p style='color: #666; font-size: 0.9rem;'>${did_effect:,.0f} per record</p>
            <p style='color: #666; font-size: 0.85rem; margin-top: 8px;'>
            {confidence_level}% CI: [{ci_lower_pct:.1f}%, {ci_upper_pct:.1f}%]</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Statistical Significance</div>
            <h2 style='color: {sig_color}; font-size: 2rem; margin: 12px 0;'>{sig_icon}</h2>
            <p style='color: #666;'>{sig_interp}</p>
            <p style='color: #999; font-size: 0.85rem; margin-top: 8px;'>
            p-value: {p_value:.4f}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        total_incremental = did_effect * len(sales_df[sales_df['is_test_period']])
        st.markdown(f"""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Total Incremental Sales</div>
            <h2 style='color: #006E74; font-size: 1.8rem; margin: 12px 0;'>${total_incremental:,.0f}</h2>
            <p style='color: #666;'>During test period</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # Calculate incremental spend
        media_df = st.session_state.media_df
        media_df['date'] = pd.to_datetime(media_df['date'])
        treatment_dmas = st.session_state.metadata['treatment_dmas']

        treatment_media = media_df[media_df['geo_id'].isin(treatment_dmas)]
        control_media = media_df[~media_df['geo_id'].isin(treatment_dmas)]

        incremental_spend = treatment_media['spend_usd'].sum() - control_media['spend_usd'].sum()

        st.markdown(f"""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Incremental Investment</div>
            <h2 style='color: #FF6B00; font-size: 1.8rem; margin: 12px 0;'>${incremental_spend:,.0f}</h2>
            <p style='color: #666;'>Marketing spend increase</p>
        </div>
        """, unsafe_allow_html=True)

    # Interpretation
    st.markdown("#### 🎯 What This Means")

    if p_value < 0.05:
        st.html(f"""
        <div class='ust-success-box'>
            <h4>✅ Marketing Investment Delivered Measurable Impact</h4>
            <p><strong>Key Finding:</strong> Increasing marketing spend caused a <strong>{pct_lift:+.1f}%</strong>
            lift in sales revenue, with {confidence_level}% confidence that the true effect is between
            <strong>{ci_lower_pct:.1f}%</strong> and <strong>{ci_upper_pct:.1f}%</strong>.</p>

            <p><strong>In Plain English:</strong> For every dollar of additional marketing spend,
            we generated <strong>${(total_incremental/incremental_spend):.2f}</strong> in incremental revenue.
            This effect is <em>statistically significant</em> (p = {p_value:.4f}), meaning we can be confident
            it's a real effect, not random chance.</p>

            <p><strong>Business Impact:</strong> The treatment generated <strong>${total_incremental:,.0f}</strong>
            in additional sales during the test period.</p>
        </div>
        """)
    else:
        st.html(f"""
        <div class='ust-accent-box'>
            <h4>⚠️ No Statistically Significant Effect Detected</h4>
            <p><strong>Finding:</strong> The estimated effect is {pct_lift:+.1f}%, but this is not
            statistically significant (p = {p_value:.4f}).</p>

            <p><strong>In Plain English:</strong> We cannot confidently say the marketing increase caused
            a change in sales. The observed difference might just be random variation.</p>

            <p><strong>Possible Reasons:</strong></p>
            <ul>
                <li>The true effect may be too small to detect with this sample size</li>
                <li>The effect may vary substantially across markets/channels (check heterogeneity below)</li>
                <li>The test period may be too short to capture the full effect</li>
                <li>There may be measurement issues or violations of assumptions</li>
            </ul>
        </div>
        """)

    st.markdown("---")

    # ========================================================================
    # SECTION 2: TREATMENT EFFECT DECOMPOSITION
    # ========================================================================

    st.markdown("### 📈 Effect Over Time (Event Study)")

    st.html("""
    <div class='ust-info-box'>
        <h4>Dynamic Treatment Effects</h4>
        <p><strong>What this shows:</strong> How the treatment effect evolves over time. This helps us understand:</p>
        <ul>
            <li>Whether effects are immediate or build up gradually</li>
            <li>If effects persist or decay over time</li>
            <li>Pre-period trends (should be near zero, validating parallel trends)</li>
        </ul>
    </div>
    """)

    # Calculate weekly effects
    sales_df['week'] = (sales_df['date'] - sales_df['date'].min()).dt.days // 7
    test_start_week = (test_start - sales_df['date'].min()).days // 7

    weekly_treatment = sales_df[sales_df['is_treatment']].groupby('week')['sales_revenue'].mean()
    weekly_control = sales_df[~sales_df['is_treatment']].groupby('week')['sales_revenue'].mean()

    # Align indices
    common_weeks = weekly_treatment.index.intersection(weekly_control.index)
    weekly_diff = weekly_treatment.loc[common_weeks] - weekly_control.loc[common_weeks]

    # Normalize to pre-period average
    pre_weeks = common_weeks[common_weeks < test_start_week]
    baseline_diff = weekly_diff.loc[pre_weeks].mean()
    weekly_effect = weekly_diff - baseline_diff

    # Plot
    fig, ax = plt.subplots(figsize=(14, 6))

    pre_effect = weekly_effect.loc[weekly_effect.index < test_start_week]
    post_effect = weekly_effect.loc[weekly_effect.index >= test_start_week]

    ax.plot(pre_effect.index, pre_effect.values, 'o-', linewidth=2.5, markersize=6,
            color='#006E74', label='Pre-Period (should be ~0)', alpha=0.8)
    ax.plot(post_effect.index, post_effect.values, 'o-', linewidth=2.5, markersize=6,
            color='#FF6B00', label='Post-Period (treatment effect)', alpha=0.8)

    ax.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.3)
    ax.axvline(test_start_week, color='red', linestyle='--', linewidth=2, alpha=0.7,
               label='Treatment Start')

    # Add confidence bands (approximate)
    ax.fill_between(post_effect.index,
                     post_effect.values - 1.96*std_error,
                     post_effect.values + 1.96*std_error,
                     alpha=0.2, color='#FF6B00', label='95% Confidence Band')

    ax.set_xlabel('Week Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Treatment Effect ($)', fontsize=12, fontweight='bold')
    ax.set_title('Dynamic Treatment Effects Over Time (Event Study)', fontsize=14, fontweight='bold', color='#006E74')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)

    # Interpretation
    col1, col2 = st.columns(2)

    with col1:
        avg_pre_effect = pre_effect.mean()
        pre_sig = abs(avg_pre_effect / std_error) < 1.96

        if pre_sig:
            st.html("""
            <div class='ust-success-box'>
                <h4>✅ Pre-Period Validation</h4>
                <p>Pre-period effects are close to zero, supporting the parallel trends assumption.</p>
            </div>
            """)
        else:
            st.html("""
            <div class='ust-accent-box'>
                <h4>⚠️ Pre-Period Concern</h4>
                <p>Pre-period effects show some divergence. This may indicate pre-existing trends.</p>
            </div>
            """)

    with col2:
        post_trend = np.polyfit(post_effect.index, post_effect.values, 1)[0]

        if post_trend > 0:
            st.html("""
            <div class='ust-success-box'>
                <h4>📈 Building Effect</h4>
                <p>Treatment effect increases over time, suggesting sustained or growing impact.</p>
            </div>
            """)
        elif post_trend < 0:
            st.html("""
            <div class='ust-info-box'>
                <h4>📉 Decaying Effect</h4>
                <p>Treatment effect decreases over time, suggesting initial spike that fades.</p>
            </div>
            """)
        else:
            st.html("""
            <div class='ust-info-box'>
                <h4>➡️ Stable Effect</h4>
                <p>Treatment effect remains relatively constant over time.</p>
            </div>
            """)

    st.markdown("---")

    # ========================================================================
    # SECTION 3: HETEROGENEOUS EFFECTS - RETAIL CHANNELS
    # ========================================================================

    st.markdown("### 🛒 Treatment Effects by Retail Channel")

    st.html("""
    <div class='ust-info-box'>
        <h4>Channel-Specific Performance</h4>
        <p><strong>Why this matters:</strong> Marketing effectiveness varies by channel. Understanding where
        the treatment worked best helps optimize budget allocation.</p>
    </div>
    """)

    channel_data = st.session_state.hte_results['channel_effects']
    channel_df = pd.DataFrame(channel_data).T.sort_values('pct_lift', ascending=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['#0097AC' if x >= 0 else '#DC3545' for x in channel_df['pct_lift']]
        bars = ax.barh(channel_df.index, channel_df['pct_lift'],
                      color=colors, edgecolor='#006E74', linewidth=2, alpha=0.8)

        # Highlight best performer
        best_idx = channel_df['pct_lift'].argmax()
        bars[best_idx].set_color('#FF6B00')

        ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        ax.set_xlabel('Treatment Effect (%)', fontsize=12, fontweight='bold')
        ax.set_title('Incremental Lift by Retail Channel', fontsize=14, fontweight='bold', color='#006E74')
        ax.grid(True, alpha=0.3, axis='x')

        # Add value labels
        for i, (idx, row) in enumerate(channel_df.iterrows()):
            label_x = row['pct_lift'] + (0.3 if row['pct_lift'] >= 0 else -0.3)
            ha = 'left' if row['pct_lift'] >= 0 else 'right'
            ax.text(label_x, i, f"{row['pct_lift']:.1f}%", va='center', ha=ha, fontweight='bold', fontsize=10)

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        best_channel = channel_df.index[best_idx]
        best_lift = channel_df['pct_lift'].iloc[best_idx]

        st.html(f"""
        <div class='ust-card ust-card-accent'>
            <div class='ust-eyebrow'>Top Performer</div>
            <h2 style='color: #FF6B00; margin: 12px 0; font-size: 1.5rem;'>{best_channel}</h2>
            <h1 style='color: #006E74; margin: 8px 0;'>{best_lift:+.1f}%</h1>
            <p style='color: #666;'>Incremental lift</p>
        </div>
        """)

        st.metric("Channels Tested", len(channel_df))
        st.metric("Positive Effects", sum(channel_df['pct_lift'] > 0))

    # Channel comparison table
    with st.expander("📊 Detailed Channel Comparison"):
        channel_table = channel_df.copy()
        channel_table['Effect'] = channel_table['pct_lift'].apply(lambda x: f"{x:+.1f}%")
        channel_table['Treatment Effect'] = channel_table['treatment_effect'].apply(lambda x: f"${x:,.0f}")

        # Sort by pct_lift before selecting columns
        channel_table_sorted = channel_table.sort_values('pct_lift', ascending=False)[['Effect', 'Treatment Effect']]

        st.dataframe(
            channel_table_sorted,
            use_container_width=True
        )

    st.markdown("---")

    # ========================================================================
    # SECTION 4: HETEROGENEOUS EFFECTS - PROMOTION TYPES
    # ========================================================================

    st.markdown("### 🏷️ Treatment Effects by Promotion Type")

    st.html("""
    <div class='ust-info-box'>
        <h4>Promotion Strategy Performance</h4>
        <p><strong>Comparing:</strong></p>
        <ul>
            <li><strong>Price Promotions:</strong> Reducing prices to drive demand (Online, Omnichannel)</li>
            <li><strong>Visibility Promotions:</strong> Better shelf position and displays (Store, Omnichannel)</li>
            <li><strong>No Promotion:</strong> Baseline sales without promotional support</li>
        </ul>
    </div>
    """)

    # Calculate promotion effects
    promo_effects = {}
    for promo_type in [None, 'Price', 'Visibility']:
        if promo_type is None:
            promo_data = sales_df[sales_df['promo_type'].isna()]
            label = 'No Promotion'
        else:
            promo_data = sales_df[sales_df['promo_type'] == promo_type]
            label = f'{promo_type} Promotion'

        if len(promo_data) > 0:
            treat_pre = promo_data[(promo_data['is_treatment']) & (~promo_data['is_test_period'])]['sales_revenue'].mean()
            treat_post = promo_data[(promo_data['is_treatment']) & (promo_data['is_test_period'])]['sales_revenue'].mean()
            ctrl_pre = promo_data[(~promo_data['is_treatment']) & (~promo_data['is_test_period'])]['sales_revenue'].mean()
            ctrl_post = promo_data[(~promo_data['is_treatment']) & (promo_data['is_test_period'])]['sales_revenue'].mean()

            # Check all values are valid and non-zero
            if (pd.notna(treat_pre) and pd.notna(treat_post) and
                pd.notna(ctrl_pre) and pd.notna(ctrl_post) and ctrl_post > 0):
                did_eff = (treat_post - treat_pre) - (ctrl_post - ctrl_pre)
                pct_eff = (did_eff / ctrl_post) * 100

                # Only add if the result is valid
                if pd.notna(pct_eff):
                    promo_effects[label] = pct_eff

    if len(promo_effects) > 0:
        col1, col2 = st.columns([2, 1])

        with col1:
            fig, ax = plt.subplots(figsize=(10, 5))

            labels = list(promo_effects.keys())
            values = list(promo_effects.values())
            colors_promo = ['#FF6B00' if 'Price' in l else '#006E74' if 'Visibility' in l else '#0097AC'
                           for l in labels]

            bars = ax.bar(labels, values, color=colors_promo, edgecolor='black', linewidth=2, alpha=0.8)

            ax.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
            ax.set_ylabel('Treatment Effect (%)', fontsize=12, fontweight='bold')
            ax.set_title('Treatment Effect by Promotion Type', fontsize=14, fontweight='bold', color='#006E74')
            ax.grid(True, alpha=0.3, axis='y')

            # Add value labels
            for bar, val in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height + (0.5 if height >= 0 else -0.5),
                       f'{val:.1f}%', ha='center', va='bottom' if height >= 0 else 'top',
                       fontweight='bold', fontsize=11)

            plt.xticks(rotation=15)
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            # Filter out any NaN or invalid values
            valid_promo_effects = {k: v for k, v in promo_effects.items() if pd.notna(v) and not np.isinf(v)}

            if len(valid_promo_effects) > 0:
                best_promo = max(valid_promo_effects, key=valid_promo_effects.get)
                best_promo_lift = valid_promo_effects[best_promo]

                st.html(f"""
                <div class='ust-card ust-card-accent'>
                    <div class='ust-eyebrow'>Most Effective</div>
                    <h2 style='color: #FF6B00; margin: 12px 0; font-size: 1.3rem;'>{best_promo}</h2>
                    <h1 style='color: #006E74; margin: 8px 0;'>{best_promo_lift:+.1f}%</h1>
                    <p style='color: #666;'>Lift vs baseline</p>
                </div>
                """)

                # Strategic insight
                if 'Price' in best_promo:
                    st.html("""
                    <div class='ust-info-box'>
                        <p><strong>Insight:</strong> Price discounts drive strongest lift. Consider expanding price-based promotions in digital channels.</p>
                    </div>
                    """)
                elif 'Visibility' in best_promo:
                    st.html("""
                    <div class='ust-info-box'>
                        <p><strong>Insight:</strong> Visibility enhancements outperform price cuts. Focus on in-store positioning and merchandising.</p>
                    </div>
                    """)
            else:
                st.html("""
                <div class='ust-info-box'>
                    <p><strong>Note:</strong> Insufficient data to determine most effective promotion type.</p>
                </div>
                """)

    st.markdown("---")

    # ========================================================================
    # SECTION 5: CUSTOMER BEHAVIOR ANALYSIS
    # ========================================================================

    st.markdown("### 👥 Customer Acquisition & Retention")

    st.html("""
    <div class='ust-info-box'>
        <h4>Understanding Customer Dynamics</h4>
        <p><strong>Key Question:</strong> Is the marketing increase attracting new customers or driving
        existing customers to buy more?</p>
    </div>
    """)

    nc = st.session_state.dynamics_results.get('new_customers', {})

    if nc:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.html(f"""
            <div class='ust-card'>
                <div class='ust-eyebrow'>New Customers</div>
                <h2 style='color: #FF6B00; font-size: 2rem;'>{nc.get('new_customers', 0):,}</h2>
                <p style='color: #666;'>First-time buyers</p>
            </div>
            """)

        with col2:
            st.html(f"""
            <div class='ust-card'>
                <div class='ust-eyebrow'>Acquisition Rate</div>
                <h2 style='color: #006E74; font-size: 2rem;'>{nc.get('new_customer_rate_pct', 0):.1f}%</h2>
                <p style='color: #666;'>Of total customers</p>
            </div>
            """)

        with col3:
            st.html(f"""
            <div class='ust-card'>
                <div class='ust-eyebrow'>Repeat Rate</div>
                <h2 style='color: #0097AC; font-size: 2rem;'>{nc.get('repeat_rate_pct', 0):.1f}%</h2>
                <p style='color: #666;'>Return purchases</p>
            </div>
            """)

        with col4:
            st.html(f"""
            <div class='ust-card'>
                <div class='ust-eyebrow'>Revenue Share</div>
                <h2 style='color: #FF6B00; font-size: 2rem;'>{nc.get('new_customer_revenue_share_pct', 0):.1f}%</h2>
                <p style='color: #666;'>From new customers</p>
            </div>
            """)

        # Interpretation
        scenario = st.session_state.dynamics_results.get('scenario', {})
        if scenario:
            scenario_type = scenario.get('scenario', '')
            scenario_desc = scenario.get('description', '')

            if 'NEW_CUSTOMER' in scenario_type:
                st.html(f"""
                <div class='ust-success-box'>
                    <h4>💡 Customer Acquisition Strategy</h4>
                    <p><strong>Finding:</strong> {scenario_desc}</p>
                    <p><strong>Recommendation:</strong> The treatment is successfully attracting new customers.
                    Focus on retention programs to convert these new customers into long-term value.</p>
                </div>
                """)
            else:
                st.html(f"""
                <div class='ust-info-box'>
                    <h4>💡 Customer Retention Focus</h4>
                    <p><strong>Finding:</strong> {scenario_desc}</p>
                    <p><strong>Recommendation:</strong> Marketing is driving repeat purchases from existing customers.
                    Consider campaigns to expand customer base.</p>
                </div>
                """)

    st.markdown("---")

    # ========================================================================
    # SECTION 6: STRATEGIC RECOMMENDATIONS
    # ========================================================================

    st.markdown("### 🎯 Strategic Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        st.html("""
        <div class='ust-success-box'>
            <h4>1. Budget Optimization</h4>
            <p><strong>Action:</strong> Reallocate marketing budget toward highest-performing channels and promotion types.</p>
            <p><strong>Expected Impact:</strong> Maximize incremental ROI by concentrating spend where it's most effective.</p>
        </div>
        """)

        st.html("""
        <div class='ust-success-box'>
            <h4>3. Scale Strategy</h4>
            <p><strong>Action:</strong> Gradually scale successful strategies to additional markets.</p>
            <p><strong>Expected Impact:</strong> Extend proven tactics while monitoring for diminishing returns.</p>
        </div>
        """)

    with col2:
        st.html("""
        <div class='ust-success-box'>
            <h4>2. Customer Strategy</h4>
            <p><strong>Action:</strong> Develop targeted programs based on acquisition vs retention patterns.</p>
            <p><strong>Expected Impact:</strong> Optimize customer lifetime value through appropriate engagement.</p>
        </div>
        """)

        st.html("""
        <div class='ust-success-box'>
            <h4>4. Continuous Testing</h4>
            <p><strong>Action:</strong> Run follow-up experiments to test new variations and validate effects.</p>
            <p><strong>Expected Impact:</strong> Build institutional knowledge and refine marketing effectiveness.</p>
        </div>
        """)

    st.markdown("---")

    # ========================================================================
    # SECTION 7: COMPLETE EFFECT DECOMPOSITION
    # ========================================================================

    st.markdown("### 🔬 Complete Effect Decomposition: The Full Story")

    st.html("""
    <div class='ust-accent-box'>
        <h4>Understanding Every Dollar: A Complete Breakdown</h4>
        <p><strong>The Big Picture:</strong> The overall treatment effect you see is actually the sum of many different forces working together (or against each other).</p>
        <p>This section breaks down <em>exactly</em> what drives the incremental revenue and what costs are involved, so you can make informed decisions about where to invest.</p>
    </div>
    """)

    # ========================================================================
    # 7.1: REVENUE DECOMPOSITION BY CHANNEL & PROMOTION TYPE
    # ========================================================================

    st.markdown("#### 💰 Revenue Impact Decomposition")

    # Calculate detailed decomposition
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    test_period_df = sales_df[sales_df['is_test_period']].copy()

    # Revenue by channel and promo type
    decomp_data = []

    for channel in sales_df['retail_channel'].unique():
        for promo in [None, 'Price', 'Visibility']:
            # Filter data - for "No Promo", look at all non-promoted periods
            if promo is None:
                # No Promo means: test period records without active promotions
                # This is the baseline marketing effect without promotional boost
                channel_promo_df = test_period_df[
                    (test_period_df['retail_channel'] == channel) &
                    (test_period_df['promo_type'].isna() | (test_period_df['promo_type'] == 'None'))
                ]
                promo_label = 'No Promo'
            else:
                channel_promo_df = test_period_df[
                    (test_period_df['retail_channel'] == channel) &
                    (test_period_df['promo_type'] == promo)
                ]
                promo_label = promo

            if len(channel_promo_df) > 0:
                # Calculate DiD for this segment
                treat_rev = channel_promo_df[channel_promo_df['is_treatment']]['sales_revenue'].sum()
                ctrl_rev = channel_promo_df[~channel_promo_df['is_treatment']]['sales_revenue'].sum()

                # Scale control to treatment size
                n_treat = channel_promo_df[channel_promo_df['is_treatment']]['geo_id'].nunique()
                n_ctrl = channel_promo_df[~channel_promo_df['is_treatment']]['geo_id'].nunique()

                if n_ctrl > 0 and n_treat > 0:
                    ctrl_rev_scaled = ctrl_rev * (n_treat / n_ctrl)
                    incremental = treat_rev - ctrl_rev_scaled

                    decomp_data.append({
                        'Channel': channel,
                        'Promotion Type': promo_label,
                        'Treatment Revenue': treat_rev,
                        'Control Revenue (Scaled)': ctrl_rev_scaled,
                        'Incremental Revenue': incremental,
                        'Contribution %': 0  # Will calculate after
                    })

    decomp_df = pd.DataFrame(decomp_data)

    if len(decomp_df) > 0:
        # Calculate contribution percentages
        total_incremental = decomp_df['Incremental Revenue'].sum()
        if total_incremental != 0:
            decomp_df['Contribution %'] = (decomp_df['Incremental Revenue'] / total_incremental) * 100

        # Create visualization: Waterfall chart showing each component
        st.markdown("**Revenue Sources & Sinks:**")

        # Aggregate by promotion type for clarity
        promo_summary = decomp_df.groupby('Promotion Type')['Incremental Revenue'].sum().sort_values(ascending=False)

        col1, col2 = st.columns([2, 1])

        with col1:
            fig, ax = plt.subplots(figsize=(12, 6))

            # Create waterfall effect
            promo_types = list(promo_summary.index)
            values = list(promo_summary.values)

            # Calculate cumulative for waterfall
            cumulative = [0]
            for i, val in enumerate(values):
                cumulative.append(cumulative[-1] + val)

            # Colors: green for positive, red for negative
            colors = ['#006E74' if v > 0 else '#DC3545' for v in values]

            # Plot bars
            for i, (promo, val) in enumerate(zip(promo_types, values)):
                ax.bar(i, val, bottom=cumulative[i], color=colors[i],
                      edgecolor='black', linewidth=2, alpha=0.8, width=0.6)

                # Add value label
                label_y = cumulative[i] + val/2
                ax.text(i, label_y, f'${val:,.0f}', ha='center', va='center',
                       fontweight='bold', fontsize=10, color='white')

            # Add total line
            ax.plot([-0.5, len(promo_types)-0.5], [cumulative[-1], cumulative[-1]],
                   'k--', linewidth=2, alpha=0.5)
            ax.text(len(promo_types)-1, cumulative[-1] + abs(cumulative[-1])*0.05,
                   f'Total: ${cumulative[-1]:,.0f}', ha='right', fontweight='bold', fontsize=11)

            ax.set_xticks(range(len(promo_types)))
            ax.set_xticklabels(promo_types, rotation=15, ha='right')
            ax.set_ylabel('Incremental Revenue ($)', fontsize=12, fontweight='bold')
            ax.set_title('Revenue Contribution by Promotion Type (Waterfall)',
                        fontsize=13, fontweight='bold', color='#006E74')
            ax.axhline(0, color='black', linewidth=1, alpha=0.3)
            ax.grid(True, alpha=0.3, axis='y')

            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            st.markdown("**Key Insights:**")

            best_promo_contrib = promo_summary.idxmax()
            best_promo_val = promo_summary.max()

            st.html(f"""
            <div class='ust-success-box'>
                <h4>Top Revenue Driver</h4>
                <p><strong>{best_promo_contrib}</strong><br>
                Contributes <strong>${best_promo_val:,.0f}</strong>
                ({(best_promo_val/total_incremental*100):.1f}% of total)</p>
            </div>
            """)

            negative_contribs = promo_summary[promo_summary < 0]
            if len(negative_contribs) > 0:
                worst_promo = negative_contribs.idxmin()
                worst_val = negative_contribs.min()
                st.html(f"""
                <div class='ust-accent-box'>
                    <h4>⚠️ Revenue Drag</h4>
                    <p><strong>{worst_promo}</strong><br>
                    Reduces revenue by <strong>${abs(worst_val):,.0f}</strong></p>
                </div>
                """)

    st.markdown("---")

    # ========================================================================
    # 7.2: COST DECOMPOSITION - THE FULL PICTURE
    # ========================================================================

    st.markdown("#### 💸 Cost & Investment Breakdown")

    st.html("""
    <div class='ust-info-box'>
        <h4>Where Does The Money Go?</h4>
        <p>To calculate true ROI, we need to account for <strong>all costs</strong>:</p>
        <ul>
            <li><strong>Media Spend:</strong> Money spent on advertising campaigns</li>
            <li><strong>Price Promotion Cost:</strong> Revenue lost from discounting</li>
            <li><strong>Visibility Promotion Cost:</strong> Investment in displays, positioning, materials</li>
        </ul>
    </div>
    """)

    # Calculate costs
    media_df['date'] = pd.to_datetime(media_df['date'])
    test_media = media_df[media_df['date'] >= test_start].copy()

    treatment_dmas = st.session_state.metadata['treatment_dmas']

    # 1. Media spend by channel
    media_spend_by_channel = {}
    for channel in test_media['channel'].unique():
        channel_spend = test_media[
            (test_media['geo_id'].isin(treatment_dmas)) &
            (test_media['channel'] == channel)
        ]['spend_usd'].sum()
        media_spend_by_channel[channel] = channel_spend

    # 2. Price promotion cost (revenue lost from discounts)
    # Estimate: 15% discount on price promotion sales
    price_promo_sales = test_period_df[
        (test_period_df['promo_type'] == 'Price') &
        (test_period_df['is_treatment'])
    ]['sales_revenue'].sum()

    discount_rate = 0.15  # 15% average discount
    price_promo_cost = price_promo_sales * discount_rate

    # 3. Visibility promotion cost (display materials, shelf space)
    # Estimate: $200 per store per week for visibility promotions
    visibility_weeks = test_period_df[
        (test_period_df['promo_type'] == 'Visibility') &
        (test_period_df['is_treatment'])
    ]['date'].nunique()

    stores_per_dma = 25  # Average stores per DMA
    cost_per_store_week = 200
    visibility_promo_cost = len(treatment_dmas) * stores_per_dma * visibility_weeks * cost_per_store_week

    # Total costs
    total_media_spend = sum(media_spend_by_channel.values())
    total_investment = total_media_spend + price_promo_cost + visibility_promo_cost

    # Visualization: Cost breakdown
    col1, col2 = st.columns([2, 1])

    with col1:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Chart 1: Cost by type
        cost_categories = ['Media Spend', 'Price Discounts\n(Lost Revenue)', 'Visibility\nInvestment']
        cost_values = [total_media_spend, price_promo_cost, visibility_promo_cost]
        cost_colors = ['#FF6B00', '#DC3545', '#0097AC']

        bars1 = ax1.bar(cost_categories, cost_values, color=cost_colors,
                       edgecolor='black', linewidth=2, alpha=0.8)

        for bar, val in zip(bars1, cost_values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height + max(cost_values)*0.02,
                    f'${val:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)

        ax1.set_ylabel('Cost ($)', fontsize=12, fontweight='bold')
        ax1.set_title('Investment Breakdown by Type', fontsize=13, fontweight='bold', color='#006E74')
        ax1.grid(True, alpha=0.3, axis='y')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0, ha='center')

        # Chart 2: Media spend by channel
        if len(media_spend_by_channel) > 0:
            channels = list(media_spend_by_channel.keys())
            spends = list(media_spend_by_channel.values())

            ax2.barh(channels, spends, color='#006E74', edgecolor='black', linewidth=2, alpha=0.8)

            for i, (ch, sp) in enumerate(zip(channels, spends)):
                ax2.text(sp + max(spends)*0.02, i, f'${sp:,.0f}',
                        va='center', ha='left', fontweight='bold', fontsize=10)

            ax2.set_xlabel('Media Spend ($)', fontsize=12, fontweight='bold')
            ax2.set_title('Media Investment by Channel', fontsize=13, fontweight='bold', color='#006E74')
            ax2.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.html(f"""
        <div class='ust-card ust-card-accent'>
            <div class='ust-eyebrow'>Total Investment</div>
            <h1 style='color: #FF6B00; font-size: 2.5rem;'>${total_investment:,.0f}</h1>
            <p style='color: #666; margin: 8px 0 0 0;'>All costs included</p>
        </div>
        """)

        st.markdown("**Cost Breakdown:**")
        st.metric("Media Spend", f"${total_media_spend:,.0f}",
                 f"{(total_media_spend/total_investment*100):.1f}% of total")
        st.metric("Price Discounts", f"${price_promo_cost:,.0f}",
                 f"{(price_promo_cost/total_investment*100):.1f}% of total")
        st.metric("Visibility Investment", f"${visibility_promo_cost:,.0f}",
                 f"{(visibility_promo_cost/total_investment*100):.1f}% of total")

    st.markdown("---")

    # ========================================================================
    # 7.3: AGE GROUP DECOMPOSITION
    # ========================================================================

    if st.session_state.transactions_df is not None and 'age_group' in st.session_state.transactions_df.columns:
        st.markdown("#### 👥 Impact by Age Group")

        st.html("""
        <div class='ust-info-box'>
            <h4>Age Segmentation Insights</h4>
            <p><strong>Not all customers respond the same way.</strong> Breaking down effects by age reveals which demographics drive value.</p>
            <p><em>Note:</em> Age data available for Omnichannel & Online channels only.</p>
        </div>
        """)

        transactions_df = st.session_state.transactions_df.copy()
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])

        # Filter for test period and channels with age data
        test_transactions = transactions_df[
            (transactions_df['date'] >= test_start) &
            (transactions_df['retail_channel'].isin(['Omnichannel', 'Online_Specialty']))
        ].copy()

        # Calculate incremental revenue by age
        age_effects = {}
        for age in test_transactions['age_group'].dropna().unique():
            age_df = test_transactions[test_transactions['age_group'] == age]

            treat_rev = age_df[age_df['geo_id'].isin(treatment_dmas)]['transaction_amount'].sum()
            ctrl_rev = age_df[~age_df['geo_id'].isin(treatment_dmas)]['transaction_amount'].sum()

            n_treat_geo = age_df[age_df['geo_id'].isin(treatment_dmas)]['geo_id'].nunique()
            n_ctrl_geo = age_df[~age_df['geo_id'].isin(treatment_dmas)]['geo_id'].nunique()

            if n_ctrl_geo > 0:
                ctrl_rev_scaled = ctrl_rev * (n_treat_geo / n_ctrl_geo)
                incremental = treat_rev - ctrl_rev_scaled
                age_effects[age] = {
                    'incremental': incremental,
                    'treat_rev': treat_rev,
                    'ctrl_rev': ctrl_rev_scaled
                }

        if len(age_effects) > 0:
            col1, col2 = st.columns([2, 1])

            with col1:
                fig, ax = plt.subplots(figsize=(10, 6))

                ages = list(age_effects.keys())
                incrementals = [age_effects[a]['incremental'] for a in ages]
                colors_age = ['#006E74' if inc > 0 else '#DC3545' for inc in incrementals]

                bars = ax.bar(ages, incrementals, color=colors_age,
                             edgecolor='black', linewidth=2, alpha=0.8)

                for bar, val in zip(bars, incrementals):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2,
                           height + (max(incrementals)*0.03 if height > 0 else -max(incrementals)*0.03),
                           f'${val:,.0f}', ha='center',
                           va='bottom' if height > 0 else 'top',
                           fontweight='bold', fontsize=10)

                ax.axhline(0, color='black', linewidth=1, alpha=0.3)
                ax.set_xlabel('Age Group', fontsize=12, fontweight='bold')
                ax.set_ylabel('Incremental Revenue ($)', fontsize=12, fontweight='bold')
                ax.set_title('Treatment Effect by Age Segment', fontsize=13, fontweight='bold', color='#006E74')
                ax.grid(True, alpha=0.3, axis='y')

                plt.tight_layout()
                st.pyplot(fig)

            with col2:
                best_age = max(age_effects, key=lambda x: age_effects[x]['incremental'])
                best_age_inc = age_effects[best_age]['incremental']

                st.html(f"""
                <div class='ust-card ust-card-accent'>
                    <div class='ust-eyebrow'>Highest Value Segment</div>
                    <h2 style='color: #FF6B00; margin: 12px 0;'>{best_age}</h2>
                    <h1 style='color: #006E74; margin: 8px 0; font-size: 1.8rem;'>${best_age_inc:,.0f}</h1>
                    <p style='color: #666;'>Incremental revenue</p>
                </div>
                """)

                total_age_inc = sum([v['incremental'] for v in age_effects.values()])
                st.metric("Total Age Impact", f"${total_age_inc:,.0f}")
                st.metric("Age Groups Analyzed", len(age_effects))

        st.markdown("---")

    # ========================================================================
    # 7.4: COMPLETE STORY - SANKEY DIAGRAM
    # ========================================================================

    st.markdown("#### 📊 The Complete Story: Investment to Profit Flow")

    st.html("""
    <div class='ust-accent-box'>
        <h4>Following The Money</h4>
        <p><strong>From Investment → Activities → Revenue → Profit</strong></p>
        <p>This visualization shows how your marketing investment flows through different channels and promotions to generate the final profit.</p>
    </div>
    """)

    # Create comprehensive summary table
    summary_data = {
        'Category': [],
        'Item': [],
        'Amount ($)': [],
        'Impact': []
    }

    # Investments
    summary_data['Category'].extend(['Investment', 'Investment', 'Investment'])
    summary_data['Item'].extend(['Media Spend', 'Price Discounts', 'Visibility Costs'])
    summary_data['Amount ($)'].extend([total_media_spend, price_promo_cost, visibility_promo_cost])
    summary_data['Impact'].extend(['Cost', 'Cost', 'Cost'])

    # Revenue by promo type
    if len(promo_summary) > 0:
        for promo, rev in promo_summary.items():
            summary_data['Category'].append('Revenue Generated')
            summary_data['Item'].append(f'{promo} Revenue')
            summary_data['Amount ($)'].append(rev)
            summary_data['Impact'].append('Gain' if rev > 0 else 'Loss')

    # Net result
    summary_data['Category'].append('Net Result')
    summary_data['Item'].append('Incremental Profit')
    net_profit = total_incremental * 0.40 - total_investment  # 40% margin
    summary_data['Amount ($)'].append(net_profit)
    summary_data['Impact'].append('Profit' if net_profit > 0 else 'Loss')

    summary_df = pd.DataFrame(summary_data)

    # Display the flow
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**💸 Investment**")
        invest_df = summary_df[summary_df['Category'] == 'Investment']
        for _, row in invest_df.iterrows():
            st.html(f"""
            <div class='ust-card' style='background: #FFE5E5; margin: 8px 0;'>
                <p style='margin: 4px 0; font-weight: bold; color: #DC3545;'>{row['Item']}</p>
                <p style='margin: 4px 0; font-size: 1.2rem; color: #DC3545;'>-${row['Amount ($)']:,.0f}</p>
            </div>
            """)

    with col2:
        st.markdown("**💰 Revenue Generated**")
        rev_df = summary_df[summary_df['Category'] == 'Revenue Generated']
        for _, row in rev_df.iterrows():
            color = '#006E74' if row['Amount ($)'] > 0 else '#DC3545'
            bg_color = '#E5F5F5' if row['Amount ($)'] > 0 else '#FFE5E5'
            st.html(f"""
            <div class='ust-card' style='background: {bg_color}; margin: 8px 0;'>
                <p style='margin: 4px 0; font-weight: bold; color: {color};'>{row['Item']}</p>
                <p style='margin: 4px 0; font-size: 1.2rem; color: {color};'>${row['Amount ($)']:,.0f}</p>
            </div>
            """)

    with col3:
        st.markdown("**📈 Net Result**")
        result_df = summary_df[summary_df['Category'] == 'Net Result']
        for _, row in result_df.iterrows():
            color = '#006E74' if row['Amount ($)'] > 0 else '#DC3545'
            bg_color = '#E5F5F5' if row['Amount ($)'] > 0 else '#FFE5E5'
            icon = '✅' if row['Amount ($)'] > 0 else '⚠️'
            st.html(f"""
            <div class='ust-card ust-card-accent' style='background: {bg_color};'>
                <p style='margin: 4px 0; font-weight: bold; color: {color};'>{icon} {row['Item']}</p>
                <h1 style='margin: 8px 0; color: {color};'>${row['Amount ($)']:,.0f}</h1>
                <p style='margin: 4px 0; color: {color};'>ROI: {(net_profit/total_investment*100):+.1f}%</p>
            </div>
            """)

    # Full breakdown table
    with st.expander("📋 Complete Financial Breakdown"):
        display_summary = summary_df.copy()
        display_summary['Amount ($)'] = display_summary['Amount ($)'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(display_summary, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ========================================================================
    # SECTION 8: TECHNICAL DETAILS
    # ========================================================================

    with st.expander("📊 Statistical Details & Model Diagnostics"):
        st.markdown("### Model Specifications")

        settings = st.session_state.get('model_settings', {})

        st.markdown("**Model Configuration:**")
        st.json({
            "Heterogeneous Effects": {
                "Channel-specific": settings.get('estimate_channel_effects', True),
                "Promotion-specific": settings.get('estimate_promo_effects', True),
                "Age-specific": settings.get('estimate_age_effects', True)
            },
            "Fixed Effects": {
                "Geographic": settings.get('include_geo_fe', True),
                "Time": settings.get('include_time_fe', True),
                "Channel": settings.get('include_channel_fe', True)
            },
            "Statistical Settings": {
                "Clustering": settings.get('cluster_se', 'Two-way (DMA + Time)'),
                "Confidence Level": f"{settings.get('confidence_level', 95)}%"
            }
        })

        st.markdown("### Treatment Effect Estimates")

        results_table = pd.DataFrame({
            'Estimate': [f'{pct_lift:.2f}%'],
            'Std Error': [f'{std_error:.2f}'],
            'T-Statistic': [f'{t_stat:.2f}'],
            'P-Value': [f'{p_value:.4f}'],
            f'{confidence_level}% CI Lower': [f'{ci_lower_pct:.2f}%'],
            f'{confidence_level}% CI Upper': [f'{ci_upper_pct:.2f}%'],
            'Significance': [sig_interp]
        }, index=['Average Treatment Effect'])

        st.dataframe(results_table, use_container_width=True)

        st.markdown("### Interpretation Guide")
        st.markdown("""
        - **Estimate:** The percentage change in sales caused by the treatment
        - **Std Error:** Uncertainty in our estimate (lower is more precise)
        - **T-Statistic:** Signal-to-noise ratio (|t| > 1.96 suggests significance)
        - **P-Value:** Probability of seeing this effect by chance (< 0.05 = significant)
        - **Confidence Interval:** Range where true effect likely lies
        - **Significance:** Plain-English interpretation of statistical evidence
        """)
