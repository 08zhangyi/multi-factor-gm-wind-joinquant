import numpy as np
import pandas as pd
from WindPy import w
import tushare as ts
import random
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_factor_from_wind_without_cache
from utils_rl import rl_build, rl_text, rl_table, rl_pie_chart, clean_path
TS_TOKEN = 'fcd3ee99a7d5f0e27c546d074a001f0b3eae01312c4dd8354415fba1'
MAX_RANDOM = 10000000


class 个股分析模板():
    def __init__(self, code, date):
        w.start()
        self.code = code
        self.date = date
        self.code_name = w.wss(code, "sec_name").Data[0][0]

    def output(self):
        # 主体内容
        result = []
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
        text = '\0\0' + self.code_name + '（' + self.code + '）的主营业务构成为（数据截止为'+date+'）：\n'
        para_1 = rl_text(text)
        df = df.sort_values(by='bz_sales', axis=0, ascending=False)
        # 预处理，将None转化为np.nan
        df['bz_profit'] = pd.to_numeric(df['bz_profit'])
        df['bz_cost'] = pd.to_numeric(df['bz_cost'])
        # 计算辅助指标
        df['bz_sales_ratio'] = df['bz_sales'] / np.sum(df['bz_sales'].fillna(0.0).values)  # 计算营业收入占比
        df['bz_profit_ratio'] = df['bz_profit'] / df['bz_sales']  # 计算毛利率
        # 文字生成部分
        table_list = [['业务名称', '销售收入', '销售成本', '销售毛利', '销售毛利率', '销售收入占比']]
        for i in range(len(df)):
            data = df.iloc[i].values
            table_list.append(['%s' % data[2], '%.2f万元' % (data[3]/10000.0), '%.2f万元' % (data[5]/10000.0), '%.2f万元' % (data[4]/10000.0), '%.2f%%' % (data[8]*100.0), '%.2f%%' % (data[7]*100.0)])
        table_1 = rl_table(table_list)
        # 总结内容
        text = '\0\0'
        if len(df) > 0:
            summary_text = self._get_summary(df, self.code_name)
            text = text + summary_text
        else:  # 无数据披露的情形
            text = text + '无数据！\n'
        # 结果展示
        para_2 = rl_text(text)
        # 饼图
        texts = []
        datas = []
        for i in range(len(df)):
            data = df.iloc[i].values
            texts.append(data[2])
            datas.append(data[7]*100)
        title = self.code_name + '（' + self.code + '）的主营业务百分比构成图（数据截止为'+date+'）'
        image_1 = rl_pie_chart(title, datas, texts, str(random.randint(0, MAX_RANDOM)))
        return [para_1, table_1, rl_text('\0'), para_2, image_1, rl_text('\0')]

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
        if len(bz_sales_ratio_core) > 0:
            for i in bz_sales_ratio_core:
                text = text + bz_item[i] + '、'
            text = text[:-1] + '是核心业务成分；'
        if len(bz_sales_ratio_aux) > 0:
            for i in bz_sales_ratio_aux:
                text = text + bz_item[i] + '、'
            text = text[:-1] + '是辅助业务成分；'
        if len(bz_sales_ratio_supple) > 0:
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
        text = '\0\0' + self.code_name + '（' + self.code + '）的主营业务构成为（数据截止为'+date+'）：\n'
        para_1 = rl_text(text)
        df = df.sort_values(by='bz_sales', axis=0, ascending=False)
        # 预处理，将None转化为np.nan
        df['bz_profit'] = pd.to_numeric(df['bz_profit'])
        df['bz_cost'] = pd.to_numeric(df['bz_cost'])
        # 计算辅助指标
        df['bz_sales_ratio'] = df['bz_sales'] / np.sum(df['bz_sales'].values)  # 计算营业收入占比
        df['bz_profit_ratio'] = df['bz_profit'] / df['bz_sales']  # 计算毛利率
        # 文字生成部分
        table_list = [['业务名称', '销售收入', '销售成本', '销售毛利', '销售毛利率', '销售收入占比']]
        for i in range(len(df)):
            data = df.iloc[i].values
            table_list.append(['%s' % data[2], '%.2f万元' % (data[3] / 10000.0), '%.2f万元' % (data[5] / 10000.0), '%.2f万元' % (data[4] / 10000.0), '%.2f%%' % (data[8] * 100.0), '%.2f%%' % (data[7] * 100.0)])
        table_1 = rl_table(table_list)
        # 画图部分
        datas = []
        texts = []
        for i in range(len(df)):
            data = df.iloc[i].values
            texts.append(data[2])
            datas.append(data[7]*100.0)
        title = self.code_name + '（' + self.code + '）的主营业务百分比构成图（数据截止为'+date+'）'
        image_1 = rl_pie_chart(title, datas, texts, str(random.randint(0, MAX_RANDOM)))
        # 总结内容
        text = '\0\0'
        if len(df) > 0:
            summary_text = self._get_summary(df, self.code_name)
            text = text + summary_text
        else:  # 无数据披露的情形
            text = text + '无数据！\n'
        para_2 = rl_text(text)
        return [para_1, table_1, rl_text('\0'), para_2, image_1, rl_text('\0')]

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
        if len(bz_sales_ratio_core):
            for i in bz_sales_ratio_core:
                text = text + bz_item[i] + '、'
            text = text[:-1] + '是核心业务区域；'
        if len(bz_sales_ratio_aux):
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


class 个股营收增长分析(个股分析模板):
    def output(self):
        from single_factor import RevenueGrowthRate, EstimateNetRevenueGrowRateFY1_6M
        factor_list = [RevenueGrowthRate, EstimateNetRevenueGrowRateFY1_6M]
        code = [self.code]
        df = get_factor_from_wind_without_cache(code, factor_list, self.date)
        df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1])
        text = '\0\0营业收入分析（数据截止' + self.date + '）：'
        para_1 = rl_text(text)
        text = '营业收入增长率为%.2f%%；分析师一致预期营业收入增长率为%.2f%%；'
        text = text % (df.iloc[:, 0].values, df.iloc[:, 1].values)
        text_summary = self._get_summary(df)
        text = text + text_summary
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]


    @staticmethod
    def _get_summary(df):
        real = df.iloc[:, 0].values
        predict = df.iloc[:, 1].values
        diff = real - predict
        diff = diff[0]
        if diff > 5.0:
            text_summary = "营业收入增速超过最新的一致预期。"
        elif diff < 5.0 and diff > -5.0:
            text_summary = "营业收入增速符合最新的一致预期"
        elif diff < -5.0:
            text_summary = "营业收入增速未达到最新的一致预期。"
        elif np.isnan(diff):
            text_summary = "暂无分析师对此公司进行营业收入预测，受关注度不高。"
        else:
            text_summary = "Warining: recoding is needed!"
        return text_summary


class 个股净利润增长分析(个股分析模板):
    def output(self):
        from single_factor import NetProfit, NetProfitGrowRateV2, EstimateNetProfitGrowRateFY1_6M
        factor_list = [NetProfit, NetProfitGrowRateV2, EstimateNetProfitGrowRateFY1_6M]
        code = [self.code]
        df = get_factor_from_wind_without_cache(code, factor_list, self.date)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1])
        df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2])
        text = '\0\0净利润增长分析（数据截止' + self.date + '）：'
        para_1 = rl_text(text)
        text = '公司净利润为%.2f亿元；净利润增长率为%.2f%%；分析师一致预期净利润增长率为%.2f%%；'
        text = text % (df.iloc[:, 0].values/100000000.0, df.iloc[:, 1].values, df.iloc[:, 2].values)
        text_summary = self._get_summary(df)
        text = text + text_summary
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]

    @staticmethod
    def _get_summary(df):
        real = df.iloc[:, 1].values
        predict = df.iloc[:, 2].values
        diff = (real - predict)
        if diff > 5.0:
            text_summary = "净利润增速超过最新的一致预期。"
        elif diff < 5.0 and diff > -5.0:
            text_summary = "净利润增速符合最新的一致预期。"
        elif diff < -5.0:
            text_summary = "净利润增速未达到最新的一致预期。"
        elif np.isnan(diff):
            text_summary = "暂无分析师对此公司进行评级预测，受关注度不高。"
        else:
            text_summary = "Warining: recoding is needed!。"
        return text_summary


class 经营活动现金流分析(个股分析模板):
    def output(self):
        from single_factor import OperateCashFlow, CashFlowCoverRatio
        factor_list = [OperateCashFlow, CashFlowCoverRatio]
        code = [self.code]
        df = get_factor_from_wind_without_cache(code, factor_list, self.date)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1])
        text = '\0\0现金流分析（数据截止' + self.date + '）：'
        para_1 = rl_text(text)
        text = '经营活动现金流为%.2f亿元；' + '利润现金保障倍数为%.2f倍；'
        text = text % (df.iloc[:, 0].values/100000000.0, df.iloc[:, 1].values)
        text_summary = self._get_summary(df)
        text = text + text_summary
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]

    def _get_summary(self, df):
        from single_factor import NetProfit
        factor_list = [NetProfit]
        code = [self.code]
        netprofit = get_factor_from_wind_without_cache(code, factor_list, self.date).iloc[:, 0].values
        if df.iloc[:, 0].values < 0.0 and netprofit < 0.0:
            text_summary = "此时利润现金保障倍数无实际含义，公司目前整体亏损，公司主营业务经营活动并无现金流入，整体现金流情况较差。"
        elif df.iloc[:, 0].values < 0.0 and netprofit > 0.0:
            text_summary = "利润现金保障倍数为负值，财务报表中提现公司仍然盈利，但经营活动现金流为负值，说明公司造血能力较差，" \
                           "日常经营消耗企业现存货币积累。此种情况可以从应收账款、投资活动、筹资活动或者会计记账原则的角度来进一步分析。"
        elif df.iloc[:, 0].values > 0.0 and netprofit < 0.0:
            text_summary = "企业经营活动现金流为正，但是公司整体亏损，说明公司在主营业务经营活动正常运转，" \
                           "此类情况并不寻常，可以从成本端和营业外支出/收入中寻找原因。"
        elif df.iloc[:, 0].values > 0.0 and netprofit > 0.0:
            if df.iloc[:, 1].values > 0.85: # 利润现金保障倍数
                text_summary = "净利润和经营现金流都为正数，企业健康发展，运营正常，自身能够产生充足经营现金流，公司产生的净利润是有足够的现金流支持。"
            elif df.iloc[:, 1].values <= 0.85 and df.iloc[:, 1].values > 0.5:
                text_summary = "净利润和经营现金流都为正数，企业经营活动能够正常运转，但是经营活动现金流入水平较低，公司产生的净利润是有一定的现金流支持，公司经营管理水平有待改善。"
            elif df.iloc[:, 1].values <= 0.5 and df.iloc[:, 1].values > 0.0:
                text_summary = "净利润和经营现金流都为正数，企业经营活动处于正常运转，但是经营活动现金流入水平偏低，公司产生的净利润缺乏足够的现金流支持，公司经营管理水平有待提高。"
        else:
            text_summary = "Warining: recoding is needed!"
        return text_summary


class 经营理念分析_销售费用(个股分析模板):
    def output(self):
        from single_factor import SellExpense, SellExpenseRevenue, SellExpenseGrowth
        factor_list = [SellExpense, SellExpenseRevenue, SellExpenseGrowth]
        code = [self.code]
        df = get_factor_from_wind_without_cache(code, factor_list, self.date)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1])
        df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2])
        text = '\0\0经营理念分析——销售费用（数据截止' + self.date + '）：'
        para_1 = rl_text(text)
        text = '销售费用为为%.2f亿元；销售费用占营业收入的比重为：%.2f%%；销售费用增长率为%.2f%%；'
        text = text % (df.iloc[:, 0].values/100000000.0, df.iloc[:, 1].values * 100.0, df.iloc[:, 2].values * 100)
        text_summary = self._get_summary(df)
        text = text + text_summary
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]

    def _get_summary(self, df):
        from single_factor import RevenueGrowthRate
        factor_list = [RevenueGrowthRate]
        code = [self.code]
        rev_growth = get_factor_from_wind_without_cache(code, factor_list, self.date).iloc[:, 0].values/100.0
        sellexp_growth = df.iloc[:, 2]
        diff = (rev_growth - sellexp_growth)[0]
        if diff >= 0.03:
            text_summary = "销售费用的增长慢于销售收入增长，预期公司毛利率具有一定的增长潜力。"
        elif diff < -0.03:
            text_summary = "销售费用的增长快于销售收入增长，预期公司毛利率增长不乐观。"
        elif diff < 0.03 and diff > -0.03:
            text_summary = "销售费用的增长与销售收入增长基本持平，预期公司经营稳定。"
        elif np.isnan(diff):
            text_summary = "公司缺失相关数据，无法分析。"
        else:
            text_summary = "Warining: recoding is needed!"
        return text_summary


class 经营理念分析_研发费用(个股分析模板):
    def output(self):
        from single_factor import RDExpense, RDExpenseRevenue
        factor_list = [RDExpense, RDExpenseRevenue]
        code = [self.code]
        date = self._get_last_year_end(self.date)
        df = get_factor_from_wind_without_cache(code, factor_list, date)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1])
        text = '\0\0经营理念分析——研发费用（数据截止' + date + '）：'
        para_1 = rl_text(text)
        text = '研发费用为%.2f亿元：占营业收入为%.2f%%。'
        text = text % (df.iloc[:, 0].values / 100000000.0, df.iloc[:, 1].values * 100.0)
        para_2 = rl_text(text)
        if np.isnan(df.iloc[:, 0].values):
            return []
        else:
            return [para_1, para_2, rl_text('\0')]


# 部分金融股不具备此指标
class 资产结构分析(个股分析模板):
    def output(self):
        from single_factor import NonCurrentAssetRatio
        factor_list = [NonCurrentAssetRatio]
        code = [self.code]
        df = get_factor_from_wind_without_cache(code, factor_list, self.date)
        date_last = self._get_last_year_date(self.date)
        df_last_year = get_factor_from_wind_without_cache(code, factor_list, date_last)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df_last_year.iloc[:, 0] = pd.to_numeric(df_last_year.iloc[:, 0])
        growth = (df.iloc[:, 0].values - df_last_year.iloc[:, 0].values) / df_last_year.iloc[:, 0].values
        text = '\0\0资产结构分析（数据截止' + date + '）：'
        para_1 = rl_text(text)
        text = '公司非流动资产占比为%.2f%%；上年同期为%.2f%%；同比增长为%.2f%%；'
        text = text % (df.iloc[:, 0].values, df_last_year.iloc[:, 0], growth * 100.0)
        text_summary = self._get_summary(df)
        text = text + text_summary
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]

    def _get_summary(self, df):
        ratio = df.iloc[:, 0].values
        if ratio <= 15.0:
            text_summary = '企业非流动资产占比低，属于轻资产公司。'
        elif ratio >= 40.0:
            text_summary = '企业非流动资产占比高，属于重资产公司。'
        elif ratio > 15.0 and ratio < 40.0:
            text_summary = '企业非流动资产占比较高，需要结合公司主营业务特点来看资产构成。'
        elif np.isnan(ratio):
            text_summary = '缺乏资产相关数据，无法分析。'
        else:
            text_summary = 'Warining: recoding is needed!'
        return text_summary


# 资产周转率指标在应用于房地产行业需要谨慎考虑，因为土地资源可能会带来增值收益。
class 管理层面分析_效率(个股分析模板):
    def output(self):
        from single_factor import AssetTurnoverRatio
        factor_list = [AssetTurnoverRatio]
        code = [self.code]
        df = get_factor_from_wind_without_cache(code, factor_list, self.date)
        last_year = self._get_last_year_date(self.date)
        df_last_year = get_factor_from_wind_without_cache(code, factor_list, last_year)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df_last_year.iloc[:, 0] = pd.to_numeric(df_last_year.iloc[:, 0])
        growth = (df.iloc[:, 0].values - df_last_year.iloc[:, 0].values) / df_last_year.iloc[:, 0].values
        text = '\0\0管理层面分析_效率分析（数据截止' + self.date + '）：'
        para_1 = rl_text(text)
        text = '总资产周转率本年为%.2f次；上年同期为%.2f次；同比增长率为%.2f%%；'
        text = text % (df.iloc[:, 0].values, df_last_year.iloc[:, 0], growth * 100.0)
        text_summary = self._get_summary(df, growth)
        text = text + text_summary
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]

    def _get_summary(self, df, growth):
        turnover = df.iloc[:, 0].values
        if turnover >= 0.9 and growth > 0.0:
            text_summary = '公司具有较高的资产周转率，且较上年同期有所提升，资产使用效率较高。'
        elif turnover >= 0.9 and growth <= 0.0:
            text_summary = '公司具有较高的资产周转率，且较上年同期并未显著提高，反而资产使用效率有所下降，但总体处于较高水平。'
        elif turnover > 0.5 and turnover < 0.9 and growth > 0.0:
            text_summary = '资产周转率较上年同期有所改善，资产使用效率有待提高。'
        elif turnover > 0.5 and turnover < 0.9 and growth <= 0.0:
            text_summary = '资产周转率总体良好，但较去年同期有所下降，资产使用效率有待提高。'
        elif turnover > 0.0 and turnover < 0.5 and growth > 0.0:
            text_summary = '资产周转率处于较低水平，但是较上年同期有所提高，总体资产使用效率有待提高。'
        elif turnover > 0.0 and turnover < 0.5 and growth <= 0.0:
            text_summary = '资产周转率处于较低水平，从最近一期数据来看情况并没有得到改善，需要做出更进一步分析。'
        elif np.isnan(turnover) or np.isnan(growth):
            text_summary = '缺乏相关数据，无法做出分析。'
        else:
            text_summary = 'Warining: recoding is needed!'
        return text_summary


class 应收账款周转率(个股分析模板):
    def output(self):
        from single_factor import AccRecTurnRatioV2
        factor_list = [AccRecTurnRatioV2]
        code = [self.code]
        date = self._get_last_year_end(self.date)
        df = get_factor_from_wind_without_cache(code, factor_list, date)
        date_last = self._get_last_year_date(date)
        df_last_year = get_factor_from_wind_without_cache(code, factor_list, date_last)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df_last_year.iloc[:, 0] = pd.to_numeric(df_last_year.iloc[:, 0])
        growth = (df.iloc[:, 0].values - df_last_year.iloc[:, 0].values) / df_last_year.iloc[:, 0].values
        text = '\0\0应收账款率分析（数据截止' + date + '）：'
        para_1 = rl_text(text)
        text = '应收账款周转率为%.2f次；上年同期为%.2f次；同比增长为%.2f%%。'
        text = text % (df.iloc[:, 0].values, df_last_year.iloc[:, 0], growth * 100.0)
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]


class 存货周转率(个股分析模板):
    def output(self):
        from single_factor import InventoryTurnRatio
        factor_list = [InventoryTurnRatio]
        code = [self.code]
        df = get_factor_from_wind_without_cache(code, factor_list, self.date)
        last_year = self._get_last_year_date(self.date)
        df_last_year = get_factor_from_wind_without_cache(code, factor_list, last_year)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df_last_year.iloc[:, 0] = pd.to_numeric(df_last_year.iloc[:, 0])
        growth = (df.iloc[:, 0].values - df_last_year.iloc[:, 0].values) / df_last_year.iloc[:, 0].values
        text = '\0\0存货周转率分析（数据截止' + self.date + '）：'
        para_1 = rl_text(text)
        text = '存货周转率为%.2f次；上年同期为%.2f次；同比增长为%.2f%%。'
        text = text % (df.iloc[:, 0].values, df_last_year.iloc[:, 0], growth * 100.0)
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]


class 资产负债率分析(个股分析模板):
    def output(self):
        from single_factor import DebetToAsset, TotalAsset
        factor_list = [DebetToAsset, TotalAsset]
        code = [self.code]
        df = get_factor_from_wind_without_cache(code, factor_list, self.date)
        last_year = self._get_last_year_date(self.date)
        df_last_year = get_factor_from_wind_without_cache(code, factor_list, last_year)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1])
        df_last_year.iloc[:, 0] = pd.to_numeric(df_last_year.iloc[:, 0])
        growth = (df.iloc[:, 0].values - df_last_year.iloc[:, 0].values) / df_last_year.iloc[:, 0].values
        text = '\0\0管理层面分析_效率分析（数据截止' + self.date + '）：'
        para_1 = rl_text(text)
        text = '总资产规模为%.2f亿元；资产负债率为%.2f%%；上年同期为%.2f%%；同比增长为%.2f%%；'
        text = text % (df.iloc[:, 1].values / 100000000.0, df.iloc[:, 0].values * 100.0, df_last_year.iloc[:, 0].values * 100.0, growth * 100.0)
        text_summary = self._get_summary(df)
        text = text + text_summary
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]

    def _get_summary(self, df):
        da_ratio = df.iloc[:, 0].values
        if da_ratio > 0.9:
            text_summary = '公司整体负债率过高，企业来源于债务的资金比较多，公司面临的财务风险水平较高。'
        elif da_ratio <= 0.9 and da_ratio > 0.7:
            text_summary = '公司整体负债率偏高，需要进一步从公司资本运作与经营战略中寻找原因'
        elif da_ratio <= 0.7 and da_ratio > 0.3:
            text_summary = '公司整体负债水平偏低，总体财务风险可控。'
        elif da_ratio <=0.3:
            text_summary = '公司负债水平偏低，一方面说明公司的财务风险很低，另一方面也说明公司不善理财，股东权益占比偏高，导致股东权益资本效率下降'
        elif np.isnan(da_ratio):
            text_summary = '缺少数据，无法分析结论。'
        else:
            text_summary = 'Warining: recoding is needed!'
        return text_summary


class 短期偿债能力分析(个股分析模板):
    def output(self):
        from single_factor import CurrentRatio
        factor_list = [CurrentRatio]
        code = [self.code]
        df = get_factor_from_wind_without_cache(code, factor_list, self.date)
        last_year = self._get_last_year_date(self.date)
        df_last_year = get_factor_from_wind_without_cache(code, factor_list, last_year)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df_last_year.iloc[:, 0] = pd.to_numeric(df_last_year.iloc[:, 0])
        growth = (df.iloc[:, 0].values - df_last_year.iloc[:, 0].values) / df_last_year.iloc[:, 0].values
        text = '\0\0短期偿债能力分析（数据截止' + self.date + '）：'
        para_1 = rl_text(text)
        text = '流动比率为%.2f；上年同期为%.2f；同比增长率为%.2f%%；'
        text = text % (df.iloc[:, 0].values, df_last_year.iloc[:, 0].values, growth * 100.0)
        text_summary = self._get_summary(df)
        text = text + text_summary
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]

    def _get_summary(self, df):
        ratio = df.iloc[:, 0].values
        if ratio >= 1.0:
            text_summary = '\t公司的流动比率水平较好，流动资产高于流动负债，公司短期的偿债能力较强，经营风险较低。'
        elif ratio <1.0 and ratio > 0.5:
            text_summary = '\t公司的流动比率水平偏低，流动负债值较高，公司可能会出现短期偿债困难的情况，具有一定的财务风险。'
        elif ratio <= 0.5 and ratio > 0.0:
            text_summary = '\t公司的流动比率严重偏低，短期偿债能力弱，公司的举债经营可能正处于财务困境中，未来发生不利于公司经营的市场环境变化可能加剧恶化公司的财务风险。'
        elif np.isnan(ratio):
            text_summary = '缺少数据，无法分析结论。'
        else:
            text_summary = 'Warining: recoding is needed!'
        return text_summary


class 业绩分析(个股分析模板):
    def output(self):
        from single_factor import ROE
        factor_list = [ROE]
        code = [self.code]
        df = get_factor_from_wind_without_cache(code, factor_list, self.date)
        last_year = self._get_last_year_date(self.date)
        df_last_year = get_factor_from_wind_without_cache(code, factor_list, last_year)
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df_last_year.iloc[:, 0] = pd.to_numeric(df_last_year.iloc[:, 0])
        growth = (df.iloc[:, 0].values - df_last_year.iloc[:, 0].values) / df_last_year.iloc[:, 0].values
        text =  '\0\0业绩分析（资本回报率ROE）（数据截止' + self.date + '）：'
        para_1 = rl_text(text)
        text = '资本回报为ROE%.2f%%；上年同期为%.2f%%；同比增长率为%.2f%%；'
        text = text % (df.iloc[:, 0].values, df_last_year.iloc[:, 0].values, growth * 100.0)
        text_summary = self._get_summary(df)
        text = text + text_summary
        para_2 = rl_text(text)
        return [para_1, para_2, rl_text('\0')]

    def _get_summary(self,df):
        ratio = df.iloc[:, 0].values
        if ratio >= 20.0:
            text_summary = 'ROE水平较高，符合主流价值投资选股要求。'
        elif ratio < 20.0 and ratio > 10.0:
            text_summary = 'ROE水平良好，需要横向对比行业水平。'
        elif ratio <= 10.0:
            text_summary = 'ROE较低。'
        elif np.isnan(ratio):
            text_summary = '缺少数据，无法分析结论。'
        else:
            text_summary = 'Warining: recoding is needed!'
        return text_summary


if __name__ == '__main__':
    clean_path()
    code = '002869.SZ'
    date = '2019-09-16'
    output_list = []
    Ms = [个股主营业务分析_按产品, 个股主营业务分析_按地区, 个股营收增长分析, 个股净利润增长分析, 经营活动现金流分析,
          经营理念分析_销售费用, 经营理念分析_研发费用, 资产结构分析, 管理层面分析_效率, 应收账款周转率,
          存货周转率, 资产负债率分析, 短期偿债能力分析, 业绩分析]
    for M in Ms:
        model = M(code, date)
        output_list += model.output()
    rl_build(output_list)