import pandas as pd
import numpy as np
from WindPy import w


def get_data_from_wind(code_list, period, start_date, end_date):
    codes = ','.join(code_list)
    w.start()
    wind_data = w.wsd(codes, "close", "2010-07-01", "2018-06-29", "Period="+period)
    df = pd.DataFrame(np.array(wind_data.Data).T, index=wind_data.Times, columns=wind_data.Codes)
    df.to_csv('data\\market_data\\data_'+period+'.csv')


code_list = ['000001.SH', '000300.SH', '000016.SH', '000905.SH', '399006.SZ']
period = 'W'
start_date = '2010-07-01'
end_date = '2018-06-29'
get_data_from_wind(code_list, period, start_date, end_date)