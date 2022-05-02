# reduce the MAGIC data to OGIP files for the 1D analysis
import logging
import astropy.units as u
from pathlib import Path
from astropy.coordinates import SkyCoord
from regions import PointSkyRegion

# gammapy imports
from gammapy.data import DataStore
from gammapy.maps import MapAxis
from gammapy.maps import RegionGeom
from gammapy.makers import (
    SpectrumDatasetMaker,
    WobbleRegionsFinder,
    ReflectedRegionsBackgroundMaker,
    SafeMaskMaker
)
from gammapy.estimators import FluxPoints, FluxPointsEstimator
from gammapy.datasets import Datasets, SpectrumDataset, FluxPointsDataset
from gammapy.modeling import Fit
from gammapy.modeling.models import Models, create_crab_spectral_model


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def load_fermi_datasets():
    """Load the `MapDataset` already prepared for the Fermi-LAT data"""
    return Datasets.read("input/fermi/Fermi-LAT-3FHL_datasets.yaml")


def reduce_magic_data():
    """Reduce the MAGIC DL3 files to `SpectrumDatasetOnOff`"""
    data_store = DataStore.from_dir("input/magic")
    observations = data_store.get_observations(required_irf=["aeff", "edisp", "rad-max"])

    # adopt the same energy axes used for flute and DL3 production
    energy_axis = MapAxis.from_energy_bounds(
        10, 1e5, nbin=20, per_decade=False, unit="GeV", name="energy"
    )
    energy_true_axis = MapAxis.from_energy_bounds(
        10, 1e5, nbin=28, per_decade=False, unit="GeV", name="energy_true"
    )

    # create a point-like geometry for the centre of the ON region
    target_position = SkyCoord(ra=83.63, dec=22.01, unit="deg", frame="icrs")
    on_center = PointSkyRegion(target_position)
    geom = RegionGeom.create(region=on_center, axes=[energy_axis])

    # spectrum dataset and its maker
    dataset_empty = SpectrumDataset.create(geom=geom, energy_axis_true=energy_true_axis)
    dataset_maker = SpectrumDatasetMaker(
        containment_correction=False, selection=["counts", "exposure", "edisp"]
    )

    # background and safe mask makers
    region_finder = WobbleRegionsFinder(n_off_regions=1)
    bkg_maker = ReflectedRegionsBackgroundMaker(region_finder=region_finder)
    # use the energy threshold specified in the DL3 files
    safe_mask_masker = SafeMaskMaker(methods=["aeff-default"])

    datasets = Datasets()

    for obs in observations:

        # fill the ON counts
        dataset = dataset_maker.run(dataset_empty.copy(name=f"{obs.obs_id}"), obs)

        # fill the OFF counts and set energy threshold
        dataset_on_off = bkg_maker.run(dataset, obs)
        dataset_on_off = safe_mask_masker.run(dataset_on_off, obs)

        datasets.append(dataset_on_off)

    return datasets


def load_hawc_flux_points():
    """Load the HAWC flux points in a FluxPointsDataset"""
    flux_points_hawc = FluxPoints.read(
        "input/hawc/HAWC19_flux_points.fits",
        reference_model=create_crab_spectral_model("meyer"),
    )
    dataset_hawc = FluxPointsDataset(data=flux_points_hawc, name="HAWC")

    return dataset_hawc


def compute_flux_points(datasets, energy_edges, filename):
    """Compute and save the flux points for a given dataset"""
    flux_points = FluxPointsEstimator(
        energy_edges=energy_edges,
        source="Crab Nebula",
        selection_optional=["ul"]
    ).run([datasets])

    Path(filename).parent.mkdir(exist_ok=True, parents=True)
    log.info(f"Writing {filename}")
    flux_points.write(filename, overwrite=True)


def fit_joint_dataset(datasets, models, filename):
    """Fit the model to the joint datasets and save the output"""
    datasets.models = models

    fit = Fit()
    fit.run(datasets=datasets)

    # write the best fit result
    Path(filename).parent.mkdir(exist_ok=True, parents=True)
    log.info(f"Writing {filename}")
    models.write(filename, overwrite=True, write_covariance=True)


if __name__ == "__main__":
    # load the three instruments datasets
    fermi_dataset = load_fermi_datasets()
    magic_datasets = reduce_magic_data()
    hawc_dataset = load_hawc_flux_points()

    # join them in a single Datasets
    datasets = Datasets()
    datasets.append(hawc_dataset)
    datasets.extend(fermi_dataset)
    datasets.extend(magic_datasets)

    # load the model
    models = Models.read("input/fermi/Fermi-LAT-3FHL_models.yaml")

    fit_joint_dataset(datasets, models, "results/crab_multi_instrument_fit.yaml")

    # now compute and store the Fermi-LAT and MAGIC flux points
    energy_edges_fermi =  MapAxis.from_energy_bounds("10 GeV", "2 TeV", nbin=5).edges
    compute_flux_points(
        datasets["Fermi-LAT"],
        energy_edges_fermi,
        "datasets/flux_points/crab_fermi_flux_points.fits"
    )

    # stack the MAGIC dataset and add the model before feeding it to the FluxPointsEstimator
    magic_datasets_to_fp = magic_datasets.stack_reduce()
    magic_datasets_to_fp.models = models
    energy_edges_magic = MapAxis.from_energy_bounds("80 GeV", "20 TeV", nbin=10).edges
    compute_flux_points(
        magic_datasets_to_fp,
        energy_edges_magic,
        "datasets/flux_points/crab_magic_flux_points.fits"
    )
