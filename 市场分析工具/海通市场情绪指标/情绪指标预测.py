import pandas as pd

# 统计指标对应的信息位置
loc_dict = {'A股日换手率（年化五个交易日平滑，左轴）': 'Unnamed: 8',
            '融资交易额/总交易额(左轴）': 'Unnamed: 14',
            '涨停公司占比（左轴）': 'Unnamed: 19',
            'PE倒数减十年期国债收益率（%，左轴）': 'Unnamed: 26',
            '恒生AH股溢价指数(%，左轴）': 'Unnamed: 30',
            '信用利差（%，左轴）': 'Unnamed: 44'}
N_history = 200  # 预测数据需要的历史数据长度
df = pd.read_excel('data\\海通策略指标.xlsx')

for key in loc_dict.keys():
    time_series = df[loc_dict[key]].values[N_history:0:-1]
    print(time_series)