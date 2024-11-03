"""

Features:
- Standard RSF training
- Out-of-bag error estimation
- Feature importance

Die Config muss alle wichtigen Parameter wie n_estimators,
max_depth etc. enhalten. Defaults sind in der model config definiert.

"""

from .base_model import BaseSurvivalModel
from sksurv.ensemble import RandomSurvivalForest


class RandomSurvivalForestModel(BaseSurvivalModel):
    def __init__(self, config):
        super().__init__(config)
        self.model = None

    def fit(self, X, y):
        pass

    def predict(self, X):
        pass