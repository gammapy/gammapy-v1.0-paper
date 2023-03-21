import logging

import config
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from astropy import units as u

from gammapy.data import DataStore
from gammapy.irf import PSFMap, load_irf_dict_from_file
from gammapy.maps import Map

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

fermi_livetime = 5e7 * u.s
hawc_lifetime = 6.4 * u.h

offset = [1] * u.deg

#data_store = DataStore.from_dir("../data/input/cta-1dc/index/gps")
#obs_cta = data_store.obs(110380)
cta_north = ("../data/cta-caldb/Prod5-North-20deg-AverageAz-4LSTs09MSTs.180000s-v0.1.fits")
cta_south = ("../data/cta-caldb/Prod5-South-20deg-AverageAz-14MSTs37SSTs.180000s-v0.1.fits")
irf_cta_north = load_irf_dict_from_file(cta_north)
irf_cta_south = load_irf_dict_from_file(cta_south)

data_store = DataStore.from_dir("../data/input/hess-dl3-dr1/")
obs_hess = data_store.obs(33787)

data_store = DataStore.from_dir("../data/input/magic/rad_max/data/")
obs_magic = data_store.obs(5029748, required_irf=["aeff"])

figsize = config.FigureSizeAA(aspect_ratio=2.6, width_aa="two-column")

xlim = 0.008, 600

kwargs = {"lw": 2}

gridspec = {"top": 0.92, "right": 0.98, "left": 0.08, "bottom": 0.15}
fig, axes = plt.subplots(figsize=figsize.inch, nrows=1, ncols=2, gridspec_kw=gridspec)

ax_aeff = axes[0]
ax_aeff.set_title("Effective Area")
ax_aeff.xaxis.set_units(u.TeV)
ax_aeff.yaxis.set_units(u.Unit("m2"))

# H.E.S.S.
aeff_hess = obs_hess.aeff.slice_by_idx({"energy_true": slice(42, None)})
aeff_hess.plot_energy_dependence(ax=ax_aeff, offset=offset, label="H.E.S.S.", **kwargs)
color = ax_aeff.lines[-1].get_color()
ax_aeff.text(x=10, y=1e6, s="H.E.S.S.", color=color)

# CTA
irf_cta_south["aeff"].plot_energy_dependence(ax=ax_aeff, offset=offset, label="CTA", **kwargs)
color = ax_aeff.lines[-1].get_color()
ax_aeff.text(x=0.06, y=3e5, s="CTAO", color=color)

# Fermi-LAT
exposure_fermi = Map.read(
    "../data/input/fermi-3fhl-gc/fermi-3fhl-gc-exposure-cube.fits.gz"
)
aeff_fermi = exposure_fermi.to_region_nd_map(func=np.mean) / fermi_livetime
energy = aeff_fermi.geom.axes["energy_true"].center
data = aeff_fermi.quantity[:, 0, 0]
ax_aeff.plot(energy, data, **kwargs)
color = ax_aeff.lines[-1].get_color()
ax_aeff.text(x=0.02, y=1.0, s="Fermi-LAT", color=color)

# MAGIC
aeff_magic = obs_magic.aeff.slice_by_idx({"energy_true": slice(2, 24)})
aeff_magic.plot_energy_dependence(ax=ax_aeff, offset=[0.4] * u.deg, **kwargs)
color = ax_aeff.lines[-1].get_color()
ax_aeff.text(x=0.04, y=300, s="MAGIC", color=color)

# HAWC
aeff_hawc_max = []

for nhit_bin in range(5, 10):
    filename = f"../data/input/hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin{nhit_bin}GP.fits.gz"
    aeff_hawc_map = Map.read(filename)
    aeff_hawc = aeff_hawc_map.to_region_nd_map(func=np.mean) / hawc_lifetime
    data = aeff_hawc.quantity[:, 0, 0]

    energy = aeff_hawc.geom.axes["energy_true"].center
    ax_aeff.plot(energy, data, alpha=0.2, color="k")
    aeff_hawc_max.append(data)

aeff_hawc_max = np.stack(aeff_hawc_max).sum(axis=0)

ax_aeff.plot(
    aeff_hawc.geom.axes["energy_true"].center,
    aeff_hawc_max,
    color="k",
    **kwargs,
)
color = ax_aeff.lines[-1].get_color()
ax_aeff.text(x=50, y=3e4, s="HAWC", color=color)

ax_aeff.set_xlim(*xlim)
ax_aeff.set_yscale("log")
ax_aeff.set_ylim(1e-1, 8e6)
ax_aeff.set_xlabel("True Energy / TeV")
ax_aeff.set_ylabel("Effective Area / m$^2$")
ax_aeff.get_legend().remove()

# PSF
psf_hess = obs_hess.psf.slice_by_idx({"energy_true": slice(10, None)})
psf_cta = irf_cta_south["psf"].slice_by_idx({"energy_true": slice(1, None)})

ax_psf = axes[1]
ax_psf.set_title("Point Spread Function")

psf_hess.plot_containment_radius_vs_energy(
    ax=ax_psf, offset=offset, fraction=[0.68], **kwargs
)
color = ax_psf.lines[-1].get_color()
ax_psf.text(x=3, y=0.15, s="H.E.S.S.", color=color)

psf_cta.plot_containment_radius_vs_energy(
    ax=ax_psf, offset=offset, fraction=[0.68], **kwargs
)
color = ax_psf.lines[-1].get_color()
ax_psf.text(x=20, y=0.05, s="CTAO", color=color)

psf_fermi = PSFMap.read(
    "../data/input/fermi-3fhl-gc/fermi-3fhl-gc-psf-cube.fits.gz", format="gtpsf"
)
energy_true = psf_fermi.psf_map.geom.axes["energy_true"].center
radius = psf_fermi.containment_radius(fraction=0.68, energy_true=energy_true)
ax_psf.plot(energy_true, radius, **kwargs)
color = ax_psf.lines[-1].get_color()
ax_psf.text(x=0.02, y=0.07, s="Fermi-LAT", color=color)
ax_psf.get_legend().remove()


ax_psf.lines[-1].set_label("Fermi-LAT")
ax_psf.set_yticks([0, 0.1, 0.2, 0.3, 0.4])
ax_psf.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
ax_psf.set_xlim(*xlim)
ax_psf.set_xlabel("True Energy / TeV")
ax_psf.set_ylabel("Containment radius / deg")


# ax_edisp = axes[0, 1]
# ax_edisp.set_title("Energy Resolution")
# obs_cta.edisp.plot_bias(ax=ax_edisp)
# #obs_cta.edisp.plot_bias(ax=ax_edisp)
# ax_edisp.set_xlim(*xlim)

filename = "irfs.pdf"
log.info(f"Writing {filename}")
plt.savefig(filename, dpi=300)
