import datetime
from WindPy import w
import numpy as np

financial_future = {'IF': 'IF.CFE', 'IH': 'IH.CFE', 'IC': 'IC.CFE'}
financial_index = {'IF': '000300.SH', 'IH': '000016.SH', 'IC': '000905.SH'}
financial_index_chinese = {'IF': '沪深300', 'IH': '上证50', 'IC': '中证500'}


def get_future_code(future, date):
    # 获取future在date日上市的期货代码
    w.start()
    code_data = w.wset("futurecc", "startdate="+date+";enddate="+date+";wind_code="+financial_future[future]).Data
    code_list = code_data[2]
    code_last_day_list = code_data[7]
    return code_list, code_last_day_list


def future_term_annualized(code_last_day_list, date):
    # 计算年化下期货距到期日的比例，一年为365日
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    days_delta_annualized = [((last_day - date).days/365.0) for last_day in code_last_day_list]
    return days_delta_annualized


def get_premium_future_from_code_list(future, code_list, days_delta_annualized, date):
    w.start()
    index_data = w.wss(financial_index[future], "close", "tradeDate="+date+";priceAdj=U;cycle=D").Data[0][0]
    future_data = w.wss(code_list, "close", "tradeDate="+date+";priceAdj=U;cycle=D").Data[0]
    open_interest = np.array(w.wss(code_list, "oi", "tradeDate=" + date + ";priceAdj=U;cycle=D").Data[0])
    premium = np.array([(data - index_data)/index_data for data in future_data])
    days_delta_annualized = np.array([1.0/data if data != 0.0 else 0.0 for data in days_delta_annualized])
    # 按持仓量计算年化升贴水比例，负值为期货贴水，正值为期货升水
    open_interest = open_interest / np.sum(open_interest)
    ratio = np.sum((premium * days_delta_annualized) * open_interest)
    return ratio


def get_premium_future_from(future, date):
    print('获取'+future+'的第'+date+'日数据')
    code_list, code_last_day_list = get_future_code(future, date)
    days_delta_annualized = future_term_annualized(code_last_day_list, date)
    ratio = get_premium_future_from_code_list(future, code_list, days_delta_annualized, date)
    return ratio


if __name__ == '__main__':
    print(get_premium_future_from('IH', '2018-09-03'))