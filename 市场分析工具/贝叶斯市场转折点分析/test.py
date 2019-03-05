from WindPy import w
import numpy as np
import matplotlib.pyplot as plt
import pymc3 as pm
import scipy.stats


w.start()
data = w.wsd("000300.SH", "pct_chg", "2018-08-21", "2019-03-01", "")
times = data.Times
data = data.Data[0]
data = np.array(data)

N = len(data)
dates = np.array(range(N))

with pm.Model() as model:
    tau = pm.DiscreteUniform(name="tau", lower=0, upper=N-1)
    mu_1 = pm.Normal(name='mu_1', mu=0.0, sd=2.0)
    mu_2 = pm.Normal(name='mu_2', mu=0.0, sd=2.0)
    # tau前为1，tau后为2
    mu = pm.math.switch(tau >= dates, mu_1, mu_2)
    returns = pm.Normal(name='returns', mu=mu, sd=2.0, observed=data)

    start = pm.find_MAP()
    step = pm.NUTS()
    trace = pm.sample(30000, step=step, start=start, chains=1)
    print(trace)

trace = trace[1000:]
tau_mean = int(np.mean(trace['tau']))
tau_mode = scipy.stats.mode(trace['tau'])
print(times[tau_mean])
print(tau_mean)
print(tau_mode)
mu_1_mean = np.mean(trace['mu_1'])
mu_2_mean = np.mean(trace['mu_2'])
pm.traceplot(trace, lines={'mu_1': mu_1_mean, 'mu_2': mu_2_mean, 'tau': 100})
plt.show()


