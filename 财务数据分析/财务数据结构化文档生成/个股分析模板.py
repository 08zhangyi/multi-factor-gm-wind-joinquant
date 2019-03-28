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
        df['bz_sales_ratio'] = df['bz_sales'] / np.sum(df['bz_sales'].values)  # 计算营业收入占比
        df['bz_profit_ratio'] = df['bz_profit'] / df['bz_sales']  # 计算毛利率
        # 文字生成部分
        for i in range(len(df)):
            data = df.iloc[i].values
            text_temp = '业务名称：%s，\t销售收入：%.2f万元，\t销售成本：%.2f万元，\t销售毛利：%.2f万元，\t销售毛利率：%.2f%%，\t销售收入占比：%.2f%%；\n'
            text_temp = text_temp % (data[2], data[3]/10000.0, data[5]/10000.0, data[4]/10000.0, data[8]*100.0, data[7]*100.0)
            text = text + text_temp
        # 画图部分
        pie_chart = pygal.Pie()
        pie_chart.title = self.code_name + '（' + self.code + '）的主营业务百分比构成图（数据截止为'+date+'）'
        for i in range(len(df)):
            data = df.iloc[i].values
            pie_chart.add(data[2], data[7]*100.0)
        # 总结内容，待开发
        summary_text = self._get_summary(df, self.code_name)
        text = text + summary_text
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
        first_bigger_index = int(np.where(bz_sales_ratio_cumsum > 0.90)[0][0])  # 第一个求和大于85%的指标，包括指标本身
        text = code_name + '的主要业务有：'
        for i in range(first_bigger_index+1):
            text = text + bz_item[i]
            if i == first_bigger_index:
                text = text + '；\n'
            else:
                text = text + '，'
        for i in range(0, first_bigger_index+1):  # 提取核心业务成分，主业的50%权重为核心业务
            core_index = first_bigger_index - i
            if bz_sales_ratio[core_index] / bz_sales_ratio[0] >= 0.5:
                break
        aux_index = core_index
        for i in range(0, first_bigger_index-core_index+1):  # 提取辅助业务成分，主业的15%权重为辅助业务
            aux_index = first_bigger_index - i
            if bz_sales_ratio[aux_index] / bz_sales_ratio[0] >= 0.15:
                break
        text = text + '其中'
        for i in range(0, core_index+1):
            text = text + bz_item[i]
            if i == core_index:
                text = text + '是核心业务成分；'
            else:
                text = text + '、'
        for i in range(core_index+1, aux_index+1):
            text = text + bz_item[i]
            if i == aux_index:
                text = text + '是辅助业务成分；'
            else:
                text = text + '、'
        for i in range(aux_index+1, first_bigger_index+1):
            text = text + bz_item[i]
            if i == first_bigger_index:
                text = text + '是补充业务成分；'
            else:
                text = text + '、'
        if text[-1] == '；':
            text = text[:-1] + '。'
        text = text + '\n'
        if (core_index + 1) > 3:
            text = text + code_name + '的业务非常多元化，无明显主营业务'
            if core_index == first_bigger_index:
                text = text + '，且公司无其他主要业务。'
            elif aux_index == core_index:
                text = text + '，且公司无辅助业务，但公司有少量补充业务。'
            elif aux_index == first_bigger_index:
                text = text + '，但公司有少量辅助业务，无补充业务。'
            else:
                text = text + '，但公司有少量辅助业务和补充业务。'
        elif (core_index + 1) == 3:
            text = text + code_name + '的业务比较多元化，属于三核心业务类型'
            if core_index == first_bigger_index:
                text = text + '，且公司无其他主要业务。'
            elif aux_index == core_index:
                text = text + '，且公司无辅助业务，但公司有少量补充业务。'
            elif aux_index == first_bigger_index:
                text = text + '，但公司有少量辅助业务，无补充业务。'
            else:
                text = text + '，但公司有少量辅助业务和补充业务。'
        elif (core_index + 1) == 2:
            text = text + code_name + '的业务双核心特征明显，属于双核心业务类型'
            if core_index == first_bigger_index:
                text = text + '，且公司无其他主要业务。'
            elif aux_index == core_index:
                text = text + '，且公司无辅助业务，但公司有少量补充业务。'
            elif aux_index == first_bigger_index:
                text = text + '，但公司有少量辅助业务，无补充业务。'
            else:
                text = text + '，但公司有少量辅助业务和补充业务。'
        else:
            text = text + code_name + '的业务核心业务突出，属于单核心业务类型'
            if core_index == first_bigger_index:
                text = text + '，且公司无其他主要业务。'
            elif aux_index == core_index:
                text = text + '，且公司无辅助业务，但公司有少量补充业务。'
            elif aux_index == first_bigger_index:
                text = text + '，但公司有少量辅助业务，无补充业务。'
            else:
                text = text + '，但公司有少量辅助业务和补充业务。'
        text = text + '\n'
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
        text = self.code_name + '（' + self.code + '）的主营业务构成为（数据截止为'+date+'）：\n'
        df = df.sort_values(by='bz_sales', axis=0, ascending=False)
        # 预处理，将None转化为np.nan
        df['bz_profit'] = pd.to_numeric(df['bz_profit'])
        df['bz_cost'] = pd.to_numeric(df['bz_cost'])
        # 计算辅助指标
        df['bz_sales_ratio'] = df['bz_sales'] / np.sum(df['bz_sales'].values)  # 计算营业收入占比
        df['bz_profit_ratio'] = df['bz_profit'] / df['bz_sales']  # 计算毛利率
        # 文字生成部分
        for i in range(len(df)):
            data = df.iloc[i].values
            text_temp = '业务名称：%s，\t销售收入：%.2f万元，\t销售成本：%.2f万元，\t销售毛利：%.2f万元，\t销售毛利率：%.2f%%，\t销售收入占比：%.2f%%；\n'
            text_temp = text_temp % (data[2], data[3]/10000.0, data[5]/10000.0, data[4]/10000.0, data[8]*100.0, data[7]*100.0)
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
    code = '002565.SZ'
    date = '2019-01-01'
    model = 个股主营业务分析_按产品(code, date)
    model.output()
