import logging
from pathlib import Path
import matplotlib.pyplot as plt
from gammapy.estimators import FluxPoints


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def plot_lightcurve():
    path = Path(".")
    filename = path / "pks2155_flare_lc.fits.gz"
    lc = FluxPoints.read(filename, sed_type="lightcurve")
    lc.plot(sed_type="eflux", axis_name="time")
    filename = "lghtcurve-pks.pdf"
    log.info(f"Writing {filename}")
    plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    plot_lightcurve()
