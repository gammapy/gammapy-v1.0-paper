# relative import "from ..data.multi-instrument" will not work because of the
# "-" in "multi-instrument"... this is the easiest trick I found
import sys

import astropy.units as u
import config
import matplotlib.pyplot as plt
import numpy as np
from astropy.constants import c

from gammapy.estimators import FluxPoints
from gammapy.modeling.models import SPECTRAL_MODEL_REGISTRY, Models

sys.path.append("../data/multi-instrument")
from make import CrabInverseComptonSpectralModel

sed_x_label = "Energy / TeV"
sed_y_label = (
    r"$E^2\,{\rm d}\phi/{\rm d}E\,/\,({\rm erg}\,{\rm cm}^{-2}\,{\rm s}^{-1})$"
)

figsize = config.FigureSizeAA(aspect_ratio=1.618, width_aa="intermediate")
fig = plt.figure(figsize=figsize.inch)
ax = fig.add_axes([0.15, 0.15, 0.84, 0.84])

# load the flux points and plot them
fermi_flux_points = FluxPoints.read(
    "../data/multi-instrument/datasets/flux_points/crab_fermi_flux_points.fits"
)
magic_flux_points = FluxPoints.read(
    "../data/multi-instrument/datasets/flux_points/crab_magic_flux_points.fits"
)
hawc_flux_points = FluxPoints.read("../data/input/hawc_crab/HAWC19_flux_points.fits")

# load the best-fit models
#  - log parabola
lp_models = Models.read(
    "../data/multi-instrument/results/crab_multi_instrument_fit_lp_model.yaml"
)
crab_lp = lp_models["Crab Nebula"].spectral_model

# - naima IC model
crab_naima_ic = CrabInverseComptonSpectralModel.from_yaml(
    "../data/multi-instrument/results/crab_multi_instrument_fit_naima_ic_model.yaml"
)

# make the plot
plot_kwargs = {
    "energy_bounds": [0.01, 300] * u.TeV,
    "sed_type": "e2dnde",
    "yunits": u.Unit("erg cm-2 s-1"),
    "xunits": u.TeV,
}

fermi_flux_points.plot(ax=ax, sed_type="e2dnde", label="Fermi-LAT")
magic_flux_points.plot(ax=ax, sed_type="e2dnde", label="MAGIC", marker="v")
hawc_flux_points.plot(ax=ax, sed_type="e2dnde", label="HAWC", marker="s")

crab_lp.plot(
    ax=ax,
    ls="-",
    lw=1.5,
    color="k",
    label="joint fit, log parabola model",
    **plot_kwargs
)
crab_lp.plot_error(ax=ax, facecolor="k", alpha=0.4, **plot_kwargs)

crab_naima_ic.plot(
    ax=ax,
    ls="--",
    lw=1.5,
    label="joint fit, naima inverse Compton model",
    **plot_kwargs
)

ax.set_xlim(plot_kwargs["energy_bounds"])
ax.set_xlabel(sed_x_label)
ax.set_ylabel(sed_y_label)
ax.legend(loc="lower left")
fig.savefig("multi_instrument_analysis.pdf")
