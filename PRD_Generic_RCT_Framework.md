# PRD: Generic RCT Incrementality Framework
**Version:** 1.0
**Date:** 2026-03-16
**Status:** Draft

---

## 1. Overview

### 1.1 Problem Statement

The current RCT Incrementality platform is tightly coupled to Brightline's specific dataset structure, brand styling, and hardcoded assumptions (50 DMAs, specific retail channels, Brightline product categories, UST brand colors). As a result, applying the same rigorous causal inference methodology to a new client or dataset requires significant manual rework — renaming fields, adjusting hardcoded constants, swapping styling, and re-validating the entire pipeline.

### 1.2 Goal

Generalize the RCT Incrementality platform into a **client-agnostic, configuration-driven framework** that can be deployed against any new dataset running a geo-based or customer-level A/B / RCT experiment — without touching core analysis code.

### 1.3 Success Criteria

| Metric | Target |
|--------|--------|
| Time to onboard a new client dataset | < 2 hours (vs. ~2 days today) |
| Lines of code changed per new deployment | < 50 (config only, zero analysis code changes) |
| Data schemas supported | Geo-level + customer-level + media spend |
| Analysis parity with current app | 100% — all 5 analysis modules preserved |
| New demo data generator | Configurable via a single YAML/JSON config file |

---

## 2. Background & Current State

### 2.1 What the Current App Does

The existing app runs a **7-step Randomized Controlled Trial (RCT) incrementality measurement pipeline**:

1. **Data Load** — Ingests 4 CSV datasets (sales, transactions, media, controls) + JSON metadata
2. **Quality Validation** — Scores data quality 0–100, blocks progression if score < 80
3. **EDA** — Exploratory distributions, trends, segment breakdowns
4. **Model Setup** — Configures a Difference-in-Differences (DiD) regression with geographic and time fixed effects
5. **Results** — Estimates causal treatment effect, p-values, confidence intervals, heterogeneous effects by segment
6. **ROI Insights** — Multi-period ROI (short/medium/long-term), scenario analysis (stockpiling vs. expansion vs. new customers)
7. **Export** — JSON + CSV download of all findings

**Core statistical model:**
```
Y_igt = β₀ + β₁(Treatment) + β₂(Post) + β₃(Treatment × Post)
        + Controls + α_g + γ_t + ε_igt
```

`β₃` is the causal treatment effect (the key deliverable).

### 2.2 What Is Hardcoded Today (Must Be Generalized)

| Category | Hardcoded element | Location |
|----------|------------------|----------|
| Brand | "Brightline", UST brand colors (#006E74, #0097AC, #FF6B00) | All UI files |
| Dataset | Column names (`geo_id`, `retail_channel`, `age_segment`, etc.) | `src/`, `app/module_pages/` |
| Segments | Retail channels: Store / Omnichannel / Online_Specialty | `data_generator_v4.py`, `results.py` |
| Segments | Age bands: 18-24, 25-34, 35-44, 45-54, 55-64, 65+ | `data_generator_v4.py`, `purchase_dynamics.py` |
| Media | Channels: Meta, Google, Amazon, TikTok | `data_generator_v4.py` |
| Geo | 50 DMAs, 70% treatment assignment | `data_generator_v4.py` |
| Effects | price_effect=0.30, visibility_effect=0.20 | `data_generator_v4.py` |
| ROI params | profit_margin=0.80, avg_clv=$150, retention=0.60 | `roi_calculator.py`, `roi_insights.py` |

---

## 3. Target Use Cases

### Primary
- **Agency reuse:** A consulting team uses this framework across multiple client engagements (CPG, retail, pharma, e-commerce) without rebuilding the app each time
- **New client onboarding:** A client provides their own geo-level or transaction-level RCT dataset; the framework ingests it with minimal configuration

### Secondary
- **Synthetic data generation for demos:** Generate a realistic demo dataset for any industry vertical from a single config file
- **Internal research:** Run the DiD analysis on publicly available datasets (e.g., academic RCTs, policy experiments)

### Out of Scope (v1)
- Multi-experiment comparison (running two campaigns simultaneously)
- Automated data ingestion from APIs (BigQuery, Snowflake, S3) — file upload only in v1
- Bayesian / synthetic control methods (DiD remains the primary method)
- Real-time / streaming data

---

## 4. Requirements

### 4.1 Configuration Layer

**FR-1: Central config file**
All client-specific parameters must live in a single `config.yaml` (or `config.json`) file at the repo root. The app reads this at startup; no Python file changes are required to onboard a new client.

Minimum required config fields:
```yaml
client:
  name: "Acme Corp"
  industry: "CPG"              # for display copy only
  primary_color: "#0055A4"
  secondary_color: "#FF9900"
  logo_path: "assets/logo.png"  # optional

experiment:
  geo_column: "market_id"       # column name in data
  treatment_column: "is_treatment"
  period_column: "period"       # or date-based derivation
  pre_period_label: "pre"       # value in period_column
  test_period_label: "test"
  post_period_label: "post"
  outcome_column: "revenue"
  date_column: "date"

segments:
  primary_segment: "channel"    # column used for HTE breakdown
  secondary_segment: "age_group"  # optional second dimension
  media_channels: ["Meta", "Google", "TV"]  # for spend attribution

roi_defaults:
  profit_margin: 0.75
  avg_clv: 120
  retention_rate: 0.55
  discount_rate: 0.10
```

**FR-2: Column mapping**
The config must support aliasing any input column name to the internal canonical names the analysis code uses. This avoids renaming columns in source data.

```yaml
column_map:
  geo_id: "dma_code"            # their column → our canonical name
  sales_revenue: "net_revenue"
  is_new_customer: "new_buyer_flag"
```

**FR-3: Config validation on startup**
On app launch, validate that all required config fields are present and that mapped columns exist in the uploaded dataset. Surface clear errors — not Python tracebacks.

---

### 4.2 Data Ingestion

**FR-4: File upload UI**
Replace the hardcoded "Connect to Database" button with a file upload interface. Users upload CSV files for each dataset type (sales, transactions, media, controls). Each upload is optional except sales (which is required).

**FR-5: Schema auto-detection**
After upload, auto-detect column types (date, numeric, categorical) and suggest mappings to canonical schema. User can confirm or override suggestions.

**FR-6: Flexible dataset structure**
The framework must handle two dataset archetypes:

| Archetype | Description | Minimum required columns |
|-----------|-------------|--------------------------|
| **Geo-level** | Aggregated sales by geo + week (no customer IDs) | geo_id, date, is_treatment, outcome, period flags |
| **Customer-level** | Individual transactions with customer IDs | geo_id, date, customer_id, is_treatment, revenue |

If only geo-level data is provided, disable the "Purchase Dynamics" and demographic HTE modules gracefully (show a notice, don't crash).

---

### 4.3 Analysis Modules

All 5 core analysis modules must be preserved. Changes are limited to removing hardcoded field names and segment values.

**FR-7: DiD regression**
Parameterize the regression formula using config values. The model specification currently hardcodes `C(geo_id)` and specific covariate names — these must come from config.

**FR-8: Heterogeneous Treatment Effects (HTE)**
Segment dimensions (currently `retail_channel`, `age_segment`) must be driven by `segments.primary_segment` and `segments.secondary_segment` from config. The analysis loops over unique values of those columns — no hardcoded category lists.

**FR-9: Purchase Dynamics**
Stockpiling / new customer / expansion detection logic currently depends on the `is_new_customer` flag. This column must be mappable via `column_map`. If absent, skip new-customer analysis and note it in the results.

**FR-10: ROI Calculator**
Default parameters (margin, CLV, retention, discount rate) come from config but remain user-adjustable via the UI sliders (existing behavior preserved).

---

### 4.4 Demo Data Generator

**FR-11: Config-driven synthetic data**
`data_generator_v4.py` currently generates Brightline-specific data. The new generator must accept the same `config.yaml` and produce a synthetic dataset that matches the configured schema:

- Uses configured segment names (not hardcoded "Store / Omnichannel / Online_Specialty")
- Uses configured geo count, treatment %, time periods
- Produces column names matching `column_map` entries (or canonical names if no map)
- Saves output to `data/demo/` with the same 4-file structure

```bash
python generate_demo_data.py --config config.yaml --output data/demo/
```

**FR-12: Industry-specific effect presets**
Provide pre-built effect size presets for common industries that a user can reference in config:

```yaml
demo_preset: "cpg_price_promo"   # loads sensible defaults for this vertical
```

Presets available at launch: `cpg_price_promo`, `ecommerce_discount`, `pharma_awareness`, `retail_loyalty`.

---

### 4.5 UI / Branding

**FR-13: Theming from config**
Primary and secondary brand colors, client name, and logo (optional) are injected from config at startup. Remove all hardcoded "Brightline" and UST color references from UI code.

**FR-14: Graceful degradation**
When optional datasets (transactions, media, controls) are absent:
- Disable the corresponding UI sections with an informational banner
- Do not show empty charts or Python errors
- Still allow full DiD analysis on geo-level sales data alone

**FR-15: Module gating preserved**
The existing gate logic (must complete prior steps before advancing) is preserved as-is.

---

### 4.6 Export

**FR-16: Configurable report title**
The exported JSON/CSV report header uses `client.name` and `client.industry` from config instead of "Brightline RCT Analysis".

---

## 5. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Performance** | App loads and validates a 100K-row CSV in < 10 seconds on a standard laptop |
| **Compatibility** | Python 3.10+, all existing dependencies preserved (no new mandatory packages) |
| **Reproducibility** | Demo data generator produces identical output for the same config + random seed |
| **Portability** | Single `streamlit run` command; no Docker or cloud infrastructure required in v1 |
| **Error handling** | All user-facing errors must be plain-English messages in the UI, not stack traces |

---

## 6. Proposed Architecture Changes

### 6.1 New Files

```
config.yaml                        # Client config (new)
config_presets/
  cpg_price_promo.yaml             # Industry presets (new)
  ecommerce_discount.yaml
  pharma_awareness.yaml
  retail_loyalty.yaml
src/
  config_loader.py                 # Loads + validates config.yaml (new)
  schema_mapper.py                 # Applies column_map to any DataFrame (new)
```

### 6.2 Modified Files

| File | Change |
|------|--------|
| `streamlit_app_ust.py` | Read brand colors + client name from config; inject into header/sidebar |
| `app/module_pages/generate_data.py` | Replace DB connection mock with file upload + schema detection |
| `app/module_pages/results.py` | Replace hardcoded segment column names with config values |
| `app/module_pages/roi_insights.py` | Load default ROI params from config |
| `app/module_pages/export.py` | Use config client name in report headers |
| `src/data_generator_v4.py` | Refactor to accept a config dict; remove all Brightline-specific constants |
| `src/analysis_did.py` | Parameterize regression formula from config |
| `src/hte_analysis.py` | Loop over configured segment columns, not hardcoded lists |
| `src/purchase_dynamics.py` | Use mapped column name for `is_new_customer`; handle absence gracefully |
| `src/roi_calculator.py` | Load defaults from config |

### 6.3 Unchanged (Preserved As-Is)

- Core DiD math and statsmodels regression logic
- Quality validation scoring algorithm
- Multi-period ROI calculation formulas
- 7-step module navigation structure
- All visualization code (charts, Plotly figures)

---

## 7. Example: Deploying Against a New Dataset

The following illustrates the end-to-end workflow after this PRD is implemented.

**Scenario:** A retail pharmacy client ran a geo-based loyalty program RCT across 30 store regions for 6 months. They have weekly sales by region and customer transaction logs.

**Step 1 — Configure**
```yaml
# config.yaml
client:
  name: "PharmaCo"
  industry: "Retail Pharmacy"
  primary_color: "#C8102E"

experiment:
  geo_column: "store_region"
  treatment_column: "loyalty_treatment"
  outcome_column: "basket_value"
  date_column: "week_ending"
  pre_period_label: "baseline"
  test_period_label: "active"
  post_period_label: "followup"

segments:
  primary_segment: "store_format"    # flagship / express / drive-thru
  secondary_segment: "patient_segment"  # chronic / acute / OTC

column_map:
  geo_id: "store_region"
  sales_revenue: "basket_value"
  is_new_customer: "new_loyalty_member"
  is_treatment: "loyalty_treatment"

roi_defaults:
  profit_margin: 0.35
  avg_clv: 280
  retention_rate: 0.70
  discount_rate: 0.08
```

**Step 2 — Run**
```bash
streamlit run streamlit_app_ust.py
```

**Step 3 — Upload data in the UI**
- Upload `pharmaco_weekly_sales.csv` (sales module)
- Upload `pharmaco_transactions.csv` (optional, enables purchase dynamics)
- Skip media file (disabled gracefully)

**Step 4 — Proceed through all 7 modules**
Results, ROI, and export all reference "PharmaCo" and use the configured column names and segments. Zero code changes made.

---

## 8. Open Questions

| # | Question | Owner | Decision needed by |
|---|----------|-------|--------------------|
| 1 | Should the config support multi-outcome models (e.g., units + revenue simultaneously)? | Analytics lead | Before FR-7 implementation |
| 2 | Is YAML or JSON preferred for the config format? YAML is more human-editable; JSON has broader tooling support | Engineering | Week 1 |
| 3 | Should column_map support computed/derived columns (e.g., `is_post_period = date > '2024-10-01'`)? | Analytics lead | Before FR-2 implementation |
| 4 | What is the target new dataset for the first deployment of this generic framework? | Client / PM | ASAP — drives demo preset selection |
| 5 | Should the file upload support Excel (.xlsx) in addition to CSV? | Engineering | Week 1 |

---

## 9. Milestones

| Milestone | Deliverables | Dependencies |
|-----------|-------------|--------------|
| **M1: Config layer** | `config.yaml` schema, `config_loader.py`, `schema_mapper.py`, startup validation | None |
| **M2: File upload** | Replace DB mock with file upload UI, schema auto-detection | M1 |
| **M3: Analysis parameterization** | Config-driven DiD, HTE, purchase dynamics, ROI | M1 |
| **M4: Branding + graceful degradation** | Theming from config, optional dataset handling | M2 |
| **M5: Generic demo generator** | `generate_demo_data.py` reads config, industry presets | M1, M3 |
| **M6: End-to-end test** | Full run against a real non-Brightline dataset | M1–M5 |

---

## 10. Appendix: Current Data Schema (Reference)

### Sales Data (canonical column names after mapping)
| Column | Type | Description |
|--------|------|-------------|
| date | date | Week start date |
| geo_id | string | Market/region identifier |
| sales_revenue | float | Primary outcome variable |
| sales_units | int | Secondary outcome (optional) |
| is_treatment | bool | 1 = treatment group |
| is_pre_period | bool | 1 = pre-experiment weeks |
| is_test_period | bool | 1 = active experiment weeks |
| is_post_period | bool | 1 = post-experiment weeks |
| promo_type | string | Promotion type (optional) |
| retail_channel | string | Segment dimension (configurable name) |

### Transaction Data (canonical)
| Column | Type | Description |
|--------|------|-------------|
| customer_id | string | Unique customer identifier |
| geo_id | string | Market (links to sales data) |
| date | date | Transaction date |
| revenue | float | Transaction value |
| units | int | Units purchased |
| is_new_customer | bool | 1 = first purchase (optional) |
| age_segment | string | Demographic segment (optional, configurable) |
| is_treatment, period flags | bool | Same as sales data |
