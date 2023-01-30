#!/usr/bin/env python
import logging
from pathlib import Path

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from regions import CircleSkyRegion

from gammapy.data import DataStore
from gammapy.datasets import Datasets, MapDataset, SpectrumDataset
from gammapy.estimators import FluxPointsEstimator
from gammapy.makers import (
    MapDatasetMaker,
    ReflectedRegionsBackgroundMaker,
    SafeMaskMaker,
    SpectrumDatasetMaker,
)
from gammapy.maps import MapAxis, RegionGeom, WcsGeom
from gammapy.modeling import Fit
from gammapy.modeling.models import PowerLawSpectralModel, SkyModel

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

ENERGY_AXIS = MapAxis.from_edges(
    np.logspace(-1.0, 1.0, 10), unit="TeV", name="energy", interp="log"
)

GEOM = WcsGeom.create(
    skydir=(0, 0),
    npix=(500, 400),
    binsz=0.02,
    frame="galactic",
    axes=[ENERGY_AXIS.squash()],
)


def get_observations():
    # Select observations
    data_store = DataStore.from_dir("../input/cta-1dc/index/gps")
    obs_id = [110380, 111140, 111159]
    return data_store.get_observations(obs_id)


def make_counts_image(observations):
    # Define map geometry
    stacked = MapDataset.create(geom=GEOM)
    maker = MapDatasetMaker(selection=["counts"])
    maker_safe_mask = SafeMaskMaker(methods=["offset-max"], offset_max=2.5 * u.deg)

    for obs in observations:
        cutout = stacked.cutout(obs.pointing_radec, width="5 deg")
        dataset = maker.run(cutout, obs)
        dataset = maker_safe_mask.run(dataset, obs)
        stacked.stack(dataset)

    return stacked.counts


def make_datasets_spectral(observations):
    target_position = SkyCoord(0, 0, unit="deg", frame="galactic")
    on_radius = 0.2 * u.deg
    on_region = CircleSkyRegion(center=target_position, radius=on_radius)

    exclusion_mask = GEOM.to_image().region_mask([on_region], inside=False)

    energy_axis = MapAxis.from_energy_bounds(0.1, 40, 40, unit="TeV", name="energy")
    energy_axis_true = MapAxis.from_energy_bounds(
        0.05, 100, 200, unit="TeV", name="energy_true"
    )

    geom = RegionGeom.create(region=on_region, axes=[energy_axis])
    dataset_empty = SpectrumDataset.create(geom=geom, energy_axis_true=energy_axis_true)

    dataset_maker = SpectrumDatasetMaker(
        containment_correction=False, selection=["counts", "exposure", "edisp"]
    )
    bkg_maker = ReflectedRegionsBackgroundMaker(exclusion_mask=exclusion_mask)
    safe_mask_masker = SafeMaskMaker(methods=["aeff-max"], aeff_percent=10)

    datasets = Datasets()

    for observation in observations:
        dataset = dataset_maker.run(
            dataset_empty.copy(name=f"obs-{observation.obs_id}"), observation
        )
        dataset_on_off = bkg_maker.run(dataset, observation)
        dataset_on_off = safe_mask_masker.run(dataset_on_off, observation)
        datasets.append(dataset_on_off)

    return datasets


def make_flux_points(datasets):
    # Flux points are computed on stacked observation
    stacked_dataset = datasets.stack_reduce(name="stacked")
    stacked_dataset.models = datasets.models

    energy_edges = MapAxis.from_energy_bounds("1 TeV", "30 TeV", nbin=7).edges

    fpe = FluxPointsEstimator(
        energy_edges=energy_edges, source="source-gc", selection_optional="all"
    )
    return fpe.run(datasets=[stacked_dataset])


def fit_model(datasets):
    spectral_model = PowerLawSpectralModel(
        index=2, amplitude=1e-11 * u.Unit("cm-2 s-1 TeV-1"), reference=1 * u.TeV
    )

    model = SkyModel(spectral_model=spectral_model, name="source-gc")

    datasets.models = model

    fit = Fit()
    result = fit.run(datasets=datasets)
    return datasets.models


if __name__ == "__main__":
    path = Path(".")

    filename = path / "stacked-counts.fits"
    observations = get_observations()
    counts = make_counts_image(observations)
    log.info(f"Writing {filename}")
    counts.write(filename, overwrite=True)

    filename = path / "datasets/datasets.yaml"
    filename.parent.mkdir(exist_ok=True)
    observations = get_observations()
    datasets = make_datasets_spectral(observations)
    log.info(f"Writing {filename}")
    datasets.write(filename, overwrite=True)

    filename = path / "best-fit-model.yaml"
    models = fit_model(datasets)
    log.info(f"Writing {filename}")
    models.write(filename, overwrite=True, write_covariance=False)

    filename = path / "flux-points.fits"
    fp = make_flux_points(datasets)
    log.info(f"Writing {filename}")
    fp.write(filename, overwrite=True)
