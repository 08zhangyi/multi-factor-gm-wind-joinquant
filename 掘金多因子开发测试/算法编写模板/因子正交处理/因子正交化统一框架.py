import numpy as np

N = 300  # 股票样本数量
K = 10  # 因子数量
F = np.random.randn(N, K)  # 仿真因子生成

S = np.random.randn(K, K)  # S为因子变化矩阵的形状，目标是求S
Ft = np.matmul(F, S)
print('确认F*K后的矩阵形状为N*K，', Ft.shape)

M = np.matmul(F.transpose(), F)  # 计算F的Overlap Matrix，即协方差矩阵乘以N-1
# 生成K*K大小的随机正交矩阵的代码
C = np.random.randn(K, K)
C, _ = np.linalg.qr(C)
# 由于M为正定对称矩阵，可以对M进行对角化，并开根号
D, U = np.linalg.eig(M)
D = np.diag(D)
zero_matrix = M - np.matmul(U, np.matmul(D, U.transpose()))  # 验证公式，M = U * D * Utraanspose
D_sqrt_inverse = np.linalg.inv(np.sqrt(D))
M_sqrt_inverse = np.matmul(U, np.matmul(D_sqrt_inverse, U.transpose()))
S = np.matmul(M_sqrt_inverse, C)  # S = M^-0.5 * C，C为任意正交矩阵，则有S * Stranspose = M^-1
# 此时Ft = F * S满足Fttranspose * Ft = I，完成正交化

# 施密特正交化，S为上三角矩阵

# 规范正交，C = U，不推荐
S = np.matmul(U, D_sqrt_inverse)
Ft = np.matmul(F, S)

# 规范正交，C = I，推荐
S = M_sqrt_inverse
Ft = np.matmul(F, S)