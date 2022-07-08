from gammapy.stats import WStatCountsStatistic

n_on = [13, 5, 3]
n_off = [11, 9, 20]
alpha = [0.8, 0.5, 0.1]
stat = WStatCountsStatistic(n_on, n_off, alpha)

# Excess
stat.n_sig

# Significance
stat.sqrt_ts

# Asymmetrical rrors
stat.compute_errn(1.)
stat.compute_errp(1.)

