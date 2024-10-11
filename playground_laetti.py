# %%
#### Notebook for some EDA wrt. structure of pData
import numpy as np
import pandas as pd
from Data.load_data import CohortLoader
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import seaborn as sns 
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

cl = CohortLoader()
cl.load_cohorts('PCa_cohorts.rds') 
cohorts = cl.get_cohorts()
cols = []
cohorts_pData_list = []
cohorts_exprs_list = []
cohorts_summary_list = []

for c, c_val in cohorts.items(): 
    pData = pd.DataFrame(c_val['pData'])
    expr =  pd.DataFrame(c_val['exprs']).T
    counts_bcr = pData['BCR_STATUS'].value_counts()
    print(pData['SURGICAL_PROCEDURE'].value_counts())
    
    summary = {
        'cohort' : c,
        'ratio_BCR_01': counts_bcr[1].item()/counts_bcr[0].item(), 
        'BCR_0' : counts_bcr[0].item(), 
        'BCR_1' : counts_bcr[1].item(), 
        'MONTH_BCR_mean' : np.mean(pData['MONTH_TO_BCR']),
        'MONTH_BCR_0' : np.mean(pData[pData['BCR_STATUS'] == 0]['MONTH_TO_BCR']).item(), 
        'MONTH_BCR_1' : np.mean(pData[pData['BCR_STATUS'] == 1]['MONTH_TO_BCR']).item(), 
        'gleason_mean' : np.mean(pData['GLEASON_SCORE'])
    }
    cohorts_pData_list.append(pData)
    cohorts_exprs_list.append(expr)
    cohorts_summary_list.append(summary)

    
# %% 
len(cohorts)

#cohorts_pData_df = pd.concat(cohorts_pData_list, join = "inner", ignore_index=True)
cohorts_pData_df = cohorts_pData_list[1]
cohorts_pData_df.describe(include = "all")

cohorts_pData_df = cohorts_pData_df[['SAMPLE_ID', 'AGE', 
                                      'STUDY', 'BCR_STATUS', 
                                      'MONTH_TO_BCR', 
                                      'TISSUE', 
                                      'CLIN_TNM_STAGE', 
                                      'CLIN_T_STAGE', 
                                      'CLIN_T_STAGE_GROUP',
                                      'CLIN_M_STAGE', 
                                      'CLIN_N_STAGE', 
                                      'GLEASON_SCORE', 
                                      'GLEASON_SCORE_1', 
                                      'GLEASON_SCORE_2', 
                                      'MONTH_TO_LAST_FOLLOW_UP']]

cohorts_pData_df.info()
print(cohorts_pData_df.isnull().sum())

# %% 
#cohorts_exprs_transposed_df = pd.DataFrame(pd.concat(cohorts_exprs_list, join = "inner", ignore_index=True))
cohorts_exprs_transposed_df = cohorts_exprs_list[1]
cohorts_exprs_transposed_df.info()
print(cohorts_exprs_transposed_df.isnull().sum())

# %%
sc_exprs = StandardScaler()
cohorts_exprs_transposed_df_sc = sc_exprs.fit_transform(cohorts_exprs_transposed_df)
pca = PCA(n_components=2)
pcas = pca.fit_transform(cohorts_exprs_transposed_df_sc)
print(pca.explained_variance_ratio_)
# %%
pca_df = pd.DataFrame(data = pcas
             , columns = ['principal component 1', 'principal component 2'])
pca_df = pca_df.reset_index(drop=True)
cohorts_pData_df = cohorts_pData_df.reset_index(drop=True)
pca_df['SAMPLE_ID'] = cohorts_pData_df['SAMPLE_ID']
pca_df['BCR_STATUS'] = cohorts_pData_df['BCR_STATUS']

# %% 
fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)

targets = [1, 0]
colors = ['r', 'g']
for target, color in zip(targets,colors):
    indicesToKeep = pca_df['BCR_STATUS'] == target
    ax.scatter(pca_df.loc[indicesToKeep, 'principal component 1']
               , pca_df.loc[indicesToKeep, 'principal component 2']
               , c = color
               , s = 50)
ax.legend(targets)
ax.grid()

# %%
tsne = TSNE(3)
tsne_result = tsne.fit_transform(cohorts_exprs_transposed_df_sc)
tsne_result_df = pd.DataFrame({'tsne_1': tsne_result[:,0], 'tsne_2': tsne_result[:,1], 'label': cohorts_pData_df['BCR_STATUS']})
# %%
fig, ax = plt.subplots(1)
sns.scatterplot(x='tsne_1', y='tsne_2', hue='label', data=tsne_result_df, ax=ax,s=120)
lim = (tsne_result.min()-5, tsne_result.max()+5)
ax.set_xlim(lim)
ax.set_ylim(lim)
ax.set_aspect('equal')
ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
# %%
