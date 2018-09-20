import numpy as np
from WindPy import w
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import list_wind2jq, list_jq2wind



class WeightsAllocation(object):
    def __init__(self, code_list, date):
        self.code_list = code_list
        self.date = date  # date日收盘后计算配置比例

    def get_weights(self):
        pass


class 等权持仓(WeightsAllocation):
    def get_weights(self):
        code_weights = {}
        for code in self.code_list:
            code_weights[code] = 1.0 / len(self.code_list)
        return code_weights


class 指数权重(WeightsAllocation):
    def __init__(self, code_list, date, index_code):
        # 按照index_code的编制权重配置，code_list的股票应为index_code的成分股
        self.index_code = index_code
        super().__init__(code_list, date)

    def get_weights(self):
        w.start()
        index_data = w.wset("indexconstituent", "date="+self.date+";windcode="+self.index_code).Data
        index_data_code = index_data[1]
        index_data_weight = index_data[3]
        code_weights_all = dict(zip(index_data_code, index_data_weight))
        code_weights = {}
        for code in self.code_list:
            try:
                code_weights[code] = code_weights_all[list_jq2wind([code])[0]]
            except KeyError:
                code_weights[code] = 0.0
        all_weights = np.sum(np.array([t for t in code_weights.values()]))
        for code in self.code_list:
            try:
                code_weights[code] = code_weights_all[list_jq2wind([code])[0]] / all_weights
            except KeyError:
                code_weights[code] = 0.0
        return code_weights