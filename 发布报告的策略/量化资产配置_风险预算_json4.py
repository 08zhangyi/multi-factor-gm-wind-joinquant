from gm.api import *
import QuantLib as ql
from WindPy import w
import json
import numpy as np
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
# 引入工具函数和学习器
from utils import get_trading_date_from_now, list_wind2jq, list_gm2wind, get_trading_date_list_by_day_monthly
from 持仓配置 import 风险预算组合_模块求解基本版_带约束

w.start()

# 回测的基本参数的设定
BACKTEST_START_DATE = '2019-01-15'  # 回测开始日期
BACKTEST_END_DATE = '2020-04-03'  # 回测结束日期，测试结束日期不运用算法
# 国内债券部分配置方案
stock_pool_bond = ['511010.SH']
risk_budget_bond = [1.0]  # 候选目标[0.2, 0.8, 0.8]
risk_bounds_bond = np.array([[0.4, 0.85]])
# 国内股票部分配置方案
stock_pool_stock = ['159949.SZ', '159928.SZ', '510050.SH', '510500.SH']
risk_budget_stock = [1.0, 1.0, 1.0, 1.0]  # 总权重固定为4个单位
risk_bounds_stock = np.array([[0.0, 1.0]] * len(stock_pool_stock))
# 国际部分配置方案
stock_pool_global = ['513100.SH', '513500.SH', '518880.SH']
risk_budget_global = [0.8, 0.8, 0.8]  # 在区间[0.75, 0.75, 0.8]-[1.0, 1.0, 1.0]之间灵活调整
risk_bounds_global = np.array([[0.0, 0.2]] * len(stock_pool_global))
# 合并为整体证券池
stock_pool = stock_pool_bond + stock_pool_stock + stock_pool_global
risk_budget = risk_budget_bond + risk_budget_stock + risk_budget_global
risk_bounds = np.concatenate([risk_bounds_bond, risk_bounds_stock, risk_bounds_global])
stock_pool = list_wind2jq(stock_pool)
EXCLUDED_INDEX = []  # 剔除的股票代码
TRADING_DATES_LIST = ['05', '15', '25']  # 每月的调仓日期，非交易日寻找下一个最近的交易日

# 用于记录调仓信息的字典
stock_dict = {}

# 根据回测阶段选取好调仓日期
trading_date_list = []  # 记录调仓日期的列表


def init(context):
    # 调仓日期获取
    global trading_date_list
    trading_date_list = get_trading_date_list_by_day_monthly(BACKTEST_START_DATE, BACKTEST_END_DATE, TRADING_DATES_LIST)
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
        if len(stock_pool) > 0:  # 有可选股票时选取合适的股票
            stock_now = 风险预算组合_模块求解基本版_带约束(stock_pool, date_previous, risk_budget=risk_budget, bounds=risk_bounds).get_weights()
            # stock_now['161716.XSHE'] = 0.09
            # stock_now['167501.XSHE'] = 0.06
            # stock_now['511010.XSHG'] = stock_now['511010.XSHG'] - 0.15
            print(stock_now)
            stock_dict[date_now] = stock_now
        else:
            stock_dict[date_now] = {}


def on_backtest_finished(context, indicator):
    # 输出回测指标
    print(indicator)
    stock_json = json.dumps(stock_dict)
    stock_file = open('data\\stock_json4.json', 'w')
    stock_file.write(stock_json)
    stock_file.close()


if __name__ == '__main__':
    run(strategy_id='4d2f6b1c-8f0a-11e8-af59-305a3a77b8c5',
        filename='量化资产配置_风险预算_json4.py',
        mode=MODE_BACKTEST,
        token='d7b08e7e21dd0315a510926e5a53ade8c01f9aaa',
        backtest_initial_cash=10000000,
        backtest_adjust=ADJUST_PREV,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001,
        backtest_start_time=BACKTEST_START_DATE+' 09:00:00',
        backtest_end_time=BACKTEST_END_DATE+' 15:00:00')