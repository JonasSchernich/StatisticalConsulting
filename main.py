from Data.load_data import CohortLoader
from Data.preprocessing import CohortPreprocessor
from Modeling.survival_ana import SurvivalAnalysis

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

# Step 3: Modeling
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
preprocessed_cohorts = preprocess_cohorts(loaded_cohorts)

# Step 3: Run the survival analysis (currently just a placeholder)
run_survival_analysis()
