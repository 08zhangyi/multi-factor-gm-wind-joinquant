from WindPy import w
import QuantLib as ql
import numpy as np
from sklearn import linear_model
from sklearn.metrics import r2_score
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_trading_date_from_now


class Without_select_time(object):
    def __getitem__(self, date_now):
        '''
        :param date_now: 计算date_now前一天收盘后的择时指标
        :return llt_value: 择时信号返回值，1为看多，-1为看空，0为不确定
        '''
        return 1


class LLT_base(object):
    # LLT择时基本版模型
    # 根据LLT曲线的趋势进行择时操作
    def __init__(self, backtest_start_date, backtest_end_date, index_code, llt_cal_history=100, llt_threshold=0.0, llt_d=39):
        w.start()
        llt_start_date = get_trading_date_from_now(backtest_start_date, -llt_cal_history, ql.Days)
        data = w.wsd(index_code, "close", llt_start_date, backtest_end_date, "")
        self.llt_times = [t.strftime('%Y-%m-%d') for t in data.Times]
        self.llt_data = data.Data[0]
        self.llt_d = llt_d
        self.llt_threshold = llt_threshold
        self.llt_cal_history = llt_cal_history  # LLT信号计算的历史长度

    def __getitem__(self, date_now):
        '''
        :param date_now: 计算date_now前一天收盘后的择时指标
        :return llt_value: 择时信号返回值，1为看多，-1为看空，0为不确定
        '''
        llt_index = self.llt_times.index(date_now)
        price_list = self.llt_data[llt_index - self.llt_cal_history:llt_index]
        llt_value = self._LLT(price_list)
        return llt_value

    def _LLT(self, price_list):
        a = 2 / (self.llt_d + 1)  # LLT的参数
        LLT_list = [price_list[0], price_list[1]]  # 记录LLT值列表的初始化序列
        for t in range(2, len(price_list)):
            LLT_value = (a - (a ** 2 / 4)) * price_list[t] + (a ** 2 / 2) * price_list[t - 1] - (a - (3 * a ** 2 / 4)) * \
                        price_list[t - 2] + 2 * (1 - a) * LLT_list[-1] - (1 - a) ** 2 * LLT_list[-2]
            LLT_list.append(LLT_value)
        return 1 if (((LLT_list[-1] - LLT_list[-2]) / price_list[-1]) > self.llt_threshold) else -1


class RSRS_base(object):
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
        self.date_list, _, self.signal_list = self._get_data()

    def __getitem__(self, date_now):
        '''
        :param date_now: 计算date_now前一天收盘后的择时指标
        :return llt_value: 择时信号返回值，1为看多，-1为看空，0为不确定
        '''
        date_previous = get_trading_date_from_now(date_now, -1, ql.Days)
        index = self.date_list.index(date_previous)
        signal = self.signal_list[index]
        return signal

    def _RSRS(self, high_price_list, low_price_list):
        high_price_list = np.nan_to_num(np.array(high_price_list))  # 去除nan并替换为0.0，可以使得交易日内也可计算当日的择时信号与持仓
        low_price_list = np.nan_to_num(np.array(low_price_list).reshape(-1, 1))
        reg = linear_model.LinearRegression()
        reg.fit(low_price_list, high_price_list)  # low为自变量，high为因变量
        RSRS_value = reg.coef_[0]
        return RSRS_value

    def _get_signal(self, date_now):
        RSRS_index = self.RSRS_times.index(date_now) + 1
        high_price_list = self.RSRS_data_high[RSRS_index - self.N:RSRS_index]
        low_price_list = self.RSRS_data_low[RSRS_index - self.N:RSRS_index]
        RSRS_value = self._RSRS(high_price_list, low_price_list)
        return RSRS_value

    def _get_data(self):
        start_date_index = self.RSRS_times.index(self.backtest_start_date) - 1
        date_list = self.RSRS_times[start_date_index:]
        index_list = self.RSRS_data[start_date_index:]
        signal_list_ori = [self._get_signal(date) for date in date_list]
        # 对signal_list进行后续处理以形成持仓信号
        signal_list = [] * len(signal_list_ori)
        for i, signal_value in enumerate(signal_list_ori):
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


class RSRS_standardization(object):
    def __init__(self, backtest_start_date, backtest_end_date, index_code, N, M, S1=0.7, S2=-0.7):
        w.start()
        RSRS_start_date = get_trading_date_from_now(backtest_start_date, -N-M, ql.Days)
        data = w.wsd(index_code, "high,low,close", RSRS_start_date, backtest_end_date, "")
        self.RSRS_times = [t.strftime('%Y-%m-%d') for t in data.Times]
        self.RSRS_data_high = data.Data[0]
        self.RSRS_data_low = data.Data[1]
        self.RSRS_data = data.Data[2]
        self.backtest_start_date = backtest_start_date
        self.RSRS_cal_start_date = get_trading_date_from_now(backtest_start_date, -M, ql.Days)
        self.N = N  # 计算RSRS指标采样的历史周期长短
        self.M = M  # 标准化序列的历史周期长短
        self.S1 = S1
        self.S2 = S2
        self.date_list, _, self.signal_list = self._get_data()

    def __getitem__(self, date_now):
        # 取date_now头一天收盘计算的择时信号
        date_previous = get_trading_date_from_now(date_now, -1, ql.Days)
        index = self.date_list.index(date_previous)
        signal = self.signal_list[index]
        return signal

    def _get_signal(self, date_now):
        RSRS_index = self.RSRS_times.index(date_now) + 1
        high_price_list = self.RSRS_data_high[RSRS_index - self.N:RSRS_index]
        low_price_list = self.RSRS_data_low[RSRS_index - self.N:RSRS_index]
        RSRS_value = self._RSRS(high_price_list, low_price_list)
        return RSRS_value

    def _get_data(self):
        start_date_index = self.RSRS_times.index(self.backtest_start_date) - 1
        date_list = self.RSRS_times[start_date_index:]
        index_list = self.RSRS_data[start_date_index:]
        # signal_list需要增加M日
        start_date_cal_index = self.RSRS_times.index(self.RSRS_cal_start_date)
        date_cal_list = self.RSRS_times[start_date_cal_index:]
        signal_cal_list = [self._get_signal(date) for date in date_cal_list]
        signal_list = []
        # 对signal_list进行后续处理以形成持仓信号
        for i in range(len(date_list)):
            signal_cal_temp = np.array(signal_cal_list[i:i+self.M])
            signal = (signal_cal_temp[-1] - np.mean(signal_cal_temp)) / np.std(signal_cal_temp)  # 计算标准化值
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
        high_price_list = np.nan_to_num(np.array(high_price_list))  # 去除nan并替换为0.0，可以使得交易日内也可计算当日的择时信号与持仓
        low_price_list = np.nan_to_num(np.array(low_price_list).reshape(-1, 1))
        reg = linear_model.LinearRegression()
        reg.fit(low_price_list, high_price_list)
        RSRS_value = reg.coef_[0]
        return RSRS_value


class RSRS_standardization_V1(object):
    # RSRS择时写法改进后的模型，此写法确实更加的科学有效
    def __init__(self, backtest_start_date, backtest_end_date, index_code, N, M, S1=0.7, S2=-0.7):
        w.start()
        RSRS_start_date = get_trading_date_from_now(backtest_start_date, -N-M-1, ql.Days)
        data = w.wsd(index_code, "high,low,close", RSRS_start_date, backtest_end_date, "")
        self.RSRS_times = [t.strftime('%Y-%m-%d') for t in data.Times]
        self.RSRS_data_high = data.Data[0]
        self.RSRS_data_low = data.Data[1]
        self.RSRS_data = data.Data[2]
        self.backtest_start_date = backtest_start_date
        self.RSRS_cal_start_date = get_trading_date_from_now(backtest_start_date, -M-1, ql.Days)
        # 整理计算用的不同的时间序列
        self.RSRS_raw_cal_times = self.RSRS_times[self.RSRS_times.index(self.RSRS_cal_start_date):]
        self.RSRS_stand_cal_times = self.RSRS_times[self.RSRS_times.index(self.backtest_start_date)-1:]
        self.N = N  # 计算RSRS指标采样的历史周期长短
        self.M = M  # 标准化序列的历史周期长短
        self.S1 = S1
        self.S2 = S2
        self.date_list, _, self.signal_list, self.RSRS_stand_data = self._get_data()

    def __getitem__(self, date_now):
        date_previous = get_trading_date_from_now(date_now, -1, ql.Days)
        index = self.RSRS_stand_cal_times.index(date_previous)
        return self.signal_list[index]

    def _get_raw_data(self, date_now):
        index = self.RSRS_times.index(date_now)
        high_price_list = self.RSRS_data_high[index - self.N + 1:index + 1]  # 包含date_now的数据
        low_price_list = self.RSRS_data_low[index - self.N + 1:index + 1]
        return self._RSRS(high_price_list, low_price_list)

    def _get_std_data(self, date_now, RSRS_raw_data):
        index = self.RSRS_raw_cal_times.index(date_now)
        signal_list = np.array(RSRS_raw_data[index - self.M + 1:index + 1])  # 包含date_now的数据
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
            # print(signal, date_list[i])
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
        return date_list, index_list, signal_list, RSRS_stand_data

    def _RSRS(self, high_price_list, low_price_list):
        high_price_list = np.nan_to_num(np.array(high_price_list))  # 去除nan并替换为0.0，可以使得交易日内也可计算当日的择时信号与持仓
        low_price_list = np.nan_to_num(np.array(low_price_list).reshape(-1, 1))
        reg = linear_model.LinearRegression()
        reg.fit(low_price_list, high_price_list)
        RSRS_value = reg.coef_[0]
        return RSRS_value


if __name__ == '__main__':
    N = 18
    M = 600
    model = RSRS_standardization_V1('2018-10-10', '2018-10-16', '801780.SI', N=N, M=M)
    print(model.RSRS_stand_data)
    print(model['2018-10-16'])