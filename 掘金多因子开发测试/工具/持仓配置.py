import numpy as np
from WindPy import w
import cvxopt
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import list_wind2jq, list_jq2wind, SW1_INDEX


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


# 指数权重，市值权重系列
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


class 市值权重(WeightsAllocation):
    # 按照date日的总市值权调仓
    def get_weights(self):
        code_list = list_jq2wind(self.code_list)
        code_weights = {}
        w.start()
        weight_data = np.array(w.wss(code_list, "mkt_cap_ard", "unit=1;tradeDate=" + self.date + ";currencyType=").Data[0])
        weight_data = weight_data / np.sum(weight_data)
        for i in range(len(code_list)):
            code = code_list[i]
            code_weights[list_wind2jq([code])[0]] = weight_data[i]
        return code_weights


class 流通市值权重(WeightsAllocation):
    # 按照date日的流通市值权调仓
    def get_weights(self):
        code_list = list_jq2wind(self.code_list)
        code_weights = {}
        w.start()
        weight_data = np.array(w.wss(code_list, "mkt_cap_float", "unit=1;tradeDate=" + self.date + ";currencyType=").Data[0])
        weight_data = weight_data / np.sum(weight_data)
        for i in range(len(code_list)):
            code = code_list[i]
            code_weights[list_wind2jq([code])[0]] = weight_data[i]
        return code_weights


class 自由流通市值权重(WeightsAllocation):
    # 按照date日的Wind定义自由流通市值权调仓
    def get_weights(self):
        code_list = list_jq2wind(self.code_list)
        code_weights = {}
        w.start()
        weight_data = np.array(w.wss(code_list, "mkt_cap_ard", "unit=1;tradeDate=" + self.date + ";currencyType=").Data[0])
        weight_data = weight_data / np.sum(weight_data)
        for i in range(len(code_list)):
            code = code_list[i]
            code_weights[list_wind2jq([code])[0]] = weight_data[i]
        return code_weights


# 用协方差矩阵计算权重系列
class 方差极小化权重_基本版(WeightsAllocation):
    def __init__(self, code_list, date, N=60):
        self.N = N  # 收益率数据采样的历史大小，默认N=60，为一个季度的数据
        super().__init__(code_list, date)

    def get_weights(self):
        code_list = list_jq2wind(self.code_list)
        (Q, p, G, h, A, b) = self._get_coef(code_list)
        # 用CVXOPT求解方差最小的权重
        sol = cvxopt.solvers.qp(Q, p, G, h, A, b)
        # 将权重分配给代码
        weight_value = sol['x']
        code_weights = {}
        for i in range(len(code_list)):
            code = code_list[i]
            code_weights[list_wind2jq([code])[0]] = weight_value[i]
        return code_weights

    def _get_coef(self, code_list):
        w.start()
        return_value = np.array(w.wsd(code_list, "pct_chg", "ED-" + str(self.N - 1) + "TD", self.date, "").Data)
        return_cov = np.cov(return_value)
        # 为求解器提供合适的参数估计，只需修改此部分就可构造不同类型的求解器
        size = len(code_list)
        Q = cvxopt.matrix(return_cov)
        p = cvxopt.matrix(np.zeros([size]))
        G = cvxopt.matrix(-np.eye(N=size))  # 权重非负
        h = cvxopt.matrix(np.zeros(shape=[size]))
        A = cvxopt.matrix(np.ones(shape=[size]), (1, size))  # 权重和为1
        b = cvxopt.matrix(1.0)
        return Q, p, G, h, A, b


class 方差极小化权重_行业版(方差极小化权重_基本版):
    def get_weights(self):
        code_list = list_jq2wind(self.code_list)
        SW1_code_list = [t[0] for t in SW1_INDEX]
        (Q, p, G, h, A, b) = self._get_coef(SW1_code_list)
        # 用CVXOPT求解方差最小的权重
        sol = cvxopt.solvers.qp(Q, p, G, h, A, b)
        # 将权重分配给代码
        weight_value = sol['x']
        industry_list = w.wss(code_list, "indexcode_sw", "tradeDate="+self.date+";industryType=1").Data[0]
        code_weights = {}
        weight_value_temp = []
        for i in range(len(code_list)):
            code = code_list[i]
            industry_temp = industry_list[i]
            if industry_temp == None:  # 无行业数据的处理
                weight_value_temp.append(0.0)
            else:
                industry_index = SW1_code_list.index(industry_temp)
                weight_value_temp.append(weight_value[industry_index])
        weight_value_temp = np.array(weight_value_temp)
        weight_value_temp = weight_value_temp / np.sum(weight_value_temp)  # 权重归一化
        for i in range(len(code_list)):
            code = code_list[i]
            code_weights[list_wind2jq([code])[0]] = weight_value_temp[i]
        return code_weights


if __name__ == '__main__':
    model = 方差极小化权重_行业版(['000002.XSHE', '600000.XSHG', '002415.XSHE', '601012.XSHG'], '2018-10-25')
    print(model.get_weights())