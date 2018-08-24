import QuantLib as ql
import pandas as pd
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
# 引入工具函数和学习器
from utils import get_factor_from_wind_v2, get_trading_date_from_now


class MasterStratery(object):
    def __init__(self, code_list, date):
        self.code_list = code_list  # 选股的股票代码
        self.date = date  # 选股的日期

    def _get_data(self):
        df = None  # 实现具体选股用到的数据
        return df

    def select_code(self):
        df = self._get_data()
        code_list = None  # 根据选股用到的数据具体选股
        return code_list


class 彼得林奇基层调查选股策略说明(MasterStratery):
    '''选股条件：
1.公司的资产负债率小于等于 25%;
2.公司每股净现金大于 0；
3.当前股价与每股自由现金流量比小于10；
4.公司的存货成长率小于其营收增长率；
5.（长期盈余成长率+股息率）/市盈率大于等于 2；'''
    def _get_data(self):
        from single_factor import DebetToAsset, CFPS, MarketValueToFreeCashFlow, NetProfitGrowRateV2, DividendYield, PE, InventoryTurnRatio
        factor_list = [DebetToAsset, CFPS, MarketValueToFreeCashFlow, NetProfitGrowRateV2, DividendYield, PE]
        factor_InvTurn_now = [InventoryTurnRatio]
        factor_InvTurn_one_year = [InventoryTurnRatio]
        date_one_year = get_trading_date_from_now(self.date, -1, ql.Years)
        df = get_factor_from_wind_v2(self.code_list, factor_list, self.date)
        # 存货增长率与营收增长率的比较判断数据，使用存货周转率判断
        df_invturn_now = get_factor_from_wind_v2(self.code_list, factor_InvTurn_now, self.date)
        df_invturn_now.rename(columns={'存货周转率': '存货周转率_今年'}, inplace=True)
        df_invturn_one_year = get_factor_from_wind_v2(self.code_list, factor_InvTurn_one_year, date_one_year)
        df_invturn_one_year.rename(columns={'存货周转率': '存货周转率_去年'}, inplace=True)
        df = pd.concat([df, df_invturn_now, df_invturn_one_year], axis=1)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        df = df[df['资产负债率'] < 0.25]
        df = df[df['每股现金流CFPS'] > 0.0]
        df = df[df['市值/企业自由现金流'] < 10.0]
        df = df[((df['净利润增长率'] + df['股息率指标'])/df['市盈率PE']) >= 2.0]
        df = df[df['存货周转率_今年'] > df['存货周转率_去年']]
        code_list = list(df.index.values)
        return code_list


class 史蒂夫路佛价值选股法(MasterStratery):
    '''选股条件：
1.市净率低于全市场平均值。
2.以五年平均盈余计算的PE 低于全市场平均值。
3.股息收益率不低于全市场平均值。
4.股价现金流量比低于全市场平均值。
5.长期借款占总资本比率低于50%'''
    def _get_data(self):
        from single_factor import PB, PE, DividendYield, PriceFreeCashFlowPerShare, LongTermLiabilityToWorkCapital
        factor_list = [PB, DividendYield, PriceFreeCashFlowPerShare, LongTermLiabilityToWorkCapital]
        df = get_factor_from_wind_v2(self.code_list, factor_list, self.date)
        # 五年PE值获取
        df_PE = []
        for i in range(5):
            date_temp = get_trading_date_from_now(self.date, -i, ql.Years)
            df_temp = get_factor_from_wind_v2(self.code_list, [PE], date_temp)
            df_temp.rename(columns={'市盈率PE': '市盈率_'+str(i)}, inplace=True)
            df_PE.append(df_temp)
        df = pd.concat([df]+df_PE, axis=1)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        PE_median = (df['市盈率_0'] + df['市盈率_1'] + df['市盈率_2'] + df['市盈率_3'] + df['市盈率_4']).median()
        df = df[(df['市盈率_0'] + df['市盈率_1'] + df['市盈率_2'] + df['市盈率_3'] + df['市盈率_4']) < PE_median]
        df = df[df['PB市净率指标'] < df['PB市净率指标'].median()]
        df = df[df['股息率指标'] >= df['股息率指标'].median()]
        df = df[df['股价_每股企业自由现金流'] < df['股价_每股企业自由现金流'].median()]
        df = df[df['长期负债/营运资金'] < 0.5]
        code_list = list(df.index.values)
        return code_list


class 霍华罗斯曼审慎致富投资法(MasterStratery):
    '''选股条件：
1.总市值≧市场平均值*1.0。
2.最近一季流动比率≧市场平均值。
3.近四季股东权益报酬率≧市场平均值。
4.近五年自由现金流量均为正值。
5.近四季营收成长率介于6%至30%。
6.近四季盈余成长率介于8%至50%
    '''
    def _get_data(self):
        from single_factor import LCap, CurrentRatio, ROE, FreeCashFlowPerShare, OperationRevenueGrowth, NetProfitGrowRateV2
        factor_list = [LCap, CurrentRatio, ROE, OperationRevenueGrowth, NetProfitGrowRateV2]
        df = get_factor_from_wind_v2(self.code_list, factor_list, self.date)
        # 五年自由现金流量
        df_PE = []
        for i in range(5):
            date_temp = get_trading_date_from_now(self.date, -i, ql.Years)
            df_temp = get_factor_from_wind_v2(self.code_list, [FreeCashFlowPerShare], date_temp)
            df_temp.rename(columns={'每股企业自由现金流指标': '每股企业自由现金流指标_' + str(i)}, inplace=True)
            df_PE.append(df_temp)
        df = pd.concat([df] + df_PE, axis=1)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        df = df[df['对数市值'] >= df['对数市值'].median()]
        df = df[df['流动比率'] >= df['流动比率'].median()]
        df = df[df['权益回报率ROE'] >= df['权益回报率ROE'].median()]
        df = df[(df['营业收入增长率'] >= 0.06) & (df['营业收入增长率'] <= 0.3)]
        df = df[(df['净利润增长率'] >= 0.08) & (df['营业收入增长率'] <= 0.5)]
        df = df[(df['每股企业自由现金流指标_0'] > 0.0) & (df['每股企业自由现金流指标_1'] > 0.0) & (df['每股企业自由现金流指标_2'] > 0.0) & (df['每股企业自由现金流指标_3'] > 0.0) & (df['每股企业自由现金流指标_4'] > 0.0)]
        code_list = list(df.index.values)
        return code_list