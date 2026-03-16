\# Brightline RCT Incrementality Measurement



Complete end-to-end solution for measuring digital marketing incrementality using Randomized Controlled Trials (RCT) and Difference-in-Differences (DiD) analysis.



\## 🎯 Overview



This project provides a production-ready framework for:

\- Generating realistic synthetic marketing data

\- Validating data quality

\- Running DiD analysis with clustered standard errors

\- Calculating ROAS and ROI

\- Interactive Streamlit dashboard for stakeholder presentations



\## ✨ Features



\- \*\*Data Generator\*\*: Creates realistic synthetic data mimicking Brightline's business

\- \*\*Data Validator\*\*: Comprehensive quality checks (100-point scoring system)

\- \*\*DiD Analysis\*\*: Regression-based difference-in-differences with geo fixed effects

\- \*\*ROAS Calculator\*\*: Revenue and profit-adjusted return on ad spend

\- \*\*Interactive Dashboard\*\*: Streamlit web app with adjustable parameters

\- \*\*Visualizations\*\*: Parallel trends, treatment effects, confidence intervals



\## 📊 Key Results



\- \*\*Accuracy\*\*: Successfully recovers true treatment effects (12.08% vs 12% true)

\- \*\*Statistical Rigor\*\*: Clustered standard errors, p-values, confidence intervals

\- \*\*Scale\*\*: Handles 150+ DMAs, 100+ weeks of data

\- \*\*Speed\*\*: Complete analysis in < 30 seconds



\## 🚀 Quick Start



\### Installation

```bash

\# Clone the repository

git clone https://github.com/yourusername/brightline-rct-analysis.git

cd brightline-rct-analysis



\# Create virtual environment

python -m venv venv



\# Activate virtual environment

\# Windows:

.\\venv\\Scripts\\activate

\# Mac/Linux:

source venv/bin/activate



\# Install dependencies

pip install -r requirements.txt

```



\### Run Demo

```bash

\# Option 1: Run complete demo script

python run\_complete\_demo.py



\# Option 2: Launch interactive dashboard

streamlit run app/streamlit\_app.py

```



\## 📁 Project Structure

```

brightline-rct-analysis/

├── src/

│   ├── utils.py              # Helper functions

│   ├── data\_generator.py     # Synthetic data generation

│   ├── data\_validator.py     # Data quality checks

│   └── analysis\_did.py       # DiD analysis engine

├── app/

│   └── streamlit\_app.py      # Interactive dashboard

├── data/

│   └── synthetic/            # Generated data files

├── outputs/

│   ├── plots/                # Visualizations

│   └── reports/              # Analysis results

├── notebooks/                # Jupyter notebooks (optional)

├── run\_complete\_demo.py      # End-to-end demo script

├── requirements.txt          # Python dependencies

└── README.md                 # This file

```



\## 📖 Usage



\### 1. Generate Synthetic Data

```python

from src.data\_generator import BrightlineSyntheticDataGenerator



generator = BrightlineSyntheticDataGenerator(seed=42)

datasets = generator.generate\_complete\_dataset(

&nbsp;   n\_weeks=104,

&nbsp;   n\_dmas=150,

&nbsp;   test\_period\_weeks=20,

&nbsp;   treatment\_pct=0.7,

&nbsp;   true\_effect\_size=0.12

)

```



\### 2. Validate Data Quality

```python

from src.data\_validator import DataQualityValidator



validator = DataQualityValidator(sales\_df, media\_df, controls\_df)

report = validator.run\_full\_validation()

```



\### 3. Run DiD Analysis

```python

from src.analysis\_did import SimpleDiDAnalysis



did = SimpleDiDAnalysis(sales\_df, media\_df, controls\_df)

did.prepare\_data(test\_start\_date, treatment\_dmas)

results = did.estimate\_effect\_regression()

roas = did.calculate\_roas(results)

```



\## 📊 Dashboard Features



The Streamlit dashboard provides:

\- \*\*Data Generation\*\*: Adjustable parameters (DMAs, weeks, effect size)

\- \*\*Quality Check\*\*: Real-time data validation

\- \*\*Analysis\*\*: One-click DiD estimation

\- \*\*Visualizations\*\*: Parallel trends, treatment effects

\- \*\*Export\*\*: Download results as JSON/CSV



\## 🔬 Methodology



\### Difference-in-Differences (DiD)



The analysis uses a regression-based DiD approach:

```

Y = β₀ + β₁\*Treatment + β₂\*Post + β₃\*Treatment×Post + Controls + GeoFE + ε

```



Where:

\- \*\*Y\*\*: Sales revenue outcome

\- \*\*β₃\*\*: Treatment effect (DiD estimate)

\- \*\*Controls\*\*: Promotions, temperature, holidays

\- \*\*GeoFE\*\*: Geographic fixed effects

\- \*\*ε\*\*: Clustered errors by geography



\### Statistical Features

\- Clustered standard errors (by geo)

\- 95% confidence intervals

\- P-values for significance testing

\- Parallel trends validation

\- Pre-period balance checks



\## 📈 Results Example

```

Treatment Effect: $5,549.12 per geo-week

Statistical Significance: p < 0.0001

Percentage Lift: 12.09%

Profit ROAS (40% margin): 0.17x

Model R²: 0.906

```



\## 🛠️ Requirements



\- Python 3.9+

\- pandas >= 2.0

\- numpy >= 1.24

\- scipy >= 1.11

\- statsmodels >= 0.14

\- matplotlib >= 3.8

\- seaborn >= 0.13

\- streamlit >= 1.29



\## 📝 Next Steps



1\. \*\*Apply to Real Data\*\*: Replace synthetic data with actual Brightline campaign data

2\. \*\*Channel Analysis\*\*: Run separate analyses for Meta, Google, Amazon

3\. \*\*Advanced Methods\*\*: Add Bayesian Synthetic Control, Causal Forests

4\. \*\*Production Deployment\*\*: Automate with Airflow/Prefect pipelines



\## 🤝 Contributing



Contributions welcome! Please:

1\. Fork the repository

2\. Create a feature branch

3\. Commit your changes

4\. Open a pull request



\## 📄 License



MIT License - see LICENSE file for details



\## 👥 Authors



\- Your Name - Initial work



\## 🙏 Acknowledgments



\- Brightline team for domain expertise

\- Anthropic Claude for development assistance



\## 📞 Contact



For questions or support, contact: your.email@example.com




Heikenek Story
Logistics, E2E, agentic AI

i want to show you a platform we have build which a suite of app and accelators for various AI problem. UST Pulse.
this container is meant to be serve and pick only the service you need and incregate with your way of working.
i would like to run through a e2e example of how UST pulse can support your logistic functions.
we start with forecasting thye price of several lanes which will need to move our final produce from our brewery to final vendor.
Forecast: we forecast the price of each lane for 12 months. we're using the past ingormatio
we are taking into consideration only one countries with 100 lanes, and 5 logistic supplier. each supplier offers different prices for each lanes and make discount if you buy more than 5 lanes. 


jdbc:postgresql://***REMOVED***:5432/***REMOVED***



postgres
***REMOVED***



CompositeHandler
PostGreSqlMuxCompositeHandler
-
DefaultConnectionString
postgres://jdbc:postgresql://***REMOVED***:5432/***REMOVED***?user=postgres&password=***REMOVED***
-
DefaultScale
0
-
DisableSpillEncryption
false
-
LambdaFunctionName
***REMOVED***
-
LambdaMemory
3008
-
LambdaRoleARN
-
-
LambdaTimeout
900
-
PermissionsBoundaryARN
-
-
SecretNamePrefix
***REMOVED***

-
SecurityGroupIds
***REMOVED***
-
SpillBucket
***REMOVED***
-
SpillPrefix
athena-spill
-
SubnetIds
***REMOVED***,***REMOVED***


