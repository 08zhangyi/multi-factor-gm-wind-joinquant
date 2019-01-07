import numpy as np
from WindPy import w
import cvxopt
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import list_wind2jq, list_jq2wind, SW1_INDEX


class WeightsAllocation(object):
    def __init__(self, code_list, date):
        self.code_list = code_list  # code_list用掘金的格式
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
        weight_value = self._calc_weights(code_list)
        code_weights = {}
        for i in range(len(code_list)):
            code = code_list[i]
            code_weights[list_wind2jq([code])[0]] = weight_value[i]
        return code_weights

    def _get_coef(self, code_list):
        # 提供_calc_weights需要计算的参数
        w.start()
        return_value = np.array(w.wsd(code_list, "pct_chg", "ED-" + str(self.N - 1) + "TD", self.date, "").Data)
        return_cov = np.cov(return_value)
        return return_cov

    def _calc_weights(self, code_list):
        # 方差极小化权重计算
        cov_mat = self._get_coef(code_list)
        n = len(cov_mat)  # 资产个数
        P = cvxopt.matrix(cov_mat)
        q = cvxopt.matrix(0.0, (n, 1))
        # 禁止做空的限制，Gx <= h
        G = cvxopt.matrix(-np.identity(n))
        h = cvxopt.matrix(0.0, (n, 1))
        # 权重求和为一，Ax = b
        A = cvxopt.matrix(1.0, (1, n))
        b = cvxopt.matrix(1.0)
        init_x = cvxopt.matrix(1.0/n, (n, 1))
        sol = cvxopt.solvers.qp(P, q, G, h, A, b, initvals={'x': init_x})
        weights = np.array(sol['x']).squeeze()
        return weights


# 用协方差矩阵计算权重系列
class 最大分散化组合_基本版(方差极小化权重_基本版):
    def _calc_weights(self, code_list):
        # 最大分散化权重计算
        cov_mat = self._get_coef(code_list)
        n = len(cov_mat)  # 资产个数
        P = cvxopt.matrix(cov_mat)
        q = cvxopt.matrix(0.0, (n, 1))
        omega_diag = np.sqrt(cov_mat.diagonal())
        # exp_rets*x >= 1 and x >= 0，组合收益大于等于1且禁止做空，Gx <= h
        G = cvxopt.matrix(np.vstack((-omega_diag, -np.identity(n))))
        h = h = cvxopt.matrix(np.vstack((-1.0, np.ones((n, 1)) * -0.0)))
        init_x = cvxopt.matrix(1.0 / n, (n, 1))
        sol = cvxopt.solvers.qp(P, q, G, h, initvals={'x': init_x})
        weights = np.array(sol['x']).squeeze()
        weights /= weights.sum()
        return weights


class 最大分散化组合_基本版_OAS(最大分散化组合_基本版):
    def _get_coef(self, code_list):
        # 提供_calc_weights需要计算的参数
        w.start()
        return_value = np.array(w.wsd(code_list, "pct_chg", "ED-" + str(self.N - 1) + "TD", self.date, "").Data)
        from sklearn.covariance import OAS
        return_cov = OAS().fit(return_value.transpose())
        return_cov = return_cov.covariance_
        return return_cov


# 按照行业进行权重配置，行业内股票等权配置
class 方差极小化权重_行业版(方差极小化权重_基本版):
    def get_weights(self):
        code_list = list_jq2wind(self.code_list)
        SW1_code_list = [t[0] for t in SW1_INDEX]
        weight_value = self._calc_weights(SW1_code_list)  # 提取行业权重
        industry_list = w.wss(code_list, "indexcode_sw", "tradeDate="+self.date+";industryType=1").Data[0]
        weight_value_temp = []
        for i in range(len(code_list)):
            industry_temp = industry_list[i]
            if industry_temp is None:  # 个股无行业分类数据的处理
                weight_value_temp.append(0.0)
            else:
                industry_index = SW1_code_list.index(industry_temp)
                weight_value_temp.append(weight_value[industry_index])
        weight_value_temp = np.array(weight_value_temp)
        weight_value_temp = weight_value_temp / np.sum(weight_value_temp)  # 权重归一化
        code_weights = dict([[list_wind2jq([code_list[i]])[0], weight_value_temp[i]] for i in range(len(code_list))])
        return code_weights


# 按照行业进行权重配置，行业内股票等权配置
class 最大分散化组合_行业版(方差极小化权重_行业版):
    def _calc_weights(self, code_list):
        # 最大分散化权重计算
        cov_mat = self._get_coef(code_list)
        n = len(cov_mat)  # 资产个数
        P = cvxopt.matrix(cov_mat)
        q = cvxopt.matrix(0.0, (n, 1))
        omega_diag = np.sqrt(cov_mat.diagonal())
        # exp_rets*x >= 1 and x >= 0，组合收益大于等于1且禁止做空，Gx <= h
        G = cvxopt.matrix(np.vstack((-omega_diag, -np.identity(n))))
        h = cvxopt.matrix(np.vstack((-1.0, np.ones((n, 1)) * -0.0)))
        init_x = cvxopt.matrix(1.0 / n, (n, 1))
        sol = cvxopt.solvers.qp(P, q, G, h, initvals={'x': init_x})
        weights = np.array(sol['x']).squeeze()
        weights /= weights.sum()
        for i in range(28):
            print('第%d个行业的权重为%.2f%%' % (i + 1, weights[i] * 100.0))
        return weights


class 最大分散化组合_行业版_OAS(最大分散化组合_行业版):
    def _get_coef(self, code_list):
        # 提供_calc_weights需要计算的参数
        w.start()
        return_value = np.array(w.wsd(code_list, "pct_chg", "ED-" + str(self.N - 1) + "TD", self.date, "").Data)
        from sklearn.covariance import OAS
        return_cov = OAS().fit(return_value.transpose())
        return_cov = return_cov.covariance_
        return return_cov


if __name__ == '__main__':
    model = 最大分散化组合_基本版(['000002.XSHE', '600000.XSHG', '002415.XSHE', '601012.XSHG', '601009.XSHG'], '2018-11-22')
    print(model.get_weights())