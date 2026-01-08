"""
Brightline Data Generator v3 - FIXED for Positive ROI

Retail Dimensions:
1. Store: Visibility promos only (positioning, graphics)
2. Omnichannel: Transaction-level data with age, all promo types
3. Online Specialty: Transaction-level data with age, digital promos

Promo Types:
- Price: Discounts, BOGO (NOT in Store channel)
- Visibility: Positioning, endcaps, graphics (ALL channels)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict
import json


class BrightlineDataGeneratorV3:
    """
    Complete data generator matching Brightline business model
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.seed = seed
        
        # Retail channel configuration
        self.retail_channels = {
            'Store': {
                'weight': 0.50,
                'has_transaction_data': False,
                'allowed_promos': ['Visibility', 'None'],
                'description': 'Physical stores - aggregate data only'
            },
            'Omnichannel': {
                'weight': 0.30,
                'has_transaction_data': True,
                'allowed_promos': ['Price', 'Visibility', 'None'],
                'description': 'Online + Physical - transaction-level with age data'
            },
            'Online_Specialty': {
                'weight': 0.20,
                'has_transaction_data': True,
                'allowed_promos': ['Price', 'Visibility', 'None'],
                'description': 'Specialized online retailers - transaction-level with age data'
            }
        }
        
        self.age_segments = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        
        self.age_responses = {
            '18-24': {'price_sensitivity': 0.20, 'visibility_response': 0.10, 'base_purchase_rate': 0.05},
            '25-34': {'price_sensitivity': 0.18, 'visibility_response': 0.12, 'base_purchase_rate': 0.07},
            '35-44': {'price_sensitivity': 0.15, 'visibility_response': 0.14, 'base_purchase_rate': 0.09},
            '45-54': {'price_sensitivity': 0.12, 'visibility_response': 0.15, 'base_purchase_rate': 0.10},
            '55-64': {'price_sensitivity': 0.10, 'visibility_response': 0.16, 'base_purchase_rate': 0.11},
            '65+':   {'price_sensitivity': 0.08, 'visibility_response': 0.18, 'base_purchase_rate': 0.12}
        }
    
    def generate_complete_dataset(
        self,
        n_weeks: int = 52,
        n_geos: int = 100,
        start_date: str = '2024-01-01',
        test_period_weeks: int = 12,
        treatment_pct: float = 0.7,
        price_effect: float = 0.30,      # INCREASED from 0.15 to 0.30 (30% lift)
        visibility_effect: float = 0.18,  # INCREASED from 0.08 to 0.18 (18% lift)
        spend_increase: float = 0.20      # DECREASED from 0.30 to 0.20 (20% more spend)
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate complete dataset
        """
        print(f"🎯 Generating Brightline data v3...")
        print(f"   Weeks: {n_weeks} | DMAs: {n_geos}")
        print(f"   Test period: Last {test_period_weeks} weeks")
        print(f"   Price effect: {price_effect*100:.0f}% | Visibility effect: {visibility_effect*100:.0f}%")
        print(f"   Spend increase: {spend_increase*100:.0f}%")
        
        dates = pd.date_range(start=start_date, periods=n_weeks, freq='W-SUN')
        dmas = [f"DMA_{str(i).zfill(3)}" for i in range(1, n_geos + 1)]
        
        test_start_idx = n_weeks - test_period_weeks
        test_start_date = dates[test_start_idx]
        
        n_treatment = int(n_geos * treatment_pct)
        treatment_dmas = np.random.choice(dmas, size=n_treatment, replace=False)
        
        print(f"   Treatment: {len(treatment_dmas)} DMAs | Control: {n_geos - len(treatment_dmas)} DMAs")
        
        all_sales = []
        all_transactions = []
        all_media = []
        all_controls = []
        
        for week_idx, date in enumerate(dates):
            is_test_period = date >= test_start_date
            week_of_year = date.isocalendar()[1]
            
            for dma in dmas:
                is_treatment = dma in treatment_dmas
                
                for channel_name, channel_config in self.retail_channels.items():
                    
                    # BASE SALES
                    base_sales = 30000 * channel_config['weight']
                    
                    # Seasonality
                    seasonality = 1 + 0.15 * np.cos(2 * np.pi * (week_of_year - 1) / 52)
                    base_sales *= seasonality
                    
                    # Trend
                    trend = 1 + (week_idx * 0.001)
                    base_sales *= trend
                    
                    # Random noise
                    base_sales += np.random.normal(0, 1000)
                    
                    # ============================================================
                    # PROMO ASSIGNMENT - FIXED!
                    # ============================================================
                    
                    if channel_name == 'Store' and is_test_period and is_treatment:
                        # Store ALWAYS gets visibility in treatment (no randomness)
                        promo_type = 'Visibility'
                    
                    elif is_test_period and is_treatment:
                        # OTHER CHANNELS: ALWAYS get a promo during treatment (no "None" option!)
                        # 60% Price, 40% Visibility
                        promo_type = np.random.choice(['Price', 'Visibility'], p=[0.6, 0.4])
                    
                    else:
                        # PRE-PERIOD and CONTROL: Lower baseline promo rate (10% instead of 20%)
                        if np.random.random() < 0.10:  # REDUCED from 0.20
                            allowed_promos = [p for p in channel_config['allowed_promos'] if p != 'None']
                            if allowed_promos:
                                promo_type = np.random.choice(allowed_promos)
                            else:
                                promo_type = 'None'
                        else:
                            promo_type = 'None'
                    
                    # ============================================================
                    # APPLY TREATMENT EFFECT - FIXED!
                    # ============================================================
                    
                    sales_with_effect = base_sales
                    
                    if is_test_period and is_treatment:
                        # Apply effect based on promo type
                        if promo_type == 'Price':
                            sales_with_effect *= (1 + price_effect)  # +30%
                        elif promo_type == 'Visibility':
                            sales_with_effect *= (1 + visibility_effect)  # +18%
                        else:
                            # Should not happen in treatment, but just in case
                            sales_with_effect *= (1 + 0.05)  # +5% baseline
                    
                    final_sales = max(0, sales_with_effect + np.random.normal(0, 500))
                    
                    # ============================================================
                    # SALES RECORD
                    # ============================================================
                    
                    all_sales.append({
                        'date': date,
                        'geo_id': dma,
                        'retail_channel': channel_name,
                        'sales_revenue': final_sales,
                        'sales_units': final_sales / 15.0,
                        'promo_type': promo_type,
                        'is_treatment': is_treatment,
                        'is_test_period': is_test_period
                    })
                    
                    # ============================================================
                    # TRANSACTION RECORDS
                    # ============================================================
                    
                    if channel_config['has_transaction_data']:
                        n_transactions = int((final_sales / 15.0) * np.random.uniform(0.9, 1.1))
                        
                        for _ in range(max(1, n_transactions)):
                            age_segment = np.random.choice(self.age_segments)
                            
                            if is_test_period and is_treatment:
                                is_new = np.random.random() < 0.15
                            else:
                                is_new = np.random.random() < 0.05
                            
                            if is_new:
                                customer_id = f"NEW_{dma}_{channel_name}_{np.random.randint(10000, 99999)}"
                            else:
                                customer_id = f"EXISTING_{dma}_{channel_name}_{np.random.randint(1000, 9999)}"
                            
                            units = 1
                            price_per_unit = 15.0
                            
                            if promo_type == 'Price':
                                discount = np.random.uniform(0.15, 0.25)
                                price_per_unit *= (1 - discount)
                            
                            all_transactions.append({
                                'date': date,
                                'geo_id': dma,
                                'retail_channel': channel_name,
                                'customer_id': customer_id,
                                'age_segment': age_segment,
                                'is_new_customer': is_new,
                                'units': units,
                                'price_per_unit': price_per_unit,
                                'revenue': units * price_per_unit,
                                'promo_type': promo_type,
                                'is_treatment': is_treatment,
                                'is_test_period': is_test_period
                            })
                
                # ============================================================
                # MEDIA SPEND
                # ============================================================
                
                base_spend_per_channel = 2000
                
                if is_test_period and is_treatment:
                    spend_multiplier = 1 + spend_increase  # +20%
                else:
                    spend_multiplier = 1.0
                
                for media_channel in ['Meta', 'Google', 'Amazon', 'TikTok']:
                    spend = base_spend_per_channel * spend_multiplier * np.random.uniform(0.9, 1.1)
                    
                    all_media.append({
                        'date': date,
                        'geo_id': dma,
                        'channel': media_channel,
                        'spend_usd': spend,
                        'impressions': int(spend * 50),
                        'clicks': int(spend * 1.5)
                    })
                
                # ============================================================
                # CONTROLS (NO TEMPERATURE!)
                # ============================================================
                
                holiday = 1 if week_of_year in [1, 24, 47, 52] else 0
                
                all_controls.append({
                    'date': date,
                    'geo_id': dma,
                    'holiday_flag': holiday,
                    'promo_flag': np.random.binomial(1, 0.2),
                    'competitor_promo': np.random.binomial(1, 0.15)
                })
        
        # Create DataFrames
        sales_df = pd.DataFrame(all_sales)
        transactions_df = pd.DataFrame(all_transactions)
        media_df = pd.DataFrame(all_media)
        controls_df = pd.DataFrame(all_controls)
        
        print(f"\n✅ Data generation complete!")
        print(f"   Sales: {len(sales_df):,} records")
        print(f"   Transactions: {len(transactions_df):,} records")
        print(f"   Media: {len(media_df):,} records")
        
        # Verify promo_type is populated
        promo_dist = sales_df['promo_type'].value_counts()
        print(f"\n📊 Promo Type Distribution:")
        for promo, count in promo_dist.items():
            print(f"   {promo}: {count:,} ({count/len(sales_df)*100:.1f}%)")
        
        # Check missing
        missing_count = sales_df['promo_type'].isna().sum()
        missing_pct = (missing_count / len(sales_df)) * 100
        print(f"   Missing: {missing_count:,} ({missing_pct:.1f}%)")
        
        # Calculate expected ROI
        treatment_sales = sales_df[
            (sales_df['is_test_period']==True) & 
            (sales_df['is_treatment']==True)
        ]['sales_revenue'].sum()
        
        control_sales = sales_df[
            (sales_df['is_test_period']==True) & 
            (sales_df['is_treatment']==False)
        ]['sales_revenue'].sum()
        
        scale_factor = len(treatment_dmas) / (n_geos - len(treatment_dmas))
        control_sales_scaled = control_sales * scale_factor
        
        incremental_sales = treatment_sales - control_sales_scaled
        incremental_profit = incremental_sales * 0.40
        
        treatment_spend = media_df[
            (media_df['date'] >= test_start_date) &
            (media_df['geo_id'].isin(treatment_dmas))
        ]['spend_usd'].sum()
        
        # Calculate extra spend (vs normal)
        normal_spend = media_df[
            (media_df['date'] >= test_start_date) &
            (media_df['geo_id'].isin(treatment_dmas))
        ]['spend_usd'].sum() / (1 + spend_increase)
        
        extra_spend = treatment_spend - normal_spend
        
        expected_roi = ((incremental_profit - extra_spend) / extra_spend) * 100
        
        print(f"\n💰 Expected Results:")
        print(f"   Treatment Sales: ${treatment_sales:,.0f}")
        print(f"   Control Sales (scaled): ${control_sales_scaled:,.0f}")
        print(f"   Incremental Sales: ${incremental_sales:,.0f}")
        print(f"   Incremental Profit (40% margin): ${incremental_profit:,.0f}")
        print(f"   Extra Marketing Spend: ${extra_spend:,.0f}")
        print(f"   Expected ROI: {expected_roi:.1f}%")
        
        if expected_roi < 0:
            print(f"\n⚠️  WARNING: Negative ROI! Consider adjusting parameters:")
            print(f"   - Increase price_effect (currently {price_effect})")
            print(f"   - Increase visibility_effect (currently {visibility_effect})")
            print(f"   - Decrease spend_increase (currently {spend_increase})")
        
        return {
            'sales': sales_df,
            'transactions': transactions_df,
            'media': media_df,
            'controls': controls_df,
            'metadata': {
                'n_weeks': n_weeks,
                'n_dmas': n_geos,
                'test_start_date': str(test_start_date),
                'treatment_dmas': treatment_dmas.tolist(),
                'price_effect': price_effect,
                'visibility_effect': visibility_effect,
                'expected_roi': expected_roi,
                'retail_channels': list(self.retail_channels.keys())
            }
        }
    
    def save_datasets(self, datasets: dict, output_dir: str = 'data/demo'):
        """Save all datasets to CSV"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        datasets['sales'].to_csv(f'{output_dir}/demo_sales.csv', index=False)
        datasets['transactions'].to_csv(f'{output_dir}/demo_transactions.csv', index=False)
        datasets['media'].to_csv(f'{output_dir}/demo_media.csv', index=False)
        datasets['controls'].to_csv(f'{output_dir}/demo_controls.csv', index=False)
        
        with open(f'{output_dir}/demo_metadata.json', 'w') as f:
            json.dump(datasets['metadata'], f, indent=2, default=str)
        
        print(f"\n✅ Saved to: {output_dir}/")


# Test it
if __name__ == "__main__":
    generator = BrightlineDataGeneratorV3(seed=42)
    
    datasets = generator.generate_complete_dataset(
        n_weeks=52,
        n_geos=100,
        test_period_weeks=12,
        treatment_pct=0.7,
        price_effect=0.30,        # FIXED: 30% (was 15%)
        visibility_effect=0.18,   # FIXED: 18% (was 8%)
        spend_increase=0.20       # FIXED: 20% (was 30%)
    )
    
    generator.save_datasets(datasets)