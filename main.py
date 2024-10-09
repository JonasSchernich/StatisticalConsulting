import pickle
from Data.load_data import CohortLoader
from Data.preprocessing import CohortPreprocessor
from Modeling.survival_ana import SurvivalAnalysis
from Exploration.cohort_stats import CohortStats

# Step 1: Load the cohort data using the CohortLoader class
def load_cohorts(rds_file_names):
    loader = CohortLoader()
    for rds_file_name in rds_file_names:
        loader.load_cohorts(rds_file_name)
    return loader.get_cohorts()

# Step 2: Preprocess the loaded cohort data
def preprocess_cohorts(cohorts_dict):
    preprocessor = CohortPreprocessor(cohorts_dict)
    preprocessor.preprocess_all()
    return preprocessor.get_preprocessed_data()

# Step 3: Cohort Statistics
def run_cohort_stats(preprocessed_data):
    """
    Calculates statistics on the different cohorts to provide an overview
    over the data structure
    :return: Data Frame with statistics
    """
    stats_calculator = CohortStats(preprocessed_data)
    cohort_stats_df = stats_calculator.calculate_all_cohort_stats()
    return cohort_stats_df

# Step 4: Modeling
def run_survival_analysis():
    """
    Dummy function
    """
    survival_ana = SurvivalAnalysis()
    survival_ana.build_model()  # Placeholder call



# using a list of file names to load the data
rds_file_names = ["PCa_cohorts.Rds"]#, "PCa_cohorts_2.Rds"] # PCa_cohorts_2 habe ich manuell generiert um zu prüfen obs geht

# Step 1: Load the cohorts
loaded_cohorts = load_cohorts(rds_file_names)

# Step 2: Preprocess the loaded cohorts
preprocessed_data = preprocess_cohorts(loaded_cohorts)

# aktuell nur eine zwischenlösung, damit man die Daten nicht jedes mal neu laden muss, wenn man sie in anderen Files nutzt
with open('Data/preprocessed_data.pkl', 'wb') as f:
    pickle.dump(preprocessed_data, f)


# Step 3: Generate Statistics
cohort_stats_df = run_cohort_stats(preprocessed_data)
with open('Data/cohort_stats_df.pkl', 'wb') as f:
    pickle.dump(cohort_stats_df, f)
# Step 4: Run the survival analysis (currently just a placeholder)
run_survival_analysis()
