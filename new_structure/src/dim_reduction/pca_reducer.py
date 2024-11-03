"""
PCA Implementation, erbt von BaseReducer.
Nutzt sklearn PCA im Hintergrund, aber mit ein paar extras:

- Speichert die feature names/indizes damit man später
  noch weiß welche original features wichtig waren
- soll variance explained ausgeben können
- Plot methoden für scree plot etc
- Automatische Bestimmung der components basierend auf
  cumulative variance wenn gewünscht


"""

from .base_reducer import BaseReducer
from sklearn.decomposition import PCA #Oder ggf eine andere library


class PCAReducer(BaseReducer):
    def __init__(self, config):
        super().__init__(config)
        self.pca = None
        self.feature_names = None

    def fit(self, X):
        pass

    def get_explained_variance(self):
        pass

    def plot_scree(self):
        pass