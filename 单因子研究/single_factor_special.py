# 单因子提取器，一些特殊的不符合三级结构的因子写在本文件
from WindPy import w
import numpy as np
import pandas as pd
# import datetime
# import QuantLib as ql
# import abc
# from sklearn.linear_model import LinearRegression

import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
# from utils import get_trading_date_from_now, SW1_INDEX, ZX1_INDEX
from single_factor import SingleFactorReasearch


# 区间收益率
class ReturnsOneMonth(SingleFactorReasearch):
    def __init__(self, date_start, date_end, code_list):
        factor_name = '区间收益率'
        super().__init__(date_start, code_list, factor_name)
        self.date_start = date_start
        self.date_end = date_end

    def _calculate_factor(self):
        returns = np.array(w.wss(self.code_list, "pct_chg_per", "startDate="+self.date_start+";endDate="+self.date_end).Data[0])
        df = pd.DataFrame(data=returns, index=self.code_list, columns=[self.factor_name])
        return df