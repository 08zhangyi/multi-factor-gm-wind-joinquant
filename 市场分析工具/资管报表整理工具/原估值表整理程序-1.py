import os
import xlrd
import xlwt


# 辅助函数区
def get_data_from_excel(sheet, data_name, col_number):
    # 寻找data_name所在的行，用col_number的列提取出实际数据
    n_rows = sheet.nrows  # 提取表格的行数
    n_cols = sheet.ncols
    value_data_name = 0.0
    for n_r in range(n_rows):  # 寻找data_name所对应的行
        for n_c in range(n_cols):
            name_temp = sheet.cell_value(n_r, n_c)
            if isinstance(name_temp, float):
                continue
            if name_temp == data_name or name_temp[:-1] == data_name:
                value_data_name += float(sheet.cell_value(n_r, col_number)) if sheet.cell_value(n_r, col_number) != '' else 0.0
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
产品简称列表 = ['中惠1号', '融通10号', '融通5号']
# 结构为{'栏目名称': {'提取数据栏目1': 栏目位置1, '提取数据栏目2': 栏目位置2},}
读取栏目字典 = {'基金资产净值': {'基金资产净值': 数据位置字典['市值']},
          '资产类合计': {'资产类合计': 数据位置字典['市值']},
          '负债类合计': {'负债类合计': 数据位置字典['市值']},
          '基金单位净值': {'基金单位净值': 数据位置字典['科目名称']},
          '累计单位净值': {'累计单位净值': 数据位置字典['科目名称']},
          '年初单位净值': {'年初单位净值': 数据位置字典['科目名称']},
          '期初单位净值': {'期初单位净值': 数据位置字典['科目名称']},
          '年化收益率': {'基金单位净值': 数据位置字典['科目名称'], '年初单位净值': 数据位置字典['科目名称']},
          '银行存款': {'银行存款': 数据位置字典['市值']},
          '清算备付金': {'清算备付金': 数据位置字典['市值']},
          '存出保证金': {'存出保证金': 数据位置字典['市值']},
          '其他现金类资产': {'清算备付金': 数据位置字典['市值'], '存出保证金': 数据位置字典['市值']},
          '买入返售金额资产': {'买入返售金额资产': 数据位置字典['市值']},
          '应收利息': {'应收利息': 数据位置字典['市值']},
          '应付管理人报酬': {'应付管理人报酬': 数据位置字典['市值']},
          '应付托管费': {'应付托管费': 数据位置字典['市值']},
          '应交税费': {'应交税费': 数据位置字典['市值']},
          '其他应付款': {'其他应付款': 数据位置字典['市值']}}

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
        if item == '年化收益率':  # 年化收益率非求和，特殊处理
            value_1 = get_data_from_excel(sheet, '基金单位净值', 数据位置字典['科目名称'])
            value_2 = get_data_from_excel(sheet, '年初单位净值', 数据位置字典['科目名称'])
            value_data_name = (value_1 - value_2) / value_2
        else:
            value_data_name = 0.0  # 此项目的数总和，单位为元
            for data_name in item_dict:
                value_data_name += get_data_from_excel(sheet, data_name, item_dict[data_name])
        print(product_name, item, value_data_name, i, j)
        sheet_write.write(i+1, j+1, value_data_name)
f.save('data\\output\\原估值表1.xls')