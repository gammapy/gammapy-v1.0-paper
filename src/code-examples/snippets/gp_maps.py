from gammapy.maps import Map
from astropy.coordinates import SkyCoord
from astripy import units as u

skydir = SkyCoord("0d", "5d", frame="galactic")

# Create a WCS Map
m_wcs = Map.create(
    binsz=0.1,
    map_type="wcs",
    skydir=skydir,
    width=[10.0, 8.0] * u.deg
)


# Create a HPX Map
m_hpx = Map.create(
    binsz=0.1,
    map_type="hpx",
    skydir=skydir,
    width=10.0 * u.deg
)
