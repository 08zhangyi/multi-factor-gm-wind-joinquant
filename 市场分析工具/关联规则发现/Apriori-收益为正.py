import pandas as pd
import numpy as np
import os
from WindPy import w
# 引入算法
from efficient_apriori import apriori

# 中信一级行业名常量
columns_names = ['石油石化', '煤炭', '有色金属', '电力及公用事业', '钢铁', '基础化工', '建筑', '建材', '轻工制造',
                 '机械', '电力设备及新能源', '国防军工', '汽车', '商贸零售', '消费者服务', '家电', '纺织服装', '医药',
                 '食品饮料', '农林牧渔', '银行', '非银行金融', '房地产', '交通运输', '电子', '通信', '计算机',
                 '传媒', '综合', '综合金融']
ZX1 = "CI005001.WI,CI005002.WI,CI005003.WI,CI005004.WI,CI005005.WI,CI005006.WI,CI005007.WI,CI005008.WI,CI005009.WI," \
      "CI005010.WI,CI005011.WI,CI005012.WI,CI005013.WI,CI005014.WI,CI005015.WI,CI005016.WI,CI005017.WI,CI005018.WI," \
      "CI005019.WI,CI005020.WI,CI005021.WI,CI005022.WI,CI005023.WI,CI005024.WI,CI005025.WI,CI005026.WI,CI005027.WI," \
      "CI005028.WI,CI005029.WI,CI005030.WI"
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
            data = w.wsd(ZX1, "pct_chg", start_date, end_date, "PriceAdj=T")
            df = pd.DataFrame(data=np.array(data.Data).transpose(), index=data.Times, columns=ZX1.split(','))
            df.to_csv(file_path)
    else:  # 不存在数据文件
        data = w.wsd(ZX1, "pct_chg", start_date, end_date, "PriceAdj=T")
        df = pd.DataFrame(data=np.array(data.Data).transpose(), index=data.Times, columns=ZX1.split(','))
        df.to_csv(file_path)


def df_to_basket(df):
    # N为进入购物篮的排名位次，去收益率为正的行业进入篮子
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
END_DATE = '2021-01-08'
history = 120  # 提取数据的历史长短
min_support = 0.40  # 共同出现项的频率
min_confidence = 0.95  # 挖掘出规则的置信度
get_data(END_DATE, history)
df = pd.read_csv('data\\data.csv', index_col=0)
basket = df_to_basket(df)
itemsets, rules = apriori(basket, min_support=min_support,  min_confidence=min_confidence)
print_results(rules)