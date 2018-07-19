# 自己使用的工具函数类
import QuantLib as ql
import pandas as pd
from WindPy import w


def get_trading_date_from_now(date_now, diff_periods, period=ql.Days):
    calculation_date = ql.Date(int(date_now.split('-')[2]), int(date_now.split('-')[1]), int(date_now.split('-')[0]))
    calendar = ql.China()
    date_diff = calendar.advance(calculation_date, diff_periods, period).to_date().strftime('%Y-%m-%d')
    return date_diff


def list_gm2wind(list_gm):
    gm2wind_dict = {'SHSE': 'SH', 'SZSE': 'SZ', 'CFFEX': 'CFE', 'SHFE': 'SHF', 'DCE': 'DCE', 'CZCE': 'CZC', 'INE': 'INE'}
    list_wind = [temp.split('.')[1]+'.'+gm2wind_dict[temp.split('.')[0]] for temp in list_gm]
    return list_wind


def list_wind2gm(list_wind):
    wind2gm_dict = {'SH': 'SHSE', 'SZ': 'SZSE', 'CFE': 'CFFEX', 'SHF': 'SHFE', 'DCE': 'DCE', 'CZC': 'CZCE', 'INE': 'INE'}
    list_gm = [wind2gm_dict[temp.split('.')[1]]+'.'+temp.split('.')[0] for temp in list_wind]
    return list_gm


def get_factor_from_wind(code_list, factor_list, date):
    # 还需加入本地存储机制，本地有的数据可以加快读取
    # 用单因子研究中的模块直接读取数据
    pass


def get_return_from_wind(code_list, date_start, date_end):
    # 从wind上获持仓收益率数据
    pass


if __name__ == '__main__':
    print(get_trading_date_from_now('2018-06-17', 0))