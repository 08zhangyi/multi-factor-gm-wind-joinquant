# 自己使用的工具函数类
import QuantLib as ql
import pandas as pd
from WindPy import w
import os
import datetime

# 申万1级行业列表
SW1_INDEX = [['801010.SI', '农林牧渔'], ['801020.SI', '采掘'], ['801030.SI', '化工'], ['801040.SI', '钢铁'], ['801050.SI', '有色金属'],
             ['801080.SI', '电子'], ['801110.SI', '家用电器'], ['801120.SI', '食品饮料'], ['801130.SI', '纺织服装'], ['801140.SI', '轻工制造'],
             ['801150.SI', '医药生物'], ['801160.SI', '公用事业'], ['801170.SI', '交通运输'], ['801180.SI', '房地产'], ['801200.SI', '商业贸易'],
             ['801210.SI', '休闲服务'], ['801230.SI', '综合'], ['801710.SI', '建筑材料'], ['801720.SI', '建筑装饰'], ['801730.SI', '电气设备'],
             ['801740.SI', '国防军工'], ['801750.SI', '计算机'], ['801760.SI', '传媒'], ['801770.SI', '通信'], ['801780.SI', '银行'],
             ['801790.SI', '非银金融'], ['801880.SI', '汽车'], ['801890.SI', '机械设备']]


# 计算不同交易日的函数
def get_trading_date_from_now(date_now, diff_periods, period=ql.Days):
    always_using_ql = False  # 是否全部使用quantlib处理日期，否则只在某些情形使用quantlib处理日期
    if (int(date_now.split('-')[0]) <= 2019 and int(date_now.split('-')[1]) <= 9 and diff_periods <= 1) or (int(date_now.split('-')[0]) <= 2018 and diff_periods <= 1) or always_using_ql:
        calculation_date = ql.Date(int(date_now.split('-')[2]), int(date_now.split('-')[1]),
                                   int(date_now.split('-')[0]))
        calendar = ql.China()
        date_diff = calendar.advance(calculation_date, diff_periods, period).to_date().strftime('%Y-%m-%d')
    else:  # 其余日子用wind处理
        if period==ql.Days:
            w.start()
            date_diff = w.tdaysoffset(diff_periods, date_now, '').Data[0][0].strftime('%Y-%m-%d')
            if diff_periods == 0:  # 非交易日顺延到下一个交易日
                date_now_date = datetime.date.fromisoformat(date_now)
                date_diff_date = datetime.date.fromisoformat(date_diff)
                if date_diff_date < date_now_date:
                    date_diff = w.tdaysoffset(1, date_now, '').Data[0][0].strftime('%Y-%m-%d')
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
def get_factor_from_wind_without_cache(code_list, factor_list, date):
    # 用单因子研究\single_factor.py中的因子类直接获取数据
    factors_dfs = []
    for factor in factor_list:
        factor_df = factor(date, code_list).get_factor()
        factors_dfs.append(factor_df)
    factors_df = pd.concat(factors_dfs, axis=1)
    return factors_df


# 有缓存版本
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


# 获取股票列表的申万一级代码
def get_SW1_industry(date, code_list):
    w.start()
    sw1_industry = w.wss(code_list, "indexcode_sw", "tradeDate=" + date + ";industryType=1").Data[0]
    sw1_result = {}
    for i, code in enumerate(code_list):
        sw1_result[code] = sw1_industry[i]
    return sw1_result


# 每月根据日期整理交易日列表
def get_trading_date_list_by_day_monthly(BACKTEST_START_DATE, BACKTEST_END_DATE, TRADING_DATES_LIST):
    trading_date_list = []  # 记录备选交易日列表
    w.start()
    date_to_be_selected = w.tdays(BACKTEST_START_DATE, BACKTEST_END_DATE, "").Data[0]  # 获取交易日列表
    date_to_be_selected = [d.strftime('%Y-%m-%d') for d in date_to_be_selected]
    i = 0
    while True:
        print('处理日期：' + str(i))
        date_now = date_to_be_selected[i]
        dates_trading = [get_trading_date_from_now(date_now.split('-')[0] + '-' + date_now.split('-')[1] + '-' + TRADING_DATE, 0, ql.Days)
                         for TRADING_DATE in TRADING_DATES_LIST]
        if date_now in dates_trading:
            trading_date_list.append(date_now)
        i += 1
        if date_now == BACKTEST_END_DATE:
            break
    return trading_date_list


# 根据月份日期整理交易日列表
def get_trading_date_list_by_month_by_day(BACKTEST_START_DATE, BACKTEST_END_DATE, MONTHS, TRADING_DATES_LIST):
    trading_date_list = []  # 记录备选交易日列表
    w.start()
    date_to_be_selected = w.tdays(BACKTEST_START_DATE, BACKTEST_END_DATE, "").Data[0]  # 获取交易日列表
    date_to_be_selected = [d.strftime('%Y-%m-%d') for d in date_to_be_selected]
    i = 0
    print('回测开始日期：' + BACKTEST_START_DATE + '，结束日期：' + BACKTEST_END_DATE)
    while True:
        print('处理日期：' + str(i))
        date_now = date_to_be_selected[i]
        dates_trading = [get_trading_date_from_now(date_now.split('-')[0] + '-' + date_now.split('-')[1] + '-' + TRADING_DATE, 0, ql.Days)
                         for TRADING_DATE in TRADING_DATES_LIST]
        if date_now in dates_trading:
            trading_date_list.append(date_now)
        i += 1
        if date_now == BACKTEST_END_DATE:
            break
    trading_date_list = [d for d in trading_date_list if d.split('-')[1] in MONTHS]  # 按照选定的调仓月份进行筛选
    return trading_date_list


if __name__ == '__main__':
    print(get_trading_date_from_now('2019-01-05', 0))