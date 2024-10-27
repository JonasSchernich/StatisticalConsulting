import pandas as pd

def get_features_cox(path, col_name_features, col_name_coef): 
    df = pd.read_csv(path)
    
    if len(df) == 1: 
        genes_list= eval(df[col_name_features].iloc[0])
        coef_list = eval(df[col_name_coef].iloc[0])
    else: 
        genes_list_temp = []
        coef_list_temp = []
        for index, row in df.iterrows():
            genes = row[[col_name_features]][0]
            coefs = row[[col_name_coef]][0]
            gene_list = eval(genes)
            coef_list = eval(coefs)
            genes_list_temp.append(gene_list)
            coef_list_temp.append(coefs)

        genes_list = [elem for sublist in genes_list_temp for elem in sublist]
        coef_list = [elem for sublist in coef_list_temp for elem in sublist]
        
        df_feat = pd.DataFrame({'feature':genes_list, 'coeff':coef_list})

    return df_feat


def get_features_xgb(path, col_name_metric, col_name_imp): 
    df = pd.read_csv(path)
    df = df[df[col_name_metric] == df[col_name_metric].max()][0]
    
    importance = df[col_name_imp][0]
    importance_df = pd.DataFrame({'col':importance.keys(), 'gain':importance.values()}).sort_values(by = 'gain', ascending=False)
    
    return importance_df
  