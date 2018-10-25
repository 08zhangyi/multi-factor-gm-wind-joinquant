from WindPy import w
import QuantLib as ql
import numpy as np
import pandas as pd
import pygal
from sklearn import linear_model
from sklearn.metrics import r2_score
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_trading_date_from_now


class SelectTimeIndexBacktest(object):
    def __init__(self, backtest_start_date, backtest_end_date, index_code):
        self.index_code = index_code
        self.date_list, self.index_list, self.signal_list = self._get_data()
        self.index_list = [t/self.index_list[0] for t in self.index_list]
        self.signal_list = [1 if t == 1 else 0 for t in self.signal_list]  # 多信号入场，空信号空仓，适用于股票
        # 对self.signal_list不修正时，1信号做多，-1信号做空，0信号空仓，适用于期货
        print(self.signal_list)
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
        if infor != '':
            infor = '_' + infor
        line_chart = pygal.Line()
        line_chart.title = '指数'+self.index_code+'的择时收益表现'
        line_chart.x_labels = self.date_list
        line_chart.add('指数累积收益', self.index_list)
        line_chart.add('择时累积收益', self.return_list)
        line_chart.render_to_file('图片\\纯多择时收益图'+infor+'.svg')

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


class RSRS_base(SelectTimeIndexBacktest):
    # RSRS择时基本版模型
    # 计算index_code的收盘指数的择时信号，并做回测
    def __init__(self, backtest_start_date, backtest_end_date, index_code, N, S1=1.0, S2=0.8):
        w.start()
        RSRS_start_date = get_trading_date_from_now(backtest_start_date, -N, ql.Days)
        data = w.wsd(index_code, "high,low,close", RSRS_start_date, backtest_end_date, "")
        self.RSRS_times = [t.strftime('%Y-%m-%d') for t in data.Times]
        self.RSRS_data_high = data.Data[0]
        self.RSRS_data_low = data.Data[1]
        self.RSRS_data = data.Data[2]
        self.backtest_start_date = backtest_start_date
        self.N = N  # 计算RSRS指标采样的历史周期长短
        self.S1 = S1
        self.S2 = S2
        super().__init__(backtest_start_date, backtest_end_date, index_code)

    def _get_signal(self, date_now):
        RSRS_index = self.RSRS_times.index(date_now) + 1
        high_price_list = self.RSRS_data_high[RSRS_index - self.N:RSRS_index]
        low_price_list = self.RSRS_data_low[RSRS_index - self.N:RSRS_index]
        RSRS_value = self._RSRS(high_price_list, low_price_list)
        return RSRS_value

    def _get_data(self):
        start_date_index = self.RSRS_times.index(self.backtest_start_date)
        date_list = self.RSRS_times[start_date_index:]
        index_list = self.RSRS_data[start_date_index:]
        signal_list = [self._get_signal(date) for date in date_list]
        # 对signal_list进行后续处理以形成持仓信号
        for i, signal_value in enumerate(signal_list):
            if i == 0:
                if signal_value > self.S1:  # 大于S1开仓
                    signal_list[i] = 1
                else:  # 空仓
                    signal_list[i] = -1
            else:
                if signal_value > self.S1:  # 大于S1开仓
                    signal_list[i] = 1
                elif signal_value > self.S2:  # 大于S2维持仓位
                    signal_list[i] = signal_list[i-1]
                else:  # 小于S2平仓
                    signal_list[i] = -1
        return date_list, index_list, signal_list

    def _RSRS(self, high_price_list, low_price_list):
        high_price_list = np.array(high_price_list)
        low_price_list = np.array(low_price_list).reshape(-1, 1)
        reg = linear_model.LinearRegression()
        reg.fit(low_price_list, high_price_list)  # low为自变量，high为因变量
        RSRS_value = reg.coef_[0]
        return RSRS_value


class RSRS_standardization(SelectTimeIndexBacktest):
    # RSRS择时M天标准化序列版
    # 计算index_code的收盘指数的择时信号，并做回测
    def __init__(self, backtest_start_date, backtest_end_date, index_code, N, M, S1=0.7, S2=-0.7):
        w.start()
        RSRS_start_date = get_trading_date_from_now(backtest_start_date, -N - M, ql.Days)
        data = w.wsd(index_code, "high,low,close", RSRS_start_date, backtest_end_date, "PriceAdj=T")
        self.RSRS_times = [t.strftime('%Y-%m-%d') for t in data.Times]
        self.RSRS_data_high = data.Data[0]
        self.RSRS_data_low = data.Data[1]
        self.RSRS_data = data.Data[2]
        self.backtest_start_date = backtest_start_date
        self.RSRS_cal_start_date = get_trading_date_from_now(backtest_start_date, -M, ql.Days)
        # 整理计算用的不同的时间序列
        self.RSRS_raw_cal_times = self.RSRS_times[self.RSRS_times.index(self.RSRS_cal_start_date):]
        self.RSRS_stand_cal_times = self.RSRS_times[self.RSRS_times.index(self.backtest_start_date):]
        self.N = N  # 计算RSRS指标采样的历史周期长短
        self.M = M  # 标准化序列的历史周期长短
        self.S1 = S1
        self.S2 = S2
        super().__init__(backtest_start_date, backtest_end_date, index_code)

    def _get_signal(self, date_now):
        index = self.RSRS_stand_cal_times.index(date_now)
        return self.signal_list[index]

    def _get_raw_data(self, date_now):
        index = self.RSRS_times.index(date_now)
        high_price_list = self.RSRS_data_high[index-self.N+1:index+1]  # 包含date_now的数据
        low_price_list = self.RSRS_data_low[index-self.N+1:index+1]
        return self._RSRS(high_price_list, low_price_list)

    def _get_std_data(self, date_now, RSRS_raw_data):
        index = self.RSRS_raw_cal_times.index(date_now)
        signal_list = np.array(RSRS_raw_data[index-self.M+1:index+1])  # 包含date_now的数据
        signal = (signal_list[-1] - np.mean(signal_list)) / np.std(signal_list)
        return signal

    def _get_data(self):
        date_list = self.RSRS_stand_cal_times
        index_list = self.RSRS_data[self.RSRS_times.index(self.backtest_start_date):]
        RSRS_raw_data = [self._get_raw_data(date) for date in self.RSRS_raw_cal_times]
        RSRS_stand_data = [self._get_std_data(date, RSRS_raw_data) for date in self.RSRS_stand_cal_times]
        signal_list = []
        for i in range(len(date_list)):  # 根据计算的结果得出择时信号
            signal = RSRS_stand_data[i]
            if i == 0:
                if signal > self.S1:
                    signal = 1
                else:
                    signal = -1
            else:
                if signal > self.S1:
                    signal = 1
                elif signal > self.S2:
                    signal = signal_list[-1]
                else:
                    signal = -1
            signal_list.append(signal)
        return date_list, index_list, signal_list

    def _RSRS(self, high_price_list, low_price_list):
        high_price_list = np.array(high_price_list)
        low_price_list = np.array(low_price_list).reshape(-1, 1)
        reg = linear_model.LinearRegression()
        reg.fit(low_price_list, high_price_list)
        RSRS_value = reg.coef_[0]
        return RSRS_value


class RSRS_standardization_VFuture(RSRS_standardization):
    # 用于期货回测开发
    def _get_data(self):
        date_list = self.RSRS_stand_cal_times
        index_list = self.RSRS_data[self.RSRS_times.index(self.backtest_start_date):]
        RSRS_raw_data = [self._get_raw_data(date) for date in self.RSRS_raw_cal_times]
        RSRS_stand_data = [self._get_std_data(date, RSRS_raw_data) for date in self.RSRS_stand_cal_times]
        signal_list = []
        for i in range(len(date_list)):  # 根据计算的结果得出择时信号
            signal = RSRS_stand_data[i]
            if signal > self.S1:
                signal = 1
            elif signal < self.S2:
                signal = -1
            else:
                signal = 0
            signal_list.append(signal)
        return date_list, index_list, signal_list


if __name__ == '__main__':
    N = 18
    M = 600
    model = RSRS_standardization('2015-01-27', '2018-10-24', '000001.SZ', N=N, M=M)
    model.plot_return(str(N)+'_'+str(M))