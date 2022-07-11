from gammapy.stats import WStatCountsStatistic

n_on = [13, 5, 3]
n_off = [11, 9, 20]
alpha = [0.8, 0.5, 0.1]
stat = WStatCountsStatistic(n_on, n_off, alpha)

# Excess
print(stat.n_sig)

# Significance
print(stat.sqrt_ts)

# Asymmetrical rrors
print(stat.compute_errn(1.))
print(stat.compute_errp(1.))

