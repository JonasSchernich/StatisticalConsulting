
"""
Idee fürs Main script fürs Training.

Command line arguments:
--config: path zur training config
--output: wo die results gespeichert werden sollen (optional)

Ablauf:
1. Lädt die training config
2. Lädt entsprechende model/tuning/reduction configs
3. Lädt die Daten über den DataLoader
   - welche exprs daten und ob clinical wird in config definiert
4. Macht dimensionsreduktion falls in config angegeben
5. Splittet die daten (cohort oder random)
6. Trainiert das modell:
   - mit tuning falls angegeben, sonst default params
7. Speichert alles in results:
   - metrics
   - model
   - plots
   - configs

Später noch logging einbauen für längere runs
"""

def parse_args():
    pass

def load_configs():
    pass

def train_model():
    pass

def save_results():
    pass

def main():
    pass

if __name__ == "__main__":
    main()