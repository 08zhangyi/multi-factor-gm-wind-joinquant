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
6.近四季盈余成长率介于8%至50%'''
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


class 麦克贝利222选股法则(MasterStratery):
    '''选股条件：
1.股票预期市盈率低于市场平均预期市盈率的“2”分之一（股票需要具备较低的估值）
2.公司预期盈利成长率大于市场平均预估盈利成长率的“2”分之一（公司的未来具备较高的盈利成长能力）
3.股票的市净率小于“2"（青睐重资产行业）'''
    def _get_data(self):
        from single_factor import EstimatePEFY1, EstimateNetProfitGrowRateFY16M, PB
        factor_list = [EstimatePEFY1, EstimateNetProfitGrowRateFY16M, PB]
        df = get_factor_from_wind_v2(self.code_list, factor_list, self.date)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        df = df[df['预测PE（FY1）'] < df['预测PE（FY1）'].median()*0.5]
        df = df[df['一致预测净利润增长率（6个月数据计算）'] > df['一致预测净利润增长率（6个月数据计算）'].median()*0.5]
        df = df[df['PB市净率指标'] < 2.0]
        code_list = list(df.index.values)
        return code_list


class 本杰明格雷厄姆成长股内在价值投资法(MasterStratery):
    '''选股条件：
1.Value = EPS *（8.5 + 2 * ExpectedReturn） 8.5为盈利增长等于0的公司的市盈率
注：ExpectedReturn=0.05'''
    def __init__(self, code_list, date, N):
        super().__init__(code_list, date)
        from single_factor import DilutedEPS, ForecastEarningGrowth_FY1_3M
        self.factor_list = [DilutedEPS, ForecastEarningGrowth_FY1_3M]
        self.N = N

    def _get_data(self):
        from single_factor import DilutedEPS, ForecastEarningGrowth_FY1_3M
        factor_list = [DilutedEPS, ForecastEarningGrowth_FY1_3M]
        df = get_factor_from_wind_v2(self.code_list, factor_list, self.date)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        eps = df['稀释每股收益']
        forcast = df['三个月个月盈利变化率（一年）预测'] / 100.0
        value = eps * (8.5 + 2 * forcast)
        share_code = value[value > value.quantile(self.N)]
        code_list = list(share_code.index.values)
        return code_list


class 本杰明格雷厄姆成长股内在价值投资法v2(MasterStratery):
    '''选股条件：
1.Value = EPS *（8.5 + 2 * ExpectedReturn） 8.5为盈利增长等于0的公司的市盈率
注：ExpectedReturn=5.0'''
    def __init__(self, code_list, date, N):
        super().__init__(code_list, date)
        self.N = N

    def _get_data(self):
        from single_factor import DilutedEPS, EstimateNetProfitGrowRateFY16M
        factor_list = [DilutedEPS, EstimateNetProfitGrowRateFY16M]
        df = get_factor_from_wind_v2(self.code_list, factor_list, self.date)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        eps = df['稀释每股收益']
        forcast = df['一致预测净利润增长率（6个月数据计算）']
        value = eps * (8.5 + 2 * forcast)
        share_code = value[value > value.quantile(self.N)]
        code_list = list(share_code.index.values)
        return code_list

class  本杰明格雷厄姆企业主投资法(MasterStratery):
    '''选股条件
---1．股票的市盈率低于市场平均水平
---2．股票的市净率小于 1.2
---3．企业的流动资产至少是流动负债的 1.5 倍 (流动比率MRQ）
4．企业的总借款不超过净流动资产的 1.1 倍
5．最近五年净利润大于 0
6．最近一期现金股利大于 0
7．盈利（TTM）大于三年前的盈利'''