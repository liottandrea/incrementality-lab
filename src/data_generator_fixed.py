"""
Fixed Data Generator - Ensures Positive Treatment Effects and ROI
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict
import warnings
warnings.filterwarnings('ignore')


class FixedBrightlineDataGenerator:
    """
    Enhanced data generator with guaranteed positive treatment effects
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.seed = seed
        
        # Retail channels
        self.retail_channels = {
            'Store': {'weight': 0.50, 'has_transaction_data': False},
            'Omnichannel': {'weight': 0.30, 'has_transaction_data': True},
            'Online_Specialty': {'weight': 0.20, 'has_transaction_data': True}
        }
        
        # Age segments
        self.age_segments = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        
        # Age-specific responses
        self.age_responses = {
            '18-24': 0.15,  # 15% response to marketing
            '25-34': 0.18,  # 18% response (best)
            '35-44': 0.16,
            '45-54': 0.14,
            '55-64': 0.12,
            '65+': 0.10
        }
    
    def generate_complete_dataset(
        self,
        n_weeks: int = 104,
        n_geos: int = 150,
        start_date: str = '2023-01-01',
        test_period_weeks: int = 20,
        treatment_pct: float = 0.7,
        treatment_effect: float = 0.12,  # 12% lift
        spend_increase: float = 0.30     # 30% more spend in treatment
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate dataset with guaranteed positive treatment effect
        
        Args:
            n_weeks: Number of weeks
            n_geos: Number of DMAs
            test_period_weeks: Test duration
            treatment_pct: % in treatment group
            treatment_effect: Expected lift (e.g., 0.12 = 12%)
            spend_increase: Marketing spend increase for treatment
        """
        print(f"🎯 Generating Brightline data with positive ROI...")
        print(f"   Weeks: {n_weeks} | DMAs: {n_geos}")
        print(f"   Treatment effect: {treatment_effect*100:.1f}%")
        print(f"   Spend increase: {spend_increase*100:.1f}%")
        
        # Generate dates
        dates = pd.date_range(start=start_date, periods=n_weeks, freq='W-SUN')
        
        # Generate DMAs
        dmas = [f"DMA_{str(i).zfill(3)}" for i in range(1, n_geos + 1)]
        
        # Test period
        test_start_idx = n_weeks - test_period_weeks
        test_start_date = dates[test_start_idx]
        
        # Random treatment assignment
        n_treatment = int(n_geos * treatment_pct)
        treatment_dmas = np.random.choice(dmas, size=n_treatment, replace=False)
        
        print(f"   Test start: {test_start_date.strftime('%Y-%m-%d')}")
        print(f"   Treatment DMAs: {len(treatment_dmas)}")
        print(f"   Control DMAs: {n_geos - len(treatment_dmas)}")
        
        # Generate data
        all_sales = []
        all_transactions = []
        all_media = []
        all_controls = []
        
        for date in dates:
            week_num = dates.get_loc(date)
            is_test_period = date >= test_start_date
            
            for dma in dmas:
                is_treatment = dma in treatment_dmas
                
                # BASE SALES (same for everyone in pre-period)
                base_sales = 45000 + np.random.normal(0, 3000)
                
                # Add seasonality (winter peak for skincare)
                week_of_year = date.isocalendar()[1]
                seasonality = 1 + 0.15 * np.cos(2 * np.pi * (week_of_year - 1) / 52)
                base_sales *= seasonality
                
                # Add trend (slow growth)
                trend = 1 + (week_num * 0.0015)
                base_sales *= trend
                
                # TREATMENT EFFECT (only during test period for treatment group)
                if is_test_period and is_treatment:
                    # Apply the treatment lift
                    sales_with_treatment = base_sales * (1 + treatment_effect)
                else:
                    sales_with_treatment = base_sales
                
                # Add noise
                final_sales = sales_with_treatment + np.random.normal(0, 1000)
                
                # Generate by channel
                for channel, config in self.retail_channels.items():
                    channel_sales = final_sales * config['weight']
                    
                    # Sales record
                    all_sales.append({
                        'date': date,
                        'geo_id': dma,
                        'retail_channel': channel,
                        'sales_revenue': channel_sales,
                        'sales_units': channel_sales / 15.0,  # $15 per unit
                        'promo_type': 'None',
                        'is_treatment': is_treatment,
                        'is_test_period': is_test_period
                    })
                    
                    # Transaction-level data (for online channels)
                    if config['has_transaction_data']:
                        n_transactions = int(channel_sales / 15 * np.random.uniform(0.8, 1.2))
                        
                        for _ in range(n_transactions):
                            age_segment = np.random.choice(self.age_segments)
                            is_new = np.random.random() < 0.15 if is_test_period else 0.05
                            
                            all_transactions.append({
                                'date': date,
                                'geo_id': dma,
                                'retail_channel': channel,
                                'customer_id': f"{dma}_{channel}_{np.random.randint(1, 1000)}",
                                'age_segment': age_segment,
                                'is_new_customer': is_new,
                                'units': 1,
                                'price_per_unit': 15.0,
                                'revenue': 15.0,
                                'promo_type': 'None',
                                'is_treatment': is_treatment,
                                'is_test_period': is_test_period
                            })
                
                # MEDIA SPEND
                base_spend_per_channel = 2500
                
                # Treatment gets MORE spend during test
                if is_test_period and is_treatment:
                    spend_multiplier = 1 + spend_increase
                else:
                    spend_multiplier = 1.0
                
                for channel in ['Meta', 'Google', 'Amazon', 'TikTok']:
                    spend = base_spend_per_channel * spend_multiplier * np.random.uniform(0.9, 1.1)
                    
                    all_media.append({
                        'date': date,
                        'geo_id': dma,
                        'channel': channel,
                        'spend_usd': spend,
                        'impressions': int(spend * 50),
                        'clicks': int(spend * 1.5)
                    })
                
                # CONTROLS
                temp = 55 + 25 * np.cos(2 * np.pi * (week_of_year - 1) / 52) + np.random.normal(0, 5)
                holiday = 1 if week_of_year in [1, 24, 47, 52] else 0
                
                all_controls.append({
                    'date': date,
                    'geo_id': dma,
                    'temperature': temp,
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
        
        # Calculate expected ROI
        treatment_sales = sales_df[
            (sales_df['is_test_period']==True) & 
            (sales_df['is_treatment']==True)
        ]['sales_revenue'].sum()
        
        control_sales = sales_df[
            (sales_df['is_test_period']==True) & 
            (sales_df['is_treatment']==False)
        ]['sales_revenue'].sum()
        
        # Scale control to treatment size
        scale_factor = len(treatment_dmas) / (n_geos - len(treatment_dmas))
        control_sales_scaled = control_sales * scale_factor
        
        incremental_sales = treatment_sales - control_sales_scaled
        incremental_profit = incremental_sales * 0.40  # 40% margin
        
        treatment_spend = media_df[
            (media_df['date'] >= test_start_date) &
            (media_df['geo_id'].isin(treatment_dmas))
        ]['spend_usd'].sum()
        
        expected_roi = (incremental_profit - treatment_spend) / treatment_spend * 100
        
        print(f"\n💰 Expected Results:")
        print(f"   Incremental Sales: ${incremental_sales:,.0f}")
        print(f"   Incremental Profit (40% margin): ${incremental_profit:,.0f}")
        print(f"   Treatment Spend: ${treatment_spend:,.0f}")
        print(f"   Expected ROI: {expected_roi:.1f}%")
        
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
                'treatment_effect': treatment_effect,
                'spend_increase': spend_increase,
                'expected_roi': expected_roi
            }
        }