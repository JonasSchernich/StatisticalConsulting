import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# load preprocessed data
with open('../Data/preprocessed_data.pkl', 'rb') as f:
    preprocessed_data = pickle.load(f)
df = preprocessed_data['merged_pData']
duplicates_pData = preprocessed_data['merged_pData'].columns[preprocessed_data['merged_pData'].columns.duplicated()]
duplicates_exprs = preprocessed_data['merged_pData'].index[preprocessed_data['merged_pData'].index.duplicated()]

dod_rows = preprocessed_data['merged_pData'][preprocessed_data['merged_pData']['DOD_STATUS'].notna()]
print(dod_rows['DOD_STATUS'].sum())

# Deskriptive Statistik für numerische Variablen
desc_stats = preprocessed_data['merged_pData'].describe()
print(desc_stats)



from lifelines import KaplanMeierFitter

# genutze variablen ignorieren, wollte nur mal versuchen eine KM in python zu plotten
kmf = KaplanMeierFitter()
T = preprocessed_data['merged_pData']['MONTH_TO_CEP']
E = preprocessed_data['merged_pData']['CEP_STATUS']

kmf.fit(T, E)
kmf.plot()
plt.title('Kaplan-Meier Überlebenskurve')
plt.show()


