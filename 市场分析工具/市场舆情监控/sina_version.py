import tushare as ts
from aip import AipNlp
import time
import re

start_date = '2018-12-28 15:00:00'
end_date = '2019-01-02 09:00:00'
# 百度配置
APP_ID = '10709883'
API_KEY = 'DP7yZde5EK2MEKLzcjzwCCp5'
SECRET_KEY = 'EQPFBZOjgyyhpf9llpsZobIUIftpyj8I'
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
# tushare配置
pro = ts.pro_api(token='9668f6b57f4e3fe1199446a9c7b251d553963832bbf6e411b8065ea2')
# 股票中文名称列表
names_data = pro.stock_basic(exchange='', list_status='L', fields='name').values
names_data = [re.sub('[AB]', '', d[0]) for d in names_data]

# 提取新闻信息
df_news = pro.news(src='sina', start_date=start_date, end_date=end_date)
ds_content = df_news['content']
ds_channel = df_news['channels']

content_negative = []
for i in range(len(ds_content)):
    time.sleep(0.1)  # 百度调用远程接口，防止溢出
    content = ds_content[i]
    content = content.split('】')
    content = content[-1]
    print('正在处理第%d条新闻，总共%d篇' % (i + 1, len(ds_content)))
    try:
        time.sleep(0.1)
        baidu_return = client.sentimentClassify(content)
        t_label = False
        for t in ds_channel[i]:
            if t['name'] == 'A股':
                t_label = True
        if t_label:
            content_negative.append((baidu_return['text'], baidu_return['items'][0]['negative_prob']))  # 提取内容和负面度
    except UnicodeEncodeError:
        continue

# 排序数据
takeSecond = lambda elem: elem[1]
content_negative.sort(key=takeSecond)
content_negative = content_negative[-40:]  # 取最负面的若干条新闻
name_negative = []
for i in range(len(content_negative)):
    print(content_negative[i])
    for name in names_data:
        if name in content_negative[i][0]:
            name_negative.append(name)
name_negative = list(set(name_negative))
print('\n负面新闻牵扯到的股票为：')
print(name_negative)
