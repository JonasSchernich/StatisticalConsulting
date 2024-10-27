
import numpy as np
import pandas as pd
from lifelines.utils import concordance_index
from xgboost import plot_importance
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import xgboost as xgb




def create_xgb_data(df_pdata, df_pdata_X, times_col, events_col, df_exprs): 
    times = df_pdata[times_col]
    events = df_pdata[events_col]
    
    y_lower_bound = np.where(events == 1, times, times)  # Use event time for both cases
    y_upper_bound = np.where(events == 1, times, np.inf)  # Use +∞ for censored observations
    
    X = pd.concat([df_pdata_X, df_exprs], axis = 1)
    y = df_pdata[times_col]
    y_event = df_pdata[events_col]
    X_temp, X_test, y_temp, y_test, y_lower_temp, y_lower_test, y_upper_temp, y_upper_test, y_temp_event, y_test_event = train_test_split(X, y, y_lower_bound, y_upper_bound, y_event, test_size=0.2, random_state=42)
    X_train, X_valid, y_train, y_valid, y_lower_train, y_lower_valid, y_upper_train, y_upper_valid, y_train_event, y_valid_event = train_test_split(X_temp, y_temp, y_lower_temp, y_upper_temp, y_temp_event, test_size=0.2, random_state=42)

    # Convert data into DMatrix, specifying the label, label_lower_bound, and label_upper_bound
    dtrain = xgb.DMatrix(X_train, label=y_train, label_lower_bound=y_lower_train, label_upper_bound=y_upper_train, enable_categorical = True)
    dtest = xgb.DMatrix(X_test, label=y_test, label_lower_bound=y_lower_test, label_upper_bound=y_upper_test, enable_categorical = True)
    dvalid = xgb.DMatrix(X_valid, label=y_valid, label_lower_bound=y_lower_valid, label_upper_bound=y_upper_valid, enable_categorical = True)
    
    return dtrain, dtest, dvalid, y_train_event, y_test_event, y_valid_event
    
    



def do_XGB_AFT(dtrain, dtest, dvalid, y_train, y_test,y_valid, y_train_event, y_test_event, 
               y_valid_event, num_boost_round, lr, max_depth, min_child_weight, 
               la, alpha): 
    params = {
    #'objective': 'survival:cox',
    #'eval_metric': 'cox-nloglik',
    'objective': 'survival:aft',
    'eval_metric': 'aft-nloglik',
    #'aft_loss_distribution': 'normal',
    #'aft_loss_distribution_scale': 1.0,
    'lambda' : la, 
    'alpha' : alpha,
    'learning_rate': lr, 
    'max_depth' : int(max_depth), 
    'tree_method' : 'hist', 
    'validate_parameters' : True, 
    'min_child_weight' : min_child_weight
}
    
    evallist = [(dtrain, 'train'), (dvalid, 'eval')]
    model = xgb.train(params, dtrain, num_boost_round= int(num_boost_round), evals=evallist, early_stopping_rounds=10)
    
    y_pred_test = model.predict(dtest)
    y_pred_train = model.predict(dtrain)

    ci_xgb_train = concordance_index(y_train, y_pred_train, y_train_event)
    ci_xgb_test = concordance_index(y_test, y_pred_test, y_test_event)
    
    result = {
        'ci_test' : ci_xgb_test, 
        'ci_train' : ci_xgb_train, 
        'num_boost_round' : num_boost_round,
        'importance' : model.get_score(importance_type='gain')
        
    }
    result.update(params)
    
    # Plot based on the fitted model
    # plot_importance(model, importance_type='gain')  # You can also use 'weight' or 'cover'
    # plt.show()
    
    return result
    
    
    
