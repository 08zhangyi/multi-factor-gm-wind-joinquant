import pandas as pd
import numpy as np
from hmmlearn import hmm
import pygal

df = pd.read_csv('data\\data.csv', index_col=0)
date_list = list(df.index.values)[1:]
return_values = np.log(df).diff().dropna().values
index_values = df.values[1:]

remodel = hmm.GaussianHMM(n_components=4, covariance_type="diag", random_state=252, n_iter=10000)
remodel.fit(return_values)
state_prob = remodel.predict_proba(return_values)
state = remodel.predict(return_values)
state_list = list(state)
state_list = [int(t) for t in state_list]
for i in range(4):
    print(str(i)+':'+str(state_list.count(i)))

print(state_prob.shape, return_values.shape, state.shape)
line_chart = pygal.Line()
line_chart.title = "市场四隐含状态分布图"
line_chart.x_labels = date_list
for i in range(4):
    line_chart.add("状态"+str(i), state_prob[:, i])
line_chart.render_to_file('data\\line.svg')

print(state_prob[-1])
print(remodel.transmat_)
print(remodel.means_)
print(np.sqrt(remodel.covars_))