"""
Klasse für alle Performance Metriken.

Survival spezifisch:
- C-index

Generell:
- R2 für die predictions vielleicht?


Idee: Wrappen die ganzen metrics in einer Klasse die man einfach auf
predictions anwenden kann und dann alle metriken auf einmal bekommt.
"""

from lifelines.utils import concordance_index
import numpy as np
from typing import Dict, Optional


class SurvivalMetrics:
    def __init__(self):
        """
        Initialisiert die Metrik-Klasse.
        """
        pass

    def calculate_all_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """
        Calc all implemented metrics

        """
        metrics = {
            'c_index': self.c_index(y_true, y_pred),
            'brier_score': self.brier_score(y_true, y_pred)
        }

        return metrics

    def c_index(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calc C-index using lifelines.

        """
        event_times = y_true['time']
        event_status = y_true['status']

        try:
            c_index = concordance_index(event_times, -y_pred, event_status)
            return c_index

        except Exception as e:
            print(f"Error calculating c-index: {str(e)}")
            return float('nan')

    def brier_score(self, y_true: np.ndarray, y_pred: np.ndarray,
                    times: Optional[np.ndarray] = None) -> float:
        """

        """

        try:
            # TODO: Implementiere Brier Score
            return 0.0

        except Exception as e:
            print(f"Error calculating brier score: {str(e)}")
            return float('nan')