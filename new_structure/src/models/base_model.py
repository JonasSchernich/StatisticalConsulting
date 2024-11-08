"""
Abstrakte Basisklasse für alle Survival Models.
Jedes Model (RSF, Cox etc) muss diese Methoden implementieren.

Key methods:
- fit: Trainiert das Model
- predict: Vorhersage der Survival/Risk Scores
- predict_survival_function: Vorhersage der Überlebensfunktion (falls möglich)
- save/load: Zum Speichern der trainierten Modelle

Optional:
- get_feature_importance: Falls das Model Feature Importance liefern kann
- callback Methoden für Training Monitoring

Idee ist dass die models austauschbar sind weil sie das gleiche Interface haben.
"""

from abc import abstractmethod
from sklearn.pipeline import Pipeline
import numpy as np
from sklearn.model_selection import LeaveOneGroupOut, GridSearchCV
from sklearn.metrics import make_scorer
from new_structure.src.utils.utils import cindex_score, get_cohort
import pandas as pd 
import pickle
import os


class BaseSurvivalModel():
    def __init__(self, config = None):
       self.config = config
       self.is_fitted = False
       self.model = None
       self.pipe_best_mod = None
       
    # Pipeline with feature selection, feature scaling and modelling
    def fit_model(self, X, y, fname, path, pipeline_steps, params_cv= None, params_feat_sel = None, refit = False, save_model = False):  
        cohorts = get_cohort(X)
        pipe = Pipeline(pipeline_steps)     
        if params_cv is not None: 
            group_kfold = LeaveOneGroupOut()
            gcv = GridSearchCV(estimator=pipe, 
                                      param_grid=params_cv,
                                      cv=group_kfold,
                                      scoring=make_scorer(cindex_score, greater_is_better=True),
                                      n_jobs=-1, 
                                      verbose=2, 
                                      refit=refit
                                      ).fit(X, y, groups = cohorts)
            
            self.save_csv_gcv(gcv, path, fname)
            
            if refit: 
               best_model = gcv.best_estimator_
               self.pipe_best_mod = best_model
               self.is_fitted = True
               # do sth else? --> nested HP tuning via predict would be possible here
            if save_model: 
               self.save_model(path, fname)
        else: 
           pipe.fit(X,y)

    # je nach modell andere methoden evtl. nötig
    def predict_model(self, X, y, model = None):
        if model is None: 
            predictions = self.model.predict(X)
        else: 
            predictions = model.predict(X)
        return predictions
   
    def save_model(self, path, fname): 
        print('Saving the best model')
        fname = fname + '.pkl'
        model = self.pipe_best_mod.named_steps['model']
        self.model = model
        print(type(model))
        model_pkl_file = os.path.join(path, fname)
        with open(model_pkl_file, 'wb') as file:  
            pickle.dump(model, file)
   
    def load_model(self, path, fname): 
        fname = fname + '.pkl'
        model_pkl_file = os.path.join(path, fname)
        with open(model_pkl_file, 'rb') as file:  
            model = pickle.load(file)
            self.model = model
            self.is_fitted = True
        return model 

    # muss pro modell gemacht werden
    def get_feature_importance(self):
        raise NotImplementedError("Feature importance not available for this model")
   
    def save_csv_gcv(self, gcv, path, fname):
        fname = fname + '.csv'
        csv_path = os.path.join(path, fname)
        cv_results = pd.DataFrame(gcv.cv_results_)
        cv_results.to_csv(csv_path)
       
    def load_csv_gcv(self, path, fname):
        fname = fname + '.csv'
        csv_path = os.path.join(path, fname)
        cv_results = pd.read_csv(csv_path)
        return cv_results