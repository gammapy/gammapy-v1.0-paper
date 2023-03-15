import os
from pathlib import Path

import config
import matplotlib.pyplot as plt

os.environ["GAMMAPY_DATA"] = "../data/input"

filename = Path("../code-examples/snippets/gp_makers.py")


with open(filename, "r") as f:
    code = f.read()
    exec(code)

fig = plt.gcf()
figsize = config.FigureSizeAA(aspect_ratio=1.5, width_aa="two-column")
fig.set_size_inches(*figsize.inch)
fig.subplots_adjust(bottom=0.05, top=0.97, right=0.92, left=0.1)

for idx in [1, 3, 5, 7]:
    ax = fig.axes[idx]
    bbox = ax.get_position()
    ax.set_position([bbox.x0 + 0.07, bbox.y0, bbox.width, bbox.height])

# if ax.get_label() == "<colorbar>":
# ax.set_position([bbox.x0 + 0.3, bbox.y0, 0.02, bbox.height])


plt.savefig("gp_makers.pdf", dpi=300)
