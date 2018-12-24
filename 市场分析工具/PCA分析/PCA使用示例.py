from sklearn import datasets
from sklearn.decomposition import PCA
import numpy as np

iris = datasets.load_iris()
X = iris.data
print(X.shape)

pca = PCA(n_components=4)
r = pca.fit(X)
print(r.explained_variance_ratio_ )
print(r.components_  )
print(np.linalg.det(r.components_ ))