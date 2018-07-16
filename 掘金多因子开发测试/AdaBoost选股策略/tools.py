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


def get_factor_from_wind(code_list, factor_list, factor_coeff_list, date):
    # 还需加入本地存储机制，本地有的数据可以加快读取
    w.start()
    code_list = list_gm2wind(code_list)  # code_list为gm中的格式
    factors = ','.join(factor_list)
    factors_coeffs = ','.join(factor_coeff_list)
    df_list = []
    for code in code_list:
        data_from_wind = w.wsd(code, factors, date, date, factors_coeffs)
        columns = data_from_wind.Fields
        index = [code]
        data = [[temp[0] for temp in data_from_wind.Data]]
        code_df = pd.DataFrame(data=data, index=index, columns=columns)
        df_list.append(code_df)
    df = pd.concat(df_list)
    return df


if __name__ == '__main__':
    print(get_trading_date_from_now('2018-06-17', 0))