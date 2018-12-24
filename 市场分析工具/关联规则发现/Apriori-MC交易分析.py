import xlrd
import re
from efficient_apriori import apriori


def get_basket(file_path):
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)
    result_temp = {}
    date_temp = None
    for i in range(1, sheet.nrows-1):
        # 读取交易品种和交易日期的代码
        name = process_name(sheet.cell(i, 9).value)
        date = sheet.cell(i, 14).value[0:10]
        # 按日整理归类数据
        if date != date_temp:
            date_temp = date
            result_temp[date_temp] = [name]
        else:
            result_temp[date_temp].append(name)
    # 将数据处理为购物篮格式
    basket = [tuple(set(t)) for t in result_temp.values()]
    return basket


def process_name(name):
    # 提取品种名字信息
    if len(name) > 6:
        name = name[:-4]
    else:
        name = re.search('[\u4e00-\u9fa5]+', name)[0]
    return name


def print_results(rules):
    print('交易品种汇总数据')
    print('最小支撑度为%.3f，最小置信度为%.3f' % (min_support, min_confidence))
    for rule in rules:
        conf = '置信度: {0:.3f}'.format(rule.confidence)
        supp = '支撑度: {0:.3f}'.format(rule.support)
        string_rule = '{} -> {} ({}, {})'.format(rule._pf(rule.lhs), rule._pf(rule.rhs), conf, supp)
        print(string_rule)


if __name__ == '__main__':
    file_path = 'data//jy.xls'
    basket = get_basket(file_path)
    min_support = 0.02
    min_confidence = 0.05
    itemsets, rules = apriori(basket, min_support=min_support, min_confidence=min_confidence)
    print_results(rules)