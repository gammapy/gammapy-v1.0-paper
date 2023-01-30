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
fig.subplots_adjust(bottom=0.06, top=0.95, right=0.9)

plt.savefig("gp_makers.pdf", dpi=300)
