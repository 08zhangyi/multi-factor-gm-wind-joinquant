# 单因子提取器，不包含作图
from WindPy import w
import numpy as np
import pandas as pd
import datetime
import QuantLib as ql
import abc
from sklearn.linear_model import LinearRegression

import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_trading_date_from_now, SW1_INDEX, ZX1_INDEX


# 基类，需继承
# 三级继承结构
# 第一级：SingleFactorReasearch，基本功能，抽象类
# 第二级：带有多参数的因子类，抽象类
# 第三级：统一为date和code_list接口的因子类，实际使用的类（部分类无二级继承结构，三级直接从一级继承），三级对二级的参数进行固化
# 抽象类的标志为__init__带有abc.abstractmethod修饰
class SingleFactorReasearch():
    @abc.abstractmethod
    def __init__(self, date, code_list, factor_name):
        # date为查询因子的日期，'yyyy-mm-dd'格式，date日收盘后查询
        # code_list为查询因子的股票代码列表
        self.date = date.split('-')  # 以list形式存储日期
        self.code_list = code_list
        self.factor_name = factor_name
        self.w = w
        self.w.start()
        self._single_factor_df = self._calculate_factor()
        # print(self._single_factor_df)

    # 具体实现因子计算的部分，返回为DataFrame对象
    def _calculate_factor(self):
        return None

    def get_factor(self):
        return self._single_factor_df


# 净利润增长率
class NetProfitGrowRate(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '净利润增长率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        profit_ttm_now = np.array(w.wss(self.code_list, "fa_profit_ttm", "unit=1;tradeDate=" + ''.join(date_list)).Data[0])
        date_list[0] = str(int(date_list[0])-1)
        profit_ttm_prev = np.array(w.wss(self.code_list, "fa_profit_ttm", "unit=1;tradeDate=" + ''.join(date_list)).Data[0])

        profit_ttm_prev[profit_ttm_prev <= 0.0] = np.nan  # 基期亏损的不考虑此因子，此因子值缺失
        net_profit_grow_rate = (profit_ttm_now - profit_ttm_prev) / profit_ttm_prev
        net_profit_grow_rate = pd.DataFrame(data=net_profit_grow_rate, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# 净利润增长率
class NetProfitGrowRateV2(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '净利润增长率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        npgr = np.array(w.wss(self.code_list,  "fa_npgr_ttm", "tradeDate="+"".join(date_list)).Data[0])
        NPGR = pd.DataFrame(data=npgr, index=self.code_list, columns=[self.factor_name])
        return NPGR


# 营业收入增长率
class RevenueGrowthRate(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '营业收入增长率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list, "fa_orgr_ttm", "tradeDate="+''.join(date_list)).Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 净利润值对N个月时间回归，返回二次项系数，需继承
class ProfitAcc(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N):
        # N为期数，一个季度为一期
        factor_name = str(N) + '个月利润成长加速度'
        self.N = N
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        X_0 = np.arange(1, (self.N+1), 1).reshape((self.N, 1))
        X_1 = X_0 * X_0
        X = np.concatenate((X_1, X_0), axis=1)
        profit_data = []
        alpha = []
        for i in np.arange(0, self.N*3, 3):  # 按日期遍历提取利润数据
            temp_day = get_trading_date_from_now("-".join(self.date), -int(i), ql.Months)
            profit = w.wss(self.code_list, "profit_ttm", "unit=1;tradeDate=" + str(temp_day)).Data[0]
            profit_data.append(profit)
        profit_data = np.array(profit_data).transpose()
        for y in profit_data:  # 回归计算因子值
            try:
                model = LinearRegression().fit(X, y)
                a = model.coef_[0]
                alpha.append(a)
            except ValueError:
                alpha.append(np.nan)
        alpha = np.array(alpha)
        df = pd.DataFrame(data=alpha, index=self.code_list, columns=[self.factor_name]).dropna()
        return df


# 净利润值对8个月时间回归，返回二次项系数
class ProfitAcc_8(ProfitAcc):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 8)


# 连续N个月的净利润同比增速的均值除以其标准差，需继承
class SteadyProfitGrowth(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N=8):
        # N为期数，一个季度为一期
        factor_name = str(N) + '个月利润稳健增速'
        self.N = N
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        profit_data = []
        data = []
        for i in np.arange(0, self.N*3, 3):  # 按日期遍历提取利润数据
            temp_day = get_trading_date_from_now("-".join(self.date), -int(i), ql.Months)
            profit = w.wss(self.code_list, "profit_ttm", "unit=1;tradeDate=" + str(temp_day)).Data[0]
            profit_data.append(profit)
        profit_data = np.array(profit_data).transpose()
        for j in profit_data:
            mean = np.mean(np.array(j))
            std = np.std(np.array(j))
            data_temp = mean/std
            data.append(data_temp)
        data = np.array(data)
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 连续8期的净利润同比增速的均值除以其标准差
class SteadyProfitGrowth_8(SteadyProfitGrowth):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 8)


# N个月利润稳健加速度，需继承
class SteadyProfitAcc(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N=8):
        factor_name = str(N) + '个月利润稳健加速度'
        # N为期数，一个季度为一期
        self.N = N
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_previous = get_trading_date_from_now("-".join(self.date), -3, ql.Months)  # 相对于一个季度前计算加速度
        current_data = SteadyProfitGrowth("-".join(self.date), self.code_list).get_factor()
        previous_data = SteadyProfitGrowth(date_previous, self.code_list).get_factor()
        data = current_data - previous_data
        data.rename(columns={"利润稳健增速": "利润稳健加速度"}, inplace=True)
        return data


# 连续8个月的净利润同比增速的均值除以其标准差
class SteadyProfitAcc_8(SteadyProfitAcc):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 8)


# 一致预测净利润增长率（6个月数据计算）
class EstimateNetProfitGrowRateFY1_6M(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '一致预测净利润增长率（6个月数据计算）'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        west_netprofit_fy1_6m = np.array(w.wss(self.code_list,  "west_netprofit_fy1_6m", "tradeDate="+"".join(date_list)).Data[0])
        west_netprofit_fy1_6m = pd.DataFrame(data=west_netprofit_fy1_6m, index=self.code_list, columns=[self.factor_name])
        return west_netprofit_fy1_6m


# 存货周转率
class InventoryTurnRatio(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '存货周转率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        invturn = np.array(w.wss(self.code_list,  "fa_invturn_ttm", "tradeDate="+"".join(date_list)).Data[0])
        InvTurn = pd.DataFrame(data=invturn, index=self.code_list, columns=[self.factor_name])
        return InvTurn


# N日移动均线，需继承
class MA_N(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N):
        self.N = N  # N日均线的长度
        factor_name = str(N) + '日移动均线'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        MA_data = np.array(w.wss(self.code_list,  "MA", "tradeDate="+"".join(date_list)+";MA_N="+str(self.N)+";priceAdj=T;cycle=D").Data[0])
        MA_N = pd.DataFrame(data=MA_data, index=self.code_list, columns=[self.factor_name])
        return MA_N


# 5日移动平均线
class MA_5(MA_N):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 5)


# 10日移动平均线
class MA_10(MA_N):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 10)


# 20日移动平均线
class MA_20(MA_N):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 20)


# 60日移动平均线
class MA_60(MA_N):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 60)


# 120日移动平均线
class MA_120(MA_N):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 120)


# N日移动均线相对价格比例
class MA_N_rel(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N):
        self.N = N  # N日均线的长度
        factor_name = str(N) + '日移动均线相对价格比例'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        MA_data = np.array(w.wss(self.code_list,  "MA", "tradeDate="+"".join(date_list)+";MA_N="+str(self.N)+";priceAdj=T;cycle=D").Data[0])
        close_data = np.array(w.wss(self.code_list,  "close", "tradeDate="+"".join(date_list)+";priceAdj=T;cycle=D").Data[0])
        MA_data = MA_data / close_data
        MA_N_rel = pd.DataFrame(data=MA_data, index=self.code_list, columns=[self.factor_name])
        return MA_N_rel


# 5日移动均线相对价格比例
class MA_5_rel(MA_N_rel):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 5)


# N日平均换手率，需继承
class VOLN(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N):
        factor_name = str(N) + '日平均换手率'
        self.N = N
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        startDate = str(w.tdaysoffset(-self.N, "".join(date_list), "").Data[0][0])  # 区间数据
        vol_data = np.array(w.wss(self.code_list, "avg_turn_per", "startDate=" + "".join(startDate) + ";endDate=" + "".join(date_list)).Data[0])
        vol_data = vol_data / 100.0
        VOL5 = pd.DataFrame(data=vol_data, index=self.code_list, columns=[self.factor_name])
        return VOL5


# 5日平均换手率
class VOL5(VOLN):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 5)


# 10日平均换手率
class VOL10(VOLN):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 10)


# 20日平均换手率
class VOL20(VOLN):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 20)


# 60日平均换手率
class VOL60(VOLN):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 60)


# 120日平均换手率
class VOL120(VOLN):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 120)


# 240日平均换手率
class VOL240(VOLN):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 240)


# Aroon指标
class AROON(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = 'Aroon指标'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        Aroon_data = np.array(w.wss(self.code_list, "tech_aroon", "tradeDate=" + "".join(date_list)).Data[0])
        Aroon = pd.DataFrame(data=Aroon_data, index=self.code_list, columns=[self.factor_name])
        return Aroon


# MTM动量指标，需继承
class MTM_interDay_N(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, MTM_interDay=6, MTM_N=6):
        factor_name = 'MTM指标'
        # MTM_interDay为间隔周期数，MTM_N为均值计算周期数，6为Wind默认参数
        self.MTM_interDay = MTM_interDay
        self.MTM_N = MTM_N
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        MTM_data = np.array(w.wss(self.code_list, "MTM", "tradeDate=" + "".join(date_list) + ";MTM_interDay="+str(self.MTM_interDay)+";MTM_N="+str(self.MTM_N)+";MTM_IO=1;priceAdj=T;cycle=D").Data[0])
        MTM = pd.DataFrame(data=MTM_data, index=self.code_list, columns=[self.factor_name])
        return MTM


# MTM动量指标，默认版
class MTM(MTM_interDay_N):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 6, 6)


# RSI指标，需继承
class RSI_N(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N=6):
        factor_name = '相对强度指标RSI'
        self.N = N
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        rsi_index = w.wss(self.code_list, "RSI", "industryType=1;tradeDate="+''.join(date_list)+";RSI_N="+str(self.N)+";priceAdj=T;cycle=D").Data[0]
        net_profit_grow_rate = pd.DataFrame(data=rsi_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# RSI指标，默认版
class RSI(RSI_N):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 6)


# BETA值，相对某一指数，需继承
class BETA(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, refer_index='000300.SH', length=22):
        factor_name = 'BETA_of_' + refer_index
        self.refer_index = refer_index  # 计算Beta值时用的参考指数
        self.length = length  # 计算Beta的历史数据长度
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        startDate = str(w.tdaysoffset(-self.length, "".join(date_list), "").Data[0][0])  # 每个月22个交易日
        beta_data = np.array(w.wss(self.code_list, "beta", "startDate="+startDate+";endDate="+"".join(date_list)+";period=2;returnType=1;index="+self.refer_index).Data[0])
        BETA = pd.DataFrame(data=beta_data, index=self.code_list, columns=[self.factor_name])
        return BETA


# BETA值，相对沪深300指数
class BETA_REF_HS300(BETA):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, refer_index='000300.SH', length=22)


# BETA值，相对上证50指数
class BETA_REF_SZ50(BETA):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, refer_index='000016.SH', length=50)


# 残差收益波动率，万德因子名称：252日残差收益波动率
# 算法：Ri=a+b*Rb+e,Rb为参考指数沪深300，a为截距项，b即为beta，e为残差项，252日残差收益波动率为252日e的标准差
class HSIGMA_252(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '252日残差收益波动率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        hsigma_252_value = np.array(w.wss(self.code_list, "risk_residvol252", "tradeDate=" + "".join(date_list)).Data[0])*100.0
        HSIGMA_252 = pd.DataFrame(data=hsigma_252_value, index=self.code_list, columns=[self.factor_name])
        return HSIGMA_252


# SKEWNESS，过去20日股价的偏度
class SKEWNESS_20(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '20日股价偏度'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        skewness_data = np.array(w.wss(self.code_list, "tech_skewness", "tradeDate=" + "".join(date_list)).Data[0])
        SKWNESS_20 = pd.DataFrame(data=skewness_data, index=self.code_list, columns=[self.factor_name])
        return SKWNESS_20


# TURN_VOLATILITY，过去20日换手率相对波动率
class TURN_VOLATILITY_20(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '20日换手率相对波动率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        volatility_data = np.array(w.wss(self.code_list, "tech_turnoverratevolatility20", "tradeDate=" + "".join(date_list)).Data[0])
        TURN_VOLATILITY_20 = pd.DataFrame(data=volatility_data, index=self.code_list, columns=[self.factor_name])
        return TURN_VOLATILITY_20


# RelativePriceN，当前价格处于过去N个交易日股价的位置 算法：(close - low)/(high - low)，需继承
class RelativePriceN(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N):
        factor_name = '过去%d天股票相对位置' % N
        self.N = N  # 计算窗口期
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        startDate = str(w.tdaysoffset(--self.N, "".join(date_list), "").Data[0][0])
        high_price = np.array(w.wss(self.code_list, "high_per", "startDate="+"".join(startDate)+";endDate="+"".join(date_list)+";priceAdj=T").Data[0])
        low_price = np.array(w.wss(self.code_list, "low_per", "startDate="+"".join(startDate)+";endDate="+"".join(date_list)+";priceAdj=T").Data[0])
        close_price = np.array(w.wss(self.code_list, "close_per", "startDate="+"".join(startDate)+";endDate="+"".join(date_list)+";priceAdj=T").Data[0])
        relative_position = (close_price - low_price)/(high_price - low_price)
        RelativePriceN = pd.DataFrame(data=relative_position, index=self.code_list, columns=[self.factor_name])
        return RelativePriceN


# 当前价格处于过去240个交易日股价的位置
class RelativePrice240(RelativePriceN):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 240)


# N日平均换手率，需继承
class VOL_N(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N):
        self.N = N
        factor_name = str(N) + '日平均换手率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        startDate = str(w.tdaysoffset(-self.N, "".join(date_list), "").Data[0][0])  # 区间数据
        vol_data = np.array(w.wss(self.code_list, "avg_turn_per", "startDate=" + "".join(startDate) + ";endDate=" + "".join(date_list)).Data[0])
        vol_data = vol_data / 100.0
        VOL240 = pd.DataFrame(data=vol_data, index=self.code_list, columns=[self.factor_name])
        return VOL240


# 240日平均换手率
class VOL_240(VOL_N):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 240)


# 总市值
class MarketCap(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '总市值'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list, "ev", "unit=1;tradeDate=" + ''.join(date_list)).Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 对数市值  # 算法：np.log(个股当日股价*当日总股本)
class LCap(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '对数市值'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        log_Cap = np.log(w.wss(self.code_list, "val_lnmv", "tradeDate=" + "".join(date_list)).Data[0])
        LCap = pd.DataFrame(data=log_Cap, index=self.code_list, columns=[self.factor_name])
        return LCap


# 对数流通市值
class LFloatCap(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '对数流通市值'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        log_Circulation_Cap = np.log(w.wss(self.code_list, "val_lnfloatmv", "tradeDate=" + "".join(date_list)).Data[0])
        LFloatCap = pd.DataFrame(data=log_Circulation_Cap, index=self.code_list, columns=[self.factor_name])
        return LFloatCap


# 成交量比率  # VolumeRatio = N日内上升日成交额总和/N日内下降日成交额总和, 万得默认N=26
class VR(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '成交量比率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        vr_data = np.array(w.wss(self.code_list, "tech_vr", "tradeDate=" + "".join(date_list)).Data[0])
        VR = pd.DataFrame(data=vr_data, index=self.code_list, columns=[self.factor_name])
        return VR


# 20日资金流量  # 用20日的收盘价、最高价及最低价的均值乘以20日成交量即可得到该交易日的资金流量
class MoneyFlow20(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '20日资金流量'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        startDate = str(w.tdaysoffset(-20, "".join(date_list), "").Data[0][0])  # 区间数据
        price_data = np.array(w.wss(self.code_list, "high_per,low_per,close_per", "startDate=" + "".join(startDate) + ";endDate=" + "".join(date_list) + ";priceAdj=T").Data)
        avg_price = np.sum(price_data, axis=0) / 3.0
        volume = np.array(w.wss(self.code_list, "vol_per", "unit=1;startDate=" + "".join(startDate) + ";endDate=" + "".join(date_list)).Data[0])
        result = avg_price * volume
        MoneyFlow20 = pd.DataFrame(data=result, index=self.code_list, columns=[self.factor_name])
        return MoneyFlow20


# N日资金流量  # 用N日的收盘价、最高价及最低价的均值乘以20日成交量即可得到该交易日的资金流量，需继承
class MoneyFlow_N(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N):
        self.N = N
        factor_name = str(N) + '日资金流量'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        startDate = str(w.tdaysoffset(-self.N, "".join(date_list), "").Data[0][0])  # 区间数据
        price_data = np.array(w.wss(self.code_list, "high_per,low_per,close_per", "startDate=" + "".join(startDate) + ";endDate=" + "".join(date_list) + ";priceAdj=T").Data)
        avg_price = np.sum(price_data, axis=0) / 3.0
        volume = np.array(w.wss(self.code_list, "vol_per", "unit=1;startDate=" + "".join(startDate) + ";endDate=" + "".join(date_list)).Data[0])
        result = avg_price * volume
        MoneyFlow20 = pd.DataFrame(data=result, index=self.code_list, columns=[self.factor_name])
        return MoneyFlow20


# 5日资金流量  # 用5日的收盘价、最高价及最低价的均值乘以20日成交量即可得到该交易日的资金流量
class MoneyFlow_5(MoneyFlow_N):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 5)


# ROE指标
class ROE(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '权益回报率ROE'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        roe_ttm = np.array(w.wss(self.code_list, "fa_roe_ttm", "tradeDate=" + ''.join(date_list)).Data[0])
        net_profit_grow_rate = pd.DataFrame(data=roe_ttm, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# 基本每股收益EPS
class BasicEPS(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '基本每股收益EPS'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        eps_index = np.array(w.wss(self.code_list, "fa_eps_basic", "tradeDate=" + ''.join(date_list)).Data[0])
        net_profit_grow_rate = pd.DataFrame(data=eps_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# 稀释每股收益EPS
class DilutedEPS(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '稀释每股收益'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        eps_data = np.array(w.wss(self.code_list, "fa_eps_diluted", "tradeDate=" + "".join(date_list)).Data[0])
        DilutedEPS = pd.DataFrame(data=eps_data, index=self.code_list, columns=[self.factor_name])
        return DilutedEPS


# 市销率PS指标
class PS(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '市销率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        ps_ttm = np.array(w.wss(self.code_list, "ps_ttm", "tradeDate=" + ''.join(date_list)).Data[0])
        df = pd.DataFrame(data=ps_ttm, index=self.code_list, columns=[self.factor_name])
        return df


# 每股净资产
class NetAssetPerShare(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '每股净资产'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list, "fa_bps", "tradeDate="+"".join(date_list)).Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# ROA
class ROA(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '资产回报率ROA'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        roa_data = np.array(w.wss(self.code_list, "fa_roa_ttm", "tradeDate=" + "".join(date_list)).Data[0])/100.0
        ROA = pd.DataFrame(data=roa_data, index=self.code_list, columns=[self.factor_name])
        return ROA


# EquityToAsset
class EquityToAsset(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = 'EquityToAsset'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        total_equity = np.array(w.wss(self.code_list, "fa_equity", "tradeDate"+"".join(self.date)).Data[0])
        total_asset = np.array(w.wss(self.code_list, "fa_totassets", "tradeDate"+"".join(self.date)).Data[0])
        data = total_equity/total_asset
        EquityToAsset = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return EquityToAsset


# 固定资产比率
class FixAssetRatio(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '固定资产比率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        fixed_asset = np.array(w.wss(self.code_list, "fa_fixassets", "tradeDate="+"".join(date_list)).Data[0])
        total_asset = np.array(w.wss(self.code_list, "fa_totassets", "tradeDate="+"".join(date_list)).Data[0])
        data = fixed_asset/total_asset
        FixAssetRatio = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return FixAssetRatio


# 账面杠杆
class BLEV(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '账面杠杆'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        blev_data = np.array(w.wss(self.code_list, "fa_blev", "tradeDate=" + "".join(date_list)).Data[0])
        BLEV = pd.DataFrame(data=blev_data, index=self.code_list, columns=[self.factor_name])
        return BLEV


# ORPS指标
class ORPS(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '每股营业收入ORPS'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        orps_index = np.array(w.wss(self.code_list, "orps_ttm", "tradeDate=" + ''.join(date_list)).Data[0])
        net_profit_grow_rate = pd.DataFrame(data=orps_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# 营业收入增长率
class OperationRevenueGrowth(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '营业收入增长率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        fa_orgr_ttm = np.array(w.wss(self.code_list, "fa_orgr_ttm", "tradeDate=" + ''.join(date_list)).Data[0])
        fa_orgr_ttm = pd.DataFrame(data=fa_orgr_ttm, index=self.code_list, columns=[self.factor_name])
        return fa_orgr_ttm


# 一致预测营业收入增长率（6个月数据计算）
class EstimateNetRevenueGrowRateFY1_6M(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '一致预测营业收入增长率（6个月数据计算）'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        west_netprofit_fy1_6m = np.array(w.wss(self.code_list,  "west_sales_fy1_6m", "tradeDate="+"".join(date_list)).Data[0])
        west_netprofit_fy1_6m = pd.DataFrame(data=west_netprofit_fy1_6m, index=self.code_list, columns=[self.factor_name])
        return west_netprofit_fy1_6m


# 销售毛利率
class GrossIncomeRatio(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '销售毛利率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        grossprofit_data = np.array(w.wss(self.code_list, "fa_grossprofitmargin_ttm", "tradeDate=" + "".join(date_list)).Data[0])/100.0
        GrossIncomeRatio = pd.DataFrame(data=grossprofit_data, index=self.code_list, columns=[self.factor_name])
        return GrossIncomeRatio


# 资产负债率
class DebetToAsset(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '资产负债率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        debet_to_asset = np.array(w.wss(self.code_list, "fa_debttoasset", "tradeDate=" + "".join(date_list)).Data[0])/100.0
        DebetToAsset = pd.DataFrame(data=debet_to_asset, index=self.code_list, columns=[self.factor_name])
        return DebetToAsset


# 流动比例
class CurrentRatio(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '流动比率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        fa_current = np.array(w.wss(self.code_list, "fa_current", "tradeDate=" + "".join(date_list)).Data[0])/100.0
        fa_current = pd.DataFrame(data=fa_current, index=self.code_list, columns=[self.factor_name])
        return fa_current


# 经营活动现金流与企业价值比
class CFO2EV(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '经营现金流比企业价值'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        OpCash = np.array(w.wss(self.code_list, "fa_operactcashflow_ttm", "tradeDate="+"".join(date_list)).Data[0])
        Rev_Ev = np.array(w.wss(self.code_list, "val_ortoev_ttm", "tradeDate="+"".join(date_list)).Data[0])
        Rev = np.array(w.wss(self.code_list, "fa_or_ttm", "tradeDate="+"".join(date_list)).Data[0])
        CFO2EV_data = OpCash/(Rev/Rev_Ev)
        GrossIncomeRatio = pd.DataFrame(data=CFO2EV_data, index=self.code_list, columns=[self.factor_name])
        return GrossIncomeRatio


# 未来预期盈利增长
# 建议不使用此因子 数据不全+没有参考价值
class ForecastEarningGrowth_FY1_3M(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '三个月盈利变化率（一年）预测'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        Forecast_data = np.array(w.wss(self.code_list, "west_netprofit_fy1_3m", "tradeDate=" + "".join(date_list)).Data[0])
        ForecastEarningGrowth = pd.DataFrame(data=Forecast_data, index=self.code_list, columns=[self.factor_name])
        return ForecastEarningGrowth


# CFPS指标，每股现金流量
class CFPS(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '每股现金流CFPS'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        cfps_index = np.array(w.wss(self.code_list, "fa_cfps_ttm", "tradeDate=" + ''.join(date_list)).Data[0])
        net_profit_grow_rate = pd.DataFrame(data=cfps_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# OCFPS指标，经营活动每股现金流量
class OCFPS(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '经营活动每股现金流OCFPS'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        ocfps_index = np.array(w.wss(self.code_list, "fa_ocfps_ttm", "tradeDate=" + ''.join(date_list)).Data[0])
        net_profit_grow_rate = pd.DataFrame(data=ocfps_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# 市值/企业自由现金流
class MarketValueToFreeCashFlow(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '市值比企业自由现金流'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        val_mvtofcff = np.array(w.wss(self.code_list, "val_mvtofcff", "tradeDate=" + ''.join(date_list)).Data[0])
        MarketValueToFreeCashFlow = pd.DataFrame(data=val_mvtofcff, index=self.code_list, columns=[self.factor_name])
        return MarketValueToFreeCashFlow


# LogEV(含货币资金)指标
class LogEVWithCash(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '对数企业价值（含货币资金）LogEV'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        ev1_index = np.array(w.wss(self.code_list, "ev1", "tradeDate=" + ''.join(date_list)).Data[0])
        ev1_index = np.log(ev1_index)
        net_profit_grow_rate = pd.DataFrame(data=ev1_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# PE指标
class PE(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '市盈率PE'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        pe_index = np.array(w.wss(self.code_list, "pe_ttm", "tradeDate=" + ''.join(date_list)).Data[0])
        net_profit_grow_rate = pd.DataFrame(data=pe_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# 预测PE（FY1）
class EstimatePEFY1(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '预测PE（FY1）'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        estpe_FY1 = np.array(w.wss(self.code_list, "estpe_FY1", "tradeDate=" + ''.join(date_list)).Data[0])
        estpe_FY1 = pd.DataFrame(data=estpe_FY1, index=self.code_list, columns=[self.factor_name])
        return estpe_FY1


# 过去N年最大PE值
class PE_MAX_N(SingleFactorReasearch):
    def __init__(self, date, code_list, N):
        self.N = N
        factor_name = '过去' + str(N) + '年最大PE值'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        startDate = get_trading_date_from_now("-".join(date_list), -self.N, ql.Years)  # 年可以改成日月
        pe_data = []
        for i in self.code_list:
            data = np.max(w.wsd(i, "pe_ttm", str(startDate), ''.join(date_list), "").Data[0])
            pe_data.append(data)
        df = pd.DataFrame(data=pe_data, index=self.code_list, columns=[self.factor_name])
        return df


# 过去5年最大PE值
class PE_MAX_5(PE_MAX_N):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, 5)


# PB指标
class PB(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = 'PB市净率指标'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        pb_index = np.array(w.wss(self.code_list, "pb_lf", "tradeDate=" + ''.join(date_list)).Data[0])
        net_profit_grow_rate = pd.DataFrame(data=pb_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# 股息率指标
class DividendYield(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '股息率指标'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        dividendyield_index = np.array(w.wss(self.code_list, "dividendyield2", "tradeDate=" + ''.join(date_list)).Data[0])
        net_profit_grow_rate = pd.DataFrame(data=dividendyield_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# 每股企业自由现金流指标
class FreeCashFlowPerShare(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '每股企业自由现金流指标'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        fa_fcffps_index = np.array(w.wss(self.code_list, "fa_fcffps", "tradeDate=" + ''.join(date_list)).Data[0])
        net_profit_grow_rate = pd.DataFrame(data=fa_fcffps_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


# 股价/每股企业自由现金流
class PriceFreeCashFlowPerShare(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '股价_每股企业自由现金流'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        fa_fcffps_index = np.array(w.wss(self.code_list, "fa_fcffps", "tradeDate=" + ''.join(date_list)).Data[0])
        price = np.array(w.wss(self.code_list, "close", "tradeDate=" + ''.join(date_list) + ';priceAdj=U;cycle=D').Data[0])
        price_fa_fcffps = pd.DataFrame(data=fa_fcffps_index/price, index=self.code_list, columns=[self.factor_name])
        return price_fa_fcffps


# 带息债务/全部投入资本
class InterestBearingDebtInvestmentCapital(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '带息债务_全部投入资本指标'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        fa_interestdebttocapital_index = np.array(w.wss(self.code_list, "fa_interestdebttocapital", "tradeDate=" + ''.join(date_list)).Data[0])
        fa_interestdebttocapital_index = pd.DataFrame(data=fa_interestdebttocapital_index, index=self.code_list, columns=[self.factor_name])
        return fa_interestdebttocapital_index


# 长期负债/营运资金
class LongTermLiabilityToWorkCapital(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '长期负债/营运资金'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        fa_uncurdebttoworkcap = np.array(w.wss(self.code_list, "fa_uncurdebttoworkcap", "tradeDate=" + ''.join(date_list)).Data[0])
        fa_uncurdebttoworkcap = pd.DataFrame(data=fa_uncurdebttoworkcap, index=self.code_list, columns=[self.factor_name])
        return fa_uncurdebttoworkcap


# 净利润ttm 前推12个月的数据
class NetProfit(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '净利润'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        profit_data = np.array(w.wss(self.code_list, "profit_ttm", "unit=1;tradeDate=" + "".join(date_list)).Data[0])
        netprofit = pd.DataFrame(data=profit_data, index=self.code_list, columns=[self.factor_name])
        return netprofit


# 营业收入ttm 前推12个月的数据
class Revenue(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '营业收入'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        revenue_data = np.array(w.wss(self.code_list, "or_ttm", "unit=1;tradeDate=" + "".join(date_list)).Data[0])
        revenue = pd.DataFrame(data=revenue_data, index=self.code_list, columns=[self.factor_name])
        return revenue


# 实际税率（所得税费用/营业收入)
class EffectiveTaxRate(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '实际税率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        tax_exp = np.array(w.wss(self.code_list, "fa_tax_ttm", "tradeDate="+"".join(date_list)).Data[0])
        EBIT = np.array(w.wss(self.code_list, "fa_ebit_ttm", "tradeDate="+"".join(date_list)).Data[0])
        tax_rate = tax_exp/EBIT
        df = pd.DataFrame(data=tax_rate, index=self.code_list, columns=[self.factor_name])
        return df


# 资本回报率ROC指标
class ROC(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '资本回报率ROC'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        roc_ttm = np.array(w.wss(self.code_list, "fa_roc_ttm", "tradeDate=" + ''.join(date_list)).Data[0])
        df = pd.DataFrame(data=roc_ttm, index=self.code_list, columns=[self.factor_name])
        return df


# 股权质押比例（三年统计）
class StockPledgeRatio(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '股权质押比例（三年统计）'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list_end = self.date
        date_list_start = date_list_end.copy()
        date_list_start[0] = str(int(date_list_start[0])-3)
        date_list_end = '-'.join(date_list_end)
        date_list_start = '-'.join(date_list_start)
        data_temp = w.wset("sharepledge", "startdate="+date_list_start+";enddate="+date_list_end+";sectorid=a001010100000000;field=wind_code,pledged_shares,pledge_end_date,pledge_termination_date").Data
        # 将None数据用一个遥远的时间代替
        data_temp[2] = self._replace_list(data_temp[2])
        data_temp[3] = self._replace_list(data_temp[3])

        df = pd.DataFrame(data=np.array([data_temp[1], data_temp[2], data_temp[3]]).transpose(), index=data_temp[0])
        df[0] = df[0] * 10000.0  # 把质押的份数换为股数
        # 取出所有未到期的股权质押信息
        df = df[(df[1]>datetime.datetime.strptime(date_list_end, '%Y-%m-%d')) & (df[2]>datetime.datetime.strptime(date_list_end, '%Y-%m-%d'))]
        ds = df[0]  # 全A个股处于股权质押状态的股票数量
        ds = ds.sum(level=0)
        all_shares = w.wss(self.code_list, "total_shares", "unit=1;tradeDate=" + ''.join(self.date)).Data[0]  # 获取总股本列表
        for i in range(len(self.code_list)):  # 计算个股的抵押比例
            code_temp = self.code_list[i]
            try:
                pledge_shares = ds[code_temp]
            except:
                pledge_shares = 0
            all_shares[i] = pledge_shares / all_shares[i]
        df_ratio = pd.DataFrame(data=all_shares, index=self.code_list, columns=[self.factor_name])  # 对应个股的总股本
        return df_ratio

    def _replace_list(self, list):
        for i in range(len(list)):
            if list[i] == None:
               list[i] = datetime.datetime.strptime('2200-12-31', '%Y-%m-%d')
        return list


# 收盘价 （不复权）
class ClosePrice(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '收盘价'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        close_prc = np.array(w.wss(self.code_list, "close", "tradeDate="+"".join(date_list)+";priceAdj=U;cycle=D").Data[0])
        df = pd.DataFrame(data=close_prc, index=self.code_list, columns=[self.factor_name])
        return df


# 每股净有形资产
class NetTangibleAssetPerShare(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '每股净有形资产'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        tgb_asset = np.array(w.wss(self.code_list, "fa_tangibleasset", "tradeDate="+"".join(date_list)).Data[0])
        tot_liab = np.array(w.wss(self.code_list, "fa_totliab", "tradeDate="+"".join(date_list)).Data[0])
        total_shares = np.array(w.wss(self.code_list, "total_shares", "unit=1;tradeDate="+"".join(date_list)).Data[0])
        data = (tgb_asset-tot_liab)/total_shares
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 每股净流动资产
class NetLiquidAssetPerShare(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '每股净流动资产'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        total_equity = np.array(w.wss(self.code_list, "fa_totequity", "tradeDate="+"".join(date_list)).Data[0])
        fixed_asset = np.array(w.wss(self.code_list, "fa_fixassets", "tradeDate="+"".join(date_list)).Data[0])
        total_shares = np.array(w.wss(self.code_list, "total_shares", "unit=1;tradeDate="+"".join(date_list)).Data[0])
        data = (total_equity-fixed_asset)/total_shares
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 总负债
class TotalLiability(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '总负债'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        liab = np.array(w.wss(self.code_list, "fa_totliab", "tradeDate="+"".join(date_list)).Data[0])
        df = pd.DataFrame(data=liab, index=self.code_list, columns=[self.factor_name])
        return df


# 净流动资产(单位：元）
class NetLiquidAsset(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '净流动资产'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        total_equity = np.array(w.wss(self.code_list, "fa_totequity", "tradeDate="+"".join(date_list)).Data[0])
        fixed_asset = np.array(w.wss(self.code_list, "fa_fixassets", "tradeDate="+"".join(date_list)).Data[0])
        data = total_equity - fixed_asset
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 有形资产净值（单位：元）
class NetTangibleAsset(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '有形资产净值'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        tgb_asset = np.array(w.wss(self.code_list, "fa_tangibleasset", "tradeDate="+"".join(date_list)).Data[0])
        tot_liab = np.array(w.wss(self.code_list, "fa_totliab", "tradeDate="+"".join(date_list)).Data[0])
        data = tgb_asset - tot_liab
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 申万一级行业
class SW1Industry(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '申万一级行业'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        sw1_industry = np.array(w.wss(self.code_list, "indexcode_sw", "tradeDate="+''.join(date_list)+";industryType=1").Data[0])
        sw1_industry = pd.DataFrame(data=sw1_industry, index=self.code_list, columns=[self.factor_name])
        return sw1_industry


# 申万一级行业one-hot编码
class SW1IndustryOneHot(SW1Industry):
    def _calculate_factor(self):
        date_list = self.date
        sw1_industry = w.wss(self.code_list, "indexcode_sw", "tradeDate="+''.join(date_list)+";industryType=1").Data[0]
        SW1_INDEX_CODES = [t[0] for t in SW1_INDEX]
        SW1_INDEX_NAMES = [t[1] for t in SW1_INDEX]
        one_hot_matrix = np.zeros((len(sw1_industry), len(SW1_INDEX)))
        for i, industry_index in enumerate(sw1_industry):
            if industry_index == None:
                continue
            else:
                industry_loc = SW1_INDEX_CODES.index(industry_index)
                one_hot_matrix[i, industry_loc] = 1.0
        sw1_industry = pd.DataFrame(data=one_hot_matrix, index=self.code_list, columns=SW1_INDEX_NAMES)
        return sw1_industry


# 中信一级行业
class ZX1Industry(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '中信一级行业'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        zx1_industry = np.array(w.wss(self.code_list, "indexcode_citic", "tradeDate="+''.join(date_list)+";industryType=1").Data[0])
        zx1_industry = pd.DataFrame(data=zx1_industry, index=self.code_list, columns=[self.factor_name])
        return zx1_industry


# 申中信一级行业one-hot编码
class ZX1IndustryOneHot(ZX1Industry):
    def _calculate_factor(self):
        date_list = self.date
        zx1_industry = w.wss(self.code_list, "indexcode_citic", "tradeDate="+''.join(date_list)+";industryType=1").Data[0]
        ZX1_INDEX_CODES = [t[0] for t in ZX1_INDEX]
        ZX1_INDEX_NAMES = [t[1] for t in ZX1_INDEX]
        one_hot_matrix = np.zeros((len(zx1_industry), len(ZX1_INDEX)))
        for i, industry_index in enumerate(zx1_industry):
            if industry_index == None:
                continue
            else:
                industry_loc = ZX1_INDEX_CODES.index(industry_index)
                one_hot_matrix[i, industry_loc] = 1.0
        zx1_industry = pd.DataFrame(data=one_hot_matrix, index=self.code_list, columns=ZX1_INDEX_NAMES)
        return zx1_industry


# 月收益率
class ReturnsOneMonth(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '过去一个月的收益率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        date_now = '-'.join(date_list)
        date_prev = get_trading_date_from_now(date_now, -1, ql.Months)
        returns = np.array(w.wss(self.code_list, "pct_chg_per", "startDate="+date_prev+";endDate="+date_now).Data[0])
        df = pd.DataFrame(data=returns, index=self.code_list, columns=[self.factor_name])
        return df


# 经营活动现金流
class OperateCashFlow(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '经营活动现金流'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list,  "fa_operactcashflow_ttm", "unit=1;tradeDate=" + "".join(date_list)).Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 经营活动现金流/净利润
class CashFlowCoverRatio(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '利润现金保障倍数'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        operateCF = np.array(w.wss(self.code_list,  "fa_operactcashflow_ttm", "unit=1;tradeDate=" + "".join(date_list)).Data[0])
        netprofit = np.array(w.wss(self.code_list,  "fa_profit_ttm", "unit=1;tradeDate=" + "".join(date_list)).Data[0])
        data = operateCF/netprofit
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 销售费用
class SellExpense(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '销售费用'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list, "fa_sellexpense_ttm", "unit=1;tradeDate=" + ''.join(date_list)).Data[0])
        df = pd.DataFrame(data = data, index=self.code_list, columns=[self.factor_name])
        return df


# 销售费用占营业收入比
class SellExpenseRevenue(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '销售费用占营业收入比'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        sellexpense = np.array(w.wss(self.code_list, "fa_sellexpense_ttm", "unit=1;tradeDate=" + ''.join(date_list)).Data[0])
        revenue_data = np.array(w.wss(self.code_list, "or_ttm", "unit=1;tradeDate=" + "".join(date_list)).Data[0])
        if revenue_data == None:
            revenue_data = np.nan
        if sellexpense == None:
            sellexpense = np.nan
        data = sellexpense/revenue_data
        df = pd.DataFrame(data = data, index=self.code_list, columns=[self.factor_name])
        return df


# 销售费用增长率
class SellExpenseGrowth(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '销售费用增长率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        sellexpense_now = np.array(w.wss(self.code_list, "fa_sellexpense_ttm", "unit=1;tradeDate=" + ''.join(date_list)).Data[0])
        date_list[0] = str(int(date_list[0])-1)
        sellexpense_prev = np.array(w.wss(self.code_list, "fa_sellexpense_ttm", "unit=1;tradeDate=" + ''.join(date_list)).Data[0])
        if sellexpense_now == None:
            sellexpense_now = np.nan
        if sellexpense_prev == None:
            sellexpense_prev = np.nan
        data = (sellexpense_now - sellexpense_prev) / sellexpense_prev
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 非流动资产占比
class NonCurrentAssetRatio(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '非流动资产占比'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list,  "fa_noncurassetsratio", "unit=1;tradeDate=" + "".join(date_list)).Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 资产周转率
class AssetTurnoverRatio(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '资产周转率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list,  "fa_taturn_ttm", "unit=1;tradeDate=" + "".join(date_list)).Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 应收账款周转率
class AccRecTurnRatioV1(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '应收账款周转率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list,  "fa_arturn_ttm", "tradeDate=" + "".join(date_list)).Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 总资产
class TotalAsset(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '总资产'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list, "fa_totassets", "unit=1;tradeDate="+"".join(date_list)).Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 研发费用目前只支持报告期数据，19年1月开始对研发费用的会计政策变更，从管理费用中剥离出研发费用
class RDExpense(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '研发费用'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list, "rd_exp", "unit=1;rptDate=" + ''.join(date_list) + ";rptType=1").Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 研发费用目前只支持报告期数据，19年1月开始对研发费用的会计政策变更，从管理费用中剥离出研发费用
class RDExpenseRevenue(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '研发费用占营业收入比'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        RDExpense = np.array(w.wss(self.code_list, "rd_exp", "unit=1;rptDate=" + ''.join(date_list) + ";rptType=1").Data[0])
        revenue_data = np.array(w.wss(self.code_list, "or_ttm", "unit=1;tradeDate=" + "".join(date_list)).Data[0])
        if revenue_data == None:
            revenue_data = np.nan
        if RDExpense == None:
            RDExpense = np.nan
        data = RDExpense / revenue_data
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 应收账款周转率目前只支持报告期数据
class AccRecTurnRatioV2(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '应收账款周转率'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list,  "arturn", "rptDate=" + "".join(date_list)).Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 外资持股占流通市值比
class ForeignCapitalHoldingRatio(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '外资持股占流通市值比'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        data = np.array(w.wss(self.code_list, "share_pct_Ntofreefloat", "tradeDate=" + "".join(date_list)).Data[0])
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 过去N日外资持股比例平均增速，需继承
class ForeignCapitalHoldingRatioGrowth_Avg(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N=30):
        factor_name = '过去' + str(N) + '日外资持股比例平均增速'
        self.N = N
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        temp_date = get_trading_date_from_now("-".join(self.date), -int(3), ql.Days)
        data_start = np.array(w.wss(self.code_list, "share_pct_Ntofreefloat", "tradeDate=" + str(temp_date)).Data[0])
        data_end = np.array(w.wss(self.code_list, "share_pct_Ntofreefloat", "tradeDate=" + "".join(self.date)).Data[0])
        avggrowth = (data_end - data_start) / self.N
        df = pd.DataFrame(data=avggrowth, index=self.code_list, columns=[self.factor_name])
        df = df.dropna()
        return df


# 过去N日外资持股比例增速，线性回归法，需继承
class ForeignCapitalHoldingRatioGrowth_LR(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N=5):
        factor_name = '过去' + str(N) + '日外资持股比例增速'
        self.N = N
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        vol_data = []
        i = 0
        j = 0
        while True:
            temp_date = get_trading_date_from_now("-".join(self.date), -int(i), ql.Days)
            vol = np.array(w.wss(self.code_list, "share_pct_Ntofreefloat", "tradeDate=" + str(temp_date)).Data[0])
            i = i + 1
            if vol[0] is None:  # 判断是否为沪港通交易日，若不是，则继续前推交易日
                continue
            j = j + 1
            vol_data.append(vol)
            if j == self.N:  # 提取够数据，跳出循环
                break
        vol_data.reverse()  # 逆序
        vol_data = np.array(vol_data)
        X = np.linspace(0, self.N-1, self.N)[:, np.newaxis]
        X = np.c_[np.ones((self.N, 1)), X]
        result = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(vol_data)
        data = result[1]
        data = np.array(data).transpose()
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


# 过去10日外资持股比例增速，线性回归法
class ForeignCapitalHoldingRatioGrowth_LR_10(ForeignCapitalHoldingRatioGrowth_LR):
    def __init__(self, date, code_list):
        super().__init__(date, code_list, N=10)


# 过去N日外资持股比例增速加速度，线性回归法，需继承
class ForeignCapitalHoldingRatioGrowth_LR_ACC(SingleFactorReasearch):
    @abc.abstractmethod
    def __init__(self, date, code_list, N=6):
        factor_name = '过去' + str(N) + '日外资持股增速加速度'
        self.N = N
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        vol_data = []
        i = 0
        j = 0
        while True:
            temp_date = get_trading_date_from_now("-".join(self.date), -int(i), ql.Days)
            vol = np.array(w.wss(self.code_list, "share_pct_Ntofreefloat", "tradeDate=" + str(temp_date)).Data[0])
            i = i + 1
            if vol[0] is None:  # 判断是否为沪港通交易日，若不是，则继续前推交易日
                continue
            j = j + 1
            vol_data.append(vol)
            if j == self.N:  # 提取够数据，跳出循环
                break
        vol_data.reverse()  # 逆序
        vol_data = np.array(vol_data)
        X = np.linspace(0, self.N-1, self.N)[:, np.newaxis]
        X = np.c_[np.ones((self.N, 1)), X, X*X]
        result = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(vol_data)
        data = result[2]
        data = np.array(data).transpose()
        df = pd.DataFrame(data=data, index=self.code_list, columns=[self.factor_name])
        return df


if __name__ == '__main__':
    date = '2017-05-09'
    w.start()
    code_list = w.wset("sectorconstituent", "date=" + date + ";windcode=000300.SH").Data[1]  # 沪深300动态股票池
    # code_list = ['000001.SZ', '000002.SZ']
    factor_model = ForeignCapitalHoldingRatioGrowth_LR(date, code_list)
    df = factor_model.get_factor()
    print(df)