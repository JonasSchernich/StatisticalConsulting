"""
Abstrakte Basisklasse für Dimensionsreduktion.
Jede Dimensionsreduktionsmethode (PCA, Feature Selection etc)
erbt von dieser Klasse.

Die Klasse definiert die grundlegenden Methoden die jeder Reducer haben muss:
- fit: Lernt die Transformation
- transform: Wendet die Transformation an
- fit_transform: Convenience Methode für beides
- save/load: Damit man den gelernten Reducer speichern kann

Ist bisschen an sklearn angelehnt, aber mit ein paar extras die wir brauchen.
"""

from abc import ABC, abstractmethod


class BaseReducer(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.is_fitted = False

    @abstractmethod
    def fit(self, X):
        pass

    @abstractmethod
    def transform(self, X):
        pass

    @abstractmethod
    def fit_transform(self, X):
        pass

    @abstractmethod
    def save(self, path):
        pass

    @abstractmethod
    def load(self, path):
        pass