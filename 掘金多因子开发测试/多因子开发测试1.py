from gm.api import *
from tools import get_trading_date_from_now

# 回测的基本参数的设定
BACKTEST_START_DATE = '2017-02-27'  # 回测开始日期
BACKTEST_END_DATE = '2018-06-20'  # 回测结束日期，测试结束日期不运用算法
INDEX = 'SHSE.000016'  # 股票池代码
FACTOR_LIST = []  # 需要获取的因子列表
TRADING_DATE = '10'  # 每月的调仓日期，非交易日去下一个最近的交易日


def init(context):
    # 按照回测的将股票池的历史股票组成提出并合并
    history_constituents = get_history_constituents(INDEX, start_date=BACKTEST_START_DATE, end_date=BACKTEST_END_DATE)
    history_constituents = [set(temp['constituents'].keys()) for temp in history_constituents]
    history_constituents_all = set()
    for temp in history_constituents:
        history_constituents_all = history_constituents_all | temp
    history_constituents_all = list(history_constituents_all)
    # print(len(history_constituents_all))
    # 根据板块的历史数据组成订阅数据
    subscribe(symbols=history_constituents_all, frequency='1d')
    # 每天10:00:00定时执行algo任务
    schedule(schedule_func=algo, date_rule='daily', time_rule='10:00:00')


def algo(context):
    date_now = context.now.strftime('%Y-%m-%d')
    date_previous = get_trading_date_from_now(date_now, -1)  # 前一个交易日，用于获取因子数据的日期
    date_trading = get_trading_date_from_now(date_now.split('-')[0]+'-'+date_now.split('-')[1]+'-'+TRADING_DATE, 0)  # 调仓日期，判断是否调仓
    if date_now != date_trading:  # 非调仓日
        pass
    else:  # 调仓日执行算法
        constituents = get_history_constituents(INDEX, start_date=date_now, end_date=date_now)[0]['constituents'].keys()
        constituents = list(constituents)
        print(date_now, date_trading)


def on_backtest_finished(context, indicator):
    print(indicator)


if __name__ == '__main__':
    run(strategy_id='efed2881-7511-11e8-8fe1-305a3a77b8c5',
        filename='多因子开发测试1.py',
        mode=MODE_BACKTEST,
        token='d7b08e7e21dd0315a510926e5a53ade8c01f9aaa',
        backtest_start_time=BACKTEST_START_DATE+' 13:00:00',
        backtest_end_time=BACKTEST_END_DATE+' 13:00:00')