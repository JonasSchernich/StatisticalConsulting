import os
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
pandas2ri.activate()

class CohortLoader:
    """
    Habe schonmal ein framework zum Laden mehrerer mehrere Expression Objekte erstellt
    """

    def __init__(self):
        """
        Initialize an empty cohorts dictionary.
        """
        self.cohorts_dict = {}

    def load_cohorts(self, rds_file_name):
        """
        Load an RDS file and convert each ExpressionSet into a Python dictionary.
        """
        if rds_file_name is None:
            raise ValueError("No RDS file name provided.")


        rds_file_path = os.path.join("Data", rds_file_name)

        # Define the R code to load and convert the ExpressionSet objects
        r_code = f'''
        library(Biobase)

        # Load data from the RDS file
        cohorts <- readRDS("{rds_file_path}")

        # Function to convert ExpressionSet to list of data frames
        convertExpressionSet <- function(eset) {{
            list(
                pData = as.data.frame(pData(eset)),
                fData = as.data.frame(fData(eset)),
                exprs = as.data.frame(exprs(eset))
            )
        }}

        # Convert all cohorts to list of data frames
        cohorts_list <- lapply(cohorts, convertExpressionSet)
        '''

        # Execute the R code
        robjects.r(r_code)
        cohorts_list_r = robjects.r['cohorts_list']

        # Convert the R list to a Python dictionary
        for cohort_name in cohorts_list_r.names:
            cohort_name_str = str(cohort_name)  # necessary because for some reason the pandas string can't be used
            cohort_data = cohorts_list_r.rx2(cohort_name_str)
            self.cohorts_dict[cohort_name_str] = {
                'pData': pandas2ri.rpy2py(cohort_data.rx2('pData')),
                'fData': pandas2ri.rpy2py(cohort_data.rx2('fData')),
                'exprs': pandas2ri.rpy2py(cohort_data.rx2('exprs'))
            }



    def get_cohorts(self):
        """
        Returns the loaded cohorts dictionary.
        """
        return self.cohorts_dict