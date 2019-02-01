import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from scipy.interpolate import griddata

# 基本输入数据
DATA_FILE_PATH = 'data\\Report_2019-01-31_18-31-21.csv'
BACKTEST_TARGET_LIST = ['Custom Criteria', 'Net Profit', 'Total Trades', '% Profitable', 'Avg Losing Trade',
                        'Win/Loss Ratio', 'Max Consecutive Losers', 'Max Intraday Drawdown', 'Profit Factor',
                        'Custom Fitness Value']
BACKTEST_TARGET = BACKTEST_TARGET_LIST[8]
BACKTEST_COEFF_LIST = ['p1 (!zhang_str_hedge_v7_stopLimit)', 'p3 (!zhang_str_hedge_v7_stopLimit)']
# 提取数据
df = pd.read_csv(DATA_FILE_PATH)
print(df.columns)  # 回测结果列表的参数情况
x_values = df[BACKTEST_COEFF_LIST].values
y_values = df[BACKTEST_TARGET].values[:, np.newaxis]
# 三维散点图
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x_values[:, 0], x_values[:, 1], y_values)
# plt.show()
# 三维差值曲面图
X0_o = np.arange(np.min(x_values, axis=0)[0], np.max(x_values, axis=0)[0], 0.1)
X1_o = np.arange(np.min(x_values, axis=0)[1], np.max(x_values, axis=0)[1], 0.1)
print(griddata(x_values, y_values, [[1, 2]]))  # 网格差值测试
X0_m, X1_m = np.meshgrid(X0_o, X1_o)
X0 = np.reshape(X0_m, (-1, 1))
X1 = np.reshape(X1_m, (-1, 1))
all_X = np.concatenate((X0, X1), axis=1)
all_Y = griddata(x_values, y_values, all_X, method='linear')
all_Y = np.reshape(all_Y, (len(X1_o), len(X0_o)))
print(all_Y.shape)
surf = ax.plot_surface(X0_m, X1_m, all_Y, cmap=cm.jet, linewidth=0, antialiased=True)
plt.colorbar(surf)
plt.title('Target Index: ' + BACKTEST_TARGET)
plt.show()
# 等高线图
cs = plt.contourf(X0_m, X1_m, all_Y, 100, cmap=cm.jet)
plt.colorbar(cs)
plt.title('Target Index: ' + BACKTEST_TARGET)
plt.show()