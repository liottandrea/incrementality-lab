"""
Heterogeneous Treatment Effects (HTE) Analyzer
Analyzes how treatment effects vary across:
- Age segments
- Retail channels
- Promotion types
- Geographic markets
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    import statsmodels.formula.api as smf
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False


class HeterogeneousEffectsAnalyzer:
    """
    Analyze heterogeneous treatment effects across different dimensions
    """
    
    def __init__(self, sales_df, transactions_df=None, controls_df=None):
        """
        Initialize analyzer
        
        Args:
            sales_df: Aggregate sales data
            transactions_df: Transaction-level data (optional)
            controls_df: Control variables
        """
        self.sales_df = sales_df.copy()
        self.transactions_df = transactions_df.copy() if transactions_df is not None else None
        self.controls_df = controls_df.copy() if controls_df is not None else None
        self.has_transaction_data = transactions_df is not None and not transactions_df.empty
    
    def analyze_complete(self, test_start_date, treatment_dmas):
        """
        Run complete heterogeneous effects analysis
        
        Args:
            test_start_date: When test started
            treatment_dmas: List of treatment DMAs
        
        Returns:
            Dictionary with all HTE results
        """
        print("🔬 Analyzing Heterogeneous Treatment Effects...")
        
        # Prepare data
        self._prepare_data(test_start_date, treatment_dmas)
        
        results = {}
        
        # 1. Effects by retail channel
        print("\n1️⃣ Analyzing effects by retail channel...")
        channel_effects = self.analyze_by_channel()
        results['channel_effects'] = channel_effects
        
        # 2. Effects by promotion type
        print("\n2️⃣ Analyzing effects by promotion type...")
        promo_effects = self.analyze_by_promo_type()
        results['promo_effects'] = promo_effects
        
        # 3. Effects by age (if transaction data available)
        if self.has_transaction_data:
            print("\n3️⃣ Analyzing effects by age segment...")
            age_effects = self.analyze_by_age()
            results['age_effects'] = age_effects
        else:
            print("\n3️⃣ Skipping age analysis (no transaction data)")
            results['age_effects'] = None
        
        # 4. Interaction effects
        if self.has_transaction_data:
            print("\n4️⃣ Analyzing interaction effects...")
            interaction_effects = self.analyze_interactions()
            results['interaction_effects'] = interaction_effects
        else:
            results['interaction_effects'] = None
        
        print("\n✅ Heterogeneous effects analysis complete!")
        return results
    
    def _prepare_data(self, test_start_date, treatment_dmas):
        """
        Prepare data for analysis
        """
        # Sales data
        self.sales_df['date'] = pd.to_datetime(self.sales_df['date'])
        test_start_date = pd.to_datetime(test_start_date)
        
        self.sales_df['is_treatment'] = self.sales_df['geo_id'].isin(treatment_dmas)
        self.sales_df['is_post'] = self.sales_df['date'] >= test_start_date
        self.sales_df['treatment_x_post'] = (
            self.sales_df['is_treatment'].astype(int) * self.sales_df['is_post'].astype(int)
        )
        
        # Transaction data
        if self.has_transaction_data:
            self.transactions_df['date'] = pd.to_datetime(self.transactions_df['date'])
            self.transactions_df['is_treatment'] = self.transactions_df['geo_id'].isin(treatment_dmas)
            self.transactions_df['is_post'] = self.transactions_df['date'] >= test_start_date
            self.transactions_df['treatment_x_post'] = (
                self.transactions_df['is_treatment'].astype(int) * 
                self.transactions_df['is_post'].astype(int)
            )
        
        # Merge controls if available
        if self.controls_df is not None:
            self.controls_df['date'] = pd.to_datetime(self.controls_df['date'])
            self.sales_df = self.sales_df.merge(
                self.controls_df, 
                on=['date', 'geo_id'], 
                how='left'
            )
    
    def analyze_by_channel(self):
        """
        Analyze treatment effects by retail channel
        """
        channels = self.sales_df['retail_channel'].unique()
        results = {}
        
        for channel in channels:
            channel_df = self.sales_df[self.sales_df['retail_channel'] == channel]
            
            # Simple DiD calculation
            pre_treatment = channel_df[
                (channel_df['is_post']==False) & (channel_df['is_treatment']==True)
            ]['sales_revenue'].mean()
            
            pre_control = channel_df[
                (channel_df['is_post']==False) & (channel_df['is_treatment']==False)
            ]['sales_revenue'].mean()
            
            post_treatment = channel_df[
                (channel_df['is_post']==True) & (channel_df['is_treatment']==True)
            ]['sales_revenue'].mean()
            
            post_control = channel_df[
                (channel_df['is_post']==True) & (channel_df['is_treatment']==False)
            ]['sales_revenue'].mean()
            
            # DiD estimate
            treatment_change = post_treatment - pre_treatment
            control_change = post_control - pre_control
            did_effect = treatment_change - control_change
            
            # Percentage lift
            pct_lift = (did_effect / pre_control * 100) if pre_control > 0 else 0
            
            results[channel] = {
                'treatment_effect': did_effect,
                'pct_lift': pct_lift,
                'pre_control_avg': pre_control,
                'post_treatment_avg': post_treatment,
                'n_observations': len(channel_df)
            }
            
            print(f"   {channel}: {pct_lift:.2f}% lift (${did_effect:,.0f})")
        
        return results
    
    def analyze_by_promo_type(self):
        """
        Analyze treatment effects by promotion type
        """
        # Focus on test period
        test_df = self.sales_df[self.sales_df['is_post'] == True].copy()
        
        # Remove NaN promo types and 'None'
        test_df = test_df[test_df['promo_type'].notna()]
        promo_types = test_df['promo_type'].unique()
        promo_types = [p for p in promo_types if str(p) != 'None' and str(p) != 'nan']
        
        if len(promo_types) == 0:
            print("   No promotion data available")
            return {}
        
        results = {}
        
        for promo_type in promo_types:
            promo_df = test_df[test_df['promo_type'] == promo_type]
            
            # Skip if insufficient data
            if len(promo_df) < 10:
                continue
            
            # Treatment vs control during promo weeks
            treatment_avg = promo_df[
                promo_df['is_treatment'] == True
            ]['sales_revenue'].mean()
            
            control_avg = promo_df[
                promo_df['is_treatment'] == False
            ]['sales_revenue'].mean()
            
            # Get baseline (no promo weeks)
            baseline_df = test_df[test_df['promo_type'] == 'None']
            
            if len(baseline_df) > 0:
                baseline_treatment = baseline_df[
                    baseline_df['is_treatment'] == True
                ]['sales_revenue'].mean()
                
                baseline_control = baseline_df[
                    baseline_df['is_treatment'] == False
                ]['sales_revenue'].mean()
            else:
                # Use overall pre-period if no 'None' promo type
                pre_df = self.sales_df[self.sales_df['is_post'] == False]
                baseline_treatment = pre_df[
                    pre_df['is_treatment'] == True
                ]['sales_revenue'].mean()
                
                baseline_control = pre_df[
                    pre_df['is_treatment'] == False
                ]['sales_revenue'].mean()
            
            # Calculate effect
            if pd.notna(baseline_treatment) and pd.notna(baseline_control):
                treatment_lift = treatment_avg - baseline_treatment
                control_lift = control_avg - baseline_control
                incremental_effect = treatment_lift - control_lift
                
                pct_lift = (incremental_effect / baseline_control * 100) if baseline_control > 0 else 0
                
                results[promo_type] = {
                    'incremental_effect': incremental_effect,
                    'pct_lift': pct_lift,
                    'treatment_avg': treatment_avg,
                    'control_avg': control_avg,
                    'n_observations': len(promo_df)
                }
                
                print(f"   {promo_type}: {pct_lift:.2f}% incremental lift (${incremental_effect:,.0f})")
        
        if len(results) == 0:
            print("   No valid promotion data for analysis")
            # Return a dummy result to prevent plotting errors
            results['No_Promo_Data'] = {
                'incremental_effect': 0,
                'pct_lift': 0,
                'treatment_avg': 0,
                'control_avg': 0,
                'n_observations': 0
            }
        
        return results
    
    def analyze_by_age(self):
        """
        Analyze treatment effects by age segment (requires transaction data)
        """
        if not self.has_transaction_data:
            return None
        
        df = self.transactions_df.copy()
        age_segments = df['age_segment'].unique()
        
        results = {}
        
        for age in age_segments:
            age_df = df[df['age_segment'] == age]
            
            # Pre-period
            pre_treatment = age_df[
                (age_df['is_post']==False) & (age_df['is_treatment']==True)
            ]['revenue'].mean()
            
            pre_control = age_df[
                (age_df['is_post']==False) & (age_df['is_treatment']==False)
            ]['revenue'].mean()
            
            # Post-period
            post_treatment = age_df[
                (age_df['is_post']==True) & (age_df['is_treatment']==True)
            ]['revenue'].mean()
            
            post_control = age_df[
                (age_df['is_post']==True) & (age_df['is_treatment']==False)
            ]['revenue'].mean()
            
            # DiD
            treatment_change = post_treatment - pre_treatment
            control_change = post_control - pre_control
            did_effect = treatment_change - control_change
            
            pct_lift = (did_effect / pre_control * 100) if pre_control > 0 else 0
            
            # Calculate average transaction size
            avg_transaction = age_df[age_df['is_post']==True]['revenue'].mean()
            
            results[age] = {
                'treatment_effect': did_effect,
                'pct_lift': pct_lift,
                'avg_transaction_size': avg_transaction,
                'n_transactions': len(age_df[age_df['is_post']==True])
            }
            
            print(f"   {age}: {pct_lift:.2f}% lift (${did_effect:,.2f} per transaction)")
        
        return results
    
    def analyze_interactions(self):
        """
        Analyze interaction effects (Age × Promo Type, Channel × Promo Type)
        """
        if not self.has_transaction_data:
            return None
        
        df = self.transactions_df[self.transactions_df['is_post'] == True].copy()
        
        results = {
            'age_x_promo': {},
            'channel_x_promo': {}
        }
        
        # Age × Promo Type
        print("\n   Analyzing Age × Promo Type interactions...")
        age_promo_groups = df.groupby(['age_segment', 'promo_type'])
        
        for (age, promo), group in age_promo_groups:
            if promo == 'None':
                continue
            
            treatment_avg = group[group['is_treatment']==True]['revenue'].mean()
            control_avg = group[group['is_treatment']==False]['revenue'].mean()
            
            effect = treatment_avg - control_avg
            
            key = f"{age}_{promo}"
            results['age_x_promo'][key] = {
                'age': age,
                'promo_type': promo,
                'effect': effect,
                'treatment_avg': treatment_avg,
                'control_avg': control_avg,
                'n_transactions': len(group)
            }
        
        # Channel × Promo Type
        print("   Analyzing Channel × Promo Type interactions...")
        
        # Merge sales with channel info
        sales_test = self.sales_df[self.sales_df['is_post'] == True].copy()
        channel_promo_groups = sales_test.groupby(['retail_channel', 'promo_type'])
        
        for (channel, promo), group in channel_promo_groups:
            if promo == 'None':
                continue
            
            treatment_avg = group[group['is_treatment']==True]['sales_revenue'].mean()
            control_avg = group[group['is_treatment']==False]['sales_revenue'].mean()
            
            effect = treatment_avg - control_avg
            
            key = f"{channel}_{promo}"
            results['channel_x_promo'][key] = {
                'channel': channel,
                'promo_type': promo,
                'effect': effect,
                'treatment_avg': treatment_avg,
                'control_avg': control_avg,
                'n_observations': len(group)
            }
        
        return results
    
    def plot_hte_results(self, results, save_path='outputs/plots/hte_analysis.png'):
        """
        Visualize heterogeneous treatment effects
        """
        import os
        os.makedirs('outputs/plots', exist_ok=True)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Heterogeneous Treatment Effects Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Effects by Channel
        channel_data = results['channel_effects']
        channels = list(channel_data.keys())
        lifts = [channel_data[c]['pct_lift'] for c in channels]
        
        axes[0, 0].bar(channels, lifts, color='steelblue', edgecolor='black')
        axes[0, 0].set_title('Treatment Effect by Retail Channel', fontsize=12, fontweight='bold')
        axes[0, 0].set_ylabel('% Lift')
        axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        for i, v in enumerate(lifts):
            axes[0, 0].text(i, v, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Plot 2: Effects by Promo Type
        promo_data = results['promo_effects']

        if promo_data and len(promo_data) > 0 and 'No_Promo_Data' not in promo_data:
            promos = list(promo_data.keys())
            promo_lifts = [promo_data[p]['pct_lift'] for p in promos]
            
            colors = ['green' if v > 10 else 'orange' if v > 5 else 'red' for v in promo_lifts]
            axes[0, 1].bar(promos, promo_lifts, color=colors, edgecolor='black')
            axes[0, 1].set_title('Treatment Effect by Promotion Type', fontsize=12, fontweight='bold')
            axes[0, 1].set_ylabel('% Lift')
            axes[0, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
            axes[0, 1].tick_params(axis='x', rotation=45)
            for i, v in enumerate(promo_lifts):
                axes[0, 1].text(i, v, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
        else:
            axes[0, 1].text(0.5, 0.5, 'Insufficient promotion data', 
                        ha='center', va='center', transform=axes[0, 1].transAxes,
                        fontsize=12)
            axes[0, 1].set_title('Treatment Effect by Promotion Type', fontsize=12, fontweight='bold')
                
        # Plot 3: Effects by Age (if available)
        if results['age_effects']:
            age_data = results['age_effects']
            ages = list(age_data.keys())
            age_lifts = [age_data[a]['pct_lift'] for a in ages]
            
            axes[1, 0].bar(ages, age_lifts, color='coral', edgecolor='black')
            axes[1, 0].set_title('Treatment Effect by Age Segment', fontsize=12, fontweight='bold')
            axes[1, 0].set_ylabel('% Lift')
            axes[1, 0].set_xlabel('Age Segment')
            axes[1, 0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
            axes[1, 0].tick_params(axis='x', rotation=45)
            for i, v in enumerate(age_lifts):
                axes[1, 0].text(i, v, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
        else:
            axes[1, 0].text(0.5, 0.5, 'No transaction data available', 
                          ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Treatment Effect by Age Segment', fontsize=12, fontweight='bold')
        
        # Plot 4: Top Interactions (if available)
        if results['interaction_effects']:
            interactions = results['interaction_effects']['age_x_promo']
            
            # Get top 10 interactions
            sorted_interactions = sorted(
                interactions.items(), 
                key=lambda x: abs(x[1]['effect']), 
                reverse=True
            )[:10]
            
            labels = [k.replace('_', '\n') for k, v in sorted_interactions]
            effects = [v['effect'] for k, v in sorted_interactions]
            
            colors = ['green' if e > 0 else 'red' for e in effects]
            axes[1, 1].barh(labels, effects, color=colors, edgecolor='black', alpha=0.7)
            axes[1, 1].set_title('Top 10 Age × Promo Interactions', fontsize=12, fontweight='bold')
            axes[1, 1].set_xlabel('Effect ($)')
            axes[1, 1].axvline(x=0, color='black', linestyle='-', alpha=0.3)
        else:
            axes[1, 1].text(0.5, 0.5, 'No interaction data available', 
                          ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Top Interactions', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        # Only save if save_path is provided
        if save_path is not None:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n📊 Saved: {save_path}")

        return fig
    
    def generate_recommendations(self, results):
        """
        Generate actionable recommendations based on HTE analysis
        """
        print("\n" + "="*60)
        print("💡 RECOMMENDATIONS")
        print("="*60)
        
        # Best performing channel
        channel_effects = results['channel_effects']
        best_channel = max(channel_effects.items(), key=lambda x: x[1]['pct_lift'])
        print(f"\n1. Best Performing Channel: {best_channel[0]}")
        print(f"   - Lift: {best_channel[1]['pct_lift']:.2f}%")
        print(f"   - Recommendation: Prioritize marketing spend in {best_channel[0]}")
        
        # Best performing promo type
        promo_effects = results['promo_effects']
        best_promo = max(promo_effects.items(), key=lambda x: x[1]['pct_lift'])
        print(f"\n2. Best Performing Promotion: {best_promo[0]}")
        print(f"   - Lift: {best_promo[1]['pct_lift']:.2f}%")
        print(f"   - Recommendation: Focus on {best_promo[0]} promotions")
        
        # Age insights (if available)
        if results['age_effects']:
            age_effects = results['age_effects']
            best_age = max(age_effects.items(), key=lambda x: x[1]['pct_lift'])
            print(f"\n3. Most Responsive Age Segment: {best_age[0]}")
            print(f"   - Lift: {best_age[1]['pct_lift']:.2f}%")
            print(f"   - Recommendation: Target {best_age[0]} for maximum impact")
        
        # Interaction insights
        if results['interaction_effects']:
            age_promo = results['interaction_effects']['age_x_promo']
            best_combo = max(age_promo.items(), key=lambda x: x[1]['effect'])
            
            print(f"\n4. Best Age × Promo Combination: {best_combo[0]}")
            print(f"   - Effect: ${best_combo[1]['effect']:,.2f}")
            print(f"   - Recommendation: Run {best_combo[1]['promo_type']} promos targeting {best_combo[1]['age']} customers")
        
        print("\n" + "="*60)


# Test
if __name__ == "__main__":
    # Load data
    sales_df = pd.read_csv('data/synthetic_v2/brightline_sales_v2.csv')
    
    try:
        transactions_df = pd.read_csv('data/synthetic_v2/brightline_transactions_v2.csv')
    except:
        transactions_df = None
    
    try:
        controls_df = pd.read_csv('data/synthetic_v2/brightline_controls_v2.csv')
    except:
        controls_df = None
    
    # Load metadata
    import json
    with open('data/synthetic_v2/metadata_v2.json', 'r') as f:
        metadata = json.load(f)
    
    # Run analysis
    analyzer = HeterogeneousEffectsAnalyzer(sales_df, transactions_df, controls_df)
    
    results = analyzer.analyze_complete(
        test_start_date=metadata['test_start_date'],
        treatment_dmas=metadata['treatment_dmas']
    )
    
    # Plot
    analyzer.plot_hte_results(results)
    
    # Generate recommendations
    analyzer.generate_recommendations(results)