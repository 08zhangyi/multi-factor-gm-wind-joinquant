import numpy as np
from hmmlearn import hmm

model = hmm.GaussianHMM(n_components=3, covariance_type="full")
model.startprob_ = np.array([0.6, 0.3, 0.1])
model.transmat_ = np.array([[0.7, 0.2, 0.1],
                            [0.3, 0.5, 0.2],
                            [0.3, 0.3, 0.4]])
model.means_ = np.array([[0.0, 0.0], [3.0, -3.0], [5.0, 10.0]])
model.covars_ = np.tile(np.identity(2), (3, 1, 1))  # (3, 2, 2)
print(model.covars_)
X, Z = model.sample(1000)
print(X.shape, Z.shape)  # X为n行乘以2列，2为X的特征大小

remodel = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=1000)
remodel.fit(X)
print(remodel.startprob_)
print(remodel.transmat_)
Z2 = remodel.predict_proba(X)
print(Z2)
# print(Z)

remodel.fit(X)
print(remodel.startprob_)
print(remodel.transmat_)