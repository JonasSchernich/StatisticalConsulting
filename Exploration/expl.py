import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# load preprocessed data
with open('../Data/preprocessed_data.pkl', 'rb') as f:
    preprocessed_data = pickle.load(f)

with open('../Data/cohort_stats_df.pkl', 'rb') as f:
    cohort_stats_df = pickle.load(f)

df = preprocessed_data['merged_pData']
duplicates_pData = preprocessed_data['merged_pData'].columns[preprocessed_data['merged_pData'].columns.duplicated()]
duplicates_exprs = preprocessed_data['merged_pData'].index[preprocessed_data['merged_pData'].index.duplicated()]

# Extrahieren der relevanten PSA-Statistiken
psa_stats = cohort_stats_df[['cohort_name', 'psa_min', 'psa_q25', 'psa_median', 'psa_q75', 'psa_max']]

# Erstellen des Box Plots
plt.figure(figsize=(12, 6))

# Zeichnen der Box Plots
for i, row in psa_stats.iterrows():
    cohort = row['cohort_name']
    plt.boxplot([row['psa_q25'], row['psa_median'], row['psa_q75']],
                positions=[i],
                widths=0.6,
                medianprops=dict(color="red"),
                boxprops=dict(color="blue"),
                whiskerprops=dict(color="black"),
                capprops=dict(color="black"))

    # Hinzufügen der Whisker für Min und Max
    plt.vlines(i, row['psa_min'], row['psa_max'], color='black', linestyle='-', lw=1)

# Anpassen der x-Achse
plt.xticks(range(len(psa_stats)), psa_stats['cohort_name'], rotation=45, ha='right')

plt.title('Verteilung der PRE_OPERATIVE_PSA-Werte nach Kohorte')
plt.ylabel('PRE_OPERATIVE_PSA')
plt.tight_layout()
#plt.show()

# Optional: Logarithmische Skala für bessere Darstellung bei großen Unterschieden
plt.figure(figsize=(12, 6))

for i, row in psa_stats.iterrows():
    cohort = row['cohort_name']
    plt.boxplot([row['psa_q25'], row['psa_median'], row['psa_q75']],
                positions=[i],
                widths=0.6,
                medianprops=dict(color="red"),
                boxprops=dict(color="blue"),
                whiskerprops=dict(color="black"),
                capprops=dict(color="black"))

    plt.vlines(i, row['psa_min'], row['psa_max'], color='black', linestyle='-', lw=1)

plt.yscale('log')
plt.xticks(range(len(psa_stats)), psa_stats['cohort_name'], rotation=45, ha='right')
plt.title('Verteilung der PRE_OPERATIVE_PSA-Werte nach Kohorte (Log-Skala)')
plt.ylabel('PRE_OPERATIVE_PSA (Log-Skala)')
plt.tight_layout()
#plt.show()

# Ausgabe der PSA-Statistiken als Tabelle
print(psa_stats.to_string(index=False))












dod_rows = preprocessed_data['merged_pData'][preprocessed_data['merged_pData']['DOD_STATUS'].notna()]
print(dod_rows['DOD_STATUS'].sum())

# Deskriptive Statistik für numerische Variablen
desc_stats = preprocessed_data['merged_pData'].describe()
age_type=preprocessed_data['merged_exprs']['PT184'].dtype
print(desc_stats)



relevant_columns = preprocessed_data['merged_pData'][['AGE', 'TISSUE', 'PATH_T_STAGE', 'GLEASON_SCORE', 'GLEASON_SCORE_1', 'GLEASON_SCORE_2', 'CEP_STATUS', 'MONTH_TO_CEP', 'PRE_OPERATIVE_PSA', 'MONTH_TO_BCR', 'CLIN_T_STAGE', 'BCR_STATUS']]

mismatch_mask = relevant_columns['CEP_STATUS'] != relevant_columns['BCR_STATUS']

# Extrahiere die Indizes der Zeilen, in denen die Werte unterschiedlich sind
mismatch_indices = relevant_columns[mismatch_mask].index.tolist()

# Wenn keine Unterschiede vorhanden sind, gib True zurück, andernfalls die Liste der Zeilen
if len(mismatch_indices) == 0:
    result = True
else:
    result = mismatch_indices

# Ausgabe des Ergebnisses
print(result)
print(test)

#%%
print('T')















