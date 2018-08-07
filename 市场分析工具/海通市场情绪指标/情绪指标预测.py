import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.api import qqplot

# 统计指标对应的信息位置
loc_dict = {'A股日换手率（年化五个交易日平滑，左轴）': 'Unnamed: 8',
            '融资交易额/总交易额(左轴）': 'Unnamed: 14',
            '涨停公司占比（左轴）': 'Unnamed: 19',
            'PE倒数减十年期国债收益率（%，左轴）': 'Unnamed: 26',
            '恒生AH股溢价指数(%，左轴）': 'Unnamed: 30',
            '信用利差（%，左轴）': 'Unnamed: 44'}
N_history = 550  # 预测数据需要的历史数据长度
df = pd.read_excel('data\\海通策略指标.xlsx')

key = 'A股日换手率（年化五个交易日平滑，左轴）'
time_series_ori = df[loc_dict[key]].values[N_history:0:-1]
time_series = np.diff(time_series_ori, 1)
time_series = list(time_series)
print(len(time_series))

# fig = plt.figure(figsize=(12, 8))
# ax1 = fig.add_subplot(211)
# fig = sm.graphics.tsa.plot_acf(time_series, lags=40, ax=ax1)
# ax2 = fig.add_subplot(212)
# fig = sm.graphics.tsa.plot_pacf(time_series, lags=40, ax=ax2)
# plt.show()
# print(adfuller(time_series))

arma_mod = sm.tsa.ARMA(time_series, (5, 2)).fit()
# print(arma_mod.aic, arma_mod.bic, arma_mod.hqic)

resid = list(arma_mod.resid)
fig = plt.figure(figsize=(12, 8))
ax1 = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(resid, lags=40, ax=ax1)
ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(resid, lags=40, ax=ax2)
plt.show()

print(sm.stats.durbin_watson(arma_mod.resid))

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111)
fig = qqplot(np.array(resid), line='q', ax=ax, fit=True)
plt.show()

predict_sunspots = arma_mod.predict(N_history-1, N_history+3, dynamic=True)
print(predict_sunspots)
predict_sunspots = predict_sunspots.cumsum()
predict_sunspots = time_series_ori[-1] + predict_sunspots
print(predict_sunspots)
time_series_ori_predict = np.r_[time_series_ori, predict_sunspots]
plt.plot(range(len(time_series_ori)), time_series_ori, 'b')
plt.plot(range(len(time_series_ori), len(time_series_ori)+5), predict_sunspots, 'r')
plt.show()
