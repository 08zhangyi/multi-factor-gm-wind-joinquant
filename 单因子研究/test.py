from WindPy import w
w.start()
print(w.wss("002352.SZ", "industry_sw,indexcode_sw", "industryType=1;tradeDate=20180828").Data)
print(w.wss("002352.SZ", "industry_sw,indexcode_sw", "industryType=1;tradeDate=20160828").Data)