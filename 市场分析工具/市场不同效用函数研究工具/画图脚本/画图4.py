import matplotlib.pyplot as plt
import numpy as np

# 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

plt.axis([0, 4, 0, 4])  # 坐标轴范围确定


# 散点与向量场画图工具
def plot_point_vector(x, y, slope, length):
    # x, y是散点位置
    # -slope是向量场斜率
    # length是向量场长度
    x1 = np.array([x-length/(np.sqrt(slope**2 + 1)), x+length/(np.sqrt(slope**2 + 1))])
    y1 = (y + slope * x) - slope * x1
    plt.plot(x1, y1, 'b')
    plt.plot([x], [y], 'ro')


plot_point_vector(1.0, 1.0, 1.0, 0.2)
plot_point_vector(1.5, 1.5, 1.0, 0.2)
plot_point_vector(1.0, 1.5, 1.1, 0.2)
plot_point_vector(1.5, 1.0, 0.9, 0.2)
plt.xlabel('$\\frac{V_x}{x}$')
plt.ylabel('$\\frac{V_y}{y}$')

plt.show()