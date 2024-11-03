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

from abc import ABC, abstractmethod

class BaseSurvivalModel(ABC):
   def __init__(self, config):
       self.config = config
       self.is_fitted = False

   @abstractmethod
   def fit(self, X, y):
       pass

   @abstractmethod
   def predict(self, X):
       pass

   def get_feature_importance(self):
       raise NotImplementedError("Feature importance not available for this model")