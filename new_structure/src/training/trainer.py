"""
Hauptklasse fürs Model Training.
- Initialisiert Model mit Config
- Führt Training durch
- Validiert während Training
- Tracked Metrics
- Handled Early Stopping
"""


class ModelTrainer:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.metrics = []

    def train(self, train_data, val_data=None):
        pass

    def _validate(self, val_data):
        pass