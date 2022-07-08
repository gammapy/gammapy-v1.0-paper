from gammapy.makers import (
    MapDatasetMaker,
    FoVBackgroundMaker,
    SafeMaskMaker,
)
from gammapy.data import Observation

observation = Observation.read()

maker = MapDatasetMaker()

bkg_maker = FoVBackgroundMaker()

mask_maker = SafeMaskMaker(
    method=["offset-max"], max_offset="2.5 deg"
)

dataset = maker.run(dataset, observation)
dataset = mask_maker.run(dataset, observation)
dataset = bkg_maker.run(dataset, observation)
print(dataset)
