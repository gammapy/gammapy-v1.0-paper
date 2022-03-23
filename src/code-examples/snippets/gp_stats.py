from gammapy.stats import WStatCountsStatistic

n_on = [13, 5, 3]
n_off = [11, 9, 20]
alpha = [0.8, 0.5, 0.1]
stat = WStatCountsStatistic(n_on=13, n_off=11, alpha=1. / 2)
print(f"Excess  : {stat.n_sig:.2f}")
print(f"sqrt(TS): {stat.sqrt_ts:.2f}")
print(f"Errors (1 sigma): {stat.compute_errn(1.):.2f} -- {stat.compute_errp(1.):.2f}")
print(f"Errors (2 sigma): {stat.compute_errn(2.):.2f} -- {stat.compute_errp(2.):.2f}")

