from gm.api import *


def init(context):
    # 每天14:50 定时执行algo任务
    schedule(schedule_func=algo, date_rule='daily', time_rule='14:50:00')


def algo(context):
    # 购买200股浦发银行股票
    order_volume(symbol='SHSE.600000', volume=200, side=1,
                 order_type=2, position_effect=1, price=0)


# 查看最终的回测结果
def on_backtest_finished(context, indicator):
    print(indicator)
    print(context.symbols)  # 订阅代码的集合
    print(context.now)  # 当前的时间
    print(context.account())  # 获取账户当前状态
    print(context.parameters)  # 获取动态参数

    account = context.account()
    print(account.positions())
    print(account.cash)


if __name__ == '__main__':
    run(strategy_id='b6e2e413-88c6-11e8-af77-305a3a77b8c5',
        filename='每日定时下单的策略.py',
        mode=MODE_BACKTEST,
        token='d7b08e7e21dd0315a510926e5a53ade8c01f9aaa',
        backtest_start_time='2016-06-17 13:00:00',
        backtest_end_time='2017-08-21 15:00:00',
        backtest_initial_cash=10000000,  # 回测的初始资金大小
        backtest_adjust=ADJUST_PREV,  # 采用前复权方式
        backtest_commission_ratio=0.0001,  # 回测佣金比例
        backtest_slippage_ratio=0.0001,  # 回测滑点比例
        )