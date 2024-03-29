import logging
from pathlib import Path

import config
import matplotlib.pyplot as plt

from gammapy.estimators import FluxPoints

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

sed_y_label = r"$\phi_{E}\,/\,({\rm erg}\,{\rm cm}^{-2}\,{\rm s}^{-1})$"


def plot_lightcurve():
    figsize = config.FigureSizeAA(aspect_ratio=1.618, width_aa="intermediate")
    fig = plt.figure(figsize=figsize.inch)

    ax = fig.add_axes([0.135, 0.33, 0.86, 0.66])

    path = Path("../data/lightcurve")
    filename = path / "pks2155_flare_lc.fits.gz"
    lc = FluxPoints.read(filename, format="lightcurve")
    lc.plot(ax=ax, sed_type="eflux", axis_name="time")
    ax.set_ylabel(sed_y_label)

    filename = "hess_lightcurve_pks.pdf"
    log.info(f"Writing {filename}")
    plt.legend(loc="lower left")
    plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    plot_lightcurve()
