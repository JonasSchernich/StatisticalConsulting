"""
Validation Strategien und Metriken.
Primär fürs Training.

- Simple train/val split
- K-fold CV
- Leave one cohort out CV

Integration mit mlflow für tracking?
Plotting der validation curves etc.
"""


class ModelValidator:
    def __init__(self, strategy='kfold', **kwargs):
        self.strategy = strategy
        self.kwargs = kwargs

    def validate(self, model, X, y):
        pass

    def plot_validation_curves(self):
        pass