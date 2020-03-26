import datetime
import numpy as np
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import list_wind2jq
from 持仓配置 import 风险预算组合_模块求解基本版_带约束

# 策略一部分，选股为前一天收盘后
date_1 = '2020-03-25'
# 国内债券部分配置方案
stock_pool_1_bond = ['511010.SH']
risk_budget_1_bond = [1.0]
risk_bounds_1_bond = np.array([[0.4, 0.81]])
# 国内股票部分配置方案
stock_pool_1_stock = ['159928.SZ', '159949.SZ', '510050.SH', '512660.SH', '512720.SH', '515000.SH']
risk_budget_1_stock = [0.7, 0.7, 0.7, 0.5, 0.8, 0.6]  # 总权重固定为4个单位
risk_bounds_1_stock = np.array([[0.0, 1.0]] * len(stock_pool_1_stock))
# 合并为整体证券池
stock_pool_1 = stock_pool_1_bond + stock_pool_1_stock
risk_budget_1 = risk_budget_1_bond + risk_budget_1_stock
risk_bounds_1 = np.concatenate([risk_bounds_1_bond, risk_bounds_1_stock])
stock_pool_1 = list_wind2jq(stock_pool_1)
stock_weights_1 = 风险预算组合_模块求解基本版_带约束(stock_pool_1, date_1, risk_budget=risk_budget_1, bounds=risk_bounds_1).get_weights()
# 加入信用债品种，对国债配置比例进行修正
stock_weights_1['160618.XSHE'] = 0.05
stock_weights_1['161713.XSHE'] = 0.03
stock_weights_1['161716.XSHE'] = 0.09
stock_weights_1['167501.XSHE'] = 0.05
stock_weights_1['511010.XSHG'] = stock_weights_1['511010.XSHG'] - 0.22
# 输出文字信息
string_output_1 = '策略一的风险预算权重为：\n'
string_output_1 += str(dict(zip(stock_pool_1, risk_budget_1))) + '\n'
string_output_1 += '策略一的选股结果（选股日为 ' + date_1 + ' 收盘）：\n'
string_output_1 += str(stock_weights_1) + '\n'
print(string_output_1)

# 策略二部分，选股为前一天收盘后
date_2 = '2020-03-25'
# 国内债券部分配置方案
stock_pool_2_bond = ['511010.SH']
risk_budget_2_bond = [1.0]
risk_bounds_2_bond = np.array([[0.4, 0.81]])
# 国内股票部分配置方案
stock_pool_2_stock = ['159928.SZ', '159949.SZ.SZ', '510050.SH', '510300.SH', '510500.SH', '512760.SH', '512930.SH', '515050.SH']
risk_budget_2_stock = [0.2, 0.8, 0.2, 0.4, 0.6, 0.9, 0.6, 0.3]
risk_bounds_2_stock = np.array([[0.0, 1.0]] * len(stock_pool_2_stock))
# 合并为整体证券池
stock_pool_2 = stock_pool_2_bond + stock_pool_2_stock
risk_budget_2 = risk_budget_2_bond + risk_budget_2_stock
risk_bounds_2 = np.concatenate([risk_bounds_2_bond, risk_bounds_2_stock])
stock_pool_2 = list_wind2jq(stock_pool_2)
stock_weights_2 = 风险预算组合_模块求解基本版_带约束(stock_pool_2, date_2, risk_budget=risk_budget_2, bounds=risk_bounds_2).get_weights()
# 加入信用债品种，对国债配置比例进行修正
stock_weights_2['160618.XSHE'] = 0.06
stock_weights_2['161713.XSHE'] = 0.03
stock_weights_2['161716.XSHE'] = 0.09
stock_weights_2['167501.XSHE'] = 0.04
stock_weights_2['511010.XSHG'] = stock_weights_2['511010.XSHG'] - 0.22
# 输出文字信息
string_output_2 = '策略二的风险预算权重为：\n'
string_output_2 += str(dict(zip(stock_pool_2, risk_budget_2))) + '\n'
string_output_2 += '策略二的选股结果（选股日为 ' + date_2 + ' 收盘）：\n'
string_output_2 += str(stock_weights_2) + '\n'
print(string_output_2)

# 策略三部分，选股为前一天收盘后
date_3 = '2020-03-25'
# 国内债券部分配置方案
stock_pool_3_bond = ['511010.SH']
risk_budget_3_bond = [1.0]
risk_bounds_3_bond = np.array([[0.4, 0.81]])
# 国内股票部分配置方案
stock_pool_3_stock = ['159928.SZ', '510050.SH', '510300.SH', '510500.SH', '512170.SH', '512720.SH', '515050.SH', '930997.CSI']
risk_budget_3_stock = [0.2, 0.6, 0.6, 0.8, 0.2, 0.8, 0.3, 0.5]
risk_bounds_3_stock = np.array([[0.0, 1.0]] * len(stock_pool_3_stock))
# 合并为整体证券池
stock_pool_3 = stock_pool_3_bond + stock_pool_3_stock
risk_budget_3 = risk_budget_3_bond + risk_budget_3_stock
risk_bounds_3 = np.concatenate([risk_bounds_3_bond, risk_bounds_3_stock])
stock_pool_3 = list_wind2jq(stock_pool_3)
stock_weights_3 = 风险预算组合_模块求解基本版_带约束(stock_pool_3, date_3, risk_budget=risk_budget_3, bounds=risk_bounds_3).get_weights()
# 加入信用债品种，对国债配置比例进行修正
stock_weights_3['160618.XSHE'] = 0.05
stock_weights_3['161713.XSHE'] = 0.03
stock_weights_3['161716.XSHE'] = 0.09
stock_weights_3['167501.XSHE'] = 0.05
stock_weights_3['511010.XSHG'] = stock_weights_3['511010.XSHG'] - 0.22
# 输出文字信息
string_output_3 = '策略三的风险预算权重为：\n'
string_output_3 += str(dict(zip(stock_pool_3, risk_budget_3))) + '\n'
string_output_3 += '策略三的选股结果（选股日为 ' + date_3 + ' 收盘）：\n'
string_output_3 += str(stock_weights_3) + '\n'
print(string_output_3)

# 写入日志
with open('data\\log.txt', 'a') as f:
    string_all = str(datetime.datetime.now()) + '  运行日志\n'
    string_all += string_output_1 + string_output_2
    string_all += '\n'
    f.write(string_all)