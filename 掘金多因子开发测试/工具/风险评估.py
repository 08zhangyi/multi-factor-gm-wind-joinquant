import numpy as np
from WindPy import w


class 风险评估(object):
    def __init__(self, code_list, date):
        self.code_list = code_list
        self.date = date  # 数据提取截止至date收盘

    def get_portfolio_risk(self, w):
        """
        :param w: 投资组合的权重，(N, K)，N个资产，K个投资组合
        :return portfolio_risk: 投资组合的风险值
        """
        K = w.shape[1]
        portfolio_risk = np.zeros(K)
        return portfolio_risk


class 方差风险_历史数据(风险评估):
    def __init__(self, code_list, date, N_days):
        self.N_days = N_days  # 历史数据的采样天数
        风险评估.__init__(self, code_list, date)
        self.return_cov = self._get_cov()  # (N, N)矩阵

    def _get_cov(self):
        w.start()
        return_value = np.array(w.wsd(self.code_list, "pct_chg", "ED-" + str(self.N_days - 1) + "TD", self.date, "").Data)
        return_cov = np.cov(return_value)
        return return_cov

    def get_portfolio_risk(self, w):
        """
        :param w: 投资组合的权重，(N, K)，N个资产，K个投资组合
        :return portfolio_risk: 投资组合的标准差
        """
        portfolio_risk = np.matmul(w.transpose(), np.matmul(self.return_cov, w))
        portfolio_risk = np.sqrt(np.diag(portfolio_risk))
        return portfolio_risk


class 方差风险_历史数据_OAS(方差风险_历史数据):
    def _get_cov(self):
        w.start()
        return_value = np.array(w.wsd(self.code_list, "pct_chg", "ED-" + str(self.N_days - 1) + "TD", self.date, "").Data)
        from sklearn.covariance import OAS
        return_cov = OAS().fit(return_value.transpose())
        return_cov = return_cov.covariance_
        return return_cov