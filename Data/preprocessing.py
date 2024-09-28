import pandas as pd
from Data.load_data import CohortLoader



class CohortPreprocessor:
    """
    aktuell nur die standardisierung für die wir r code bekommen haben
    """

    def __init__(self, cohorts_dict):
        """
        Initialize with the loaded cohorts dictionary.
        """
        self.cohorts_dict = cohorts_dict

    def standardize(self, df):
        """
        Standardize a DataFrame by subtracting the mean and dividing by the standard deviation for each row.

        Parameters:
        df: The data to be standardized.

        Returns:
        DataFrame: The standardized DataFrame.
        """
        # Calculate mean and standard deviation for each row
        row_mean = df.mean(axis=1)
        row_std = df.std(axis=1)

        # Subtract the mean and divide by the standard deviation
        standardized_df = df.sub(row_mean, axis=0).div(row_std, axis=0)

        return standardized_df

    def preprocess_all(self):
        """
        Apply standardization to the expression data for all cohorts.
        """
        for cohort in self.cohorts_dict.keys():
            exprs_df = self.cohorts_dict[cohort]['exprs']  # Get the exprs data
            standardized_exprs_df = self.standardize(exprs_df)  # Apply standardization

            # Overwrite the original exprs data with the standardized version
            self.cohorts_dict[cohort]['exprs'] = standardized_exprs_df

    def get_preprocessed_data(self):
        """
        Returns the preprocessed cohorts dictionary.
        """
        return self.cohorts_dict

