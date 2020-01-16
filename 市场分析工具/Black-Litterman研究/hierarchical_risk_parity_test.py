import pandas as pd
import numpy as np
from pypfopt.hierarchical_risk_parity import HRPOpt

names = ['a', 'b', 'c', 'd']
x = np.random.random((3, len(names)))
x = pd.DataFrame(x, columns=names)

optimizer = HRPOpt(x)
print(optimizer.hrp_portfolio())