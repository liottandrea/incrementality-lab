"""
Synthetic Data Generator for Brightline POV Demo
Generates realistic sales and marketing data
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class BrightlineSyntheticDataGenerator:
    """
    Generate realistic synthetic data mimicking Brightline's business
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize generator
        
        Args:
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        self.seed = seed
        
    def generate_complete_dataset(
        self,
        n_weeks: int = 104,  # 2 years
        n_dmas: int = 150,
        start_date: str = '2023-01-01',
        product_name: str = 'Brightline_HydraCare',
        test_period_weeks: int = 20,
        treatment_pct: float = 0.7,
        true_effect_size: float = 0.12  # 12% lift
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate complete synthetic dataset
        
        Args:
            n_weeks: Number of weeks of data
            n_dmas: Number of DMAs/geographic units
            start_date: Start date for data
            product_name: Product SKU name
            test_period_weeks: Length of test period in weeks
            treatment_pct: % of DMAs in treatment group
            true_effect_size: True treatment effect to inject
        
        Returns:
            Dictionary with 'sales', 'media', 'controls' DataFrames
        """
        print(f"🎯 Generating synthetic Brightline data...")
        print(f"   Product: {product_name}")
        print(f"   Time period: {n_weeks} weeks from {start_date}")
        print(f"   Geographic units: {n_dmas} DMAs")
        print(f"   Test period: Last {test_period_weeks} weeks")
        print(f"   Treatment allocation: {treatment_pct:.0%}")
        print(f"   True effect size: {true_effect_size:.1%}")
        
        # Generate dates
        dates = pd.date_range(start=start_date, periods=n_weeks, freq='W-SUN')
        
        # Generate DMAs
        dmas = [f"DMA_{str(i).zfill(3)}" for i in range(1, n_dmas + 1)]
        
        # Determine test period
        test_start_idx = n_weeks - test_period_weeks
        test_start_date = dates[test_start_idx]
        
        # Assign treatment/control
        n_treatment = int(n_dmas * treatment_pct)
        treatment_dmas = np.random.choice(dmas, size=n_treatment, replace=False)
        
        print(f"   Treatment DMAs: {len(treatment_dmas)}")
        print(f"   Control DMAs: {n_dmas - len(treatment_dmas)}")
        
        # Generate base data structure
        base_data = []
        for date_idx, date in enumerate(dates):
            for dma in dmas:
                base_data.append({
                    'date': date,
                    'geo_id': dma,
                    'is_treatment': dma in treatment_dmas,
                    'is_test_period': date >= test_start_date,
                    'week_num': date_idx
                })
        
        base_df = pd.DataFrame(base_data)
        
        # Generate sales
        sales_df = self._generate_sales(base_df, product_name)
        
        # Generate media spend
        media_df = self._generate_media(base_df)
        
        # Generate control variables
        controls_df = self._generate_controls(base_df)

        # Merge treatment info back into sales for effect injection
        sales_df = sales_df.merge(
            base_df[['date', 'geo_id', 'is_treatment', 'is_test_period']], 
            on=['date', 'geo_id'], 
            how='left'
        )
        
        # Inject treatment effect
        sales_df = self._inject_treatment_effect(
            sales_df, 
            effect_size=true_effect_size
        )
        
        # Clean up temporary columns
        for df in [sales_df, media_df, controls_df]:
            df.drop(['is_treatment', 'is_test_period', 'week_num'], 
                   axis=1, errors='ignore', inplace=True)
        
        print(f"\n✅ Data generation complete!")
        print(f"   Sales records: {len(sales_df):,}")
        print(f"   Media records: {len(media_df):,}")
        print(f"   Control records: {len(controls_df):,}")
        
        return {
            'sales': sales_df,
            'media': media_df,
            'controls': controls_df,
            'metadata': {
                'product': product_name,
                'n_weeks': n_weeks,
                'n_dmas': n_dmas,
                'test_start_date': str(test_start_date),
                'treatment_dmas': treatment_dmas.tolist(),
                'true_effect_size': true_effect_size
            }
        }
    
    def _generate_sales(
        self, 
        base_df: pd.DataFrame,
        product_name: str
    ) -> pd.DataFrame:
        """
        Generate sales data with realistic patterns
        """
        df = base_df.copy()
        
        # Base sales level by DMA (heterogeneous market sizes)
        dma_base_sales = {
            dma: np.random.gamma(shape=2.0, scale=1200)
            for dma in df['geo_id'].unique()
        }
        df['base_sales'] = df['geo_id'].map(dma_base_sales)
        
        # Seasonality (skincare sells more in winter - dry skin season)
        # Peak in Jan-Feb, trough in summer
        df['week_of_year'] = pd.to_datetime(df['date']).dt.isocalendar().week
        df['seasonality'] = 1 + 0.25 * np.cos(2 * np.pi * (df['week_of_year'] - 6) / 52)
        
        # Trend (slowly growing brand)
        df['trend'] = 1 + 0.0015 * df['week_num']  # ~0.15% weekly growth
        
        # Random week-to-week variation
        df['random_shock'] = np.random.normal(1, 0.12, size=len(df))
        
        # Calculate base sales units
        df['sales_units'] = (
            df['base_sales'] * 
            df['seasonality'] * 
            df['trend'] * 
            df['random_shock']
        ).clip(0).round()
        
        # Price with some variation
        base_price = 15.00
        # df['price_per_unit'] = np.random.normal(base_price, 0.75, size=len(df)).clip(lower=12, upper=18)
        df['price_per_unit'] = np.random.normal(base_price, 0.75, size=len(df)).clip(12, 18)

        # Promotions (20% of weeks, boost sales by 18-25%)
        df['promo_flag'] = np.random.binomial(1, 0.20, size=len(df))
        promo_lift = np.random.uniform(1.18, 1.25, size=len(df))
        df.loc[df['promo_flag'] == 1, 'sales_units'] *= promo_lift[df['promo_flag'] == 1]
        
        # Calculate revenue
        df['sales_revenue'] = df['sales_units'] * df['price_per_unit']
        
        # Add product info
        df['product_sku'] = product_name
        
        return df[[
            'date', 'geo_id', 'product_sku', 
            'sales_units', 'sales_revenue', 'promo_flag'
        ]]
    
    def _generate_media(self, base_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate media spend data
        """
        channels = ['Meta', 'Google', 'Amazon', 'TikTok']
        
        # Base spend by channel
        channel_base_spend = {
            'Meta': 3500,
            'Google': 2800,
            'Amazon': 2200,
            'TikTok': 1500
        }
        
        media_rows = []
        
        for _, row in base_df.iterrows():
            for channel in channels:
                base_spend = channel_base_spend[channel]
                
                # Add DMA-level variation (bigger DMAs get more spend)
                dma_factor = 0.7 + 0.6 * np.random.random()
                
                # Add week-to-week variation
                weekly_variation = np.random.uniform(0.85, 1.15)
                
                spend = base_spend * dma_factor * weekly_variation
                
                # Treatment group gets 30% more spend during test period
                if row['is_test_period'] and row['is_treatment']:
                    spend *= 1.30
                
                # Generate corresponding metrics
                # Impressions: ~50-60 per dollar
                impressions = int(spend * np.random.uniform(48, 62))
                
                # CTR: 2.5-4%
                clicks = int(impressions * np.random.uniform(0.025, 0.04))
                
                media_rows.append({
                    'date': row['date'],
                    'geo_id': row['geo_id'],
                    'channel': channel,
                    'spend_usd': round(spend, 2),
                    'impressions': impressions,
                    'clicks': clicks
                })
        
        return pd.DataFrame(media_rows)
    
    def _generate_controls(self, base_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate control/covariate data
        """
        df = base_df[['date', 'geo_id']].copy()
        
        # Temperature (seasonal, varies by week)
        df['week_of_year'] = pd.to_datetime(df['date']).dt.isocalendar().week
        df['temperature'] = (
            55 + 
            25 * np.cos(2 * np.pi * (df['week_of_year'] - 1) / 52) +
            np.random.normal(0, 6, size=len(df))
        )
        
        # Holiday weeks
        holiday_weeks = [1, 24, 47, 52]  # New Year, Memorial Day, Thanksgiving, Christmas
        df['holiday_flag'] = df['week_of_year'].isin(holiday_weeks).astype(int)
        
        # Competitor promotion activity (15% of weeks)
        df['competitor_promo'] = np.random.binomial(1, 0.15, size=len(df))
        
        # Consumer confidence index (slowly changing)
        base_confidence = 100
        df['consumer_confidence'] = (
            base_confidence + 
            5 * np.sin(2 * np.pi * df['week_of_year'] / 52) +
            np.random.normal(0, 2, size=len(df))
        )
        
        df.drop('week_of_year', axis=1, inplace=True)
        
        return df
    
    def _inject_treatment_effect(
        self,
        sales_df: pd.DataFrame,
        effect_size: float = 0.12
    ) -> pd.DataFrame:
        """
        Inject realistic treatment effect
        
        Effect is:
        - Only in test period
        - Only for treatment DMAs
        - Proportional to existing sales (multiplicative)
        """
        df = sales_df.copy()
        
        # Apply effect
        mask = df['is_test_period'] & df['is_treatment']
        
        # Multiplicative lift
        df.loc[mask, 'sales_units'] *= (1 + effect_size)
        df.loc[mask, 'sales_revenue'] *= (1 + effect_size)
        
        n_affected = mask.sum()
        print(f"   💉 Injected {effect_size:.1%} treatment effect into {n_affected:,} records")
        
        return df
    
    def save_datasets(
        self,
        datasets: Dict[str, pd.DataFrame],
        output_dir: str = 'data/synthetic'
    ):
        """
        Save generated datasets to CSV
        """
        import os
        import json
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save data files
        for name, df in datasets.items():
            if name == 'metadata':
                continue
            filepath = os.path.join(output_dir, f'brightline_{name}.csv')
            df.to_csv(filepath, index=False)
            print(f"✅ Saved: {filepath}")
        
        # Save metadata
        if 'metadata' in datasets:
            metadata_path = os.path.join(output_dir, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(datasets['metadata'], f, indent=2)
            print(f"✅ Saved: {metadata_path}")


# Quick test / demo
if __name__ == "__main__":
    # Generate data
    generator = BrightlineSyntheticDataGenerator(seed=42)
    
    datasets = generator.generate_complete_dataset(
        n_weeks=104,
        n_dmas=150,
        test_period_weeks=20,
        treatment_pct=0.7,
        true_effect_size=0.12
    )
    
    # Save to files
    generator.save_datasets(datasets)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DATA SUMMARY")
    print("="*60)
    
    sales_df = datasets['sales']
    media_df = datasets['media']
    
    print(f"\nSales Data:")
    print(f"  Total records: {len(sales_df):,}")
    print(f"  Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")
    print(f"  Total revenue: ${sales_df['sales_revenue'].sum():,.0f}")
    print(f"  Avg weekly revenue per DMA: ${sales_df.groupby(['date', 'geo_id'])['sales_revenue'].sum().mean():,.0f}")
    
    print(f"\nMedia Data:")
    print(f"  Total records: {len(media_df):,}")
    print(f"  Channels: {', '.join(media_df['channel'].unique())}")
    print(f"  Total spend: ${media_df['spend_usd'].sum():,.0f}")
    print(f"  Avg weekly spend per DMA: ${media_df.groupby(['date', 'geo_id'])['spend_usd'].sum().mean():,.0f}")
    
    print("\n✅ Data generation complete!")