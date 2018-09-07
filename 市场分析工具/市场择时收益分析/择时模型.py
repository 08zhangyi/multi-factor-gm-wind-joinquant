from WindPy import w
import QuantLib as ql
import numpy as np
import pandas as pd
import pygal
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_trading_date_from_now


class SelectTimeIndexBacktest(object):
    def __init__(self, backtest_start_date, backtest_end_date, index_code):
        self.index_code = index_code
        self.date_list, self.index_list, self.signal_list = self._get_data()
        self.index_list = [t/self.index_list[0] for t in self.index_list]
        self.signal_list = [1 if t == 1 else 0 for t in self.signal_list]  # 多信号入场，空信号空仓
        # 一句择时信号计算累积收益
        return_list = np.diff(np.log(np.array(self.index_list)))
        return_list = np.cumsum(return_list * np.array(self.signal_list[:-1]))
        return_list = np.concatenate(([0], return_list))
        self.return_list = list(np.exp(return_list))  # 根据择时信号计算的累计收益率

    def get_return(self):
        data = np.array([self.index_list, self.return_list, self.signal_list]).transpose()
        df = pd.DataFrame(data, index=self.date_list, columns=['指数累积收益', '择时累积收益', '择时信号'])
        print(df)
        return df

    def plot_return(self, infor=''):
        line_chart = pygal.Line()
        line_chart.title = '指数'+self.index_code+'的择时收益表现'
        line_chart.x_labels = self.date_list
        line_chart.add('指数累积收益', self.index_list)
        line_chart.add('择时累积收益', self.return_list)
        line_chart.render_to_file('图片\\纯多择时收益图_'+infor+'.svg')

    def _get_signal(self, date_now):
        '''
        获取某一日的择时信号，需要具体实现
        :param date_now: 计算date_now当天收盘后的择时指标
        :return : 择时信号返回值，1为看多，-1为看空，0为不确定
        '''
        pass

    def _get_data(self):
        '''
        获取择时时间、信号、指数序列，需要具体实现
        :return date_list: 日期列表
        :return index_list: 指数值列表
        :return signal_list: 择时信号列表
        '''
        date_list = []
        index_list = []
        signal_list = []
        return date_list, index_list, signal_list


class LLT_base(SelectTimeIndexBacktest):
    # LLT择时基本版模型
    # 计算index_code的收盘指数的择时信号，并做回测
    def __init__(self, backtest_start_date, backtest_end_date, index_code, llt_d, llt_cal_history=100, llt_threshold=0.0):
        '''
        :param llt_d: 上证综指适合参数39
        :param llt_cal_history:
        :param llt_threshold:
        '''
        w.start()
        llt_start_date = get_trading_date_from_now(backtest_start_date, -llt_cal_history, ql.Days)
        data = w.wsd(index_code, "close", llt_start_date, backtest_end_date, "")
        self.llt_times = [t.strftime('%Y-%m-%d') for t in data.Times]
        self.llt_data = data.Data[0]
        self.llt_d = llt_d
        self.llt_threshold = llt_threshold
        self.llt_cal_history = llt_cal_history  # LLT信号计算的历史长度
        self.backtest_start_date = backtest_start_date
        super().__init__(backtest_start_date, backtest_end_date, index_code)

    def _get_signal(self, date_now):
        llt_index = self.llt_times.index(date_now) + 1
        price_list = self.llt_data[llt_index - self.llt_cal_history:llt_index]
        llt_value = self._LLT(price_list)
        return llt_value

    def _get_data(self):
        start_date_index = self.llt_times.index(self.backtest_start_date)
        date_list = self.llt_times[start_date_index:]
        index_list = self.llt_data[start_date_index:]
        signal_list = [self._get_signal(date) for date in date_list]
        return date_list, index_list, signal_list

    def _LLT(self, price_list):
        a = 2 / (self.llt_d + 1)  # LLT的参数
        LLT_list = [price_list[0], price_list[1]]  # 记录LLT值列表的初始化序列
        for t in range(2, len(price_list)):
            LLT_value = (a - (a ** 2 / 4)) * price_list[t] + (a ** 2 / 2) * price_list[t - 1] - (a - (3 * a ** 2 / 4)) * \
                        price_list[t - 2] + 2 * (1 - a) * LLT_list[-1] - (1 - a) ** 2 * LLT_list[-2]
            LLT_list.append(LLT_value)
        return 1 if (((LLT_list[-1] - LLT_list[-2]) / price_list[-1]) > self.llt_threshold) else -1


if __name__ == '__main__':
    model = LLT_base('2016-02-02', '2018-09-06', '000001.SH', llt_d=9)
    model.plot_return('9')