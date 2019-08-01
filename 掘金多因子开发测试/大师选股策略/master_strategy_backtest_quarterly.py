from gm.api import *
import QuantLib as ql
from WindPy import w
import json
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
# 引入工具函数和学习器
from utils import get_trading_date_from_now, list_wind2jq, list_gm2wind
from master_strategy import 戴维斯双击v3 as STRATEGY
from 持仓配置 import 等权持仓 as WEIGHTS
from 候选股票 import SelectedStockPoolFromListV1

w.start()

# 回测的基本参数的设定
BACKTEST_START_DATE = '2010-07-09'  # 回测开始日期
BACKTEST_END_DATE = '2018-09-04'  # 回测结束日期，测试结束日期不运用算法
INCLUDED_INDEX = ['000300.SH', '000016.SH']  # 股票池代码，用Wind代码
EXCLUDED_INDEX = ['801780.SI']  # 剔除的股票代码
TRADING_DATE = '21'  # 每月的调仓日期，非交易日寻找下一个最近的交易日
QUARTERS = ['1', '4', '7', '10']  # 每季度的调仓月份，一共四个

# 用于记录调仓信息的字典
stock_dict = {}

# 根据回测阶段选取好调仓日期
trading_date_list = []  # 记录调仓日期的列表


def init(context):
    global date_trading  # 调仓日期获取
    i = 0
    while True:
        print('处理日期：' + str(i))
        date_now = get_trading_date_from_now(BACKTEST_START_DATE, i, ql.Days)  # 遍历每个交易日
        date_trading = get_trading_date_from_now(
            date_now.split('-')[0] + '-' + date_now.split('-')[1] + '-' + TRADING_DATE, 0, ql.Days)
        if date_now == date_trading:
            trading_date_list.append(date_now)
        i += 1
        if date_now == BACKTEST_END_DATE:
            break
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
        strategy = STRATEGY(code_list, date_previous)
        select_code_list = list_wind2jq(strategy.select_code())
        if len(select_code_list) > 0:  # 有可选股票时选取合适的股票
            stock_now = WEIGHTS(select_code_list, date_previous).get_weights()
            stock_dict[date_now] = stock_now
        else:
            stock_dict[date_now] = {}
        # 待开发选股策略


def on_backtest_finished(context, indicator):
    # 输出回测指标
    print(indicator)
    stock_json = json.dumps(stock_dict)
    stock_file = open('data\\stock_json.json', 'w')
    stock_file.write(stock_json)
    stock_file.close()


if __name__ == '__main__':
    run(strategy_id='4d2f6b1c-8f0a-11e8-af59-305a3a77b8c5',
        filename='master_strategy_backtest_quarterly.py',
        mode=MODE_BACKTEST,
        token='d7b08e7e21dd0315a510926e5a53ade8c01f9aaa',
        backtest_initial_cash=10000000,
        backtest_adjust=ADJUST_PREV,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001,
        backtest_start_time=BACKTEST_START_DATE+' 09:00:00',
        backtest_end_time=BACKTEST_END_DATE+' 15:00:00')