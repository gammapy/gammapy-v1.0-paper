import config
import matplotlib.pyplot as plt

figsize = config.FigureSizeAA(aspect_ratio=1.618, width_aa="one-column")
fig, ax  = plt.subplots(figsize=figsize)



fig.savefig("multi_instrument_analysis.pdf")