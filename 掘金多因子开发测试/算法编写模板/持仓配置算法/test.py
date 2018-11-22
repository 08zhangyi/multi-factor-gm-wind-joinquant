# 极大分散化投资组合算法的实现
import numpy as np
from 组合与优化函数集合 import maximum_diversification

Omega = np.load('data\\cov.npy')
r = np.load('data\\ret.npy')
weights = maximum_diversification(Omega)

for i in range(28):
    print('第%d个行业的权重为%.2f%%' % (i+1, weights[i]*100.0))