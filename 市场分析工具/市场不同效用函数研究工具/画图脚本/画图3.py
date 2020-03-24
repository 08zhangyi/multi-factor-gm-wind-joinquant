import matplotlib.pyplot as plt
import numpy as np

# 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

plt.axis([0, 2, 0, 2])
x1 = np.arange(0.8, 1.2, 0.01)
y1 = 2 - x1
plt.plot(x1, y1)
plt.plot([1], [1], 'ro')
plt.annotate('斜率=$-\\frac{x}{y}$', xy=(1.03, 1.03))
plt.xlabel('$\\frac{V_x}{x}$')
plt.ylabel('$\\frac{V_y}{y}$')

plt.show()