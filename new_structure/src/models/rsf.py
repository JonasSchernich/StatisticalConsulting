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
import pandas as pd
from sklearn.inspection import permutation_importance


class RSFModel(BaseSurvivalModel):
    def __init__(self, config):
        super().__init__(config)

    def fit(self, X, y, fname, path, pipeline_steps, params_cv= None, params_feat_sel = None, refit = False, save_model = False):
        super().fit_model(self, X, y, fname, path, pipeline_steps, params_cv= None, params_feat_sel = None, refit = False, save_model = False)
        
    def predict(self, X, what = None):
        if what is None: 
            super().predict_model(X)
        else: 
            # evtl andere predict functionen rein z.B. mean surivival times
            # vgl : https://scikit-survival.readthedocs.io/en/stable/user_guide/random-survival-forest.html
            pass
           
    def get_feature_importance(self, X, y, model, feat_imp_type, path):
        result = permutation_importance(model, X, y, n_repeats=15, random_state=123)
        
        df_result = pd.DataFrame(
            {k: result[k] for k in (
            "importances_mean",
            "importances_std")}, index=X.columns).sort_values(by="importances_mean", ascending=False)
        
        return df_result