# Load modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from sksurv.linear_model import CoxnetSurvivalAnalysis
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.exceptions import FitFailedWarning
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, KFold
import seaborn as sns


# TODO: Pipeline erweitern mit preprocessing
def do_lasso_gcv(cohort, X, y, n_splits = 5, random_state = 123, l1_ratio = 1.0, alpha_min_ratio = 0.5, max_iter = 1000, n_alphas = 50): 
    coxnet_pipe = make_pipeline(CoxnetSurvivalAnalysis(l1_ratio=l1_ratio, alpha_min_ratio=alpha_min_ratio, max_iter=max_iter, n_alphas = n_alphas))
    warnings.simplefilter("ignore", UserWarning)
    warnings.simplefilter("ignore", FitFailedWarning)
    coxnet_pipe.fit(X, y)
    
    estimated_alphas = coxnet_pipe.named_steps["coxnetsurvivalanalysis"].alphas_
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    gcv = GridSearchCV(
    make_pipeline(StandardScaler(), CoxnetSurvivalAnalysis(l1_ratio=1.0)),
    param_grid={"coxnetsurvivalanalysis__alphas": [[v] for v in estimated_alphas]},
    cv=cv,
    #error_score=0.5,
    n_jobs=-1,
    ).fit(X, y)
    
    best_model = gcv.best_estimator_.named_steps["coxnetsurvivalanalysis"]
    best_coefs = pd.DataFrame(best_model.coef_, index=X.columns, columns=["coefficient"])

    non_zero = np.sum(best_coefs.iloc[:, 0] != 0)
    non_zero_coefs = best_coefs.query("coefficient != 0")

    result = {
        'cohort' : cohort,
        'method' : "pen_cox", 
        'nmb_non_zero' : non_zero.item(), 
        'CI' : gcv.best_score_.item(), 
        'alpha_best_model' : best_model.alphas_[0].item(),
        'non_zero_genes' : non_zero_coefs.index.values.tolist(),      
        'non_zero_coeffs' : non_zero_coefs.coefficient.values.tolist(),
        'l1_ratio' : l1_ratio,
        'alpha_min_ratio' : alpha_min_ratio, 
        'max_iter' : max_iter, 
        'n_alphas' : n_alphas,
        'n_splits' : n_splits,
        'estimated_alphas' : estimated_alphas
    }
    
    
    return result  