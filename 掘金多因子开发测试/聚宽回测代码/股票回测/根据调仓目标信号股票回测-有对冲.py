# 导入函数库
import jqdata
import json
import math


# 初始化函数，设定基准等等
def initialize(context):
    print(dir(math))
    # 设定沪深300作为基准
    set_benchmark('000001.XSHG')
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

    ### 股指期货相关设定 ###
    context.index_future = 'IF'  # 对冲品种的设置
    set_option('futures_margin_rate', 0.0000000000001)  # 期货合约保证金设置
    init_cash = context.portfolio.starting_cash
    # 账户1交易stock，账户2交易future，两个账户初始资金一致
    set_subportfolios([SubPortfolioConfig(cash=init_cash, type='stock'),
                       SubPortfolioConfig(cash=init_cash, type='futures')])
    index_information = {'IF': (300, '000300.XSHG'), 'IH': (300, '000016.XSHG'), 'IC': (200, '000905.XSHG')}  # 未完成
    context.index_information = index_information[context.index_future]
    # 确定对冲比例
    context.hedging_ratio = 1.0
    # 确定是否用股指期货对冲，1为开启对冲模式，2为开启择时对冲模式，0为无对冲基准模式
    context.hedging_mode = 1


def algo(context):
    log.info('函数运行时间：' + str(context.current_dt))
    # 读取文件，获取调仓对应的字典
    f = open(u'D:\\programs\\多因子策略开发\\掘金多因子开发测试\\大师选股策略\\data\\stock_json_LLT_10.json')
    json_string = f.read()
    f.close()
    stock_dict = json.loads(json_string)
    date_now = context.current_dt.strftime('%Y-%m-%d')
    if date_now in list(stock_dict.keys()):
        total_value = context.subportfolios[0].total_value  # 提取股票账户总资产值
        stocks_now_dict = stock_dict[date_now]
        stocks_target = list(stocks_now_dict.keys())
        if len(stocks_target) == 0:
            stocks_now = list(context.portfolio.long_positions.keys())
            for stock in stocks_now:
                order_target_value(stock, 0.0, pindex=0)
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
                order_target_value(stock, 0.0, pindex=0)
            for stock in stocks_adjust:
                order_target_value(stock, stocks_now_dict[stock] * total_value, pindex=0)
            for stock in stocks_open:
                order_target_value(stock, stocks_now_dict[stock] * total_value, pindex=0)

    # 股票建仓后进入期货调仓部分
    if context.hedging_mode == 1:  # 完全对冲的模式
        positions_value = context.subportfolios[0].positions_value  # 提取股票账户总股票市值
        current_data = get_current_data()
        index_price = current_data[context.index_information[1]].last_price
        contract_number = int(future_round(positions_value / (index_price * context.index_information[0])))
    elif context.hedging_mode == 2:  # 择时对冲的模式
        f = open(u'D:\\programs\\多因子策略开发\\掘金多因子开发测试\\大师选股策略\\data\\select_time_json.json')
        json_string = f.read()
        f.close()
        select_time_dict = json.loads(json_string)
        select_time_value = select_time_dict[context.current_dt.strftime('%Y-%m-%d')]
        if select_time_value == 1:  # 择时信号为正，不对冲
            contract_number = 0
        elif select_time_value == -1:  # 择时信号为负，对冲
            positions_value = context.subportfolios[0].positions_value  # 提取股票账户总股票市值
            current_data = get_current_data()
            index_price = current_data[context.index_information[1]].last_price
            contract_number = int(context.hedging_ratio*future_round(positions_value / (index_price * context.index_information[0])))
        else:  # 其他情况，暂时不对冲
            contract_number = 0
    else:  # 不对冲的基准模式
        contract_number = 0
    # 获取主力合约，并调仓
    main_contract = get_dominant_future(context.index_future, date=context.current_dt.strftime('%Y-%m-%d'))
    print(contract_number, main_contract, context.current_dt)
    if context.subportfolios[1].short_positions != {}:
        main_contract_pre = context.subportfolios[1].short_positions.keys()[0]
        if main_contract_pre != main_contract:  # 主力合约移仓
            for key in context.subportfolios[1].short_positions.keys():
                order_target(key, 0, side='short', pindex=1)
            order_target(main_contract, contract_number, side='short', pindex=1)
    else:
        order_target(main_contract, contract_number, side='short', pindex=1)


def future_round(number):
    # 根据目标手数取整的函数
    return round(number)

