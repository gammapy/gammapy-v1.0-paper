from gammapy.stats import WStatCountsStatistic

n_on = [13, 5, 3]
n_off = [11, 9, 20]
alpha = [0.8, 0.5, 0.1]
stat = WStatCountsStatistic(n_on, n_off, alpha)

# Excess
print(f"Excess: {stat.n_sig}")

# Significance
print(f"Significance: {stat.sqrt_ts}")

# Asymmetrical errors
print(f"Error Neg.: {stat.compute_errn(n_sigma=1.0)}")
print(f"Error Pos.: {stat.compute_errp(n_sigma=1.0)}")
