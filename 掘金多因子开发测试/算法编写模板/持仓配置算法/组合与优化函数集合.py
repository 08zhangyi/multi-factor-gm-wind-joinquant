import numpy as np
import cvxopt as opt
import cvxopt.solvers as optsolvers


def min_var_portfolio(cov_mat, allow_short=False):
    """
    极小方差组合函数
    Parameters
    ----------
    cov_mat: np数组，协方差矩阵
    allow_short: bool，False为禁止做空，True为可以做空
    Returns
    -------
    weights: np数组，最优权重序列
    """
    n = len(cov_mat)  # 资产个数
    P = opt.matrix(cov_mat)
    q = opt.matrix(0.0, (n, 1))
    if not allow_short:
        # 禁止做空的限制，Gx <= h
        G = opt.matrix(-np.identity(n))
        h = opt.matrix(0.0, (n, 1))
    else:
        G = None
        h = None
    # 权重求和为一，Ax = b
    A = opt.matrix(1.0, (1, n))
    b = opt.matrix(1.0)
    sol = optsolvers.qp(P, q, G, h, A, b)
    weights = np.array(sol['x']).squeeze()
    return weights


def tangency_portfolio(cov_mat, exp_rets, risk_free_rets=0.0, allow_short=False):
    """
    切组合，最大夏普比的组合
    具体求解方法为要求组合的预期收益大于等于1且方差最小
    Parameters
    ----------
    cov_mat: np数组，协方差矩阵
    exp_rets: np数组，预期回报（通常为历史回报的均值）
    allow_short: bool，False为禁止做空，True为可以做空
    Returns
    -------
    weights: np数组，最优权重序列
    """
    n = len(cov_mat)  # 资产个数
    P = opt.matrix(cov_mat)
    q = opt.matrix(0.0, (n, 1))
    exp_rets = exp_rets - risk_free_rets
    if not allow_short:  # Gx <= h
        # exp_rets*x >= 1 and x >= 0，组合收益大于等于1且禁止做空
        G = opt.matrix(np.vstack((-exp_rets, -np.identity(n))))
        h = opt.matrix(np.vstack((-1.0, np.ones((n, 1)) * -0.0)))
    else:
        # exp_rets*x >= 1，组合收益大于等于1且可以做空
        G = opt.matrix(-exp_rets.values).T
        h = opt.matrix(-1.0)
    sol = optsolvers.qp(P, q, G, h)
    weights = np.array(sol['x']).squeeze()
    weights /= weights.sum()
    return weights


def maximum_diversification(cov_mat, allow_short=False):
    """
    最大分散化组合
    Parameters
    ----------
    cov_mat: np数组，协方差矩阵
    allow_short: bool，False为禁止做空，True为可以做空
    Returns
    -------
    weights: np数组，最优权重序列
    """
    n = len(cov_mat)  # 资产个数
    P = opt.matrix(cov_mat)
    q = opt.matrix(0.0, (n, 1))
    omega_diag = np.sqrt(cov_mat.diagonal())
    if not allow_short:  # Gx <= h
        # exp_rets*x >= 1 and x >= 0，组合收益大于等于1且禁止做空
        G = opt.matrix(np.vstack((-omega_diag, -np.identity(n))))
        h = opt.matrix(np.vstack((-1.0, np.ones((n, 1)) * -0.0)))
    else:
        # exp_rets*x >= 1，组合收益大于等于1且可以做空
        G = opt.matrix(-omega_diag.values).T
        h = opt.matrix(-1.0)
    sol = optsolvers.qp(P, q, G, h)
    weights = np.array(sol['x']).squeeze()
    weights /= weights.sum()
    return weights


def markowitz_portfolio(cov_mat, exp_rets, target_ret,
                        allow_short=False, market_neutral=False):
    """
    求解Markowitz投资组合
    Parameters
    ----------
    cov_mat: np数组，协方差矩阵
    exp_rets: np数组，预期回报（通常为历史回报的均值）
    target_ret: float，投资组合的预期收益
    allow_short: bool，False为禁止做空，True为可以做空
    market_neutral: bool, False表示权重和为1，True表示权重和为0，也就是市场中性组合，或者是纯alpha组合
    Returns
    -------
    weights: np数组，最优权重序列
    """
    if market_neutral and not allow_short:
        print("市场中性意味着可以做空")
        allow_short = True
    n = len(cov_mat)  # 资产个数
    P = opt.matrix(cov_mat)
    q = opt.matrix(0.0, (n, 1))
    if not allow_short:  # Gx <= h
        # exp_rets*x >= target_ret and x >= 0，组合收益大于等于1且禁止做空
        G = opt.matrix(np.vstack((-exp_rets.values, -np.identity(n))))
        h = opt.matrix(np.vstack((-target_ret, np.zeros((n, 1)) * -0.0)))
    else:
        # exp_rets*x >= 1，组合收益大于等于1且可以做空
        G = opt.matrix(-exp_rets.values).T
        h = opt.matrix(-target_ret)
    A = opt.matrix(1.0, (1, n))
    if not market_neutral:  # 权重和为1
        b = opt.matrix(1.0)
    else:  # 市场中性，权重和为0
        b = opt.matrix(0.0)
    sol = optsolvers.qp(P, q, G, h, A, b)
    weights = np.array(sol['x']).squeeze()
    return weights