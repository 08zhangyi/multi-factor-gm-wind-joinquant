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
files_path = 'data\\余额表原始'  # 原始excel文件的列表
原始文件列表 = os.listdir(files_path)
原始文件列表 = [files_path+'\\'+f for f in 原始文件列表]
数据位置字典 = {'科目名称': 2, '累计贷方发生': 8, '期末': 10}
产品简称列表 = ['抚顺特钢', '中惠1号', '天诚25号', '天盈12号', '融通10号', '融通5号', '天泽1号', '汇沣1号',
                '天盈13号', '汇沣2号', '汇沣3号', '天沃1号']
# 结构为{'栏目名称': {'提取数据栏目1': 栏目位置1, '提取数据栏目2': 栏目位置2},}
读取栏目字典 = {'银行存款': {'银行存款': 数据位置字典['期末']},
          '清算备付金': {'清算备付金': 数据位置字典['期末']},
          '存出保证金': {'存出保证金': 数据位置字典['期末']},
          '存款科目': {'银行存款': 数据位置字典['期末'], '清算备付金': 数据位置字典['期末'], '存出保证金': 数据位置字典['期末']},
          '买入返售金融资产': {'买入返售金融资产': 数据位置字典['期末']},
          '股票投资': {'股票投资': 数据位置字典['期末']},
          '债券投资': {'债券投资': 数据位置字典['期末']},
          '应收利息': {'应收利息': 数据位置字典['期末']},
          '应收申购款': {'应收申购款': 数据位置字典['期末']},
          '基金投资': {'基金投资': 数据位置字典['期末']},
          '其他投资': {'其他投资': 数据位置字典['期末']},
          '应收股利': {'应收股利': 数据位置字典['期末']},
          '证券清算款': {'证券清算款': 数据位置字典['期末']},
          '计算的资产总值': {'银行存款': 数据位置字典['期末'], '清算备付金': 数据位置字典['期末'], '存出保证金': 数据位置字典['期末'],
                      '买入返售金融资产': 数据位置字典['期末'], '股票投资': 数据位置字典['期末'], '债券投资': 数据位置字典['期末'],
                      '应收利息': 数据位置字典['期末'], '应收申购款': 数据位置字典['期末'], '基金投资': 数据位置字典['期末'],
                      '其他投资': 数据位置字典['期末'], '应收股利': 数据位置字典['期末'], '证券清算款': 数据位置字典['期末']},
          '应付管理人报酬': {'应付管理人报酬':  数据位置字典['期末']},
          '应付托管费': {'应付托管费': 数据位置字典['期末']},
          '应付交易费用': {'应付交易费用': 数据位置字典['期末']},
          '应交税费': {'应交税费': 数据位置字典['期末']},
          '应付利息': {'应付利息': 数据位置字典['期末']},
          '卖出回购金融资产款': {'卖出回购金融资产款': 数据位置字典['期末']},
          '应付赎回款': {'应付赎回款': 数据位置字典['期末']},
          '其他应付款': {'其他应付款': 数据位置字典['期末']},
          '应付利润': {'应付利润': 数据位置字典['期末']},
          '计提的应付管理人报酬': {'应付管理人报酬': 数据位置字典['累计贷方发生']},
          '计提的应付托管费': {'应付托管费': 数据位置字典['累计贷方发生']},
          '计提的应付交易费用': {'应付交易费用': 数据位置字典['累计贷方发生']},
          '计提的应交税费': {'应交税费': 数据位置字典['累计贷方发生']},
          '计提的应付利息': {'应付利息': 数据位置字典['累计贷方发生']},
          '实收基金': {'实收基金': 数据位置字典['期末']},
          '损益平准金': {'损益平准金': 数据位置字典['期末']},
          '本期利润': {'本期利润': 数据位置字典['期末']},
          '收益分配': {'收益分配': 数据位置字典['期末']},
          '资产类合计': {'资产类合计': 数据位置字典['期末']},
          '负债类合计': {'负债类合计': 数据位置字典['期末']}}

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
        for data_name in item_dict:  # 提取数据的操作
            value_data_list.append(get_data_from_excel(sheet, data_name, item_dict[data_name]))
        value_data_name = np.sum(np.array(value_data_list))
        if '计提' not in item:
            value_data_name = value_data_name / 10000.0  # 单位转化为万元
        print(product_name, item, value_data_name, i, j)
        sheet_write.write(i+1, j+1, value_data_name)
f.save('data\\output\\新余额报表.xls')