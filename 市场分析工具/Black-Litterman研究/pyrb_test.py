# pyrb模块的使用试验
# pyrb用于求解Risk Budgeting模型的比例配置问题

import pyrb
import numpy as np
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from 风险评估 import 方差风险_历史数据

code_list = ['000002.SZ', '600000.SH', '002415.SZ', '601012.SH', '511880.SH']
date = '2019-11-06'
model = 方差风险_历史数据(code_list, date, N_days=60)
return_cov = model.return_cov
print(return_cov)

# 风险平价模型
ERC = pyrb.EqualRiskContribution(return_cov)
ERC.solve()
print(ERC.get_risk_contributions())
print(ERC.x)

# 风险预算模型
risk_budget = [100, 30, 40, 30, 0.0]
RB = pyrb.RiskBudgeting(return_cov, risk_budget)
RB.solve()
print(RB.get_risk_contributions())
print(RB.x)

# 约束风险预算模型
risk_budget = [0.25, 0.25, 0.25, 0.25, 0.0]
bounds = np.array([[0.0, 0.5],
                   [0.0, 0.5],
                   [0.0, 0.5],
                   [0.0, 0.5],
                   [0.0, 0.01]])
CRB = pyrb.ConstrainedRiskBudgeting(return_cov, risk_budget, bounds=bounds)
CRB.solve()
print(CRB.get_risk_contributions())
print(CRB.x)