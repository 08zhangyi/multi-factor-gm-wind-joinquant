import tushare as ts
from aip import AipNlp
import time
from pyecharts.charts import WordCloud
from pyecharts.options import InitOpts
import math

start_date = '2020-04-21 08:00:00'
end_date = '2020-04-21 08:30:00'
# 百度配置
APP_ID = '10709883'
API_KEY = 'DP7yZde5EK2MEKLzcjzwCCp5'
SECRET_KEY = 'EQPFBZOjgyyhpf9llpsZobIUIftpyj8I'
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
# tushare配置
pro = ts.pro_api(token='fcd3ee99a7d5f0e27c546d074a001f0b3eae01312c4dd8354415fba1')
# 股票中文名称列表
names_data = pro.stock_basic(exchange='', list_status='L', fields='name').values
name_normalization = lambda d: d[0][:-1] if d[0][-1] == 'A' or d[0][-1] == 'B' else d[0]
names_data = [name_normalization(d) for d in names_data]

# 提取新闻信息
df_news = pro.news(src='sina', fields='datetime,content,channels', start_date=start_date, end_date=end_date)
ds_content = df_news['content']
ds_channel = df_news['channels']

content_negative = []  # 文章情感倾向记录
words_score_dict = {}
for i in range(len(ds_content)):
    # 文章内容处理与准备
    content = ds_content[i]
    content = content.split('】')
    content_main = content[-1]
    content_title2 = content[0][1:]
    if len(content_title2) > 40:  # 调整标题长度过长
        content_title2 = content_title2[:40]
    content_main2 = content_main
    if content_main2 == '':  # 无内容，跳过
        continue
    while len(content_main2) < 50:  # 调整内容长度过短
        content_main2 = 2 * content_main2
    print('正在处理第%d条新闻，总共%d篇' % (i + 1, len(ds_content)))
    try:
        time.sleep(0.1)
        # 内容情感分析部分
        baidu_return = client.sentimentClassify(content_main)
        t_label = False
        for t in ds_channel[i]:
            if t['name'] == 'A股' or '公司':  # 仅分析这两个领域的新闻
                t_label = True
        if t_label:
            content_negative.append((baidu_return['text'], baidu_return['items'][0]['negative_prob']))  # 提取内容和负面度
            # content_negative.append((baidu_return['text'], baidu_return['items'][0]['confidence']))  # 提取内容和置信
        # 内容标签提取
        baidu_return = client.keyword(content_title2, content_main2)
        items = baidu_return['items']
        for item in items:
            words_score_dict[item['tag']] = words_score_dict.get(item['tag'], 0.0) + item['score']
    except (UnicodeEncodeError, UnicodeDecodeError, KeyError):
        continue

# 舆情负面程度排序
takeSecond = lambda elem: elem[1]
content_negative.sort(key=takeSecond, reverse=True)
content_negative = content_negative[:20]  # 取最负面的若干条新闻
name_negative = []
negative_content = '重要舆情新闻汇总\n\n'
for i in range(len(content_negative)):
    negative_content += ('    第' + str(i+1) + '条新闻：' + content_negative[i][0] + '\n\n')
    for name in names_data:
        if name in content_negative[i][0]:
            name_negative.append(name)
name_negative = list(set(name_negative))
negative_content += '\n重要舆情新闻涉及到的股票为：\n'
for name in name_negative:
    negative_content += (name + '，')
f = open('data\\'+end_date[:10]+'舆情晨报新闻.txt', 'w', encoding='utf-8')  # 保存文件
f.write(negative_content)
f.close()
print(negative_content)
# 标签汇总
delete_words = ['投资', '股票', '经济', '时政', '宏观经济', '时政外交', '财经', '金融', '公司', '国内宏观', '国外宏观',
                '国际社会', '分析师', '银行', '基金', '保险', '环比', '同比', '董事会', '股东', '外汇', '期货',
                '证券', '股权', '会议纪要', '子公司', '能源']  # 去除无意义的词汇，相当于停用词
for w in delete_words:
    try:
        del words_score_dict[w]
    except KeyError:
        continue
sorted_words_score = sorted(words_score_dict.items(), key=lambda d: d[1], reverse=True)
print(sorted_words_score)
words, scores = zip(*sorted_words_score)
word_cloud = WordCloud(InitOpts(width="1600px", height="1000px"))
scores = [math.sqrt(score) for score in scores]  # 调整权重以画图显示的更好
words = list(zip(words, scores))
word_cloud.add("", words, shape="circle")
word_cloud.render('data\\'+end_date[:10]+'舆情晨报词云.html')  # 保存文件