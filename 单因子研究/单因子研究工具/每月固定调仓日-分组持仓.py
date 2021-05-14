from gm.api import *
import QuantLib as ql
from WindPy import w
import json
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from single_factor import PE
# 引入工具函数和学习器
from utils import get_trading_date_from_now, get_fix_trading_days_from_start_to_end_monthly, list_wind2jq
from 持仓配置 import 等权持仓, 自由流通市值权重_行业版
from 候选股票 import SelectedStockPoolFromListExcluded

# 用于记录调仓信息的字典
stock_dict = {}
w.start()

BACKTEST_START_DATE = '2014-08-01'  # 回测开始日期
BACKTEST_END_DATE = '2018-08-14'  # 回测结束日期，测试结束日期不运用算法


def init(context):
    # 回测的基本参数的设定
    global BACKTEST_START_DATE, BACKTEST_END_DATE
    context.INCLUDED_INDEX = ['000300.SH']  # 股票池代码，用Wind代码
    context.EXCLUDED_INDEX = []  # 剔除的股票代码
    context.FACTOR = PE  # 需要获取的因子列表，用单因子研究中得模块
    context.QUANTILE = [0.8, 1.0]  # 因子分组的分位数
    context.TRADING_DATES = ['10']  # 每月的调仓日期，非交易日寻找下一个最近的交易日
    context.WEIGHTS_FUNCTION = 自由流通市值权重_行业版  # 仓位配置
    # 根据回测阶段选取好调仓日期
    print('提取调仓日信息......')
    trading_date_list = get_fix_trading_days_from_start_to_end_monthly(BACKTEST_START_DATE,
                                                                       BACKTEST_END_DATE,
                                                                       context.TRADING_DATES)
    BACKTEST_START_DATE = trading_date_list[0]  # 调整回测起始日为第一次调仓的日子
    context.trading_date_list = trading_date_list
    # 每天time_rule定时执行algo任务，time_rule处于09:00:00和15:00:00之间
    schedule(schedule_func=algo, date_rule='daily', time_rule='10:00:00')


def algo(context):
    date_now = context.now.strftime('%Y-%m-%d')
    print(date_now + '日回测程序执行中...')
    if date_now not in context.trading_date_list:  # 非调仓日
        pass  # 预留非调仓日的微调空间
    else:  # 调仓日执行算法
        date_previous = get_trading_date_from_now(date_now, -1, ql.Days)  # 前一个交易日，用于获取因子数据的日期
        code_list = SelectedStockPoolFromListExcluded(context.INCLUDED_INDEX, context.EXCLUDED_INDEX, date_previous).get_stock_pool()
        factor = context.FACTOR(date_previous, code_list)  # 读取单因子的代码
        df = factor.get_factor().dropna()
        quantiles = df.quantile(context.QUANTILE).values  # 取对应的分位数值
        stock_codes = list(df[(df[factor.factor_name] >= quantiles[0][0]) & (df[factor.factor_name] < quantiles[1][0])].index.values)
        stock_codes = list_wind2jq(stock_codes)  # 仓位配置前转换为聚宽代码
        stock_now = context.WEIGHTS_FUNCTION(stock_codes, date_previous).get_weights()
        stock_dict[date_now] = stock_now


def on_backtest_finished(context, indicator):
    # 输出回测指标
    print(indicator)
    stock_json = json.dumps(stock_dict)
    stock_file = open('data\\stock_json.json', 'w')
    stock_file.write(stock_json)
    stock_file.close()


if __name__ == '__main__':
    run(strategy_id='4d2f6b1c-8f0a-11e8-af59-305a3a77b8c5',
        filename='每月固定调仓日-分组持仓.py',
        mode=MODE_BACKTEST,
        token='d7b08e7e21dd0315a510926e5a53ade8c01f9aaa',
        backtest_initial_cash=10000000,
        backtest_adjust=ADJUST_PREV,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001,
        backtest_start_time=BACKTEST_START_DATE+' 09:00:00',
        backtest_end_time=BACKTEST_END_DATE+' 15:00:00')