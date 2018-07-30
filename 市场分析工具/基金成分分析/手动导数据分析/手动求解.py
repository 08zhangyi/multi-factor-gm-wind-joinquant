import pandas as pd
import numpy as np
from cvxopt import matrix, solvers

df = pd.read_csv('data\\data2.csv', index_col=0)
return_values = df.values
fundation_values = return_values[:, 0:1]
index_values = return_values[:, 1:]
print(fundation_values.shape, index_values.shape)
x_szie = index_values.shape[1]

Q = np.zeros((29, 29))
p = np.zeros(29)
G = np.zeros((29, 29))
h = np.zeros(29)
A = np.ones((1, 29))
b = np.ones(1)

for i in range(x_szie):
    for j in range(x_szie):
        if i == j:
            Q[i, j] = np.sum(index_values[:, i] * index_values[:, j])
            G[i, j] = -1
        else:
            Q[i, j] = np.sum(index_values[:, i] * index_values[:, j])
for i in range(x_szie):
    p[i] = -2 * np.sum(fundation_values[:, 0] * index_values[:, i])

Q = matrix(Q)
p = matrix(p)
G = matrix(G)
h = matrix(h)
A = matrix(A)
b = matrix(b)

sol = solvers.qp(Q, p, G, h, A, b)
x_sol = np.array(sol['x']).transpose()[0]
for x in x_sol:
    print(x)