# 自己使用的工具函数类
import QuantLib as ql
import pandas as pd
from WindPy import w
import os
import datetime

# 申万1级行业列表
SW1_INDEX = [['801010.SI', '农林牧渔'], ['801020.SI', '采掘'], ['801030.SI', '化工'], ['801040.SI', '钢铁'],
             ['801050.SI', '有色金属'], ['801080.SI', '电子'], ['801110.SI', '家用电器'], ['801120.SI', '食品饮料'],
             ['801130.SI', '纺织服装'], ['801140.SI', '轻工制造'], ['801150.SI', '医药生物'], ['801160.SI', '公用事业'],
             ['801170.SI', '交通运输'], ['801180.SI', '房地产'], ['801200.SI', '商业贸易'], ['801210.SI', '休闲服务'],
             ['801230.SI', '综合'], ['801710.SI', '建筑材料'], ['801720.SI', '建筑装饰'], ['801730.SI', '电气设备'],
             ['801740.SI', '国防军工'], ['801750.SI', '计算机'], ['801760.SI', '传媒'], ['801770.SI', '通信'],
             ['801780.SI', '银行'], ['801790.SI', '非银金融'], ['801880.SI', '汽车'], ['801890.SI', '机械设备']]
# 中信1级行业列表
ZX1_INDEX = [['CI005001.WI', '石油石化'], ['CI005002.WI', '煤炭'], ['CI005003.WI', '有色金属'], ['CI005004.WI', '电力及公用事业'],
             ['CI005005.WI', '钢铁'], ['CI005006.WI', '基础化工'], ['CI005007.WI', '建筑'], ['CI005008.WI', '建材'],
             ['CI005009.WI', '轻工制造'], ['CI005010.WI', '机械'], ['CI005011.WI', '电力设备及新能源'], ['CI005012.WI', '国防军工'],
             ['CI005013.WI', '汽车'], ['CI005014.WI', '商贸零售'], ['CI005015.WI', '消费者服务'], ['CI005016.WI', '家电'],
             ['CI005017.WI', '纺织服装'], ['CI005018.WI', '医药'], ['CI005019.WI', '食品饮料'], ['CI005020.WI', '农林牧渔'],
             ['CI005021.WI', '银行'], ['CI005022.WI', '非银行金融'], ['CI005023.WI', '房地产'], ['CI005024.WI', '交通运输'],
             ['CI005025.WI', '电子'], ['CI005026.WI', '通信'], ['CI005027.WI', '计算机'], ['CI005028.WI', '传媒'],
             ['CI005029.WI', '综合'], ['CI005030.WI', '综合金融']]


# 计算不同交易日的函数
def get_trading_date_from_now(date_now, diff_periods, period=ql.Days):
    if period==ql.Months:
        w.start()
        date_diff = w.tdaysoffset(diff_periods, date_now, 'Period=M').Data[0][0].strftime('%Y-%m-%d')
        if diff_periods == 0:  # 非交易日顺延到下一个交易日
            date_now_date = datetime.date.fromisoformat(date_now)
            date_diff_date = datetime.date.fromisoformat(date_diff)
            if date_diff_date < date_now_date:
                date_diff = w.tdaysoffset(1, date_now, '').Data[0][0].strftime('%Y-%m-%d')
    else:  # 默认以日为单位进行调整
        w.start()
        date_diff = w.tdaysoffset(diff_periods, date_now, '').Data[0][0].strftime('%Y-%m-%d')
        if diff_periods == 0:  # 非交易日顺延到下一个交易日
            date_now_date = datetime.date.fromisoformat(date_now)
            date_diff_date = datetime.date.fromisoformat(date_diff)
            if date_diff_date < date_now_date:
                date_diff = w.tdaysoffset(1, date_now, '').Data[0][0].strftime('%Y-%m-%d')
    return date_diff


# 获取两个日期之间的所有交易日，包括头尾交易日
def get_trading_days_from_start_to_end(start_day, end_day):
    w.start()
    days = w.tdays(start_day, end_day, "").Data[0]
    days = [d.strftime('%Y-%m-%d') for d in days]
    return days


# 获取两个日期之间的所有调仓日，包括头尾交易日
# fixing_days可以为月中的几个调仓日
def get_fix_trading_days_from_start_to_end_monthly(start_day, end_day, fixing_days):
    start_day = datetime.datetime.strptime(start_day, '%Y-%m-%d')
    end_day = datetime.datetime.strptime(end_day, '%Y-%m-%d')
    trading_days_all = []
    for fixing_day in fixing_days:  # 按fixing_day选取调仓日
        months = (end_day.year - start_day.year) * 12 + end_day.month - start_day.month
        trading_days = ['%04d-%02d-%02d' % (start_day.year + mon // 12, mon % 12 + 1, int(fixing_day))
                        for mon in range(start_day.month - 1, start_day.month + months)]
        trading_days = [get_trading_date_from_now(d, 0) for d in trading_days]
        trading_days_all += trading_days
    trading_days_all = list(set(trading_days_all))  # 去重
    trading_days_all = sorted([datetime.datetime.strptime(d, '%Y-%m-%d') for d in trading_days_all])  # 重新排序
    trading_days_all = [d.strftime('%Y-%m-%d') for d in trading_days_all if d >= start_day and d <= end_day]
    return trading_days_all


def list_gm2wind(list_gm):
    gm2wind_dict = {'SHSE': 'SH', 'SZSE': 'SZ', 'CFFEX': 'CFE', 'SHFE': 'SHF', 'DCE': 'DCE', 'CZCE': 'CZC', 'INE': 'INE', 'CSI': 'CSI'}
    list_wind = [temp.split('.')[1]+'.'+gm2wind_dict[temp.split('.')[0]] for temp in list_gm]
    return list_wind


def list_wind2gm(list_wind):
    wind2gm_dict = {'SH': 'SHSE', 'SZ': 'SZSE', 'CFE': 'CFFEX', 'SHF': 'SHFE', 'DCE': 'DCE', 'CZC': 'CZCE', 'INE': 'INE', 'CSI': 'CSI'}
    list_gm = [wind2gm_dict[temp.split('.')[1]]+'.'+temp.split('.')[0] for temp in list_wind]
    return list_gm


def list_wind2jq(list_wind):
    wind2jq_dict = {'SH': 'XSHG', 'SZ': 'XSHE', 'CFE': 'CCFX', 'SHF': 'XSGE', 'DCE': 'XDCE', 'CZC': 'XZCE', 'INE': 'XINE', 'CSI': 'CSI'}
    list_jq = [temp.split('.')[0] + '.' + wind2jq_dict[temp.split('.')[1]] for temp in list_wind]
    return list_jq


def list_jq2wind(list_jq):
    jq2wind_dict = {'XSHG': 'SH', 'XSHE': 'SZ', 'CCFX': 'CFE', 'XSGE': 'SHF', 'XDCE': 'DCE', 'XZCE': 'CZC', 'XINE': 'INE', 'CSI': 'CSI'}
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
    # print(get_trading_date_from_now('2021-04-08', 0))
    # print(get_trading_date_from_now('2021-04-18', 0))
    # print(get_trading_date_from_now('2021-02-30', 0))
    print(get_fix_trading_days_from_start_to_end_monthly('2020-03-22', '2021-04-18', ['5', '10']))
