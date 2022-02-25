from gammapy.maps import Map, MapAxis
from astropy.coordinates import SkyCoord
from astropy import units as u

skydir = SkyCoord("0d", "5d", frame="galactic")
energy_axis = MapAxis.from_bounds(lo_bnd=0.1, hi_bnd=100, 
              nbin=5, unit='TeV', interp='log', name='energy')

# Create a WCS Map
m_wcs = Map.create(
    binsz=0.1,
    map_type="wcs",
    skydir=skydir,
    width=[10.0, 8.0] * u.deg,
    axes = [energy_axis])


# Create a HEALPix Map
m_hpx = Map.create(
    binsz=0.1,
    map_type="hpx",
    skydir=skydir,
    width=10.0 * u.deg,
    axes = [energy_axis])

# Create a region map
region = "galactic;circle(0, 5, 1)"
m_region = Map.create(
    region = region,
    map_type='region',
    axes = [energy_axis])
