from gm.api import *
import QuantLib as ql
from WindPy import w
import json
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
# 引入工具函数和学习器
from utils import get_trading_date_from_now, list_wind2jq, list_gm2wind
from master_strategy import 本杰明格雷厄姆成长股内在价值投资法 as STRATEGY

w.start()

# 回测的基本参数的设定
BACKTEST_START_DATE = '2010-03-10'  # 回测开始日期
BACKTEST_END_DATE = '2018-08-23'  # 回测结束日期，测试结束日期不运用算法
INDEX = '000300.SH'  # 股票池代码，可以用掘金代码，也可以用Wind代码
TRADING_DATE = '10'  # 每月的调仓日期，非交易日寻找下一个最近的交易日

# LLT择时指数参数
def LLT(price_list, d=69):  # LLT计算函数
    a = 2 / (d + 1)  # LLT的参数
    LLT_list = [price_list[0], price_list[1]]  # 记录LLT值列表的初始化序列
    for t in range(2, len(price_list)):
        LLT_value = (a - (a ** 2 / 4)) * price_list[t] + (a ** 2 / 2) * price_list[t - 1] - (a - (3 * a ** 2 / 4)) * price_list[t - 2] + 2 * (1 - a) * LLT_list[-1] - (1 - a) ** 2 * LLT_list[-2]
        LLT_list.append(LLT_value)
    return (LLT_list[-1] - LLT_list[-2]) / price_list[-1]  # LLT趋势值，>=阈值买入，<阈值空仓
LLT_HISTORY = 100  # 计算LLT使用的历史时期
LLT_THRESHOLD = -0.003
LLT_INDEX = '000001.SH'  # 计算LLT择时的指数
LLT_START_DATE = get_trading_date_from_now(BACKTEST_START_DATE, -LLT_HISTORY, ql.Days)
data = w.wsd(LLT_INDEX, "close", LLT_START_DATE, BACKTEST_END_DATE, "")
LLT_TIMES = [t.strftime('%Y-%m-%d') for t in data.Times]
LLT_DATA = data.Data[0]

# 用于记录调仓信息的字典
stock_dict = {}
position_target = {}  # 无目标持仓
position_now = False  # 无持仓

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


def init(context):
    # 根据板块的历史数据组成订阅数据
    # subscribe(symbols=history_constituents_all, frequency='1d')
    # 每天time_rule定时执行algo任务，time_rule处于09:00:00和15:00:00之间
    schedule(schedule_func=algo, date_rule='daily', time_rule='10:00:00')


def algo(context):
    global position_now, position_target
    date_now = context.now.strftime('%Y-%m-%d')
    date_previous = get_trading_date_from_now(date_now, -1, ql.Days)  # 前一个交易日，用于获取因子数据的日期
    # 计算当日的LLT指标
    llt_index = LLT_TIMES.index(date_now)
    price_list = LLT_DATA[llt_index-100:llt_index]
    llt_value = LLT(price_list)
    print(date_now + ('日回测程序执行中...，LLT值：%.4f' % llt_value))

    if date_now not in trading_date_list:  # 非调仓日
        pass
    else:  # 调仓日执行算法，更新position_target
        position_now = False  # 虚拟上，调仓日需要提前清仓
        stock_dict[date_now] = {}
        try:
            code_list = list_gm2wind(list(get_history_constituents(INDEX, start_date=date_previous, end_date=date_previous)[0]['constituents'].keys()))
        except IndexError:
            code_list = w.wset("sectorconstituent", "date="+date_previous+";windcode="+INDEX).Data[1]
        strategy = STRATEGY(code_list, date_previous, 0.9)
        select_code_list = list_wind2jq(strategy.select_code())
        if len(select_code_list) > 0:  # 有可选股票时记录下可选股票
            stock_now = {}
            for code in select_code_list:
                stock_now[code] = 1.0 / len(select_code_list)
            position_target = stock_now
        else:
            position_target = {}

    # LLT择时判定
    if llt_value >= LLT_THRESHOLD and not position_now and position_target != {}:  # LLT择时信号为正,空仓且有目标持仓状态
        stock_dict[date_now] = position_target
        position_now = True
    elif llt_value < LLT_THRESHOLD and position_now and position_target != {}:  # LLT择时信号为负且持仓状态:
        stock_dict[date_now] = {}
        position_now = False


def on_backtest_finished(context, indicator):
    # 输出回测指标
    print(indicator)
    stock_json = json.dumps(stock_dict)
    stock_file = open('data\\stock_json.json', 'w')
    stock_file.write(stock_json)
    stock_file.close()


if __name__ == '__main__':
    run(strategy_id='4d2f6b1c-8f0a-11e8-af59-305a3a77b8c5',
        filename='master_strategy_backtest_select_time.py',
        mode=MODE_BACKTEST,
        token='d7b08e7e21dd0315a510926e5a53ade8c01f9aaa',
        backtest_initial_cash=10000000,
        backtest_adjust=ADJUST_PREV,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001,
        backtest_start_time=BACKTEST_START_DATE+' 09:00:00',
        backtest_end_time=BACKTEST_END_DATE+' 15:00:00')