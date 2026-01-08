"""
Generate demo data with pre/test/post periods
"""

import sys
sys.path.append('src')

from data_generator_v4 import BrightlineDataGeneratorV4

print("🎯 Generating demo data v4 (with post-test period)...")

generator = BrightlineDataGeneratorV4(seed=42)

datasets = generator.generate_complete_dataset(
    n_weeks=52,              # 1 year
    n_geos=50,               # 50 markets (adequate statistical power)
    n_customers_per_geo=5,   # ~250 unique customers
    pre_period_weeks=28,     # 28 weeks pre
    test_period_weeks=12,    # 12 weeks test
    post_period_weeks=12,    # 12 weeks post
    treatment_pct=0.7,
    price_effect=0.30,
    visibility_effect=0.18,
    sustained_effect=0.12,   # 12% sustained lift post-test
    spend_increase=0.20
)

generator.save_datasets(datasets)

print("\n✅ Demo data ready with pre/test/post periods!")
print("   Run: streamlit run app/streamlit_app_ust.py")