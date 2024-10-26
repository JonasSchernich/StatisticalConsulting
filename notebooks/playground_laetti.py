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
from Data.preprocessing import CohortPreprocessor
from sksurv.linear_model import CoxnetSurvivalAnalysis





# %% 

# %%
def plot_coefficients(coefs, n_highlight):
    _, ax = plt.subplots(figsize=(9, 6))
    n_features = coefs.shape[0]
    alphas = coefs.columns
    for row in coefs.itertuples():
        ax.semilogx(alphas, row[1:], ".-", label=row.Index)

    alpha_min = alphas.min()
    top_coefs = coefs.loc[:, alpha_min].map(abs).sort_values().tail(n_highlight)
    for name in top_coefs.index:
        coef = coefs.loc[name, alpha_min]
        plt.text(alpha_min, coef, name + "   ", horizontalalignment="right", verticalalignment="center")

    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.grid(True)
    ax.set_xlabel("alpha")
    ax.set_ylabel("coefficient")

# %%
cl = CohortLoader()
cl.load_cohorts('PCa_cohorts.rds') 
cohorts = cl.get_cohorts()
cp = CohortPreprocessor(cohorts)
cp.fix_r_na_values()
cp.fix_pData_types()
cp.preprocess_all()
cohorts = cp.get_preprocessed_data()['cohorts']

# %% 
cols = []
cohorts_pData_list = []
cohorts_exprs_list = []
cohorts_summary_list = []
df_null = pd.DataFrame()

for c, c_val in cohorts.items(): 
    pData = pd.DataFrame(c_val['pData'])
    expr =  pd.DataFrame(c_val['exprs']).T
    counts_bcr = pData['BCR_STATUS'].value_counts()
    # print(pData['SURGICAL_PROCEDURE'].value_counts())
    # print(null_vals)
    null_vals = pData.isnull().sum().to_frame().T
    df_null = pd.concat([df_null, null_vals])
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

cohorts_pData_df = pd.concat(cohorts_pData_list, join = "inner", ignore_index=True)
#cohorts_pData_df = cohorts_pData_list
cohorts_pData_df.describe(include = "all")
df_null_per_coh = cohorts_pData_df.set_index('STUDY').isnull().groupby(["STUDY"]).sum().astype(int)

# %%V
#y = cohorts_pData_df[['BCR_STATUS', 'MONTH_TO_BCR']]
#y['BCR_STATUS'] = y['BCR_STATUS'].astype('bool')

cohorts_pData_df = cohorts_pData_df[['SAMPLE_ID', 
                                     'AGE', 
                                      #'STUDY', 
                                      'BCR_STATUS', 
                                      'MONTH_TO_BCR', 
                                      #'TISSUE', 
                                      #'CLIN_TNM_STAGE', 
                                      #'PATH_T_STAGE', 
                                      #'CLIN_T_STAGE_GROUP',
                                      #'CLIN_M_STAGE', 
                                      #'CLIN_N_STAGE', 
                                      'GLEASON_SCORE', 
                                      #'GLEASON_SCORE_1', 
                                      #'GLEASON_SCORE_2', 
                                      #'MONTH_TO_LAST_FOLLOW_UP'
                                      ]]

cohorts_pData_df.info()
print(cohorts_pData_df.isnull().sum())

# %% 
cohorts_exprs_transposed_df = pd.DataFrame(pd.concat(cohorts_exprs_list, join = "inner", ignore_index=True))
#cohorts_exprs_transposed_df = cohorts_exprs_list[1]
cohorts_exprs_transposed_df.info()
print(cohorts_exprs_transposed_df.isnull().sum())

# %%
sc_exprs = StandardScaler()
cohorts_exprs_transposed_df_sc = pd.DataFrame(sc_exprs.fit_transform(cohorts_exprs_transposed_df))
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
tsne = TSNE(2)
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

# %% 
cohorts_exprs_transposed_df_sc['SAMPLE_ID'] = cohorts_pData_df['SAMPLE_ID']
X = pd.merge(cohorts_pData_df, cohorts_exprs_transposed_df_sc, on = ["SAMPLE_ID"])
#X = X.drop(['SAMPLE_ID'], axis = 1)
X = X.dropna()

dtype = [('BCR_STATUS', bool), ('MONTH_TO_BCR', float)]

# %%
# Convert the DataFrame into a structured array
dtype = [('event', bool), ('time', float)]

y = np.array([(bool(e), t) for e, t in 
              zip(X['BCR_STATUS'], X['MONTH_TO_BCR'])], dtype = dtype)
X = X.drop(['SAMPLE_ID', 'MONTH_TO_BCR', 'BCR_STATUS'], axis = 1)
# %%
cox_lasso = CoxnetSurvivalAnalysis(l1_ratio=1.0, alpha_min_ratio=0.01)
cox_lasso.fit(X, y)
# %%
coefficients_lasso = pd.DataFrame(cox_lasso.coef_, index=X.columns, columns=np.round(cox_lasso.alphas_, 5))

plot_coefficients(coefficients_lasso, n_highlight=5)


# %%
import warnings
from sklearn.exceptions import FitFailedWarning
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, KFold

# %%
coxnet_pipe = make_pipeline(StandardScaler(), CoxnetSurvivalAnalysis(l1_ratio=1.0, alpha_min_ratio=0.05, max_iter=1000, n_alphas = 15))
warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", FitFailedWarning)
coxnet_pipe.fit(X, y)
# %%
estimated_alphas = coxnet_pipe.named_steps["coxnetsurvivalanalysis"].alphas_
cv = KFold(n_splits=2, shuffle=True, random_state=0)
# %%
gcv = GridSearchCV(
    make_pipeline(StandardScaler(), CoxnetSurvivalAnalysis(l1_ratio=1.0)),
    param_grid={"coxnetsurvivalanalysis__alphas": [[v] for v in estimated_alphas]},
    cv=cv,
    #error_score=0.5,
    n_jobs=-1,
).fit(X, y)

cv_results = pd.DataFrame(gcv.cv_results_)
 # %%
alphas = cv_results.param_coxnetsurvivalanalysis__alphas.map(lambda x: x[0])
mean = cv_results.mean_test_score
std = cv_results.std_test_score

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(alphas, mean)
ax.fill_between(alphas, mean - std, mean + std, alpha=0.15)
ax.set_xscale("log")
ax.set_ylabel("concordance index")
ax.set_xlabel("alpha")
ax.axvline(gcv.best_params_["coxnetsurvivalanalysis__alphas"][0], c="C1")
ax.axhline(0.5, color="grey", linestyle="--")
ax.grid(True)
# %%
best_model = gcv.best_estimator_.named_steps["coxnetsurvivalanalysis"]
best_coefs = pd.DataFrame(best_model.coef_, index=X.columns, columns=["coefficient"])

non_zero = np.sum(best_coefs.iloc[:, 0] != 0)
print(f"Number of non-zero coefficients: {non_zero}")

non_zero_coefs = best_coefs.query("coefficient != 0")
coef_order = non_zero_coefs.abs().sort_values("coefficient").index

_, ax = plt.subplots(figsize=(6, 8))
non_zero_coefs.loc[coef_order].plot.barh(ax=ax, legend=False)
ax.set_xlabel("coefficient")
ax.grid(True)

# %% 
coxnet_pred = make_pipeline(StandardScaler(), CoxnetSurvivalAnalysis(l1_ratio=0.9, fit_baseline_model=True))
coxnet_pred.set_params(**gcv.best_params_)
coxnet_pred.fit(X, y)




# %%
from sksurv.ensemble import RandomSurvivalForest
from sklearn.model_selection import train_test_split

random_state = 20

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=random_state) 
# %%
rsf = RandomSurvivalForest(
    n_estimators=1, min_samples_split=2, min_samples_leaf=3, n_jobs=-1, random_state=random_state
)
rsf.fit(X_train, y_train)
# %%
rsf.score(X_test, y_test)
# %%
from sklearn.inspection import permutation_importance

result = permutation_importance(rsf, X_test, y_test, n_repeats=15, random_state=random_state, n_jobs = -1)
# %%
pd.DataFrame(
    {
        k: result[k]
        for k in (
            "importances_mean",
            "importances_std",
        )
    },
    index=X_test.columns,
).sort_values(by="importances_mean", ascending=False)


# %%
# compare lasso results across cohorts