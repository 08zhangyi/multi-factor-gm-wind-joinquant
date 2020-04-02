from WindPy import w
import numpy as np
import matplotlib.pyplot as plt

START_DATE = '2017-01-02'
END_DATE = '2020-03-30'
FUND_CODE_LIST = ['513050.SH', '513100.SH', '513500.SH', '513030.SH', '513520.SH']


def plot_fund_premium(start_date, end_date, fund_code):
    # 支持中文
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 提取数据
    w.start()
    wind_return_object = w.wsd(fund_code, "close,nav,iopv", start_date, end_date, "")
    datas = wind_return_object.Data
    dates = [t.strftime('%Y-%m-%d') for t in w.wsd(fund_code, "close,nav,iopv", start_date, end_date, "").Times]
    close = np.array(datas[0])
    nav = np.array(datas[1])
    iopv = np.array(datas[2])
    nav_premium = (close - nav) / nav
    iopv_premium = (close - iopv) / iopv
    # 画图
    p1, = plt.plot(nav_premium)
    p2, = plt.plot(iopv_premium)
    plt.legend([p1, p2], ['净值溢价率', 'IOPV溢价率'], loc='upper left')
    plt.title(fund_code + '收盘价溢价率图示')
    ax = plt.gca()
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.01))
    ax.grid(which='major', axis='y', linewidth=0.75, linestyle='-', color='0.75')
    plt.show()


if __name__ == '__main__':
    for FUND_CODE in FUND_CODE_LIST:
        plot_fund_premium(START_DATE, END_DATE, FUND_CODE)