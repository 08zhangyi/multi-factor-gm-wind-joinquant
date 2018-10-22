import datetime
from WindPy import w

financial_future = {'IF': 'IF.CFE', 'IH': 'IH.CFE', 'IC': 'IC.CFE'}
financial_index = {'IF': '000300.SH', 'IH': '000016.SH', 'IC': '000905.SH'}
financial_index_chinese = {'IF': '沪深300', 'IH': '上证50', 'IC': '中证500'}


def get_future_code(future, date):
    # 获取future在date日上市的期货代码
    w.start()
    code_data = w.wset("futurecc", "startdate="+date+";enddate="+date+";wind_code="+future).Data
    code_list = code_data[2]
    code_last_day_list = code_data[7]
    return code_list, code_last_day_list


def future_term_annualized(code_last_day_list, date):
    # 计算年化下期货距到期日的比例，一年为365日
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    days_delta_annualized = [((last_day - date).days/365.0) for last_day in code_last_day_list]
    return days_delta_annualized


def get_premium_future(future, code_list, date):
    pass



if __name__ == '__main__':
    code_list, code_last_day_list = get_future_code('IF.CFE', '2018-10-19')
    future_term_annualized(code_last_day_list, '2018-10-19')