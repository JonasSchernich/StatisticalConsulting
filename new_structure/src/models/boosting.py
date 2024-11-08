from .base_model import BaseSurvivalModel
from sksurv.ensemble import GradientBoostingSurvivalAnalysis
from sklearn.model_selection import GroupKFold
from dim_reduction.feature_selection import do_feat_sel

class GBModel(BaseSurvivalModel): 
    def __init__(self, config):
        super().__init__(config)
        self.model = GradientBoostingSurvivalAnalysis()
                
        
    def fit(self, X, y, do_res = False, do_nes_res = False, do_feat_sel = False, feat_sel_config = None, 
            save_model = False, saving_path = None): 
        if do_feat_sel: 
            ### get selected X from do_feat_sel_config uing do_feat_sel from other packages
            X = do_feat_sel()
        else: 
            if do_res: 
                pass 
            elif do_nes_res: 
                pass
            else: 
                self.model.fit(X, y)
                return self.model
            
    
    
    def do_res(self, n_folds, group = "cohort"):
        pass 
    
    def do_nes_res(self, n_folds_outer, n_folds_inner, group = "cohort"):
        pass
    
    
    