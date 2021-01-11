#!/usr/bin/env python
# coding:utf-8
from PoboAPI import *
import datetime
import time
import numpy as np
from copy import *
import calendar
import math


# 开始时间，用于初始化一些参数
def OnStart(context) :
    # 初始化账户信息
    context.myacc = None
    context.myaccOPT = None
    context.myaccSTC = None
    # 投资品种代码设定
    context.code_main = "510050.SHSE" #证券品种为50ETF 
    # context.code_main = "510300.SHSE"
    # 设定期权和现货账户
    if "回测期权" in context.accounts :
        print("登录交易账号[回测期权]")
        if context.accounts["回测期权"].Login() :
            context.myaccOPT = context.accounts["回测期权"]
    if "回测证券" in context.accounts :
        print("登录交易账号[回测证券]")
        if context.accounts["回测证券"].Login() :
            context.myaccSTC = context.accounts["回测证券"]
    print('衍生品保证金初始值：%.2f' % context.myaccOPT.AccountBalance.AvailableMargin)
    print('证券可用资金初始值：%.2f' % context.myaccSTC.AccountBalance.AvailableCashBalance)
    print('-'*50)
    # offset_days为移仓提前日期
    context.offset_day = 1


# 一个工具函数，计算期权距离到期日还有几天，op为期权代码
def GetDaystoExpire(op):
    info_op = GetContractInfo(op)
    kill_date = info_op['行权到期日']
    current_date = GetCurrentTime().date()
    d = GetTradingDates('SHSE', int(current_date.strftime('%Y%m%d')), int(kill_date.strftime('%Y%m%d')))
    n_days = len(d)-1  # 距离到期的时间
    return n_days


# 每天行情初始化时，获取当前的code对应的平值期权
def OnMarketQuotationInitialEx(context, exchange, daynight):
    if exchange == 'SHFE' and daynight == 'day':
        context.myaccOPT.Logout()
        context.myaccOPT.Login()
        # 得到月末前到期合约列表
        context.oplist = GetOptionContracts(context.code_main, 0, 0)
        if context.oplist == []:
            context.oplist = GetOptionContracts(context.code_main, 1, 0)
        else:
            day_last = GetOptionsLastDates(context.code_main)[0].strftime('%Y%m%d')
            day_now = GetCurrentTradingDate('SHSE').strftime('%Y%m%d')
            d = GetTradingDates('SHSE', int(day_now), int(day_last))
            if len(d) <= context.offset_day+2:
                context.oplist = GetOptionContracts(context.code_main, 1, 0)
        print(context.oplist)
    #订阅日K线用来驱动onbar事件
    SubscribeQuote(context.code_main)


# 在k线出现的时候，如果没持仓就卖开，如果有就平仓
def OnQuote(context, code):
    a = False
    # 获取当前时间
    current_time= GetCurrentTime()
    buylist=[]
    code_price = GetQuote(context.code_main).now
    
    # 可用资金情况
    balOPT = context.myaccOPT.AccountBalance
    position_optmarginOPT = balOPT.AvailableCashBalance
    position_assetOPT = balOPT.AssetsBalance
    balSTC = context.myaccSTC.AccountBalance
    position_optmarginSTC = balSTC.AvailableCashBalance
    position_assetSTC = balSTC.AssetsBalance
    print('-'*50)
    print('期权保证金可用资金比例：%.4f%%' % (position_optmarginOPT/position_assetOPT*100.0)+'，现货可用资金比例：%.4f%%' % (position_optmarginSTC/position_assetSTC*100.0))
    
    # 打印现货和期权账户持仓情况
    position_opt = context.myaccOPT.GetPositions()
    position_code = context.myaccSTC.GetPositions()
    for pos_opt in position_opt:
        print('持有期权' + pos_opt.contract + '：' + str(pos_opt.volume) + '张')
    for pos_code in position_code:
        print('持有证券' + pos_code.contract + '：' + str(pos_code.volume) + '份')
        
    # 每天监测，有持仓是否要平仓
    if context.myaccOPT and context.myaccSTC and len(position_opt) != 0:
        opc = position_opt[0].contract
        kill_date = GetContractInfo(opc)['行权到期日']
        print('持仓的期权到期日为：'+str(kill_date))
        if GetDaystoExpire(opc) == context.offset_day:  # 距离期权到期日一定日期时，平仓操作
            for opt in position_opt:
                OptClosePrice = GetQuote(opt.contract).now
                OptCloseVolume = opt.volume
                order_opt = context.myaccOPT.InsertOrder(opt.contract, BSType.BuyClose, OptClosePrice, OptCloseVolume)
            codeVolume = position_code[0].volume
            order_code = context.myaccSTC.InsertOrder(context.code_main, BSType.SellClose, code_price, codeVolume)
            print(str(current_time)+'，期权临近到期，平仓操作')
            a = True

    position_opt = context.myaccOPT.GetPositions()
    # 无仓位时的操作
    if len(context.oplist)!=0 and (len(position_opt)==0 or a):
        for i in context.oplist:
            info1 = GetContractInfo(i)['行权到期日']
            info2 = GetContractInfo(i)['行权价格']
            ratio = info2/code_price  # K/S筛选合适的期权
            if ratio>0.9 and ratio<1.1:
                buylist.append(i)
        print('可选期权合约：'+str(buylist))
    # 无仓位时交易
    if len(buylist)!=0 and (len(position_opt)==0 or a):
        opc_number = len(buylist)
        v1 = math.floor((context.myaccSTC.AccountBalance.AvailableCashBalance)/code_price/10000/opc_number)
        v2 = v1*10000
        for opc in buylist:
            opc_price = GetQuote(opc).now
            #做空期权，做多50ETF
            s1 = context.myaccOPT.InsertOrder(opc, BSType.SellOpen,opc_price, v1)
            # print(s1,code_price)
            s2 = context.myaccSTC.InsertOrder(context.code_main, BSType.BuyOpen,code_price, v2)
        print(str(current_time)+'  开仓'+('-'*50))
    
