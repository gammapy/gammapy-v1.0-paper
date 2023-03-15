import os
from pathlib import Path

import config
import matplotlib.pyplot as plt

os.environ["GAMMAPY_DATA"] = "../data/input"

filename = Path("../code-examples/snippets/gp_estimators.py")


with open(filename, "r") as f:
    code = f.read()
    exec(code)

fig = plt.gcf()
figsize = config.FigureSizeAA(aspect_ratio=2.5, width_aa="two-column")
fig.set_size_inches(*figsize.inch)
fig.subplots_adjust(left=0.1, bottom=0.05, top=0.98, right=0.98)

fig.axes[2].set_ylabel("$\sqrt{TS}$")
fig.axes[3].set_ylabel("$\sqrt{TS}$")

plt.savefig("gp_estimators.pdf", dpi=300)
