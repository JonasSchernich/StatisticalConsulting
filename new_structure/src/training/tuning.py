"""
Hyperparameter Tuning für alle Models.
Unterstützt verschiedene Strategien:

- Random Search (default)
- Grid Search
- ggf. noch irgendwas mit Bayesian Optimization?

Config definiert:
- Welche Parameter getunt werden
- Ranges/Werte für Parameter
- Anzahl Iterationen
- CV Strategie

"""


class ModelTuner:
    def __init__(self, model_class, config):
        self.model_class = model_class
        self.config = config

    def tune(self, X, y):
        pass

    def _evaluate_params(self, params, X, y):
        pass