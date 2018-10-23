from WindPy import w
import xlwt
from 基本工具 import get_premium_future_from, financial_index, financial_index_chinese


def future_premium_list(future, start_date, end_date):
    # 计算时间序列下的期货升贴水指数
    w.start()
    index = financial_index[future]
    data = w.wsd(index, "close", start_date, end_date, "")
    date_list = data.Times
    premium_list = [get_premium_future_from(future, d.strftime('%Y-%m-%d')) for d in date_list]
    index_list = data.Data[0]
    return date_list, premium_list, index_list


def future_premium_list_to_excel(future, start_date, end_date, file_name='data\\data'):
    file = xlwt.Workbook(encoding='utf-8')
    table = file.add_sheet('data')
    date_list, premium_list, index_list = future_premium_list(future, start_date, end_date)
    for i in range(len(date_list)+1):
        if i == 0:
            table.write(i, 0, '日期')
            table.write(i, 1, '升贴水指数')
            table.write(i, 2, financial_index_chinese[future]+'指数')
        else:
            table.write(i, 0, date_list[i-1].strftime('%Y-%m-%d'))
            table.write(i, 1, '%.8f' % premium_list[i-1])
            table.write(i, 2, '%.2f' % index_list[i-1])
    file.save(file_name+'.xls')


if __name__ == '__main__':
    future_premium_list_to_excel('IC', '2015-04-22', '2018-10-22')