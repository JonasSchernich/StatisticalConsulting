from .base_model import BaseSurvivalModel
import pandas as pd

class GBModel(BaseSurvivalModel): 
    def __init__(self, config = None):
        super().__init__(config)
    
    def get_feature_importance(self, X, model = None):
        if model is None: 
            feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_}).sort_values('importance', ascending=False)
        else: 
            feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_}).sort_values('importance', ascending=False)
        return feature_importance
    
    
    
    
    