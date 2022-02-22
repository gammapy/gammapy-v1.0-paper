import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.time import Time
from regions import CircleSkyRegion
from astropy.coordinates import Angle
from gammapy.data import DataStore
from gammapy.datasets import SpectrumDataset, Datasets
from gammapy.modeling.models import PowerLawSpectralModel, SkyModel
from gammapy.maps import MapAxis, RegionGeom
from gammapy.estimators import LightCurveEstimator
from gammapy.makers import (
    SpectrumDatasetMaker,
    ReflectedRegionsBackgroundMaker,
    SafeMaskMaker,
)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def get_observations():
    data_store = DataStore.from_dir("data/")
    obs_table = data_store.obs_table
    obs_table_seclected = obs_table[obs_table["TARGET_TAG"]=="pks2155_flare"]
    obs_ids = obs_table_seclected["OBS_ID"]
    observations = data_store.get_observations(obs_ids)
    return observations

def split_observations(observations):
    t0 = Time("2006-07-29T20:30")
    duration = 10 * u.min
    n_time_bins = 35
    times = t0 + np.arange(n_time_bins) * duration
    time_intervals = [
        Time([tstart, tstop]) for tstart, tstop in zip(times[:-1], times[1:])
    ]
    short_observations = observations.select_time(time_intervals)
    return time_intervals, short_observations


def data_reduction(short_observations):
    energy_axis = MapAxis.from_energy_bounds("0.4 TeV", "20 TeV", nbin=10)
    energy_axis_true = MapAxis.from_energy_bounds(
        "0.1 TeV", "40 TeV", nbin=20, name="energy_true"
    )

    target_position = target_position = SkyCoord(
        329.71693826 * u.deg, -30.2255890 * u.deg, frame="icrs"
    )
    on_region_radius = Angle("0.11 deg")
    on_region = CircleSkyRegion(center=target_position, radius=on_region_radius)

    geom = RegionGeom.create(region=on_region, axes=[energy_axis])
    dataset_maker = SpectrumDatasetMaker(
        containment_correction=True, selection=["counts", "exposure", "edisp"]
    )
    bkg_maker = ReflectedRegionsBackgroundMaker()
    safe_mask_masker = SafeMaskMaker(methods=["aeff-max"], aeff_percent=10)

    datasets = Datasets()

    dataset_empty = SpectrumDataset.create(
        geom=geom, energy_axis_true=energy_axis_true
    )

    for obs in short_observations:
        dataset = dataset_maker.run(dataset_empty.copy(), obs)

        dataset_on_off = bkg_maker.run(dataset, obs)
        dataset_on_off = safe_mask_masker.run(dataset_on_off, obs)
        datasets.append(dataset_on_off)
    return datasets

def light_curve(datasets, time_intervals):
    spectral_model = PowerLawSpectralModel(
        index=3.4, amplitude=2e-11 * u.Unit("1 / (cm2 s TeV)"), reference=1 * u.TeV
    )
    spectral_model.parameters["index"].frozen = False

    sky_model = SkyModel(
        spatial_model=None, spectral_model=spectral_model, name="pks2155"
    )
    datasets.models = sky_model
    lc_maker_1d = LightCurveEstimator(
        energy_edges=[0.5, 1.5, 20] * u.TeV,
        source="pks2155",
        time_intervals=time_intervals,
        selection_optional=None,
    )
    lc_1d = lc_maker_1d.run(datasets)
    return lc_1d


if __name__ == "__main__":
    path = Path(".")
    filename = path / "pks2155_flare_lc.fits.gz"

    observations = get_observations()
    time_intervals, short_observations = split_observations(observations)
    datasets = data_reduction(short_observations)
    lc = light_curve(datasets, time_intervals)
    log.info(f"Writing {filename}")
    lc.write(filename, format="lightcurve", overwrite=True)

