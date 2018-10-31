import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
from single_factor import SW1Industry, SW1IndustryOneHot
# 后处理测试用的因子
from single_factor import VOL10, RSI, PE
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_factor_from_wind_v2


# 因子后处理基类
class 因子后处理(object):
    def __init__(self, factor_df):
        self.factor_df = factor_df

    def get_factor_df(self):
        return self.factor_df


if __name__ == '__main__':
    factor_df = get_factor_from_wind_v2(['000002.SZ', '000016.SZ', '600004.SH', '600008.SH'], [VOL10, RSI, PE], '2018-10-30')
    factor_df = 因子后处理(factor_df).get_factor_df()
    print(factor_df)