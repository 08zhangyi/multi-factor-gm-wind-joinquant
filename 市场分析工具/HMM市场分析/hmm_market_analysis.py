import pandas as pd
import numpy as np
from hmmlearn import hmm


def hmm_market_analysis(period, history_length, state_number=4, random_state=252, n_iter=1000):
    df = pd.read_csv('data\\market_data\\data_'+period+'.csv', index_col=0)
    date_list = list(df.index.values)[1:]
    return_values = np.log(df).diff().dropna()
    # 设计df的columns
    index_columns = list(df.columns.values)
    state_columns = ['state_'+str(i) for i in range(state_number)]
    next_state_columns = ['next_state_'+str(i) for i in range(state_number)]
    next_index_columns = ['next_'+code for code in index_columns]
    columns = index_columns + ['state'] + state_columns + next_state_columns + next_index_columns
    # 记录新的df的index和数据用
    calculate_data = []
    calculate_date_index = []
    for i in range(history_length, len(date_list)):
        calculate_date = date_list[i]
        return_values_temp = return_values.ix[i+1-history_length:i+1].values
        state, state_prob, trans_porb, means = hmm_model(return_values_temp, state_number=state_number, random_state=random_state, n_iter=n_iter)
        next_state_prob = np.matmul(state_prob.reshape(1, -1), trans_porb)[0]
        next_return = np.matmul(next_state_prob.reshape(1, -1), means)[0]
        # 记录数据
        calculate_data.append(list(return_values_temp[-1])+[state]+list(state_prob)+list(next_state_prob)+list(next_return))
        calculate_date_index.append(calculate_date)
    result_df = pd.DataFrame(data=calculate_data, index=calculate_date_index, columns=columns)
    result_df.to_csv('data\\predict_data\\result_'+period+'.csv')


def hmm_model(data, state_number, random_state, n_iter):
    model = hmm.GaussianHMM(n_components=state_number, covariance_type="diag", random_state=random_state, n_iter=n_iter)
    model.fit(data)
    state_prob = model.predict_proba(data)[-1]
    means = model.means_
    trans_porb = model.transmat_
    rank_position = np.argsort(means[:, 0])  # 取培训映照
    # 将对应数据都从由低到高排序，0为收益最低的状态，state_number-1为收益最高的状态
    state_prob = state_prob[rank_position]
    state = int(np.argmax(state_prob))
    means = means[rank_position]
    trans_porb = trans_porb[rank_position, :][:, rank_position]
    return state, state_prob, trans_porb, means



period = 'W'
history_length = 200
hmm_market_analysis(period, history_length)