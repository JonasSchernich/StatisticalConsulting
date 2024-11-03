import pandas as pd
merged_pdata_original['merged_original_pData.csv']['AGE'] = pd.to_numeric(
    merged_pdata_original['merged_original_pData.csv']['AGE'], errors='coerce'
)
quantile_10 = merged_pdata_original['merged_original_pData.csv']['AGE'].quantile(0.10)
quantile_90 = merged_pdata_original['merged_original_pData.csv']['AGE'].quantile(0.90)
mean_age = merged_pdata_original['merged_original_pData.csv']['AGE'].mean()