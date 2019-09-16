import pandas as pd
import numpy as np
import os
from WindPy import w
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# 申万一级行业名常量
columns_names = ['农林牧渔', '采掘', '化工', '钢铁', '有色金属', '电子', '家用电器', '食品饮料', '纺织服装',
                 '轻工制造', '医药生物', '公用事业', '交通运输', '房地产', '商业贸易', '休闲服务', '综合', '建筑材料',
                 '建筑装饰', '电气设备', '国防军工', '计算机', '传媒', '通信', '银行', '非银金融', '汽车', '机械设备',
                 '中证国债', '中证信用债']
SW1 = "801010.SI,801020.SI,801030.SI,801040.SI,801050.SI,801080.SI,801110.SI,801120.SI,801130.SI,801140.SI,801150.SI,801160.SI,801170.SI,801180.SI,801200.SI,801210.SI,801230.SI,801710.SI,801720.SI,801730.SI,801740.SI,801750.SI,801760.SI,801770.SI,801780.SI,801790.SI,801880.SI,801890.SI,H11006.CSI,H11073.CSI"
# matplotlib设置中文显示
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['FangSong']
mpl.rcParams['axes.unicode_minus'] = False


# 使用到的函数
# 数据提取函数
def get_data(end_date, start_date=None):
    w.start()
    if not start_date:  # 不给定起始日期，自用回推240天计算起始日期
        start_date = w.tdaysoffset(-240, end_date, "").Data[0][0].strftime('%Y-%m-%d')
    file_path = 'data\\after_close\\data.csv'
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


# 对相关性的df画热力图的函数
def plot_heatmap(df, name=''):
    fig, ax = plt.subplots(figsize=(16, 16))
    ax.imshow(df.values)
    ax.set_xticks(np.arange(len(columns_names)))
    ax.set_yticks(np.arange(len(columns_names)))
    ax.set_xticklabels(columns_names)
    ax.set_yticklabels(columns_names)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    for i in range(len(columns_names)):
        for j in range(len(columns_names)):
            ax.text(j, i, '%.0f' % (df.values[i, j]*100), ha="center", va="center", color="w")  # 乘以100取整
    ax.set_title(name+'相关系数热力图')
    fig.tight_layout()
    # plt.show()
    plt.savefig("data\\after_close\\"+name+"相关系数热力图.jpg")


# 主成分分布绘制图
def plot_pca_components(n):
    # n为第几个主成分
    component = pca_components[n, :]
    ratio = pca_explained_variance_ratio[n]
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.bar(np.arange(len(columns_names)), component, 0.8)
    ax.set_xticks(np.arange(len(columns_names)))
    ax.set_xticklabels(columns_names, size=20)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_title('第'+str(n)+'个主成分的组成系数，方差比例为%.2f%%' % (ratio*100.0))
    fig.tight_layout()
    # plt.show()
    plt.savefig("data\\after_close\\第"+str(n)+"个主成分的组成系数图.jpg")


# 主成分回报图
def plot_pca_return_values(return_oneday, n):
    # return_oneday为某一日的各行业收益回报，n为计算到第几个PCA（不包括n）
    return_oneday = np.array(return_oneday).reshape((-1, 1))
    return_oneday_mean = np.mean(return_oneday)
    pca_return_values = np.matmul(pca_components, return_oneday)[0:n, 0]
    l2_ratio = np.square(np.linalg.norm(pca_return_values)) / np.square(np.linalg.norm(return_oneday))
    pca_return_values = pca_return_values / np.sqrt(len(columns_names))
    print(pca_return_values)
    fig, ax = plt.subplots(figsize=(16, 16))
    rects = ax.bar(np.arange(len(pca_return_values)), pca_return_values, 0.8)
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, 1.01 * height, '%.2f%%' % height, ha="center", va='bottom', size=40)
    ax.set_title('前'+str(n)+'个主成分的收益贡献，占当日收益分布的平方范数比例为%.2f%%' % (l2_ratio * 100.0)+'，申万行业收益算术均值为%.2f%%' % return_oneday_mean, size=30)
    ax.set_xticks(np.arange(len(pca_return_values)))
    fig.tight_layout()
    # plt.show()
    plt.savefig("data\\after_close\\主成分回报分布图.jpg")


# 设定计算日期函数和主成分提取参数
END_DATE = "2019-08-28"  # 收盘计算日期
N = 5
# 读取数据
get_data(END_DATE)
df = pd.read_csv('data\\after_close\\data.csv', index_col=0)
columns = list(df.columns.values)
# w.start()
# columns_names = w.wss(','.join(columns), "sec_name").Data[0]

# 计算三大相关系数
pearson_corr = df.corr(method='pearson')
plot_heatmap(pearson_corr, 'Pearson')
kendall_corr = df.corr(method='kendall')
plot_heatmap(kendall_corr, 'Kendall')
spearman_corr = df.corr(method='spearman')
plot_heatmap(spearman_corr, 'Spearman')

# PCA计算
return_values = df.values
pca = PCA(n_components=len(columns_names))
pca.fit(return_values)

# 取出PCA的变幻矩阵
pca_components = pca.components_
pca_explained_variance_ratio = pca.explained_variance_ratio_
# pca_components * Cov(return_values) * pca_componentsT = diagonal
if np.sum(pca_components[0, :]) < 0:  # 修正第0个主成分为正值，且旋转矩阵pca_components保持镜像
    if np.linalg.det(pca_components) > 0:
        pca_components[0, :] = -pca_components[0, :]
        pca_components[-1, :] = -pca_components[1, :]
    else:
        pca_components[0, :] = -pca_components[0, :]
print(np.linalg.det(pca_components))
# PCA成分展示图
for i in range(N):
    plot_pca_components(i)

# 测试计算每日的收益率分布
w.start()
test_return = w.wss(','.join(columns), "pct_chg", "tradeDate="+END_DATE+";cycle=D").Data[0]
plot_pca_return_values(test_return, N)