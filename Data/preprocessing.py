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

    def create_merged_pData(self):
        """
        Creates a merged pData DataFrame containing only columns that are present in all cohorts.
        Preserves the original index (patient ID) from each cohort's pData.
        """
        pData_dfs = []
        for cohort_name, cohort_data in self.cohorts_dict.items():
            if 'pData' in cohort_data:
                df = cohort_data['pData'].copy()
                df['original_cohort'] = cohort_name  # Add cohort name for reference
                pData_dfs.append(df)

        # Find common columns
        common_columns = set.intersection(*[set(df.columns) for df in pData_dfs])
        common_columns = list(common_columns) + ['original_cohort']

        # Filter dataframes for common columns and concatenate
        merged_pData = pd.concat([df[common_columns] for df in pData_dfs], axis=0)

        # Create a new unique index if there are any duplicates
        if merged_pData.index.duplicated().any():
            merged_pData.index = [f"{idx}_{cohort}" for idx, cohort in
                                  zip(merged_pData.index, merged_pData['original_cohort'])]

        # Remove the temporary 'original_cohort' column
        merged_pData = merged_pData.drop('original_cohort', axis=1)

        return merged_pData

    def create_merged_exprs(self):
        """
        Creates a merged exprs DataFrame containing only genes (rows) that are present in all cohorts.
        Columns are merged based on the patients from all cohorts.
        """
        exprs_dfs = [cohort_data['exprs'] for cohort_data in self.cohorts_dict.values() if 'exprs' in cohort_data]

        # Find common genes (index)
        common_genes = set.intersection(*[set(df.index) for df in exprs_dfs])

        # Filter dataframes for common genes
        filtered_exprs_dfs = [df.loc[list(common_genes)] for df in exprs_dfs]

        # Merge dataframes
        merged_exprs = pd.concat(filtered_exprs_dfs, axis=1)

        return merged_exprs

    def preprocess_all(self):
        """
        Apply standardization to the expression data for all cohorts, fixing R NA values,
        and create merged dataframes.
        """
        self.fix_r_na_values()
        for cohort in self.cohorts_dict.keys():
            if 'exprs' in self.cohorts_dict[cohort]:
                exprs_df = self.cohorts_dict[cohort]['exprs']
                standardized_exprs_df = self.standardize(exprs_df)
                self.cohorts_dict[cohort]['exprs'] = standardized_exprs_df

        # Create merged dataframes
        self.merged_cohorts_pData = self.create_merged_pData()
        self.merged_cohorts_exprs = self.create_merged_exprs()

    def get_preprocessed_data(self):
        """
        Returns the preprocessed cohorts dictionary and merged dataframes.
        """
        return {
            'cohorts': self.cohorts_dict,
            'merged_pData': self.merged_cohorts_pData,
            'merged_exprs': self.merged_cohorts_exprs
        }

