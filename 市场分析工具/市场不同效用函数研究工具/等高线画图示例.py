import numpy as np
import matplotlib.pyplot as plt


# 目标画图函数
def f(x, y):
    """
    计算高度的函数
    :param x: 向量，m*n
    :param y: 向量，m*n
    :return: dim(x)*dim(y)维的矩阵
    """
    return (1 - x / 2 + x**5 + y**3) * np.exp(-x**2 - y**2)


x = np.linspace(-5, 5, 256)
y = np.linspace(-5, 5, 256)
X, Y = np.meshgrid(x, y)  # 画图网格
plt.contourf(X, Y, f(X, Y), 8, cmap=plt.cm.hot)
c = plt.contour(X, Y, f(X, Y), 8, colors='black')
# plt.clabel(c, inline=True, fontsize=10)  # 等高线标注
# plt.xticks(())  # 删除坐标
# plt.yticks(())
plt.show()
