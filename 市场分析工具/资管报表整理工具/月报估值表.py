import os
import xlrd
import xlwt
import numpy as np


# 辅助函数区
def get_data_from_excel(sheet, data_name, col_number):
    # 寻找data_name所在的行，用col_number的列提取出实际数据
    n_rows = sheet.nrows  # 提取表格的行数
    n_cols = sheet.ncols
    value_data_name = 0.0
    if_get = False  # 读取到数据的标识，读取到数据即跳出
    for n_r in range(n_rows):  # 寻找data_name所对应的行
        for n_c in range(n_cols):
            name_temp = sheet.cell_value(n_r, n_c)
            if isinstance(name_temp, float):
                continue
            if name_temp == data_name or name_temp[:-1] == data_name:
                value_data_name += float(sheet.cell_value(n_r, col_number)) if sheet.cell_value(n_r, col_number) != '' else 0.0
                if_get = True
                break
        if if_get:
            break
    return value_data_name


def file_name(file_list, product_name):
    # 获取包含产品名称的文件路径
    for file in file_list:
        if product_name in file:
            return file


# 程序数据准备区
files_path = 'data\\估值表原始'  # 原始excel文件的列表
原始文件列表 = os.listdir(files_path)
原始文件列表 = [files_path+'\\'+f for f in 原始文件列表]
数据位置字典 = {'科目名称': 1, '市值': 7}
产品简称列表 = ['抚顺特钢', '中惠1号', '天诚25号', '天盈12号', '融通10号', '融通5号', '天泽1号', '汇沣1号', '天盈13号',
          '汇沣2号', '汇沣3号', '天沃1号']
# 结构为{'栏目名称': {'提取数据栏目1': 栏目位置1, '提取数据栏目2': 栏目位置2},}
读取栏目字典 = {'基金资产净值': {'基金资产净值': 数据位置字典['市值']},
          '资产类合计': {'资产类合计': 数据位置字典['市值']},
          '负债类合计': {'负债类合计': 数据位置字典['市值']},
          '基金单位净值': {'基金单位净值': 数据位置字典['科目名称']},
          '累计单位净值': {'累计单位净值': 数据位置字典['科目名称']},
          '年初单位净值': {'年初单位净值': 数据位置字典['科目名称']},
          '期初单位净值': {'期初单位净值': 数据位置字典['科目名称']},
          '实收资本金额': {'实收资本金额': 数据位置字典['市值']},
          '年化收益率': {'基金单位净值': 数据位置字典['科目名称'], '年初单位净值': 数据位置字典['科目名称']},
          '银行存款': {'银行存款': 数据位置字典['市值']},
          '清算备付金': {'清算备付金': 数据位置字典['市值']},
          '存出保证金': {'存出保证金': 数据位置字典['市值']},
          '其他现金类资产': {'清算备付金': 数据位置字典['市值'], '存出保证金': 数据位置字典['市值']},
          '买入返售金额资产': {'买入返售金额资产': 数据位置字典['市值']},
          '买入返售金融资产': {'买入返售金融资产': 数据位置字典['市值']},
          '股票投资': {'股票投资': 数据位置字典['市值']},
          '债券投资': {'债券投资': 数据位置字典['市值']},
          '应收利息': {'应收利息': 数据位置字典['市值']},
          '应付管理人报酬': {'应付管理人报酬': 数据位置字典['市值']},
          '应付托管费': {'应付托管费': 数据位置字典['市值']},
          '应交税费': {'应交税费': 数据位置字典['市值']},
          '其他应付款': {'其他应付款': 数据位置字典['市值']},
          '卖出回购金融资产款': {'卖出回购金融资产款': 数据位置字典['市值']},
          '证券清算款': {'证券清算款': 数据位置字典['市值']}}

# 准备写入的excel文件
f = xlwt.Workbook()
sheet_write = f.add_sheet(u'Sheet1', cell_overwrite_ok=True)
# 遍历产品名称，提取数据
for i, product_name in enumerate(产品简称列表):
    sheet_write.write(i+1, 0, product_name)
    file_path = file_name(原始文件列表, product_name)
    if file_path is None:
        continue
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)
    for j, item in enumerate(读取栏目字典.keys()):
        sheet_write.write(0, j+1, item)
        item_dict = 读取栏目字典[item]
        value_data_name = 0.0  # 此项目的数总和，单位为元
        value_data_list = []  # 提取的数据的存储区
        for data_name in item_dict:    # 提取数据的操作
            value_data_list.append(get_data_from_excel(sheet, data_name, item_dict[data_name]))
        if item == '年化收益率':  # 年化收益率非求和，特殊处理
            value_data_name = (value_data_list[0] - value_data_list[1]) / value_data_list[1]
            value_data_name = '%.2f%%' % (value_data_name * 100.0)
        else:
            value_data_name = np.sum(np.array(value_data_list))
        print(product_name, item, value_data_name, i, j)
        sheet_write.write(i+1, j+1, value_data_name)
f.save('data\\output\\月报估值表.xls')