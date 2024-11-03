"""
Script zum Anwenden trainierter Modelle auf neue Daten.

Command line arguments:
--model: welches model aus registry geladen werden soll
--exprs: path zur csv mit expressions
--clinical: path zur clinical data csv (optional)
--output: wohin predictions gespeichert werden

Ablauf:
1. Lädt model (und reducer falls verwendet) aus registry
2. Lädt neue daten
3. Prüft ob alle nötigen features da sind
4. Wendet preprocessing/dimensionsreduktion an falls nötig
5. Macht predictions
6. Speichert predictions als csv

Müssen noch überlegen wie wir mit verschiedenen feature sets umgehen -
also wenn das trainierte modell andere features hatte als die neuen daten.
Vllt eine warning ausgeben?
"""


def parse_args():
    pass


def load_model():
    pass


def validate_features():
    pass


def predict():
    pass


def main():
    pass


if __name__ == "__main__":
    main()