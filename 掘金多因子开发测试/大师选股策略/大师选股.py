import QuantLib as ql
import pandas as pd
from WindPy import w
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
# 引入工具函数和学习器
from utils import get_factor_from_wind_without_cache, get_trading_date_from_now


class MasterStrategy(object):
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


class AllCode(MasterStrategy):
    def select_code(self):
        return self.code_list


class 彼得林奇基层调查选股策略说明(MasterStrategy):
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
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        # 存货增长率与营收增长率的比较判断数据，使用存货周转率判断
        df_invturn_now = get_factor_from_wind_without_cache(self.code_list, factor_InvTurn_now, self.date)
        df_invturn_now.rename(columns={'存货周转率': '存货周转率_今年'}, inplace=True)
        df_invturn_one_year = get_factor_from_wind_without_cache(self.code_list, factor_InvTurn_one_year, date_one_year)
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


class 史蒂夫路佛价值选股法(MasterStrategy):
    '''选股条件：
1.市净率低于全市场平均值。
2.以五年平均盈余计算的PE 低于全市场平均值。
3.股息收益率不低于全市场平均值。
4.股价现金流量比低于全市场平均值。
5.长期借款占总资本比率低于50%'''
    def _get_data(self):
        from single_factor import PB, PE, DividendYield, PriceFreeCashFlowPerShare, LongTermLiabilityToWorkCapital
        factor_list = [PB, DividendYield, PriceFreeCashFlowPerShare, LongTermLiabilityToWorkCapital]
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        # 五年PE值获取
        df_PE = []
        for i in range(5):
            date_temp = get_trading_date_from_now(self.date, -i, ql.Years)
            df_temp = get_factor_from_wind_without_cache(self.code_list, [PE], date_temp)
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


class 霍华罗斯曼审慎致富投资法(MasterStrategy):
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
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        # 五年自由现金流量
        df_PE = []
        for i in range(5):
            date_temp = get_trading_date_from_now(self.date, -i, ql.Years)
            df_temp = get_factor_from_wind_without_cache(self.code_list, [FreeCashFlowPerShare], date_temp)
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
        df = df[(df['营业收入增长率'] >= 6.0)]
        df = df[(df['营业收入增长率'] <= 30.0)]
        df = df[df['净利润增长率'] >= 8.0]
        df = df[df['净利润增长率'] <= 50.0]
        df = df[(df['每股企业自由现金流指标_0'] > 0.0) & (df['每股企业自由现金流指标_1'] > 0.0) & (df['每股企业自由现金流指标_2'] > 0.0) &\
                (df['每股企业自由现金流指标_3'] > 0.0) & (df['每股企业自由现金流指标_4'] > 0.0)]
        code_list = list(df.index.values)
        return code_list


class 麦克贝利222选股法则(MasterStrategy):
    '''选股条件：
1.股票预期市盈率低于市场平均预期市盈率的“2”分之一（股票需要具备较低的估值）
2.公司预期盈利成长率大于市场平均预估盈利成长率的“2”分之一（公司的未来具备较高的盈利成长能力）
3.股票的市净率小于“2"（青睐重资产行业）'''
    def _get_data(self):
        from single_factor import EstimatePEFY1, EstimateNetProfitGrowRateFY1_6M, PB
        factor_list = [EstimatePEFY1, EstimateNetProfitGrowRateFY1_6M, PB]
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        df = df[df['预测PE（FY1）'] < df['预测PE（FY1）'].median()*0.5]
        df = df[df['一致预测净利润增长率（6个月数据计算）'] > df['一致预测净利润增长率（6个月数据计算）'].median()*0.5]
        df = df[df['PB市净率指标'] < 2.0]
        code_list = list(df.index.values)
        return code_list


class 本杰明格雷厄姆成长股内在价值投资法(MasterStrategy):
    '''选股条件：
1.Value = EPS *（8.5 + 2 * ExpectedReturn） 8.5为盈利增长等于0的公司的市盈率
注：ExpectedReturn=0.05'''
    def __init__(self, code_list, date, N):
        super().__init__(code_list, date)
        self.N = N  # 取对应分位数排名

    def _get_data(self):
        from single_factor import DilutedEPS, ForecastEarningGrowth_FY1_3M
        factor_list = [DilutedEPS, ForecastEarningGrowth_FY1_3M]
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
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


class 本杰明格雷厄姆成长股内在价值投资法v2(MasterStrategy):
    '''选股条件：
1.Value = EPS *（8.5 + 2 * ExpectedReturn） 8.5为盈利增长等于0的公司的市盈率
注：ExpectedReturn=5.0'''
    def __init__(self, code_list, date, N):
        super().__init__(code_list, date)
        self.N = N  # 取对应分位数排名

    def _get_data(self):
        from single_factor import DilutedEPS, EstimateNetProfitGrowRateFY1_6M
        factor_list = [DilutedEPS, EstimateNetProfitGrowRateFY1_6M]
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
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


class 戴维斯双击v1(MasterStrategy):
    '''选股条件：
1.净利润ttm增速>0%，三个月前净利润ttm>300万*4
2.三个月前净利润ttm增速>0%
3.(净利润ttm增速-三个月前净利润ttm增速)>0%（加速增长）
4.三个月前营业收入ttm>0
5.按照第3条排名取最高的前25个股票'''
    def __init__(self, code_list, date, N=25):
        super().__init__(code_list, date)
        self.N = N  # N为选股的个数，默认为25个

    def _get_data(self):
        from single_factor import NetProfitGrowRateV2, NetProfit, Revenue
        factor_list = [NetProfitGrowRateV2, NetProfit]
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        date_temp = get_trading_date_from_now(self.date, -3, ql.Months)
        df_temp = get_factor_from_wind_without_cache(self.code_list, [NetProfitGrowRateV2, Revenue], date_temp)
        df_temp.rename(columns={'净利润增长率': '净利润增长率_3个月前'}, inplace=True)
        df_temp_1 = df['净利润增长率'] - df_temp['净利润增长率_3个月前']
        df = pd.concat([df, df_temp, df_temp_1], axis=1)
        df.rename(columns={0: '差值'}, inplace=True)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        df = df[df['净利润'] > 12000000.0]
        df = df[df['净利润增长率'] > 0.0]
        df = df[df['净利润增长率_3个月前'] > 0.0]
        df = df[df['营业收入'] > 0.0]
        df = df[df['差值'] > 0.0]
        df = df.sort_values(by='差值', axis=0, ascending=False)
        df = df.head(self.N)

        code_list = list(df.index.values)
        return code_list


class 戴维斯双击v2(MasterStrategy):
    '''选股条件：
1.净利润ttm增速>0%，三个月前净利润ttm>300万*4
2.三个月前净利润ttm增速>0%
3.(净利润ttm增速-三个月前净利润ttm增速)>0%（加速增长）
4.三个月前营业收入ttm>0
5.按照第3条排名取最高的前25个股票
6.PE < 50.0'''
    def __init__(self, code_list, date, N=25):
        super().__init__(code_list, date)
        self.N = N  # N为选股的个数，默认为25个

    def _get_data(self):
        from single_factor import NetProfitGrowRateV2, NetProfit, Revenue, PE
        factor_list = [NetProfitGrowRateV2, NetProfit, PE]
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        date_temp = get_trading_date_from_now(self.date, -3, ql.Months)
        df_temp = get_factor_from_wind_without_cache(self.code_list, [NetProfitGrowRateV2, Revenue], date_temp)
        df_temp.rename(columns={'净利润增长率': '净利润增长率_3个月前'}, inplace=True)
        df_temp_1 = df['净利润增长率'] - df_temp['净利润增长率_3个月前']
        df = pd.concat([df, df_temp, df_temp_1], axis=1)
        df.rename(columns={0: '差值'}, inplace=True)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        df = df[df['市盈率PE'] < 50.0]
        df = df[df['净利润'] > 12000000.0]
        df = df[df['净利润增长率'] > 0.0]
        df = df[df['净利润增长率_3个月前'] > 0.0]
        df = df[df['营业收入'] > 0.0]
        df = df[df['差值'] > 0.0]
        df = df.sort_values(by='差值', axis=0, ascending=False)
        df = df.head(self.N)

        code_list = list(df.index.values)
        return code_list


class 戴维斯双击v3(MasterStrategy):
    '''选股条件：
1.净利润ttm增速>0%，三个月前净利润ttm>300万*4
2.三个月前净利润ttm增速>0%
3.(净利润ttm增速-三个月前净利润ttm增速)>0%（加速增长）
4.三个月前营业收入ttm>0
5.按照第3条排名取最高的前25个股票
6.PE < 50.0'''
    def __init__(self, code_list, date, N=25):
        super().__init__(code_list, date)
        self.N = N  # N为选股的个数，默认为25个

    def _get_data(self):
        from single_factor import NetProfitGrowRateV2, NetProfit, Revenue, PE
        factor_list = [NetProfitGrowRateV2, NetProfit,PE]
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        date_temp = get_trading_date_from_now(self.date, -3, ql.Months)
        df_temp = get_factor_from_wind_without_cache(self.code_list, [NetProfitGrowRateV2, Revenue], date_temp)
        df_temp.rename(columns={'净利润增长率': '净利润增长率_3个月前'}, inplace=True)
        df_temp_1 = df['净利润增长率'] - df_temp['净利润增长率_3个月前']
        df = pd.concat([df, df_temp, df_temp_1], axis=1)
        df.rename(columns={0: '差值'}, inplace=True)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        df = df[df['市盈率PE'] < 50.0]
        df = df[df['净利润'] > 12000000.0]
        df = df[df['净利润增长率'] > 0.0]
        df = df[df['净利润增长率_3个月前'] > 0.0]
        df = df[df['营业收入'] > 0.0]
        df = df[(df['差值'] > 20.0) & (df['差值'] < 100.0)]
        df = df.sort_values(by='差值', axis=0, ascending=False)
        df = df.head(self.N)

        code_list = list(df.index.values)
        return code_list


class 戴维斯双击v4(MasterStrategy):
    '''选股条件：
1.净利润ttm增速>0%，三个月前净利润ttm>300万*4
2.三个月前净利润ttm增速>0%
3.(净利润ttm增速-三个月前净利润ttm增速)>0%（加速增长）
4.三个月前营业收入ttm>0
5.按照第3条排名取最高的前25个股票
6.PE < 50.0'''
    def __init__(self, code_list, date, N=25):
        super().__init__(code_list, date)
        self.N = N  # N为选股的个数，默认为25个

    def _get_data(self):
        from single_factor import NetProfitGrowRateV2, NetProfit, Revenue, PE
        factor_list = [NetProfitGrowRateV2, NetProfit,PE]
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        date_temp = get_trading_date_from_now(self.date, -3, ql.Months)
        df_temp = get_factor_from_wind_without_cache(self.code_list, [NetProfitGrowRateV2, Revenue], date_temp)
        df_temp.rename(columns={'净利润增长率': '净利润增长率_3个月前'}, inplace=True)
        df_temp_1 = df['净利润增长率'] - df_temp['净利润增长率_3个月前']
        df = pd.concat([df, df_temp, df_temp_1], axis=1)
        df.rename(columns={0: '差值'}, inplace=True)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        df = df[df['市盈率PE'] < 50.0]
        df = df[df['净利润'] > 12000000.0]
        df = df[df['净利润增长率'] > 0.0]
        df = df[df['净利润增长率_3个月前'] > 0.0]
        df = df[df['营业收入'] > 0.0]
        df_temp1 = df[(df['差值'] > 20.0) & (df['差值'] < 100.0)]
        df_temp2 = df[df['差值'] >= 100.0]
        if len(df_temp1) >= self.N:
            df = df_temp1.sort_values(by='差值', axis=0, ascending=False)
            df = df.head(self.N)
        if len(df_temp1) < self.N:
            df_temp2 = df_temp2.sort_values(by='差值', axis=0, ascending=True)
            df_temp2 = df_temp2.head(self.N - len(df_temp1))
            df_temp1 = df_temp1.sort_values(by='差值', axis=0, ascending=False)
            df = pd.concat([df_temp1, df_temp2], axis=0)

        code_list = list(df.index.values)
        return code_list


# 投资十法
class 本杰明格雷厄姆经典价值投资法(MasterStrategy):
    ''' 选股条件
价值五法：
1.股票的盈利回报率（市盈率倒数）应大于美国AAA 级债券收益的2 倍。例如某只股票的市盈率为10 倍，则盈利回报率为10%，
    如AAA债券收益率为4%,则该只股票的盈利回报率满足条件；(直接用PE值）
2.股票的市盈率应小于其过去五年最高市盈率的40%。
3.股票派息率应大于美国AAA 级债券收益率的2/3。
4.股价要低于每股有形资产净值的2/3。  # 每股有形资产 vs 每股净资产
5.股价要低于每股净流动资产（流动资产-总负债）的2/3。

安全五法：
1.总负债要小于有形资产净值。
2.流动比率（流动资产/流动负债）要大于2。
3.总负债要要小于净流动资产的2 倍。
4.过去10 年的平均年化盈利增长率要大于7%。
5.过去十年中不能超过2 次的盈利增长率小于-5%。'''
    def __init__(self, code_list, date, N=1):
        super().__init__(code_list, date,)
        self.N = N

    def _get_data(self):
        from single_factor import ClosePrice, PE, DividendYield, NetTangibleAssetPerShare, NetLiquidAssetPerShare, TotalLiability, NetLiquidAsset, NetTangibleAsset, CurrentRatio, NetProfitGrowRateV2
        factor_list = [ClosePrice, PE, DividendYield, NetTangibleAssetPerShare, NetLiquidAssetPerShare, TotalLiability, NetLiquidAsset, NetTangibleAsset, CurrentRatio, NetProfitGrowRateV2]
        # factor_list = [PE_MAX] # 待添加到上述列表，条件筛选不完整
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        date_temp_1 = get_trading_date_from_now(self.date, -3, ql.Days)  # 取3天前国债收益率
        yield_data = w.wss("TB" + str(self.N) + "Y.WI", "close", "tradeDate=" + str(date_temp_1) + ";priceAdj=U;cycle=D").Data[0][0]
        df = df.dropna()
        return df, yield_data

    def select_code(self):
        df, TB_yield = self._get_data()
        df = df[df['市盈率PE'] < (1.0/(TB_yield*0.005))]  # 此处2倍 可以修改 0.02
        # print(1.0/(TB_yield*0.005))  # 打印PE筛选条件
        # df = df[df['市盈率PE'] < (df['过去5年最大PE值']*0.40)]  # 待优化 数据量太大
        df = df[df['股息率指标'] > (TB_yield*0.5)]  # 原值2/3
        # df = df[df['每股净有形资产'] > (df['收盘价'])]   # 原值 2/3  打开即崩
        # df = df[df['每股净流动资产'] > (df['收盘价'])]    # 原值 2/3  打开即崩
        # 安全5法
        # df = df[df['总负债'] < df['有形资产净值']]  # 数据接口提取不稳定 出现None较多
        df = df[df['流动比率'] > 1.0]  # 原值 2.0
        df = df[(df['总负债']*1.0) < df['净流动资产']]  # 原值2.0
        df = df[df['净利润增长率'] > 7.0]  # 原值7.0
        code_list = list(df.index.values)
        return code_list


class 柯林麦克连成长价值优势投资法(MasterStrategy):
    ''' 选股条件
1.年度营收成长率> 前一年度营收成长率，
2.预估营收成长率> 年度营收成长率，
3.最近三年每股自由现金流量皆> 0，
4.近四季营业利益率>= 10 %，
5.最近四季可运用资本报酬率>= 10 %，
6.最近年度有效税率>= 5 %，
7.高估/低估指数(股价营收比*边际获利乘数) <= 1。
'''
    def __init__(self, code_list, date,):
        super().__init__(code_list, date, )

    def _get_data(self):
        from single_factor import OperationRevenueGrowth, EstimateNetRevenueGrowRateFY1_6M, FreeCashFlowPerShare, GrossIncomeRatio, ROC, EffectiveTaxRate, PS
        factor_list = [OperationRevenueGrowth, EstimateNetRevenueGrowRateFY1_6M, FreeCashFlowPerShare, GrossIncomeRatio, ROC, EffectiveTaxRate, PS]
        date_one_year = get_trading_date_from_now(self.date, -1, ql.Years)
        date_two_year = get_trading_date_from_now(self.date, -2, ql.Years)
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        df_Revenue_growth_one_year = get_factor_from_wind_without_cache(self.code_list, [OperationRevenueGrowth], date_one_year)
        df_Revenue_growth_one_year.rename(columns={'营业收入增长率': '营业收入增长率_去年'}, inplace=True)
        df_FreeCashFlowPerShare_one_year = get_factor_from_wind_without_cache(self.code_list, [FreeCashFlowPerShare], date_one_year)
        df_FreeCashFlowPerShare_one_year.rename(columns={'每股企业自由现金流': '每股企业自由现金流_去年'}, inplace=True)
        df_FreeCashFlowPerShare_two_year = get_factor_from_wind_without_cache(self.code_list, [FreeCashFlowPerShare], date_two_year)
        df_FreeCashFlowPerShare_two_year.rename(columns={'每股企业自由现金流': '每股企业自由现金流_前年'}, inplace=True)
        df_temp = df['市销率'] * df['销售毛利率'] * 10.0  # 边际获利乘数即：销售毛利率*10

        df = pd.concat([df, df_Revenue_growth_one_year,df_FreeCashFlowPerShare_one_year,df_FreeCashFlowPerShare_two_year, df_temp], axis=1)
        df.rename(columns={0: '高估/低估指数'}, inplace=True)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        df = df[df['营业收入增长率'] > df['营业收入增长率_去年']]   # 可以尝试>0
        # df = df[df['一致预测营业收入增长率（6个月数据计算）'] > df['营业收入增长率']]
        df = df[df['一致预测营业收入增长率（6个月数据计算）'] > 0.0]  # 上一行为原文条件
        df = df[df['每股企业自由现金流'] > 0.0]
        # df = df[df['每股企业自由现金流_去年'] > 0]
        # df = df[df['每股企业自由现金流_前年'] > 0]
        df = df[df['销售毛利率'] >= 0.10]
        df = df[df['资本回报率ROC'] > 5.0]  # 原值10.0
        df = df[df['实际税率'] >= 0.05]  # 原值0.05
        df = df[df['高估/低估指数'] <= 20.0]  # 原值1.0

        code_list = list(df.index.values)
        return code_list


class 必要消费(MasterStrategy):
    def __init__(self, code_list, date,):
        super().__init__(code_list, date, )

    def _get_data(self):
        from single_factor import SteadyProfitAcc, InventoryTurnRatio, PB
        factor_list = [SteadyProfitAcc, InventoryTurnRatio, PB]
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        df = df[df['利润稳健加速度'] > df['利润稳健加速度'].quantile(1/3)]
        df = df[df['存货周转率'] > df['存货周转率'].quantile(0.5)]
        df = df[df['PB市净率指标'] < df['PB市净率指标'].quantile(1/3)]
        code_list = list(df.index.values)
        return code_list


class 北上资金趋势选股V1(MasterStrategy):
    def __init__(self, code_list, date):
        super().__init__(code_list, date)

    def _get_data(self):
        # 10日的策略
        from single_factor import ForeignCapitalHoldingRatioGrowth_LR_10
        factor_list = [ForeignCapitalHoldingRatioGrowth_LR_10]
        df = get_factor_from_wind_without_cache(self.code_list, factor_list, self.date)
        df = df.dropna()
        return df

    def select_code(self):
        df = self._get_data()
        strf = '过去10日外资持股比例增速'
        df = df[(df[strf] > df[strf].quantile(0.65)) & (df[strf] <= df[strf].quantile(0.75))]
        code_list = list(df.index.values)
        return code_list