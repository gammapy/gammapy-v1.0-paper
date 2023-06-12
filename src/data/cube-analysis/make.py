#!/usr/bin/env python
import codecs
import logging
import time
from pathlib import Path

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from regions import CircleSkyRegion

from gammapy.data import DataStore
from gammapy.datasets import MapDataset
from gammapy.estimators import ExcessMapEstimator
from gammapy.makers import MapDatasetMaker, SafeMaskMaker
from gammapy.maps import Map, MapAxis, WcsGeom
from gammapy.modeling import Fit
from gammapy.modeling.models import (
    GaussianSpatialModel,
    LogParabolaSpectralModel,
    PointSpatialModel,
    PowerLawSpectralModel,
    ShellSpatialModel,
    SkyModel,
)

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

ENERGY_AXIS = MapAxis.from_edges(
    np.logspace(-1.0, 1.0, 20), unit="TeV", name="energy", interp="log"
)

ENERGY_AXIS_TRUE = MapAxis.from_edges(
    np.logspace(-1.0, 1.5, 40), unit="TeV", name="energy_true", interp="log"
)

GEOM = WcsGeom.create(
    skydir=(0, 0), npix=(350, 350), binsz=0.02, frame="galactic", axes=[ENERGY_AXIS]
)

REGION = CircleSkyRegion(
    center=SkyCoord(0, 0, frame="galactic", unit="deg"), radius=0.5 * u.deg
)


def get_observations():
    # Select observations
    data_store = DataStore.from_dir("../input/cta-1dc/index/gps")
    obs_id = [110380, 111140, 111159]
    return data_store.get_observations(obs_id)


def make_map_dataset(observations):
    stacked = MapDataset.create(geom=GEOM, energy_axis_true=ENERGY_AXIS_TRUE)
    dataset_maker = MapDatasetMaker(
        selection=["background", "exposure", "psf", "edisp"]
    )
    safe_mask_masker = SafeMaskMaker(
        methods=["offset-max", "aeff-default"], offset_max=2.5 * u.deg
    )

    for obs in observations:
        cutout = stacked.cutout(obs.pointing_radec, width="5 deg")
        dataset = dataset_maker.run(cutout, obs)
        dataset = safe_mask_masker.run(dataset, obs)
        stacked.stack(dataset)

    return stacked


def simulate_counts(stacked):
    spectral_model_1 = PowerLawSpectralModel(
        index=1.95, amplitude="5e-12 cm-2 s-1 TeV-1", reference="1 TeV"
    )
    spatial_model_1 = PointSpatialModel(lon_0="0 deg", lat_0="0 deg", frame="galactic")
    model_1 = SkyModel(spectral_model_1, spatial_model_1, name="source 1")

    spectral_model_2 = LogParabolaSpectralModel(
        alpha=2.1, beta=0.01, amplitude="1e-11 cm-2 s-1 TeV-1", reference="1 TeV"
    )
    spatial_model_2 = GaussianSpatialModel(
        lon_0="0.4 deg", lat_0="0.15 deg", sigma=0.2 * u.deg, frame="galactic"
    )
    model_2 = SkyModel(spectral_model_2, spatial_model_2, name="source 2")

    spectral_model_3 = PowerLawSpectralModel(
        index=2.7, amplitude="5e-11 cm-2 s-1 TeV-1", reference="1 TeV"
    )
    spatial_model_3 = ShellSpatialModel(
        lon_0="0.06 deg",
        lat_0="0.6 deg",
        radius=0.6 * u.deg,
        width=0.3 * u.deg,
        frame="galactic",
    )
    model_3 = SkyModel(spectral_model_3, spatial_model_3, name="source 3")

    stacked.models = [model_1, model_2, model_3]

    stacked.fake(0)

    return stacked


def make_significance_map(stacked):
    stacked.models = []
    e = ExcessMapEstimator("0.1deg")
    result = e.run(stacked)
    return result["sqrt_ts"]


def fit_models(stacked):
    spectral_model_fit_1 = PowerLawSpectralModel(
        index=2, amplitude="0.5e-12 cm-2 s-1 TeV-1", reference="1 TeV"
    )
    spectral_model_fit_1.amplitude.min = 0
    spatial_model_fit_1 = PointSpatialModel(
        lon_0="0 deg", lat_0="0 deg", frame="galactic"
    )
    model_fit_1 = SkyModel(
        spectral_model_fit_1, spatial_model_fit_1, name="source 1 fit"
    )

    spectral_model_fit_2 = LogParabolaSpectralModel(
        alpha=2, beta=0.01, amplitude="1e-11 cm-2 s-1 TeV-1", reference="1 TeV"
    )
    spectral_model_fit_2.amplitude.min = 0
    spectral_model_fit_2.beta.min = 0
    spatial_model_fit_2 = GaussianSpatialModel(
        lon_0="0.4 deg", lat_0="0.15 deg", sigma=0.2 * u.deg, frame="galactic"
    )
    model_fit_2 = SkyModel(
        spectral_model_fit_2, spatial_model_fit_2, name="source 2 fit"
    )

    spectral_model_fit_3 = PowerLawSpectralModel(
        index=2, amplitude="3e-11 cm-2 s-1 TeV-1", reference="1 TeV"
    )
    spectral_model_fit_3.amplitude.min = 0

    spatial_model_fit_3 = ShellSpatialModel(
        lon_0="0.06 deg",
        lat_0="0.6 deg",
        radius=0.5 * u.deg,
        width=0.2 * u.deg,
        frame="galactic",
    )
    model_fit_3 = SkyModel(
        spectral_model_fit_3, spatial_model_fit_3, name="source 3 fit"
    )

    stacked.models = [model_fit_1, model_fit_2, model_fit_3]
    fit = Fit()
    result = fit.run(stacked)
    return stacked.models


def make_residual_map(stacked, models):
    stacked.models = models
    e = ExcessMapEstimator("0.1deg")
    result = e.run(stacked)
    return result["sqrt_ts"]


def make_contribution_to_region(stacked, models, region):
    spec = stacked.to_spectrum_dataset(region, containment_correction=True)

    so1 = SkyModel(models[0].spectral_model)
    spec.models = [so1]
    npred_1 = Map.from_geom(spec.counts.geom)
    npred_1.data = spec.npred_signal().data

    so2 = SkyModel(models[1].spectral_model)
    spec.models = [so2]
    npred_2 = Map.from_geom(spec.counts.geom)
    npred_2.data = spec.npred_signal().data
    npred_2.data *= (
        models[1].spatial_model.integrate_geom(spec.counts.geom).quantity.to_value("")
    )

    so3 = SkyModel(models[2].spectral_model)
    spec.models = [so3]
    npred_3 = Map.from_geom(spec.counts.geom)
    npred_3.data = spec.npred_signal().data
    npred_3.data *= (
        models[2].spatial_model.integrate_geom(spec.counts.geom).quantity.to_value("")
    )

    return spec.excess, npred_1, npred_2, npred_3


if __name__ == "__main__":
    t_start = time.time()
    path = Path(".")
    observations = get_observations()
    stacked = make_map_dataset(observations)
    stacked = simulate_counts(stacked)

    filename = path / "significance_map.fits"
    ts_map = make_significance_map(stacked)
    log.info(f"Writing {filename}")
    ts_map.write(filename, overwrite=True)

    filename = path / "best-fit-model.yaml"
    models = fit_models(stacked)
    log.info(f"Writing {filename}")
    models.write(filename, overwrite=True, write_covariance=False)

    filename = path / "residual_map.fits"
    residual_map = make_residual_map(stacked, models)
    log.info(f"Writing {filename}")
    residual_map.write(filename, overwrite=True)

    excess, npred_1, npred_2, npred_3 = make_contribution_to_region(
        stacked, models, REGION
    )

    filename_excess = path / "excess_counts.fits"
    log.info(f"Writing {filename_excess}")
    excess.write(filename_excess, format="ogip", overwrite=True)

    filename_source1 = path / "npred_1.fits"
    log.info(f"Writing {filename_source1}")
    npred_1.write(filename_source1, format="ogip", overwrite=True)

    filename_source2 = path / "npred_2.fits"
    log.info(f"Writing {filename_source2}")
    npred_2.write(filename_source2, format="ogip", overwrite=True)

    filename_source3 = path / "npred_3.fits"
    log.info(f"Writing {filename_source3}")
    npred_3.write(filename_source3, format="ogip", overwrite=True)

    t_stop = time.time()

    with (path / "../run-times.csv").open("a") as fh:
        fh.write(f"cube-example: {t_stop - t_start}\n")
