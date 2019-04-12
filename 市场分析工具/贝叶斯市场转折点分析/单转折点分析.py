from WindPy import w
import numpy as np
import matplotlib.pyplot as plt
import pymc3 as pm
import scipy.stats


w.start()
INDEX = '000300.SH'  # 分析的指数代码
START_DATE = '2019-01-07'
END_DATE = '2019-04-11'
data = w.wsd(INDEX, "pct_chg", START_DATE, END_DATE, "")
times = data.Times
data = data.Data[0]
data = np.array(data)

N = len(data)
dates = np.array(range(N))

with pm.Model() as model:
    tau = pm.DiscreteUniform(name="tau", lower=0, upper=N-1)
    mu_1 = pm.Normal(name='mu_1', mu=0.0, sd=2.0)
    mu_2 = pm.Normal(name='mu_2', mu=0.0, sd=2.0)
    sd_1 = pm.Exponential(name='sd_1', lam=0.4)
    sd_2 = pm.Exponential(name='sd_2', lam=0.4)
    # tau前为1，tau后为2
    mu = pm.math.switch(tau >= dates, mu_1, mu_2)
    sd = pm.math.switch(tau >= dates, sd_1, sd_2)
    # returns = pm.Normal(name='returns', mu=mu, sd=2.0, observed=data)
    # returns = pm.Normal(name='returns', mu=mu, sd=sd, observed=data)
    returns = pm.StudentT(name='returns', nu=4, mu=mu, sd=sd, observed=data)

    start = pm.find_MAP()
    step = pm.NUTS()
    trace = pm.sample(30000, step=step, start=start, chains=1)
    print(trace)

trace = trace[1000:]
tau_mean = int(np.mean(trace['tau']))
tau_mode = scipy.stats.mode(trace['tau'])[0][0]
print(times[tau_mean], tau_mean)
print(times[tau_mode], tau_mode)
tau_lower, tau_upper = pm.hpd(trace['tau'], alpha=0.2)
print(times[tau_lower], tau_lower)
print(times[tau_upper], tau_upper)
mu_1_mean = np.mean(trace['mu_1'])
mu_2_mean = np.mean(trace['mu_2'])
pm.traceplot(trace, lines={'mu_1': mu_1_mean, 'mu_2': mu_2_mean, 'tau': tau_mode})
plt.show()
