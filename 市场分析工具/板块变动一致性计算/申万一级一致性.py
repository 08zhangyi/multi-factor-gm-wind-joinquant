from WindPy import w
import numpy as np
import textdistance

SW1 = {'801010.SI': 'a',
       '801020.SI': 'b',
       '801030.SI': 'c',
       '801040.SI': 'd',
       '801050.SI': 'e',
       '801080.SI': 'f',
       '801110.SI': 'g',
       '801120.SI': 'h',
       '801130.SI': 'i',
       '801140.SI': 'j',
       '801150.SI': 'k',
       '801160.SI': 'l',
       '801170.SI': 'm',
       '801180.SI': 'n',
       '801200.SI': 'o',
       '801210.SI': 'p',
       '801230.SI': 'q',
       '801710.SI': 'r',
       '801720.SI': 's',
       '801730.SI': 't',
       '801740.SI': 'u',
       '801750.SI': 'v',
       '801760.SI': 'w',
       '801770.SI': 'x',
       '801780.SI': 'y',
       '801790.SI': 'z',
       '801880.SI': 'A',
       '801890.SI': 'B'}


def get_history(date_end, T):
    w.start()
    print('获取指数历史数据......')
    if type(T) == int:
        date_start = w.tdaysoffset(-T, date_end, '').Data[0][0].strftime('%Y-%m-%d')
    else:
        date_start = T
    Data = w.wsd(list(SW1.keys()), "pct_chg", date_start, date_end, "")
    return_d = np.array(Data.Data)
    date_list = Data.Times
    date_list = [d.strftime('%Y-%m-%d') for d in date_list]
    print('指数历史数据获取完毕')
    return return_d, date_list


# 距离计算代码：Jaro，取全部
def calculate_Jaro_distance(d1, d2):
    SW1_list = np.array(list(SW1.keys()))
    SW1_list1 = SW1_list[np.argsort(d1)]
    SW1_list2 = SW1_list[np.argsort(d2)]
    SW1_list1 = ''.join([SW1[t] for t in SW1_list1])
    SW1_list2 = ''.join([SW1[t] for t in SW1_list2])
    print('计算距离......')
    d = textdistance.Jaro().distance(SW1_list1, SW1_list2)
    return d


# 距离计算代码：Levenshtein，取前N
def calculate_Levenshtein_distance(d1, d2):
    N = 10
    SW1_list = np.array(list(SW1.keys()))
    SW1_list1 = SW1_list[np.argsort(d1)][-N:]
    SW1_list2 = SW1_list[np.argsort(d2)][-N:]
    SW1_list1 = ''.join([SW1[t] for t in SW1_list1])
    SW1_list2 = ''.join([SW1[t] for t in SW1_list2])
    print('计算距离......')
    d = textdistance.Levenshtein().distance(SW1_list1, SW1_list2)
    d = textdistance.Jaro().distance(SW1_list1, SW1_list2)
    return d


def calculate_Jaro_distance_list(return_d, date_list):
    I = return_d.shape[1]
    result_list = []
    for i in range(I-1):
        d1 = return_d[:,  i]
        d2 = return_d[:, i+1]
        #d = calculate_Jaro_distance(d1, d2)
        d = calculate_Levenshtein_distance(d1, d2)
        date = date_list[i+1]
        print(date + '日相对前一日指数排序变动值为：%.8f' % d)
        result_list.append(d)
    result_mean = np.mean(result_list)
    print('从'+date_list[0]+'日到'+date_list[-1]+'日变动均值为：%.8f' % result_mean)
    return result_list, result_mean


def main():
    # date_end = '2019-01-31'
    # T = 20
    # return_d, date_list = get_history(date_end, T)

    date_start = '2018-12-28'
    date_end = '2019-01-31'
    return_d, date_list = get_history(date_end, date_start)
    calculate_Jaro_distance_list(return_d, date_list)
    print(len(date_list)-1)  # 输出交易日个数


main()