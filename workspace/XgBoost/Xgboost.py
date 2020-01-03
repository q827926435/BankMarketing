from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from xgboost.sklearn import XGBClassifier
from sklearn.model_selection import KFold
from feature import feature_engineering
from utils import metric

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 200)


def train_xgb(plot=False):
    X, y, data = feature_engineering.get_process_data(plot=True, use_corr=True, use_variance=True)

    # kFold cv
    models = []
    scores = []
    checkpoint_predictions = []

    kf = KFold(n_splits=5, random_state=42)
    for i, (tdx, vdx) in enumerate(kf.split(X, y)):
        print(f'Fold : {i}')
        X_train, X_val, y_train, y_val = X.loc[tdx], X.loc[vdx], y.loc[tdx], y.loc[vdx]
        y_true = y_val

        params = {
            'learning_rate': .05,
            'n_estimators': 2000,
            'max_depth': 8,
            'min_child_weight': 4,
            'gamma': .2,
            'subsample': .8,
            'colsample_bytree': .8,

            'n_jobs': -1,
            'random_state': 0
        }
        model = XGBClassifier().set_params(**params)
        model.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_val, y_val)], early_stopping_rounds=50,
                  verbose=False)

        ## plot feature importance
        if plot:
            fscores = pd.Series(model.feature_importances_, X_train.columns).sort_values(ascending=False)
            fscores.plot(kind='bar', title='Feature Importance %d' % i, figsize=(20, 10))
            plt.ylabel('Feature Importance Score')
            plt.show()

        y_pred = model.predict_proba(X_val, ntree_limit=model.best_ntree_limit)[:, 1]
        auc = roc_auc_score(y_true, y_pred)
        print("AUC score at %d floder: %f" % (i, auc))
        scores.append(auc)
        models.append(model)
        data.loc[vdx, 'y_pred'] = y_pred
        # print(data['y_pred'].value_counts())

    mean_score = np.mean(scores)
    coupon_mean_score = metric.metric_coupon_AUC(data)
    print("coupon mean_score:", coupon_mean_score)
    print("5-floder total mean_score:", mean_score)


if __name__ == '__main__':
    train_xgb(plot=True)
