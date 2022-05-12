from WindPy import w

w.start()
CODE_LIST = ['510300.SH', '511380.SH']
START_DATE = '2022-02-12'
END_DATE = '2022-05-12'
data = w.wss(CODE_LIST, "stdevry",
             "startDate="+START_DATE+";endDate="+END_DATE+";period=1;returnType=1").Data[0]
print(data)
print(data[0]/data[1])