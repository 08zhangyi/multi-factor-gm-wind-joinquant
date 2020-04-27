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


def sigma_value(x_1, y_1, amt_x_1, amt_y_1, x_2, y_2, amt_x_2, amt_y_2):
    sigma_1 = np.log(amt_x_1 / amt_y_1) - np.log(amt_x_2 / amt_y_2)
    sigma_2 = np.log(x_1 / y_1) - np.log(x_2 / y_2)
    sigma = (-sigma_1 + sigma_2) / sigma_2
    return sigma


w.start()
CODE_1 = '000001.SH'
CODE_2 = '399006.SZ'
START_DATE = '2019-12-31'
END_DATE = '2020-03-30'

DATA_1 = w.wsd(CODE_1, "close,amt", START_DATE, END_DATE, "")
DATA_2 = w.wsd(CODE_2, "close,amt", START_DATE, END_DATE, "")
"TradingCalendar=NYSE"
DATE_LIST = DATA_1.Times
CLOSE_1, AMT_1 = DATA_1.Data
CLOSE_2, AMT_2 = DATA_2.Data

close_1_prev, amt_1_prev, close_2_prev, amt_2_prev = None, None, None, None
for close_1, amt_1, close_2, amt_2, date in zip(CLOSE_1, AMT_1, CLOSE_2, AMT_2, DATE_LIST):
    print(date, ' datas: ', close_1, amt_1, close_2, amt_2)
    x = amt_1/close_1
    y = amt_2/close_2
    slope = close_1/close_2
    length = 3000000
    plot_point_vector(x, y, slope, length)
    if close_1_prev is not None:
        sigma = sigma_value(close_1_prev, close_2_prev, amt_1_prev, amt_2_prev, close_1, close_2, amt_1, amt_2)
        print(date, ' sigma: ', sigma)
    close_1_prev, amt_1_prev, close_2_prev, amt_2_prev = close_1, amt_1, close_2, amt_2

# plt.axis([0, 4, 0, 4])
plt.show()