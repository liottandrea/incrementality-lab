"""
Generate and save optimized demo data for instant loading
"""

import sys
sys.path.append('src')

from src.data_generator_v3 import BrightlineDataGeneratorV3
import pandas as pd

print("🎯 Generating optimized demo data...")

generator = BrightlineDataGeneratorV3(seed=43)

# Generate smaller dataset for quick loading
datasets = generator.generate_complete_dataset(
    n_weeks=104,          # 1 year (vs 104)
    n_geos=100,          # 100 DMAs (vs 150)
    test_period_weeks=20, # 12 weeks (vs 20)
    treatment_pct=0.7,
    price_effect=0.18,
    visibility_effect=0.10,
    spend_increase=0.25
)

# Save to demo folder
import os
os.makedirs('data/demo', exist_ok=True)

print("\n💾 Saving demo data...")

datasets['sales'].to_csv('data/demo/demo_sales.csv', index=False)
datasets['transactions'].to_csv('data/demo/demo_transactions.csv', index=False)
datasets['media'].to_csv('data/demo/demo_media.csv', index=False)
datasets['controls'].to_csv('data/demo/demo_controls.csv', index=False)

import json
with open('data/demo/demo_metadata.json', 'w') as f:
    json.dump(datasets['metadata'], f, indent=2)

print("\n✅ Demo data saved!")
print(f"   Location: data/demo/")
print(f"   Sales: {len(datasets['sales']):,} records")
print(f"   Transactions: {len(datasets['transactions']):,} records")
print(f"   File size: ~{(len(datasets['sales']) + len(datasets['transactions']))/1000:.0f}K records")