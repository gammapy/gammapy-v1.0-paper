# reduce the MAGIC data to OGIP files for the 1D analysis
import logging
from pathlib import Path
from astropy.coordinates import SkyCoord
from regions import PointSkyRegion

# gammapy imports
from gammapy.data import DataStore
from gammapy.maps import MapAxis
from gammapy.maps import RegionGeom
from gammapy.datasets import SpectrumDataset
from gammapy.makers import (
    SpectrumDatasetMaker,
    WobbleRegionsFinder,
    ReflectedRegionsBackgroundMaker,
    SafeMaskMaker
)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# reduce the MAGIC data to OGIP files
data_store = DataStore.from_dir("input/magic")
observations = data_store.get_observations(required_irf=["aeff", "edisp"])

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
dataset_empty = SpectrumDataset.create(
    geom=geom, energy_axis_true=energy_true_axis
)
dataset_maker = SpectrumDatasetMaker(
    containment_correction=False, selection=["counts", "exposure", "edisp"]
)

# background and safe mask makers
region_finder = WobbleRegionsFinder(n_off_regions=1)
bkg_maker = ReflectedRegionsBackgroundMaker(region_finder=region_finder)
safe_mask_maker = SafeMaskMaker(method=["aeff-default"])

for obs in observations:

    # fill the ON counts
    dataset = dataset_maker.run(dataset_empty.copy(name=f"{obs.obs_id}"), obs)

    # fill the OFF counts and set threshold
    dataset_on_off = bkg_maker.run(dataset, obs)
    dataset_on_off = safe_mask_maker.run(dataset, obs)

    # write the results
    path = Path(f"datasets/magic/")
    path.mkdir(exist_ok=True, parents=True)
    dataset_on_off.write(path / f"pha_obs_{obs.obs_id}.fits", overwrite=True)
