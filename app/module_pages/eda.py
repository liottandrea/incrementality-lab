"""
Exploratory Data Analysis Module
Analyzes the RCT data and explains the business problem
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.append('src')


def render():
    """Render the EDA panel"""
    st.html("<div class='ust-eyebrow'>Understanding the Challenge</div>")
    st.markdown("## Exploratory Data Analysis")

    if not st.session_state.data_generated:
        st.html("""
        <div class='ust-info-box'>
            <strong>⚠️ Data Required</strong><br>
            Please load or generate data in Step 1 before exploring.
        </div>
        """)
        return

    # ========================================================================
    # SECTION 1: THE BUSINESS PROBLEM
    # ========================================================================

    st.markdown("### 🎯 The Business Problem")

    st.html("""
    <div class='ust-accent-box'>
        <h4>Measuring Marketing Incrementality</h4>
        <p><strong>Core Question:</strong> Does increasing marketing spend actually drive incremental sales, or are we just reaching customers who would have bought anyway?</p>

        <p><strong>The Challenge:</strong></p>
        <ul>
            <li><strong>Correlation ≠ Causation:</strong> Sales and marketing spend naturally move together, making it hard to isolate the true causal effect</li>
            <li><strong>Confounding Factors:</strong> Seasonality, holidays, competitors, and other external factors can mask the true impact</li>
            <li><strong>ROI Uncertainty:</strong> Without knowing the incremental effect, we can't confidently calculate return on investment</li>
        </ul>

        <p><strong>Our Solution:</strong> Randomized Controlled Trial (RCT) using Difference-in-Differences methodology</p>
    </div>
    """)

    st.markdown("---")

    # ========================================================================
    # SECTION 2: THE EXPERIMENTAL DESIGN
    # ========================================================================

    st.markdown("### 🔬 The Experimental Design")

    metadata = st.session_state.metadata
    test_start = pd.to_datetime(metadata['test_start_date'])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.html("""
        <div class='ust-card ust-card-info'>
            <div class='ust-eyebrow'>Duration</div>
            <h2 style='color: #006E74;'>{} weeks</h2>
            <p style='color: #666;'>Total observation period</p>
        </div>
        """.format(metadata['n_weeks']))

    with col2:
        st.html("""
        <div class='ust-card ust-card-info'>
            <div class='ust-eyebrow'>Markets</div>
            <h2 style='color: #006E74;'>{}</h2>
            <p style='color: #666;'>DMAs (geographic markets)</p>
        </div>
        """.format(metadata['n_dmas']))

    with col3:
        n_treatment = len(metadata['treatment_dmas'])
        st.html("""
        <div class='ust-card ust-card-accent'>
            <div class='ust-eyebrow'>Treatment Group</div>
            <h2 style='color: #FF6B00;'>{}</h2>
            <p style='color: #666;'>DMAs with increased spend</p>
        </div>
        """.format(n_treatment))

    with col4:
        n_control = metadata['n_dmas'] - n_treatment
        st.html("""
        <div class='ust-card'>
            <div class='ust-eyebrow'>Control Group</div>
            <h2 style='color: #006E74;'>{}</h2>
            <p style='color: #666;'>DMAs with baseline spend</p>
        </div>
        """.format(n_control))

    st.html("""
    <div class='ust-info-box'>
        <strong>How it Works:</strong><br>
        • <strong>Pre-period:</strong> Both treatment and control groups operate normally (baseline)<br>
        • <strong>Test period:</strong> Treatment group receives increased marketing spend, control stays at baseline<br>
        • <strong>Measurement:</strong> Compare the change in sales between treatment and control groups<br>
        • <strong>Causal Inference:</strong> The difference in changes = incremental effect of marketing
    </div>
    """)

    st.markdown("---")

    # ========================================================================
    # SECTION 3: DATA OVERVIEW
    # ========================================================================

    st.markdown("### 📊 Data Overview")

    sales_df = st.session_state.sales_df
    transactions_df = st.session_state.transactions_df
    media_df = st.session_state.media_df
    controls_df = st.session_state.controls_df

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sales Records", f"{len(sales_df):,}")
        st.metric("Total Revenue", f"${sales_df['sales_revenue'].sum():,.0f}")

    with col2:
        st.metric("Total Transactions", f"{len(transactions_df):,}")
        st.metric("Unique Customers", f"{transactions_df['customer_id'].nunique():,}")

    with col3:
        st.metric("Media Records", f"{len(media_df):,}")
        st.metric("Total Spend", f"${media_df['spend_usd'].sum():,.0f}")

    with col4:
        st.metric("Retail Channels", sales_df['retail_channel'].nunique())
        st.metric("Media Channels", media_df['channel'].nunique())

    # Data Tables
    with st.expander("📋 View Data Samples"):
        tab1, tab2, tab3, tab4 = st.tabs(["Sales", "Transactions", "Media", "Controls"])

        with tab1:
            st.dataframe(sales_df.head(50), use_container_width=True)

        with tab2:
            st.dataframe(transactions_df.head(50), use_container_width=True)

        with tab3:
            st.dataframe(media_df.head(50), use_container_width=True)

        with tab4:
            st.dataframe(controls_df.head(50), use_container_width=True)

    st.markdown("---")

    # ========================================================================
    # SECTION 4: TEMPORAL PATTERNS
    # ========================================================================

    st.markdown("### 📈 Temporal Patterns")

    # Prepare time series data
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    daily_sales = sales_df.groupby(['date', 'is_treatment', 'is_test_period']).agg({
        'sales_revenue': 'sum',
        'sales_units': 'sum'
    }).reset_index()

    col1, col2 = st.columns([2, 1])

    with col1:
        # Sales over time
        fig, ax = plt.subplots(figsize=(12, 6))

        treatment_sales = daily_sales[daily_sales['is_treatment']].groupby('date')['sales_revenue'].sum()
        control_sales = daily_sales[~daily_sales['is_treatment']].groupby('date')['sales_revenue'].sum()

        ax.plot(treatment_sales.index, treatment_sales.values, label='Treatment DMAs',
                linewidth=2, color='#FF6B00', alpha=0.8)
        ax.plot(control_sales.index, control_sales.values, label='Control DMAs',
                linewidth=2, color='#006E74', alpha=0.8)

        # Mark test period start
        ax.axvline(test_start, color='red', linestyle='--', linewidth=2,
                   label=f'Test Start ({test_start.strftime("%Y-%m-%d")})', alpha=0.7)

        ax.set_title('Sales Over Time: Treatment vs Control', fontsize=16, fontweight='bold', color='#006E74')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Daily Sales Revenue ($)', fontsize=12)
        ax.legend(fontsize=10, loc='upper left')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        st.pyplot(fig)

    with col2:
        st.html("""
        <div class='ust-info-box'>
            <strong>What to Look For:</strong><br>
            • <strong>Parallel Trends:</strong> Treatment and control should move together before test period<br>
            • <strong>Divergence:</strong> After test starts, we expect treatment to increase if marketing is effective<br>
            • <strong>Seasonality:</strong> Weekly/monthly patterns should be visible
        </div>
        """)

        # Pre vs Test stats
        pre_treatment = sales_df[(sales_df['is_treatment']) & (~sales_df['is_test_period'])]['sales_revenue'].sum()
        test_treatment = sales_df[(sales_df['is_treatment']) & (sales_df['is_test_period'])]['sales_revenue'].sum()
        pre_control = sales_df[(~sales_df['is_treatment']) & (~sales_df['is_test_period'])]['sales_revenue'].sum()
        test_control = sales_df[(~sales_df['is_treatment']) & (sales_df['is_test_period'])]['sales_revenue'].sum()

        treatment_change = ((test_treatment / pre_treatment) - 1) * 100
        control_change = ((test_control / pre_control) - 1) * 100

        st.metric("Treatment Change", f"{treatment_change:+.1f}%",
                  help="Revenue change from pre to test period")
        st.metric("Control Change", f"{control_change:+.1f}%",
                  help="Revenue change from pre to test period")
        st.metric("Difference", f"{treatment_change - control_change:+.1f}pp",
                  help="Potential incremental effect")

    st.markdown("---")

    # ========================================================================
    # SECTION 5: CHANNEL ANALYSIS
    # ========================================================================

    st.markdown("### 🎯 Channel Performance")

    col1, col2 = st.columns(2)

    with col1:
        # Retail channel breakdown
        st.markdown("**Retail Channel Distribution**")

        channel_revenue = sales_df.groupby(['retail_channel', 'is_test_period']).agg({
            'sales_revenue': 'sum'
        }).reset_index()

        fig, ax = plt.subplots(figsize=(8, 6))

        channels = channel_revenue['retail_channel'].unique()
        x = np.arange(len(channels))
        width = 0.35

        pre_data = channel_revenue[~channel_revenue['is_test_period']].set_index('retail_channel')['sales_revenue']
        test_data = channel_revenue[channel_revenue['is_test_period']].set_index('retail_channel')['sales_revenue']

        ax.bar(x - width/2, pre_data, width, label='Pre-Period', color='#006E74', alpha=0.8)
        ax.bar(x + width/2, test_data, width, label='Test-Period', color='#FF6B00', alpha=0.8)

        ax.set_xlabel('Retail Channel', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Revenue ($)', fontsize=12, fontweight='bold')
        ax.set_title('Sales by Retail Channel', fontsize=14, fontweight='bold', color='#006E74')
        ax.set_xticks(x)
        ax.set_xticklabels(channels)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        # Media channel spend
        st.markdown("**Media Channel Investment**")

        media_spend = media_df.groupby('channel')['spend_usd'].sum().sort_values(ascending=True)

        fig, ax = plt.subplots(figsize=(8, 6))

        colors = ['#0097AC' if i < len(media_spend)-1 else '#FF6B00' for i in range(len(media_spend))]
        ax.barh(media_spend.index, media_spend.values, color=colors, edgecolor='#006E74', linewidth=1.5)

        ax.set_xlabel('Total Spend ($)', fontsize=12, fontweight='bold')
        ax.set_title('Media Spend by Channel', fontsize=14, fontweight='bold', color='#006E74')
        ax.grid(True, alpha=0.3, axis='x')

        # Add value labels
        for i, v in enumerate(media_spend.values):
            ax.text(v, i, f' ${v:,.0f}', va='center', fontsize=10)

        plt.tight_layout()
        st.pyplot(fig)

    # Channel metrics
    st.markdown("**Channel Performance Metrics**")
    col1, col2, col3, col4 = st.columns(4)

    retail_channels = sales_df['retail_channel'].unique()
    media_channels = media_df['channel'].unique()

    with col1:
        st.metric("Retail Channels", len(retail_channels))
        for ch in retail_channels:
            rev = sales_df[sales_df['retail_channel']==ch]['sales_revenue'].sum()
            st.write(f"• {ch}: ${rev:,.0f}")

    with col2:
        st.metric("Media Channels", len(media_channels))
        for ch in media_channels:
            spend = media_df[media_df['channel']==ch]['spend_usd'].sum()
            st.write(f"• {ch}: ${spend:,.0f}")

    with col3:
        st.metric("Total Impressions", f"{media_df['impressions'].sum():,.0f}")
        st.metric("Total Clicks", f"{media_df['clicks'].sum():,.0f}")

    with col4:
        avg_ctr = (media_df['clicks'].sum() / media_df['impressions'].sum()) * 100
        st.metric("Avg CTR", f"{avg_ctr:.2f}%")
        avg_cpc = media_df['spend_usd'].sum() / media_df['clicks'].sum()
        st.metric("Avg CPC", f"${avg_cpc:.2f}")

    st.markdown("---")

    # ========================================================================
    # SECTION 6: PROMOTION TYPE ANALYSIS
    # ========================================================================

    st.markdown("### 🏷️ Promotion Strategy Analysis")

    st.html("""
    <div class='ust-info-box'>
        <strong>Understanding Promotion Types:</strong><br>
        • <strong>Price Promotions:</strong> Used for Online and Omnichannel - reduce product prices to drive demand<br>
        • <strong>Visibility Promotions:</strong> Used for Store and Omnichannel - improve shelf positioning and brand visibility<br>
        • Omnichannel can leverage both strategies depending on customer touchpoint<br>
        <br>
        <strong>Note:</strong> This section shows promotional activity distribution. True incremental effectiveness will be measured through the RCT analysis in later steps.
    </div>
    """)

    col1, col2 = st.columns(2)

    with col1:
        # Promo type by channel
        st.markdown("**Promotion Type by Retail Channel**")

        promo_channel = sales_df[sales_df['promo_type'].notna()].groupby(['retail_channel', 'promo_type']).agg({
            'sales_revenue': 'sum',
            'sales_units': 'sum'
        }).reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))

        channels = promo_channel['retail_channel'].unique()
        promo_types = promo_channel['promo_type'].unique()
        x = np.arange(len(channels))
        width = 0.35

        for i, promo in enumerate(promo_types):
            data = promo_channel[promo_channel['promo_type']==promo].set_index('retail_channel')['sales_revenue']
            # Reindex to ensure all channels are present
            data = data.reindex(channels, fill_value=0)
            color = '#FF6B00' if promo == 'Price' else '#006E74'
            ax.bar(x + i*width, data.values, width, label=promo, color=color, alpha=0.8)

        ax.set_xlabel('Retail Channel', fontsize=12, fontweight='bold')
        ax.set_ylabel('Promo Sales Revenue ($)', fontsize=12, fontweight='bold')
        ax.set_title('Promotional Sales by Channel & Type', fontsize=14, fontweight='bold', color='#006E74')
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(channels)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        # Promo distribution
        st.markdown("**Promotion Type Distribution**")

        # Calculate promo vs non-promo sales
        promo_sales = sales_df[sales_df['promo_type'].notna()].groupby('promo_type').agg({
            'sales_revenue': 'sum',
            'sales_units': 'sum'
        }).reset_index()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))

        # Revenue pie chart
        colors_promo = ['#FF6B00', '#006E74']
        ax1.pie(promo_sales['sales_revenue'], labels=promo_sales['promo_type'], autopct='%1.1f%%',
                colors=colors_promo, startangle=90)
        ax1.set_title('Promo Revenue Share', fontsize=12, fontweight='bold')

        # Units pie chart
        ax2.pie(promo_sales['sales_units'], labels=promo_sales['promo_type'], autopct='%1.1f%%',
                colors=colors_promo, startangle=90)
        ax2.set_title('Promo Units Share', fontsize=12, fontweight='bold')

        plt.tight_layout()
        st.pyplot(fig)

    # Promo metrics
    col1, col2, col3, col4 = st.columns(4)

    total_promo_rev = sales_df[sales_df['promo_type'].notna()]['sales_revenue'].sum()
    total_rev = sales_df['sales_revenue'].sum()
    promo_pct = (total_promo_rev / total_rev) * 100

    price_rev = sales_df[sales_df['promo_type']=='Price']['sales_revenue'].sum()
    visibility_rev = sales_df[sales_df['promo_type']=='Visibility']['sales_revenue'].sum()

    with col1:
        st.metric("Total Promo Revenue", f"${total_promo_rev:,.0f}", f"{promo_pct:.1f}% of total")

    with col2:
        st.metric("Price Promo Revenue", f"${price_rev:,.0f}")

    with col3:
        st.metric("Visibility Promo Revenue", f"${visibility_rev:,.0f}")

    with col4:
        avg_promo_sales = sales_df[sales_df['promo_type'].notna()]['sales_revenue'].mean()
        avg_nonpromo_sales = sales_df[sales_df['promo_type'].isna()]['sales_revenue'].mean()
        promo_vs_nonpromo = ((avg_promo_sales / avg_nonpromo_sales) - 1) * 100
        st.metric("Promo vs Non-Promo", f"{promo_vs_nonpromo:+.1f}%",
                  help="Comparison only - not causal lift")

    st.markdown("---")

    # ========================================================================
    # SECTION 7: AGE GROUP DEMOGRAPHICS (Omnichannel & Online)
    # ========================================================================

    st.markdown("### 👥 Age Group Demographics Analysis")

    st.html("""
    <div class='ust-info-box'>
        <strong>Demographic Data Availability:</strong><br>
        • <strong>Omnichannel & Online:</strong> Full customer demographic data including age segments<br>
        • <strong>Store:</strong> Limited demographic tracking (not included in age analysis)<br>
        • Focus on digital channels provides insights into customer preferences by age group
    </div>
    """)

    # Filter for channels with age data (Omnichannel and Online)
    age_data = transactions_df[transactions_df['retail_channel'].isin(['Omnichannel', 'Online_Specialty'])]

    col1, col2 = st.columns(2)

    with col1:
        # Age distribution by channel
        st.markdown("**Age Distribution by Channel (Omnichannel & Online)**")

        age_channel = age_data.groupby(['retail_channel', 'age_segment']).agg({
            'customer_id': 'count',
            'revenue': 'sum'
        }).reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))

        channels_with_age = age_channel['retail_channel'].unique()
        age_segments = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        x = np.arange(len(age_segments))
        width = 0.35

        for i, channel in enumerate(channels_with_age):
            data = age_channel[age_channel['retail_channel']==channel].set_index('age_segment')['customer_id']
            data = data.reindex(age_segments, fill_value=0)
            color = '#FF6B00' if channel == 'Omnichannel' else '#0097AC'
            ax.bar(x + i*width, data.values, width, label=channel, color=color, alpha=0.8)

        ax.set_xlabel('Age Segment', fontsize=12, fontweight='bold')
        ax.set_ylabel('Transaction Count', fontsize=12, fontweight='bold')
        ax.set_title('Transactions by Age & Channel', fontsize=14, fontweight='bold', color='#006E74')
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(age_segments, rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        # Age segment revenue contribution
        st.markdown("**Revenue Contribution by Age Segment**")

        age_revenue = age_data.groupby('age_segment')['revenue'].sum().sort_values(ascending=True)
        age_revenue = age_revenue.reindex(['18-24', '25-34', '35-44', '45-54', '55-64', '65+'], fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 6))

        colors_age = ['#0097AC', '#006E74', '#FF6B00', '#0097AC', '#006E74', '#FF6B00']
        bars = ax.barh(age_revenue.index, age_revenue.values, color=colors_age, edgecolor='#006E74', linewidth=1.5)

        # Highlight top segment
        max_idx = age_revenue.values.argmax()
        bars[max_idx].set_color('#FF6B00')

        ax.set_xlabel('Total Revenue ($)', fontsize=12, fontweight='bold')
        ax.set_title('Revenue by Age Segment (Digital Channels)', fontsize=14, fontweight='bold', color='#006E74')
        ax.grid(True, alpha=0.3, axis='x')

        # Add value labels
        for i, v in enumerate(age_revenue.values):
            ax.text(v, i, f' ${v:,.0f}', va='center', fontsize=10)

        plt.tight_layout()
        st.pyplot(fig)

    # Age group metrics
    st.markdown("**Age Group Performance Metrics**")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        dominant_age = age_data.groupby('age_segment')['revenue'].sum().idxmax()
        dominant_rev = age_data.groupby('age_segment')['revenue'].sum().max()
        st.metric("Dominant Age Segment", dominant_age, f"${dominant_rev:,.0f}")

    with col2:
        avg_age_revenue = age_data.groupby('age_segment')['revenue'].mean()
        highest_avg_age = avg_age_revenue.idxmax()
        st.metric("Highest Avg Transaction", highest_avg_age, f"${avg_age_revenue.max():.2f}")

    with col3:
        new_cust_by_age = age_data[age_data['is_new_customer']].groupby('age_segment')['customer_id'].nunique()
        top_acquisition_age = new_cust_by_age.idxmax()
        st.metric("Top Acquisition Age", top_acquisition_age, f"{new_cust_by_age.max():,} new")

    with col4:
        total_digital_customers = age_data['customer_id'].nunique()
        st.metric("Total Digital Customers", f"{total_digital_customers:,}")

    # Age segment insights table
    with st.expander("📊 Detailed Age Segment Analysis"):
        age_analysis = age_data.groupby('age_segment').agg({
            'customer_id': 'nunique',
            'revenue': ['sum', 'mean'],
            'units': 'sum'
        }).reset_index()
        age_analysis.columns = ['Age Segment', 'Unique Customers', 'Total Revenue', 'Avg Transaction', 'Total Units']
        age_analysis = age_analysis.sort_values('Total Revenue', ascending=False)
        age_analysis['Revenue Share %'] = (age_analysis['Total Revenue'] / age_analysis['Total Revenue'].sum() * 100).round(1)
        age_analysis['Total Revenue'] = age_analysis['Total Revenue'].apply(lambda x: f"${x:,.0f}")
        age_analysis['Avg Transaction'] = age_analysis['Avg Transaction'].apply(lambda x: f"${x:.2f}")

        st.dataframe(age_analysis, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ========================================================================
    # SECTION 8: CUSTOMER INSIGHTS
    # ========================================================================

    st.markdown("### 👥 Customer Insights")

    col1, col2 = st.columns(2)

    with col1:
        # Age segment distribution
        st.markdown("**Customer Age Distribution**")

        age_dist = transactions_df.groupby('age_segment').agg({
            'customer_id': 'count',
            'revenue': 'sum'
        }).reset_index()
        age_dist.columns = ['age_segment', 'transactions', 'revenue']
        age_dist = age_dist.sort_values('transactions', ascending=False)

        fig, ax = plt.subplots(figsize=(8, 6))

        ax.bar(age_dist['age_segment'], age_dist['transactions'],
               color='#0097AC', edgecolor='#006E74', linewidth=1.5)

        ax.set_xlabel('Age Segment', fontsize=12, fontweight='bold')
        ax.set_ylabel('Transaction Count', fontsize=12, fontweight='bold')
        ax.set_title('Transactions by Age Segment', fontsize=14, fontweight='bold', color='#006E74')
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        # New vs Existing customers
        st.markdown("**New vs Existing Customers**")

        customer_type = transactions_df.groupby(['is_new_customer', 'is_test_period']).agg({
            'customer_id': 'count',
            'revenue': 'sum'
        }).reset_index()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 6))

        # Pre-period
        pre_data = customer_type[~customer_type['is_test_period']]
        new_pre = pre_data[pre_data['is_new_customer']]['customer_id'].sum()
        existing_pre = pre_data[~pre_data['is_new_customer']]['customer_id'].sum()

        ax1.pie([new_pre, existing_pre], labels=['New', 'Existing'], autopct='%1.1f%%',
                colors=['#FF6B00', '#006E74'], startangle=90)
        ax1.set_title('Pre-Period', fontsize=12, fontweight='bold')

        # Test-period
        test_data = customer_type[customer_type['is_test_period']]
        new_test = test_data[test_data['is_new_customer']]['customer_id'].sum()
        existing_test = test_data[~test_data['is_new_customer']]['customer_id'].sum()

        ax2.pie([new_test, existing_test], labels=['New', 'Existing'], autopct='%1.1f%%',
                colors=['#FF6B00', '#006E74'], startangle=90)
        ax2.set_title('Test-Period', fontsize=12, fontweight='bold')

        plt.tight_layout()
        st.pyplot(fig)

    # Customer metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_customers = transactions_df['customer_id'].nunique()
        st.metric("Total Customers", f"{total_customers:,}")

    with col2:
        new_customers = transactions_df[transactions_df['is_new_customer']]['customer_id'].nunique()
        new_pct = (new_customers / total_customers) * 100
        st.metric("New Customers", f"{new_customers:,}", f"{new_pct:.1f}%")

    with col3:
        avg_transaction = transactions_df['revenue'].mean()
        st.metric("Avg Transaction", f"${avg_transaction:.2f}")

    with col4:
        avg_units = transactions_df['units'].mean()
        st.metric("Avg Units/Transaction", f"{avg_units:.1f}")

    st.markdown("---")

    # ========================================================================
    # SECTION 7: KEY INSIGHTS & NEXT STEPS
    # ========================================================================

    st.markdown("### 💡 Key Insights & Next Steps")

    col1, col2 = st.columns(2)

    with col1:
        st.html("""
        <div class='ust-success-box'>
            <h4>What We've Learned</h4>
            <ul>
                <li><strong>Experimental Design:</strong> {n_treatment} treatment DMAs vs {n_control} control DMAs over {n_weeks} weeks</li>
                <li><strong>Data Quality:</strong> {total_sales:,} sales records, {total_trans:,} transactions, ${total_spend:,.0f} in media spend</li>
                <li><strong>Channels:</strong> {n_retail} retail channels and {n_media} media channels tracked</li>
                <li><strong>Customer Base:</strong> {total_cust:,} unique customers with {new_pct:.1f}% new acquisitions</li>
            </ul>
        </div>
        """.format(
            n_treatment=n_treatment,
            n_control=n_control,
            n_weeks=metadata['n_weeks'],
            total_sales=len(sales_df),
            total_trans=len(transactions_df),
            total_spend=media_df['spend_usd'].sum(),
            n_retail=sales_df['retail_channel'].nunique(),
            n_media=media_df['channel'].nunique(),
            total_cust=total_customers,
            new_pct=new_pct
        ))

    with col2:
        st.html("""
        <div class='ust-accent-box'>
            <h4>Next Steps in Analysis</h4>
            <ol>
                <li><strong>Data Quality Validation:</strong> Check for missing values, outliers, and parallel trends assumption</li>
                <li><strong>Difference-in-Differences Model:</strong> Estimate the causal treatment effect using statistical controls</li>
                <li><strong>Heterogeneous Effects:</strong> Analyze which channels, customer segments, and markets show strongest lift</li>
                <li><strong>ROI Calculation:</strong> Measure short-term, medium-term, and long-term return on investment</li>
                <li><strong>Strategic Recommendations:</strong> Identify optimal budget allocation and scaling opportunities</li>
            </ol>
        </div>
        """)

    st.html("""
    <div class='ust-info-box'>
        <strong>📊 Ready to Continue?</strong><br>
        Proceed to <strong>Validate Quality</strong> to ensure data meets statistical requirements for causal analysis.
    </div>
    """)
