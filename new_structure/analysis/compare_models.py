"""
Die Klasse soll alle model performances aus den results ordnern einlesen,
die Metriken der unterschiedlichen modelle und modell+dimensionsreduktion kombis
dann vergleichen und visualisieren. Soll dafür in den results unterordnern jeweils
nach metrics.json suchen.

Plots:
- Box Plots der C indices
- Korrelation der predictions der verschiedenen modelle (vllt paarweise)
- Feature importance falls das modell das ausgibt

Wäre gut wenn man per parameter auswählen kann was man vergleichen will,
zb nur die ensemble modelle vs einzelmodelle, oder alle modelle mit pca vs ohne pca,
etc.

Am Ende wenn report=True dann soll ein report als pdf erstellt werden (nützlich?)
"""


class ModelComparison:
    def __init__(self, results_dir, report=False):
        pass

    def load_metrics(self):
        pass

    def compare_performances(self):
        pass

    def plot_comparisons(self):
        pass

    def generate_report(self):
        pass