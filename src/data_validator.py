"""
Data Quality Validator for Brightline POV
Run this BEFORE any analysis to ensure data quality
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class DataQualityValidator:
    """
    Validate data quality before RCT analysis
    """
    
    def __init__(self, sales_df, media_df, controls_df=None):
        self.sales_df = sales_df.copy()
        self.media_df = media_df.copy()
        self.controls_df = controls_df.copy() if controls_df is not None else None
        
        self.issues = []
        self.warnings = []
        self.quality_score = 100  # Start at 100, deduct points for issues
    
    def run_full_validation(self):
        """
        Run all validation checks
        """
        print("🔍 Starting Data Quality Validation...\n")
        
        # Check 1: Completeness
        self._check_completeness()
        
        # Check 2: Consistency
        self._check_consistency()
        
        # Check 3: Temporal coverage
        self._check_temporal_coverage()
        
        # Check 4: Geographic coverage
        self._check_geographic_coverage()
        
        # Check 5: Outliers
        self._check_outliers()
        
        # Generate report
        report = self._generate_report()
        
        return report
    
    def _check_completeness(self):
        """
        Check for missing values
        """
        print("📋 Checking completeness...")
        
        for name, df in [('Sales', self.sales_df), ('Media', self.media_df)]:
            missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
            critical_missing = missing_pct[missing_pct > 5]
            
            if len(critical_missing) > 0:
                self.issues.append(
                    f"❌ {name} data has >5% missing in: {critical_missing.to_dict()}"
                )
                self.quality_score -= 10
            
            moderate_missing = missing_pct[(missing_pct > 1) & (missing_pct <= 5)]
            if len(moderate_missing) > 0:
                self.warnings.append(
                    f"⚠️  {name} data has 1-5% missing in: {moderate_missing.to_dict()}"
                )
                self.quality_score -= 5
        
        print("   ✅ Completeness check done\n")
    
    def _check_consistency(self):
        """
        Check for logical consistency
        """
        print("🔗 Checking consistency...")
        
        # Negative values check
        numeric_cols = self.sales_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in ['sales_units', 'sales_revenue']:
                negative_count = (self.sales_df[col] < 0).sum()
                if negative_count > 0:
                    self.issues.append(
                        f"❌ {col} has {negative_count} negative values"
                    )
                    self.quality_score -= 5
        
        # Check spend values
        if 'spend_usd' in self.media_df.columns:
            negative_spend = (self.media_df['spend_usd'] < 0).sum()
            if negative_spend > 0:
                self.issues.append(
                    f"❌ Media spend has {negative_spend} negative values"
                )
                self.quality_score -= 5
        
        print("   ✅ Consistency check done\n")
    
    def _check_temporal_coverage(self):
        """
        Check for date gaps
        """
        print("📅 Checking temporal coverage...")
        
        sales_dates = pd.to_datetime(self.sales_df['date']).sort_values().unique()
        
        # Check total weeks
        total_weeks = len(sales_dates)
        
        if total_weeks < 52:
            self.issues.append(
                f"❌ Only {total_weeks} weeks of data. Need ≥52 weeks."
            )
            self.quality_score -= 15
        elif total_weeks < 80:
            self.warnings.append(
                f"⚠️  Only {total_weeks} weeks of data. Recommend ≥80 weeks."
            )
            self.quality_score -= 5
        
        print(f"   Total weeks: {total_weeks}")
        print("   ✅ Temporal coverage check done\n")
    
    def _check_geographic_coverage(self):
        """
        Check geographic units
        """
        print("🗺️  Checking geographic coverage...")
        
        sales_geos = set(self.sales_df['geo_id'].unique())
        media_geos = set(self.media_df['geo_id'].unique())
        
        # Check if media and sales have same geos
        missing_in_media = sales_geos - media_geos
        missing_in_sales = media_geos - sales_geos
        
        if missing_in_media:
            self.warnings.append(
                f"⚠️  {len(missing_in_media)} geos in sales but not in media"
            )
            self.quality_score -= 3
        
        if missing_in_sales:
            self.warnings.append(
                f"⚠️  {len(missing_in_sales)} geos in media but not in sales"
            )
            self.quality_score -= 3
        
        # Check if we have enough geos for statistical power
        n_geos = len(sales_geos)
        if n_geos < 50:
            self.issues.append(
                f"❌ Only {n_geos} geographic units. Need ≥50 for adequate power."
            )
            self.quality_score -= 15
        elif n_geos < 100:
            self.warnings.append(
                f"⚠️  Only {n_geos} geographic units. Recommend ≥100."
            )
            self.quality_score -= 5
        
        print(f"   Total geos: {n_geos}")
        print("   ✅ Geographic coverage check done\n")
    
    def _check_outliers(self):
        """
        Detect outliers that could bias results
        """
        print("🔍 Checking for outliers...")
        
        # Z-score method for continuous variables
        for col in ['sales_revenue', 'sales_units']:
            if col in self.sales_df.columns:
                z_scores = np.abs(stats.zscore(self.sales_df[col].dropna()))
                outliers = (z_scores > 3).sum()
                
                if outliers > len(self.sales_df) * 0.05:  # >5% outliers
                    self.warnings.append(
                        f"⚠️  {col} has {outliers} outliers (>3 SD)"
                    )
                    self.quality_score -= 3
        
        print("   ✅ Outlier check done\n")
    
    def _generate_report(self):
        """
        Generate final report
        """
        print("=" * 60)
        print("📊 DATA QUALITY REPORT")
        print("=" * 60)
        
        # Overall score
        if self.quality_score >= 90:
            grade = "🟢 EXCELLENT"
            recommendation = "Data is ready for analysis"
        elif self.quality_score >= 75:
            grade = "🟡 GOOD"
            recommendation = "Data is usable, address warnings if possible"
        elif self.quality_score >= 60:
            grade = "🟠 FAIR"
            recommendation = "Address critical issues before proceeding"
        else:
            grade = "🔴 POOR"
            recommendation = "Data requires significant cleanup"
        
        print(f"\nOverall Quality Score: {self.quality_score}/100 - {grade}")
        print(f"Recommendation: {recommendation}\n")
        
        # Issues
        if self.issues:
            print("❌ CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  {issue}")
            print()
        
        # Warnings
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if not self.issues and not self.warnings:
            print("✅ No issues found! Data looks great.\n")
        
        print("=" * 60)
        
        return {
            'quality_score': self.quality_score,
            'grade': grade,
            'recommendation': recommendation,
            'issues': self.issues,
            'warnings': self.warnings
        }


# Quick test
if __name__ == "__main__":
    # Load data
    sales_df = pd.read_csv('data/synthetic/brightline_sales.csv')
    media_df = pd.read_csv('data/synthetic/brightline_media.csv')
    controls_df = pd.read_csv('data/synthetic/brightline_controls.csv')
    
    # Run validation
    validator = DataQualityValidator(sales_df, media_df, controls_df)
    report = validator.run_full_validation()
    
    print(f"\n💾 Quality Score: {report['quality_score']}")