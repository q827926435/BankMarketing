from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_auc_score
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
import feature_engineering
from utils.metric import cal_roc_curve

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 200)


def train_knn():
    X, y = feature_engineering.get_train_data(use_over_sampler=True)
    data = pd.DataFrame(y)
    # kFold cv
    models = []
    scores = []

    kf = StratifiedKFold(n_splits=5, random_state=42)
    for i, (tdx, vdx) in enumerate(kf.split(X, y)):
        print(f'Fold : {i}')
        X_train, X_val, y_train, y_val = X.loc[tdx], X.loc[vdx], y.loc[tdx], y.loc[vdx]
        y_true = y_val

        model = KNeighborsClassifier(n_neighbors=5,weights='uniform', algorithm='auto', leaf_size=30,
                                     p=2, metric='minkowski')
        model.fit(X_train, y_train)

        y_pred = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_true, y_pred)
        print("AUC score at %d floder: %f" % (i, auc))
        scores.append(auc)
        models.append(model)
        data.loc[vdx, 'y_pred'] = y_pred
        # print(data['y_pred'].value_counts())

    mean_score = np.mean(scores)
    oof = roc_auc_score(data['y'], data['y_pred'])
    print("5-floder total mean_score:", mean_score)
    print("5-floder oof auc score:", oof)
    print("----train %s finish!----" % model.__class__.__name__)
    cal_roc_curve(data['y'], data['y_pred'], model.__class__.__name__)

    return data['y_pred']


if __name__ == '__main__':
    knn_oof = train_knn()
