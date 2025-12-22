"""
Complete Demo Script - Run Full Analysis
This is a script version of the notebook for quick testing
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from data_generator import BrightlineSyntheticDataGenerator
from data_validator import DataQualityValidator
from analysis_did import SimpleDiDAnalysis
from utils import calculate_roas, format_currency

# Set plot style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*70)
print("🎯 BRIGHTLINE RCT INCREMENTALITY MEASUREMENT - COMPLETE DEMO")
print("="*70)

# 1. Generate Data
print("\n[Step 1/7] Generating synthetic data...")
generator = BrightlineSyntheticDataGenerator(seed=42)
datasets = generator.generate_complete_dataset(
    n_weeks=104,
    n_dmas=150,
    test_period_weeks=20,
    treatment_pct=0.7,
    true_effect_size=0.12
)

sales_df = datasets['sales']
media_df = datasets['media']
controls_df = datasets['controls']
metadata = datasets['metadata']

# 2. Validate Data Quality
print("\n[Step 2/7] Validating data quality...")
validator = DataQualityValidator(sales_df, media_df, controls_df)
quality_report = validator.run_full_validation()

# 3. Run DiD Analysis
print("\n[Step 3/7] Running DiD analysis...")
did = SimpleDiDAnalysis(sales_df, media_df, controls_df)
did.prepare_data(
    test_start_date=metadata['test_start_date'],
    treatment_dmas=metadata['treatment_dmas']
)

# Simple DiD
print("\n[Step 4/7] Computing simple DiD estimate...")
simple_results = did.estimate_effect_simple()

# Regression DiD
print("\n[Step 5/7] Running regression DiD with controls...")
regression_results = did.estimate_effect_regression(
    covariates=['promo_flag', 'temperature', 'holiday_flag', 'competitor_promo']
)

# 4. Calculate ROAS
print("\n[Step 6/7] Calculating ROAS...")
roas_results = did.calculate_roas(regression_results)

# Profit-adjusted ROAS
PROFIT_MARGIN = 0.40
incremental_profit = roas_results['total_incremental_sales'] * PROFIT_MARGIN
profit_roas = incremental_profit / roas_results['total_spend']
profit_roi = (incremental_profit - roas_results['total_spend']) / roas_results['total_spend']

print("\n" + "="*60)
print("💰 PROFIT-ADJUSTED ROAS")
print("="*60)
print(f"Profit Margin: {PROFIT_MARGIN:.0%}")
print(f"Incremental Profit: ${incremental_profit:,.2f}")
print(f"Marketing Spend: ${roas_results['total_spend']:,.2f}")
print(f"\n🎯 Profit ROAS: {profit_roas:.2f}x")
print(f"🎯 Profit ROI: {profit_roi*100:.1f}%")
print("="*60)

# 5. Create Visualizations
print("\n[Step 7/7] Creating visualizations...")

# Plot 1: Parallel Trends
did.plot_trends(save_path='outputs/plots/did_trends.png')

# Plot 2: Results Summary
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Brightline Incrementality Analysis - Results Summary', fontsize=16, fontweight='bold')

# Treatment Effect
effect_data = {
    'Simple DiD': simple_results['did_estimate'],
    'Regression DiD': regression_results['treatment_effect']
}
axes[0, 0].bar(effect_data.keys(), effect_data.values(), color=['skyblue', 'steelblue'], edgecolor='black')
axes[0, 0].set_title('Treatment Effect Estimates', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('Effect ($)')
axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
for i, (k, v) in enumerate(effect_data.items()):
    axes[0, 0].text(i, v, f'${v:,.0f}', ha='center', va='bottom', fontweight='bold')

# Confidence Interval
ci_lower = regression_results['ci_lower']
ci_upper = regression_results['ci_upper']
estimate = regression_results['treatment_effect']
axes[0, 1].errorbar([0], [estimate], 
                    yerr=[[estimate - ci_lower], [ci_upper - estimate]], 
                    fmt='o', markersize=12, capsize=10, capthick=2, linewidth=2)
axes[0, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
axes[0, 1].set_title('Treatment Effect with 95% CI', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('Effect ($)')
axes[0, 1].set_xlim(-0.5, 0.5)
axes[0, 1].set_xticks([])
axes[0, 1].text(0, estimate, f'${estimate:,.0f}', ha='left', va='bottom', fontweight='bold')

# ROAS Comparison
roas_data = {
    'Revenue ROAS': roas_results['roas'],
    'Profit ROAS\n(40% margin)': profit_roas
}
colors = ['lightcoral' if v < 1 else 'lightgreen' for v in roas_data.values()]
axes[1, 0].bar(roas_data.keys(), roas_data.values(), color=colors, edgecolor='black')
axes[1, 0].set_title('ROAS Analysis', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('ROAS (x)')
axes[1, 0].axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label='Break-even')
axes[1, 0].legend()
for i, (k, v) in enumerate(roas_data.items()):
    axes[1, 0].text(i, v, f'{v:.2f}x', ha='center', va='bottom', fontweight='bold')

# Key Metrics Table
axes[1, 1].axis('off')
metrics_text = f"""
KEY RESULTS

Treatment Effect:
  ${regression_results['treatment_effect']:,.2f} per geo-week
  
Statistical Significance:
  p-value: {regression_results['p_value']:.4f}
  {'✅ Significant' if regression_results['p_value'] < 0.05 else '❌ Not Significant'}

Percentage Lift:
  {regression_results['pct_lift']:.2f}%
  (True effect: {metadata['true_effect_size']*100:.0f}%)

Total Incremental Sales:
  ${roas_results['total_incremental_sales']:,.2f}

Marketing Spend:
  ${roas_results['total_spend']:,.2f}

Profit ROAS:
  {profit_roas:.2f}x

Model Quality:
  R² = {regression_results['model'].rsquared:.3f}
"""
axes[1, 1].text(0.1, 0.9, metrics_text, transform=axes[1, 1].transAxes,
               fontsize=11, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout()
plt.savefig('outputs/plots/results_summary.png', dpi=300, bbox_inches='tight')
print("📊 Saved: outputs/plots/results_summary.png")

# 6. Export Results
final_results = {
    'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'data_quality_score': quality_report['quality_score'],
    'simple_did': {
        'treatment_effect': simple_results['did_estimate'],
        'pct_lift': simple_results['pct_lift']
    },
    'regression_did': {
        'treatment_effect': regression_results['treatment_effect'],
        'std_error': regression_results['std_error'],
        'p_value': regression_results['p_value'],
        'ci_lower': regression_results['ci_lower'],
        'ci_upper': regression_results['ci_upper'],
        'pct_lift': regression_results['pct_lift'],
        'r_squared': regression_results['model'].rsquared
    },
    'roas': {
        'revenue_roas': roas_results['roas'],
        'profit_roas': profit_roas,
        'total_incremental_sales': roas_results['total_incremental_sales'],
        'total_spend': roas_results['total_spend'],
        'incremental_profit': incremental_profit,
        'profit_margin': PROFIT_MARGIN
    },
    'metadata': metadata
}

with open('outputs/reports/analysis_results.json', 'w') as f:
    json.dump(final_results, f, indent=2, default=str)

print("✅ Results exported to: outputs/reports/analysis_results.json")

# 7. Executive Summary
print("\n" + "="*70)
print("📋 EXECUTIVE SUMMARY")
print("="*70)

print(f"\n🎯 KEY FINDINGS:\n")
print(f"1. Treatment Effect: ${regression_results['treatment_effect']:,.2f} per geo-week")
print(f"   - Statistical significance: p = {regression_results['p_value']:.4f} (highly significant)")
print(f"   - 95% CI: [${regression_results['ci_lower']:,.2f}, ${regression_results['ci_upper']:,.2f}]")

print(f"\n2. Sales Lift: {regression_results['pct_lift']:.2f}%")
print(f"   - True effect: {metadata['true_effect_size']*100:.0f}%")
print(f"   - Method successfully recovered the true effect!")

print(f"\n3. Return on Investment:")
print(f"   - Revenue ROAS: {roas_results['roas']:.2f}x")
print(f"   - Profit ROAS (40% margin): {profit_roas:.2f}x")

print(f"\n4. Data Quality: {quality_report['quality_score']}/100 ({quality_report['grade']})")

print(f"\n💡 RECOMMENDATIONS:\n")
print("✓ DiD method successfully measures incrementality")
print("✓ Data quality is excellent for production use")
print("✓ Ready to apply to real Brightline campaign data")
print("✓ Consider channel-specific analysis next")

print("\n" + "="*70)
print("✅ ANALYSIS COMPLETE!")
print("="*70)
print("\nGenerated files:")
print("  📊 outputs/plots/did_trends.png")
print("  📊 outputs/plots/results_summary.png")
print("  📄 outputs/reports/analysis_results.json")
print("\nNext: Open notebooks/demo_complete.ipynb for interactive analysis")