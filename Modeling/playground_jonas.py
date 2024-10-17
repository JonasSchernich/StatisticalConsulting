import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sksurv.svm import FastSurvivalSVM
from sksurv.metrics import concordance_index_censored

# Laden der Daten
completed_pData = pd.read_csv("completed_pData.csv", index_col=0)
merged_exprs_t = pd.read_csv("merged_exprs_t.csv", index_col=0)

# Entfernen von Zeilen mit 0 Zeit bis zum Ereignis
mask = completed_pData['MONTH_TO_BCR'] > 0
completed_pData_no_0_times = completed_pData[mask]
subset_exprs = merged_exprs_t.loc[completed_pData_no_0_times.index]

# Erstellen des Survival-Objekts
y = np.array([(status, time) for status, time in
              zip(completed_pData_no_0_times['BCR_STATUS'],
                  completed_pData_no_0_times['MONTH_TO_BCR'])],
             dtype=[('status', bool), ('time', float)])

# Standardisierung der Features
scaler = StandardScaler()
X = scaler.fit_transform(subset_exprs)

# Aufteilen in Trainings- und Testdaten
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Trainieren der Survival SVM
ssvm = FastSurvivalSVM(max_iter=1000, tol=1e-5, random_state=42)
ssvm.fit(X_train, y_train)

# Berechnen des Konkordanz-Index auf den Testdaten
c_index = ssvm.score(X_test, y_test)
print(f"Konkordanz-Index auf Testdaten: {c_index:.4f}")

# Feature-Wichtigkeit basierend auf den absoluten Gewichten
feature_importance = pd.Series(np.abs(ssvm.coef_), index=subset_exprs.columns)
top_features = feature_importance.nlargest(20)  # Top 20 Features

print("Top 20 wichtigste Features:")
print(top_features)

