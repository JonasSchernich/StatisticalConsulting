"""
Klasse für alle Performance Metriken.

Survival spezifisch:
- C-index

Generell:
- R2 für die predictions vielleicht?


Idee: Wrappen die ganzen metrics in einer Klasse die man einfach auf
predictions anwenden kann und dann alle metriken auf einmal bekommt.
"""


class SurvivalMetrics:
    def __init__(self):
        pass

    def calculate_all_metrics(self, y_true, y_pred):
        pass

    def c_index(self, y_true, y_pred):
        pass

    def brier_score(self, y_true, y_pred):
        pass

    def calibration_plot(self, y_true, y_pred):
        pass