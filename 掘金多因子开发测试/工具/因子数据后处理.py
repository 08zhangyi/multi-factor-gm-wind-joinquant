import numpy as np
import pandas as pd
import sklearn
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
from single_factor import SW1Industry, SW1IndustryOneHot
# 后处理测试用的因子
from WindPy import w
from single_factor import VOL10, RSI, PE
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_factor_from_wind_v2


# 因子后处理基类
# 可以嵌套应用因子后处理工具
class 因子后处理(object):
    def __init__(self, factor_df, date):
        self.factor_df = factor_df
        self.date = date  # 采集因子的日期

    def get_factor_df(self):
        return self.factor_df


class 加入行业编码(因子后处理):
    def get_factor_df(self):
        code_list = list(self.factor_df.index.values)
        SW1_df = SW1IndustryOneHot(self.date, code_list).get_factor()
        df = pd.concat((self.factor_df, SW1_df), axis=1).dropna()
        return df


# 以下处理依赖于去除有缺失值的样本
class 去缺失值(因子后处理):
    def __init__(self, factor_df, date):
        super().__init__(factor_df, date)
        self.factor_df = factor_df.dropna()


class 因子中心化(去缺失值):
    def get_factor_df(self):
        df = self.factor_df
        df = (df - df.mean()) / df.std()
        return df


class 因子排序值(去缺失值):
    def get_factor_df(self):
        df = self.factor_df
        value = np.argsort(np.argsort(df.values, axis=0), axis=0) / (len(df) - 1)  # 转化为0-1的排序值
        df = pd.DataFrame(data=value, columns=df.columns, index=df.index)
        return df


class 因子去极值(去缺失值):
    def __init__(self, factor_df, date, min_quantile=0.05, max_quantitle=0.95):
        super().__init__(factor_df, date)
        self.min_quantile = min_quantile
        self.max_quantitle = max_quantitle

    def get_factor_df(self):
        df = self.factor_df
        df = self._deextreme_value(df)
        return df

    def _deextreme_value(self, df):
        values_df = df.values
        values_df_min = df.quantile(0.05).values
        values_df_max = df.quantile(0.95).values
        values_df = np.minimum(np.maximum(values_df, values_df_min), values_df_max)
        df.values[:, :] = values_df
        return df


class 因子行业中性化(去缺失值):
    def get_factor_df(self):
        df = self.factor_df
        code_list = list(df.index.values)  # 股票的代码
        factor_list = list(df.columns.values)  # 因子名称的代码
        SW1_df = SW1Industry(self.date, code_list).get_factor()
        df = pd.concat([df, SW1_df], axis=1).dropna()  # 去除缺失行业因子的股票
        # 根据行业分组进行因子标准化
        df_group_by = df.groupby('申万一级行业')
        result_df_list = []
        for industry, df_industry in df_group_by:
            df_industry = df_industry[factor_list]
            df_industry = (df_industry - df_group_by.mean().loc[industry]) / df_group_by.std().loc[industry]
            result_df_list.append(df_industry)
        df = pd.concat(result_df_list, axis=0)
        return df


class 因子行业中性化_回归法(去缺失值):
    def get_factor_df(self):
        factor_df = self.factor_df
        code_list = list(factor_df.index.values)  # 股票的代码
        factor_list = list(factor_df.columns.values)  # 因子名称的代码
        SW1_df = SW1IndustryOneHot(self.date, code_list).get_factor()
        df = pd.concat([factor_df, SW1_df], axis=1).dropna()  # 去除缺失行业因子的股票
        # 将因子值行业关于行业哑变量回归，去残值作为中性化 的因子值
        for factor in factor_list:  # 对因子依次做回归
            factor_df_temp = factor_df[factor]
            df_temp = pd.concat([factor_df_temp, SW1_df], axis=1)
            df_y = df_temp[factor].values  # 因子值
            del df_temp[factor]
            df_x = df_temp.values  # 行业哑变量值
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(df_x, df_y)
            res_value = df_y - model.predict(df_x)
            factor_df[factor].values[:] = res_value
        return factor_df


class 因子行业排序值(去缺失值):
    def get_factor_df(self):
        df = self.factor_df
        code_list = list(df.index.values)  # 股票的代码
        factor_list = list(df.columns.values)  # 因子名称的代码
        SW1_df = SW1Industry(self.date, code_list).get_factor()
        df = pd.concat([df, SW1_df], axis=1).dropna()  # 去除缺失行业因子的股票
        # 根据行业分组进行因子标准化
        df_group_by = df.groupby('申万一级行业')
        result_df_list = []
        for industry, df_industry in df_group_by:
            df_industry = df_industry[factor_list]
            value = np.argsort(np.argsort(df_industry.values, axis=0), axis=0) / (len(df_industry) - 1)  # 转化为0-1的排序值
            df_industry = pd.DataFrame(data=value, columns=df_industry.columns, index=df_industry.index)
            result_df_list.append(df_industry)
        df = pd.concat(result_df_list, axis=0)
        return df


class 因子行业去极值(因子去极值):
    def get_factor_df(self):
        df = self.factor_df
        code_list = list(df.index.values)  # 股票的代码
        factor_list = list(df.columns.values)  # 因子名称的代码
        SW1_df = SW1Industry(self.date, code_list).get_factor()
        df = pd.concat([df, SW1_df], axis=1).dropna()  # 去除缺失行业因子的股票
        # 根据行业分组进行因子标准化
        df_group_by = df.groupby('申万一级行业')
        result_df_list = []
        for industry, df_industry in df_group_by:
            df_industry = df_industry[factor_list]
            df_industry = self._deextreme_value(df_industry)
            result_df_list.append(df_industry)
        df = pd.concat(result_df_list, axis=0)
        return df


if __name__ == '__main__':
    w.start()
    # code_list = w.wset("sectorconstituent", "date=2018-10-30;windcode=000300.SH").Data[1]
    code_list = ['000002.SZ', '600000.SH']
    factor_df = get_factor_from_wind_v2(code_list, [VOL10, RSI, PE], '2018-12-18')  # 故意引入错误数据
    factor_df = 因子行业中性化_回归法(factor_df, '2018-12-18').get_factor_df()
    print(factor_df)