# 单因子提取器，不包含作图和行业分组
from WindPy import w
import numpy as np
import pandas as pd
import datetime


class SingleFactorReasearch():
    def __init__(self, date, code_list, factor_name):
        # date为查询因子的日期，'yyyy-mm-dd'格式
        # code_list为查询因子的股票代码列表
        self.date = date.split('-')
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


# RSI指标
class RSI(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '相对强度指标RSI'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        rsi_index = w.wss(self.code_list, "RSI", "industryType=1;tradeDate="+''.join(date_list)+";RSI_N=6;priceAdj=T;cycle=D").Data[0]
        net_profit_grow_rate = pd.DataFrame(data=rsi_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


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


# EPS指标
class EPS(SingleFactorReasearch):
    def __init__(self, date, code_list):
        factor_name = '基本每股收益EPS'
        super().__init__(date, code_list, factor_name)

    def _calculate_factor(self):
        date_list = self.date
        eps_index = np.array(w.wss(self.code_list, "eps_ttm", "tradeDate=" + ''.join(date_list)).Data[0])
        net_profit_grow_rate = pd.DataFrame(data=eps_index, index=self.code_list, columns=[self.factor_name])
        return net_profit_grow_rate


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


if __name__ == '__main__':
    date = '2018-06-19'
    w.start()
    code_list = w.wset("sectorconstituent", "date=" + date + ";windcode=000300.SH").Data[1]  # 沪深300动态股票池
    # code_list = ['000001.SZ', '000002.SZ']
    factor_model = NetProfitGrowRate(date, code_list)
    df = factor_model.get_factor()
    df.to_csv('temp1.csv')
    print(df)