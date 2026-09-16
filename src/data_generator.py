"""
Enhanced Synthetic Data Generator for Brightline POV Demo
Adds retail channels, age segments, transaction data, and promotion types
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class EnhancedBrightlineDataGenerator:
    """
    Generate realistic synthetic data with:
    - Multiple retail channels (Store, Omnichannel, Online)
    - Age segmentation
    - Transaction-level data for online/omnichannel
    - Different promotion types (Price vs Visibility)
    - Customer behavior (new customers, stockpiling)
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.seed = seed
        
        # Define retail channels
        self.retail_channels = {
            'Store': {
                'has_transaction_data': False,
                'has_age_data': False,
                'promo_types': ['Visibility', 'Positioning', 'Display'],
                'weight': 0.50  # 50% of business
            },
            'Omnichannel': {
                'has_transaction_data': True,
                'has_age_data': True,
                'promo_types': ['Price', 'Visibility', 'Bundle', 'Loyalty'],
                'weight': 0.30  # 30% of business
            },
            'Online_Specialty': {
                'has_transaction_data': True,
                'has_age_data': True,
                'promo_types': ['Price', 'Visibility', 'Banner'],
                'weight': 0.20  # 20% of business
            }
        }
        
        # Age segments
        self.age_segments = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        
        # Age-specific behavior
        self.age_behavior = {
            '18-24': {'price_sensitivity': 0.30, 'stockpiling_rate': 0.40, 'repeat_rate': 0.50},
            '25-34': {'price_sensitivity': 0.25, 'stockpiling_rate': 0.35, 'repeat_rate': 0.60},
            '35-44': {'price_sensitivity': 0.20, 'stockpiling_rate': 0.25, 'repeat_rate': 0.70},
            '45-54': {'price_sensitivity': 0.15, 'stockpiling_rate': 0.20, 'repeat_rate': 0.75},
            '55-64': {'price_sensitivity': 0.12, 'stockpiling_rate': 0.15, 'repeat_rate': 0.80},
            '65+':   {'price_sensitivity': 0.10, 'stockpiling_rate': 0.10, 'repeat_rate': 0.85}
        }
    
    def generate_complete_dataset(
        self,
        n_weeks: int = 104,
        n_geos: int = 150,
        start_date: str = '2023-01-01',
        test_period_weeks: int = 20,
        treatment_pct: float = 0.7,
        price_effect_size: float = 0.15,  # Price promo effect
        visibility_effect_size: float = 0.08  # Visibility promo effect
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate enhanced dataset with retail channels, age, and promotion types
        """
        print(f"🎯 Generating enhanced Brightline data...")
        print(f"   Time period: {n_weeks} weeks from {start_date}")
        print(f"   Geographic units: {n_geos} DMAs")
        print(f"   Retail channels: {list(self.retail_channels.keys())}")
        print(f"   Age segments: {self.age_segments}")
        print(f"   Test period: Last {test_period_weeks} weeks")
        
        # Generate dates
        dates = pd.date_range(start=start_date, periods=n_weeks, freq='W-SUN')
        
        # Generate DMAs
        dmas = [f"DMA_{str(i).zfill(3)}" for i in range(1, n_geos + 1)]
        
        # Determine test period
        test_start_idx = n_weeks - test_period_weeks
        test_start_date = dates[test_start_idx]
        
        # Assign treatment/control
        n_treatment = int(n_geos * treatment_pct)
        treatment_dmas = np.random.choice(dmas, size=n_treatment, replace=False)
        
        print(f"   Treatment DMAs: {len(treatment_dmas)}")
        print(f"   Control DMAs: {n_geos - len(treatment_dmas)}")
        
        # Generate data for each retail channel
        all_sales = []
        all_transactions = []
        
        for channel_name, channel_config in self.retail_channels.items():
            print(f"\n   Generating {channel_name} data...")
            
            if channel_config['has_transaction_data']:
                # Transaction-level data
                channel_sales, channel_transactions = self._generate_transaction_data(
                    dates, dmas, treatment_dmas, test_start_date,
                    channel_name, channel_config,
                    price_effect_size, visibility_effect_size
                )
                all_transactions.append(channel_transactions)
            else:
                # Aggregate data only
                channel_sales = self._generate_aggregate_data(
                    dates, dmas, treatment_dmas, test_start_date,
                    channel_name, channel_config,
                    visibility_effect_size
                )
            
            all_sales.append(channel_sales)
        
        # Combine all channels
        sales_df = pd.concat(all_sales, ignore_index=True)
        
        # Combine transactions (if any)
        if all_transactions:
            transactions_df = pd.concat(all_transactions, ignore_index=True)
        else:
            transactions_df = pd.DataFrame()
        
        # Generate media spend
        media_df = self._generate_media_spend(dates, dmas, treatment_dmas, test_start_date)
        
        # Generate controls
        controls_df = self._generate_controls(dates, dmas)
        
        print(f"\n✅ Enhanced data generation complete!")
        print(f"   Sales records: {len(sales_df):,}")
        if len(transactions_df) > 0:
            print(f"   Transaction records: {len(transactions_df):,}")
        print(f"   Media records: {len(media_df):,}")
        
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
                'price_effect_size': price_effect_size,
                'visibility_effect_size': visibility_effect_size,
                'retail_channels': list(self.retail_channels.keys())
            }
        }
    
    def _generate_transaction_data(
        self, dates, dmas, treatment_dmas, test_start_date,
        channel_name, channel_config, price_effect, visibility_effect
    ):
        """
        Generate transaction-level data for online/omnichannel channels
        """
        transactions = []
        sales_summary = []
        
        # Number of customers per DMA
        customers_per_dma = 100  # Average (kept small for a lightweight public demo dataset)
        
        for date in dates:
            is_test_period = date >= test_start_date
            
            for dma in dmas:
                is_treatment = dma in treatment_dmas
                
                # Randomly select promotion type for this week
                promo_type = np.random.choice(channel_config['promo_types'])
                has_promo = np.random.random() < 0.3  # 30% of weeks have promos
                
                # Base number of transactions
                base_transactions = int(np.random.normal(customers_per_dma * 0.15, 30))
                
                # Apply treatment effect during test period
                if is_test_period and is_treatment and has_promo:
                    if promo_type == 'Price':
                        lift_factor = 1 + price_effect
                    else:
                        lift_factor = 1 + visibility_effect
                else:
                    lift_factor = 1.0
                
                n_transactions = int(base_transactions * lift_factor * channel_config['weight'])
                
                # Generate individual transactions
                for _ in range(n_transactions):
                    # Generate customer
                    customer_id = f"{dma}_{channel_name}_{np.random.randint(1, customers_per_dma)}"
                    
                    # Assign age segment
                    age_segment = np.random.choice(self.age_segments)
                    age_behavior = self.age_behavior[age_segment]
                    
                    # Is this a new customer?
                    is_new = np.random.random() < 0.15  # 15% are new
                    
                    # Units purchased
                    base_units = 1
                    
                    # Stockpiling behavior (buy extra during price promos)
                    if promo_type == 'Price' and has_promo:
                        if np.random.random() < age_behavior['stockpiling_rate']:
                            base_units = np.random.choice([2, 3, 4], p=[0.6, 0.3, 0.1])
                    
                    # Price per unit
                    base_price = 15.0
                    if promo_type == 'Price' and has_promo:
                        discount = np.random.uniform(0.15, 0.30)
                        price = base_price * (1 - discount)
                    else:
                        price = base_price * np.random.uniform(0.95, 1.05)
                    
                    # Revenue
                    revenue = base_units * price
                    
                    transactions.append({
                        'date': date,
                        'geo_id': dma,
                        'retail_channel': channel_name,
                        'customer_id': customer_id,
                        'age_segment': age_segment,
                        'is_new_customer': is_new,
                        'units': base_units,
                        'price_per_unit': price,
                        'revenue': revenue,
                        'promo_type': promo_type if has_promo else 'None',
                        'is_treatment': is_treatment,
                        'is_test_period': is_test_period
                    })
                
                # Aggregate for sales summary
                day_transactions = [t for t in transactions if t['date'] == date and t['geo_id'] == dma]
                if day_transactions:
                    total_units = sum(t['units'] for t in day_transactions)
                    total_revenue = sum(t['revenue'] for t in day_transactions)
                    n_new_customers = sum(t['is_new_customer'] for t in day_transactions)
                    
                    sales_summary.append({
                        'date': date,
                        'geo_id': dma,
                        'retail_channel': channel_name,
                        'sales_units': total_units,
                        'sales_revenue': total_revenue,
                        'n_transactions': len(day_transactions),
                        'n_new_customers': n_new_customers,
                        'promo_type': promo_type if has_promo else 'None'
                    })
        
        return pd.DataFrame(sales_summary), pd.DataFrame(transactions)
    
    def _generate_aggregate_data(
        self, dates, dmas, treatment_dmas, test_start_date,
        channel_name, channel_config, visibility_effect
    ):
        """
        Generate aggregate sales data for store channel (no transaction-level data)
        """
        sales = []
        
        for date in dates:
            is_test_period = date >= test_start_date
            
            for dma in dmas:
                is_treatment = dma in treatment_dmas
                
                # Randomly select promotion type
                promo_type = np.random.choice(channel_config['promo_types'])
                has_promo = np.random.random() < 0.25  # 25% of weeks
                
                # Base sales
                base_sales = np.random.gamma(shape=2.0, scale=1500) * channel_config['weight']
                
                # Apply treatment effect
                if is_test_period and is_treatment and has_promo:
                    lift_factor = 1 + visibility_effect
                else:
                    lift_factor = 1.0
                
                sales_units = base_sales * lift_factor
                sales_revenue = sales_units * 15.0  # Fixed price
                
                sales.append({
                    'date': date,
                    'geo_id': dma,
                    'retail_channel': channel_name,
                    'sales_units': sales_units,
                    'sales_revenue': sales_revenue,
                    'n_transactions': np.nan,  # Not available
                    'n_new_customers': np.nan,  # Not available
                    'promo_type': promo_type if has_promo else 'None'
                })
        
        return pd.DataFrame(sales)
    
    def _generate_media_spend(self, dates, dmas, treatment_dmas, test_start_date):
        """
        Generate media spend data
        """
        channels = ['Meta', 'Google', 'Amazon', 'TikTok']
        channel_base_spend = {
            'Meta': 3500,
            'Google': 2800,
            'Amazon': 2200,
            'TikTok': 1500
        }
        
        media_rows = []
        
        for date in dates:
            is_test_period = date >= test_start_date
            
            for dma in dmas:
                is_treatment = dma in treatment_dmas
                
                for channel in channels:
                    base_spend = channel_base_spend[channel]
                    spend = base_spend * np.random.uniform(0.85, 1.15)
                    
                    # Treatment boost during test
                    if is_test_period and is_treatment:
                        spend *= 1.30
                    
                    media_rows.append({
                        'date': date,
                        'geo_id': dma,
                        'channel': channel,
                        'spend_usd': round(spend, 2),
                        'impressions': int(spend * np.random.uniform(48, 62)),
                        'clicks': int(spend * np.random.uniform(1.2, 1.8))
                    })
        
        return pd.DataFrame(media_rows)
    
    def _generate_controls(self, dates, dmas):
        """
        Generate control variables
        """
        controls = []
        
        for date in dates:
            week_of_year = date.isocalendar()[1]
            
            for dma in dmas:
                # Temperature
                temp = 55 + 25 * np.cos(2 * np.pi * (week_of_year - 1) / 52) + np.random.normal(0, 6)
                
                # Holidays
                holiday_weeks = [1, 24, 47, 52]
                holiday_flag = 1 if week_of_year in holiday_weeks else 0
                
                # Competitor promo
                competitor_promo = np.random.binomial(1, 0.15)
                
                controls.append({
                    'date': date,
                    'geo_id': dma,
                    'temperature': temp,
                    'holiday_flag': holiday_flag,
                    'competitor_promo': competitor_promo
                })
        
        return pd.DataFrame(controls)
    
    def save_datasets(self, datasets: Dict, output_dir: str = 'data/synthetic_v2'):
        """
        Save generated datasets
        """
        import os
        import json
        
        os.makedirs(output_dir, exist_ok=True)
        
        for name, df in datasets.items():
            if name == 'metadata':
                continue
            if not df.empty:
                filepath = os.path.join(output_dir, f'brightline_{name}_v2.csv')
                df.to_csv(filepath, index=False)
                print(f"✅ Saved: {filepath}")
        
        if 'metadata' in datasets:
            metadata_path = os.path.join(output_dir, 'metadata_v2.json')
            with open(metadata_path, 'w') as f:
                json.dump(datasets['metadata'], f, indent=2)
            print(f"✅ Saved: {metadata_path}")


# Test
if __name__ == "__main__":
    generator = EnhancedBrightlineDataGenerator(seed=42)
    
    datasets = generator.generate_complete_dataset(
        n_weeks=52,
        n_geos=50,
        test_period_weeks=12,
        treatment_pct=0.7,
        price_effect_size=0.15,
        visibility_effect_size=0.08
    )
    
    generator.save_datasets(datasets)
    
    print("\n📊 Dataset Summary:")
    print(f"Sales: {len(datasets['sales']):,} rows")
    print(f"Transactions: {len(datasets['transactions']):,} rows")
    print(f"Channels: {datasets['sales']['retail_channel'].unique()}")
    if not datasets['transactions'].empty:
        print(f"Age segments: {datasets['transactions']['age_segment'].unique()}")