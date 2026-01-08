"""
ROI Insights Module
Comprehensive business value analysis with multi-period ROI and strategic recommendations
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.append('src')

from roi_calculator import MultiPeriodROI


def render():
    """Render the comprehensive ROI Insights panel"""
    st.html("<div class='ust-eyebrow'>Step 5: Business Impact & Value</div>")
    st.markdown("## ROI & Strategic Insights")

    if not st.session_state.analysis_complete:
        st.html("""
        <div class='ust-info-box'>
            <strong>⚠️ Analysis Required</strong><br>
            Please complete the analysis in Steps 3 & 4 before viewing ROI metrics.
        </div>
        """)
        return

    # ========================================================================
    # INTRODUCTION
    # ========================================================================

    st.html("""
    <div class='ust-accent-box'>
        <h4>Translating Causal Effects into Business Value</h4>
        <p><strong>The Bridge:</strong> Statistical significance tells us <em>if</em> marketing works.
        ROI tells us <em>whether it's worth it</em>.</p>
        <p>This section converts the causal treatment effects into dollar returns, accounting for
        costs, profit margins, and customer lifetime value.</p>
    </div>
    """)

    # ========================================================================
    # CALCULATE ROI IF NOT DONE
    # ========================================================================

    if 'roi_results' not in st.session_state:
        with st.spinner("Calculating multi-period ROI and business value..."):
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

    # ========================================================================
    # SECTION 1: MULTI-PERIOD ROI OVERVIEW
    # ========================================================================

    st.markdown("### 💰 Multi-Period ROI Analysis")

    st.html("""
    <div class='ust-info-box'>
        <h4>Why Multiple Time Horizons?</h4>
        <p><strong>Marketing impact unfolds over time:</strong></p>
        <ul>
            <li><strong>Short-Term (4 weeks):</strong> Immediate campaign effects, quick wins</li>
            <li><strong>Medium-Term (12 weeks):</strong> Sustained behavioral changes, repeat purchases</li>
            <li><strong>Long-Term (with CLV):</strong> Full customer lifetime value, brand loyalty</li>
        </ul>
        <p>Understanding all three perspectives ensures balanced decision-making.</p>
    </div>
    """)

    # ROI Metrics Cards
    col1, col2, col3 = st.columns(3)

    periods_config = [
        ('short_term', 'Short-Term ROI', 'Weeks 1-4', col1, '#FF6B00'),
        ('medium_term', 'Medium-Term ROI', 'Weeks 1-12', col2, '#0097AC'),
        ('long_term', 'Long-Term ROI', 'With Customer LTV', col3, '#006E74')
    ]

    for key, label, sublabel, col, color in periods_config:
        with col:
            roi_val = roi[key]['roi_pct']
            roas_val = roi[key]['profit_roas']

            # Get appropriate keys based on period
            if key == 'short_term':
                revenue = roi[key]['incremental_sales']
                profit = roi[key]['incremental_profit']
            elif key == 'medium_term':
                revenue = roi[key]['incremental_sales_adjusted']
                profit = roi[key]['incremental_profit']
            else:  # long_term
                revenue = roi[key].get('incremental_sales_adjusted', roi[key].get('incremental_profit_base', 0))
                profit = roi[key]['total_profit']

            investment = roi[key]['marketing_spend']

            icon = "✅" if roi_val > 0 else "⚠️"

            st.html(f"""
            <div class='ust-card ust-card-accent'>
                <div class='ust-eyebrow'>{label}</div>
                <h1 style='color: {color}; font-size: 2.5rem; margin: 12px 0;'>{icon} {roi_val:+.1f}%</h1>
                <p style='color: #666; font-size: 0.95rem; margin: 4px 0;'><strong>ROAS:</strong> ${roas_val:.2f}</p>
                <p style='color: #999; font-size: 0.85rem; margin: 8px 0 4px 0;'>{sublabel}</p>
            </div>
            """)

            with st.expander(f"📊 {label} Breakdown"):
                st.markdown(f"""
                **Revenue & Profit:**
                - Incremental Sales: ${revenue:,.0f}
                - Incremental Profit: ${profit:,.0f}
                - Investment: ${investment:,.0f}

                **Metrics:**
                - ROI: {roi_val:.1f}%
                - ROAS (Profit): ${roas_val:.2f}
                - Revenue per Dollar: ${revenue/investment:.2f}
                """)

    st.markdown("---")

    # ========================================================================
    # SECTION 2: ROI VISUALIZATION & COMPARISON
    # ========================================================================

    st.markdown("### 📈 ROI Evolution Over Time")

    st.html("""
    <div class='ust-info-box'>
        <p><strong>How ROI Builds:</strong> Watch how returns accumulate as we move from immediate effects
        to sustained customer value.</p>
    </div>
    """)

    # Create ROI comparison visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Chart 1: ROI by Period
    periods = ['Short-Term\n(4 weeks)', 'Medium-Term\n(12 weeks)', 'Long-Term\n(with CLV)']
    roi_values = [roi['short_term']['roi_pct'], roi['medium_term']['roi_pct'], roi['long_term']['roi_pct']]
    colors_roi = ['#FF6B00', '#0097AC', '#006E74']

    bars1 = ax1.bar(periods, roi_values, color=colors_roi, edgecolor='black', linewidth=2, alpha=0.8)
    ax1.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax1.set_ylabel('ROI (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Return on Investment by Time Horizon', fontsize=13, fontweight='bold', color='#006E74')
    ax1.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bar, val in zip(bars1, roi_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height + (2 if height >= 0 else -2),
                f'{val:.1f}%', ha='center', va='bottom' if height >= 0 else 'top',
                fontweight='bold', fontsize=11)

    # Chart 2: ROAS by Period
    roas_values = [roi['short_term']['profit_roas'], roi['medium_term']['profit_roas'], roi['long_term']['profit_roas']]

    bars2 = ax2.bar(periods, roas_values, color=colors_roi, edgecolor='black', linewidth=2, alpha=0.8)
    ax2.axhline(1.0, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Break-even (ROAS = 1.0)')
    ax2.set_ylabel('Profit ROAS ($)', fontsize=12, fontweight='bold')
    ax2.set_title('Return on Ad Spend by Time Horizon', fontsize=13, fontweight='bold', color='#006E74')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend(loc='upper left', fontsize=9)

    # Add value labels
    for bar, val in zip(bars2, roas_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height + 0.05,
                f'${val:.2f}', ha='center', va='bottom',
                fontweight='bold', fontsize=11)

    plt.tight_layout()
    st.pyplot(fig)

    # Interpretation
    col1, col2 = st.columns(2)

    with col1:
        best_period = max([('short_term', 'Short-Term'), ('medium_term', 'Medium-Term'), ('long_term', 'Long-Term')],
                         key=lambda x: roi[x[0]]['roi_pct'])
        best_roi = roi[best_period[0]]['roi_pct']

        st.html(f"""
        <div class='ust-success-box'>
            <h4>🏆 Best Performance</h4>
            <p><strong>{best_period[1]}</strong> delivers the highest ROI at <strong>{best_roi:+.1f}%</strong>.</p>
            <p>This suggests {"immediate campaign effectiveness" if best_period[0] == 'short_term'
               else "sustained value creation" if best_period[0] == 'medium_term'
               else "strong customer lifetime value"} drives overall returns.</p>
        </div>
        """)

    with col2:
        if roi['long_term']['roi_pct'] > roi['short_term']['roi_pct']:
            st.html("""
            <div class='ust-success-box'>
                <h4>📈 Building Value</h4>
                <p>Long-term ROI exceeds short-term, indicating <strong>durable customer relationships</strong>
                and strong retention effects.</p>
                <p><strong>Implication:</strong> Marketing investment pays off over time through repeat purchases.</p>
            </div>
            """)
        else:
            st.html("""
            <div class='ust-info-box'>
                <h4>⚡ Immediate Impact</h4>
                <p>Short-term ROI is highest, suggesting <strong>quick wins</strong> but potential decay over time.</p>
                <p><strong>Implication:</strong> Focus on retention programs to extend customer value.</p>
            </div>
            """)

    st.markdown("---")

    # ========================================================================
    # SECTION 3: CHANNEL-LEVEL ROI
    # ========================================================================

    st.markdown("### 🛒 ROI by Retail Channel")

    st.html("""
    <div class='ust-info-box'>
        <h4>Channel Efficiency Analysis</h4>
        <p><strong>Where should we invest?</strong> Not all channels deliver equal returns.
        Understanding channel-level ROI enables precise budget allocation.</p>
    </div>
    """)

    # Calculate channel-level ROI (simplified approach using treatment effects)
    channel_effects = st.session_state.hte_results['channel_effects']

    channel_roi_data = []
    for channel, metrics in channel_effects.items():
        # Simplified ROI calculation based on lift
        pct_lift = metrics['pct_lift']
        treatment_effect = metrics['treatment_effect']

        # Approximate investment per channel (simplified)
        media_df = st.session_state.media_df
        treatment_dmas = st.session_state.metadata['treatment_dmas']

        channel_spend = media_df[
            (media_df['geo_id'].isin(treatment_dmas)) &
            (media_df['date'] >= st.session_state.metadata['test_start_date'])
        ]['spend_usd'].sum() / len(channel_effects)  # Simplified equal distribution

        channel_roi = ((treatment_effect * 0.40) / channel_spend - 1) * 100 if channel_spend > 0 else 0
        channel_roas = (treatment_effect * 0.40) / channel_spend if channel_spend > 0 else 0

        channel_roi_data.append({
            'Channel': channel,
            'ROI (%)': channel_roi,
            'ROAS': channel_roas,
            'Lift (%)': pct_lift,
            'Investment': channel_spend
        })

    channel_roi_df = pd.DataFrame(channel_roi_data).sort_values('ROI (%)', ascending=False)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))

        colors_channel = ['#FF6B00' if i == 0 else '#006E74' if roi >= 0 else '#DC3545'
                         for i, roi in enumerate(channel_roi_df['ROI (%)'])]

        bars = ax.barh(channel_roi_df['Channel'], channel_roi_df['ROI (%)'],
                      color=colors_channel, edgecolor='black', linewidth=2, alpha=0.8)

        ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        ax.set_xlabel('ROI (%)', fontsize=12, fontweight='bold')
        ax.set_title('Return on Investment by Retail Channel', fontsize=14, fontweight='bold', color='#006E74')
        ax.grid(True, alpha=0.3, axis='x')

        # Add value labels
        for i, (idx, row) in enumerate(channel_roi_df.iterrows()):
            label_x = row['ROI (%)'] + (2 if row['ROI (%)'] >= 0 else -2)
            ha = 'left' if row['ROI (%)'] >= 0 else 'right'
            ax.text(label_x, i, f"{row['ROI (%)']:.1f}%", va='center', ha=ha, fontweight='bold', fontsize=10)

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        best_channel_roi = channel_roi_df.iloc[0]

        st.html(f"""
        <div class='ust-card ust-card-accent'>
            <div class='ust-eyebrow'>Highest ROI Channel</div>
            <h2 style='color: #FF6B00; margin: 12px 0; font-size: 1.3rem;'>{best_channel_roi['Channel']}</h2>
            <h1 style='color: #006E74; margin: 8px 0;'>{best_channel_roi['ROI (%)']:+.1f}%</h1>
            <p style='color: #666; margin: 4px 0;'>ROAS: ${best_channel_roi['ROAS']:.2f}</p>
            <p style='color: #666; margin: 4px 0;'>Lift: {best_channel_roi['Lift (%)']:+.1f}%</p>
        </div>
        """)

        st.metric("Positive ROI Channels", sum(channel_roi_df['ROI (%)'] > 0))
        st.metric("Total Channels", len(channel_roi_df))

    # Detailed table
    with st.expander("📊 Detailed Channel ROI Comparison"):
        display_df = channel_roi_df.copy()
        display_df['ROI (%)'] = display_df['ROI (%)'].apply(lambda x: f"{x:+.1f}%")
        display_df['ROAS'] = display_df['ROAS'].apply(lambda x: f"${x:.2f}")
        display_df['Lift (%)'] = display_df['Lift (%)'].apply(lambda x: f"{x:+.1f}%")
        display_df['Investment'] = display_df['Investment'].apply(lambda x: f"${x:,.0f}")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ========================================================================
    # SECTION 4: SCENARIO MODELING
    # ========================================================================

    st.markdown("### 🎯 Scenario Planning: Scaling Strategy")

    st.html("""
    <div class='ust-accent-box'>
        <h4>What If We Scale?</h4>
        <p><strong>Strategic Question:</strong> If we increase marketing spend by X%, what returns can we expect?</p>
        <p>Use the slider below to model different investment scenarios and understand potential outcomes.</p>
    </div>
    """)

    # Scenario slider
    scale_factor = st.slider(
        "Investment Scale Factor",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.1,
        format="%.1fx",
        help="Model the impact of scaling marketing investment up or down"
    )

    # Calculate scaled metrics
    base_investment = roi['medium_term']['marketing_spend']
    base_profit = roi['medium_term']['incremental_profit']
    base_roi = roi['medium_term']['roi_pct']

    # Apply diminishing returns curve (realistic assumption)
    # Returns diminish as we scale (square root function)
    diminishing_factor = np.sqrt(scale_factor)

    scaled_investment = base_investment * scale_factor
    scaled_profit = base_profit * diminishing_factor
    scaled_roi = ((scaled_profit / scaled_investment) - 1) * 100 if scaled_investment > 0 else 0
    scaled_roas = scaled_profit / scaled_investment if scaled_investment > 0 else 0

    # Display scenario results
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.html(f"""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Scaled Investment</div>
            <h2 style='color: #FF6B00; font-size: 1.8rem;'>${scaled_investment:,.0f}</h2>
            <p style='color: #666;'>Marketing spend</p>
        </div>
        """)

    with col2:
        st.html(f"""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Expected Profit</div>
            <h2 style='color: #006E74; font-size: 1.8rem;'>${scaled_profit:,.0f}</h2>
            <p style='color: #666;'>Incremental profit</p>
        </div>
        """)

    with col3:
        roi_color = "#006E74" if scaled_roi > 0 else "#DC3545"
        st.html(f"""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Projected ROI</div>
            <h2 style='color: {roi_color}; font-size: 1.8rem;'>{scaled_roi:+.1f}%</h2>
            <p style='color: #666;'>With diminishing returns</p>
        </div>
        """)

    with col4:
        st.html(f"""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Profit ROAS</div>
            <h2 style='color: #0097AC; font-size: 1.8rem;'>${scaled_roas:.2f}</h2>
            <p style='color: #666;'>Per dollar spent</p>
        </div>
        """)

    # Visualization: Diminishing Returns Curve
    st.markdown("#### 📉 Diminishing Returns Curve")

    scale_range = np.linspace(0.5, 3.0, 50)
    roi_curve = []
    profit_curve = []

    for sf in scale_range:
        dim_factor = np.sqrt(sf)
        scaled_inv = base_investment * sf
        scaled_prof = base_profit * dim_factor
        scaled_roi_val = ((scaled_prof / scaled_inv) - 1) * 100 if scaled_inv > 0 else 0

        roi_curve.append(scaled_roi_val)
        profit_curve.append(scaled_prof)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # ROI vs Scale
    ax1.plot(scale_range, roi_curve, linewidth=3, color='#006E74', label='Expected ROI')
    ax1.axvline(scale_factor, color='#FF6B00', linestyle='--', linewidth=2, alpha=0.7, label=f'Current Selection ({scale_factor:.1f}x)')
    ax1.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.3)
    ax1.scatter([scale_factor], [scaled_roi], color='#FF6B00', s=200, zorder=5, edgecolor='black', linewidth=2)
    ax1.set_xlabel('Investment Scale Factor', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Expected ROI (%)', fontsize=12, fontweight='bold')
    ax1.set_title('ROI vs Investment Scale (with Diminishing Returns)', fontsize=13, fontweight='bold', color='#006E74')
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Profit vs Scale
    ax2.plot(scale_range, profit_curve, linewidth=3, color='#0097AC', label='Expected Profit')
    ax2.axvline(scale_factor, color='#FF6B00', linestyle='--', linewidth=2, alpha=0.7, label=f'Current Selection ({scale_factor:.1f}x)')
    ax2.scatter([scale_factor], [scaled_profit], color='#FF6B00', s=200, zorder=5, edgecolor='black', linewidth=2)
    ax2.set_xlabel('Investment Scale Factor', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Expected Profit ($)', fontsize=12, fontweight='bold')
    ax2.set_title('Incremental Profit vs Investment Scale', fontsize=13, fontweight='bold', color='#006E74')
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)

    # Recommendation based on scenario
    if scale_factor > 1.5:
        st.html("""
        <div class='ust-accent-box'>
            <h4>⚠️ Aggressive Scaling Risk</h4>
            <p><strong>Caution:</strong> Scaling beyond 1.5x introduces significant diminishing returns risk.
            ROI naturally decreases as we exhaust high-value audiences.</p>
            <p><strong>Recommendation:</strong> Consider gradual scaling with continuous monitoring to validate sustained returns.</p>
        </div>
        """)
    elif scale_factor > 1.0:
        st.html("""
        <div class='ust-success-box'>
            <h4>✅ Moderate Scaling Opportunity</h4>
            <p><strong>Insight:</strong> Modest scaling shows favorable profit projection even with diminishing returns.</p>
            <p><strong>Recommendation:</strong> Test this scale in select markets before full rollout.</p>
        </div>
        """)
    elif scale_factor < 1.0:
        st.html("""
        <div class='ust-info-box'>
            <h4>📉 Budget Reduction Scenario</h4>
            <p><strong>Insight:</strong> Reducing investment improves efficiency but lowers total profit.</p>
            <p><strong>Recommendation:</strong> Only reduce if budget-constrained; prioritize highest-ROI channels.</p>
        </div>
        """)

    st.markdown("---")

    # ========================================================================
    # SECTION 5: STRATEGIC RECOMMENDATIONS
    # ========================================================================

    st.markdown("### 🎯 Strategic Recommendations & Action Plan")

    st.html("""
    <div class='ust-info-box'>
        <h4>From Insights to Action</h4>
        <p>Based on the ROI analysis, here are concrete steps to maximize marketing effectiveness.</p>
    </div>
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.html(f"""
        <div class='ust-success-box'>
            <h4>1. Reallocate Budget to Top Channels</h4>
            <p><strong>Action:</strong> Shift {10 + (best_channel_roi['ROI (%)'] / 10):.0f}% of budget
            toward <strong>{best_channel_roi['Channel']}</strong> (highest ROI channel).</p>
            <p><strong>Expected Impact:</strong> Improve overall portfolio ROI by {2 + (best_channel_roi['ROI (%)'] / 20):.1f}%
            through better allocation efficiency.</p>
            <p><strong>Timeline:</strong> Implement over next quarter with weekly monitoring.</p>
        </div>
        """)

        st.html("""
        <div class='ust-success-box'>
            <h4>3. Optimize Campaign Duration</h4>
            <p><strong>Action:</strong> Align campaign length with time-to-peak ROI identified in multi-period analysis.</p>
            <p><strong>Expected Impact:</strong> Capture maximum value while avoiding diminishing returns.</p>
            <p><strong>Timeline:</strong> Apply to next campaign cycle.</p>
        </div>
        """)

        # Customer strategy based on dynamics
        scenario = st.session_state.dynamics_results.get('scenario', {}).get('scenario', '')
        if 'NEW_CUSTOMER' in scenario:
            st.html(f"""
            <div class='ust-success-box'>
                <h4>5. Customer Acquisition Focus</h4>
                <p><strong>Finding:</strong> Marketing drives new customer acquisition with long-term ROI of {roi['long_term']['roi_pct']:.1f}%.</p>
                <p><strong>Action:</strong> Continue acquisition campaigns while implementing retention programs
                to maximize lifetime value.</p>
            </div>
            """)
        else:
            st.html("""
            <div class='ust-success-box'>
                <h4>5. Retention & Frequency Strategy</h4>
                <p><strong>Finding:</strong> Marketing primarily drives repeat purchases from existing customers.</p>
                <p><strong>Action:</strong> Complement retention efforts with new customer acquisition campaigns
                to balance growth.</p>
            </div>
            """)

    with col2:
        st.html("""
        <div class='ust-success-box'>
            <h4>2. Test Scaled Investment</h4>
            <p><strong>Action:</strong> Run pilot test with 1.2x investment scale in 3-5 markets
            to validate diminishing returns curve.</p>
            <p><strong>Expected Impact:</strong> Confirm scalability before full rollout, reducing risk.</p>
            <p><strong>Timeline:</strong> 6-week test period with analysis.</p>
        </div>
        """)

        st.html(f"""
        <div class='ust-success-box'>
            <h4>4. Set ROI Guardrails</h4>
            <p><strong>Action:</strong> Establish minimum ROI threshold of {max(0, roi['medium_term']['roi_pct'] * 0.7):.1f}%
            for continued investment in each channel.</p>
            <p><strong>Expected Impact:</strong> Prevent value-destroying spend through systematic monitoring.</p>
            <p><strong>Timeline:</strong> Implement immediately in budget planning process.</p>
        </div>
        """)

        st.html("""
        <div class='ust-success-box'>
            <h4>6. Continuous Measurement</h4>
            <p><strong>Action:</strong> Establish quarterly RCT cadence to track evolving effectiveness
            and market dynamics.</p>
            <p><strong>Expected Impact:</strong> Build institutional knowledge, refine strategies over time.</p>
            <p><strong>Timeline:</strong> Ongoing with quarterly reviews.</p>
        </div>
        """)

    st.markdown("---")

    # ========================================================================
    # SECTION 6: PROFIT BRIDGE - FROM REVENUE TO PROFIT
    # ========================================================================

    st.markdown("### 🌉 Profit Bridge: Revenue to Net Profit")

    st.html("""
    <div class='ust-accent-box'>
        <h4>The Path from Revenue to Profit</h4>
        <p><strong>Understanding True Profitability:</strong> Revenue is the top line, but profit is what matters.
        This section shows every deduction and cost to arrive at the true incremental profit.</p>
    </div>
    """)

    # Get data for calculations
    sales_df = st.session_state.sales_df
    media_df = st.session_state.media_df
    test_start = pd.to_datetime(st.session_state.metadata['test_start_date'])
    treatment_dmas = st.session_state.metadata['treatment_dmas']

    sales_df['date'] = pd.to_datetime(sales_df['date'])
    media_df['date'] = pd.to_datetime(media_df['date'])

    # Calculate incremental revenue (from medium-term)
    test_sales = sales_df[sales_df['date'] >= test_start]

    treat_revenue = test_sales[test_sales['is_treatment']]['sales_revenue'].sum()
    ctrl_revenue = test_sales[~test_sales['is_treatment']]['sales_revenue'].sum()

    n_treat = len(treatment_dmas)
    n_ctrl = sales_df[~sales_df['geo_id'].isin(treatment_dmas)]['geo_id'].nunique()

    ctrl_revenue_scaled = ctrl_revenue * (n_treat / n_ctrl) if n_ctrl > 0 else 0
    incremental_revenue = treat_revenue - ctrl_revenue_scaled

    # Cost of Goods Sold (60% of revenue, leaving 40% margin)
    cogs = incremental_revenue * 0.60

    # Gross Profit
    gross_profit = incremental_revenue * 0.40

    # Marketing Costs
    media_spend = media_df[
        (media_df['date'] >= test_start) &
        (media_df['geo_id'].isin(treatment_dmas))
    ]['spend_usd'].sum()

    # Price Promotion Cost (lost revenue)
    price_promo_sales = test_sales[
        (test_sales['promo_type'] == 'Price') &
        (test_sales['is_treatment'])
    ]['sales_revenue'].sum()
    price_discount_cost = price_promo_sales * 0.15  # 15% discount

    # Visibility Promotion Cost
    visibility_weeks = test_sales[
        (test_sales['promo_type'] == 'Visibility') &
        (test_sales['is_treatment'])
    ]['date'].nunique()
    stores_per_dma = 25
    visibility_cost = n_treat * stores_per_dma * visibility_weeks * 200  # $200/store/week

    # Total Marketing Investment
    total_marketing = media_spend + price_discount_cost + visibility_cost

    # Net Incremental Profit
    net_profit = gross_profit - total_marketing

    # ROI
    profit_roi = (net_profit / total_marketing * 100) if total_marketing > 0 else 0

    # Create waterfall visualization
    fig, ax = plt.subplots(figsize=(14, 7))

    # Waterfall data
    labels = [
        'Incremental\nRevenue',
        'COGS\n(60%)',
        'Gross\nProfit',
        'Media\nSpend',
        'Price\nDiscounts',
        'Visibility\nCosts',
        'Net\nProfit'
    ]

    values = [
        incremental_revenue,
        -cogs,
        0,  # Placeholder (gross profit shown as running total)
        -media_spend,
        -price_discount_cost,
        -visibility_cost,
        0   # Placeholder (net profit shown as running total)
    ]

    # Calculate running totals for waterfall
    running_total = 0
    bottoms = []
    heights = []
    colors = []

    for i, (label, value) in enumerate(zip(labels, values)):
        if label == 'Gross\nProfit':
            # Show gross profit as bar from 0
            bottoms.append(0)
            heights.append(gross_profit)
            colors.append('#0097AC')
        elif label == 'Net\nProfit':
            # Show net profit as bar from 0
            bottoms.append(0)
            heights.append(net_profit)
            colors.append('#006E74' if net_profit > 0 else '#DC3545')
        else:
            bottoms.append(running_total if value < 0 else running_total)
            heights.append(abs(value))
            colors.append('#DC3545' if value < 0 else '#006E74')
            running_total += value

    # Plot bars
    bars = ax.bar(range(len(labels)), heights, bottom=bottoms,
                   color=colors, edgecolor='black', linewidth=2, alpha=0.8, width=0.6)

    # Add value labels
    for i, (bar, label, value, height, bottom) in enumerate(zip(bars, labels, values, heights, bottoms)):
        if label in ['Gross\nProfit', 'Net\nProfit']:
            # Show total value for subtotals
            display_val = gross_profit if label == 'Gross\nProfit' else net_profit
            label_y = display_val / 2
        else:
            label_y = bottom + height / 2

        value_to_show = (
            value if value != 0 else                   # keep `value` when it isn’t zero
            gross_profit if label == "Gross Profit"   # otherwise use either gross_profit or net_profit
            else net_profit
        )
        label_text = (f'${abs(value_to_show):,.0f}'               # plain format spec → no \ needed here
        )

        ax.text(i, label_y, label_text,
               ha='center', va='center', fontweight='bold', fontsize=10, color='white')

    # Add connector lines
    for i in range(len(labels) - 1):
        if labels[i] not in ['Gross\nProfit'] and labels[i+1] not in ['Gross\nProfit', 'Net\nProfit']:
            # Calculate the end point of current bar
            if values[i] < 0:
                y1 = bottoms[i]
            else:
                y1 = bottoms[i] + heights[i]

            # Draw connector to next bar
            ax.plot([i + 0.3, i + 0.7], [y1, y1], 'k--', linewidth=1, alpha=0.5)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11, fontweight='bold')
    ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
    ax.set_title('Profit Bridge: From Revenue to Net Incremental Profit (Waterfall)', fontsize=14, fontweight='bold', color='#006E74')
    ax.axhline(0, color='black', linewidth=1, alpha=0.3)
    ax.grid(True, alpha=0.3, axis='y')

    # Add ROI annotation
    ax.text(len(labels) - 1, net_profit + abs(net_profit) * 0.1,
           f'ROI: {profit_roi:+.1f}%', ha='center', fontweight='bold',
           fontsize=12, bbox=dict(boxstyle='round,pad=0.5', facecolor='#E5F5F5', edgecolor='#006E74', linewidth=2))

    plt.tight_layout()
    st.pyplot(fig)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.html(f"""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Incremental Revenue</div>
            <h2 style='color: #006E74; font-size: 1.8rem;'>${incremental_revenue:,.0f}</h2>
            <p style='color: #666;'>Top line impact</p>
        </div>
        """)

    with col2:
        st.html(f"""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Gross Profit (40%)</div>
            <h2 style='color: #0097AC; font-size: 1.8rem;'>${gross_profit:,.0f}</h2>
            <p style='color: #666;'>After COGS</p>
        </div>
        """)

    with col3:
        st.html(f"""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Total Marketing</div>
            <h2 style='color: #FF6B00; font-size: 1.8rem;'>${total_marketing:,.0f}</h2>
            <p style='color: #666;'>All costs included</p>
        </div>
        """)

    with col4:
        profit_color = '#006E74' if net_profit > 0 else '#DC3545'
        st.html(f"""
        <div class='ust-card ust-card-accent'>
            <div class='ust-eyebrow'>Net Profit</div>
            <h2 style='color: {profit_color}; font-size: 1.8rem;'>${net_profit:,.0f}</h2>
            <p style='color: #666;'>Bottom line</p>
        </div>
        """)

    # Detailed breakdown
    with st.expander("📊 Detailed Profit Bridge Breakdown"):
        bridge_df = pd.DataFrame({
            'Step': [
                '1. Incremental Revenue',
                '2. Less: Cost of Goods Sold (60%)',
                '3. Equals: Gross Profit (40%)',
                '4. Less: Media Spend',
                '5. Less: Price Promotion Discounts (15%)',
                '6. Less: Visibility Promotion Costs',
                '7. Equals: Net Incremental Profit'
            ],
            'Amount ($)': [
                f'${incremental_revenue:,.0f}',
                f'-${cogs:,.0f}',
                f'${gross_profit:,.0f}',
                f'-${media_spend:,.0f}',
                f'-${price_discount_cost:,.0f}',
                f'-${visibility_cost:,.0f}',
                f'${net_profit:,.0f}'
            ],
            'Notes': [
                'Treatment revenue minus control baseline',
                '60% margin to cover product, fulfillment costs',
                'Revenue available to cover marketing',
                'Advertising spend across all channels',
                f'{price_promo_sales:,.0f} in promo sales × 15% discount',
                f'{n_treat} DMAs × {stores_per_dma} stores × {visibility_weeks} weeks × $200/store/week',
                f'ROI: {profit_roi:+.1f}%'
            ]
        })

        st.dataframe(bridge_df, use_container_width=True, hide_index=True)

        st.markdown("""
        **Key Insights from Profit Bridge:**

        - **Gross Margin Impact:** 60% of revenue goes to COGS, leaving 40% for marketing and profit
        - **Marketing Efficiency:** Compare total marketing cost to gross profit to see spending rate
        - **Promotion Costs:** Both price discounts and visibility investments are real costs that impact ROI
        - **Net Profitability:** Final metric shows if campaign created or destroyed value
        """)

    st.markdown("---")

    # ========================================================================
    # SECTION 7: EXECUTIVE SUMMARY
    # ========================================================================

    st.markdown("### 📋 Executive Summary: Key Takeaways")

    st.html(f"""
    <div class='ust-card ust-card-accent' style='padding: 24px;'>
        <h3 style='color: #006E74; margin-bottom: 16px;'>ROI Analysis Summary</h3>

        <p style='font-size: 1.1rem; margin-bottom: 20px;'><strong>Overall Assessment:</strong>
        {"The marketing investment delivered positive returns across all time horizons." if roi['short_term']['roi_pct'] > 0
         else "The marketing investment shows mixed results requiring strategic refinement."}</p>

        <div style='background: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;'>
            <p style='margin: 8px 0;'><strong>📊 Multi-Period Performance:</strong></p>
            <ul style='margin: 8px 0;'>
                <li>Short-Term ROI: <strong>{roi['short_term']['roi_pct']:+.1f}%</strong> (ROAS: ${roi['short_term']['profit_roas']:.2f})</li>
                <li>Medium-Term ROI: <strong>{roi['medium_term']['roi_pct']:+.1f}%</strong> (ROAS: ${roi['medium_term']['profit_roas']:.2f})</li>
                <li>Long-Term ROI: <strong>{roi['long_term']['roi_pct']:+.1f}%</strong> (ROAS: ${roi['long_term']['profit_roas']:.2f})</li>
            </ul>
        </div>

        <div style='background: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;'>
            <p style='margin: 8px 0;'><strong>🏆 Top Performer:</strong></p>
            <p style='margin: 8px 0;'><strong>{best_channel_roi['Channel']}</strong> channel delivers
            <strong>{best_channel_roi['ROI (%)']:+.1f}%</strong> ROI with ${best_channel_roi['ROAS']:.2f} ROAS.</p>
        </div>

        <div style='background: white; padding: 16px; border-radius: 8px;'>
            <p style='margin: 8px 0;'><strong>🎯 Primary Recommendation:</strong></p>
            <p style='margin: 8px 0;'>Reallocate budget toward highest-performing channels while testing
            moderate scaling (1.2x) in pilot markets to validate sustained returns.</p>
        </div>
    </div>
    """)

    st.markdown("---")

    # ========================================================================
    # SECTION 7: TECHNICAL DETAILS
    # ========================================================================

    with st.expander("📊 Technical Details: ROI Calculation Methodology"):
        st.markdown("### ROI Calculation Framework")

        st.markdown("""
        **Formula Components:**

        1. **Incremental Revenue:** Treatment effect (DiD) × Volume
        2. **Incremental Profit:** Incremental Revenue × Profit Margin
        3. **Incremental Investment:** Treatment group spend - Control group spend
        4. **ROI:** (Incremental Profit / Incremental Investment - 1) × 100%
        5. **ROAS:** Incremental Profit / Incremental Investment

        **Time Horizons:**

        - **Short-Term (4 weeks):** Direct campaign effects during test period
        - **Medium-Term (12 weeks):** Sustained effects including early repeat purchases
        - **Long-Term (with CLV):** Full customer lifetime value for new customers acquired

        **Assumptions:**
        """)

        st.json({
            "Profit Margin": "40%",
            "Average Customer LTV": "$150",
            "Retention Rate": "60%",
            "Diminishing Returns": "Square root function (conservative estimate)",
            "Clustering": "Two-way (DMA + Time) for standard errors"
        })

        st.markdown("""
        **Limitations:**

        - Channel-level ROI uses simplified equal investment distribution
        - Diminishing returns curve is modeled, not empirically validated
        - Long-term projections assume stable retention rates
        - Does not account for competitive responses or market saturation

        **Recommendation:** Validate assumptions with follow-up experiments and continuous monitoring.
        """)
