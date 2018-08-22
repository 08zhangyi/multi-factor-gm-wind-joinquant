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


class 彼得_林奇基层调查选股策略说明(MasterStratery):
    '''选股条件：
1.公司的资产负债率小于等于 25%;
2.公司每股净现金大于 0；
3.当前股价与每股自由现金流量比小于10；
4.公司的存货成长率小于其营收增长率；
5.（长期盈余成长率+股息率）/市盈率大于等于 2；
    '''
    def __init__(self,  code_list, date):
        super().__init__(code_list, date)
        from single_factor import DebetToAsset, CFPS, MarketValueToFreeCashFlow, NetProfitGrowRateV2, DividendYield, PE, InventoryTurnRatio
        self.factor_list = [DebetToAsset, CFPS, MarketValueToFreeCashFlow, NetProfitGrowRateV2, DividendYield, PE]
        self.factor_InvTurn_now = [InventoryTurnRatio]
        self.factor_InvTurn_one_year = [InventoryTurnRatio]
        self.date_one_year = get_trading_date_from_now(self.date, -1, ql.Years)

    def select_code(self):
        df = get_factor_from_wind_v2(self.code_list, self.factor_list, self.date)
        # 存货增长率与营收增长率的比较判断数据，使用存货周转率判断
        df_invturn_now = get_factor_from_wind_v2(self.code_list, self.factor_InvTurn_now, self.date)
        df_invturn_now.rename(columns={'存货周转率': '存货周转率_今年'}, inplace=True)
        df_invturn_one_year = get_factor_from_wind_v2(self.code_list, self.factor_InvTurn_one_year, self.date_one_year)
        df_invturn_one_year.rename(columns={'存货周转率': '存货周转率_去年'}, inplace=True)
        df = pd.concat([df, df_invturn_now, df_invturn_one_year], axis=1)
        df = df.dropna()
        df = df[df['资产负债率'] < 0.25]
        df = df[df['每股现金流CFPS'] > 0.0]
        df = df[df['市值/企业自由现金流'] < 10.0]
        df = df[((df['净利润增长率'] + df['股息率指标'])/df['市盈率PE']) >= 2.0]
        df = df[df['存货周转率_今年'] > df['存货周转率_去年']]
        code_list = list(df.index.values)
        print(code_list)
        return code_list