
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm_notebook
from scipy.sparse import csr_matrix
import seaborn as sns
from matplotlib import pyplot as plt


train_df = pd.read_csv("train_sessions.csv", index_col="session_id")
test_df = pd.read_csv("test_sessions.csv", index_col="session_id")

times = ["time%s" % i for i in range(1, 11)]
train_df[times] = train_df[times].apply(pd.to_datetime)
test_df[times] = test_df[times].apply(pd.to_datetime)

train_df = train_df.sort_values(by="time1")


sites = ["site%s" % i for i in range(1, 11)]
train_df[sites] = train_df[sites].fillna(0).astype("int")
test_df[sites] = test_df[sites].fillna(0).astype("int")



y_train = train_df["target"]

full_df = pd.concat([train_df.drop("target", axis=1), test_df])

idx_split = train_df.shape[0]


full_sites = full_df[sites]

sites_flatten = full_sites.values.flatten()

full_sites_sparse = csr_matrix(
    (
        [1] * sites_flatten.shape[0],
        sites_flatten,
        range(0, sites_flatten.shape[0] + 10, 10),
    )
)[:, 1:]



X_train_sparse = full_sites_sparse[:idx_split]
X_test_sparse = full_sites_sparse[idx_split:]


def get_auc_lr_valid(X, y, C=1, ratio=0.9, seed=17):
    train_len = int(ratio * X.shape[0])
    X_train = X[:train_len, :]
    X_valid = X[train_len:, :]
    y_train = y[:train_len]
    y_valid = y[train_len:]

    logit = LogisticRegression(C=C, n_jobs=-1, random_state=seed)

    logit.fit(X_train, y_train)

    valid_pred = logit.predict_proba(X_valid)[:, 1]

    return roc_auc_score(y_valid, valid_pred)



def write_to_submission_file(
    predicted_labels, out_file, target="target", index_label="session_id"
):
    predicted_df = pd.DataFrame(
        predicted_labels,
        index=np.arange(1, predicted_labels.shape[0] + 1),
        columns=[target],
    )
    predicted_df.to_csv(out_file, index_label=index_label)

logit = LogisticRegression(n_jobs=-1, random_state=17)
logit.fit(X_train_sparse, y_train)


test_pred = logit.predict_proba(X_test_sparse)[:, 1]

write_to_submission_file(test_pred, "submission.csv")