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

    def fix_r_na_values(self):
        for cohort_name, cohort_data in self.cohorts_dict.items():
            for data_type in ['pData', 'fData', 'exprs']:
                if data_type in cohort_data:
                    df = cohort_data[data_type]
                    for column in df.columns:
                        unique_values = df[column].unique()
                        if len(unique_values) == 1 and unique_values[0] == -2147483648:
                            df[column] = None
                    cohort_data[data_type] = df
            self.cohorts_dict[cohort_name] = cohort_data

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
        Apply standardization to the expression data for all cohorts and fixing R NA values
        """
        self.fix_r_na_values()
        for cohort in self.cohorts_dict.keys():
            if 'exprs' in self.cohorts_dict[cohort]:
                exprs_df = self.cohorts_dict[cohort]['exprs']
                standardized_exprs_df = self.standardize(exprs_df)
                self.cohorts_dict[cohort]['exprs'] = standardized_exprs_df

    def get_preprocessed_data(self):
        """
        Returns the preprocessed cohorts dictionary.
        """
        return self.cohorts_dict

