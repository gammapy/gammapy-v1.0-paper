import os
from pathlib import Path

import config
import matplotlib.pyplot as plt

os.environ["GAMMAPY_DATA"] = "../data"

filename = Path("../code-examples/snippets/gp_catalogs.py")


with open(filename, "r") as f:
    code = f.read()
    exec(code)

fig = plt.gcf()
figsize = config.FigureSizeAA(aspect_ratio=2.2, width_aa="two-column")
fig.set_size_inches(*figsize.inch)

gridspec_kw = {
    "bottom": 0.25,
    "wspace": 0.2,
    "top": 0.92,
    "left": 0.12,
    "right": 0.98,
}

fig.subplots_adjust(**gridspec_kw)

plt.savefig("gp_catalogs.pdf", dpi=300)
