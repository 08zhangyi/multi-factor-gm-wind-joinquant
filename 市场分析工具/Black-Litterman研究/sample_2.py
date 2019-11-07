import xlrd
import numpy as np
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from 持仓配置 import 风险平价组合_迭代求解基本版 as WEIGHTS
from utils import list_wind2jq
from sample_1 import get_equilibrium_returns, get_unconstrained_weights, get_black_litterman_posterior_return_vector, \
    get_risk_aversion_delta_value, get_variance_of_return_from_weights_covariances, get_variance_of_views_from_weights_covariances
from 风险评估 import 方差风险_历史数据


def 品种获取(file_path):
    code_list = []
    wb = xlrd.open_workbook(file_path)
    ws = wb.sheet_by_index(0)
    for i in range(1, ws.nrows-2):
        code_list.append(ws.cell(i, 0).value)
    return code_list


def 观点信息获取(file_path):
    wb = xlrd.open_workbook(file_path)
    ws = wb.sheet_by_index(0)
    views_matrix = []
    for i in range(1, ws.nrows-2):
        views_temp = []
        for j in range(2, ws.ncols):
            views_temp.append(ws.cell(i, j).value)
        views_matrix.append(views_temp)
    views_vector = []
    views_cov = []
    for j in range(2, ws.ncols):
        views_vector.append(ws.cell(ws.nrows - 2, j).value)
        views_cov.append(ws.cell(ws.nrows - 1, j).value)
    views_matrix = np.array(views_matrix).transpose()
    views_vector = np.array(views_vector).reshape(-1, 1)
    views_cov = np.diag(np.array(views_cov) ** 2)
    return views_matrix, views_vector, views_cov


if __name__ == '__main__':
    # 输入数据
    date = '2019-11-04'
    file_path = '投资示例.xlsx'
    # 数据整理
    code_list = 品种获取(file_path)
    views_matrix, views_vector, views_cov = 观点信息获取(file_path)
    code_weights = WEIGHTS(list_wind2jq(code_list), date).get_weights()

    # 风险平价收益和历史数据估计协方差数据
    rp_weights = [code_weights[code] for code in code_weights]
    return_cov = 方差风险_历史数据(code_list, date, 60).return_cov * 240
    # 主观观点标准差与历史估计标准差的比较
    views_variance = get_variance_of_views_from_weights_covariances(return_cov, views_matrix)
    views_std = np.sqrt(views_variance)
    print('观点的历史数据估计标准差为：')
    print(views_std)
    print('观点的主观判断标准差为：')
    print(np.sqrt(np.diag(views_cov)))

    # BL模型的参数设定
    delta_value = 50.0
    tau_value = 1.0
    equilibrium_returns = get_equilibrium_returns(return_cov, rp_weights, delta_value)
    print('风险平价模型各品种的均衡收益率：')
    print(equilibrium_returns)
    equilibrium_returns = equilibrium_returns.reshape(-1, 1)
    posterior_return_vector = get_black_litterman_posterior_return_vector(tau_value, return_cov, equilibrium_returns, views_matrix, views_vector, views_cov)
    print('BL模型各品种的后验均衡收益率：')
    print(posterior_return_vector.reshape(-1))
    black_litterman_weights = get_unconstrained_weights(return_cov, posterior_return_vector, delta_value).reshape(-1)
    print('BL模型各品种的后验权重：')
    print(black_litterman_weights)
    print('风险平价模型的配置方案：')
    print(code_weights)
    # Black-Litterman权重正则化
    black_litterman_weights = np.maximum(black_litterman_weights, 0.0)  # 去除负权重
    black_litterman_weights = black_litterman_weights / np.sum(black_litterman_weights)  # 归一化
    print('BL模型各品种的后验权重（正则化处理后）：')
    code_weights_BL = dict(zip(list_wind2jq(code_list), black_litterman_weights))
    print(code_weights_BL)