# Duka Sales Exploration & Agent Network Clean-Up

An end-to-end data analysis, data quality audit, and data engineering project for retail sales exploration and financial agent network data sanitization in Kenya.

---

## Table of Contents
- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Project Architecture & Components](#project-architecture--components)
  - [1. Deterministic Data Generation (`generate_data.py`)](#1-deterministic-data-generation-generate_datapy)
  - [2. Duka Sales Exploration (`duka_sales_exploration.ipynb`)](#2-duka-sales-exploration-duka_sales_explorationipynb)
  - [3. Mobile Money Agent Network Clean-Up (`agent_cleanup.ipynb`)](#3-mobile-money-agent-network-clean-up-agent_cleanupipynb)
  - [4. Production Cleaning Pipeline (`cleaning_pipeline.py`)](#4-production-cleaning-pipeline-cleaning_pipelinepy)
  - [5. Excel Summary Workbook (`excel/duka_branch_summary.xlsx`)](#5-excel-summary-workbook-excelduka_branch_summaryxlsx)
  - [6. Curated Outputs (`outputs/`)](#6-curated-outputs-outputs)
- [Installation & Setup](#installation--setup)
- [Execution Guide](#execution-guide)
- [Key Analytical Findings](#key-analytical-findings)
  - [Duka Electronics Sales Analysis](#duka-electronics-sales-analysis)
  - [Agent Network Data Quality Audit](#agent-network-data-quality-audit)
- [Regulatory Compliance (KDPA 2019)](#regulatory-compliance-kdpa-2019)
- [Technologies Used](#technologies-used)
- [Author & Source Control](#author--source-control)

---

## Overview

This repository addresses two enterprise data challenges:
1. **Duka Electronics Retail Analysis**: Evaluates sales performance across four regional branches (Nairobi, Mombasa, Kisumu, Nakuru), analyzes product category revenues and order volumes, investigates weekday vs. weekend transaction behavior, filters high-value customer cohorts, and reconciles analytical findings against an executive multi-sheet Excel model.
2. **Mobile Money Agent Network Audit & Clean-Up**: Performs a systematic 6-dimension data quality audit (Uniqueness, Consistency, Validity, Completeness, Outliers, Referential Integrity) on raw mobile money transaction logs and agent registries. It packages cleaning treatments into an automated, reusable production function `clean_agent_data(txns, agents)` and documents compliance with the Kenya Data Protection Act 2019.

---

## Repository Structure

```text
plp-da-a3-duka-sales-and-agent-cleanup/
├── README.md
├── generate_data.py
├── duka_sales_exploration.ipynb
├── agent_cleanup.ipynb
├── cleaning_pipeline.py
├── requirements.txt
├── excel/
│   └── duka_branch_summary.xlsx
└── outputs/
    ├── premium_online_coast_capital.csv
    ├── agent_transactions_clean.csv
    └── agent_weekly_pivot.csv
```

---

## Project Architecture & Components

### 1. Deterministic Data Generation (`generate_data.py`)
Generates reproducible synthetic datasets utilizing fixed NumPy random number generators:
- **Seed 44**: Produces `agents.csv` (20 registered agents across 5 Kenyan counties) and `agent_transactions.csv` (600 baseline transactions + 12 duplicates + injected missing values, string anomalies, slash-delimited dates, extreme amounts, and unmapped agent IDs).
- **Seed 2026**: Produces `duka_sales.csv` (1,000 multi-branch electronic sales records spanning Nairobi, Mombasa, Kisumu, and Nakuru).

### 2. Duka Sales Exploration (`duka_sales_exploration.ipynb`)
Structured exploratory data analysis executing:
- **Inspection & Ingestion**: Validates shapes, missing values, and date ranges.
- **Feature Engineering**: Calculates `revenue` (`quantity * unit_price_kes`), `month`, `weekday`, `is_weekend`, and `price_band` (`Premium` for items $\ge$ KES 28,000, `Value` otherwise).
- **Branch Ranking**: Ranks branches by total revenue and order volume.
- **Product Distribution**: Analyzes high-ticket revenue drivers (Laptops, Smart TVs) vs. high-velocity volume drivers (Smartphones).
- **Temporal Dynamics**: Evaluates weekend vs. weekday sales volumes and identifies seasonal revenue peaks.
- **Cohort Filtering**: Filters high-value transactions (`Premium` products ordered `Online` from `Nairobi` or `Mombasa`) and exports to `outputs/premium_online_coast_capital.csv`.
- **Excel Reconciliation**: Verifies that the Pandas total revenue (KES 32,759,500) reconciles exactly with `excel/duka_branch_summary.xlsx`.
- **Artifact Generation**: Creates the branch-summary Excel workbook and premium online cohort CSV when the notebook is run.

### 3. Mobile Money Agent Network Clean-Up (`agent_cleanup.ipynb`)
Comprehensive data cleansing workflow that:
- Conducts a baseline Data-Quality Audit evaluating Uniqueness, Consistency, Validity, Completeness, Outlier contamination, and Referential Integrity.
- Imports and executes `cleaning_pipeline.clean_agent_data()`.
- Generates county-level performance summaries by transaction type (`Deposit` vs. `Withdrawal`).
- Constructs weekly pivot tables tracking transaction values across counties.
- Displays and saves the pivot to `outputs/agent_weekly_pivot.csv`.
- Produces a final data-quality report and a privacy statement describing the synthetic data and safeguards required for real personal data.
- Evaluates operational data governance against the Kenya Data Protection Act 2019.

### 4. Production Cleaning Pipeline (`cleaning_pipeline.py`)
A modular, production-ready function `clean_agent_data(txns, agents)` that returns `(clean_df, log_dict)`:
- **Uniqueness**: Deduplicates records on `txn_id`, retaining the first occurrence in source order (12 duplicate rows removed).
- **Consistency**: Strips whitespace and standardizes casing on `txn_type` to Title Case (`Deposit`, `Withdrawal`); 376 deduplicated rows required normalization.
- **Validity (Format)**: Harmonizes slash-delimited dates into ISO-standard datetimes (`YYYY-MM-DD`); 5 deduplicated rows required normalization.
- **Completeness**: Converts textual `'N/A'` and empty values to numeric `NaN`, flags imputed records (`amount_imputed`), and imputes missing transaction amounts using the sample median (20 values imputed).
- **Outliers**: Calculates Interquartile Range (IQR) fences ($Q_1 - 1.5 \times \text{IQR}$ to $Q_3 + 1.5 \times \text{IQR}$), flags values outside them (`is_outlier = True`), and retains transaction history (53 outliers detected).
- **Referential Integrity**: Left-merges transactions with the agent registry on `agent_id` and assigns `county = 'Unknown'` for unmatched IDs like `AG099` (7 rows remain after deduplication; 8 unmatched rows occur in the raw extract).

### 5. Excel Summary Workbook (`excel/duka_branch_summary.xlsx`)
Multi-worksheet executive workbook generated by the Duka notebook, containing:
- `duka_sales`: Transactional data with engineered price bands and revenue calculations.
- `Branch_Summary`: Branch-level revenue, region, and channel totals, matching the KES 32,759,500 grand total.
- `Region_Summary`: Revenue and order totals by region and sales channel.

### 6. Curated Outputs (`outputs/`)
- `premium_online_coast_capital.csv`: 119 targeted orders representing KES 7,905,000 in high-value e-commerce revenue from Nairobi and Mombasa.
- `agent_transactions_clean.csv`: Cleaned dataset with 600 verified transactions enriched with agent metadata, data-quality flags (`amount_imputed`, `is_outlier`), and county assignments.
- `agent_weekly_pivot.csv`: Weekly transaction-value pivot by county, generated and displayed by the agent cleanup notebook.

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sr7Rama/plp-da-a3-duka-sales-and-agent-cleanup.git
   cd plp-da-a3-duka-sales-and-agent-cleanup
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install project dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   python -m ipykernel install --user --name duka-cleanup --display-name "Python (Duka Cleanup)"
   ```

---

## Execution Guide

### 1. Generate Synthetic Datasets
Run the data generator to initialize `duka_sales.csv`, `agents.csv`, and `agent_transactions.csv`:
```bash
python generate_data.py
```

### 2. Execute Cleaning Pipeline Programmatically
```python
import pandas as pd
from cleaning_pipeline import clean_agent_data

txns = pd.read_csv("agent_transactions.csv")
agents = pd.read_csv("agents.csv")

clean_df, log = clean_agent_data(txns, agents)
print("Pipeline Completion Log:", log)
```

### 3. Run Jupyter Notebooks
Open either notebook in VS Code and select the `Python (Duka Cleanup)` kernel, or launch Jupyter with the same environment. Both notebooks use the active kernel's Python executable when generating data:
```bash
jupyter notebook duka_sales_exploration.ipynb
jupyter notebook agent_cleanup.ipynb
```

---

## Key Analytical Findings

### Duka Electronics Sales Analysis
- **Top Branch**: **Nairobi** generated the highest total revenue (**KES 12,335,500**) and highest order volume (**376 orders**), followed by Mombasa, Kisumu, and Nakuru.
- **Product Highlights**: **Smartphones** led product revenue (**KES 11,046,500**) and units sold (**464**), followed by **Laptops** and **Wireless Headphones** in revenue.
- **Channel Segmentation**: Online sales in coastal (Mombasa) and capital (Nairobi) hubs generated **KES 7,905,000** across **119 transactions**, highlighting a strong e-commerce customer base.
- **Total Revenue**: KES 32,759,500 across 1,000 orders, reconciles 100% with the Excel executive summary.

### Agent Network Data Quality Audit
| Dimension | Audit Finding | Cleaning Treatment | Count |
|---|---|---|---|
| **Uniqueness** | Duplicate transaction IDs | Dropped duplicated rows, kept first occurrence | 12 rows removed |
| **Consistency** | Inconsistent casing or whitespace in `txn_type` | `.str.strip().str.capitalize()` | 376 rows standardized after deduplication |
| **Validity** | Five slash-delimited dates | Normalized to ISO format `YYYY-MM-DD` | 5 dates normalized after deduplication |
| **Completeness** | Missing/non-numeric amount (`NaN`, `'N/A'`) | Imputed missing values with median amount | 20 values imputed |
| **Outliers** | Extreme transaction amounts | Flagged via IQR without discarding records | 53 outliers flagged |
| **Referential Integrity** | 8 raw rows contain unregistered `AG099`; one loses to first-row transaction-ID deduplication | Left joined with registry; 7 retained rows mapped to `'Unknown'` | 7 rows after deduplication |

---

## Regulatory Compliance (KDPA 2019)

In compliance with the **Kenya Data Protection Act (KDPA) 2019**:
1. **Data Minimisation & Purpose Limitation (Section 25)**: Only transaction identifiers, amounts, dates, and non-sensitive geographical county metadata are stored. Personally Identifiable Information (PII) such as customer names and phone numbers is omitted.
2. **Data Accuracy (Section 25(d))**: Imputed and outlier records are explicitly tagged (`amount_imputed`, `is_outlier`) to maintain transparency in audit trails and prevent distortion of customer financial standing.
3. **Storage Limitation & Safeguards (Section 41)**: Unregistered agent activities (`AG099`) are segregated and routed to review queues (`county = 'Unknown'`) rather than dropped, maintaining forensic auditability.

---

## Technologies Used
- **Language**: Python 3.10+
- **Data Manipulation**: `pandas`, `numpy`
- **Spreadsheet Automation**: `openpyxl`
- **Version Control**: Git & GitHub

---

## Author & Source Control
- **Repository**: [https://github.com/Sr7Rama/plp-da-a3-duka-sales-and-agent-cleanup](https://github.com/Sr7Rama/plp-da-a3-duka-sales-and-agent-cleanup)
- **Maintainer**: Sr7Rama (rmswaleh1@gmail.com)
