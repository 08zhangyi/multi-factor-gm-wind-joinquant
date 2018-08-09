import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']

# 统计指标对应的信息位置
loc_dict = {'A股日换手率（年化五个交易日平滑，左轴）': 'Unnamed: 8',
            '融资交易额/总交易额(左轴）': 'Unnamed: 14',
            '涨停公司占比（左轴）': 'Unnamed: 19',
            'PE倒数减十年期国债收益率（%，左轴）': 'Unnamed: 26',
            '恒生AH股溢价指数(%，左轴）': 'Unnamed: 30',
            '信用利差（%，左轴）': 'Unnamed: 44'}
# 记录需要预测的指标，(差分阶数, (ARMA模型阶数))
statistics_dict = {'A股日换手率（年化五个交易日平滑，左轴）': (1, (5, 2)),
                   '融资交易额/总交易额(左轴）': (1, (2, 4)),
                   '涨停公司占比（左轴）': (0, (9, 1)),
                   '信用利差（%，左轴）': (1, (1, 1))}
N_history = 500  # 预测数据需要的历史数据长度
df = pd.read_excel('data\\海通策略指标.xlsx')

plot_number = len(statistics_dict)
i = 0
plt.figure(figsize=(8, 32))
for key in statistics_dict.keys():
    time_series_ori = df[loc_dict[key]].values[N_history:0:-1]
    time_series = list(np.diff(time_series_ori, statistics_dict[key][0]))

    arma_mod = sm.tsa.ARMA(time_series, statistics_dict[key][1]).fit()

    predict = arma_mod.predict(N_history - 1, N_history + 3, dynamic=True)
    if statistics_dict[key][0] == 1:  # 差分时需要加和得到原值
        predict = predict.cumsum()
        predict = time_series_ori[-1] + predict
    time_series_ori_predict = np.r_[time_series_ori, predict]
    plt.subplot(plot_number, 1, i+1)
    i += 1
    plt.plot(range(len(time_series_ori)), time_series_ori, 'b')
    plt.plot(range(len(time_series_ori), len(time_series_ori) + 5), predict, 'r')
    plt.title(key)

plt.show()  # 输出预测图