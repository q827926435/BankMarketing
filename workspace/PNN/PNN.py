from keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import roc_auc_score
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import KFold
from feature import feature_engineering
from models.PNN import PNN
from utils import inputs,metric

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 200)

def train_PNN():
    X, y, data, sparse_list, dense_list = feature_engineering.get_process_data(plot=True, use_corr=True, use_variance=True, NN=True)
    dnn_feature_columns = linear_feature_columns = sparse_list + dense_list
    feature_names = inputs.get_feature_names(linear_feature_columns + dnn_feature_columns)

    # kFold cv
    models = []
    scores = []

    kf = KFold(n_splits=5, random_state=42)
    for i, (tdx, vdx) in enumerate(kf.split(X, y)):
        print(f'Fold : {i}')
        X_train, X_val, y_train, y_val = X.loc[tdx], X.loc[vdx], y.loc[tdx], y.loc[vdx]
        y_true = y_val

        X_train = {name: X_train[name] for name in feature_names}
        X_val = {name: X_val[name] for name in feature_names}

        model = PNN(dnn_feature_columns, dnn_hidden_units=(128, 64), task='binary', dnn_dropout=0.5)

        best_param_path = 'best_param_%s_%d.h5' % (os.path.basename(__file__), i)

        if os.path.exists(best_param_path):
            model.load_weights(best_param_path)
        else:
            model.compile("adam", "binary_crossentropy", metrics=['binary_crossentropy'])
            es = EarlyStopping(monitor='val_binary_crossentropy', mode='min', patience=10)
            mc = ModelCheckpoint(best_param_path, monitor='val_binary_crossentropy', mode='min', save_best_only=True,
                                 verbose=False, save_weights_only=True)
            model.fit(X_train, y_train, batch_size=1024, epochs=1000, verbose=2, validation_split=0.2,
                      callbacks=[es, mc])
            model.load_weights(best_param_path)

        y_pred = model.predict(X_val, batch_size=64).flatten()
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
    train_PNN()


