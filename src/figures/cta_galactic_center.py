import logging
from pathlib import Path

import config
import matplotlib.pyplot as plt
from astropy.visualization import simple_norm

from gammapy.datasets import Datasets
from gammapy.estimators import FluxPoints
from gammapy.maps import Map
from gammapy.visualization import plot_spectrum_datasets_off_regions

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def plot_spectrum_and_image():
    path = Path("../data/cta-galactic-center/")
    counts = Map.read(path / "stacked-counts.fits")
    datasets = Datasets.read(path / "datasets/datasets.yaml")

    figsize = config.FigureSizeAA(aspect_ratio=2.8, width_aa="two-column")
    fig = plt.figure(figsize=figsize.inch)

    wcs = counts.geom.wcs
    rect = (0.05, 0.17, 0.4, 0.8)
    ax = fig.add_axes(rect=rect, projection=wcs)
    counts = counts.smooth("0.03 deg")
    norm = simple_norm(counts.data, stretch="asinh", max_cut=15, min_cut=0)
    counts.plot(ax=ax, norm=norm)

    datasets[0].counts.geom.region.to_pixel(ax.wcs).plot(ax=ax, edgecolor="white")
    plot_spectrum_datasets_off_regions(
        datasets, ax=ax, legend_kwargs={"loc": "lower left", "fontsize": 6}
    )

    rect = (0.55, 0.17, 0.4, 0.8)
    ax = fig.add_axes(rect=rect)
    fp = FluxPoints.read(
        "../data/cta-galactic-center/flux-points.fits", sed_type="likelihood"
    )
    fp.plot(ax=ax, sed_type="e2dnde", color="tab:orange")
    fp.plot_ts_profiles(ax=ax, sed_type="e2dnde", rasterized=True)
    sed_x_label = "Energy / TeV"
    sed_y_label = (
        r"$E^2\,{\rm d}\phi/{\rm d}E\,/\,({\rm erg}\,{\rm cm}^{-2}\,{\rm s}^{-1})$"
    )

    ax.set_xlabel(sed_x_label)
    ax.set_ylabel(sed_y_label)

    filename = "cta_galactic_center.pdf"
    log.info(f"Writing {filename}")
    plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    plot_spectrum_and_image()
