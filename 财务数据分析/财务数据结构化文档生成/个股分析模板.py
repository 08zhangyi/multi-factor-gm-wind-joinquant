import numpy as np
import pandas as pd
import pygal
from WindPy import w
import tushare as ts
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
TS_TOKEN = '9668f6b57f4e3fe1199446a9c7b251d553963832bbf6e411b8065ea2'


class 个股分析模板():
    def __init__(self, code, date):
        w.start()
        self.code = code
        self.date = date
        self.code_name = w.wss(code, "sec_name").Data[0][0]

    def output(self):
        # 主体内容
        result = {'text': ''}
        return result

    @staticmethod
    def _get_last_year_end(date):
        year = int(date[0:4])
        month = int(date[5:7])
        season = (month-1) // 3
        if season == 0:
            last_year_end = str(year - 1)+'-12-31'
        elif season == 1:
            last_year_end = str(year) + '-03-31'
        elif season == 2:
            last_year_end = str(year) + '-06-30'
        else:
            last_year_end = str(year) + '-09-30'
        return last_year_end

    @staticmethod
    def tushare_date_format(date):
        date = ''.join(date.split('-'))
        return date


class 个股主营业务分析(个股分析模板):
    def output(self):
        pro = ts.pro_api(token=TS_TOKEN)
        date = self._get_last_year_end(self.date)
        df = pro.fina_mainbz(ts_code=self.code, period=self.tushare_date_format(date), type='P')
        for i in range(6):  # 取6个季度的数据
            if len(df) == 0:
                date = self._get_last_year_end(date)
                df = pro.fina_mainbz(ts_code=self.code, period=self.tushare_date_format(date), type='P')
        text = self.code_name + '（' + self.code + '）的主营业务构成为（数据截止为'+date+'）：\n'
        df = df.sort_values(by='bz_sales', axis=0, ascending=False)
        # 预处理，将None转化为np.nan
        df['bz_profit'] = pd.to_numeric(df['bz_profit'])
        df['bz_cost'] = pd.to_numeric(df['bz_cost'])
        # 计算辅助指标
        df['bz_ratio'] = df['bz_sales'] / np.sum(df['bz_sales'].values)  # 计算营业收入占比
        df['bz_profit_ratio'] = df['bz_profit'] / df['bz_sales']  # 计算毛利率
        # 文字生成部分
        for i in range(len(df)):
            data = df.iloc[i].values
            text_temp = '业务名称：%s，\t销售收入：%.2f，\t销售成本：%.2f，\t销售毛利：%.2f，\t销售毛利率：%.2f%%，\t销售收入占比：%.2f%%；\n'
            text_temp = text_temp % (data[2], data[3], data[5], data[4], data[8]*100.0, data[7]*100.0)
            text = text + text_temp
        # 画图部分
        pie_chart = pygal.Pie()
        pie_chart.title = self.code_name + '（' + self.code + '）的主营业务百分比构成图（数据截止为'+date+'）'
        for i in range(len(df)):
            data = df.iloc[i].values
            pie_chart.add(data[2], data[7]*100.0)
        # 结果展示
        print(text)
        pie_chart.render_to_file('output\\temp.svg')
        result = {'text': text, 'image': [pie_chart]}
        return result


if __name__ == '__main__':
    code = '600823.SH'
    date = '2019-03-26'
    model = 个股主营业务分析(code, date)
    model.output()
