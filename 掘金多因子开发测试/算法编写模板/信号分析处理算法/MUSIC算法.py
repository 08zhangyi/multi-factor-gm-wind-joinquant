# MUSIC指Multiple Signal Classification，多重信号分类算法
# 此处为此算法的计算实例

import numpy as np
import matplotlib.pyplot as plt

# 一些常数
deg2rad = np.pi / 180
rad2deg = 180 / np.pi
twopi = 2 * np.pi
j = np.complex(0.0, 1.0)

kelm = 8  # 信号发射源的个数
dd = 0.5  # 信号发射源的间距
d = np.linspace(0, (kelm - 1) * dd, kelm)

iwave = 3
theta = np.array([10, 30, 60])  # 辐射的角度
snr = 30  # 信噪比
n = 500  # 采样频率
A_image = np.matmul(d.reshape((kelm, 1)), np.sin(theta * deg2rad).reshape(1, iwave)) * twopi
A = np.exp(- j * A_image)
print(A.shape)
S = np.random.randn(iwave, n)  # 信号发出的本源值生成
X = np.matmul(A, S)  # 8个信号，500个时刻长，X为信号的取值

Rx = np.matmul(X, X.transpose()) / n
InvS = np.linalg.inv(Rx)
EVA, EV = np.linalg.eig(Rx)  # EVA为特征值，EV为特征向量

I = np.argsort(EVA)
EVA = np.sort(EVA)  # 按特征值绝对值从小到大排序
EVA = EVA.reshape((1, -1))
EVA = np.fliplr(EVA)  # 按特征值绝对值从大到小排序
EVA = EVA.squeeze()
EV = EV[:, I]
EV = np.fliplr(EV)

angle = []
SP = []
for iang in range(0, 360):
    angle.append((iang - 180) / 2)
    phim = deg2rad * angle[-1]
    a = np.exp(- j * twopi * d * np.sin(phim))
    En = EV[:, iwave+1:kelm]  # 取波数以后的作为杂波部分
    print(a.shape, En.shape)
    SP.append(np.matmul(a.transpose(), a) / (np.matmul(np.matmul(a.transpose(), En), np.matmul(En.transpose(), a))))

SP = np.abs(SP)
SPmax = np.max(SP)
SP = SP / SPmax
plt.plot(angle, SP)
plt.show()