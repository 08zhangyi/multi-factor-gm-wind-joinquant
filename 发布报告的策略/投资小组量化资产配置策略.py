import datetime
import numpy as np
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import list_wind2jq
from 持仓配置 import 风险预算组合_模块求解基本版_带约束

# 策略一部分，调仓日每月15日，选股为前一天收盘后（风险预算模型，等待启用）
date_1 = '2020-02-14'
# 国内债券部分配置方案
stock_pool_1_bond = ['161716.SZ', '167501.SZ', '511010.SH']
risk_budget_1_bond = [0.25, 0.25, 0.7]  # 候选目标[0.2, 0.8, 0.8]
risk_bounds_1_bond = np.array([[0.0, 0.09],
                               [0.0, 0.06],
                               [0.0, 1.0]])
# 国内股票部分配置方案
stock_pool_1_stock = ['510050.SH', '159928.SZ', '510500.SH', '515000.SH', '512170.SH']
risk_budget_1_stock = [1, 0.85, 1, 0.85, 0.3]  # 总权重固定为4个单位
risk_bounds_1_stock = np.array([[0.0, 1.0]] * len(stock_pool_1_stock))
# 国际部分配置方案
stock_pool_1_global = ['513100.SH', '513500.SH', '518880.SH']
risk_budget_1_global = [0.9, 0.9, 0.95]  # 最终目标[0.75, 0.75, 0.8]
risk_bounds_1_global = np.array([[0.0, 1.0]] * len(stock_pool_1_global))
# 合并为整体证券池
stock_pool_1 = stock_pool_1_bond + stock_pool_1_stock + stock_pool_1_global
risk_budget_1 = risk_budget_1_bond + risk_budget_1_stock + risk_budget_1_global
risk_bounds_1 = np.concatenate([risk_bounds_1_bond, risk_bounds_1_stock, risk_bounds_1_global])
stock_pool_1 = list_wind2jq(stock_pool_1)
stock_weights_1 = 风险预算组合_模块求解基本版_带约束(stock_pool_1, date_1, risk_budget=risk_budget_1, bounds=risk_bounds_1).get_weights()
# 输出文字信息
string_output_1 = '策略一的风险预算权重为：\n'
string_output_1 += str(dict(zip(stock_pool_1, risk_budget_1))) + '\n'
string_output_1 += '策略一的选股结果（选股日为 ' + date_1 + ' 收盘）：\n'
string_output_1 += str(stock_weights_1) + '\n'
print(string_output_1)

# 策略二部分，调仓日每月05日，选股为前一天收盘后
date_2 = '2020-01-03'
# 国内债券部分配置方案
stock_pool_2_bond = ['161716.SZ', '167501.SZ', '511010.SH']
risk_budget_2_bond = [0.25, 0.25, 0.7]  # 候选目标[0.2, 0.8, 0.8]
risk_bounds_2_bond = np.array([[0.0, 0.09],
                               [0.0, 0.06],
                               [0.0, 1.0]])
# 国内股票部分配置方案
stock_pool_2_stock = ['510050.SH', '510500.SH', '510900.SH', '512760.SH']
risk_budget_2_stock = [1, 1, 1, 1]
risk_bounds_2_stock = np.array([[0.0, 1.0]] * len(stock_pool_2_stock))
# 国际部分配置方案
stock_pool_2_global = ['513100.SH', '513500.SH', '518880.SH']
risk_budget_2_global = [0.9, 0.9, 0.95]  # 最终目标[0.75, 0.75, 0.8]
risk_bounds_2_global = np.array([[0.0, 1.0]] * len(stock_pool_2_global))
# 合并为整体证券池
stock_pool_2 = stock_pool_2_bond + stock_pool_2_stock + stock_pool_2_global
risk_budget_2 = risk_budget_2_bond + risk_budget_2_stock + risk_budget_2_global
risk_bounds_2 = np.concatenate([risk_bounds_2_bond, risk_bounds_2_stock, risk_bounds_2_global])
stock_pool_2 = list_wind2jq(stock_pool_2)
stock_weights_2 = 风险预算组合_模块求解基本版_带约束(stock_pool_2, date_2, risk_budget=risk_budget_2, bounds=risk_bounds_2).get_weights()
# 输出文字信息
string_output_2 = '策略二的风险预算权重为：\n'
string_output_2 += str(dict(zip(stock_pool_2, risk_budget_2))) + '\n'
string_output_2 += '策略二的选股结果（选股日为 ' + date_2 + ' 收盘）：\n'
string_output_2 += str(stock_weights_2) + '\n'
print(string_output_2)

# 策略三部分，调仓日每月25日，选股为前一天收盘后
date_3 = '2020-02-04'
# 国内债券部分配置方案
stock_pool_3_bond = ['161716.SZ', '167501.SZ', '511010.SH']
risk_budget_3_bond = [0.25, 0.25, 0.7]  # 候选目标[0.2, 0.8, 0.8]
risk_bounds_3_bond = np.array([[0.0, 0.09],
                               [0.0, 0.06],
                               [0.0, 1.0]])
# 国内股票部分配置方案
stock_pool_3_stock = ['159938.SZ', '510050.SH', '510300.SH', '510500.SH', '512170.SH', '512930.SH']
risk_budget_3_stock = [0.5, 1, 0.6, 1, 0.4, 0.5]
risk_bounds_3_stock = np.array([[0.0, 1.0]] * len(stock_pool_3_stock))
# 国际部分配置方案
stock_pool_3_global = ['513100.SH', '513500.SH', '518880.SH']
risk_budget_3_global = [0.75, 0.75, 0.8]  # 最终目标[0.75, 0.75, 0.8]
risk_bounds_3_global = np.array([[0.0, 1.0]] * len(stock_pool_3_global))
# 合并为整体证券池
stock_pool_3 = stock_pool_3_bond + stock_pool_3_stock + stock_pool_3_global
risk_budget_3 = risk_budget_3_bond + risk_budget_3_stock + risk_budget_3_global
risk_bounds_3 = np.concatenate([risk_bounds_3_bond, risk_bounds_3_stock, risk_bounds_3_global])
stock_pool_3 = list_wind2jq(stock_pool_3)
stock_weights_3 = 风险预算组合_模块求解基本版_带约束(stock_pool_3, date_3, risk_budget=risk_budget_3, bounds=risk_bounds_3).get_weights()
# 输出文字信息
string_output_3 = '策略三的风险预算权重为：\n'
string_output_3 += str(dict(zip(stock_pool_3, risk_budget_3))) + '\n'
string_output_3 += '策略三的选股结果（选股日为 ' + date_3 + ' 收盘）：\n'
string_output_3 += str(stock_weights_3) + '\n'
print(string_output_3)
