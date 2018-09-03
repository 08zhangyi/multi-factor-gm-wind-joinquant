from WindPy import w
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_trading_date_from_now


def LLT(price_list, d=69):
    a = 2 / (d + 1)  # LLT的参数
    LLT_list = [price_list[0], price_list[1]]  # 记录LLT值列表的初始化序列
    for t in range(2, len(price_list)):
        LLT_value = (a - (a ** 2 / 4)) * price_list[t] + (a ** 2 / 2) * price_list[t - 1] - (a - (3 * a ** 2 / 4)) * price_list[t - 2] + 2 * (1 - a) * LLT_list[-1] - (1 - a) ** 2 * LLT_list[-2]
        LLT_list.append(LLT_value)
    return LLT_list[-1] - LLT_list[-2]  # LLT趋势值


w.start()
date_now = '2017-07-28'
date_prev = get_trading_date_from_now(date_now, -4)
print(w.wsd("801010.SI", "close2", date_prev, date_now, "adjDate="+date_now+";PriceAdj=T"))