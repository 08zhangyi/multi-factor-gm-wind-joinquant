from WindPy import w
import pandas as pd
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from 择时模型 import RSRS_standardization_V1
from utils import get_trading_date_from_now

# 需要查询的行业和查询日期，query为收盘日
w.start()
query_date = '2021-08-17'
industry_index_1 = w.wset("sectorconstituent", "date=" + query_date + ";sectorid=1000017213000000").Data[1]
industry_index_2 = w.wset("sectorconstituent", "date=" + query_date + ";sectorid=a39901012f000000").Data[1]

# 计算择时信号
data_using = get_trading_date_from_now(query_date, 1)
N = 18
M = 600
# 万得热门
select_time_result = []
industry_index_name = w.wss(industry_index_1, "sec_name").Data[0]
for index in industry_index_1:
    model = RSRS_standardization_V1(data_using, data_using, index, N=N, M=M)
    select_time_value = model.RSRS_stand_data[-1]
    select_time_result.append(select_time_value)
    print(index + '在' + query_date + '收盘的RSRS择时信号为：%.4f' % select_time_value)
# 结果输出
df_result = pd.DataFrame(zip(industry_index_1, industry_index_name, select_time_result), columns=['行业指数', '行业名称', 'RSRS择时指标'])
df_result = df_result.sort_values('RSRS择时指标', ascending=False)
df_result.to_excel('data_output\\result_' + query_date + '_万得热门.xlsx')
# 中信二级
select_time_result = []
industry_index_name = w.wss(industry_index_2, "sec_name").Data[0]
for index in industry_index_2:
    model = RSRS_standardization_V1(data_using, data_using, index, N=N, M=M)
    select_time_value = model.RSRS_stand_data[-1]
    select_time_result.append(select_time_value)
    print(index + '在' + query_date + '收盘的RSRS择时信号为：%.4f' % select_time_value)
# 结果输出
df_result = pd.DataFrame(zip(industry_index_2, industry_index_name, select_time_result), columns=['行业指数', '行业名称', 'RSRS择时指标'])
df_result = df_result.sort_values('RSRS择时指标', ascending=False)
df_result.to_excel('data_output\\result_' + query_date + '_中信二级.xlsx')