from WindPy import w
import numpy as np
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import list_wind2jq


def equal_transfer(code_list, date):
    # 按照date日的参数等权调仓
    stock_now = {}
    for code in code_list:
        stock_now[list_wind2jq([code])[0]] = 1. / len(code_list)
    return stock_now


def market_capital_transfer(code_list, date):
    # 按照date日的总市值权调仓
    stock_now = {}
    w.start()
    weight_data = np.array(w.wss(code_list, "mkt_cap_ard", "unit=1;tradeDate="+date+";currencyType=").Data[0])
    weight_data = weight_data / np.sum(weight_data)
    for i in range(len(code_list)):
        code = code_list[i]
        stock_now[list_wind2jq([code])[0]] = weight_data[i]
    return stock_now


def market_capital_float_transfer(code_list, date):
    # 按照date日的流通市值权调仓
    stock_now = {}
    w.start()
    weight_data = np.array(w.wss(code_list, "mkt_cap_float", "unit=1;tradeDate=" + date + ";currencyType=").Data[0])
    weight_data = weight_data / np.sum(weight_data)
    for i in range(len(code_list)):
        code = code_list[i]
        stock_now[list_wind2jq([code])[0]] = weight_data[i]
    return stock_now


def market_capital_freeshares_transfer(code_list, date):
    # 按照date日的Wind定义自由流通市值权调仓
    stock_now = {}
    w.start()
    weight_data = np.array(w.wss(code_list, "mkt_freeshares", "unit=1;tradeDate=" + date + ";currencyType=").Data[0])
    weight_data = weight_data / np.sum(weight_data)
    for i in range(len(code_list)):
        code = code_list[i]
        stock_now[list_wind2jq([code])[0]] = weight_data[i]
    return stock_now


if __name__ == '__main__':
    code_list = ["000001.SZ", "000002.SZ"]
    date = '2018-08-15'
    print(market_capital_transfer(code_list, date))