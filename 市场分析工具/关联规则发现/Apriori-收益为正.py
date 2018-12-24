import pandas as pd
import numpy as np
import os
from WindPy import w
# 引入算法
from efficient_apriori import apriori

# 申万一级行业名常量
columns_names = ['农林牧渔', '采掘', '化工', '钢铁', '有色金属', '电子', '家用电器', '食品饮料', '纺织服装',
                 '轻工制造', '医药生物', '公用事业', '交通运输', '房地产', '商业贸易', '休闲服务', '综合', '建筑材料',
                 '建筑装饰', '电气设备', '国防军工', '计算机', '传媒', '通信', '银行', '非银金融', '汽车', '机械设备']
SW1 = "801010.SI,801020.SI,801030.SI,801040.SI,801050.SI,801080.SI,801110.SI,801120.SI,801130.SI,801140.SI,801150.SI,801160.SI,801170.SI,801180.SI,801200.SI,801210.SI,801230.SI,801710.SI,801720.SI,801730.SI,801740.SI,801750.SI,801760.SI,801770.SI,801780.SI,801790.SI,801880.SI,801890.SI"
# matplotlib设置中文显示
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['FangSong']
mpl.rcParams['axes.unicode_minus'] = False


# 使用到的函数
# 数据提取函数
def get_data(end_date, history):
    w.start()
    start_date = w.tdaysoffset(-history, end_date, "").Data[0][0].strftime('%Y-%m-%d')
    file_path = 'data\\data.csv'
    if os.path.exists(file_path):  # 存在数据文件
        df = pd.read_csv(file_path, index_col=0)
        index = df.index.values
        if index[0] != start_date or index[-1] != end_date:  # 时间日期不符
            os.remove(file_path)  # 删除数据文件
            data = w.wsd(SW1, "pct_chg", start_date, end_date, "PriceAdj=T")
            df = pd.DataFrame(data=np.array(data.Data).transpose(), index=data.Times, columns=SW1.split(','))
            df.to_csv(file_path)
    else:  # 不存在数据文件
        data = w.wsd(SW1, "pct_chg", start_date, end_date, "PriceAdj=T")
        df = pd.DataFrame(data=np.array(data.Data).transpose(), index=data.Times, columns=SW1.split(','))
        df.to_csv(file_path)


def df_to_basket(df):
    # N为进入购物篮的排名位次
    basket = []
    for _, l in df.iterrows():
        l = l.values
        basket.append(tuple(np.array(columns_names)[l>0.0]))
    return basket


def print_results(rules):
    print(END_DATE+'日收盘后截取'+str(history)+'个交易日挖掘的规则数据（收益为正进入篮子）')
    print('最小支撑度为%.3f，最小置信度为%.3f' % (min_support, min_confidence))
    for rule in rules:
        conf = '置信度: {0:.3f}'.format(rule.confidence)
        supp = '支撑度: {0:.3f}'.format(rule.support)
        string_rule = '{} -> {} ({}, {})'.format(rule._pf(rule.lhs), rule._pf(rule.rhs), conf, supp)
        print(string_rule)


# 算法参数配置
END_DATE = '2018-12-03'
history = 240  # 提取数据的历史长短
min_support = 0.40  # 共同出现项的频率
min_confidence = 0.95  # 挖掘出规则的置信度
get_data(END_DATE, history)
df = pd.read_csv('data\\data.csv', index_col=0)
basket = df_to_basket(df)
itemsets, rules = apriori(basket, min_support=min_support,  min_confidence=min_confidence)
print_results(rules)