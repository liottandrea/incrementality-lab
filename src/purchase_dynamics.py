"""
Purchase Dynamics Analyzer
Detects stockpiling, new customer acquisition, and category expansion
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple
import warnings
warnings.filterwarnings('ignore')


class PurchaseDynamicsAnalyzer:
    """
    Analyze purchase behavior patterns:
    1. Stockpiling (pull-forward effect)
    2. New customer acquisition
    3. Category expansion
    """
    
    def __init__(self, sales_df, transactions_df=None):
        """
        Initialize analyzer
        
        Args:
            sales_df: Aggregate sales data
            transactions_df: Transaction-level data (optional, for detailed analysis)
        """
        self.sales_df = sales_df.copy()
        self.transactions_df = transactions_df.copy() if transactions_df is not None else None
        self.has_transaction_data = transactions_df is not None and not transactions_df.empty
        
    def analyze_complete(self, test_start_date, treatment_dmas, pre_weeks=8, post_weeks=8):
        """
        Run complete purchase dynamics analysis
        
        Args:
            test_start_date: When test period started
            treatment_dmas: List of treatment DMAs
            pre_weeks: Weeks before test to analyze
            post_weeks: Weeks after test to analyze
        
        Returns:
            Dictionary with all analysis results
        """
        print("🔬 Analyzing Purchase Dynamics...")
        
        # Prepare data
        self.sales_df['date'] = pd.to_datetime(self.sales_df['date'])
        test_start_date = pd.to_datetime(test_start_date)
        
        self.sales_df['is_treatment'] = self.sales_df['geo_id'].isin(treatment_dmas)
        self.sales_df['is_test_period'] = self.sales_df['date'] >= test_start_date
        
        results = {}
        
        # 1. Stockpiling detection
        print("\n1️⃣ Detecting stockpiling behavior...")
        stockpiling = self.detect_stockpiling(test_start_date, pre_weeks, post_weeks)
        results['stockpiling'] = stockpiling
        
        # 2. New customer acquisition (if transaction data available)
        if self.has_transaction_data:
            print("\n2️⃣ Analyzing new customer acquisition...")
            new_customers = self.analyze_new_customers(test_start_date)
            results['new_customers'] = new_customers
        else:
            print("\n2️⃣ Skipping new customer analysis (no transaction data)")
            results['new_customers'] = None
        
        # 3. Category expansion
        print("\n3️⃣ Measuring category expansion...")
        expansion = self.measure_category_expansion(test_start_date, pre_weeks, post_weeks)
        results['category_expansion'] = expansion
        
        # 4. Classify scenario
        print("\n4️⃣ Classifying promo scenario...")
        scenario = self.classify_scenario(stockpiling, expansion, results['new_customers'])
        results['scenario'] = scenario
        
        print("\n✅ Purchase dynamics analysis complete!")
        return results
    
    def detect_stockpiling(self, test_start_date, pre_weeks=8, post_weeks=8):
        """
        Detect stockpiling by looking for post-promotion dip
        
        Stockpiling signature:
        - Spike during promotion
        - Dip after promotion
        - Net effect close to zero
        """
        df = self.sales_df.copy()
        
        # Define periods
        test_end_date = test_start_date + pd.Timedelta(weeks=4)  # Assume 4-week test
        post_start = test_end_date
        post_end = post_start + pd.Timedelta(weeks=post_weeks)
        pre_start = test_start_date - pd.Timedelta(weeks=pre_weeks)
        
        # Calculate average sales in each period
        results = {}
        
        for is_treatment in [True, False]:
            group_name = "Treatment" if is_treatment else "Control"
            group_df = df[df['is_treatment'] == is_treatment]
            
            # Pre-period baseline
            pre = group_df[
                (group_df['date'] >= pre_start) & 
                (group_df['date'] < test_start_date)
            ]['sales_revenue'].mean()
            
            # During test
            during = group_df[
                (group_df['date'] >= test_start_date) & 
                (group_df['date'] < test_end_date)
            ]['sales_revenue'].mean()
            
            # Post test
            post = group_df[
                (group_df['date'] >= post_start) & 
                (group_df['date'] < post_end)
            ]['sales_revenue'].mean()
            
            # Calculate changes
            during_lift = ((during - pre) / pre) * 100
            post_change = ((post - pre) / pre) * 100
            net_effect = during_lift + post_change
            
            # Stockpiling ratio: how much of the lift was pulled forward?
            if during_lift > 0:
                stockpiling_ratio = abs(post_change) / during_lift
            else:
                stockpiling_ratio = 0
            
            results[group_name] = {
                'pre_period_avg': pre,
                'during_period_avg': during,
                'post_period_avg': post,
                'during_lift_pct': during_lift,
                'post_change_pct': post_change,
                'net_effect_pct': net_effect,
                'stockpiling_ratio': stockpiling_ratio
            }
        
        # Calculate treatment vs control
        treatment = results['Treatment']
        control = results['Control']
        
        did_during = treatment['during_lift_pct'] - control['during_lift_pct']
        did_post = treatment['post_change_pct'] - control['post_change_pct']
        
        # Classification
        if did_during > 5 and did_post < -3:
            classification = "HIGH_STOCKPILING"
            severity = "Severe pull-forward effect"
        elif did_during > 5 and did_post < 0:
            classification = "MODERATE_STOCKPILING"
            severity = "Some pull-forward effect"
        elif did_during > 5 and did_post >= 0:
            classification = "NO_STOCKPILING"
            severity = "True incremental lift"
        else:
            classification = "UNCLEAR"
            severity = "Insufficient lift to measure"
        
        results['summary'] = {
            'did_during_lift': did_during,
            'did_post_change': did_post,
            'classification': classification,
            'severity': severity
        }
        
        # Print results
        print(f"\n   Treatment during lift: {treatment['during_lift_pct']:.1f}%")
        print(f"   Treatment post change: {treatment['post_change_pct']:.1f}%")
        print(f"   Stockpiling ratio: {treatment['stockpiling_ratio']:.2f}")
        print(f"   Classification: {classification} - {severity}")
        
        return results
    
    def analyze_new_customers(self, test_start_date):
        """
        Analyze new customer acquisition (requires transaction data)
        """
        if not self.has_transaction_data:
            return None
        
        df = self.transactions_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        test_start_date = pd.to_datetime(test_start_date)
        
        # Identify new customers
        df['is_test_period'] = df['date'] >= test_start_date
        
        # New customers during test
        test_customers = df[df['is_test_period']]
        new_customers_test = test_customers[test_customers['is_new_customer'] == True]
        
        # Calculate metrics
        total_customers_test = test_customers['customer_id'].nunique()
        n_new_customers = new_customers_test['customer_id'].nunique()
        new_customer_rate = (n_new_customers / total_customers_test) * 100
        
        # Revenue from new customers
        new_customer_revenue = new_customers_test['revenue'].sum()
        total_test_revenue = test_customers['revenue'].sum()
        new_customer_revenue_share = (new_customer_revenue / total_test_revenue) * 100
        
        # Repeat purchase analysis (customers who bought again)
        # Group by customer and check if they have multiple purchases
        customer_purchases = df.groupby('customer_id').agg({
            'date': 'count',
            'revenue': 'sum',
            'is_new_customer': 'first'
        }).rename(columns={'date': 'n_purchases'})
        
        new_cust_ids = new_customers_test['customer_id'].unique()
        new_cust_purchases = customer_purchases[customer_purchases.index.isin(new_cust_ids)]
        
        repeat_customers = (new_cust_purchases['n_purchases'] > 1).sum()
        repeat_rate = (repeat_customers / n_new_customers * 100) if n_new_customers > 0 else 0
        
        results = {
            'total_customers_in_test': total_customers_test,
            'new_customers': n_new_customers,
            'new_customer_rate_pct': new_customer_rate,
            'new_customer_revenue': new_customer_revenue,
            'new_customer_revenue_share_pct': new_customer_revenue_share,
            'repeat_customers': repeat_customers,
            'repeat_rate_pct': repeat_rate
        }
        
        print(f"\n   New customers: {n_new_customers:,} ({new_customer_rate:.1f}% of test customers)")
        print(f"   New customer revenue: ${new_customer_revenue:,.0f} ({new_customer_revenue_share:.1f}% of test revenue)")
        print(f"   Repeat rate: {repeat_rate:.1f}%")
        
        return results
    
    def measure_category_expansion(self, test_start_date, pre_weeks=8, post_weeks=8):
        """
        Measure true category expansion (sustained lift without dip)
        """
        df = self.sales_df.copy()
        
        test_end_date = test_start_date + pd.Timedelta(weeks=4)
        post_start = test_end_date
        post_end = post_start + pd.Timedelta(weeks=post_weeks)
        pre_start = test_start_date - pd.Timedelta(weeks=pre_weeks)
        
        # Treatment group only
        treatment_df = df[df['is_treatment'] == True]
        
        # Calculate periods
        pre_avg = treatment_df[
            (treatment_df['date'] >= pre_start) & 
            (treatment_df['date'] < test_start_date)
        ]['sales_revenue'].mean()
        
        during_avg = treatment_df[
            (treatment_df['date'] >= test_start_date) & 
            (treatment_df['date'] < test_end_date)
        ]['sales_revenue'].mean()
        
        post_avg = treatment_df[
            (treatment_df['date'] >= post_start) & 
            (treatment_df['date'] < post_end)
        ]['sales_revenue'].mean()
        
        # Sustained lift = post period still above pre period
        during_lift = ((during_avg - pre_avg) / pre_avg) * 100
        sustained_lift = ((post_avg - pre_avg) / pre_avg) * 100
        
        # Category expansion = sustained lift with no dip
        if sustained_lift > 3:  # At least 3% sustained
            classification = "TRUE_EXPANSION"
            explanation = "Sustained lift indicates real category growth"
        elif during_lift > 5 and sustained_lift < 2:
            classification = "TEMPORARY_BOOST"
            explanation = "Lift not sustained, likely promotional effect only"
        else:
            classification = "MINIMAL_IMPACT"
            explanation = "Insufficient evidence of category expansion"
        
        results = {
            'pre_avg': pre_avg,
            'during_avg': during_avg,
            'post_avg': post_avg,
            'during_lift_pct': during_lift,
            'sustained_lift_pct': sustained_lift,
            'classification': classification,
            'explanation': explanation
        }
        
        print(f"\n   During lift: {during_lift:.1f}%")
        print(f"   Sustained lift: {sustained_lift:.1f}%")
        print(f"   Classification: {classification}")
        
        return results
    
    def classify_scenario(self, stockpiling, expansion, new_customers):
        """
        Classify overall promotion scenario
        """
        stockpiling_class = stockpiling['summary']['classification']
        expansion_class = expansion['classification']
        
        # Determine dominant scenario
        if stockpiling_class == "HIGH_STOCKPILING":
            scenario = "STOCKPILING"
            quality = "❌ Poor"
            description = "Promotion mostly pulled forward future purchases"
            
        elif expansion_class == "TRUE_EXPANSION" and new_customers and new_customers['new_customer_rate_pct'] > 20:
            scenario = "NEW_CUSTOMER_ACQUISITION"
            quality = "✅ Excellent"
            description = "Attracted new customers with sustained purchases"
            
        elif expansion_class == "TRUE_EXPANSION":
            scenario = "CATEGORY_EXPANSION"
            quality = "✅ Good"
            description = "Existing customers buying more with sustained lift"
            
        elif stockpiling_class == "MODERATE_STOCKPILING":
            scenario = "MIXED"
            quality = "⚠️ Fair"
            description = "Some real lift but also some pull-forward effect"
            
        else:
            scenario = "UNCLEAR"
            quality = "⚠️ Uncertain"
            description = "Insufficient evidence to classify"
        
        return {
            'scenario': scenario,
            'quality': quality,
            'description': description,
            'stockpiling_component': stockpiling_class,
            'expansion_component': expansion_class
        }
    
    def plot_dynamics(self, test_start_date, save_path='outputs/plots/purchase_dynamics.png'):
        """
        Visualize purchase dynamics over time
        """
        import os
        os.makedirs('outputs/plots', exist_ok=True)
        
        df = self.sales_df.copy()
        
        # Aggregate by week and treatment
        weekly = df.groupby(['date', 'is_treatment'])['sales_revenue'].mean().reset_index()
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        for is_treatment in [True, False]:
            subset = weekly[weekly['is_treatment'] == is_treatment]
            label = "Treatment" if is_treatment else "Control"
            color = 'blue' if is_treatment else 'red'
            ax.plot(subset['date'], subset['sales_revenue'], 
                   marker='o', label=label, linewidth=2, color=color, alpha=0.7)
        
        # Mark periods
        test_start = pd.to_datetime(test_start_date)
        test_end = test_start + pd.Timedelta(weeks=4)
        
        ax.axvline(test_start, color='green', linestyle='--', label='Test Start', linewidth=2)
        ax.axvline(test_end, color='orange', linestyle='--', label='Test End', linewidth=2)
        
        # Shade test period
        ax.axvspan(test_start, test_end, alpha=0.1, color='green', label='Test Period')
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Average Sales Revenue', fontsize=12)
        ax.set_title('Purchase Dynamics: Detecting Stockpiling & Category Expansion', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path is not None:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n📊 Saved: {save_path}")

        return fig

# Test
if __name__ == "__main__":
    # Load enhanced data
    sales_df = pd.read_csv('data/synthetic_v2/brightline_sales_v2.csv')
    
    # Try to load transactions
    try:
        transactions_df = pd.read_csv('data/synthetic_v2/brightline_transactions_v2.csv')
    except:
        transactions_df = None
    
    # Load metadata
    import json
    with open('data/synthetic_v2/metadata_v2.json', 'r') as f:
        metadata = json.load(f)
    
    # Run analysis
    analyzer = PurchaseDynamicsAnalyzer(sales_df, transactions_df)
    
    results = analyzer.analyze_complete(
        test_start_date=metadata['test_start_date'],
        treatment_dmas=metadata['treatment_dmas'],
        pre_weeks=8,
        post_weeks=8
    )
    
    # Plot
    analyzer.plot_dynamics(metadata['test_start_date'])
    
    # Print summary
    print("\n" + "="*60)
    print("📊 PURCHASE DYNAMICS SUMMARY")
    print("="*60)
    
    scenario = results['scenario']
    print(f"\nScenario: {scenario['scenario']}")
    print(f"Quality: {scenario['quality']}")
    print(f"Description: {scenario['description']}")
    
    print("\n" + "="*60)