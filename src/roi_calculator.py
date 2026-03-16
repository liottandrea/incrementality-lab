"""
Multi-Period ROI Calculator
Calculates ROI across different time horizons accounting for:
- Short-term lift (immediate promo effect)
- Medium-term effects (stockpiling adjustment)
- Long-term value (new customer CLV)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class MultiPeriodROI:
    """
    Calculate ROI across multiple time periods with scenario-based adjustments
    """
    
    def __init__(
        self, 
        sales_df, 
        media_df, 
        transactions_df=None,
        purchase_dynamics_results=None,
        hte_results=None
    ):
        """
        Initialize ROI calculator
        
        Args:
            sales_df: Sales data
            media_df: Media spend data
            transactions_df: Transaction-level data (optional)
            purchase_dynamics_results: Results from PurchaseDynamicsAnalyzer
            hte_results: Results from HeterogeneousEffectsAnalyzer
        """
        self.sales_df = sales_df.copy()
        self.media_df = media_df.copy()
        self.transactions_df = transactions_df.copy() if transactions_df is not None else None
        self.purchase_dynamics = purchase_dynamics_results
        self.hte_results = hte_results
        
        self.has_transaction_data = transactions_df is not None and not transactions_df.empty
    
    def calculate_complete_roi(
        self,
        test_start_date,
        treatment_dmas,
        profit_margin: float = 0.80,
        avg_clv: float = 150.0,
        retention_rate: float = 0.60,
        discount_rate: float = 0.10
    ) -> Dict:
        """
        Calculate comprehensive ROI across all time periods
        
        Args:
            test_start_date: When test started
            treatment_dmas: List of treatment DMAs
            profit_margin: Gross profit margin (e.g., 0.40 = 40%)
            avg_clv: Average customer lifetime value
            retention_rate: Customer retention rate
            discount_rate: Discount rate for NPV calculations
        
        Returns:
            Dictionary with ROI metrics for all periods
        """
        print("💰 Calculating Multi-Period ROI...")
        
        # Prepare data
        self._prepare_data(test_start_date, treatment_dmas)
        
        results = {}
        
        # 1. Short-term ROI (Weeks 1-4)
        print("\n1️⃣ Calculating short-term ROI (Weeks 1-4)...")
        short_term = self.calculate_short_term_roi(profit_margin)
        results['short_term'] = short_term
        
        # 2. Medium-term ROI (Weeks 1-12, adjusted for stockpiling)
        print("\n2️⃣ Calculating medium-term ROI (Weeks 1-12)...")
        medium_term = self.calculate_medium_term_roi(profit_margin)
        results['medium_term'] = medium_term
        
        # 3. Long-term ROI (Including CLV)
        print("\n3️⃣ Calculating long-term ROI (with CLV)...")
        long_term = self.calculate_long_term_roi(
            profit_margin, avg_clv, retention_rate, discount_rate
        )
        results['long_term'] = long_term
        
        # 4. Scenario-based ROI
        print("\n4️⃣ Calculating scenario-based ROI...")
        scenarios = self.calculate_scenario_roi(profit_margin, avg_clv)
        results['scenarios'] = scenarios
        
        # 5. Channel-specific ROI (if HTE data available)
        if self.hte_results and 'channel_effects' in self.hte_results:
            print("\n5️⃣ Calculating channel-specific ROI...")
            channel_roi = self.calculate_channel_roi(profit_margin)
            results['channel_roi'] = channel_roi
        
        print("\n✅ Multi-period ROI calculation complete!")
        return results
    
    def _prepare_data(self, test_start_date, treatment_dmas):
        """
        Prepare data for ROI calculations
        """
        self.sales_df['date'] = pd.to_datetime(self.sales_df['date'])
        self.media_df['date'] = pd.to_datetime(self.media_df['date'])
        test_start_date = pd.to_datetime(test_start_date)
        
        self.sales_df['is_treatment'] = self.sales_df['geo_id'].isin(treatment_dmas)
        self.sales_df['is_post'] = self.sales_df['date'] >= test_start_date
        
        self.test_start_date = test_start_date
        self.treatment_dmas = treatment_dmas
    
    def calculate_short_term_roi(self, profit_margin: float = 0.80) -> Dict:
        """
        Calculate short-term ROI (test period only)
        """
        # Get sales in test period using the is_test_period flag
        short_df = self.sales_df[self.sales_df['is_test_period'] == True].copy()
        
        # Treatment group sales
        treatment_sales = short_df[
            short_df['is_treatment'] == True
        ]['sales_revenue'].sum()
        
        # Control group sales (scale up to treatment group size)
        control_sales = short_df[
            short_df['is_treatment'] == False
        ]['sales_revenue'].sum()
        
        n_treatment = len(self.treatment_dmas)
        n_control = len([d for d in self.sales_df['geo_id'].unique() if d not in self.treatment_dmas])
        
        control_sales_scaled = control_sales * (n_treatment / n_control)
        
        # Incremental sales
        incremental_sales = treatment_sales - control_sales_scaled
        
        # Incremental profit
        incremental_profit = incremental_sales * profit_margin
        
        # Marketing spend in test period
        spend_df = self.media_df[
            (self.media_df['date'] >= self.test_start_date) &
            (self.media_df['geo_id'].isin(self.treatment_dmas))
        ]
        # Filter to test period dates only
        test_dates = short_df['date'].unique()
        spend_df = spend_df[spend_df['date'].isin(test_dates)]
        total_spend = spend_df['spend_usd'].sum()
        
        # Calculate ROI metrics
        revenue_roas = incremental_sales / total_spend if total_spend > 0 else 0
        profit_roas = incremental_profit / total_spend if total_spend > 0 else 0
        roi = (incremental_profit - total_spend) / total_spend if total_spend > 0 else 0
        
        print(f"   Incremental Sales: ${incremental_sales:,.0f}")
        print(f"   Incremental Profit: ${incremental_profit:,.0f}")
        print(f"   Marketing Spend: ${total_spend:,.0f}")
        print(f"   Profit ROAS: {profit_roas:.2f}x")
        print(f"   ROI: {roi*100:.1f}%")
        
        return {
            'period': 'Test Period',
            'incremental_sales': incremental_sales,
            'incremental_profit': incremental_profit,
            'marketing_spend': total_spend,
            'revenue_roas': revenue_roas,
            'profit_roas': profit_roas,
            'roi': roi,
            'roi_pct': roi * 100
        }
    
    def calculate_medium_term_roi(self, profit_margin: float = 0.80) -> Dict:
        """
        Calculate medium-term ROI (test + post periods, adjusted for stockpiling)
        """
        # Get sales in test + post periods
        medium_df = self.sales_df[
            (self.sales_df['is_test_period'] == True) |
            (self.sales_df['is_post_period'] == True)
        ].copy()
        
        # Treatment group sales
        treatment_sales = medium_df[
            medium_df['is_treatment'] == True
        ]['sales_revenue'].sum()
        
        # Control group sales (scaled)
        control_sales = medium_df[
            medium_df['is_treatment'] == False
        ]['sales_revenue'].sum()
        
        n_treatment = len(self.treatment_dmas)
        n_control = len([d for d in self.sales_df['geo_id'].unique() if d not in self.treatment_dmas])
        control_sales_scaled = control_sales * (n_treatment / n_control)
        
        # Incremental sales
        incremental_sales = treatment_sales - control_sales_scaled
        
        # Adjust for stockpiling if data available AND stockpiling is detected
        if self.purchase_dynamics and 'stockpiling' in self.purchase_dynamics:
            classification = self.purchase_dynamics['stockpiling']['summary'].get('classification', 'UNCLEAR')
            stockpiling_ratio = self.purchase_dynamics['stockpiling']['Treatment'].get('stockpiling_ratio', 0)

            # Only apply adjustment if stockpiling is actually detected
            if classification in ['HIGH_STOCKPILING', 'MODERATE_STOCKPILING']:
                # Reduce incremental sales by stockpiling effect
                stockpiling_adjustment = incremental_sales * stockpiling_ratio * 0.5  # 50% of stockpiling
                incremental_sales_adjusted = incremental_sales - stockpiling_adjustment
                print(f"   Stockpiling detected ({classification})")
                print(f"   Stockpiling adjustment: -${stockpiling_adjustment:,.0f}")
            else:
                # No stockpiling - use full incremental sales
                incremental_sales_adjusted = incremental_sales
                stockpiling_adjustment = 0
                print(f"   No stockpiling detected ({classification}) - using full incremental sales")
        else:
            incremental_sales_adjusted = incremental_sales
            stockpiling_adjustment = 0
        
        # Incremental profit
        incremental_profit = incremental_sales_adjusted * profit_margin
        
        # Marketing spend (test + post periods)
        medium_dates = medium_df['date'].unique()
        spend_df = self.media_df[
            (self.media_df['date'].isin(medium_dates)) &
            (self.media_df['geo_id'].isin(self.treatment_dmas))
        ]
        total_spend = spend_df['spend_usd'].sum()
        
        # ROI metrics
        revenue_roas = incremental_sales_adjusted / total_spend if total_spend > 0 else 0
        profit_roas = incremental_profit / total_spend if total_spend > 0 else 0
        roi = (incremental_profit - total_spend) / total_spend if total_spend > 0 else 0
        
        print(f"   Incremental Sales (adjusted): ${incremental_sales_adjusted:,.0f}")
        print(f"   Incremental Profit: ${incremental_profit:,.0f}")
        print(f"   Profit ROAS: {profit_roas:.2f}x")
        print(f"   ROI: {roi*100:.1f}%")
        
        return {
            'period': 'Test + Post Periods',
            'incremental_sales_raw': incremental_sales,
            'stockpiling_adjustment': stockpiling_adjustment,
            'incremental_sales_adjusted': incremental_sales_adjusted,
            'incremental_profit': incremental_profit,
            'marketing_spend': total_spend,
            'revenue_roas': revenue_roas,
            'profit_roas': profit_roas,
            'roi': roi,
            'roi_pct': roi * 100
        }
    
    def calculate_long_term_roi(
        self,
        profit_margin: float = 0.80,
        avg_clv: float = 150.0,
        retention_rate: float = 0.60,
        discount_rate: float = 0.10
    ) -> Dict:
        """
        Calculate long-term ROI including customer lifetime value
        """
        # Start with medium-term numbers
        medium_term = self.calculate_medium_term_roi(profit_margin)
        
        incremental_profit_base = medium_term['incremental_profit']
        total_spend = medium_term['marketing_spend']
        
        # Add CLV from new customers (if transaction data available)
        if self.has_transaction_data and self.purchase_dynamics:
            new_cust_data = self.purchase_dynamics.get('new_customers')
            
            if new_cust_data:
                n_new_customers = new_cust_data['new_customers']
                repeat_rate = new_cust_data['repeat_rate_pct'] / 100
                
                # Calculate CLV contribution
                # CLV = avg_clv × retention_rate (discounted)
                clv_value = avg_clv * retention_rate
                
                # Discount to present value (assume 1 year out)
                clv_npv = clv_value / (1 + discount_rate)
                
                # Total CLV from new customers
                total_clv = n_new_customers * clv_npv * repeat_rate
                
                print(f"   New customers acquired: {n_new_customers:,}")
                print(f"   CLV per customer (NPV): ${clv_npv:,.0f}")
                print(f"   Total CLV contribution: ${total_clv:,.0f}")
            else:
                total_clv = 0
                n_new_customers = 0
        else:
            # Estimate new customers as % of incremental volume
            n_new_customers = 0
            total_clv = 0
            print("   No transaction data - CLV estimate not available")
        
        # Total long-term profit
        total_long_term_profit = incremental_profit_base + total_clv
        
        # Long-term ROI
        profit_roas = total_long_term_profit / total_spend if total_spend > 0 else 0
        roi = (total_long_term_profit - total_spend) / total_spend if total_spend > 0 else 0
        
        print(f"   Total Long-term Profit: ${total_long_term_profit:,.0f}")
        print(f"   Profit ROAS (with CLV): {profit_roas:.2f}x")
        print(f"   ROI: {roi*100:.1f}%")
        
        return {
            'period': 'All Periods (with CLV)',
            'incremental_profit_base': incremental_profit_base,
            'clv_contribution': total_clv,
            'new_customers': n_new_customers,
            'total_profit': total_long_term_profit,
            'marketing_spend': total_spend,
            'profit_roas': profit_roas,
            'roi': roi,
            'roi_pct': roi * 100
        }
    
    def calculate_scenario_roi(self, profit_margin: float = 0.80, avg_clv: float = 150.0) -> Dict:
        """
        Calculate ROI for different scenarios:
        1. Stockpiling scenario (worst case)
        2. Category expansion (good case)
        3. New customer acquisition (best case)
        """
        scenarios = {}
        
        # Base numbers
        short_term = self.calculate_short_term_roi(profit_margin)
        base_profit = short_term['incremental_profit']
        total_spend = short_term['marketing_spend']
        
        # Scenario 1: Pure Stockpiling
        # All lift is pull-forward, post-period dip negates gains
        stockpiling_net_profit = base_profit * 0.3  # Only 30% is real
        stockpiling_roi = (stockpiling_net_profit - total_spend) / total_spend if total_spend > 0 else 0
        
        scenarios['stockpiling'] = {
            'name': 'Stockpiling (Worst Case)',
            'description': 'All lift is pulled forward from future sales',
            'net_profit': stockpiling_net_profit,
            'roi': stockpiling_roi,
            'roi_pct': stockpiling_roi * 100,
            'quality': '❌ Poor'
        }
        
        # Scenario 2: Category Expansion
        # Sustained lift, no post-dip
        expansion_multiplier = 2.5  # Sustained over time
        expansion_net_profit = base_profit * expansion_multiplier
        expansion_roi = (expansion_net_profit - total_spend) / total_spend if total_spend > 0 else 0
        
        scenarios['expansion'] = {
            'name': 'Category Expansion (Good Case)',
            'description': 'Existing customers buy more with sustained lift',
            'net_profit': expansion_net_profit,
            'roi': expansion_roi,
            'roi_pct': expansion_roi * 100,
            'quality': '✅ Good'
        }
        
        # Scenario 3: New Customer Acquisition
        # Immediate profit + CLV
        if self.has_transaction_data:
            # Estimate new customers
            n_new_est = int(base_profit / (15 * profit_margin))  # Estimate based on avg order
            clv_contribution = n_new_est * avg_clv * 0.6  # 60% retention
        else:
            clv_contribution = base_profit * 2.0  # Conservative estimate
        
        new_cust_profit = base_profit + clv_contribution
        new_cust_roi = (new_cust_profit - total_spend) / total_spend if total_spend > 0 else 0
        
        scenarios['new_customers'] = {
            'name': 'New Customer Acquisition (Best Case)',
            'description': 'Attracted new customers with high CLV',
            'net_profit': new_cust_profit,
            'roi': new_cust_roi,
            'roi_pct': new_cust_roi * 100,
            'quality': '🎉 Excellent'
        }
        
        # Print summary
        print("\n   Scenario Comparison:")
        for key, scenario in scenarios.items():
            print(f"   {scenario['name']}: ROI = {scenario['roi_pct']:.1f}% {scenario['quality']}")
        
        return scenarios
    
    def calculate_channel_roi(self, profit_margin: float = 0.80) -> Dict:
        """
        Calculate ROI by retail channel using proper DiD methodology
        """
        if not self.hte_results or 'channel_effects' not in self.hte_results:
            return {}

        channel_effects = self.hte_results['channel_effects']

        # Get test + post period data
        test_df = self.sales_df[
            (self.sales_df['is_test_period'] == True) |
            (self.sales_df['is_post_period'] == True)
        ]
        spend_df = self.media_df[self.media_df['date'] >= self.test_start_date]

        channel_roi = {}

        # Calculate total spend for allocation
        total_spend = spend_df[
            spend_df['geo_id'].isin(self.treatment_dmas)
        ]['spend_usd'].sum()

        for channel, effect_data in channel_effects.items():
            # Treatment sales for this channel
            treatment_sales = test_df[
                (test_df['retail_channel'] == channel) &
                (test_df['is_treatment'] == True)
            ]['sales_revenue'].sum()

            # Control sales for this channel (scaled to treatment size)
            control_sales = test_df[
                (test_df['retail_channel'] == channel) &
                (test_df['is_treatment'] == False)
            ]['sales_revenue'].sum()

            # Scale control to treatment group size
            n_treatment = len(self.treatment_dmas)
            n_control = len([d for d in self.sales_df['geo_id'].unique() if d not in self.treatment_dmas])
            control_sales_scaled = control_sales * (n_treatment / n_control) if n_control > 0 else 0

            # Incremental sales (DiD approach)
            incremental_sales = treatment_sales - control_sales_scaled

            # Profit
            incremental_profit = incremental_sales * profit_margin

            # Allocate spend proportionally by treatment sales share
            total_treatment_sales = test_df[test_df['is_treatment']==True]['sales_revenue'].sum()
            channel_share = treatment_sales / total_treatment_sales if total_treatment_sales > 0 else 0
            channel_spend = total_spend * channel_share

            # ROI
            roi = (incremental_profit - channel_spend) / channel_spend if channel_spend > 0 else 0
            profit_roas = incremental_profit / channel_spend if channel_spend > 0 else 0

            channel_roi[channel] = {
                'incremental_sales': incremental_sales,
                'incremental_profit': incremental_profit,
                'allocated_spend': channel_spend,
                'profit_roas': profit_roas,
                'roi': roi,
                'roi_pct': roi * 100
            }

            print(f"   {channel}: ROAS = {profit_roas:.2f}x, ROI = {roi*100:.1f}%")

        return channel_roi
    
    def generate_summary_report(self, results: Dict):
        """
        Generate executive summary of ROI results
        """
        print("\n" + "="*70)
        print("💰 MULTI-PERIOD ROI SUMMARY")
        print("="*70)
        
        # Short-term
        st = results['short_term']
        print(f"\n📊 SHORT-TERM (Weeks 1-4):")
        print(f"   Profit ROAS: {st['profit_roas']:.2f}x")
        print(f"   ROI: {st['roi_pct']:.1f}%")
        print(f"   Incremental Profit: ${st['incremental_profit']:,.0f}")
        
        # Medium-term
        mt = results['medium_term']
        print(f"\n📊 MEDIUM-TERM (Weeks 1-12, adjusted):")
        print(f"   Profit ROAS: {mt['profit_roas']:.2f}x")
        print(f"   ROI: {mt['roi_pct']:.1f}%")
        print(f"   Incremental Profit: ${mt['incremental_profit']:,.0f}")
        if mt['stockpiling_adjustment'] > 0:
            print(f"   Stockpiling Adjustment: -${mt['stockpiling_adjustment']:,.0f}")
        
        # Long-term
        lt = results['long_term']
        print(f"\n📊 LONG-TERM (with CLV):")
        print(f"   Profit ROAS: {lt['profit_roas']:.2f}x")
        print(f"   ROI: {lt['roi_pct']:.1f}%")
        print(f"   Total Profit: ${lt['total_profit']:,.0f}")
        if lt['new_customers'] > 0:
            print(f"   New Customers: {lt['new_customers']:,}")
            print(f"   CLV Contribution: ${lt['clv_contribution']:,.0f}")
        
        # Scenarios
        print(f"\n📊 SCENARIO ANALYSIS:")
        for key, scenario in results['scenarios'].items():
            print(f"   {scenario['name']}: {scenario['roi_pct']:.1f}% {scenario['quality']}")
        
        # Best channel (if available)
        if 'channel_roi' in results and results['channel_roi']:
            best_channel = max(results['channel_roi'].items(), key=lambda x: x[1]['roi'])
            print(f"\n📊 BEST PERFORMING CHANNEL:")
            print(f"   {best_channel[0]}: ROI = {best_channel[1]['roi_pct']:.1f}%")
        
        print("\n" + "="*70)


# Test
if __name__ == "__main__":
    import json
    
    # Load data
    sales_df = pd.read_csv('data/demo/demo_sales.csv')
    media_df = pd.read_csv('data/demo/demo_media.csv')
    
    try:
        transactions_df = pd.read_csv('data/demo/demo_transactions.csv')
    except:
        transactions_df = None
    
    # Load metadata
    with open('data/demo/demo_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    # Initialize calculator
    roi_calc = MultiPeriodROI(sales_df, media_df, transactions_df)
    
    # Calculate ROI
    results = roi_calc.calculate_complete_roi(
        test_start_date=metadata['test_start_date'],
        treatment_dmas=metadata['treatment_dmas'],
        profit_margin=0.80,
        avg_clv=150.0,
        retention_rate=0.60,
        discount_rate=0.10
    )
    
    # Generate report
    roi_calc.generate_summary_report(results)