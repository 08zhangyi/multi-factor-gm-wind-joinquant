# 自己使用的工具函数类
import QuantLib as ql


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


def list_wind2jq(list_wind):
    wind2jq_dict = {'SH': 'XSHG', 'SZ': 'XSHE', 'CFE': 'CCFX', 'SHF': 'XSGE', 'DCE': 'XDCE', 'CZC': 'XZCE', 'INE': 'XINE'}
    list_jq = [temp.split('.')[0] + '.' + wind2jq_dict[temp.split('.')[1]] for temp in list_wind]
    return list_jq
