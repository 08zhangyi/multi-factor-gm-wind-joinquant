import pandas as pd
import pandas.core.groupby

df = pd.DataFrame([[1.0, 2.0, 3.0, 'a'], [2.0, 3.0, 4.0, 'b'], [1.2, 3.4, 5.6, 'a'], [1.3, 2.4, 5.2, 'b']], columns=['aa', 'bb', 'cc', 'dd'])
df_group_by = df.groupby('dd')
df_mean = df_group_by.mean()
# print(df_mean.loc['a'])  # 取某一行
print('------------')
temp_list = []
for name, df_temp in df_group_by:
    print(name)
    df_temp = df_temp[['aa', 'bb', 'cc']]
    df_temp = (df_temp - df_group_by.mean().loc[name])/df_temp - df_group_by.std().loc[name]
    print(df_temp)
    print('------------------')
    temp_list.append(df_temp)

df = pd.concat(temp_list, axis=0)
print(df)