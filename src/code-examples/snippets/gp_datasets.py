from astropy.coordinates import SkyCoord
from gammapy.maps import WcsGeom
from gammapy.datasets import MapDataset

skydir = SkyCoord("0d", "0d")
geom = WcsGeom.create(
	skydir=skydir, width="5 deg", binsz="0.2 deg"
)

dataset = MapDataset.create(
	geom=geom, name="my-dataset"
)
