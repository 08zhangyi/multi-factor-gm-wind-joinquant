from gm.api import *
import QuantLib as ql
import pandas as pd
from WindPy import w
import json
from learning_model import OrdinaryLinearRegression
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
# 引入因子类
from single_factor import RSI, PE
# 引入工具函数和学习器
from utils import get_trading_date_from_now, get_factor_from_wind, get_return_from_wind, delete_data_cache, sort_data, list_wind2jq, list_gm2wind
from 候选股票 import SelectedStockPoolFromListV1

# 回测的基本参数的设定
BACKTEST_START_DATE = '2017-02-27'  # 回测开始日期
BACKTEST_END_DATE = '2018-07-23'  # 回测结束日期，测试结束日期不运用算法
INCLUDED_INDEX = ['000300.SH', '000016.SH']  # 股票池代码，用Wind代码
EXCLUDED_INDEX = ['801780.SI']  # 剔除的股票代码
FACTOR_LIST = [RSI, PE]  # 需要获取的因子列表，用单因子研究中得模块
TRADING_DATE = '10'  # 每月的调仓日期，非交易日寻找下一个最近的交易日
HISTORY_LENGTH = 3  # 取得的历史样本的周期数
STOCK_NUMBER = 10  # 选股数量

# 用于记录调仓信息的字典
stock_dict = {}
w.start()

# 根据回测阶段选取好调仓日期
trading_date_list = []  # 记录调仓日期的列表
i = 0
while True:
    date_now = get_trading_date_from_now(BACKTEST_START_DATE, i, ql.Days)  # 遍历每个交易日
    date_trading = get_trading_date_from_now(date_now.split('-')[0] + '-' + date_now.split('-')[1] + '-' + TRADING_DATE, 0, ql.Days)
    if date_now == date_trading:
        trading_date_list.append(date_now)
    i += 1
    if date_now == BACKTEST_END_DATE:
        break
BACKTEST_START_DATE = trading_date_list[HISTORY_LENGTH]  # 调整回测起始日为第一次调仓的日子


def init(context):
    # 每天time_rule定时执行algo任务，time_rule处于09:00:00和15:00:00之间
    schedule(schedule_func=algo, date_rule='daily', time_rule='10:00:00')


def algo(context):
    date_now = context.now.strftime('%Y-%m-%d')
    date_previous = get_trading_date_from_now(date_now, -1, ql.Days)  # 前一个交易日，用于获取因子数据的日期
    if date_now not in trading_date_list:  # 非调仓日
        pass  # 预留非调仓日的微调空间
    else:  # 调仓日执行算法
        print(date_now+'日回测程序执行中...')
        # 根据指数获取股票候选池的代码
        code_list = SelectedStockPoolFromListV1(INCLUDED_INDEX, EXCLUDED_INDEX, date_previous).get_stock_pool()
        I = trading_date_list.index(date_now)
        trading_dates = trading_date_list[I-HISTORY_LENGTH:I+1]
        data_dfs = []
        for i in range(len(trading_dates)-1):
            date_start = get_trading_date_from_now(trading_dates[i], -1, ql.Days)  # 计算因子值的日子，买入前一日的因子值
            date_end = get_trading_date_from_now(trading_dates[i+1], -1, ql.Days)  # 计算收益率到期的日子-收盘

            factors_df = get_factor_from_wind(code_list, FACTOR_LIST, date_start)  # 获取因子
            return_df = get_return_from_wind(code_list, date_start, date_end)
            factors_df_and_return_df = pd.concat([factors_df, return_df], axis=1).dropna()  # 去掉因子或者回报有空缺值的样本
            factors_df_and_return_df = sort_data(factors_df_and_return_df)  # 使用排序数据作为输入
            data_dfs.append(factors_df_and_return_df)
        factors_return_df = pd.concat(data_dfs, axis=0)  # 获取的最终训练数据拼接，return为目标
        # 根据data_df训练模型
        model = OrdinaryLinearRegression()
        model.fit(factors_return_df)
        # 根据factor_date_previous选取股票
        factor_date_previous_df = get_factor_from_wind(code_list, FACTOR_LIST, date_previous).dropna()
        sorted_codes = model.predict(factor_date_previous_df)  # 获取预测收益率从小到大排序的股票列表
        sorted_codes = list_wind2jq(sorted_codes)
        # 根据股票列表下单
        stock_codes = sorted_codes[-STOCK_NUMBER:]
        stock_now = {}
        for stock_code in stock_codes:  # 平均持仓持股
            stock_now[stock_code] = 1./STOCK_NUMBER
        stock_dict[date_now] = stock_now


def on_backtest_finished(context, indicator):
    delete_data_cache()  # 删除缓存中的数据，可手动选取是否删除
    # 输出回测指标
    print(indicator)
    stock_json = json.dumps(stock_dict)
    stock_file = open('data\\stock_json.json', 'w')
    stock_file.write(stock_json)
    stock_file.close()


if __name__ == '__main__':
    run(strategy_id='4d2f6b1c-8f0a-11e8-af59-305a3a77b8c5',
        filename='多因子开发测试1.py',
        mode=MODE_BACKTEST,
        token='d7b08e7e21dd0315a510926e5a53ade8c01f9aaa',
        backtest_initial_cash=10000000,
        backtest_adjust=ADJUST_PREV,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001,
        backtest_start_time=BACKTEST_START_DATE+' 09:00:00',
        backtest_end_time=BACKTEST_END_DATE+' 15:00:00')