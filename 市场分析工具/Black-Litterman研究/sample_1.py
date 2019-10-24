# 论文《A step-by-step guide to the Black-Litterman model》的计算实例
# 导入模块区
import pandas as pd
import numpy as np


# 使用函数区
# 根据均衡权重、协方差矩阵，计算均衡收益
def get_equilibrium_returns(covariance_matrix, equilibrium_weights, delta_value):
    """
    :param covariance_matrix: (N, N)
    :param equilibrium_weights: (N, 1)
    :param delta_value: 风险厌恶系数值，>0
    :return equilibrium_returns: (N, 1)，超额收益
    """
    equilibrium_returns = delta_value * np.matmul(covariance_matrix, equilibrium_weights)
    return equilibrium_returns


# 根据协方差矩阵，均衡收益，计算无约束的权重
def get_unconstrained_weights(covariance_matrix, equilibrium_returns, delta_value):
    """
    :param covariance_matrix: (N, N)
    :param equilibrium_returns: (N, 1)，超额收益
    :param delta_value: 风险厌恶系数值，>0
    :return unconstrained_weights: (N, 1)
    """
    unconstrained_weights = 1/delta_value * np.matmul(np.linalg.inv(covariance_matrix), equilibrium_returns)
    return unconstrained_weights


# 计算Black-Litterman后验回报向量
def get_black_litterman_posterior_return_vector(tau_value, covariance_matrix, equilibrium_returns, views_matrix, views_return_vector, views_error_covariance_matrix):
    """
    :param tau: 数值，>0
    :param covariance_matrix: (N, N)
    :param equilibrium_returns: (N, 1)，超额收益
    :param views_matrix: (K, N)，观点组成矩阵，K个观点
    :param views_return_vector: (K, 1)，观点收益矩阵（与无风险利率相比较的超额收益）
    :param views_error_covariance_matrix: (K, K)，观点收益误差矩阵（正定，一般为对角矩阵）
    :return posterior_return_vector: (N, 1)，后验超额收益
    """
    cov_inv = np.linalg.inv(covariance_matrix)
    views_cov_inv = np.linalg.inv(views_error_covariance_matrix)
    A = 1/tau_value * cov_inv
    B = np.matmul(np.matmul(views_matrix.transpose(), views_cov_inv), views_matrix)
    C = np.matmul(1/tau_value * cov_inv, equilibrium_returns)
    D = np.matmul(np.matmul(views_matrix.transpose(), views_cov_inv), views_return_vector)
    posterior_return_vector = np.matmul(np.linalg.inv(A + B), C + D)
    return posterior_return_vector


# 根据风险红利，风险红利的标准差估计风险厌恶系数值
def get_risk_aversion_delta_value(risk_preminum, standard_deviation_of_return):
    """
    :param risk_preminum: 风险红利，市场收益相对于无风险利率的超额收益率，也称超额收益
    :param standard_deviation_of_return: 市场收益率的标准差
    :return delta_value: 风险厌恶系数值
    """
    delta_value = risk_preminum / (standard_deviation_of_return**2)
    return delta_value


# 根据协方差矩阵的权重估计组合的标准差
def get_variance_of_return_from_weights_covariances(covariance_matrix, weights):
    """
    :param covariance_matrix: (N, N)
    :param weights: (N, 1)
    :return standard_deviation:  >0
    """
    variance = np.matmul(weights.transpose(), np.matmul(covariance_matrix, weights))
    return variance[0][0]


# 根据协方差矩阵的权重估计观点的标准差
def get_variance_of_views_from_weights_covariances(covariance_matrix, views_matrix):
    """
    :param covariance_matrix: (N, N)
    :param views_matrix: (K, N)，观点组成矩阵，K个观点
    :return standard_deviation:  (K, )，每条观点对应投资组合的标准差
    """
    variance = np.matmul(views_matrix, np.matmul(covariance_matrix, views_matrix.transpose()))
    variance = np.diag(variance)
    return variance


if __name__ == '__main__':
    # 例子计算区

    # 论文计算原始数据的获取
    market_weights = pd.read_excel('data//weight_data.xlsx', index_col=0).to_numpy()  # 市场市值权重
    cov = pd.read_excel('data//cov_data.xlsx', index_col=0).to_numpy()  # 收益率协方差矩阵
    views_matrix = pd.read_excel('data//view_data.xlsx', header=None).to_numpy()  # 观点矩阵

    # 论文参数的设定
    risk_preminum = 0.075  # 论文中的DJIA风险红利7.5%，年化
    risk_free = 0.05  # 论文中的无风险利率5%
    standard_deviation_of_return = 0.1825  # 论文中的DJIA波动率18.25%，年化
    # delta_value = get_risk_aversion_delta_value(risk_preminum, standard_deviation_of_return)
    delta_value = 2.0  # 论文中使用的风险厌恶系数
    # print(market_weights)
    # print(cov)

    # 计算无约束条件下的结果
    equilibrium_returns = get_equilibrium_returns(cov, market_weights, delta_value)  # 取超额收益估计值
    # print(equilibrium_returns + risk_free)
    # print(get_unconstrained_weights(cov, equilibrium_returns, delta_value))

    # 论文的主观观点
    # print(views_matrix)
    views_vector = np.array([0.1-risk_free, 0.03, 0.015]).reshape((3, 1))  # 观点的收益向量
    level_of_confidence = np.array([0.5, 0.65, 0.3])  # 对每个观点的置信度，0-100%之间
    #  calibration_factor = 0.2806/(1/0.5)  # 第一个观点组合的方差与把握度，论文中取0.2806
    calibration_factor = 0.2843 / (1 / 0.5)  # 第一个观点组合的方差与把握度，计算中采用views_variance的标准差的均值更加合适
    # 0.2843 = np.mean(np.sqrt(views_variance))
    views_cov = np.diag(1.0/level_of_confidence * calibration_factor)
    print(views_cov)
    # tau_value = 0.873  # 论文中对tau值的设定，观点等权下计算的标准差
    tau_value = 1.0
    views_variance = get_variance_of_views_from_weights_covariances(cov, views_matrix)  # 观点的协方差矩阵计算
    # print(np.diag(views_cov), np.sqrt(np.diag(views_cov)))
    print(views_variance, np.sqrt(views_variance))
    print(np.mean(np.sqrt(views_variance)))

    # 计算后验收益和权重
    posterior_return_vector = get_black_litterman_posterior_return_vector(tau_value, cov, equilibrium_returns, views_matrix, views_vector, views_cov)
    # print(posterior_return_vector + risk_free)
    black_litterman_weights = get_unconstrained_weights(cov, posterior_return_vector, delta_value)  # 从后验收益求得权重
    print(black_litterman_weights)
    # print(black_litterman_weights - market_weights)
    # print(np.sum(black_litterman_weights), np.sum(market_weights))  # Black-Litterman权重求和不唯一

    # Black-Litterman权重正则化
    black_litterman_weights = np.maximum(black_litterman_weights, 0.0)  # 去除负权重
    black_litterman_weights = black_litterman_weights / np.sum(black_litterman_weights)  # 归一化
    # print(black_litterman_weights)