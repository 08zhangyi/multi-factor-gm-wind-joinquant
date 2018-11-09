from WindPy import w
import pandas as pd
import numpy as np

SW1 = "801010.SI,801020.SI,801030.SI,801040.SI,801050.SI,801080.SI,801110.SI,801120.SI,801130.SI,801140.SI,801150.SI,801160.SI,801170.SI,801180.SI,801200.SI,801210.SI,801230.SI,801710.SI,801720.SI,801730.SI,801740.SI,801750.SI,801760.SI,801770.SI,801780.SI,801790.SI,801880.SI,801890.SI"
w.start()
data = w.wsd(SW1, "pct_chg", "2017-11-01", "2018-11-02", "PriceAdj=T")

df = pd.DataFrame(data=np.array(data.Data).transpose(), index=data.Times, columns=SW1.split(','))
df.to_csv('data\\data.csv')