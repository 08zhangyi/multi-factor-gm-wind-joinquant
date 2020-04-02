import matplotlib.pyplot as plt
import numpy as np


x = np.arange(0.3, 3, 0.01)
y = 1/x
plt.plot(x, y)

x1 = np.arange(0.8, 1.2, 0.01)
y1 = 2 - x1
plt.plot(x1, y1)
plt.plot([1], [1], 'ro')
plt.annotate('A', xy=(1.03, 1.03))

plt.show()