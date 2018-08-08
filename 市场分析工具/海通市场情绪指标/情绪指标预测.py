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

# 数据准备
key = '信用利差（%，左轴）'
time_series_ori = df[loc_dict[key]].values[N_history:0:-1]
time_series = np.diff(time_series_ori, 0)
time_series = list(time_series)

# 时序图绘制
plt.plot(time_series)
plt.show()
# 诊断图绘制
fig = plt.figure(figsize=(12, 8))
ax1 = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(time_series, lags=40, ax=ax1)
ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(time_series, lags=40, ax=ax2)
plt.show()
print('ADF检验:', adfuller(time_series))

# 计算ARMA模型的评估准则
arma_mod = sm.tsa.ARMA(time_series, (1, 1)).fit()
print('AIC:', arma_mod.aic, 'BIC:', arma_mod.bic, 'HQIC:', arma_mod.hqic)
# ARMA模型回归的诊断
resid = list(arma_mod.resid)
fig = plt.figure(figsize=(12, 8))
ax1 = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(resid, lags=40, ax=ax1)
ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(resid, lags=40, ax=ax2)
plt.show()
# Durbin-Watson检验值
print('Durbin-Watson:', sm.stats.durbin_watson(arma_mod.resid))
# 残差QQ图
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111)
fig = qqplot(np.array(resid), line='q', ax=ax, fit=True)
plt.show()

# 新的预测序列值，对应于一阶差分的计算
predict = arma_mod.predict(N_history-1, N_history+3, dynamic=True)
print(predict)
predict = predict.cumsum()  # 不用差分时两行注释掉
predict = time_series_ori[-1] + predict
print(predict)
time_series_ori_predict = np.r_[time_series_ori, predict]
plt.plot(range(len(time_series_ori)), time_series_ori, 'b')
plt.plot(range(len(time_series_ori), len(time_series_ori)+5), predict, 'r')
plt.show()


