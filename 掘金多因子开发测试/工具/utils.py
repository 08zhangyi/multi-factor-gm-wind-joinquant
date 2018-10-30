# 自己使用的工具函数类
import QuantLib as ql
import pandas as pd
from WindPy import w
import os
import numpy as np
import jqdatasdk
from sqlalchemy.orm.query import Query

# 申万1级行业列表
SW1_INDEX = [['801010.SI', '农林牧渔'], ['801020.SI', '采掘'], ['801030.SI', '化工'], ['801040.SI', '钢铁'], ['801050.SI', '有色金属'],
             ['801080.SI', '电子'], ['801110.SI', '家用电器'], ['801120.SI', '食品饮料'], ['801130.SI', '纺织服装'], ['801140.SI', '轻工制造'],
             ['801150.SI', '医药生物'], ['801160.SI', '公用事业'], ['801170.SI', '交通运输'], ['801180.SI', '房地产'], ['801200.SI', '商业贸易'],
             ['801210.SI', '休闲服务'], ['801230.SI', '综合'], ['801710.SI', '建筑材料'], ['801720.SI', '建筑装饰'], ['801730.SI', '电气设备'],
             ['801740.SI', '国防军工'], ['801750.SI', '计算机'], ['801760.SI', '传媒'], ['801770.SI', '通信'], ['801780.SI', '银行'],
             ['801790.SI', '非银金融'], ['801880.SI', '汽车'], ['801890.SI', '机械设备']]


# 计算不同交易日的函数
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


def list_jq2wind(list_jq):
    jq2wind_dict = {'XSHG': 'SH', 'XSHE': 'SZ', 'CCFX': 'CFE', 'XSGE': 'SHF', 'XDCE': 'DCE', 'XZCE': 'CZC', 'XINE': 'INE'}
    list_wind = [temp.split('.')[0] + '.' + jq2wind_dict[temp.split('.')[1]] for temp in list_jq]
    return list_wind


# 有缓存版本
def get_factor_from_wind(code_list, factor_list, date):
    # 用单因子研究\single_factor.py中的因子类直接获取数据
    file_path = 'data_cache\\factor_' + date + '.csv'
    if os.path.exists(file_path):  # 使用缓存中数据减少数据交互，加快读取速度
        factors_df = pd.read_csv(file_path, index_col=0)
    else:
        factors_dfs = []
        for factor in factor_list:
            factor_df = factor(date, code_list).get_factor()
            factors_dfs.append(factor_df)
        factors_df = pd.concat(factors_dfs, axis=1)
        factors_df.to_csv(file_path, encoding='utf-8')
    return factors_df


# 无缓存版本
def get_factor_from_wind_v2(code_list, factor_list, date):
    # 用单因子研究\single_factor.py中的因子类直接获取数据
    file_path = 'data_cache\\factor_' + date + '.csv'
    if os.path.exists(file_path):
        factors_df = pd.read_csv(file_path, index_col=0)
    else:
        factors_dfs = []
        for factor in factor_list:
            factor_df = factor(date, code_list).get_factor()
            factors_dfs.append(factor_df)
        factors_df = pd.concat(factors_dfs, axis=1)
    return factors_df


def get_return_from_wind(code_list, date_start, date_end):
    # 从wind上获待选股票收益率数据，为百分比数据，如：3代表3%
    file_path = 'data_cache\\return_' + date_start + '_' + date_end + '.csv'
    if os.path.exists(file_path):  # 使用缓存中数据减少数据交互，加快读取速度
        return_df = pd.read_csv(file_path, index_col=0)
    else:
        w.start()
        date_start = get_trading_date_from_now(date_start, 1, ql.Days)
        return_data = w.wss(code_list, "pct_chg_per", "startDate="+date_start+";endDate="+date_end).Data[0]
        return_df = pd.DataFrame(data=return_data, index=code_list, columns=['return'])
        return_df.to_csv(file_path, encoding='utf-8')
    return return_df


def delete_data_cache():
    # 删除data_cache中的数据缓存
    for i in os.listdir('data_cache'):
        path_file = os.path.join('data_cache', i)
        os.remove(path_file)


def sort_data(df):
    # 用排序值对数据进行标准化
    value = np.argsort(np.argsort(df.values, axis=0), axis=0) / (len(df)-1)  # 转化为0-1的排序值
    df = pd.DataFrame(data=value, columns=df.columns, index=df.index)
    return df


# 获取股票列表的申万一级代码
def get_SW1_industry(date, code_list):
    w.start()
    sw1_industry = w.wss(code_list, "indexcode_sw", "tradeDate=" + date + ";industryType=1").Data[0]
    sw1_result = {}
    for i, code in enumerate(code_list):
        sw1_result[code] = sw1_industry[i]
    return sw1_result


if __name__ == '__main__':
    print(get_SW1_industry('2016-12-29', ['600649.SH']))