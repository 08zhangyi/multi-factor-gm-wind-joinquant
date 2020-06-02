import datetime
import numpy as np
import xlrd
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import list_wind2jq
from 持仓配置 import 风险预算组合_模块求解基本版_带约束

# 统一设定调仓日，选股为前一天收盘后
DATE = '2020-05-22'
# 债券品种的比例调整
BOND_CORRECTIONG = {'160618.XSHE': 0.06, '161713.XSHE': 0.03, '161716.XSHE': 0.09, '167501.XSHE': 0.02, '511260.XSHG': 0.02, '511010.XSHG': -0.22}

# 自动读取风险预算数据
FILE_PATH = 'C:\\Users\\pc\\Desktop\\策略计算表temp.xlsx'
file = xlrd.open_workbook(FILE_PATH)
table = file.sheet_by_name('计算表')
row_number = table.nrows
S_all = ((0, 2), (7, 9), (14, 16))  # 每个策略所在的列代码
S_result = []  # 记录策略结果的代码
for S in S_all:
    stock_pool = []
    risk_budget = []
    risk_bounds = []
    for i in range(5, row_number):
        value_code = table.cell(i, S[0]).value
        value_ratio = table.cell(i, S[1]).value
        if value_code != '':
            if value_code in ['160618.SZ', '161713.SZ', '161716.SZ', '167501.SZ', '511260.SH']:  # 债券类不参与权重计算
                pass
            elif value_code in ['511010.SH']:  # 债券类参与权重计算
                stock_pool.append(value_code)
                risk_budget.append(value_ratio)
                risk_bounds.append([0.4, 0.85])  # 权重约束设置
            elif value_code in ['513050.SH', '513100.SH', '513500.SH', '518880.SH']:  # 外盘黄金类
                stock_pool.append(value_code)
                risk_budget.append(value_ratio)
                risk_bounds.append([0.0, 0.2])  # 权重约束设置
            else:  # 国内股票类
                stock_pool.append(value_code)
                risk_budget.append(value_ratio)
                risk_bounds.append([0.0, 1.0])  # 权重约束设置
    S_result.append([stock_pool, risk_budget, np.array(risk_bounds)])

# 策略0部分
stock_pool_0 = list_wind2jq(S_result[0][0])
risk_budget_0 = S_result[0][1]
risk_bounds_0 = S_result[0][2]
stock_weights_0 = 风险预算组合_模块求解基本版_带约束(stock_pool_0, DATE, risk_budget=risk_budget_0, bounds=risk_bounds_0).get_weights()
# 加入信用债品种，对国债配置比例进行修正
stock_weights_0['160618.XSHE'] = BOND_CORRECTIONG['160618.XSHE']
stock_weights_0['161713.XSHE'] = BOND_CORRECTIONG['161713.XSHE']
stock_weights_0['161716.XSHE'] = BOND_CORRECTIONG['161716.XSHE']
stock_weights_0['167501.XSHE'] = BOND_CORRECTIONG['167501.XSHE']
stock_weights_0['511260.XSHG'] = BOND_CORRECTIONG['511260.XSHG']
stock_weights_0['511010.XSHG'] = BOND_CORRECTIONG['511010.XSHG'] + stock_weights_0['511010.XSHG']
# 输出文字信息
string_output_0 = '策略0的风险预算权重为：\n'
string_output_0 += str(dict(zip(stock_pool_0, risk_budget_0))) + '\n'
string_output_0 += '策略0的选股结果（选股日为 ' + DATE + ' 收盘）：\n'
string_output_0 += str(stock_weights_0) + '\n'
print(string_output_0)

# 策略1部分
stock_pool_1 = list_wind2jq(S_result[1][0])
risk_budget_1 = S_result[1][1]
risk_bounds_1 = S_result[1][2]
stock_weights_1 = 风险预算组合_模块求解基本版_带约束(stock_pool_1, DATE, risk_budget=risk_budget_1, bounds=risk_bounds_1).get_weights()
# 加入信用债品种，对国债配置比例进行修正
stock_weights_1['160618.XSHE'] = BOND_CORRECTIONG['160618.XSHE']
stock_weights_1['161713.XSHE'] = BOND_CORRECTIONG['161713.XSHE']
stock_weights_1['161716.XSHE'] = BOND_CORRECTIONG['161716.XSHE']
stock_weights_1['167501.XSHE'] = BOND_CORRECTIONG['167501.XSHE']
stock_weights_1['511260.XSHG'] = BOND_CORRECTIONG['511260.XSHG']
stock_weights_1['511010.XSHG'] = BOND_CORRECTIONG['511010.XSHG'] + stock_weights_1['511010.XSHG']
# 输出文字信息
string_output_1 = '策略1的风险预算权重为：\n'
string_output_1 += str(dict(zip(stock_pool_1, risk_budget_1))) + '\n'
string_output_1 += '策略1的选股结果（选股日为 ' + DATE + ' 收盘）：\n'
string_output_1 += str(stock_weights_1) + '\n'
print(string_output_1)

# 策略2部分
stock_pool_2 = list_wind2jq(S_result[2][0])
risk_budget_2 = S_result[2][1]
risk_bounds_2 = S_result[2][2]
stock_weights_2 = 风险预算组合_模块求解基本版_带约束(stock_pool_2, DATE, risk_budget=risk_budget_2, bounds=risk_bounds_2).get_weights()
# 加入信用债品种，对国债配置比例进行修正
stock_weights_2['160618.XSHE'] = BOND_CORRECTIONG['160618.XSHE']
stock_weights_2['161713.XSHE'] = BOND_CORRECTIONG['161713.XSHE']
stock_weights_2['161716.XSHE'] = BOND_CORRECTIONG['161716.XSHE']
stock_weights_2['167501.XSHE'] = BOND_CORRECTIONG['167501.XSHE']
stock_weights_2['511260.XSHG'] = BOND_CORRECTIONG['511260.XSHG']
stock_weights_2['511010.XSHG'] = BOND_CORRECTIONG['511010.XSHG'] + stock_weights_2['511010.XSHG']
# 输出文字信息
string_output_2 = '策略2的风险预算权重为：\n'
string_output_2 += str(dict(zip(stock_pool_2, risk_budget_2))) + '\n'
string_output_2 += '策略2的选股结果（选股日为 ' + DATE + ' 收盘）：\n'
string_output_2 += str(stock_weights_2) + '\n'
print(string_output_2)

# 写入日志
with open('data\\log.txt', 'a') as f:
    string_all = str(datetime.datetime.now()) + '  运行日志\n'
    string_all += string_output_0 + string_output_1 + string_output_2
    string_all += '\n'
    f.write(string_all)