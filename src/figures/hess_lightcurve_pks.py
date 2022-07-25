import logging
from pathlib import Path
import matplotlib.pyplot as plt
from gammapy.estimators import FluxPoints
import config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def plot_lightcurve():
    figsize = config.FigureSizeAA(aspect_ratio=1.618, width_aa="intermediate")
    fig = plt.figure(figsize=figsize.inch)

    ax = fig.add_axes([0.1, 0.22, 0.88, 0.77])

    path = Path("../data/lightcurve")
    filename = path / "pks2155_flare_lc.fits.gz"
    lc = FluxPoints.read(filename, format="lightcurve")
    lc.plot(ax=ax, sed_type="eflux", axis_name="time")
    filename = "hess_lightcurve_pks.pdf"
    log.info(f"Writing {filename}")
    plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    plot_lightcurve()
