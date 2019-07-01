from WindPy import w
import QuantLib as ql
import numpy as np
import pandas as pd
import pygal
import talib
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
        print('RSRS最新择时信号为：%.4f' % RSRS_stand_data[-1])
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


class 量价共振_v1_华创(SelectTimeIndexBacktest):
    def __init__(self, backtest_start_date, backtest_end_date, index_code, L=50, N=3, Long=100, Threshold=1.02):
        self.backtest_start_date = backtest_start_date
        # 策略参数设定
        self.L = L
        self.N = N
        self.Long = Long
        self.Threshold = Threshold
        # 基本数据获取
        w.start()
        start_date = get_trading_date_from_now(backtest_start_date, -(max(L+N, Long)+100), ql.Days)
        data = w.wsd(index_code, "close,amt", start_date, backtest_end_date, "")
        self.times = [t.strftime('%Y-%m-%d') for t in data.Times]  # 日期序列
        self.close = data.Data[0]  # 价格序列
        self.amt = data.Data[1]  # 成交额序列
        self._get_signal('2015-01-27')
        super().__init__(backtest_start_date, backtest_end_date, index_code)

    def _get_signal(self, date_now):
        index = self.times.index(date_now) + 1
        diff_step = 1
        # 量能
        amt_5 = np.array(self.amt[index-5-diff_step:index])
        amt_Long = np.array(self.amt[index-self.Long-diff_step:index])
        amt_5 = talib.KAMA(amt_5, timeperiod=5)[-1]
        amt_Long = talib.KAMA(amt_Long, timeperiod=self.Long)[-1]
        amt_index = amt_5 / amt_Long
        # 价能
        close_today = np.array(self.close[index-self.L-diff_step:index])
        close_today_n = np.array(self.close[index-self.N-self.L-diff_step:index-self.N])
        _, close_today, _ = talib.BBANDS(close_today, timeperiod=self.L)
        _, close_today_n, _ = talib.BBANDS(close_today_n, timeperiod=self.L)
        close_today = close_today[-1]
        close_today_n = close_today_n[-1]
        close_index = close_today / close_today_n
        # 返回指标值
        all_index = amt_index * close_index
        return all_index

    def _get_data(self):
        start_date_index = self.times.index(self.backtest_start_date)
        date_list = self.times[start_date_index:]
        index_list = self.close[start_date_index:]
        signal_list = [self._get_signal(date) for date in date_list]
        signal_list = [1 if t > self.Threshold else -1 for t in signal_list]
        return date_list, index_list, signal_list


class 量价共振_v2_华创(SelectTimeIndexBacktest):
    def __init__(self, backtest_start_date, backtest_end_date, index_code, L=50, N=3, Long=100, Threshold1=0.98, Threshold2=1.075):
        self.backtest_start_date = backtest_start_date
        # 策略参数设定
        self.L = L
        self.N = N
        self.Long = Long
        self.Threshold1 = Threshold1
        self.Threshold2 = Threshold2
        # 基本数据获取
        w.start()
        start_date = get_trading_date_from_now(backtest_start_date, -(max(L+N, Long)+120), ql.Days)
        data = w.wsd(index_code, "close,amt", start_date, backtest_end_date, "")
        self.times = [t.strftime('%Y-%m-%d') for t in data.Times]  # 日期序列
        self.close = data.Data[0]  # 价格序列
        self.amt = data.Data[1]  # 成交额序列
        self._get_signal('2015-01-27')
        super().__init__(backtest_start_date, backtest_end_date, index_code)

    def _get_signal(self, date_now):
        index = self.times.index(date_now) + 1
        diff_step = 20
        # 量能
        amt_5 = np.array(self.amt[index-5-diff_step:index])
        amt_Long = np.array(self.amt[index-self.Long-diff_step:index])
        amt_5 = talib.KAMA(amt_5, timeperiod=5)[-1]
        amt_Long = talib.KAMA(amt_Long, timeperiod=self.Long)[-1]
        amt_index = amt_5 / amt_Long
        # 价能
        close_today = np.array(self.close[index-self.L-diff_step:index])
        close_today_n = np.array(self.close[index-self.N-self.L-diff_step:index-self.N])
        _, close_today, _ = talib.BBANDS(close_today, timeperiod=self.L)
        _, close_today_n, _ = talib.BBANDS(close_today_n, timeperiod=self.L)
        close_today = close_today[-1]
        close_today_n = close_today_n[-1]
        close_index = close_today / close_today_n
        # 返回指标值
        all_index = amt_index * close_index
        # 牛熊指标
        ma_5 = np.array(self.close[index-5-diff_step:index])
        ma_90 = np.array(self.close[index-90-diff_step:index])
        ma_5 = talib.MA(ma_5, timeperiod=5)[-1]
        ma_90 = talib.MA(ma_90, timeperiod=90)[-1]
        if ma_5 > ma_90:
            bull_bear = 1
        else:
            bull_bear = -1
        return (all_index, bull_bear)

    def _get_data(self):
        start_date_index = self.times.index(self.backtest_start_date)
        date_list = self.times[start_date_index:]
        index_list = self.close[start_date_index:]
        signal_list = [self._get_signal(date) for date in date_list]
        for i, t in enumerate(signal_list):
            if t[1] > 1:  # 牛市
                if t[0] > self.Threshold1:
                    signal_list[i] = 1
                else:
                    signal_list[i] = -1
            else:  # 熊市
                if t[0] > self.Threshold2:
                    signal_list[i] = 1
                else:
                    signal_list[i] = -1
        return date_list, index_list, signal_list


class 脉冲比_银河(SelectTimeIndexBacktest):
    def __init__(self, backtest_start_date, backtest_end_date, index_code, threshold=1.5, hold_L=30, mean_L=5):
        self.backtest_start_date = backtest_start_date
        # 策略参数设定
        self.threshold = threshold
        self.hold_L = hold_L
        self.mean_L = mean_L
        # 提取数据
        w.start()
        start_date = get_trading_date_from_now(backtest_start_date, -mean_L-3, ql.Days)
        data = w.wsd(index_code, "amt, close", start_date, backtest_end_date, "")
        self.times = [t.strftime('%Y-%m-%d') for t in data.Times]  # 日期序列
        self.amt = data.Data[0]  # 成交额数据
        self.close = data.Data[1]  # 价格序列
        super().__init__(backtest_start_date, backtest_end_date, index_code)

    def _get_signal(self, date_now):
        index = self.times.index(date_now) + 1
        amt_5 = np.mean(self.amt[index-self.mean_L-1:index-1])
        amt = self.amt[index-1]
        pulse_ratio = amt / amt_5
        return pulse_ratio

    def _get_data(self):
        start_date_index = self.times.index(self.backtest_start_date)
        date_list = self.times[start_date_index:]
        index_list = self.close[start_date_index:]
        signal_list = [self._get_signal(date) for date in date_list]
        signal_list = [1 if t > self.threshold else -1 for t in signal_list]
        # signal_list的后处理，用到self.hold_L参数
        index_1_t = []
        for index_t, i_t in enumerate(signal_list):
            if i_t == 1:
                index_1_t.append(index_t)  # 获取1的下角标
        for index_t in index_1_t:
            for j_t in range(self.hold_L):
                if (index_t + j_t) > (len(signal_list)-1):  # 超出范围
                    pass
                else:
                    signal_list[index_t + j_t] = 1
        print('脉冲比最新择时信号为：' + str(signal_list[-1]))
        return date_list, index_list, signal_list


class 单向波动差_国信(SelectTimeIndexBacktest):
    def __init__(self, backtest_start_date, backtest_end_date, index_code, threshold=0.0, RPS_history=250, max_vol_diff_history=100):
        self.backtest_start_date = backtest_start_date
        # 策略参数设定
        self.threshold = threshold
        self.RPS_history = RPS_history
        self.max_vol_diff_history = max_vol_diff_history
        # 提取数据
        w.start()
        start_date = get_trading_date_from_now(backtest_start_date, -RPS_history-max_vol_diff_history-30, ql.Days)
        data = w.wsd(index_code, "open, close, high, low", start_date, backtest_end_date, "")
        self.times = [t.strftime('%Y-%m-%d') for t in data.Times]  # 日期序列
        self.open = data.Data[0]
        self.close = data.Data[1]
        self.high = data.Data[2]
        self.low = data.Data[3]
        super().__init__(backtest_start_date, backtest_end_date, index_code)

    def _get_signal(self, date_now):
        index = self.times.index(date_now) + 1
        up_vol = (self.high[index-1] - self.open[index-1]) / self.open[index-1]
        down_vol = (self.open[index-1] - self.low[index-1]) / self.open[index-1]
        vol_diff = up_vol - down_vol  # 波动率剪刀差
        RPS = -(self.close[index-1]-np.max(self.high[index-self.RPS_history:index])) / (np.max(self.high[index-self.RPS_history:index]) - np.min(self.low[index-self.RPS_history:index]))
        return [vol_diff, RPS]

    def _get_data(self):
        start_date_index = self.times.index(self.backtest_start_date)
        # 获取未均值化的数据
        date_list = self.times[start_date_index-self.max_vol_diff_history - 20:]
        signal_list = [self._get_signal(date) for date in date_list]
        vol_diff_seq = [t[0] for t in signal_list]
        RPS_seq = [t[1] for t in signal_list]
        # 开始计算信号
        date_list = self.times[start_date_index:]
        index_list = self.close[start_date_index:]
        signal_list = []
        for i in range(start_date_index, len(self.times)):
            k = i - start_date_index + self.max_vol_diff_history + 20
            RPS = np.mean(RPS_seq[k-9:k+1])
            MEAN_DAYS = int(RPS*self.max_vol_diff_history)
            vol_diff_mean = np.mean(vol_diff_seq[k-MEAN_DAYS:k])
            signal = vol_diff_seq[k] - vol_diff_mean
            if signal > self.threshold:
                signal_list.append(1)
            else:
                signal_list.append(0)
        print('单向波动差择时信号为：%.4f' % signal)
        return date_list, index_list, signal_list


class 北上资金择时_LLT(SelectTimeIndexBacktest):
    # LLT择时基本版模型
    # 计算index_code的收盘指数的择时信号，并做回测
    def __init__(self, backtest_start_date, backtest_end_date, index_code, llt_d, llt_cal_history=100, llt_threshold=0.0):
        '''
        :param llt_d: 沪深300适合20,25
        :param llt_cal_history:
        :param llt_threshold:
        '''
        w.start()
        llt_start_date = get_trading_date_from_now(backtest_start_date, -llt_cal_history, ql.Days)
        data_std = w.wsd(index_code, "close", llt_start_date, backtest_end_date, "")  # 指数收盘价数据
        # 提取北上资金净流入数据
        sh_data_base = w.wset("shhktransactionstatistics", "startdate=" + llt_start_date + ";enddate=" + backtest_end_date + ";cycle=day;currency=cny;field=date,sh_net_purchases")
        sh_data = sh_data_base.Data[1]
        sh_data_list = np.array([np.nan if i==None else i for i in sh_data])
        sz_data = w.wset("szhktransactionstatistics", "startdate=" + llt_start_date + ";enddate=" + backtest_end_date + ";cycle=day;currency=cny;field=sz_net_purchases").Data[0]
        sz_data_list = np.array([np.nan if i==None else i for i in sz_data])
        sum_list = sh_data_list + sz_data_list  # 北上资金合计
        sum_list = sum_list[::-1]  # 数据倒序
        # 整理北上资金净流入为pandas数据
        df_sum_index = [t.strftime('%Y-%m-%d') for t in sh_data_base.Data[0]]
        df_sum_index.reverse()  # w.wset和w.wss日期序列顺序是反的 此处做倒叙处理
        df_sum = pd.DataFrame(data=sum_list, index=df_sum_index, columns=['total'])
        df_std_index = [t.strftime('%Y-%m-%d') for t in data_std.Times]
        df_std = pd.DataFrame(data=np.random.rand((len(df_std_index))), index=df_std_index, columns=['std'])
        target = pd.concat([df_std, df_sum], axis=1, ignore_index=True, sort=True) # 按照w.wss的index拼接df
        target = target.fillna(0)
        # 计算择时信号
        self.llt_times = [t.strftime('%Y-%m-%d') for t in data_std.Times]
        self.llt_data = list(target[1].values)
        self.close_data = data_std.Data[0]
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
        index_list = self.close_data[start_date_index:]
        signal_list = [self._get_signal(date) for date in date_list]
        print('北上资金LLT择时信号为：%i' % (signal_list[-1]))
        return date_list, index_list, signal_list

    def _LLT(self, price_list):
        a = 2 / (self.llt_d + 1)  # LLT的参数
        LLT_list = [price_list[0], price_list[1]]  # 记录LLT值列表的初始化序列
        for t in range(2, len(price_list)):
            LLT_value = (a - (a ** 2 / 4)) * price_list[t] + (a ** 2 / 2) * price_list[t - 1] - (a - (3 * a ** 2 / 4)) * \
                        price_list[t - 2] + 2 * (1 - a) * LLT_list[-1] - (1 - a) ** 2 * LLT_list[-2]
            LLT_list.append(LLT_value)
        return 1 if (((LLT_list[-1] - LLT_list[-2]) / price_list[-1]) > self.llt_threshold) else -1


def 使用模板1():
    N = 18
    M = 600
    model = RSRS_standardization('2015-01-27', '2018-10-24', '000300.SH', N=N, M=M)
    model.plot_return(str(N) + '_' + str(M))


def 使用模板2():
    # model = 量价共振_v1_华创('2015-01-27', '2019-04-11', '000300.SH')
    # model.plot_return('1')
    model = 量价共振_v2_华创('2013-05-13', '2019-04-11', '000300.SH')
    model.plot_return('2')


def 使用模板3():
    model = 脉冲比_银河('2013-05-13', '2019-04-11', '000001.SH')
    model.plot_return('2')


def 使用模板4():
    model = 单向波动差_国信('2013-05-13', '2019-04-11', '000300.SH')
    model.plot_return('2')


def 使用模板5():
    backtest_start_date = '2018-01-04'
    # backtest_start_date = '2018-07-03'
    backtest_end_date = '2019-06-21'
    index_code = '000300.SH'
    llt_d = 30
    model = 北上资金择时_LLT(backtest_start_date, backtest_end_date, index_code, llt_d, llt_cal_history=30, llt_threshold=0.0)
    model.plot_return(str(llt_d))


def 发布报告的模板1():
    end_date = '2019-06-28'
    start_date = get_trading_date_from_now(end_date, -100, ql.Days)
    # RSRS模型
    N = 18
    M = 600
    model = RSRS_standardization(start_date, end_date, '000300.SH', N=N, M=M)
    # 脉冲比模型
    model = 脉冲比_银河(start_date, end_date, '000001.SH')
    # 单向波动差模型
    model = 单向波动差_国信(start_date, end_date, '000300.SH')
    # 北上资金LLT择时
    model = 北上资金择时_LLT(start_date, end_date, '000300.SH', llt_d=20, llt_cal_history=30, llt_threshold=0.0)


if __name__ == '__main__':
    发布报告的模板1()
    # 使用模板5()