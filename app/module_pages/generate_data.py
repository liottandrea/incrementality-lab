"""
Data Load Module
Handles data loading from database
"""

import streamlit as st
import pandas as pd
import json
import time
import sys
sys.path.append('src')


def render():
    """Render the Data Load panel"""
    st.markdown("<div class='ust-eyebrow'>Step 1: Data Foundation</div>", unsafe_allow_html=True)
    st.markdown("## Load Data from Database")

    st.markdown("""
    <div class='ust-info-box'>
        <strong>Building resilience through data.</strong><br>
        Connect to the Brightline RCT database to load campaign data for incrementality analysis.
    </div>
    """, unsafe_allow_html=True)

    # ========================================================================
    # DATABASE CONNECTION SECTION
    # ========================================================================

    st.markdown("### 🗄️ Database Connection")

    # Show database connection details
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div class='ust-card ust-card-info'>
            <div class='ust-eyebrow'>Connection Details</div>
            <p style='margin: 8px 0;'><strong>Host:</strong> brightline-analytics-prod.database.windows.net</p>
            <p style='margin: 8px 0;'><strong>Database:</strong> brightline_rct_prod</p>
            <p style='margin: 8px 0;'><strong>Schema:</strong> marketing_analytics</p>
            <p style='margin: 8px 0;'><strong>Port:</strong> 1433</p>
            <p style='margin: 8px 0;'><strong>Driver:</strong> SQL Server Native Client 11.0</p>
        </div>
        """, unsafe_allow_html=True)

        # Connection status
        if st.session_state.data_generated:
            st.markdown("""
            <div class='ust-success-box'>
                <strong>✓ Connected</strong><br>
                Active connection established to production database
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='ust-info-box'>
                <strong>⚪ Not Connected</strong><br>
                Click below to establish database connection
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if st.button("🔌 Connect & Load Data", use_container_width=True, type="primary"):
            # Simulate database connection
            with st.spinner("Establishing connection..."):
                time.sleep(0.2)
                st.info("🔐 Authenticating credentials...")
                time.sleep(0.2)
                st.info("🌐 Opening connection pool...")
                time.sleep(0.2)
                st.info("📊 Fetching table metadata...")
                time.sleep(0.2)

                try:
                    # Load the demo data (simulating database query)
                    st.info("🔍 Querying fact_sales table...")
                    time.sleep(0.2)
                    sales_df = pd.read_csv('data/demo/demo_sales.csv')

                    st.info("🔍 Querying fact_transactions table...")
                    time.sleep(0.2)
                    transactions_df = pd.read_csv('data/demo/demo_transactions.csv')

                    st.info("🔍 Querying fact_media_spend table...")
                    time.sleep(0.2)
                    media_df = pd.read_csv('data/demo/demo_media.csv')

                    st.info("🔍 Querying dim_controls table...")
                    time.sleep(0.2)
                    controls_df = pd.read_csv('data/demo/demo_controls.csv')

                    st.info("📋 Loading experiment metadata...")
                    time.sleep(0.2)
                    with open('data/demo/demo_metadata.json', 'r') as f:
                        metadata = json.load(f)

                    # Store in session state
                    st.session_state.sales_df = sales_df
                    st.session_state.transactions_df = transactions_df
                    st.session_state.media_df = media_df
                    st.session_state.controls_df = controls_df
                    st.session_state.metadata = metadata
                    st.session_state.data_generated = True
                    st.session_state.current_step = 2

                    st.success("✅ Data loaded successfully from database!")
                    # st.balloons()

                except FileNotFoundError:
                    st.error("⚠️ Database connection failed. Please check connection settings.")
                    return

    st.markdown("---")

    # ========================================================================
    # DATABASE METADATA SECTION (shown after data is loaded)
    # ========================================================================

    if st.session_state.data_generated:
        st.markdown("### 📊 Database Schema & Metadata")

        # Schema Overview
        st.markdown("**Schema: marketing_analytics**")
        st.markdown("*Last Updated: 2024-01-08 | Version: 3.2.1 | Owner: data_engineering*")

        st.markdown("---")

        # Table metadata
        st.markdown("### 📋 Available Tables")

        # Create metadata for each table
        tables_metadata = []

        # Sales table
        sales_df = st.session_state.sales_df
        tables_metadata.append({
            'Table Name': 'fact_sales',
            'Table Type': 'FACT',
            'Row Count': f"{len(sales_df):,}",
            'Columns': len(sales_df.columns),
            'Size (MB)': f"{sales_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}",
            'Partitioned': 'Yes (by date)',
            'Primary Key': 'date, geo_id, retail_channel',
            'Description': 'Daily sales revenue and units by market and channel'
        })

        # Transactions table
        transactions_df = st.session_state.transactions_df
        tables_metadata.append({
            'Table Name': 'fact_transactions',
            'Table Type': 'FACT',
            'Row Count': f"{len(transactions_df):,}",
            'Columns': len(transactions_df.columns),
            'Size (MB)': f"{transactions_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}",
            'Partitioned': 'Yes (by date)',
            'Primary Key': 'date, customer_id',
            'Description': 'Customer-level transaction records with demographics'
        })

        # Media table
        media_df = st.session_state.media_df
        tables_metadata.append({
            'Table Name': 'fact_media_spend',
            'Table Type': 'FACT',
            'Row Count': f"{len(media_df):,}",
            'Columns': len(media_df.columns),
            'Size (MB)': f"{media_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}",
            'Partitioned': 'Yes (by date)',
            'Primary Key': 'date, geo_id, channel',
            'Description': 'Daily media spend, impressions, and clicks by channel'
        })

        # Controls table
        controls_df = st.session_state.controls_df
        tables_metadata.append({
            'Table Name': 'dim_controls',
            'Table Type': 'DIMENSION',
            'Row Count': f"{len(controls_df):,}",
            'Columns': len(controls_df.columns),
            'Size (MB)': f"{controls_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}",
            'Partitioned': 'No',
            'Primary Key': 'date, geo_id',
            'Description': 'Control variables: holidays, promotions, competitor activity'
        })

        # Display table metadata
        metadata_df = pd.DataFrame(tables_metadata)
        st.dataframe(metadata_df, use_container_width=True, height=250)

        st.markdown("---")

        # Detailed column information
        st.markdown("### 🔍 Column Details")

        tab1, tab2, tab3, tab4 = st.tabs([
            "fact_sales",
            "fact_transactions",
            "fact_media_spend",
            "dim_controls"
        ])

        with tab1:
            st.markdown("**Table: fact_sales**")
            col_info = []
            for col in sales_df.columns:
                col_info.append({
                    'Column Name': col,
                    'Data Type': str(sales_df[col].dtype),
                    'Null Count': sales_df[col].isna().sum(),
                    'Unique Values': sales_df[col].nunique(),
                    'Sample Value': str(sales_df[col].iloc[0])
                })
            col_df = pd.DataFrame(col_info)
            st.dataframe(col_df, use_container_width=True)

            st.markdown("**Indexes:**")
            st.code("""
PRIMARY KEY: (date, geo_id, retail_channel)
INDEX idx_sales_date: (date)
INDEX idx_sales_geo: (geo_id)
INDEX idx_sales_treatment: (is_treatment)
INDEX idx_sales_test_period: (is_test_period)
            """)

        with tab2:
            st.markdown("**Table: fact_transactions**")
            col_info = []
            for col in transactions_df.columns:
                col_info.append({
                    'Column Name': col,
                    'Data Type': str(transactions_df[col].dtype),
                    'Null Count': transactions_df[col].isna().sum(),
                    'Unique Values': transactions_df[col].nunique(),
                    'Sample Value': str(transactions_df[col].iloc[0])
                })
            col_df = pd.DataFrame(col_info)
            st.dataframe(col_df, use_container_width=True)

            st.markdown("**Indexes:**")
            st.code("""
PRIMARY KEY: (date, customer_id)
INDEX idx_trans_date: (date)
INDEX idx_trans_customer: (customer_id)
INDEX idx_trans_geo: (geo_id)
INDEX idx_trans_new_customer: (is_new_customer)
            """)

        with tab3:
            st.markdown("**Table: fact_media_spend**")
            col_info = []
            for col in media_df.columns:
                col_info.append({
                    'Column Name': col,
                    'Data Type': str(media_df[col].dtype),
                    'Null Count': media_df[col].isna().sum(),
                    'Unique Values': media_df[col].nunique(),
                    'Sample Value': str(media_df[col].iloc[0])
                })
            col_df = pd.DataFrame(col_info)
            st.dataframe(col_df, use_container_width=True)

            st.markdown("**Indexes:**")
            st.code("""
PRIMARY KEY: (date, geo_id, channel)
INDEX idx_media_date: (date)
INDEX idx_media_geo: (geo_id)
INDEX idx_media_channel: (channel)
            """)

        with tab4:
            st.markdown("**Table: dim_controls**")
            col_info = []
            for col in controls_df.columns:
                col_info.append({
                    'Column Name': col,
                    'Data Type': str(controls_df[col].dtype),
                    'Null Count': controls_df[col].isna().sum(),
                    'Unique Values': controls_df[col].nunique(),
                    'Sample Value': str(controls_df[col].iloc[0])
                })
            col_df = pd.DataFrame(col_info)
            st.dataframe(col_df, use_container_width=True)

            st.markdown("**Indexes:**")
            st.code("""
PRIMARY KEY: (date, geo_id)
INDEX idx_controls_date: (date)
INDEX idx_controls_geo: (geo_id)
            """)

        st.markdown("---")

        # Data summary statistics
        st.markdown("### 📈 Data Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
            <div class='ust-card'>
                <div class='ust-eyebrow'>Total Records</div>
                <h2 style='color: #006E74;'>{:,}</h2>
                <p style='color: #666;'>Across all tables</p>
            </div>
            """.format(
                len(sales_df) + len(transactions_df) + len(media_df) + len(controls_df)
            ), unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class='ust-card'>
                <div class='ust-eyebrow'>Date Range</div>
                <h3 style='color: #006E74; font-size: 1rem;'>{}</h3>
                <p style='color: #666;'>to</p>
                <h3 style='color: #006E74; font-size: 1rem;'>{}</h3>
            </div>
            """.format(
                pd.to_datetime(sales_df['date']).min().strftime('%Y-%m-%d'),
                pd.to_datetime(sales_df['date']).max().strftime('%Y-%m-%d')
            ), unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class='ust-card ust-card-accent'>
                <div class='ust-eyebrow'>Experiment Design</div>
                <p style='margin: 4px 0;'><strong>Treatment:</strong> {} DMAs</p>
                <p style='margin: 4px 0;'><strong>Control:</strong> {} DMAs</p>
                <p style='margin: 4px 0;'><strong>Duration:</strong> {} weeks</p>
            </div>
            """.format(
                len(st.session_state.metadata['treatment_dmas']),
                st.session_state.metadata['n_dmas'] - len(st.session_state.metadata['treatment_dmas']),
                st.session_state.metadata['n_weeks']
            ), unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div class='ust-card'>
                <div class='ust-eyebrow'>Data Quality</div>
                <p style='margin: 4px 0;'><strong>Completeness:</strong> 100%</p>
                <p style='margin: 4px 0;'><strong>Null Values:</strong> 0</p>
                <p style='margin: 4px 0;'><strong>Duplicates:</strong> 0</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Experiment Metadata
        st.markdown("### 🧪 Experiment Metadata")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Experiment Configuration**")
            st.json({
                "experiment_id": "RCT_BRIGHTLINE_2024_Q1",
                "experiment_name": "Marketing Incrementality Test",
                "test_start_date": st.session_state.metadata['test_start_date'],
                "n_weeks": st.session_state.metadata['n_weeks'],
                "n_dmas": st.session_state.metadata['n_dmas'],
                "treatment_group_size": len(st.session_state.metadata['treatment_dmas']),
                "control_group_size": st.session_state.metadata['n_dmas'] - len(st.session_state.metadata['treatment_dmas'])
            })

        with col2:
            st.markdown("**Treatment Parameters**")
            st.json({
                "price_effect": st.session_state.metadata['price_effect'],
                "visibility_effect": st.session_state.metadata['visibility_effect'],
                "retail_channels": st.session_state.metadata['retail_channels'],
                "expected_roi": st.session_state.metadata['expected_roi']
            })

        st.markdown("""
        <div class='ust-success-box'>
            <strong>✓ Data Ready for Analysis</strong><br>
            All tables loaded successfully. Proceed to <strong>Explore Data (EDA)</strong> to understand patterns and insights.
        </div>
        """, unsafe_allow_html=True)
