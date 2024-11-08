# Load modules
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from new_structure.src.models.base_model import BaseSurvivalModel
from abc import abstractmethod
from sklearn.pipeline import Pipeline
import numpy as np
from sklearn.model_selection import LeaveOneGroupOut, GridSearchCV
from sklearn.metrics import make_scorer
from new_structure.src.utils.utils import cindex_score, get_cohort
import pandas as pd 
import pickle
import os

class PenCoxModel(BaseSurvivalModel): 
    def __init__(self, config=None):
        super().__init__(config)
    
    def fit_model(self, X, y, fname, path, pipeline_steps, params_cv= None, params_feat_sel = None, refit = False, save_model = False):
        cohorts = get_cohort(X)
        pipe = Pipeline(pipeline_steps)     

        if params_cv is not None: 
            temp_pipe = Pipeline(pipeline_steps).fit(X, y)
            estimated_alphas = temp_pipe.named_steps['model'].alphas_
            params_cv ={"coxnetsurvivalanalysis__alphas": [[v] for v in estimated_alphas]}
            group_kfold = LeaveOneGroupOut()
            gcv = GridSearchCV(estimator=pipe, 
                                      param_grid=params_cv,
                                      cv=group_kfold,
                                      scoring=make_scorer(cindex_score, greater_is_better=True),
                                      n_jobs=-1, 
                                      verbose=2, 
                                      refit=refit
                                      ).fit(X, y, groups = cohorts)
            
            self.save_csv_gcv(gcv, path, fname, X)
            
            if refit: 
               best_model = gcv.best_estimator_
               self.model = best_model
               self.is_fitted = True
               # do sth else? --> nested HP tuning via predict would be possible here
            if save_model: 
               self.save_model(path, fname)
        else: 
           pipe.fit(X,y)

    
    def save_csv_gcv(self, gcv, path, fname, X):
        best_model = gcv.best_estimator_.named_steps['model']
        best_coefs = pd.DataFrame(best_model.coef_, index=X.columns, columns=["coefficient"])
    
        non_zero = np.sum(best_coefs.iloc[:, 0] != 0)
        non_zero_coefs = best_coefs.query("coefficient != 0")
        
        result = {
        'method' : "pen_cox", 
        'nmb_non_zero' : non_zero.item(), 
        'CI' : gcv.best_score_.item(), 
        'alpha_best_model' : best_model.alphas_[0].item(),
        'non_zero_genes' : non_zero_coefs.index.values.tolist(),      
        'non_zero_coeffs' : non_zero_coefs.coefficient.values.tolist()}
        fname = fname + '.csv'
        csv_path = os.path.join(path, fname)
        cv_results = pd.DataFrame([result])
        cv_results.to_csv(csv_path)    
    