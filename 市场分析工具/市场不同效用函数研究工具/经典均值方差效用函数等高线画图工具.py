import numpy as np
import matplotlib.pyplot as plt

# 效用函数的参数
Er_1 = 0.08
Er_2 = 0.09
alpha = 3
sigma_1 = 0.2
sigma_2 = 0.22
rho_1_2 = 0.5


# 效用函数，仅支持二元效用函数
def U(w_1, w_2):
    """
    计算高度的函数
    :param w_1: 向量，m*n
    :param w_2: 向量，m*n
    :return: dim(x)*dim(y)维的矩阵
    """
    utility = Er_1 * w_1 + Er_2 * w_2 - 0.5 * alpha * \
              (sigma_1**2 * w_1**2 + sigma_2**2 * w_2**2 + 2 * rho_1_2 * sigma_1 * sigma_2 * w_1 * w_2)
    return utility


x = np.linspace(0.0, 1.0, 1024)
y = np.linspace(0.0, 1.0, 1024)
X, Y = np.meshgrid(x, y)  # 画图网格
plt.contourf(X, Y, U(X, Y), 8, cmap=plt.cm.hot)
c = plt.contour(X, Y, U(X, Y), 8, colors='black')
plt.clabel(c, inline=True, fontsize=10)  # 等高线标注
plt.title('E$r_1$=%.2f, E$r_2$=%.2f, $\\alpha$=%.2f\n$\\sigma_1$=%.2f, $\\sigma_2$=%.2f, $\\rho_{12}$=%.2f' %
          (Er_1, Er_2, alpha, sigma_1, sigma_2, rho_1_2))
plt.plot(x, -y+1, '--')
plt.show()
