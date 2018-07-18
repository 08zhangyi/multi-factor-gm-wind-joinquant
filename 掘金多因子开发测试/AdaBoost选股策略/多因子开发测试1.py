from gm.api import *
import QuantLib as ql
import pandas as pd
import copy
from tools import get_trading_date_from_now, get_factor_from_wind

# 回测的基本参数的设定
BACKTEST_START_DATE = '2017-02-27'  # 回测开始日期
BACKTEST_END_DATE = '2018-06-20'  # 回测结束日期，测试结束日期不运用算法
INDEX = 'SHSE.000016'  # 股票池代码
FACTOR_LIST = []  # 需要获取的因子列表，用单因子研究中得模块
TRADING_DATE = '10'  # 每月的调仓日期，非交易日寻找下一个最近的交易日
HISTORY_LENGTH = 3  # 取得的历史样本的周期数
# 创建历史数据记录的文件夹

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
    # 按照回测的将股票池的历史股票组成提出并合并
    history_constituents = get_history_constituents(INDEX, start_date=BACKTEST_START_DATE, end_date=BACKTEST_END_DATE)
    history_constituents = [set(temp['constituents'].keys()) for temp in history_constituents]
    history_constituents_all = set()
    for temp in history_constituents:
        history_constituents_all = history_constituents_all | temp
    history_constituents_all = list(history_constituents_all)
    pd.DataFrame(history_constituents_all).to_csv('data\\设计到的股票代码.csv')  # 存储股票代码以方便调试
    # 根据板块的历史数据组成订阅数据
    subscribe(symbols=history_constituents_all, frequency='1d')
    # 每天time_rule定时执行algo任务，time_rule处于09:00:00和15:00:00之间
    schedule(schedule_func=algo, date_rule='daily', time_rule='10:00:00')


def algo(context):
    date_now = context.now.strftime('%Y-%m-%d')
    date_previous = get_trading_date_from_now(date_now, -1, ql.Days)  # 前一个交易日，用于获取因子数据的日期
    if date_now not in trading_date_list:  # 非调仓日
        pass  # 预留非调仓日的微调空间
    else:  # 调仓日执行算法
        code_list = list(get_history_constituents(INDEX, start_date=date_previous, end_date=date_previous)[0]['constituents'].keys())
        I = trading_date_list.index(date_now)
        trading_dates = trading_date_list[I-HISTORY_LENGTH:I]
        for date in trading_dates:
            get_factor_from_wind(code_list, FACTOR_LIST, date)


def on_backtest_finished(context, indicator):
    print(indicator)


if __name__ == '__main__':
    run(strategy_id='efed2881-7511-11e8-8fe1-305a3a77b8c5',
        filename='多因子开发测试1.py',
        mode=MODE_BACKTEST,
        token='d7b08e7e21dd0315a510926e5a53ade8c01f9aaa',
        backtest_start_time=BACKTEST_START_DATE+' 09:00:00',
        backtest_end_time=BACKTEST_END_DATE+' 15:00:00')