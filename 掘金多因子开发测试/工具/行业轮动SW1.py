from WindPy import w
import QuantLib as ql
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_trading_date_from_now, SW1_INDEX


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