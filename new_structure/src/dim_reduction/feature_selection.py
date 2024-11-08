from sklearn.model_selection import SelectFromModel
from models.boosting import GBModel


def do_feat_sel(X, y, params, max_features): 
    model_flag = params['model_class']
    model_params = params['model_params']      
    if(model_flag == 'GBM'): 
        model = GBModel(model_params)
        selector = SelectFromModel(model, 
                        max_features=max_features)
        selector.fit(X, y)
        return selector.transform(X), selector.get_feature_names_out()
    else: 
        print("Not implemented yet - None's returned")
        return None, None
    

def do_feat_sel_fitted(model, X, max_features): 
    selector = SelectFromModel(model, prefit=True, max_features=max_features)
    return selector.transform(X), selector.get_feature_names_out()
        
