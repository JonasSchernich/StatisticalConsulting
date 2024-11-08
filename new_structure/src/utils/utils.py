from sksurv.metrics import concordance_index_censored
import re
import numpy as np


def cindex_score(y, y_pred):
    ci = concordance_index_censored(
            y['event'],
            y['time'],
            y_pred
        )
    return ci[0]


def get_cohort(X): 
    def extract_cohort_name(text):
        regex = r"^([^.]+)\."
        match = re.search(regex, text)
        if match:
            return match.group(1)
        return None

    cohort_col = [extract_cohort_name(cor) for cor in X.index.tolist()]
    return cohort_col

def create_surv_y(y_events, y_times): 
    y = np.array([(bool(e), t) for e, t in 
              zip(y_events, y_times)], dtype = [('event', bool), ('time', float)])
    return y
    