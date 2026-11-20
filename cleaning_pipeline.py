import pandas as pd
import numpy as np

def clean_agent_data(txns, agents):
    """
    Cleans agent transaction data and merges with the agent register.

    Parameters:
        txns (DataFrame): Raw transaction DataFrame.
        agents (DataFrame): Raw agent registry DataFrame.

    Returns:
        tuple: (clean_df, log_dict)
    """
    log = {}
    txns_clean = txns.copy()

    # 1. Uniqueness - Drop duplicate txn_ids
    initial_count = len(txns_clean)
    txns_clean = txns_clean.drop_duplicates(subset=['txn_id'], keep='first')
    log['duplicates_removed'] = initial_count - len(txns_clean)

    # 2. Consistency - Standardise txn_type
    txns_clean['txn_type'] = txns_clean['txn_type'].astype(str).str.strip().str.capitalize()

    # 3. Validity - Standardise txn_date formatting to YYYY-MM-DD
    txns_clean['txn_date'] = pd.to_datetime(txns_clean['txn_date'].astype(str).str.replace('/', '-'), errors='coerce')

    # 4. Completeness - amount conversion, numeric extraction & median imputation
    txns_clean['amount'] = txns_clean['amount'].replace('N/A', np.nan)
    txns_clean['amount'] = pd.to_numeric(txns_clean['amount'], errors='coerce')

    txns_clean['amount_imputed'] = txns_clean['amount'].isna()
    median_val = txns_clean['amount'].median()
    txns_clean['amount'] = txns_clean['amount'].fillna(median_val)
    log['imputed_values_count'] = int(txns_clean['amount_imputed'].sum())

    # 5. Outliers - IQR validation
    q1 = txns_clean['amount'].quantile(0.25)
    q3 = txns_clean['amount'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    txns_clean['is_outlier'] = (txns_clean['amount'] < lower_bound) | (txns_clean['amount'] > upper_bound)
    log['outliers_detected'] = int(txns_clean['is_outlier'].sum())

    # 6. Referential Integrity - Merge with agent register
    merged_df = pd.merge(txns_clean, agents, on='agent_id', how='left')
    unknown_agents_mask = merged_df['county'].isna()
    log['unknown_agents_count'] = int(unknown_agents_mask.sum())
    merged_df.loc[unknown_agents_mask, 'county'] = 'Unknown'

    return merged_df, log
