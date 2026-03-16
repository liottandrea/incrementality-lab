"""
Brightline Data Generator v4 - With Post-Test Period

Timeline:
- Pre-period: 28 weeks (baseline)
- Test period: 12 weeks (intervention)
- Post-period: 12 weeks (sustained effect check)

Scale: ~100 unique customers, realistic small-scale test
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict
import json


class BrightlineDataGeneratorV4:
    """
    Realistic small-scale data generator with post-test period
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.seed = seed
        
        self.retail_channels = {
            'Store': {
                'weight': 0.50,
                'has_transaction_data': False,
                'allowed_promos': ['Visibility', 'No_Promo'],
                'description': 'Physical stores - aggregate data only'
            },
            'Omnichannel': {
                'weight': 0.30,
                'has_transaction_data': True,
                'allowed_promos': ['Price', 'Visibility', 'No_Promo'],
                'description': 'Online + Physical - transaction-level with age data'
            },
            'Online_Specialty': {
                'weight': 0.20,
                'has_transaction_data': True,
                'allowed_promos': ['Price', 'Visibility', 'No_Promo'],
                'description': 'Specialized online retailers - transaction-level with age data'
            }
        }
        
        self.age_segments = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        
        # More varied age responses with higher purchase rates for better distribution
        self.age_responses = {
            '18-24': {'price_sensitivity': 0.25, 'visibility_response': 0.08, 'base_purchase_rate': 0.08},
            '25-34': {'price_sensitivity': 0.22, 'visibility_response': 0.15, 'base_purchase_rate': 0.15},
            '35-44': {'price_sensitivity': 0.18, 'visibility_response': 0.18, 'base_purchase_rate': 0.18},
            '45-54': {'price_sensitivity': 0.14, 'visibility_response': 0.20, 'base_purchase_rate': 0.22},
            '55-64': {'price_sensitivity': 0.12, 'visibility_response': 0.22, 'base_purchase_rate': 0.20},
            '65+':   {'price_sensitivity': 0.10, 'visibility_response': 0.25, 'base_purchase_rate': 0.16}
        }
    
    def generate_complete_dataset(
        self,
        n_weeks: int = 52,
        n_geos: int = 50,
        n_customers_per_geo: int = 5,  # ~250 total customers
        pre_period_weeks: int = 28,
        test_period_weeks: int = 12,
        post_period_weeks: int = 12,
        start_date: str = '2024-01-01',
        treatment_pct: float = 0.7,
        price_effect: float = 0.30,
        visibility_effect: float = 0.20,
        sustained_effect: float = 0.12,  # Lift remains after test ends!
        spend_increase: float = 0.10
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate complete dataset with pre/test/post periods
        """
        print(f"🎯 Generating Brightline data v4...")
        print(f"   Timeline: {n_weeks} weeks")
        print(f"   - Pre-period: Weeks 1-{pre_period_weeks} ({pre_period_weeks} weeks)")
        print(f"   - Test period: Weeks {pre_period_weeks+1}-{pre_period_weeks+test_period_weeks} ({test_period_weeks} weeks)")
        print(f"   - Post-period: Weeks {pre_period_weeks+test_period_weeks+1}-{n_weeks} ({post_period_weeks} weeks)")
        print(f"   Markets: {n_geos} DMAs")
        print(f"   Customers: ~{n_geos * n_customers_per_geo * 3} unique customers")
        
        dates = pd.date_range(start=start_date, periods=n_weeks, freq='W-SUN')
        dmas = [f"DMA_{str(i).zfill(3)}" for i in range(1, n_geos + 1)]
        
        # Define periods
        test_start_idx = pre_period_weeks
        test_end_idx = pre_period_weeks + test_period_weeks
        test_start_date = dates[test_start_idx]
        test_end_date = dates[test_end_idx - 1]
        post_start_date = dates[test_end_idx]
        
        # Treatment assignment
        n_treatment = int(n_geos * treatment_pct)
        treatment_dmas = np.random.choice(dmas, size=n_treatment, replace=False)
        
        print(f"   Treatment: {len(treatment_dmas)} DMAs | Control: {n_geos - len(treatment_dmas)} DMAs")
        print(f"   Effects: Price={price_effect*100:.0f}%, Visibility={visibility_effect*100:.0f}%, Sustained={sustained_effect*100:.0f}%")
        
        all_sales = []
        all_transactions = []
        all_media = []
        all_controls = []
        
        # Generate stable customer base per DMA with varied loyalty levels
        customer_base = {}
        for dma in dmas:
            for channel in ['Omnichannel', 'Online_Specialty']:
                base_size = n_customers_per_geo
                customers = [
                    f"CUST_{dma}_{channel}_{str(i).zfill(4)}"
                    for i in range(1, base_size + 1)
                ]
                customer_base[f"{dma}_{channel}"] = {
                    'existing': customers,
                    'age_map': {
                        cust: np.random.choice(self.age_segments)
                        for cust in customers
                    },
                    # Add customer loyalty factor for more varied purchase frequency
                    # Using gamma distribution for realistic variation (some very loyal, most moderate)
                    'loyalty_factor': {
                        cust: np.random.gamma(2, 0.5)
                        for cust in customers
                    }
                }
        
        for week_idx, date in enumerate(dates):
            # Determine period
            is_pre_period = week_idx < test_start_idx
            is_test_period = test_start_idx <= week_idx < test_end_idx
            is_post_period = week_idx >= test_end_idx
            
            week_of_year = date.isocalendar()[1]
            
            for dma in dmas:
                is_treatment = dma in treatment_dmas
                
                for channel_name, channel_config in self.retail_channels.items():
                    
                    # BASE SALES with more variation
                    base_sales = 30000 * channel_config['weight']

                    # Moderate seasonality (±10% instead of ±25% for more realistic pattern)
                    seasonality = 1 + 0.10 * np.cos(2 * np.pi * (week_of_year - 1) / 52)
                    base_sales *= seasonality

                    # Growth trend
                    trend = 1 + (week_idx * 0.003)  # 0.3% per week (slightly higher for visibility)
                    base_sales *= trend
                    
                    # Day-of-week effects (some DMAs have different shopping patterns)
                    dma_idx = int(dma.split('_')[1])
                    dow_effect = 1 + 0.05 * np.sin(dma_idx)  # Varies by DMA
                    base_sales *= dow_effect
                    
                    # More noise for realism
                    base_sales += np.random.normal(0, 1500)
                    
                    # ============================================================
                    # PROMO ASSIGNMENT - Varied by period
                    # ============================================================
                    
                    if is_test_period and is_treatment:
                        # TEST PERIOD: High promo rate
                        if channel_name == 'Store':
                            promo_type = 'Visibility'
                        else:
                            promo_type = np.random.choice(['Price', 'Visibility', 'No_Promo'],
                                                         p=[0.50, 0.40, 0.10])
                    
                    elif is_post_period and is_treatment:
                        # POST PERIOD: Lower promo rate, but some sustained activity
                        if np.random.random() < 0.25:  # 25% promo rate
                            if channel_name == 'Store':
                                promo_type = 'Visibility'
                            else:
                                promo_type = np.random.choice(['Price', 'Visibility'], p=[0.4, 0.6])
                        else:
                            promo_type = 'No_Promo'

                    else:
                        # PRE-PERIOD and CONTROL: Low baseline promo rate
                        if np.random.random() < 0.12:  # 12% baseline
                            allowed = [p for p in channel_config['allowed_promos'] if p != 'No_Promo']
                            if allowed:
                                promo_type = np.random.choice(allowed)
                            else:
                                promo_type = 'No_Promo'
                        else:
                            promo_type = 'No_Promo'
                    
                    # ============================================================
                    # APPLY TREATMENT EFFECT (with gradual ramp-up)
                    # ============================================================

                    sales_with_effect = base_sales

                    if is_test_period and is_treatment:
                        # Calculate ramp-up factor (gradual increase over first 4 weeks)
                        weeks_into_test = week_idx - test_start_idx + 1
                        if weeks_into_test <= 4:
                            # Smoother ramp-up: 15% → 40% → 65% → 90% → 100%
                            ramp_up_factor = min(1.0, 0.15 + (weeks_into_test * 0.23))
                        else:
                            ramp_up_factor = 1.0

                        # Apply ramped-up effect
                        if promo_type == 'Price':
                            sales_with_effect *= (1 + price_effect * ramp_up_factor)
                        elif promo_type == 'Visibility':
                            sales_with_effect *= (1 + visibility_effect * ramp_up_factor)
                        else:
                            sales_with_effect *= (1 + 0.05 * ramp_up_factor)

                    elif is_post_period and is_treatment:
                        # AFTER TEST: Sustained lift (habit formation, brand awareness)
                        if promo_type == 'Price':
                            sales_with_effect *= (1 + price_effect * 0.6)  # 60% of original
                        elif promo_type == 'Visibility':
                            sales_with_effect *= (1 + visibility_effect * 0.7)  # 70% of original
                        else:
                            sales_with_effect *= (1 + sustained_effect)  # Baseline sustained lift
                    
                    final_sales = max(0, sales_with_effect + np.random.normal(0, 800))
                    
                    # ============================================================
                    # SALES RECORD
                    # ============================================================
                    
                    all_sales.append({
                        'date': date,
                        'week': week_idx + 1,
                        'geo_id': dma,
                        'retail_channel': channel_name,
                        'sales_revenue': final_sales,
                        'sales_units': final_sales / 15.0,
                        'promo_type': promo_type,
                        'is_treatment': is_treatment,
                        'is_pre_period': is_pre_period,
                        'is_test_period': is_test_period,
                        'is_post_period': is_post_period
                    })
                    
                    # ============================================================
                    # TRANSACTION RECORDS - Realistic customer behavior
                    # ============================================================
                    
                    if channel_config['has_transaction_data']:
                        key = f"{dma}_{channel_name}"
                        existing_custs = customer_base[key]['existing']
                        age_map = customer_base[key]['age_map']
                        loyalty_map = customer_base[key]['loyalty_factor']

                        # Existing customers: purchase probability
                        for customer_id in existing_custs:
                            age = age_map[customer_id]
                            loyalty = loyalty_map[customer_id]

                            # Base purchase probability adjusted by customer loyalty
                            base_prob = self.age_responses[age]['base_purchase_rate'] * loyalty

                            # Adjust for promo
                            if promo_type == 'Price':
                                purchase_prob = base_prob * (1 + self.age_responses[age]['price_sensitivity'])
                            elif promo_type == 'Visibility':
                                purchase_prob = base_prob * (1 + self.age_responses[age]['visibility_response'])
                            else:
                                purchase_prob = base_prob

                            # Higher in test/post for treatment
                            if (is_test_period or is_post_period) and is_treatment:
                                purchase_prob *= 1.3
                            
                            # Did they purchase this week?
                            if np.random.random() < purchase_prob:
                                # More varied units per purchase (1-5 units possible)
                                units = np.random.choice([1, 2, 3, 4, 5], p=[0.50, 0.25, 0.15, 0.07, 0.03])
                                price_per_unit = 15.0
                                
                                if promo_type == 'Price':
                                    discount = np.random.uniform(0.15, 0.30)
                                    price_per_unit *= (1 - discount)
                                
                                all_transactions.append({
                                    'date': date,
                                    'week': week_idx + 1,
                                    'geo_id': dma,
                                    'retail_channel': channel_name,
                                    'customer_id': customer_id,
                                    'age_segment': age,
                                    'is_new_customer': False,
                                    'units': units,
                                    'price_per_unit': price_per_unit,
                                    'revenue': units * price_per_unit,
                                    'promo_type': promo_type,
                                    'is_treatment': is_treatment,
                                    'is_pre_period': is_pre_period,
                                    'is_test_period': is_test_period,
                                    'is_post_period': is_post_period
                                })
                        
                        # New customers (only in test/post for treatment)
                        if (is_test_period or is_post_period) and is_treatment:
                            n_new = np.random.poisson(0.5)  # Average 0.5 new customers per week
                            
                            for _ in range(n_new):
                                new_cust_id = f"NEW_{dma}_{channel_name}_{week_idx}_{np.random.randint(1000, 9999)}"
                                age = np.random.choice(self.age_segments)
                                units = 1
                                price_per_unit = 15.0
                                
                                if promo_type == 'Price':
                                    discount = np.random.uniform(0.15, 0.30)
                                    price_per_unit *= (1 - discount)
                                
                                all_transactions.append({
                                    'date': date,
                                    'week': week_idx + 1,
                                    'geo_id': dma,
                                    'retail_channel': channel_name,
                                    'customer_id': new_cust_id,
                                    'age_segment': age,
                                    'is_new_customer': True,
                                    'units': units,
                                    'price_per_unit': price_per_unit,
                                    'revenue': units * price_per_unit,
                                    'promo_type': promo_type,
                                    'is_treatment': is_treatment,
                                    'is_pre_period': is_pre_period,
                                    'is_test_period': is_test_period,
                                    'is_post_period': is_post_period
                                })
                
                # ============================================================
                # MEDIA SPEND - Varies by period
                # ============================================================
                
                base_spend = 2000
                
                if is_test_period and is_treatment:
                    spend_mult = 1 + spend_increase  # +20% during test
                else:
                    spend_mult = 1.0
                
                # More varied media mix with channel-specific variation
                media_channels = {
                    'Meta': {'weight': 0.35, 'variation': (0.75, 1.25)},      # ±25%
                    'Google': {'weight': 0.30, 'variation': (0.80, 1.30)},    # ±30%
                    'Amazon': {'weight': 0.20, 'variation': (0.70, 1.40)},    # ±40%
                    'TikTok': {'weight': 0.15, 'variation': (0.65, 1.45)}     # ±45%
                }

                for media_channel, config in media_channels.items():
                    # Base spend with channel weight and treatment multiplier
                    channel_spend = base_spend * config['weight'] * spend_mult
                    # Add weekly variation specific to each channel
                    variation = np.random.uniform(config['variation'][0], config['variation'][1])
                    spend = channel_spend * variation
                    
                    all_media.append({
                        'date': date,
                        'week': week_idx + 1,
                        'geo_id': dma,
                        'channel': media_channel,
                        'spend_usd': spend * 0.70,
                        'impressions': int(spend * np.random.uniform(45, 55)),
                        'clicks': int(spend * np.random.uniform(1.3, 1.7))
                    })
                
                # ============================================================
                # CONTROLS
                # ============================================================
                
                # Holiday detection
                is_holiday = week_of_year in [1, 2, 24, 47, 51, 52]

                all_controls.append({
                    'date': date,
                    'week': week_idx + 1,
                    'geo_id': dma,
                    'holiday_flag': 1 if is_holiday else 0,
                    'promo_flag': np.random.binomial(1, 0.15),
                    'competitor_promo': np.random.binomial(1, 0.18),  # Slightly higher
                    'is_pre_period': is_pre_period,
                    'is_test_period': is_test_period,
                    'is_post_period': is_post_period
                })
        
        # Create DataFrames
        sales_df = pd.DataFrame(all_sales)
        transactions_df = pd.DataFrame(all_transactions)
        media_df = pd.DataFrame(all_media)
        controls_df = pd.DataFrame(all_controls)
        
        print(f"\n✅ Data generation complete!")
        print(f"   Sales: {len(sales_df):,} records")
        print(f"   Transactions: {len(transactions_df):,} records")
        print(f"   Unique customers: {transactions_df['customer_id'].nunique():,}")
        print(f"   Media: {len(media_df):,} records")
        
        # Promo distribution
        print(f"\n📊 Promo Distribution:")
        for period, period_name in [('is_pre_period', 'Pre'), 
                                    ('is_test_period', 'Test'), 
                                    ('is_post_period', 'Post')]:
            period_sales = sales_df[sales_df[period] == True]
            promo_dist = period_sales['promo_type'].value_counts()
            print(f"\n   {period_name} Period:")
            for promo, count in promo_dist.items():
                pct = count / len(period_sales) * 100
                print(f"     {promo}: {count} ({pct:.1f}%)")
        
        # Calculate ROI for each period
    
        print(f"\n💰 Expected Results by Period:")
        
        # Test Period
        t_sales_test = sales_df[(sales_df['is_test_period']) & (sales_df['is_treatment'])]['sales_revenue'].sum()
        c_sales_test = sales_df[(sales_df['is_test_period']) & (~sales_df['is_treatment'])]['sales_revenue'].sum()
        
        scale = len(treatment_dmas) / (n_geos - len(treatment_dmas))
        c_scaled_test = c_sales_test * scale
        
        incr_sales_test = t_sales_test - c_scaled_test
        incr_profit_test = incr_sales_test * 0.50
        
        # Media spend during test (using DATE filtering, not period flag)
        test_spend = media_df[
            (media_df['date'] >= test_start_date) & 
            (media_df['date'] <= test_end_date) &
            (media_df['geo_id'].isin(treatment_dmas))
        ]['spend_usd'].sum()
        
        normal_spend_test = test_spend / (1 + spend_increase)
        extra_spend_test = test_spend - normal_spend_test
        
        roi_test = ((incr_profit_test - extra_spend_test) / extra_spend_test) * 100 if extra_spend_test > 0 else 0
        roas_test = incr_profit_test / extra_spend_test if extra_spend_test > 0 else 0
        
        print(f"\n   Test Period:")
        print(f"     Incremental Sales: ${incr_sales_test:,.0f}")
        print(f"     Incremental Profit: ${incr_profit_test:,.0f}")
        print(f"     Extra Spend: ${extra_spend_test:,.0f}")
        print(f"     ROI: {roi_test:.1f}%")
        print(f"     ROAS: {roas_test:.2f}x")
        
        # Post Period
        t_sales_post = sales_df[(sales_df['is_post_period']) & (sales_df['is_treatment'])]['sales_revenue'].sum()
        c_sales_post = sales_df[(sales_df['is_post_period']) & (~sales_df['is_treatment'])]['sales_revenue'].sum()
        
        c_scaled_post = c_sales_post * scale
        incr_sales_post = t_sales_post - c_scaled_post
        incr_profit_post = incr_sales_post * 0.50
        
        sustained_lift_pct = (incr_sales_post / c_scaled_post) * 100 if c_scaled_post > 0 else 0
        
        print(f"\n   Post Period:")
        print(f"     Incremental Sales: ${incr_sales_post:,.0f}")
        print(f"     Incremental Profit: ${incr_profit_post:,.0f}")
        print(f"     Extra Spend: $0 (marketing back to normal)")
        print(f"     Sustained Lift: {sustained_lift_pct:.1f}%")
        
        return {
            'sales': sales_df,
            'transactions': transactions_df,
            'media': media_df,
            'controls': controls_df,
            'metadata': {
                'n_weeks': n_weeks,
                'n_dmas': n_geos,
                'pre_period_weeks': pre_period_weeks,
                'test_period_weeks': test_period_weeks,
                'post_period_weeks': post_period_weeks,
                'test_start_date': str(test_start_date),
                'test_end_date': str(test_end_date),
                'post_start_date': str(post_start_date),
                'treatment_dmas': treatment_dmas.tolist(),
                'price_effect': price_effect,
                'visibility_effect': visibility_effect,
                'sustained_effect': sustained_effect,
                'n_unique_customers': transactions_df['customer_id'].nunique(),
                'retail_channels': list(self.retail_channels.keys()),
                'test_period_roi': roi_test,
                'test_period_roas': roas_test,
                'sustained_lift_pct': sustained_lift_pct
            }
        }
    
    def save_datasets(self, datasets: dict, output_dir: str = 'data/demo'):
        """Save all datasets"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        datasets['sales'].to_csv(f'{output_dir}/demo_sales.csv', index=False)
        datasets['transactions'].to_csv(f'{output_dir}/demo_transactions.csv', index=False)
        datasets['media'].to_csv(f'{output_dir}/demo_media.csv', index=False)
        datasets['controls'].to_csv(f'{output_dir}/demo_controls.csv', index=False)
        
        with open(f'{output_dir}/demo_metadata.json', 'w') as f:
            json.dump(datasets['metadata'], f, indent=2, default=str)
        
        print(f"\n✅ Saved to: {output_dir}/")


if __name__ == "__main__":
    generator = BrightlineDataGeneratorV4(seed=42)

    datasets = generator.generate_complete_dataset(
        n_weeks=52,
        n_geos=50,
        n_customers_per_geo=5,
        pre_period_weeks=28,
        test_period_weeks=12,
        post_period_weeks=12,
        treatment_pct=0.7,
        price_effect=0.30,
        visibility_effect=0.20,
        sustained_effect=0.12,
        spend_increase=0.10
    )
    
    generator.save_datasets(datasets)