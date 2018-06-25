from WindPy import w
import pandas as pd
import numpy as np
import datetime

w.start()
data_temp = w.wset("sharepledge","startdate=2017-11-12;enddate=2018-02-12;sectorid=1000008660000000;field=wind_code,pledged_shares,pledge_end_date,pledge_termination_date").Data
df = pd.DataFrame(data=np.array([data_temp[1], data_temp[2], data_temp[3]]).transpose(), index=data_temp[0])
df[0] = df[0] * 10000.0
# df1 = (df[1]==None)
#df1 = df.replace(None, datetime.datetime.strptime('2200-12-21', '%Y-%m-%d'))
print(df[0]['601966.SH'])
#df = df[(df[1]==None & df[2]==None) | ((df[1]>datetime.datetime.strptime('2018-02-12', '%y-%m-%d')) & (df[2]>datetime.datetime.strptime('2018-02-12', '%y-%m-%d')))]
#print(df)