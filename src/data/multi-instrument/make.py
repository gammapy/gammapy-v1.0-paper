# reduce the MAGIC data to OGIP files for the 1D analysis
import logging
import time
from pathlib import Path

import astropy.units as u
import numpy as np
from astropy.constants import c
from astropy.coordinates import SkyCoord
from naima.models import LogParabola
from naima.radiative import InverseCompton, Synchrotron
from regions import PointSkyRegion

# gammapy imports
from gammapy.data import DataStore
from gammapy.datasets import Datasets, FluxPointsDataset, SpectrumDataset
from gammapy.estimators import FluxPoints, FluxPointsEstimator
from gammapy.makers import (
    ReflectedRegionsBackgroundMaker,
    SpectrumDatasetMaker,
    WobbleRegionsFinder,
)
from gammapy.maps import MapAxis, RegionGeom
from gammapy.modeling import Fit
from gammapy.modeling.models import (
    Models,
    NaimaSpectralModel,
    SkyModel,
    create_crab_spectral_model,
)
from gammapy.utils.scripts import read_yaml

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class CrabInverseComptonSpectralModel(NaimaSpectralModel):
    """A `~gammapy.modeling.models.NaimaSpectralModel` wrapping
    the inverse Compton radiative scenario defined for the Crab Nebula in the
    naima docs https://naima.readthedocs.io/en/latest/examples.html#crabssc.

    A LogParabola is assumed to describe the electron distribution.
    """

    def __init__(self, amplitude, e_0, alpha, beta):
        particle_distribution = LogParabola(amplitude, e_0, alpha, beta)

        synch = Synchrotron(
            particle_distribution, B=125 * u.uG, Eemin=0.1 * u.GeV, Eemax=50 * u.PeV
        )

        # compute photon density spectrum from synchrotron emission assuming R=2.1 pc
        Rpwn = 2.1 * u.pc
        Esy = np.logspace(-7, 9, 100) * u.eV
        Lsy = synch.flux(Esy, distance=0 * u.cm)  # use distance 0 to get luminosity
        phn_sy = Lsy / (4 * np.pi * Rpwn**2 * c) * 2.24

        radiative_model = InverseCompton(
            particle_distribution,
            seed_photon_fields=[
                "CMB",
                ["FIR", 70 * u.K, 0.5 * u.eV / u.cm**3],
                ["NIR", 5000 * u.K, 1 * u.eV / u.cm**3],
                ["SSC", Esy, phn_sy],
            ],
            Eemin=0.1 * u.GeV,
            Eemax=50 * u.PeV,
        )

        super().__init__(radiative_model, distance=6.523 * u.lyr)

    @classmethod
    def from_yaml(cls, yaml_file):
        """Read this spectral model from a `.yaml` file.
        Cannot use `Models.read` not even after adding this class to the
        `SPECTRAL_MODEL_REGISTRY`.
        """
        results = read_yaml(yaml_file)
        amplitude = results["components"][0]["spectral"]["parameters"][0][
            "value"
        ] * u.Unit(results["components"][0]["spectral"]["parameters"][0]["unit"])
        e_0 = results["components"][0]["spectral"]["parameters"][1]["value"] * u.Unit(
            results["components"][0]["spectral"]["parameters"][1]["unit"]
        )
        alpha = results["components"][0]["spectral"]["parameters"][2]["value"]
        beta = results["components"][0]["spectral"]["parameters"][3]["value"]

        return cls(amplitude, e_0, alpha, beta)


def load_fermi_datasets():
    """Load the `MapDataset` already prepared for the Fermi-LAT data"""
    return Datasets.read("../input/fermi-3fhl-crab/Fermi-LAT-3FHL_datasets.yaml")


def reduce_magic_data():
    """Reduce the MAGIC DL3 files to `SpectrumDatasetOnOff`"""
    e_min = 80 * u.GeV
    e_max = 20 * u.TeV

    data_store = DataStore.from_dir("../input/magic/rad_max/data")
    observations = data_store.get_observations(
        required_irf=["aeff", "edisp", "rad_max"]
    )

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

    datasets = Datasets()

    for obs in observations:
        # fill the ON counts
        dataset = dataset_maker.run(dataset_empty.copy(name=f"{obs.obs_id}"), obs)
        # fill the OFF counts and set the energy range appropiate for the fit
        dataset_on_off = bkg_maker.run(dataset, obs)
        dataset_on_off.mask_fit = dataset.counts.geom.energy_mask(e_min, e_max)

        datasets.append(dataset_on_off)

    return datasets


def load_hawc_flux_points():
    """Load the HAWC flux points in a FluxPointsDataset"""
    flux_points_hawc = FluxPoints.read(
        "../input/hawc_crab/HAWC19_flux_points.fits",
        reference_model=create_crab_spectral_model("meyer"),
    )
    dataset_hawc = FluxPointsDataset(data=flux_points_hawc, name="HAWC")

    return dataset_hawc


def compute_flux_points(datasets, energy_edges, filename, source):
    """Compute and save the flux points for a given dataset"""
    flux_points = FluxPointsEstimator(
        energy_edges=energy_edges, source=source, selection_optional=["ul"]
    ).run([datasets])

    Path(filename).parent.mkdir(exist_ok=True, parents=True)
    log.info(f"Writing {filename}")
    flux_points.write(filename, overwrite=True)


def fit_joint_dataset(datasets, models, filename):
    """Fit the model to the joint datasets and save the output"""
    datasets.models = models

    fit = Fit()
    result = fit.run(datasets=datasets)

    print(result)
    print(datasets.models.parameters.to_table())

    # write the best fit result
    Path(filename).parent.mkdir(exist_ok=True, parents=True)
    log.info(f"Writing {filename}")
    models.write(filename, overwrite=True, write_covariance=True)


if __name__ == "__main__":
    # load the three instruments datasets
    t_start = time.time()
    fermi_dataset = load_fermi_datasets()
    magic_datasets = reduce_magic_data()
    hawc_dataset = load_hawc_flux_points()

    # join them in a single Datasets
    datasets = Datasets()
    datasets.append(hawc_dataset)
    datasets.extend(fermi_dataset)
    datasets.extend(magic_datasets)

    # load the model
    models = Models.read("../input/fermi-3fhl-crab/Fermi-LAT-3FHL_models.yaml")
    models[0].spectral_model.amplitude.value = 1e-11
    models[0].spectral_model.reference.value = 500
    models[0].spectral_model.reference.unit = u.GeV
    models[0].spectral_model.alpha.min = 1.0
    models[0].spectral_model.alpha.max = 4.0
    models[0].spectral_model.beta.min = 0.0
    models[0].spectral_model.beta.max = 1.0

    # create a model only with the Log Parabola to be applied to the MAGIC data
    model_magic = SkyModel(
        spectral_model=models[0].spectral_model,
        name="crab-nebula-spectrum-only",
        datasets_names=["5029747", "5029748"],
    )
    # add it to the list of models
    models.append(model_magic)
    # the first SkyModel, with the source definition is meant only for HAWC and Fermi-LAT data
    models[0].datasets_names = ["Fermi-LAT", "HAWC"]

    fit_joint_dataset(
        datasets, models, "results/crab_multi_instrument_fit_lp_model.yaml"
    )

    # now compute and store the Fermi-LAT and MAGIC flux points
    energy_edges_fermi = MapAxis.from_energy_bounds("10 GeV", "2 TeV", nbin=5).edges
    compute_flux_points(
        datasets["Fermi-LAT"],
        energy_edges_fermi,
        "datasets/flux_points/crab_fermi_flux_points.fits",
        "Crab Nebula",
    )

    # stack the MAGIC dataset and add the model before feeding it to the FluxPointsEstimator
    magic_datasets_to_fp = magic_datasets.stack_reduce(name="magic_stacked")
    # the previous magic_model is set to work only with runs 5029747 and 5029748
    model_magic.datasets_names = "magic_stacked"
    magic_datasets_to_fp.models = [model_magic]
    energy_edges_magic = MapAxis.from_energy_bounds("80 GeV", "20 TeV", nbin=6).edges
    compute_flux_points(
        magic_datasets_to_fp,
        energy_edges_magic,
        "datasets/flux_points/crab_magic_flux_points.fits",
        "crab-nebula-spectrum-only",
    )

    t_stop = time.time()

    path = Path(".")
    with (path / "../run-times.csv").open("a") as fh:
        fh.write(f"multi-istrument-example: {t_stop - t_start}\n")

    # fit with the naima IC model
    naima_ic_spectral_model = CrabInverseComptonSpectralModel(
        amplitude=1e32 / u.eV, alpha=2.1, e_0=100 * u.GeV, beta=0.1
    )
    naima_ic_spectral_model.parameters["e_0"].frozen = True

    # change the spectral models
    models[0].spectral_model = naima_ic_spectral_model
    models[2].spectral_model = naima_ic_spectral_model

    fit_joint_dataset(
        datasets, models, "results/crab_multi_instrument_fit_naima_ic_model.yaml"
    )

    t_stop = time.time()

    path = Path(".")
    with (path / "../run-times.csv").open("a") as fh:
        fh.write(f"multi-istrument-naima-example: {t_stop - t_start}\n")
