from WindPy import w
import numpy as np
import matplotlib.pyplot as plt


# 散点与向量场画图工具
def plot_point_vector(x, y, slope, length):
    # x, y是散点位置
    # -slope是向量场斜率
    # length是向量场长度
    x1 = np.array([x-length/(np.sqrt(slope**2 + 1)), x+length/(np.sqrt(slope**2 + 1))])
    y1 = (y + slope * x) - slope * x1
    plt.plot(x1, y1, 'b')
    plt.plot([x], [y], 'ro')


w.start()
CODE_1 = '000001.SH'
CODE_2 = '399006.SZ'
CODE_1 = 'SPX.GI'
CODE_2 = 'NDX.GI'
START_DATE = '2019-01-02'
END_DATE = '2020-03-30'

DATA_1 = w.wsd(CODE_1, "close,amt", START_DATE, END_DATE, "")
DATA_2 = w.wsd(CODE_2, "close,amt", START_DATE, END_DATE, "")
"TradingCalendar=NYSE"
DATE_LIST = DATA_1.Times
CLOSE_1, AMT_1 = DATA_1.Data
CLOSE_2, AMT_2 = DATA_2.Data

for close_1, amt_1, close_2, amt_2 in zip(CLOSE_1, AMT_1, CLOSE_2, AMT_2):
    print(close_1, amt_1, close_2, amt_2)
    x = amt_1/close_1
    y = amt_2/close_2
    slope = close_1/close_2
    length = 3000000
    plot_point_vector(x, y, slope, length)

# plt.axis([0, 4, 0, 4])
plt.show()