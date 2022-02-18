from pathlib import Path
import logging
import matplotlib.pyplot as plt
from gammapy.estimators import FluxMaps
import astropy.units as u
from astropy.io import fits
import config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def plot_sqrt_ts_maps(maps):
    figsize = config.FigureSizeAA(aspect_ratio=3, width_aa="two-column")
    fig = plt.figure(figsize=figsize.inch)

    projection = maps.sqrt_ts.geom.wcs
    rect = (0.08, 0.12, 0.4, 0.8)
    ax_1 = fig.add_axes(rect=rect, projection=projection)

    rect = (0.49, 0.12, 0.4, 0.8)
    ax_2 = fig.add_axes(rect=rect, projection=projection)

    rect = (0.915, 0.22, 0.02, 0.6)
    cax = fig.add_axes(rect=rect)

    kwargs = {}
    kwargs.setdefault("interpolation", "nearest")
    kwargs.setdefault("origin", "lower")
    kwargs.setdefault("cmap", "afmhot")
    kwargs.setdefault("vmin", -2)
    kwargs.setdefault("vmax", 14)

    sqrt_ts_1 = maps.sqrt_ts.get_image_by_idx((0,))
    im = ax_1.imshow(sqrt_ts_1.data, **kwargs)
    ax_1.set_title("Energy 10 GeV - 60 GeV")
    lon, lat = ax_1.coords["glon"], ax_1.coords["glat"]
    lon.set_axislabel("Galactic Longitude")
    lat.set_axislabel("Galactic Latitude")
    lon.set_ticks_position('b')
    lat.set_ticks_position('l')

    sqrt_ts_2 = maps.sqrt_ts.get_image_by_idx((1,))
    im = ax_2.imshow(sqrt_ts_2.data, **kwargs)
    ax_2.set_title("Energy 60 GeV - 2000 GeV")
    lon, lat = ax_2.coords["glon"], ax_2.coords["glat"]
    lon.set_axislabel("Galactic Longitude")
    lat.set_ticklabel_visible(False)
    lon.set_ticks_position('b')
    lat.set_ticks_position('r')
    lon.set_ticks([5, 0, 355, 350] * u.deg)
    lon.set_major_formatter("dd")

    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label("sqrt(TS)", labelpad=0)
    filename = "fermi_ts_map.pdf"
    log.info(f"Writing {filename}")
    plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    filename = Path("../data/fermi-ts-map/") / "fermi-ts-maps.fits"
    log.info(f"Reading {filename}")
    hdulist = fits.open(filename)
    hdulist[0].header["MODEL"] = "../data/fermi-ts-map/fermi-ts-maps.fits_model.yaml"
    maps = FluxMaps.from_hdulist(hdulist=hdulist)
    plot_sqrt_ts_maps(maps=maps)
