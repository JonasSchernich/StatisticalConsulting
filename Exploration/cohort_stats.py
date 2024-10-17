import pandas as pd


class CohortStats:
    def __init__(self, preprocessed_data):
        self.preprocessed_data = preprocessed_data
        self.stats_df = pd.DataFrame()

    def calculate_cohort_stats(self, cohort_name):
        cohort_data = self.preprocessed_data['cohorts'][cohort_name]
        pdata = cohort_data['pData']
        exprs = cohort_data['exprs']

        stats = {
            'cohort_name': cohort_name,
            'min_age': pdata['AGE'].min(),
            'q25_age': pdata['AGE'].quantile(0.25),
            'median_age': pdata['AGE'].median(),
            'q75_age': pdata['AGE'].quantile(0.75),
            'max_age': pdata['AGE'].max(),
            'patient_count': len(pdata),
            'tissue': pdata['TISSUE'].iloc[0] if 'TISSUE' in pdata.columns else 'N/A',
        }

        # Function to calculate counts and proportions
        def calculate_stage_stats(column_name, stages):
            total_stage = 0
            for stage in stages:
                count = (pdata[column_name] == stage).sum()
                stats[f'count_{column_name}_{stage}'] = count
                total_stage += count

            for stage in stages:
                stats[f'prop_{column_name}_{stage}'] = stats[
                                                           f'count_{column_name}_{stage}'] / total_stage if total_stage > 0 else 0

        # Path_T_Stage and CLIN_T_STAGE counts and proportions
        t_stages = ['T1', 'T1A', 'T1B', 'T1C', 'T2', 'T2A', 'T2B', 'T2C', 'T3', 'T3A', 'T3B', 'T4']
        calculate_stage_stats('PATH_T_STAGE', t_stages)
        calculate_stage_stats('CLIN_T_STAGE', t_stages)

        # Gleason Score counts and proportions
        total_gleason = 0
        for score in range(2, 11):
            count = (pdata['GLEASON_SCORE'] == score).sum()
            stats[f'gleason_{score}'] = count
            total_gleason += count

        for score in range(2, 11):
            stats[f'gleason_{score}_prop'] = stats[f'gleason_{score}'] / total_gleason if total_gleason > 0 else 0

        # GLEASON_SCORE_1 and GLEASON_SCORE_2 counts and proportions
        for gs_column in ['GLEASON_SCORE_1', 'GLEASON_SCORE_2']:
            total_gs = 0
            for score in range(1, 6):
                count = (pdata[gs_column] == score).sum()
                stats[f'{gs_column}_{score}'] = count
                total_gs += count

            for score in range(1, 6):
                stats[f'{gs_column}_{score}_prop'] = stats[f'{gs_column}_{score}'] / total_gs if total_gs > 0 else 0

        # PRE_OPERATIVE_PSA stats
        psa_data = pdata['PRE_OPERATIVE_PSA']
        stats.update({
            'psa_mean': psa_data.mean(),
            'psa_median': psa_data.median(),
            'psa_min': psa_data.min(),
            'psa_max': psa_data.max(),
            'psa_q25': psa_data.quantile(0.25),
            'psa_q75': psa_data.quantile(0.75),
            'psa_over_4_count': (psa_data > 4).sum(),
            'psa_over_4_prop': (psa_data > 4).sum() / len(psa_data) if len(psa_data) > 0 else 0
        })

        # MONTH_TO_BCR stats for patients with BCR_STATUS == 1
        bcr_data = pdata[pdata['BCR_STATUS'] == 1]['MONTH_TO_BCR']
        stats.update({
            'bcr_mean': bcr_data.mean(),
            'bcr_median': bcr_data.median(),
            'bcr_min': bcr_data.min(),
            'bcr_max': bcr_data.max(),
            'bcr_q25': bcr_data.quantile(0.25),
            'bcr_q75': bcr_data.quantile(0.75)
        })

        # Calculate proportion of patients with BCR_STATUS = 1
        bcr_count = (pdata['BCR_STATUS'] == 1).sum()
        stats['bcr_proportion'] = bcr_count / len(pdata) if len(pdata) > 0 else 0

        # Gene count
        stats['gene_count'] = exprs.index.nunique()

        return stats

    def calculate_all_cohort_stats(self):
        all_stats = []
        for cohort_name in self.preprocessed_data['cohorts'].keys():
            cohort_stats = self.calculate_cohort_stats(cohort_name)
            all_stats.append(cohort_stats)

        self.stats_df = pd.DataFrame(all_stats)
        return self.stats_df

    def get_stats_df(self):
        return self.stats_df