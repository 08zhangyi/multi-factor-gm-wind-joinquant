import pandas as pd
import numpy as np
from WindPy import w
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# 申万一级行业名常量
columns_names = ['农林牧渔', '采掘', '化工', '钢铁', '有色金属', '电子', '家用电器', '食品饮料', '纺织服装',
                 '轻工制造', '医药生物', '公用事业', '交通运输', '房地产', '商业贸易', '休闲服务', '综合', '建筑材料',
                 '建筑装饰', '电气设备', '国防军工', '计算机', '传媒', '通信', '银行', '非银金融', '汽车', '机械设备']
# matplotlib设置中文显示
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['FangSong']
mpl.rcParams['axes.unicode_minus'] = False


# 使用到的函数
# 对相关性的df画热力图的函数
def plot_heatmap(df, columns_names, name=''):
    fig, ax = plt.subplots()
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
    plt.show()


# 主成分分布绘制图
def plot_pca_components(n):
    # n为第几个主成分
    component = pca_components[n, :]
    ratio = pca_explained_variance_ratio[n]
    fig, ax = plt.subplots()
    ax.bar(np.arange(len(columns_names)), component, 0.8)
    ax.set_xticks(np.arange(len(columns_names)))
    ax.set_xticklabels(columns_names)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_title('第'+str(n)+'个主成分的组成系数，方差比例为%.2f%%' % (ratio*100.0))
    fig.tight_layout()
    plt.show()


# 主成分回报图
def plot_pca_return_values(return_oneday, n):
    # return_oneday为某一日的各行业收益回报，n为计算到第几个PCA（不包括n）
    return_oneday = np.array(return_oneday).reshape((-1, 1))
    print(np.mean(return_oneday))
    pca_return_values = np.matmul(pca_components, return_oneday)[0:n, 0]
    l2_ratio = np.square(np.linalg.norm(pca_return_values)) / np.square(np.linalg.norm(return_oneday))
    print(pca_return_values)
    fig, ax = plt.subplots()
    rects = ax.bar(np.arange(len(pca_return_values)), pca_return_values, 0.8)
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, 1.01 * height, '%.2f%%' % height, ha="center", va='bottom')
    ax.set_title('前'+str(n)+'个主成分的收益贡献，占当日收益分布的平方范数比例为%.2f%%' % (l2_ratio * 100.0))
    ax.set_xticks(np.arange(len(pca_return_values)))
    fig.tight_layout()
    plt.show()


# 读取数据
df = pd.read_csv('data//data.csv', index_col=0)
columns = list(df.columns.values)
# w.start()
# columns_names = w.wss(','.join(columns), "sec_name").Data[0]

# 计算三大相关系数
pearson_corr = df.corr(method='pearson')
kendall_corr = df.corr(method='kendall')
spearman_corr = df.corr(method='spearman')

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
        pca_components[1, :] = -pca_components[1, :]
    else:
        pca_components[0, :] = -pca_components[0, :]

# 测试计算每日的收益率分布
w.start()
print(w.wss(','.join(columns), "pct_chg", "tradeDate=20181109;cycle=D").Data[0])
test_return = [-1.672970822043962, -1.1620441366525736, -0.5864365171350472, -1.0249515725496927, -1.2619353354926477, -0.06176108114694934, -1.3587441223239627, -0.6697546783714481, 0.06870746454814558, 0.4769069297306805, -0.7361213949730105, -0.6518287168486014, -0.9856302760125168, -0.6570431098732898, -0.1816393803234173, -0.4593019288861466, 0.7990557476616145, -1.440198924368219, -0.736087168945132, -0.0936627968292636, 0.021862321756827008, 0.18027533504283433, -0.7150836038677832, 1.0938123967923374, -3.0357761785871684, -1.3295511819735206, -0.32267698954664414, -0.3602766594404838]
plot_pca_return_values(test_return, 5)