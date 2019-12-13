import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import list_wind2jq
from 持仓配置 import 风险平价组合_迭代求解基本版, 风险预算组合_模块求解基本版

# 策略一部分，调仓日每月15日，选股为前一天收盘后（风险预算模型，等待启用）
date_1 = '2019-12-13'
stock_pool_1 = ['510050.SH', '513100.SH', '159928.SZ', '513500.SH', '510500.SH', '511010.SH', '518880.SH', '515000.SH']
risk_budget_1 = [1, 1, 1, 1, 1, 1, 1, 1]  # 权重配置
stock_pool_1 = list_wind2jq(stock_pool_1)
stock_weights_1 = 风险预算组合_模块求解基本版(stock_pool_1, date_1, risk_budget=risk_budget_1).get_weights()
print('策略一的选股结果（选股日为 ' + date_1 + ' 收盘）：')
print(stock_weights_1, '\n')

# 策略二部分，调仓日每月05日，选股为前一天收盘后
date_2 = '2019-12-04'
stock_pool_2 = ['510050.SH', '513100.SH', '513500.SH', '510500.SH', '511010.SH', '518880.SH', '159920.SZ', '512760.SH']
risk_budget_2 = [1, 1, 1, 1, 1, 1, 1, 1]  # 权重配置
stock_pool_2 = list_wind2jq(stock_pool_2)
stock_weights_2 = 风险预算组合_模块求解基本版(stock_pool_2, date_2, risk_budget=risk_budget_2).get_weights()
print('策略二的选股结果（选股日为' + date_2 + '收盘）：')
print(stock_weights_2, '\n')

