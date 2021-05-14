import numpy as np
import pandas as pd
import scipy.stats, scipy.optimize
from WindPy import w
import cvxopt
import pyrb
from pypfopt.hierarchical_portfolio import HRPOpt
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import list_wind2jq, list_jq2wind, ZX1_INDEX


class WeightsAllocation(object):
    def __init__(self, code_list, date):
        w.start()
        self.code_list = code_list  # code_list用聚宽的格式
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
        WeightsAllocation.__init__(self, code_list, date)

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
        WeightsAllocation.__init__(self, code_list, date)

    def get_weights(self):
        code_list = list_jq2wind(self.code_list)
        weight_value = self._calc_weights(code_list)
        code_weights = {}
        for i in range(len(code_list)):
            code = code_list[i]
            code_weights[list_wind2jq([code])[0]] = weight_value[i]
        return code_weights

    def _get_coef(self, code_list):
        from 风险评估 import 方差风险_历史数据
        risk_model = 方差风险_历史数据(code_list, self.date, self.N)
        return_cov = risk_model.return_cov
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
        sol = cvxopt.solvers.qp(P, q, G, h, A, b)
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
        h = cvxopt.matrix(np.vstack((-1.0, np.ones((n, 1)) * -0.0)))
        sol = cvxopt.solvers.qp(P, q, G, h)
        weights = np.array(sol['x']).squeeze()
        weights /= weights.sum()
        return weights


class 最大分散化组合_基本版_OAS(最大分散化组合_基本版):
    def _get_coef(self, code_list):
        from 风险评估 import 方差风险_历史数据_OAS
        risk_model = 方差风险_历史数据_OAS(code_list, self.date, self.N)
        return_cov = risk_model.return_cov
        return return_cov


# 按照行业进行权重配置，行业内股票等权配置
class 方差极小化权重_行业版(方差极小化权重_基本版):
    def get_weights(self):
        code_list = list_jq2wind(self.code_list)
        stock_ZX1_industry_code_list = w.wss(code_list, "indexcode_citic", "industryType=1;tradeDate="+self.date).Data[0]
        ZX1_industry_code_list = list(set(stock_ZX1_industry_code_list))
        weight_value = self._calc_weights(list(set(ZX1_industry_code_list)))  # 计算股票涉及到的行业权重
        # industry_list = w.wss(code_list, "indexcode_sw", "tradeDate="+self.date+";industryType=1").Data[0]
        weight_value_temp = []
        for i in range(len(code_list)):
            industry_temp = stock_ZX1_industry_code_list[i]
            if industry_temp is None:  # 个股无行业分类数据的处理
                weight_value_temp.append(0.0)
            else:
                industry_index = ZX1_industry_code_list.index(industry_temp)
                weight_value_temp.append(weight_value[industry_index])
        weight_value_temp = np.array(weight_value_temp)
        weight_value_temp = weight_value_temp / np.sum(weight_value_temp)  # 权重归一化
        code_weights = dict([[list_wind2jq([code_list[i]])[0], weight_value_temp[i]] for i in range(len(code_list))])
        return code_weights


# 按照行业自由流通市值进行权重配置，行业内股票等权配置
class 自由流通市值权重_行业版(方差极小化权重_行业版):
    # 按照date日的Wind定义自由流通市值权调仓
    def _calc_weights(self, code_list):
        w.start()
        weight_data = np.array(w.wss(code_list, "mkt_cap_ard", "unit=1;tradeDate=" + self.date + ";currencyType=").Data[0])
        weight_data = weight_data / np.sum(weight_data)
        return weight_data


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
        sol = cvxopt.solvers.qp(P, q, G, h)
        weights = np.array(sol['x']).squeeze()
        weights /= weights.sum()
        for i in range(len(ZX1_INDEX)):
            print('第%d个行业的权重为%.2f%%' % (i + 1, weights[i] * 100.0))
        return weights


class 最大分散化组合_行业版_OAS(最大分散化组合_行业版):
    def _get_coef(self, code_list):
        from 风险评估 import 方差风险_历史数据_OAS
        risk_model = 方差风险_历史数据_OAS(code_list, self.date, self.N)
        return_cov = risk_model.return_cov
        return return_cov


class 风险平价组合_迭代求解基本版(方差极小化权重_基本版):
    def _calc_weights(self, code_list):
        # 风险平价组合，迭代法求解
        sigma = self._get_coef(code_list)
        n = len(sigma)  # 资产个数
        # 迭代法初始值
        x_0 = np.ones((n, 1)) * 1.0/n
        lambda_value_0 = np.ones((1, 1)) * 0.1
        y_0 = np.concatenate((x_0, lambda_value_0), axis=0)
        # 两个使用到的辅助函数
        def F(y):
            x = y[0:n, :]
            lambda_value = y[n, 0]
            x = np.matmul(sigma, x) - lambda_value * (1.0 / x)
            lambda_value = np.array([[np.sum(x) - 1.0]])
            F = np.concatenate((x, lambda_value), axis=0)
            return F
        def J(y):
            x = y[0:n, :]
            lambda_value = y[n, 0]
            a = lambda_value * np.diag((1.0 / (x * x))[:, 0]) + sigma
            b = -1.0 / x
            c = np.ones((1, n))
            d = np.zeros((1, 1))
            J1 = np.concatenate((a, c), axis=0)
            J2 = np.concatenate((b, d), axis=0)
            J = np.concatenate((J1, J2), axis=1)
            J = np.linalg.inv(J)  # 对J求逆
            return J
        y_n = y_0 - np.matmul(J(y_0), F(y_0))
        y_n = np.abs(y_n)
        y_n = y_n / np.sum(y_n)  # 和为一
        eps_value = np.sqrt(np.sum((y_n-y_0) * (y_n-y_0)))
        while eps_value > 1e-8:  # 计算精度评价标准
            # print(eps_value)
            y_0 = y_n
            y_n = y_0 - np.matmul(J(y_0), F(y_0))
            y_n = np.abs(y_n)
            y_n = y_n / np.sum(y_n)  # 和为一
            eps_value = np.sum((y_n-y_0) * (y_n-y_0))
        weights = y_n[0:n, 0] / np.sum(y_n[0:n, 0])
        return weights


class 风险平价组合_迭代求解基本版_OAS(风险平价组合_迭代求解基本版):
    def _get_coef(self, code_list):
        from 风险评估 import 方差风险_历史数据_OAS
        risk_model = 方差风险_历史数据_OAS(code_list, self.date, self.N)
        return_cov = risk_model.return_cov
        return return_cov


class 风险平价组合_模块求解基本版(方差极小化权重_基本版):
    def _calc_weights(self, code_list):
        # 风险平价组合，迭代法求解
        sigma = self._get_coef(code_list)
        ERC = pyrb.EqualRiskContribution(sigma)
        ERC.solve()
        weights = ERC.x
        return weights


class 风险平价组合_模块求解基本版_OAS(风险平价组合_模块求解基本版):
    def _get_coef(self, code_list):
        from 风险评估 import 方差风险_历史数据_OAS
        risk_model = 方差风险_历史数据_OAS(code_list, self.date, self.N)
        return_cov = risk_model.return_cov
        return return_cov


class 风险预算组合_模块求解基本版(方差极小化权重_基本版):
    def __init__(self, code_list, date, N=60, risk_budget=None):
        if risk_budget is None:
            self.risk_budget = np.ones(len(code_list))
        else:
            self.risk_budget = risk_budget  # 风险预算，行向量，无需归一化
        方差极小化权重_基本版.__init__(self, code_list, date, N)

    def _calc_weights(self, code_list):
        # 风险平价组合，迭代法求解
        sigma = self._get_coef(code_list)
        RB = pyrb.RiskBudgeting(sigma, self.risk_budget)
        RB.solve()
        print('风险配置比例为：', RB.get_risk_contributions())
        weights = RB.x
        return weights


class 风险预算组合_模块求解基本版_OAS(风险预算组合_模块求解基本版):
    def _get_coef(self, code_list):
        from 风险评估 import 方差风险_历史数据_OAS
        risk_model = 方差风险_历史数据_OAS(code_list, self.date, self.N)
        return_cov = risk_model.return_cov
        return return_cov


class 风险预算组合_模块求解基本版_带约束(方差极小化权重_基本版):
    def __init__(self, code_list, date, N=60, risk_budget=None, bounds=None):
        if risk_budget is None:
            self.risk_budget = np.ones(len(code_list))
        else:
            self.risk_budget = risk_budget  # 风险预算，行向量，无需归一化
        self.bounds = bounds  # 约束界，(n, 2)的np.array，n为品种个数
        方差极小化权重_基本版.__init__(self, code_list, date, N)

    def _calc_weights(self, code_list):
        # 风险平价组合，迭代法求解
        sigma = self._get_coef(code_list)
        CRB = pyrb.ConstrainedRiskBudgeting(sigma, self.risk_budget, bounds=self.bounds)
        CRB.solve()
        print('风险配置比例为：', CRB.get_risk_contributions())
        weights = CRB.x
        return weights


class 风险预算组合_模块求解基本版_带约束_OAS(风险预算组合_模块求解基本版_带约束):
    def _get_coef(self, code_list):
        from 风险评估 import 方差风险_历史数据_OAS
        risk_model = 方差风险_历史数据_OAS(code_list, self.date, self.N)
        return_cov = risk_model.return_cov
        return return_cov


class 高阶矩优化配置策略_V0(WeightsAllocation):
    def __init__(self, code_list, date, N=60, w2=1.0, w3=1.0, w4=1.0):
        self.N = N  # 收益率数据采样的历史大小，默认N=60，为一个季度的数据
        self.w2 = w2  # 优化目标函数的权重参数
        self.w3 = w3
        self.w4 = w4
        super().__init__(code_list, date)

    def get_weights(self):
        code_list = list_jq2wind(self.code_list)
        code_weights = {}
        return_value = self._get_return(code_list)
        def optimization_target(weight_temp):
            weight_temp = weight_temp[:, np.newaxis]
            portfolio_return_value = np.matmul(weight_temp.transpose(), return_value)[0, :]  # 组合的投资回报序列
            mean = np.mean(portfolio_return_value)
            var = np.var(portfolio_return_value)
            skew = scipy.stats.skew(portfolio_return_value)
            kurtosis = scipy.stats.kurtosis(portfolio_return_value)
            loss = self.w2 * var + self.w3 * skew + self.w4 * kurtosis  # 对方差、偏度、峰度进行优化，期望值最小越好
            return loss
        def constraint(weight_temp):
            return np.sum(weight_temp) - 1.0
        n = len(self.code_list)  # 资产个数
        x_0 = np.ones((n,)) * 1.0 / n
        bounds = n * ((0.0, None),)  # 权重非负约束条件
        res = scipy.optimize.minimize(optimization_target, x_0, method='SLSQP', bounds=bounds, constraints={'type': 'eq', 'fun': constraint})
        # print(res)
        if res.success:  # 优化成功
            x = res.x
        else:  # 优化失败，用等权
            x = x_0
        for i in range(len(code_list)):
            code = code_list[i]
            code_weights[list_wind2jq([code])[0]] = x[i]
        return code_weights

    def _get_return(self, code_list):
        # 提供_calc_weights需要计算的参数
        w.start()
        return_value = np.array(w.wsd(code_list, "pct_chg", "ED-" + str(self.N - 1) + "TD", self.date, "").Data)
        return return_value


class 层次风险平价(方差极小化权重_基本版):
    def get_weights(self):
        code_list = list_jq2wind(self.code_list)
        w.start()
        return_value = np.array(w.wsd(code_list, "pct_chg", "ED-" + str(self.N - 1) + "TD", self.date, "").Data)
        return_value = return_value.transpose()
        return_value = pd.DataFrame(return_value, columns=code_list)
        optimizer = HRPOpt(return_value)
        hrp_portfolio = optimizer.hrp_portfolio()
        hrp_portfolio = dict(zip(list_wind2jq(list(hrp_portfolio.keys())), hrp_portfolio.values()))
        return hrp_portfolio


if __name__ == '__main__':
    # model = 风险预算组合_模块求解基本版(['000002.XSHE', '600000.XSHG', '002415.XSHE', '601012.XSHG', '601009.XSHG'], '2019-11-06', risk_budget=[0.2, 0.3, 0.4, 0.5, 0.6])
    # print(model.get_weights())
    #
    # model = 层次风险平价(['000002.XSHE', '600000.XSHG', '002415.XSHE', '601012.XSHG', '601009.XSHG'], '2019-11-06', N=60)
    # print(model.get_weights())

    model = 方差极小化权重_行业版(['000002.XSHE', '600000.XSHG', '002415.XSHE', '601012.XSHG', '601009.XSHG'], '2019-11-06')
    print(model.get_weights())
