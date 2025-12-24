"""
Complete Enhanced Demo - Full Analysis Pipeline
Demonstrates all enhanced features for Brightline POV
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from data_generator import EnhancedBrightlineDataGenerator
from data_validator import DataQualityValidator
from purchase_dynamics import PurchaseDynamicsAnalyzer
from hte_analysis import HeterogeneousEffectsAnalyzer
from roi_calculator import MultiPeriodROI

print("="*80)
print("🎯 BRIGHTLINE ENHANCED RCT ANALYSIS - COMPLETE DEMO")
print("="*80)
print("\nThis demo showcases:")
print("  ✅ Multi-channel retail analysis (Store, Omnichannel, Online)")
print("  ✅ Age-based segmentation")
print("  ✅ Promotion type comparison (Price vs Visibility)")
print("  ✅ Purchase dynamics (Stockpiling vs New Customers)")
print("  ✅ Heterogeneous treatment effects")
print("  ✅ Multi-period ROI (Short/Medium/Long-term)")
print("\n" + "="*80)

# ============================================================================
# STEP 1: Generate Enhanced Synthetic Data
# ============================================================================
print("\n" + "="*80)
print("STEP 1: GENERATING ENHANCED SYNTHETIC DATA")
print("="*80)

generator = EnhancedBrightlineDataGenerator(seed=42)

datasets = generator.generate_complete_dataset(
    n_weeks=104,
    n_geos=150,
    test_period_weeks=20,
    treatment_pct=0.7,
    price_effect_size=0.15,      # 15% lift from price promos
    visibility_effect_size=0.08   # 8% lift from visibility promos
)

# Save datasets
generator.save_datasets(datasets, output_dir='data/synthetic_v2')

sales_df = datasets['sales']
transactions_df = datasets['transactions']
media_df = datasets['media']
controls_df = datasets['controls']
metadata = datasets['metadata']

print(f"\n✅ Generated:")
print(f"   • {len(sales_df):,} sales records")
print(f"   • {len(transactions_df):,} transaction records")
print(f"   • {len(media_df):,} media records")
print(f"   • Retail channels: {sales_df['retail_channel'].unique().tolist()}")
if not transactions_df.empty:
    print(f"   • Age segments: {transactions_df['age_segment'].unique().tolist()}")

# ============================================================================
# STEP 2: Data Quality Validation
# ============================================================================
print("\n" + "="*80)
print("STEP 2: DATA QUALITY VALIDATION")
print("="*80)

validator = DataQualityValidator(sales_df, media_df, controls_df)
quality_report = validator.run_full_validation()

# ============================================================================
# STEP 3: Purchase Dynamics Analysis
# ============================================================================
print("\n" + "="*80)
print("STEP 3: PURCHASE DYNAMICS ANALYSIS")
print("="*80)

dynamics_analyzer = PurchaseDynamicsAnalyzer(sales_df, transactions_df)

dynamics_results = dynamics_analyzer.analyze_complete(
    test_start_date=metadata['test_start_date'],
    treatment_dmas=metadata['treatment_dmas'],
    pre_weeks=8,
    post_weeks=8
)

# Save dynamics plot
dynamics_analyzer.plot_dynamics(
    metadata['test_start_date'],
    save_path='outputs/plots/purchase_dynamics_enhanced.png'
)

# ============================================================================
# STEP 4: Heterogeneous Treatment Effects Analysis
# ============================================================================
print("\n" + "="*80)
print("STEP 4: HETEROGENEOUS TREATMENT EFFECTS ANALYSIS")
print("="*80)

hte_analyzer = HeterogeneousEffectsAnalyzer(sales_df, transactions_df, controls_df)

hte_results = hte_analyzer.analyze_complete(
    test_start_date=metadata['test_start_date'],
    treatment_dmas=metadata['treatment_dmas']
)

# Save HTE plot
hte_analyzer.plot_hte_results(
    hte_results,
    save_path='outputs/plots/hte_analysis_enhanced.png'
)

# Generate recommendations
hte_analyzer.generate_recommendations(hte_results)

# ============================================================================
# STEP 5: Multi-Period ROI Analysis
# ============================================================================
print("\n" + "="*80)
print("STEP 5: MULTI-PERIOD ROI ANALYSIS")
print("="*80)

roi_calculator = MultiPeriodROI(
    sales_df, 
    media_df, 
    transactions_df,
    purchase_dynamics_results=dynamics_results,
    hte_results=hte_results
)

roi_results = roi_calculator.calculate_complete_roi(
    test_start_date=metadata['test_start_date'],
    treatment_dmas=metadata['treatment_dmas'],
    profit_margin=0.40,      # 40% gross margin
    avg_clv=150.0,           # $150 average CLV
    retention_rate=0.60,     # 60% retention
    discount_rate=0.10       # 10% discount rate
)

# Generate summary report
roi_calculator.generate_summary_report(roi_results)

# ============================================================================
# STEP 6: Export Complete Results
# ============================================================================
print("\n" + "="*80)
print("STEP 6: EXPORTING RESULTS")
print("="*80)

# Compile comprehensive results
final_results = {
    'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'data_quality': {
        'score': quality_report['quality_score'],
        'grade': quality_report['grade']
    },
    'purchase_dynamics': {
        'scenario': dynamics_results['scenario']['scenario'],
        'quality': dynamics_results['scenario']['quality'],
        'description': dynamics_results['scenario']['description']
    },
    'heterogeneous_effects': {
        'channel_effects': {
            k: {'pct_lift': v['pct_lift']} 
            for k, v in hte_results['channel_effects'].items()
        },
        'best_channel': max(
            hte_results['channel_effects'].items(), 
            key=lambda x: x[1]['pct_lift']
        )[0]
    },
    'roi_analysis': {
        'short_term': {
            'profit_roas': roi_results['short_term']['profit_roas'],
            'roi_pct': roi_results['short_term']['roi_pct']
        },
        'medium_term': {
            'profit_roas': roi_results['medium_term']['profit_roas'],
            'roi_pct': roi_results['medium_term']['roi_pct']
        },
        'long_term': {
            'profit_roas': roi_results['long_term']['profit_roas'],
            'roi_pct': roi_results['long_term']['roi_pct']
        },
        'best_scenario': max(
            roi_results['scenarios'].items(),
            key=lambda x: x[1]['roi']
        )[0]
    },
    'metadata': metadata
}

# Save to JSON
with open('outputs/reports/enhanced_analysis_results.json', 'w') as f:
    json.dump(final_results, f, indent=2, default=str)

print("\n✅ Results exported to: outputs/reports/enhanced_analysis_results.json")

# Save to CSV (flattened)
results_df = pd.DataFrame([{
    'analysis_date': final_results['analysis_date'],
    'data_quality_score': final_results['data_quality']['score'],
    'purchase_scenario': final_results['purchase_dynamics']['scenario'],
    'best_channel': final_results['heterogeneous_effects']['best_channel'],
    'short_term_roi': final_results['roi_analysis']['short_term']['roi_pct'],
    'medium_term_roi': final_results['roi_analysis']['medium_term']['roi_pct'],
    'long_term_roi': final_results['roi_analysis']['long_term']['roi_pct'],
    'best_scenario': final_results['roi_analysis']['best_scenario']
}])

results_df.to_csv('outputs/reports/enhanced_analysis_summary.csv', index=False)
print("✅ Summary saved to: outputs/reports/enhanced_analysis_summary.csv")

# ============================================================================
# STEP 7: Executive Summary
# ============================================================================
print("\n" + "="*80)
print("📋 EXECUTIVE SUMMARY - ENHANCED BRIGHTLINE ANALYSIS")
print("="*80)

print(f"\n🎯 KEY FINDINGS:\n")

# Data Quality
print(f"1. DATA QUALITY: {quality_report['grade']}")
print(f"   • Score: {quality_report['quality_score']}/100")
print(f"   • {quality_report['recommendation']}")

# Purchase Dynamics
scenario = dynamics_results['scenario']
print(f"\n2. PURCHASE BEHAVIOR: {scenario['scenario']}")
print(f"   • Quality: {scenario['quality']}")
print(f"   • {scenario['description']}")

if dynamics_results['new_customers']:
    nc = dynamics_results['new_customers']
    print(f"   • New customers: {nc['new_customers']:,} ({nc['new_customer_rate_pct']:.1f}%)")
    print(f"   • Repeat rate: {nc['repeat_rate_pct']:.1f}%")

# Heterogeneous Effects
best_channel = max(hte_results['channel_effects'].items(), key=lambda x: x[1]['pct_lift'])
print(f"\n3. BEST PERFORMING CHANNEL: {best_channel[0]}")
print(f"   • Lift: {best_channel[1]['pct_lift']:.2f}%")

if hte_results['age_effects']:
    best_age = max(hte_results['age_effects'].items(), key=lambda x: x[1]['pct_lift'])
    print(f"\n4. MOST RESPONSIVE AGE: {best_age[0]}")
    print(f"   • Lift: {best_age[1]['pct_lift']:.2f}%")

# ROI
print(f"\n5. RETURN ON INVESTMENT:")
print(f"   • Short-term (Weeks 1-4): {roi_results['short_term']['roi_pct']:.1f}%")
print(f"   • Medium-term (Weeks 1-12): {roi_results['medium_term']['roi_pct']:.1f}%")
print(f"   • Long-term (with CLV): {roi_results['long_term']['roi_pct']:.1f}%")

best_scenario = max(roi_results['scenarios'].items(), key=lambda x: x[1]['roi'])
print(f"\n6. BEST CASE SCENARIO: {best_scenario[1]['name']}")
print(f"   • ROI: {best_scenario[1]['roi_pct']:.1f}%")
print(f"   • {best_scenario[1]['description']}")

print(f"\n💡 STRATEGIC RECOMMENDATIONS:\n")

# Channel recommendation
print(f"✓ Focus marketing investment on {best_channel[0]} channel")
print(f"  (Delivers {best_channel[1]['pct_lift']:.1f}% lift vs other channels)")

# Promo type recommendation
if hte_results['promo_effects'] and len(hte_results['promo_effects']) > 0:
    if 'No_Promo_Data' not in hte_results['promo_effects']:
        best_promo = max(hte_results['promo_effects'].items(), key=lambda x: x[1]['pct_lift'])
        print(f"✓ Prioritize {best_promo[0]} promotions")
        print(f"  (Generates {best_promo[1]['pct_lift']:.1f}% incremental lift)")

# Age targeting
if hte_results['age_effects']:
    best_age = max(hte_results['age_effects'].items(), key=lambda x: x[1]['pct_lift'])
    print(f"✓ Target {best_age[0]} age segment")
    print(f"  (Most price-responsive with {best_age[1]['pct_lift']:.1f}% lift)")

# Purchase dynamics insight
if scenario['scenario'] == 'NEW_CUSTOMER_ACQUISITION':
    print(f"✓ Continue customer acquisition focus")
    print(f"  (High CLV potential with {roi_results['long_term']['roi_pct']:.1f}% long-term ROI)")
elif scenario['scenario'] == 'STOCKPILING':
    print(f"⚠ Reduce price promotion frequency")
    print(f"  (Current promos show pull-forward effect)")
    print(f"✓ Shift to visibility/positioning tactics")

print("\n" + "="*80)
print("✅ ENHANCED ANALYSIS COMPLETE!")
print("="*80)
print("\nGenerated files:")
print("  📊 outputs/plots/purchase_dynamics_enhanced.png")
print("  📊 outputs/plots/hte_analysis_enhanced.png")
print("  📄 outputs/reports/enhanced_analysis_results.json")
print("  📄 outputs/reports/enhanced_analysis_summary.csv")
print("\n" + "="*80)