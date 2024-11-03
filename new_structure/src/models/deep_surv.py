"""

Architektur:
- Fully connected layers
- Batch norm nach jedem layer
- Dropout
- ReLU activation
- Custom loss function für survival data


TODO: GPU support einbauen
"""

from .base_model import BaseSurvivalModel
import torch.nn as nn


class DeepSurvModel(BaseSurvivalModel):
    def __init__(self, config):
        super().__init__(config)
        self.network = None
        self.optimizer = None

    def _build_network(self):
        pass

    def fit(self, X, y):
        pass