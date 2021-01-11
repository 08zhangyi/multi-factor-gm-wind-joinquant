#!/usr/bin/env python
# coding:utf-8
from PoboAPI import *
import datetime
import time
import math
import numpy as np
from copy import *


#开始时间，用于初始化一些参数
def OnStart(context) :
    context.myacc = None
    context.code_main = '510050.SHSE'
    SubscribeQuote(context.code_main)
    context.offset_day = 1
    context.long_putopt_level = 1        #-1，-2，-3分别表示虚1，虚2，虚3；1，2，3表示实1，实2，实3，0表示平值合约
    context.short_putopt_level = -1
    #登录交易账号
    if context.accounts["回测期权"].Login() :
        context.myaccOPT = context.accounts["回测期权"]
    print('-'*50)

def GetDaystoExpire(op):
    info_op = GetContractInfo(op)
    kill_date = info_op['行权到期日']
    current_date = GetCurrentTime().date()
    d = GetTradingDates('SHSE', int(current_date.strftime('%Y%m%d')), int(kill_date.strftime('%Y%m%d')))
    n_days = len(d)-1  # 距离到期的时间
    return n_days

# 计算下单手数使用
def est_volume(context, asset_balance):
    last_date = GetPreviousTradingDate('SHFE',GetCurrentTradingDate('SHFE'))
    last_close = GetHisDataByField2(context.code_main, 'close', bar_type=BarType.Day,count = 1)[0]  # context传不进来
    separate_volume = math.floor(asset_balance/(last_close*10000)/2) * 8   # 双卖 每个期权下单数量
    return separate_volume
    

def OnMarketQuotationInitialEx(context, exchange,daynight):
    if exchange == 'SHFE' and daynight == 'day':
        context.myaccOPT.Logout()
        context.myaccOPT.Login()
        
        #获取合约
        day_last = GetOptionsLastDates(context.code_main)[0].strftime('%Y%m%d')
        day_now = GetCurrentTradingDate('SHSE').strftime('%Y%m%d')
        d = GetTradingDates('SHSE', int(day_now), int(day_last))
        if len(d) <= context.offset_day+2:
            context.long_putopt = GetAtmOptionContractByPos(context.code_main, "now", context.long_putopt_level, 1, 1)
            context.short_putopt = GetAtmOptionContractByPos(context.code_main, "now", context.short_putopt_level, 1, 1)
            context.optopenlist = [context.long_putopt, context.short_putopt]
        else:
            context.long_putopt = GetAtmOptionContractByPos(context.code_main, "now", context.long_putopt_level, 1, 0)
            context.short_putopt = GetAtmOptionContractByPos(context.code_main, "now", context.short_putopt_level, 1, 0)
            context.optopenlist = [context.long_putopt, context.short_putopt]
        print(GetContractInfo(context.long_putopt)['名称'], GetContractInfo(context.short_putopt)['名称'])
    
    
    #订阅日K线用来驱动onbar事件
    SubscribeQuote(context.code_main)
    
  
#在k线出现的时候，如果没持仓就卖开，如果有就平仓
def OnQuote(context, code):
    a = False
    # 先获取基本要素
    current_time= GetCurrentTime()
    code_price = GetQuote(context.code_main).now
    position_opt = context.myaccOPT.GetPositions()
    
    
    # 计算下单数量
    total_asset = context.myaccOPT.AccountBalance.DynamicNetAssets   # 返回值是int
    separate_volume = est_volume(context, total_asset)
    print(separate_volume)

    
    
    # 合约换月 先平昨仓
    if len(position_opt) != 0:
        opc = position_opt[0].contract
        kill_date = GetContractInfo(opc)['行权到期日']
        print('持仓的期权到期日为：'+str(kill_date))
        
        if GetDaystoExpire(opc) == context.offset_day:  # 距离期权到期日一定日期时，平仓操作
            # 平多仓
            long_OptclosePrice = GetQuote(position_opt[0].contract).now
            long_OptcloseVolume = position_opt[0].volume
            order_long_opt = context.myaccOPT.InsertOrder(position_opt[0].contract, BSType.SellClose, long_OptclosePrice, long_OptcloseVolume)
            order_long_opt = context.myaccOPT.InsertOrder(position_opt[0].contract, BSType.BuyClose, long_OptclosePrice, long_OptcloseVolume)
            # 平空仓
            short_OptclosePrice = GetQuote(position_opt[1].contract).now
            short_OptcloseVolume = position_opt[1].volume
            order_long_opt = context.myaccOPT.InsertOrder(position_opt[1].contract, BSType.SellClose, short_OptclosePrice, short_OptcloseVolume)
            order_long_opt = context.myaccOPT.InsertOrder(position_opt[1].contract, BSType.BuyClose, short_OptclosePrice, short_OptcloseVolume)
            a = True
            print(str(current_time)+'，期权临近到期，平仓操作')
    
    if len(position_opt) == 0 or a:
        # 开多仓
        longopt_price = GetQuote(str(context.optopenlist[0])).now
        order_long_opt = context.myaccOPT.InsertOrder(context.optopenlist[0], BSType.BuyOpen, longopt_price, separate_volume)
        # 开空仓
        shortopt_price = GetQuote(str(context.optopenlist[1])).now
        order_short_opt = context.myaccOPT.InsertOrder(context.optopenlist[1], BSType.SellOpen, shortopt_price, separate_volume)
        print(str(current_time)+'  开仓'+('-'*50))


    
    
    
    
    
    
    
    