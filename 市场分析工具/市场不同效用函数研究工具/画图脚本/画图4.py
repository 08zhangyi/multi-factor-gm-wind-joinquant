import matplotlib.pyplot as plt
import numpy as np

# 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

plt.axis([0, 4, 0, 4])


def plot_point_vector(x, y, slope, length):
    x1 = np.arange(x-length/(np.sqrt(slope**2 + 1)), x+length/(np.sqrt(slope**2 + 1)), 0.001)
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