import pandas as pd
import numpy as np
from WindPy import w

codes = "000300.SH,000001.SH"
w.start()
wind_data = w.wsd(codes, "close", "2013-07-01", "2018-06-29", "Period=W")

df = pd.DataFrame(np.array(wind_data.Data).T, index=wind_data.Times, columns=wind_data.Codes)
df.to_csv('data\\data.csv')