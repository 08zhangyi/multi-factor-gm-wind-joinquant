from gm.api import *
import QuantLib as ql
import pandas as pd
import numpy as np
from WindPy import w
import json
from learning_model import AdaboostRegressor
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
# 引入因子类
from single_factor import PE, PB, ROE, RSI, AROON, NetProfitGrowRate, MA_10, MA_5, RevenueGrowthRate
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
# 引入工具函数和学习器
from utils import get_trading_date_from_now, get_factor_from_wind, get_return_from_wind, delete_data_cache, list_wind2jq, list_gm2wind, get_SW1_industry, get_trading_date_list_by_day_monthly
from 候选股票 import SelectedStockPoolFromListV1
# 因子预处理部分包括在了Adaboost算法中，不需要直接调用  # from 因子数据后处理 import ...
from 择时模型 import Without_select_time
from 行业轮动SW1 import Without_industry_wheel_movement
from 持仓配置 import 等权持仓

# 回测的基本参数的设定
BACKTEST_START_DATE = '2020-01-01'  # 回测开始日期
BACKTEST_END_DATE = '2020-07-16'  # 回测结束日期，测试结束日期不运用算法
INCLUDED_INDEX = ['000300.SH']  # 股票池代码，用Wind代码
EXCLUDED_INDEX = []  # 剔除的股票代码
FACTOR_LIST = [PE, PB, ROE, RSI, AROON, NetProfitGrowRate, MA_10, MA_5, RevenueGrowthRate]  # 需要获取的因子列表，用单因子研究中得模块

TRADING_DATES_LIST = ['15']  # 每月的调仓日期，非交易日寻找下一个最近的交易日
HISTORY_LENGTH = 6  # 取得的历史样本的周期数
# 选股策略的参数
SELECT_NUMBER = 20  # 选股数量
# 择时模型的配置
select_time_model = Without_select_time()
# 行业轮动的配置
industry_wheel_movement = Without_industry_wheel_movement()
# 仓位配置的参数
WEIGHTS = 等权持仓
# 仓位记录变量
stock_dict = {}  # 用于记录调仓信息的字典
position_target = {}  # 无目标持仓
position_now = False  # 无持仓

w.start()

# 根据回测阶段选取好调仓日期
trading_date_list = []  # 记录调仓日期的列表


def init(context):
    # 调仓日期获取
    global trading_date_list
    BACKTEST_START_DATE_temp = get_trading_date_from_now(BACKTEST_START_DATE, -HISTORY_LENGTH-1, ql.Months)
    trading_date_list = get_trading_date_list_by_day_monthly(BACKTEST_START_DATE_temp, BACKTEST_END_DATE, TRADING_DATES_LIST)
    # 每天time_rule定时执行algo任务，time_rule处于09:00:00和15:00:00之间
    schedule(schedule_func=algo, date_rule='daily', time_rule='10:00:00')


def algo(context):
    global position_now, position_target
    date_now = context.now.strftime('%Y-%m-%d')
    date_previous = get_trading_date_from_now(date_now, -1, ql.Days)  # 前一个交易日，用于获取因子数据的日期
    select_time_value = select_time_model[date_now]  # 择时信号计算
    print(date_now + ('日回测程序执行中...，择时值：%.2f' % select_time_value))

    if date_now not in trading_date_list:  # 非调仓日
        pass  # 预留非调仓日的微调空间
    else:  # 调仓日执行算法
        position_now = False  # 虚拟上，调仓日需要提前清仓
        # 根据指数获取股票候选池的代码
        code_list = SelectedStockPoolFromListV1(INCLUDED_INDEX, EXCLUDED_INDEX, date_previous).get_stock_pool()
        I = trading_date_list.index(date_now)
        trading_dates = trading_date_list[I-HISTORY_LENGTH:I+1]
        # 提取训练数据并训练模型
        data_dfs = []
        for i in range(len(trading_dates)-1):
            date_start = get_trading_date_from_now(trading_dates[i], -1, ql.Days)  # 计算因子值的日子，买入前一日的因子值
            date_end = get_trading_date_from_now(trading_dates[i+1], -1, ql.Days)  # 计算收益率到期的日子-收盘
            print(date_start)
            # 提取因子和收益数据
            factors_df = get_factor_from_wind(code_list, FACTOR_LIST, date_start)  # 获取因子
            return_df = get_return_from_wind(code_list, date_start, date_end)   # 可以考虑把收益率直接写到因子里，使代码更简洁
            factors_df_and_return_df = pd.concat([factors_df, return_df], axis=1).dropna()  # 去掉因子或者回报有空缺值的样本
            data_dfs.append(factors_df_and_return_df)
        factors_return_df = pd.concat(data_dfs, axis=0)  # 获取的最终训练数据拼接，return为目标
        # 根据data_df训练模型
        model = AdaboostRegressor(select_number=SELECT_NUMBER+1)  # 模型名称可以修改在前面
        model.fit(factors_return_df)
        # 根据factor_date_previous选取股票，使用模型
        factor_date_previous_df = get_factor_from_wind(code_list, FACTOR_LIST, date_previous).dropna()  # 验证集    已经校验了日期问题，没有数据重合 和 时间函数问题
        select_code_list = model.predict(factor_date_previous_df)  # 返回选取的股票代码，Wind格式
        # 行业轮动部分
        sw1_industry = get_SW1_industry(date_now, select_code_list)
        industry_wm_result = industry_wheel_movement[date_now]
        select_code_list = [stock for stock in select_code_list if sw1_industry[stock] is not None and industry_wm_result[sw1_industry[stock]] == 1]  # 忽略无行业信息的股票并根据行业择时信号选择候选股票
        # 转化为聚宽代码格式
        select_code_list = list_wind2jq(select_code_list)
        # 根据股票列表下单
        if len(select_code_list) > 0:  # 有可选股票时记录下可选股票
            stock_now = WEIGHTS(select_code_list, date_previous).get_weights()
            position_target = stock_now
        else:
            position_target = {}

    # 择时判定
    if select_time_value >= 0 and not position_now and position_target != {}:  # LLT择时信号为正,空仓且有目标持仓状态
        stock_dict[date_now] = position_target
        position_now = True
    elif select_time_value < 0 and position_now and position_target != {}:  # LLT择时信号为负且持仓状态:
        stock_dict[date_now] = {}
        position_now = False


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
        filename='adaboost回测框架.py',
        mode=MODE_BACKTEST,
        token='d7b08e7e21dd0315a510926e5a53ade8c01f9aaa',
        backtest_initial_cash=10000000,
        backtest_adjust=ADJUST_PREV,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001,
        backtest_start_time=BACKTEST_START_DATE+' 09:00:00',
        backtest_end_time=BACKTEST_END_DATE+' 15:00:00')
