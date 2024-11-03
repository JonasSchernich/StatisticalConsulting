"""
Verschiedene Strategien zum Splitten der Daten in Train/Val/Test.

Implementiert:
- Random split mit stratification nach events
- Cohort basiertes splitting


Was mir noch eingefallen ist beim Splitting: Müssen wir stratifizieren?
"""


class DataSplitter:
    def __init__(self, strategy='random'):
        self.strategy = strategy

    def split(self, X, y):
        if self.strategy == 'random':
            return self._random_split(X, y)
        elif self.strategy == 'cohort':
            return self._cohort_split(X, y)