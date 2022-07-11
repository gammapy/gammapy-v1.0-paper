from gammapy.makers import (
    MapDatasetMaker,
    FoVBackgroundMaker,
    SafeMaskMaker,
)
from gammapy.data import DataStore
from gammapy.maps import MapAxis, WcsGeom
from gammapy.datasets import MapDataset
from regions import CircleSkyRegion
import astropy.units as u

data_store = DataStore.from_dir("$GAMMAPY_DATA/hess-dl3-dr1")

obs = data_store.obs(23523)

energy_axis = MapAxis.from_energy_bounds(1.0, 10.0, 6, unit="TeV")
geom = WcsGeom.create(
    skydir=(83.633, 22.014),
    width=(2, 2),
    axes=[energy_axis],
)

circle = CircleSkyRegion(
    center=geom.center_skydir, radius=0.2 * u.deg
)
exclusion_mask = ~geom.region_mask(regions=[circle],
                                   inside=False)

empty = MapDataset.create(geom=geom)

maker = MapDatasetMaker()
mask_maker = SafeMaskMaker(methods=["offset-max", "aeff-default"],
                           offset_max="2.3 deg")
bkg_maker = FoVBackgroundMaker(method="scale",
                               exclusion_mask=exclusion_mask)

dataset = maker.run(empty, obs)
dataset = mask_maker.run(dataset, obs)
print(dataset)