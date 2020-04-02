import matplotlib.pyplot as plt
import numpy as np

# 互补品效用函数
x1 = np.arange(1.0, 3.0, 0.001)
x2 = np.ones(len(x1)) * 1.0
y1 = np.ones(len(x1)) * 1.0
y2 = np.arange(1.0, 3.0, 0.001)

plt.plot(x1, y1, 'b-')
plt.plot(x2, y2, 'b-')
plt.xlim((0.0, 3.2))
plt.ylim((0.0, 3.2))
plt.show()

# 替代品效用函数
x3 = np.arange(0.5, 3.5, 0.001)
y3 = 4.0 - x3
plt.plot(x3, y3, 'b-')
plt.xlim((0.0, 4.0))
plt.ylim((0.0, 4.0))
plt.show()