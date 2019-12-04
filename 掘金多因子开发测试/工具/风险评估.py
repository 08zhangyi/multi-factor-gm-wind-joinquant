import numpy as np
from WindPy import w


class 风险评估(object):
    def __init__(self, code_list, date):
        self.code_list = code_list
        self.date = date  # 数据提取截止至date收盘

    def get_portfolio_risk(self, w):
        """
        :param w: 投资组合的权重，(N, K)，N个资产，K个投资组合
        :return portfolio_risk: 投资组合的风险值，单个交易日的风险，未年化，(K,)
        """
        K = w.shape[1]
        portfolio_risk = np.zeros(K)
        return portfolio_risk


class 方差风险_历史数据(风险评估):
    def __init__(self, code_list, date, N_days):
        self.N_days = N_days  # 历史数据的采样天数
        风险评估.__init__(self, code_list, date)
        self.return_cov = self.get_cov()  # (N, N)矩阵

    def get_cov(self):
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

    def get_corr(self):
        """
        :return return_corr: 相关系数矩阵
        """
        return_std = np.sqrt(np.diag(self.return_cov))
        return_corr = self.return_cov / np.matmul(return_std.reshape(-1, 1), return_std.reshape(1, -1))
        return return_corr


class 方差风险_历史数据_OAS(方差风险_历史数据):
    def get_cov(self):
        w.start()
        return_value = np.array(w.wsd(self.code_list, "pct_chg", "ED-" + str(self.N_days - 1) + "TD", self.date, "").Data)
        from sklearn.covariance import OAS
        return_cov = OAS().fit(return_value.transpose())
        return_cov = return_cov.covariance_
        return return_cov


class 方差风险_历史数据_硬阈值稀疏(方差风险_历史数据):
    def __init__(self, code_list, date, N_days, threshold):
        self.threshold = threshold
        方差风险_历史数据.__init__(self, code_list, date, N_days)

    def get_cov(self):
        return_cov = 方差风险_历史数据.get_cov(self)
        return_cov_diag = np.diag(return_cov)
        threshold_matrix = np.abs(return_cov) >= self.threshold
        return_cov = threshold_matrix * return_cov
        for i in range(len(return_cov_diag)):  # 对角线保持不变
            return_cov[i, i] = return_cov_diag[i]
        return return_cov


class 方差风险_历史数据_软阈值稀疏(方差风险_历史数据_硬阈值稀疏):
    def get_cov(self):
        return_cov = 方差风险_历史数据.get_cov(self)
        return_cov_diag = np.diag(return_cov)
        threshold_matrix_pos = ((return_cov <= self.threshold) & (return_cov >= 0)) * self.threshold
        threshold_matrix_nag = ((return_cov >= -self.threshold) & (return_cov <= 0)) * self.threshold
        return_cov = return_cov - threshold_matrix_pos - threshold_matrix_nag
        for i in range(len(return_cov_diag)):  # 对角线保持不变
            return_cov[i, i] = return_cov_diag[i]
        return return_cov


class 方差风险_历史数据_去基准趋势(方差风险_历史数据):
    def __init__(self, code_list, date, N_days, bench_mark):
        self.bench_mark = bench_mark
        方差风险_历史数据.__init__(self, code_list, date, N_days)
        self.return_cov = self.get_cov()  # (N, N)矩阵

    def get_cov(self):
        w.start()
        return_value = np.array(w.wsd(self.code_list, "pct_chg", "ED-" + str(self.N_days - 1) + "TD", self.date, "").Data)
        return_value_bench_mark = np.array(w.wsd(self.bench_mark, "pct_chg", "ED-" + str(self.N_days - 1) + "TD", self.date, "").Data)
        return_value = return_value - return_value_bench_mark
        return_cov = np.cov(return_value)
        return return_cov


if __name__ == '__main__':
    code_list = ['000002.SZ', '600000.SH', '002415.SZ', '601012.SH', '601009.SH']
    date = '2019-12-04'
    model = 方差风险_历史数据_去基准趋势(code_list, date, N_days=60, bench_mark='000300.SH')
    return_cov = model.get_cov() * np.sqrt(240)
    return_corr = model.get_corr()
    print(return_cov)
    print(return_corr)