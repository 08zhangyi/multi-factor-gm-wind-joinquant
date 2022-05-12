import xlrd
import pandas as pd
from WindPy import w

ANALYSING_DATE = '2022-01-14'  # 取分析日收盘后数据

# 配置pandas，打印全部信息
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
# 自动读取股票持仓数据
FILE_PATH = 'C:\\Users\\pc\\Desktop\\策略计算表.xlsx'  # 参考data\策略计算表example.xlsx
file = xlrd.open_workbook(FILE_PATH)
table = file.sheet_by_name('股票组合')
row_number = table.nrows
result_list = []
for i in range(3, row_number):  # 提取股票代码和持仓数据
    value_code = table.cell(i, 1).value
    value_number = table.cell(i, 6).value
    value_ratio = table.cell(i, 10).value
    result_list.append([value_code, value_number, value_ratio])
df_result = pd.DataFrame(result_list, columns=['股票代码', '持仓数量', '持仓权重'])
# 提取中信行业信息
w.start()
industry_list = w.wss(list(df_result['股票代码']), "industry_citic", "tradeDate="+ANALYSING_DATE+";industryType=1").Data[0]
df_result['中信一级行业'] = industry_list
# 提取wind主体行业
industry_list = w.wss(list(df_result['股票代码']), "thematicindustry_wind", "tradeDate="+ANALYSING_DATE).Data[0]
df_result['万得主题行业'] = industry_list
# 输出
df_result.to_excel('output\\行业信息.xlsx')
# 显示行业信息
df_industry = df_result[['持仓权重', '中信一级行业']].groupby('中信一级行业').sum()
df_industry['持仓权重'] = df_industry['持仓权重'].apply(lambda x: format(x, '.2%'))
print(df_industry)
df_industry = df_result[['持仓权重', '万得主题行业']].groupby('万得主题行业').sum()
df_industry['持仓权重'] = df_industry['持仓权重'].apply(lambda x: format(x, '.2%'))
print(df_industry)