import datetime
import numpy as np
import xlrd
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import list_wind2jq
from 持仓配置 import 风险预算组合_模块求解基本版_带约束

# 统一设定调仓日，选股为前一交易日收盘后
DATE = '2022-10-24'
# 债券品种的比例调整
BOND_ADJUST = {'161716.XSHE': 0.15, '511260.XSHG': -0.075, '511010.XSHG': -0.075}
# A股手动调整比例
STOCK_ADJUST = 0.0


# 调整函数
def adjust_weights(stock_weights, bond_adjust, stock_adjust):
    # A股部分的调整，同步等比例调整债券、外盘、商品的比例
    stock_weights['510300.XSHG'] = stock_weights.get('510300.XSHG', 0.0) + stock_adjust
    # adjusted_codes = ['511010.XSHG', '511260.XSHG',
    #                   '513050.XSHG', '513100.XSHG', '513500.XSHG',
    #                   '518880.XSHG']
    adjusted_codes = ['518880.XSHG']
    adjusted_full_ratio = np.sum([stock_weights[code] for code in adjusted_codes])
    for code in adjusted_codes:
        stock_weights[code] = stock_weights[code] * ((adjusted_full_ratio - stock_adjust) / adjusted_full_ratio)
    # 债券部分的调整，加入信用债和长期国债，并调整比例
    for bond_code in bond_adjust:
        stock_weights[bond_code] = stock_weights.get(bond_code, 0.0) + bond_adjust[bond_code]
    # 债券权重平均分配
    bond_weights = (stock_weights['511010.XSHG'] + stock_weights['511260.XSHG'])
    stock_weights['511010.XSHG'] = bond_weights * 0.5
    stock_weights['511260.XSHG'] = bond_weights * 0.5
    return stock_weights


# 自动读取风险预算数据
FILE_PATH = 'C:\\Users\\pc\\Desktop\\策略计算表temp.xls'  # 参考data\策略计算表example.xls
file = xlrd.open_workbook(FILE_PATH)
table = file.sheet_by_name('ETF组合策略1602')
row_number = table.nrows
S_all = ((0, 2), (7, 9), (14, 16))  # 每个策略所在的列代码
S_result = []  # 记录策略结果的代码
for S in S_all:
    stock_pool = []
    risk_budget = []
    risk_bounds = []
    for i in range(6, row_number):
        value_code = table.cell(i, S[0]).value
        value_ratio = table.cell(i, S[1]).value
        if value_code != '':
            if value_code in ['161716.SZ']:  # 债券类不参与权重计算
                pass
            elif value_code in ['511010.SH', '511260.SH']:  # 债券类参与权重计算
                stock_pool.append(value_code)
                risk_budget.append(value_ratio)
                risk_bounds.append([0.15, 0.85])  # 权重约束设置
            elif value_code in ['513050.SH', '513100.SH', '513500.SH']:  # 外盘类
                stock_pool.append(value_code)
                risk_budget.append(value_ratio)
                risk_bounds.append([0.0, 0.2])  # 权重约束设置
            elif value_code in ['518880.SH']:  # 商品类
                stock_pool.append(value_code)
                risk_budget.append(value_ratio)
                risk_bounds.append([0.0, 0.1])  # 权重约束设置
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
stock_weights_0 = adjust_weights(stock_weights_0, BOND_ADJUST, STOCK_ADJUST)
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
stock_weights_1 = adjust_weights(stock_weights_1, BOND_ADJUST, STOCK_ADJUST)
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
stock_weights_2 = adjust_weights(stock_weights_2, BOND_ADJUST, STOCK_ADJUST)
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