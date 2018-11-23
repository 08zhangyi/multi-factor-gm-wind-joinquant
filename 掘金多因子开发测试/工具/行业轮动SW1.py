from WindPy import w
import QuantLib as ql
import numpy as np
from sklearn import linear_model
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_trading_date_from_now, SW1_INDEX


class Without_industry_wheel_movement(object):
    def __getitem__(self, date_now):
        value_result = {}
        sw1_index_code = [t[0] for t in SW1_INDEX]
        for index in sw1_index_code:
            value_result[index] = 1
        return value_result


class LLT_base(object):
    # LLT择时行业轮动基本版模型
    # 根据LLT曲线的趋势进行行业轮动择时操作
    def __init__(self, backtest_start_date, backtest_end_date, llt_cal_history=100, llt_threshold=[0.0]*len(SW1_INDEX), llt_d=[19]*len(SW1_INDEX)):
        w.start()
        llt_start_date = get_trading_date_from_now(backtest_start_date, -llt_cal_history, ql.Days)
        self.sw1_index_code = [t[0] for t in SW1_INDEX]
        data = w.wsd(self.sw1_index_code, "close", llt_start_date, backtest_end_date, "")
        self.llt_times = [t.strftime('%Y-%m-%d') for t in data.Times]
        self.llt_data = data.Data  # 记录每个指数的择时信号
        self.llt_d = llt_d
        self.llt_threshold = llt_threshold
        self.llt_cal_history = llt_cal_history  # LLT信号计算的历史长度

    def __getitem__(self, date_now):
        '''
        :param date_now: 计算date_now前一天收盘后的择时指标
        :return llt_value: 择时信号返回值，1为看多，-1为看空，0为不确定
        '''
        llt_value_result = {}
        for index_i in range(len(self.sw1_index_code)):  # 计算每个行业的择时信号，作为行业轮动依据
            index = self.sw1_index_code[index_i]
            price_list = self.llt_data[index_i]
            llt_index = self.llt_times.index(date_now)
            price_list = price_list[llt_index - self.llt_cal_history:llt_index]
            llt_d = self.llt_d[index_i]
            llt_threshold = self.llt_threshold[index_i]
            llt_value = self._LLT(price_list, llt_threshold, llt_d)
            llt_value_result[index] = llt_value
        return llt_value_result

    def _LLT(self, price_list, llt_threshold, llt_d):
        '''
        :param llt_threshold, llt_d: 计算LLT的参数
        '''
        a = 2 / (llt_d + 1)  # LLT的参数
        LLT_list = [price_list[0], price_list[1]]  # 记录LLT值列表的初始化序列
        for t in range(2, len(price_list)):
            LLT_value = (a - (a ** 2 / 4)) * price_list[t] + (a ** 2 / 2) * price_list[t - 1] - (a - (3 * a ** 2 / 4)) * \
                        price_list[t - 2] + 2 * (1 - a) * LLT_list[-1] - (1 - a) ** 2 * LLT_list[-2]
            LLT_list.append(LLT_value)
        return 1 if (((LLT_list[-1] - LLT_list[-2]) / price_list[-1]) > llt_threshold) else -1


class RSRS_standardization(object):
    def __init__(self, backtest_start_date, backtest_end_date, N_list, M_list, industry_number=3):
        # N_list，M_list，S1_list，S2_list为计算各个行业指数的用到的参数
        # industry_number为选择的行业数量
        w.start()
        RSRS_start_date = get_trading_date_from_now(backtest_start_date, -max(N_list)-max(M_list)-1, ql.Days)
        self.sw1_index_code = [t[0] for t in SW1_INDEX]
        data = w.wsd(self.sw1_index_code, "high", RSRS_start_date, backtest_end_date, "")
        self.RSRS_times = [t.strftime('%Y-%m-%d') for t in data.Times]
        self.RSRS_data_high = np.array(data.Data)  # 格式为len(SW1_index) * 时间长度
        data = w.wsd(self.sw1_index_code, "low", RSRS_start_date, backtest_end_date, "")
        self.RSRS_data_low = np.array(data.Data)  # 格式为len(SW1_index) * 时间长度
        # 时间序列的截取
        self.backtest_start_date = backtest_start_date
        self.RSRS_cal_start_date = get_trading_date_from_now(backtest_start_date, -max(M_list)-1, ql.Days)
        # 整理计算用的不同的时间序列
        self.RSRS_raw_cal_times = self.RSRS_times[self.RSRS_times.index(self.RSRS_cal_start_date):]
        self.RSRS_stand_cal_times = self.RSRS_times[self.RSRS_times.index(self.backtest_start_date)-1:]
        self.N_list = N_list  # 计算RSRS指标采样的历史周期长短
        self.M_list = M_list  # 标准化序列的历史周期长短
        self.date_list, self.signal_list = self._get_data()
        self.industry_number = industry_number

    def __getitem__(self, date_now):
        RSRS_value_result = {}
        date_previous = get_trading_date_from_now(date_now, -1, ql.Days)
        index = self.RSRS_stand_cal_times.index(date_previous)
        signal_date_now = self.signal_list[:, index]
        industry_selected_number = np.argsort(signal_date_now)[-self.industry_number:]  # ，按照RSRS标准化值从大到小排序，选取备选行业编号
        for i in range(len(SW1_INDEX)):
            index = self.sw1_index_code[i]
            if i in industry_selected_number:
                RSRS_value_result[index] = 1
            else:
                RSRS_value_result[index] = -1
        return RSRS_value_result

    def _get_raw_data(self, date_now):
        raw_data_list = []
        index = self.RSRS_times.index(date_now)
        for i in range(len(SW1_INDEX)):
            high_price_list = self.RSRS_data_high[i, index-self.N_list[i]+1:index+1]  # 包含date_now的数据
            low_price_list = self.RSRS_data_low[i, index-self.N_list[i]+1:index+1]
            raw_data_list.append(self._RSRS(high_price_list, low_price_list))
        return raw_data_list

    def _get_std_data(self, date_now, RSRS_raw_data):
        signal_result_list = []
        index = self.RSRS_raw_cal_times.index(date_now)
        for i in range(len(SW1_INDEX)):
            signal_list = np.array(RSRS_raw_data[i, index-self.M_list[i]+1:index+1])  # 包含date_now的数据
            signal = (signal_list[-1] - np.mean(signal_list)) / np.std(signal_list)
            signal_result_list.append(signal)
        return signal_result_list

    def _get_data(self):
        date_list = self.RSRS_stand_cal_times
        RSRS_raw_data = np.array([self._get_raw_data(date) for date in self.RSRS_raw_cal_times]).transpose()  # 格式为len(SW1_index) * 时间长度
        RSRS_stand_data = np.array([self._get_std_data(date, RSRS_raw_data) for date in self.RSRS_stand_cal_times]).transpose()  # 格式为len(SW1_index) * 时间长度
        return date_list, RSRS_stand_data

    def _RSRS(self, high_price_list, low_price_list):
        high_price_list = np.nan_to_num(high_price_list)  # 去除nan并替换为0.0，可以使得交易日内也可计算当日的择时信号与持仓
        low_price_list = np.nan_to_num(low_price_list.reshape(-1, 1))
        reg = linear_model.LinearRegression()
        reg.fit(low_price_list, high_price_list)
        RSRS_value = reg.coef_[0]
        return RSRS_value


if __name__ == '__main__':
    model = RSRS_standardization('2016-02-02', '2018-10-17', [40]*len(SW1_INDEX), [300]*len(SW1_INDEX))
    print(model['2018-10-17'])