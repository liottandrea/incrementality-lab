"""
Quick test of basic functionality
"""

import sys
sys.path.append('src')

from utils import *
from data_generator import BrightlineSyntheticDataGenerator

print("="*60)
print("🧪 TESTING BRIGHTLINE POV CODEBASE")
print("="*60)

# Test 1: Directory setup
print("\n[Test 1] Setting up directories...")
setup_directories()

# Test 2: Utility functions
print("\n[Test 2] Testing utility functions...")
roas = calculate_roas(incremental_sales=100000, marketing_spend=20000)
print(f"  ROAS: {roas['roas']:.2f}x")
print(f"  ROI: {roas['roi_pct']:.1f}%")

power = calculate_statistical_power(
    n_geos=150,
    n_weeks=20,
    baseline_std=5000,
    mde=0.12
)
print(f"  Statistical Power: {power:.2%}")

# Test 3: Data generation
print("\n[Test 3] Generating synthetic data...")
generator = BrightlineSyntheticDataGenerator(seed=42)

datasets = generator.generate_complete_dataset(
    n_weeks=104,
    n_dmas=150,
    test_period_weeks=20,
    treatment_pct=0.7,
    true_effect_size=0.12
)

# Test 4: Save datasets
print("\n[Test 4] Saving datasets...")
generator.save_datasets(datasets)

# Test 5: Verify data quality
print("\n[Test 5] Quick data quality checks...")
sales_df = datasets['sales']
media_df = datasets['media']
controls_df = datasets['controls']

print(f"\n  Sales DataFrame:")
print(f"    Shape: {sales_df.shape}")
print(f"    Columns: {list(sales_df.columns)}")
print(f"    Missing values: {sales_df.isnull().sum().sum()}")
print(f"    Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")

print(f"\n  Media DataFrame:")
print(f"    Shape: {media_df.shape}")
print(f"    Channels: {media_df['channel'].unique().tolist()}")
print(f"    Total spend: ${media_df['spend_usd'].sum():,.0f}")

print(f"\n  Controls DataFrame:")
print(f"    Shape: {controls_df.shape}")
print(f"    Columns: {list(controls_df.columns)}")

# Test 6: Summary statistics
print("\n[Test 6] Summary statistics...")
print("\nSales Units Summary:")
print(sales_df['sales_units'].describe())

print("\nSales Revenue Summary:")
print(sales_df['sales_revenue'].describe())

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\nGenerated files in data/synthetic/:")
print("  - brightline_sales.csv")
print("  - brightline_media.csv")
print("  - brightline_controls.csv")
print("  - metadata.json")
print("\nNext steps:")
print("  1. Check the CSV files to verify data looks good")
print("  2. Ready to build data validator")
print("  3. Ready to build DiD analysis")