import logging
from pathlib import Path

import astropy.units as u
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from astropy.coordinates import SkyCoord

from gammapy.datasets import MapDataset
from gammapy.estimators import FluxMaps, TSMapEstimator
from gammapy.irf import EDispKernelMap, PSFMap
from gammapy.maps import Map
from gammapy.modeling.models import PointSpatialModel, PowerLawSpectralModel, SkyModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def read_dataset():
    path = Path("../input/fermi-3fhl-gc/")
    counts = Map.read(path / "fermi-3fhl-gc-counts-cube.fits.gz")
    background = Map.read(path / "fermi-3fhl-gc-background-cube.fits.gz")
    exposure = Map.read(path / "fermi-3fhl-gc-exposure-cube.fits.gz")
    psfmap = PSFMap.read(path / "fermi-3fhl-gc-psf-cube.fits.gz", format="gtpsf")

    edisp = EDispKernelMap.from_diagonal_response(
        energy_axis=counts.geom.axes["energy"],
        energy_axis_true=exposure.geom.axes["energy_true"],
    )

    return MapDataset(
        counts=counts,
        background=background,
        exposure=exposure,
        psf=psfmap,
        name="fermi-3fhl-gc",
        edisp=edisp,
    )


def estimate_ts_map(dataset):
    spatial_model = PointSpatialModel()

    # We choose units consistent with the map units here...
    spectral_model = PowerLawSpectralModel(amplitude="1e-22 cm-2 s-1 keV-1", index=2)
    model = SkyModel(spatial_model=spatial_model, spectral_model=spectral_model)

    estimator = TSMapEstimator(
        model, kernel_width="3 deg", energy_edges=[10, 50, 2000] * u.GeV, n_jobs=4
    )
    return estimator.run(dataset)


if __name__ == "__main__":
    filename = Path("fermi-ts-maps.fits")
    dataset = read_dataset()
    maps = estimate_ts_map(dataset=dataset)
    log.info(f"Writing {filename}")
    maps.write(filename, overwrite=True)
