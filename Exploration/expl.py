import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# load preprocessed data
with open('../Data/preprocessed_cohorts.pkl', 'rb') as f:
    preprocessed_cohorts = pickle.load(f)


