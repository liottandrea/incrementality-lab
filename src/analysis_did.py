"""
METHOD 1: Simple Difference-in-Differences Analysis
- Easy to understand and explain to stakeholders
- Fast to run
- Good baseline for comparison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Try to import statsmodels (for regression)
try:
    import statsmodels.formula.api as smf
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    print("⚠️  statsmodels not available. Install with: pip install statsmodels")


class SimpleDiDAnalysis:
    """
    Difference-in-Differences estimator
    """
    
    def __init__(self, sales_df, media_df, controls_df=None):
        """
        Initialize DiD analysis
        
        Args:
            sales_df: Sales data with date, geo_id, sales_revenue
            media_df: Media data with treatment information
            controls_df: Optional control variables
        """
        self.sales_df = sales_df.copy()
        self.media_df = media_df.copy()
        self.controls_df = controls_df.copy() if controls_df is not None else None
        self.results = None
        self.data = None
        
    def prepare_data(self, test_start_date, treatment_dmas):
        """
        Prepare data for DiD analysis
        
        Args:
            test_start_date: When the test started
            treatment_dmas: List of DMAs in treatment group
        """
        print("📊 Preparing data for DiD analysis...")
        
        # Merge sales with media spend
        df = self.sales_df.copy()
        
        # Add total spend per geo-week
        spend_by_geo = self.media_df.groupby(['date', 'geo_id'])['spend_usd'].sum().reset_index()
        df = df.merge(spend_by_geo, on=['date', 'geo_id'], how='left')
        
        # Add controls if available
        if self.controls_df is not None:
            df = df.merge(self.controls_df, on=['date', 'geo_id'], how='left')
        
        # Convert date
        df['date'] = pd.to_datetime(df['date'])
        test_start_date = pd.to_datetime(test_start_date)
        
        # Create treatment indicators
        df['is_treatment'] = df['geo_id'].isin(treatment_dmas).astype(int)
        df['is_post'] = (df['date'] >= test_start_date).astype(int)
        df['treatment_x_post'] = df['is_treatment'] * df['is_post']
        
        self.data = df
        
        print(f"✅ Data prepared:")
        print(f"   Total observations: {len(df):,}")
        print(f"   Pre-period: {(df['is_post']==0).sum():,} observations")
        print(f"   Post-period: {(df['is_post']==1).sum():,} observations")
        print(f"   Treatment geos: {df['is_treatment'].sum() // len(df['date'].unique())}")
        print(f"   Control geos: {(1-df['is_treatment']).sum() // len(df['date'].unique())}")
        
        return df
    
    def estimate_effect_simple(self):
        """
        Simple DiD: Compare treatment vs control in pre vs post
        """
        print("\n📈 Running Simple DiD Estimation...")
        
        df = self.data
        
        # Calculate means for each group
        pre_treatment = df[(df['is_post']==0) & (df['is_treatment']==1)]['sales_revenue'].mean()
        pre_control = df[(df['is_post']==0) & (df['is_treatment']==0)]['sales_revenue'].mean()
        post_treatment = df[(df['is_post']==1) & (df['is_treatment']==1)]['sales_revenue'].mean()
        post_control = df[(df['is_post']==1) & (df['is_treatment']==0)]['sales_revenue'].mean()
        
        # DiD estimate
        treatment_change = post_treatment - pre_treatment
        control_change = post_control - pre_control
        did_estimate = treatment_change - control_change
        
        # Percentage lift
        pct_lift = (did_estimate / pre_control) * 100
        
        print("\n" + "="*60)
        print("📊 SIMPLE DiD RESULTS")
        print("="*60)
        print(f"\nPre-period:")
        print(f"  Treatment avg: ${pre_treatment:,.2f}")
        print(f"  Control avg:   ${pre_control:,.2f}")
        print(f"\nPost-period:")
        print(f"  Treatment avg: ${post_treatment:,.2f}")
        print(f"  Control avg:   ${post_control:,.2f}")
        print(f"\nChanges:")
        print(f"  Treatment change: ${treatment_change:,.2f}")
        print(f"  Control change:   ${control_change:,.2f}")
        print(f"\n🎯 DiD Estimate: ${did_estimate:,.2f}")
        print(f"🎯 Percentage Lift: {pct_lift:.2f}%")
        print("="*60)
        
        return {
            'did_estimate': did_estimate,
            'pct_lift': pct_lift,
            'pre_treatment': pre_treatment,
            'pre_control': pre_control,
            'post_treatment': post_treatment,
            'post_control': post_control
        }
    
    def estimate_effect_regression(self, covariates=None):
        """
        Regression-based DiD with standard errors
        
        Model: Y = β0 + β1*Treatment + β2*Post + β3*Treatment*Post + controls + ε
        β3 is the DiD estimate
        """
        if not HAS_STATSMODELS:
            print("⚠️  Regression requires statsmodels. Using simple method instead.")
            return self.estimate_effect_simple()
        
        print("\n📈 Running Regression-based DiD...")
        
        df = self.data
        
        # Build formula
        formula = "sales_revenue ~ is_treatment + is_post + treatment_x_post"
        
        # Add covariates
        if covariates:
            available_covariates = [c for c in covariates if c in df.columns]
            if available_covariates:
                formula += " + " + " + ".join(available_covariates)
        
        # Add geo fixed effects (absorbs time-invariant differences)
        formula += " + C(geo_id)"
        
        print(f"   Model: {formula}\n")
        
        # Fit model with clustered standard errors
        try:
            model = smf.ols(formula, data=df).fit(
                cov_type='cluster',
                cov_kwds={'groups': df['geo_id']}
            )
        except:
            # Fallback without clustering
            model = smf.ols(formula, data=df).fit()
        
        # Extract results
        did_coef = model.params['treatment_x_post']
        std_error = model.bse['treatment_x_post']
        p_value = model.pvalues['treatment_x_post']
        ci_lower, ci_upper = model.conf_int().loc['treatment_x_post']
        
        # Calculate percentage lift
        baseline = df[(df['is_treatment']==0) & (df['is_post']==0)]['sales_revenue'].mean()
        pct_lift = (did_coef / baseline) * 100
        
        # Print results
        print("\n" + "="*60)
        print("📈 REGRESSION DiD RESULTS")
        print("="*60)
        print(f"\nTreatment Effect: ${did_coef:,.2f}")
        print(f"Standard Error:   ${std_error:,.2f}")
        print(f"95% CI: [${ci_lower:,.2f}, ${ci_upper:,.2f}]")
        print(f"P-value: {p_value:.4f}")
        print(f"Percentage Lift: {pct_lift:.2f}%")
        
        if p_value < 0.05:
            print("\n✅ Effect is statistically significant (p < 0.05)")
        else:
            print("\n⚠️  Effect is NOT statistically significant (p ≥ 0.05)")
        
        print(f"\nModel R-squared: {model.rsquared:.3f}")
        print("="*60)
        
        self.results = {
            'treatment_effect': did_coef,
            'std_error': std_error,
            'p_value': p_value,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'pct_lift': pct_lift,
            'baseline_sales': baseline,
            'model': model
        }
        
        return self.results
    
    def calculate_roas(self, results):
        """
        Calculate Return on Ad Spend
        """
        df = self.data
        
        # Total incremental sales in test period
        n_weeks_test = df[df['is_post']==1]['date'].nunique()
        n_geos_treatment = df[df['is_treatment']==1]['geo_id'].nunique()
        
        incremental_sales_per_geo_week = results['treatment_effect']
        total_incremental_sales = incremental_sales_per_geo_week * n_weeks_test * n_geos_treatment
        
        # Total spend in test period (treatment group only)
        test_spend = df[(df['is_post']==1) & (df['is_treatment']==1)]['spend_usd'].sum()
        
        # ROAS
        roas = total_incremental_sales / test_spend if test_spend > 0 else 0
        roi = (total_incremental_sales - test_spend) / test_spend if test_spend > 0 else 0
        
        print("\n" + "="*60)
        print("💰 ROAS CALCULATION")
        print("="*60)
        print(f"Total Incremental Sales: ${total_incremental_sales:,.2f}")
        print(f"Total Marketing Spend:   ${test_spend:,.2f}")
        print(f"\n🎯 ROAS: {roas:.2f}x")
        print(f"🎯 ROI: {roi*100:.1f}%")
        print("="*60)
        
        return {
            'total_incremental_sales': total_incremental_sales,
            'total_spend': test_spend,
            'roas': roas,
            'roi': roi
        }
    
    def plot_trends(self, save_path='outputs/plots/did_trends.png'):
        """
        Visualize parallel trends
        """
        import os
        os.makedirs('outputs/plots', exist_ok=True)
        
        df = self.data
        
        # Aggregate by week and treatment status
        trends = df.groupby(['date', 'is_treatment'])['sales_revenue'].mean().reset_index()
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for treatment in [0, 1]:
            subset = trends[trends['is_treatment'] == treatment]
            label = "Treatment" if treatment == 1 else "Control"
            color = 'blue' if treatment == 1 else 'red'
            ax.plot(subset['date'], subset['sales_revenue'], 
                   marker='o', label=label, linewidth=2, color=color, alpha=0.7)
        
        # Mark test period
        test_start = df[df['is_post']==1]['date'].min()
        ax.axvline(test_start, color='green', linestyle='--', 
                  label='Test Start', linewidth=2)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Average Sales Revenue', fontsize=12)
        ax.set_title('Parallel Trends: Treatment vs Control', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path is not None:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n📊 Saved plot: {save_path}")
    
        return fig


# Quick test
if __name__ == "__main__":
    import json
    
    # Load data
    sales_df = pd.read_csv('data/synthetic/brightline_sales.csv')
    media_df = pd.read_csv('data/synthetic/brightline_media.csv')
    controls_df = pd.read_csv('data/synthetic/brightline_controls.csv')
    
    # Load metadata
    with open('data/synthetic/metadata.json', 'r') as f:
        metadata = json.load(f)
    
    # Initialize analysis
    did = SimpleDiDAnalysis(sales_df, media_df, controls_df)
    
    # Prepare data
    did.prepare_data(
        test_start_date=metadata['test_start_date'],
        treatment_dmas=metadata['treatment_dmas']
    )
    
    # Run simple DiD
    simple_results = did.estimate_effect_simple()
    
    # Run regression DiD (if statsmodels available)
    if HAS_STATSMODELS:
        regression_results = did.estimate_effect_regression(
            covariates=['promo_flag', 'temperature', 'holiday_flag']
        )
        
        # Calculate ROAS
        roas_results = did.calculate_roas(regression_results)
    
    # Plot trends
    did.plot_trends()
    
    print("\n✅ DiD Analysis Complete!")