from WindPy import w
import pandas as pd
import sys
sys.path.append('D:\\programs\\多因子策略开发\\掘金多因子开发测试\\工具')
from utils import get_trading_date_from_now

# 准备工作
w.start()
# 确定研究范围，以发行日期圈定可转债
START_DATE = '2017-09-01'
END_DATE = '2021-08-26'
T1 = 1  # 发行日前第几天买入正股
T2 = 0  # 发行日后第几天卖出正股
T3 = 0  # 上市日后第几天卖出可转债

# 获取交易所可转债发行代码
result_list_sh = w.wset("newbondissueview",
                        "startdate=%s;enddate=%s;datetype=startdate;bondtype=convertiblebonds;dealmarket=sse;maingrade=all" % (START_DATE, END_DATE)).Data[0]
result_list_sz = w.wset("newbondissueview",
                        "startdate=%s;enddate=%s;datetype=startdate;bondtype=convertiblebonds;dealmarket=szse;maingrade=all" % (START_DATE, END_DATE)).Data[0]
conv_bonds = result_list_sh + result_list_sz
# 获取发行额度，发行日，上市日，正股代码信息
result = w.wss(conv_bonds, "issueamount,issue_firstissue,ipo_date,underlyingcode", "unit=1").Data
conv_bonds_issue_amount = result[0]
conv_bonds_issue_date = result[1]
conv_bonds_listing_date = result[2]
conv_bonds_underlying_code = result[3]

result_list = []
# 根据可转债列表计算抢权配售收益率
for conv_bond, issue_amount, issue_date, listing_date, underlying_code \
        in zip(conv_bonds, conv_bonds_issue_amount, conv_bonds_issue_date, conv_bonds_listing_date, conv_bonds_underlying_code):
    issue_date = issue_date.strftime('%Y-%m-%d')
    listing_date = listing_date.strftime('%Y-%m-%d')
    underlying_buy_date = get_trading_date_from_now(issue_date, -T1)  # 正股买入日期
    underlying_sell_date = get_trading_date_from_now(issue_date, T2)  # 正股卖出日期
    if underlying_code is None or underlying_code[-2:] not in ['SZ', 'SH']:  # 可转债无正股代码信息，跳过
        continue
    # 获取正股走势变动信息
    underlying_price = w.wsd(underlying_code, "close", underlying_buy_date, underlying_sell_date, "PriceAdj=T").Data[0]
    print(conv_bond, underlying_code, underlying_price)
    if underlying_price[-1] is None:  # 可转债无正股价格信息，跳过
        continue
    # 获取可转债上市收益信息
    if listing_date == '1899-12-30':  # 可转债尚未上市
        conv_bond_price = 100
    else:
        conv_bond_sell_date = get_trading_date_from_now(listing_date, T3)
        conv_bond_price = w.wsd(conv_bond, "close", conv_bond_sell_date, conv_bond_sell_date, "").Data[0][0]
    # 获取发行日总股份信息和可转债配售比例信息
    underlying_number = w.wss(underlying_code, "total_shares", "unit=1;tradeDate=" + issue_date).Data[0][0]
    conv_bond_number = issue_amount / underlying_number
    conv_bond_ratio = conv_bond_number / underlying_price[0]
    # 计算抢权配售收益率
    money_amount = underlying_price[0] + conv_bond_number
    total_asset = underlying_price[-1] + conv_bond_number * conv_bond_price / 100
    rate_return = (total_asset - money_amount) / money_amount
    # 汇总信息
    # ['可转债代码', '正股代码', '可转债发行日', '可转债上市日', '配售比例', '配售收益率', '正股买入价格', '正股卖出价格', '可转债卖出价格']
    print([conv_bond, underlying_code, issue_date, listing_date, conv_bond_ratio, rate_return])
    result_list.append([conv_bond, underlying_code, issue_date, listing_date, conv_bond_ratio, rate_return,
                        underlying_price[0], underlying_price[-1], conv_bond_price])
result = pd.DataFrame(result_list, columns=['可转债代码', '正股代码', '可转债发行日', '可转债上市日', '配售比例', '配售收益率',
                                            '正股买入价格', '正股卖出价格', '可转债卖出价格'])
result = result.sort_values('可转债发行日')
print(result)
result.to_excel('data//result.xlsx')