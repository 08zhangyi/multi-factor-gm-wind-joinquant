from WindPy import w

w.start()

print(w.wss("600000.SH", "pct_chg_per","startDate=2018-06-19;endDate=2018-07-18").Data[0])
print(w.wsd("600000.SH", "close", "2018-06-15", "2018-07-18", "PriceAdj=T").Data[0])

print(w.wss("600000.SH", "pre_close_per","startDate=20180619;endDate=20180718;priceAdj=F").Data[0])
print(w.wss("600000.SH", "close_per","startDate=20180619;endDate=20180718;priceAdj=F").Data[0])