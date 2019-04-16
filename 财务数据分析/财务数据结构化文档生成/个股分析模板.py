import numpy as np
import pandas as pd
import pygal
from WindPy import w
import tushare as ts
import prettytable
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
TS_TOKEN = 'fcd3ee99a7d5f0e27c546d074a001f0b3eae01312c4dd8354415fba1'


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
    def _get_last_season_end(date):
        year = int(date[0:4])
        month = int(date[5:7])
        season = (month-1) // 3
        if season == 0:
            last_season_end = str(year - 1)+'-12-31'
        elif season == 1:
            last_season_end = str(year) + '-03-31'
        elif season == 2:
            last_season_end = str(year) + '-06-30'
        else:
            last_season_end = str(year) + '-09-30'
        return last_season_end

    @staticmethod
    def _get_last_year_end(date):
        year = int(date[0:4])
        last_year_end = str(year - 1) + '-12-31'
        return last_year_end

    @staticmethod
    def _get_last_year_date(date):
        year = int(date[0:4])
        last_year_date = str(year - 1) + date[4:]
        return last_year_date

    @staticmethod
    def tushare_date_format(date):
        date = ''.join(date.split('-'))
        return date


class 个股主营业务分析_按产品(个股分析模板):
    def output(self):
        pro = ts.pro_api(token=TS_TOKEN)
        date = self._get_last_season_end(self.date)
        df = pro.fina_mainbz(ts_code=self.code, period=self.tushare_date_format(date), type='P')
        for i in range(5):  # 最多尝试取6个季度的数据
            if len(df) == 0:
                date = self._get_last_season_end(date)
                df = pro.fina_mainbz(ts_code=self.code, period=self.tushare_date_format(date), type='P')
        text = self.code_name + '（' + self.code + '）的主营业务构成为（数据截止为'+date+'）：\n'
        df = df.sort_values(by='bz_sales', axis=0, ascending=False)
        # 预处理，将None转化为np.nan
        df['bz_profit'] = pd.to_numeric(df['bz_profit'])
        df['bz_cost'] = pd.to_numeric(df['bz_cost'])
        # 计算辅助指标
        df['bz_sales_ratio'] = df['bz_sales'] / np.sum(df['bz_sales'].fillna(0.0).values)  # 计算营业收入占比
        df['bz_profit_ratio'] = df['bz_profit'] / df['bz_sales']  # 计算毛利率
        # 文字生成部分
        table = prettytable.PrettyTable(['业务名称', '销售收入', '销售成本', '销售毛利', '销售毛利率', '销售收入占比'])
        for i in range(len(df)):
            data = df.iloc[i].values
            table.add_row(['%s' % data[2], '%.2f万元' % (data[3]/10000.0), '%.2f万元' % (data[5]/10000.0), '%.2f万元' % (data[4]/10000.0), '%.2f%%' % (data[8]*100.0), '%.2f%%' % (data[7]*100.0)])
        text = text + str(table) + '\n'
        # 画图部分
        pie_chart = pygal.Pie()
        pie_chart.title = self.code_name + '（' + self.code + '）的主营业务百分比构成图（数据截止为'+date+'）'
        for i in range(len(df)):
            data = df.iloc[i].values
            pie_chart.add(data[2], data[7]*100.0)
        # 总结内容
        if len(df) > 0:
            summary_text = self._get_summary(df, self.code_name)
            text = text + summary_text
        else:  # 无数据披露的情形
            text = text + '无数据！\n'
        # 结果展示
        print(text)
        pie_chart.render_to_file('output\\temp.svg')
        result = {'text': text, 'image': [pie_chart]}
        return result

    @staticmethod
    def _get_summary(df, code_name):
        bz_item = df['bz_item'].values
        bz_sales_ratio = df['bz_sales_ratio'].values
        bz_sales_ratio_cumsum = np.cumsum(bz_sales_ratio)
        first_bigger_index = int(np.where(bz_sales_ratio_cumsum > 0.90)[0][0])  # 第一个求和大于90%的指标，包括指标本身，为主要业务
        text = code_name + '的主要业务有：'
        for i in range(first_bigger_index+1):
            text = text + bz_item[i]
            if i == first_bigger_index:
                text = text + '；\n'
            else:
                text = text + '，'
        bz_sales_ratio_main = bz_sales_ratio[:first_bigger_index+1]  # 主要业务比例列表
        bz_sales_ratio_main = bz_sales_ratio_main / bz_sales_ratio_main[0]
        bz_sales_ratio_core = np.where(bz_sales_ratio_main > 0.5)[0]  # 核心业务指标
        bz_sales_ratio_aux = np.where((bz_sales_ratio_main <= 0.5) & (bz_sales_ratio_main > 0.2))[0]  # 辅助业务指标
        bz_sales_ratio_supple = np.where(bz_sales_ratio_main <= 0.2)[0]  # 补充业务指标
        text = text + '其中'
        for i in bz_sales_ratio_core:
            text = text + bz_item[i] + '、'
        text = text[:-1] + '是核心业务成分；'
        for i in bz_sales_ratio_aux:
            text = text + bz_item[i] + '、'
        text = text[:-1] + '是辅助业务成分；'
        for i in bz_sales_ratio_supple:
            text = text + bz_item[i] + '、'
        text = text[:-1] + '是补充业务成分；'
        text = text[:-1] + '。\n'
        if len(bz_sales_ratio_core) > 3:
            text = text + code_name + '的业务非常多元化，无明显主营业务'
        elif len(bz_sales_ratio_core) == 3:
            text = text + code_name + '的业务比较多元化，属于三核心业务类型'
        elif len(bz_sales_ratio_core) == 2:
            text = text + code_name + '的业务双核心特征明显，属于双核心业务类型'
        else:
            text = text + code_name + '的业务核心业务突出，属于单核心业务类型'
        if len(bz_sales_ratio_aux) > 3:
            text = text + '，同时公司具有较多的辅助业务'
        elif len(bz_sales_ratio_aux) > 0 and len(bz_sales_ratio_aux) < 3:
            text = text + '，同时公司具有一定的辅助业务'
        else:
            text = text + '，同时公司无辅助业务'
        if len(bz_sales_ratio_supple) > 3:
            text = text + '，具有较多的补充业务'
        elif len(bz_sales_ratio_supple) > 0 and len(bz_sales_ratio_supple) < 3:
            text = text + '，具有一定的补充业务'
        else:
            text = text + '，无补充业务'
        text = text + '。\n'
        return text


class 个股主营业务分析_按地区(个股分析模板):
    def output(self):
        pro = ts.pro_api(token=TS_TOKEN)
        date = self._get_last_season_end(self.date)
        df = pro.fina_mainbz(ts_code=self.code, period=self.tushare_date_format(date), type='D')
        for i in range(5):  # 最多尝试取6个季度的数据
            if len(df) == 0:
                date = self._get_last_season_end(date)
                df = pro.fina_mainbz(ts_code=self.code, period=self.tushare_date_format(date), type='D')
        print(df)
        text = self.code_name + '（' + self.code + '）的主营业务构成为（数据截止为'+date+'）：\n'
        df = df.sort_values(by='bz_sales', axis=0, ascending=False)
        # 预处理，将None转化为np.nan
        df['bz_profit'] = pd.to_numeric(df['bz_profit'])
        df['bz_cost'] = pd.to_numeric(df['bz_cost'])
        # 计算辅助指标
        df['bz_sales_ratio'] = df['bz_sales'] / np.sum(df['bz_sales'].values)  # 计算营业收入占比
        df['bz_profit_ratio'] = df['bz_profit'] / df['bz_sales']  # 计算毛利率
        # 文字生成部分
        table = prettytable.PrettyTable(['业务名称', '销售收入', '销售成本', '销售毛利', '销售毛利率', '销售收入占比'])
        for i in range(len(df)):
            data = df.iloc[i].values
            table.add_row(['%s' % data[2], '%.2f万元' % (data[3] / 10000.0), '%.2f万元' % (data[5] / 10000.0), '%.2f万元' % (data[4] / 10000.0), '%.2f%%' % (data[8] * 100.0), '%.2f%%' % (data[7] * 100.0)])
        text = text + str(table) + '\n'
        # 画图部分
        pie_chart = pygal.Pie()
        pie_chart.title = self.code_name + '（' + self.code + '）的主营业务百分比构成图（数据截止为'+date+'）'
        for i in range(len(df)):
            data = df.iloc[i].values
            pie_chart.add(data[2], data[7]*100.0)
        # 总结内容
        if len(df) > 0:
            summary_text = self._get_summary(df, self.code_name)
            text = text + summary_text
        else:  # 无数据披露的情形
            text = text + '无数据！\n'
        # 结果展示
        print(text)
        pie_chart.render_to_file('output\\temp.svg')
        result = {'text': text, 'image': [pie_chart]}
        return result

    @staticmethod
    def _get_summary(df, code_name):
        bz_item = df['bz_item'].values
        bz_sales_ratio = df['bz_sales_ratio'].values
        bz_sales_ratio_cumsum = np.cumsum(bz_sales_ratio)
        first_bigger_index = int(np.where(bz_sales_ratio_cumsum > 0.90)[0][0])  # 第一个求和大于90%的指标，包括指标本身
        text = code_name + '的主要业务区域有：'
        for i in range(first_bigger_index + 1):
            text = text + bz_item[i]
            if i == first_bigger_index:
                text = text + '；\n'
            else:
                text = text + '，'
        bz_sales_ratio_main = bz_sales_ratio[:first_bigger_index + 1]  # 主要业务比例列表
        bz_sales_ratio_main = bz_sales_ratio_main / bz_sales_ratio_main[0]
        bz_sales_ratio_core = np.where(bz_sales_ratio_main > 0.5)[0]  # 核心业务区域指标
        bz_sales_ratio_aux = np.where(bz_sales_ratio_main <= 0.5)[0]  # 补充业务区域指标
        text = text + '其中'
        for i in bz_sales_ratio_core:
            text = text + bz_item[i] + '、'
        text = text[:-1] + '是核心业务区域；'
        for i in bz_sales_ratio_aux:
            text = text + bz_item[i] + '、'
        text = text[:-1] + '是补充业务区域；'
        text = text[:-1] + '。\n'
        if len(bz_sales_ratio_core) > 3:
            text = text + code_name + '的业务区域非常多元化，业务在地域分布上比较分散'
        elif len(bz_sales_ratio_core) == 3:
            text = text + code_name + '的业务区域比较多元化，属于三核心业务区域类型'
        elif len(bz_sales_ratio_core) == 2:
            text = text + code_name + '的业务集中在两个区域，属于双核心业务区域类型'
        else:
            text = text + code_name + '的业务集中在一个区域，属于单核心业务区域类型'
        if len(bz_sales_ratio_aux) > 3:
            text = text + '，同时公司还有较多的辅助业务区域'
        elif len(bz_sales_ratio_aux) > 0 and len(bz_sales_ratio_aux) < 3:
            text = text + '，同时公司还有一定的辅助业务区域'
        else:
            text = text + '，同时公司无辅助业务区域'
        text = text + '。\n'
        return text


if __name__ == '__main__':
    code = '600155.SH'
    date = '2019-01-01'
    model = 个股主营业务分析_按产品(code, date)
    model.output()
