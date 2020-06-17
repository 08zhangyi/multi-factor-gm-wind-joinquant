from gm.api import *
import QuantLib as ql
from WindPy import w
import json
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
# 引入工具函数和学习器
from utils import get_trading_date_from_now, list_wind2jq, list_gm2wind, get_trading_date_list_by_day_monthly
from 择时模型 import RSRS_standardization_V1
from 持仓配置 import 等权持仓 as WEIGHTS
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\大师选股策略')
from 大师选股 import 本杰明格雷厄姆成长股内在价值投资法 as STRATEGY

w.start()

# 回测的基本参数的设定
BACKTEST_START_DATE = '2018-10-10'  # 回测开始日期
BACKTEST_END_DATE = '2020-06-16'  # 回测结束日期，测试结束日期不运用算法
INDEX = ['000300.SH']  # 股票池代码，可以用掘金代码，也可以用Wind代码
TRADING_DATES_LIST = ['10']  # 每月的调仓日期，非交易日寻找下一个最近的交易日

# 择时模型的配置
RSRS_N = 18
RSRS_M = 600
RSRS_INDEX = '000300.SH'  # 计算择时的指数
select_time_model = RSRS_standardization_V1(BACKTEST_START_DATE, BACKTEST_END_DATE, RSRS_INDEX, RSRS_N, RSRS_M)

stock_dict = {}  # 用于记录调仓信息的字典
position_target = {}  # 无目标持仓
position_now = False  # 无持仓

# 根据回测阶段选取好调仓日期
trading_date_list = []  # 记录调仓日期的列表


def init(context):
    # 调仓日期获取
    global trading_date_list
    trading_date_list = get_trading_date_list_by_day_monthly(BACKTEST_START_DATE, BACKTEST_END_DATE, TRADING_DATES_LIST)
    # 每天time_rule定时执行algo任务，time_rule处于09:00:00和15:00:00之间
    schedule(schedule_func=algo, date_rule='daily', time_rule='10:00:00')


def algo(context):
    global position_now, position_target
    date_now = context.now.strftime('%Y-%m-%d')
    date_previous = get_trading_date_from_now(date_now, -1, ql.Days)  # 前一个交易日，用于获取因子数据的日期
    select_time_value = select_time_model[date_now]  # 择时信号计算

    if date_now not in trading_date_list:  # 非调仓日
        pass
    else:  # 调仓日执行算法，更新position_target
        position_now = False  # 虚拟上，调仓日需要提前清仓
        stock_dict[date_now] = {}
        # 根据指数获取股票候选池的代码
        all_code_set = set()
        for index in INDEX:
            code_set = set(w.wset("sectorconstituent", "date=" + date_previous + ";windcode=" + index).Data[1])
            all_code_set = all_code_set | code_set
        code_list = list(all_code_set)  # 股票候选池
        strategy = STRATEGY(code_list, date_previous, 0.9)
        select_code_list = list_wind2jq(strategy.select_code())
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

    # 打印择时信号和仓位配置信息
    print(date_now + ('日回测程序执行中...，择时值：%.2f' % select_time_value))
    print(date_now + '日回测程序执行中...，选股：')
    print(position_target)


def on_backtest_finished(context, indicator):
    # 输出回测指标
    print(indicator)
    stock_json = json.dumps(stock_dict)
    stock_file = open('data\\stock_json1.json', 'w')
    stock_file.write(stock_json)
    stock_file.close()


if __name__ == '__main__':
    run(strategy_id='4d2f6b1c-8f0a-11e8-af59-305a3a77b8c5',
        filename='本杰明格雷厄姆_RSRS择时V1_json1.py',
        mode=MODE_BACKTEST,
        token='d7b08e7e21dd0315a510926e5a53ade8c01f9aaa',
        backtest_initial_cash=10000000,
        backtest_adjust=ADJUST_PREV,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001,
        backtest_start_time=BACKTEST_START_DATE+' 09:00:00',
        backtest_end_time=BACKTEST_END_DATE+' 15:00:00')