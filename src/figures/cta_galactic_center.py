#!/usr/bin/env python
# coding: utf-8
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.convolution import Gaussian2DKernel
from astropy.visualization import simple_norm
from regions import CircleSkyRegion
from gammapy.modeling import Fit
from gammapy.data import DataStore
from gammapy.datasets import (
    Datasets,
    FluxPointsDataset,
    SpectrumDataset,
    MapDataset,
)
from gammapy.modeling.models import (
    PowerLawSpectralModel,
    SkyModel,
    GaussianSpatialModel,
)
from gammapy.maps import MapAxis, WcsNDMap, WcsGeom, RegionGeom, Map
from gammapy.makers import (
    MapDatasetMaker,
    SafeMaskMaker,
    SpectrumDatasetMaker,
    ReflectedRegionsBackgroundMaker,
)
from gammapy.estimators import TSMapEstimator, FluxPointsEstimator, FluxPoints
from gammapy.estimators.utils import find_peaks
from gammapy.visualization import plot_spectrum_datasets_off_regions
import config

# Configure the logger, so that the spectral analysis
# isn't so chatty about what it's doing.
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

ENERGY_AXIS = MapAxis.from_edges(
    np.logspace(-1.0, 1.0, 10), unit="TeV", name="energy", interp="log"
)

GEOM = WcsGeom.create(
    skydir=(0, 0), npix=(500, 400), binsz=0.02, frame="galactic", axes=[ENERGY_AXIS.squash()]
)


def plot_spectrum_and_image():
    counts = Map.read("../data/cta-galactic-center/stacked-counts.fits")
    datasets = Datasets.read("../data/cta-galactic-center/datasets/datasets.yaml")

    figsize = config.FigureSizeAA(aspect_ratio=2.8, width_aa="two-column")
    fig = plt.figure(figsize=figsize.inch)

    wcs = counts.geom.wcs
    rect = (0.05, 0.2, 0.4, 0.75)
    ax = fig.add_axes(rect=rect, projection=wcs)
    counts = counts.smooth("0.03 deg")
    norm = simple_norm(counts.data, stretch="asinh",  max_cut=15, min_cut=0)
    counts.plot(ax=ax, norm=norm)

    datasets[0].counts.geom.region.to_pixel(ax.wcs).plot(ax=ax, edgecolor="white")
    plot_spectrum_datasets_off_regions(datasets, ax=ax, legend_kwargs={"loc": "lower left", "fontsize": 6})

    rect = (0.55, 0.2, 0.4, 0.75)
    ax = fig.add_axes(rect=rect)
    fp = FluxPoints.read("../data/cta-galactic-center/flux-points.fits", sed_type="likelihood")
    fp.plot(ax=ax, sed_type="e2dnde", color="tab:orange")
    fp.plot_ts_profiles(ax=ax, sed_type="e2dnde", rasterized=True)

    filename = "cta_galactic_center.pdf"
    log.info(f"Writing {filename}")
    plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    plot_spectrum_and_image()
