"""
Utility functions for the POV
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

def setup_directories():
    """Create project directory structure"""
    import os
    
    dirs = [
        'data/synthetic',
        'data/real',
        'outputs/plots',
        'outputs/reports'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("✅ Directory structure created")


def calculate_roas(
    incremental_sales: float,
    marketing_spend: float
) -> Dict[str, float]:
    """
    Calculate Return on Ad Spend (ROAS)
    
    Args:
        incremental_sales: Additional sales from marketing
        marketing_spend: Total marketing spend
    
    Returns:
        Dictionary with ROAS metrics
    """
    roas = incremental_sales / marketing_spend if marketing_spend > 0 else 0
    roi = (incremental_sales - marketing_spend) / marketing_spend if marketing_spend > 0 else 0
    
    return {
        'roas': roas,
        'roi': roi,
        'roi_pct': roi * 100,
        'incremental_sales': incremental_sales,
        'marketing_spend': marketing_spend,
        'profit': incremental_sales - marketing_spend
    }


def format_currency(value: float) -> str:
    """Format number as currency"""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format number as percentage"""
    return f"{value:.2f}%"


def create_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create summary statistics table
    
    Args:
        df: DataFrame with numeric columns
    
    Returns:
        Summary statistics DataFrame
    """
    summary = df.describe().T
    summary['missing_pct'] = (df.isnull().sum() / len(df) * 100).values
    
    return summary.round(2)


def detect_test_period(
    df: pd.DataFrame,
    date_col: str = 'date',
    percentile: float = 0.8
) -> Tuple[datetime, datetime]:
    """
    Auto-detect test period (assumes last 20% of data)
    
    Args:
        df: DataFrame with date column
        date_col: Name of date column
        percentile: Where test period starts (0.8 = last 20%)
    
    Returns:
        Tuple of (test_start_date, test_end_date)
    """
    dates = pd.to_datetime(df[date_col]).sort_values()
    test_start = dates.quantile(percentile)
    test_end = dates.max()
    
    return test_start, test_end


def assign_treatment_control(
    geo_ids: List[str],
    treatment_pct: float = 0.7,
    seed: int = 42
) -> Dict[str, bool]:
    """
    Randomly assign geos to treatment/control
    
    Args:
        geo_ids: List of geographic identifiers
        treatment_pct: Percentage to assign to treatment (0-1)
        seed: Random seed for reproducibility
    
    Returns:
        Dictionary mapping geo_id -> is_treatment (bool)
    """
    np.random.seed(seed)
    
    n_treatment = int(len(geo_ids) * treatment_pct)
    treatment_geos = np.random.choice(geo_ids, size=n_treatment, replace=False)
    
    return {geo: (geo in treatment_geos) for geo in geo_ids}


def check_balance(
    df: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    pre_period_filter: pd.Series
) -> Dict[str, float]:
    """
    Check balance between treatment and control in pre-period
    
    Args:
        df: DataFrame with data
        treatment_col: Name of treatment indicator column
        outcome_col: Name of outcome variable
        pre_period_filter: Boolean series for pre-period rows
    
    Returns:
        Dictionary with balance statistics
    """
    pre_df = df[pre_period_filter]
    
    treatment_mean = pre_df[pre_df[treatment_col] == True][outcome_col].mean()
    control_mean = pre_df[pre_df[treatment_col] == False][outcome_col].mean()
    
    diff = treatment_mean - control_mean
    diff_pct = (diff / control_mean) * 100 if control_mean != 0 else 0
    
    return {
        'treatment_mean': treatment_mean,
        'control_mean': control_mean,
        'difference': diff,
        'difference_pct': diff_pct,
        'is_balanced': abs(diff_pct) < 10  # <10% difference is acceptable
    }


def calculate_statistical_power(
    n_geos: int,
    n_weeks: int,
    baseline_std: float,
    mde: float = 0.10,
    alpha: float = 0.05
) -> float:
    """
    Calculate statistical power for DiD design
    
    Args:
        n_geos: Number of geographic units
        n_weeks: Number of weeks in test period
        baseline_std: Standard deviation of baseline outcome
        mde: Minimum detectable effect (as proportion, e.g., 0.10 = 10%)
        alpha: Significance level
    
    Returns:
        Statistical power (0-1)
    """
    from scipy import stats
    
    # Simplified power calculation for cluster-randomized design
    # Effective sample size
    effective_n = n_geos * n_weeks / 2  # Divide by 2 for treatment/control split
    
    # Effect size (Cohen's d)
    effect_size = mde / (baseline_std / np.sqrt(effective_n))
    
    # Power calculation
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = effect_size - z_alpha
    power = stats.norm.cdf(z_beta)
    
    return max(0, min(1, power))


def export_results(
    results: Dict,
    filename: str,
    output_dir: str = 'outputs/reports'
):
    """
    Export results to CSV and JSON
    
    Args:
        results: Dictionary of results
        filename: Base filename (without extension)
        output_dir: Output directory
    """
    import json
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as JSON
    json_path = os.path.join(output_dir, f"{filename}.json")
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"✅ Results saved to {json_path}")
    
    # If results contain dataframes, save as CSV
    if any(isinstance(v, pd.DataFrame) for v in results.values()):
        for key, value in results.items():
            if isinstance(value, pd.DataFrame):
                csv_path = os.path.join(output_dir, f"{filename}_{key}.csv")
                value.to_csv(csv_path, index=False)
                print(f"✅ {key} saved to {csv_path}")


class ProgressTracker:
    """Simple progress tracker for long-running operations"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, step_name: str = ""):
        self.current_step += 1
        pct = (self.current_step / self.total_steps) * 100
        elapsed = (datetime.now() - self.start_time).seconds
        
        print(f"[{pct:5.1f}%] {self.description}: {step_name} ({self.current_step}/{self.total_steps})")
    
    def complete(self):
        elapsed = (datetime.now() - self.start_time).seconds
        print(f"✅ {self.description} complete in {elapsed}s")


if __name__ == "__main__":
    # Test utilities
    setup_directories()
    
    # Test ROAS calculation
    roas_metrics = calculate_roas(
        incremental_sales=100000,
        marketing_spend=20000
    )
    print(f"\nROAS Test: {roas_metrics}")
    
    # Test power calculation
    power = calculate_statistical_power(
        n_geos=150,
        n_weeks=20,
        baseline_std=5000,
        mde=0.12
    )
    print(f"\nStatistical Power: {power:.2%}")