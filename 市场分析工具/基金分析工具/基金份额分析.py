from WindPy import w
import numpy as np
import matplotlib.pyplot as plt

START_DATE = '2020-01-02'
END_DATE = '2020-03-26'
FUND_CODE_LIST = ['513050.SH', '513100.SH', '513500.SH', '513030.SH']


def plot_fund_share(start_date, end_date, fund_code_list):
    # 支持中文
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 提取数据
    w.start()
    p_list = []
    for fund_code in fund_code_list:
        wind_return_object = w.wsd(fund_code, "unit_total", start_date, end_date, "")
        datas = wind_return_object.Data
        dates = wind_return_object.Times
        shares = np.array(datas[0])
        shares = shares / shares[0]
        # 画图
        p, = plt.plot(dates, shares)
        p_list.append(p)
    plt.legend(p_list, fund_code_list, loc='upper left')
    plt.title('基金份额变动图')
    plt.show()


if __name__ == '__main__':
    plot_fund_share(START_DATE, END_DATE, FUND_CODE_LIST)