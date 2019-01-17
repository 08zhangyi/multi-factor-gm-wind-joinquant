# 导入函数库
import jqdata
import json


# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')

    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之一，卖出时佣金万分之一加千分之零印花税, 每笔交易佣金最低扣1块钱
    set_order_cost(OrderCost(close_tax=0.0, open_commission=0.0001, close_commission=0.0001, min_commission=1),
                   type='stock')
    # 10:00:00定时运行
    run_daily(algo, '10:00:00')
    # run_daily(algo, 'open')


def algo(context):
    log.info('函数运行时间：' + str(context.current_dt))
    # 读取文件，获取调仓对应的字典
    # f = open(u'D:\\programs\\多因子策略开发\\掘金多因子开发测试\\AdaBoost选股策略\\data\\stock_json.json')
    # f = open(u'D:\programs\\多因子策略开发\\单因子研究\\单因子研究工具\\data\\stock_json.json')
    f = open(u'D:\\programs\\多因子策略开发\\掘金多因子开发测试\\大师选股策略\\data\\stock_json.json')
    json_string = f.read()
    f.close()
    stock_dict = json.loads(json_string)
    date_now = context.current_dt.strftime('%Y-%m-%d')
    if date_now in list(stock_dict.keys()):
        total_value = context.portfolio.total_value
        stocks_now_dict = stock_dict[date_now]
        stocks_target = list(stocks_now_dict.keys())
        if len(stocks_target) == 0:
            stocks_now = list(context.portfolio.long_positions.keys())
            for stock in stocks_now:
                order_target_value(stock, 0.0)
        else:
            stocks_now = list(context.portfolio.long_positions.keys())
            # 平仓，调仓，开仓
            stocks_close = list(set(stocks_now) - set(stocks_target))
            stocks_close.sort()
            stocks_adjust = list(set(stocks_now) - set(stocks_close))
            stocks_adjust.sort()
            stocks_open = list(set(stocks_target) - set(stocks_now))
            stocks_open.sort()

            for stock in stocks_close:
                order_target_value(stock, 0.0)
            for stock in stocks_adjust:
                order_target_value(stock, stocks_now_dict[stock] * total_value)
            for stock in stocks_open:
                order_target_value(stock, stocks_now_dict[stock] * total_value)

