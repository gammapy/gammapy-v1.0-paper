import config
import numpy as np
import matplotlib.pyplot as plt

figsize = config.FigureSizeAA(aspect_ratio=1.618, width_aa="single-column")
fig, ax  = plt.subplots(1, 1, figsize=figsize.inch)

x = np.ones(5)
ax.plot(x, x, marker="o")

fig.savefig("multi_instrument_analysis.pdf")