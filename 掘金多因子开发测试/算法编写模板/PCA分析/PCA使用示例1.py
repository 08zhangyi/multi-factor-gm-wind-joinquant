import pandas as pd
import numpy as np
from WindPy import w
from sklearn.decomposition import PCA
import matplotlib
import matplotlib.pyplot as plt

df = pd.read_csv('data//data.csv', index_col=0)
w.start()
columns = list(df.columns.values)
columns_names = w.wss(','.join(columns), "sec_name").Data[0]

# 计算三大相关系数
pearson_corr = df.corr(method='pearson')
kendall_corr = df.corr(method='kendall')
spearman_corr = df.corr(method='spearman')


def plot_heatmap(df, name=''):
    fig, ax = plt.subplots()
    im = ax.imshow(df.values)
    ax.set_xticks(np.arange(len(columns_names)))
    ax.set_yticks(np.arange(len(columns_names)))
    ax.set_xticklabels(columns_names)
    ax.set_yticklabels(columns_names)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    for i in range(len(columns_names)):
        for j in range(len(columns_names)):
            text = ax.text(j, i, '%.0f' % (df.values[i, j]*100), ha="center", va="center", color="w")
    ax.set_title(name+'相关系数热力图')
    fig.tight_layout()
    plt.show()


from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['FangSong']
mpl.rcParams['axes.unicode_minus'] = False
plot_heatmap(pearson_corr, 'Pearson')
plot_heatmap(kendall_corr, 'Kendall')
plot_heatmap(spearman_corr, 'Spearman')

# PCA计算
pca = PCA(n_components=5)
pca.fit(df.values)
pca_components = pca.components_
pca_components[0, :] = -pca_components[0, :]
pca_explained_variance_ratio = pca.explained_variance_ratio_
print(pca_explained_variance_ratio)

df_pca = pd.DataFrame(pca_components, columns=columns_names)
df_pca.to_csv('data//pca_data.csv')


def plot_pca_components(n):
    component = pca_components[n, :]
    ratio = pca_explained_variance_ratio[n]
    fig, ax = plt.subplots()
    rects1 = ax.bar(np.arange(len(columns_names)), component, 0.8)
    ax.set_xticks(np.arange(len(columns_names)))
    ax.set_xticklabels(columns_names)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_title('第'+str(n)+'个主成分的组成系数，方差比例为%.2f%%' % (ratio*100.0))
    fig.tight_layout()
    plt.show()


plot_pca_components(0)
plot_pca_components(1)
plot_pca_components(2)
plot_pca_components(3)
plot_pca_components(4)