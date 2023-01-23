import logging

import config
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from astropy import units as u

from gammapy.data import DataStore
from gammapy.irf import PSFMap
from gammapy.maps import Map

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

fermi_livetime = 5e7 * u.s

offset = [1] * u.deg

data_store = DataStore.from_dir("../data/cta-galactic-center/input/index/gps")
obs_cta = data_store.obs(110380)

data_store = DataStore.from_dir("../data/lightcurve/input/")
obs_hess = data_store.obs(33787)

data_store = DataStore.from_dir("../data/multi-instrument/input/magic")
obs_magic = data_store.obs(5029748, required_irf=["aeff"])

figsize = config.FigureSizeAA(aspect_ratio=2.6, width_aa="two-column")

xlim = 0.008, 500

kwargs = {"lw": 2}

gridspec = {"top": 0.92, "right": 0.98, "left": 0.08, "bottom": 0.15}
fig, axes = plt.subplots(figsize=figsize.inch, nrows=1, ncols=2, gridspec_kw=gridspec)

exposure_fermi = Map.read(
    "../data/fermi-ts-map/input/fermi-3fhl-gc-exposure-cube.fits.gz"
)
aeff_fermi = exposure_fermi.to_region_nd_map(func=np.mean) / fermi_livetime

ax_aeff = axes[0]
ax_aeff.set_title("Effective Area")
ax_aeff.xaxis.set_units(u.TeV)
ax_aeff.yaxis.set_units(u.Unit("m2"))

aeff_hess = obs_hess.aeff.slice_by_idx({"energy_true": slice(42, None)})
obs_cta.aeff.plot_energy_dependence(ax=ax_aeff, offset=offset, label="CTA", **kwargs)
aeff_hess.plot_energy_dependence(ax=ax_aeff, offset=offset, label="H.E.S.S.", **kwargs)
aeff_fermi.plot(ax=ax_aeff, marker="None", label="Fermi-LAT", **kwargs)

aeff_magic = obs_magic.aeff.slice_by_idx({"energy_true": slice(2, 24)})
aeff_magic.plot_energy_dependence(
    ax=ax_aeff, offset=[0.4] * u.deg, label="MAGIC", **kwargs
)

ax_aeff.set_xlim(*xlim)
ax_aeff.set_yscale("log")
ax_aeff.set_ylim(1e-1, 8e6)
ax_aeff.legend()

psf_hess = obs_hess.psf.slice_by_idx({"energy_true": slice(10, None)})
psf_cta = obs_cta.psf.slice_by_idx({"energy_true": slice(None, -2)})

ax_psf = axes[1]
ax_psf.set_title("Point Spread Function")
psf_cta.plot_containment_radius_vs_energy(
    ax=ax_psf, offset=offset, fraction=[0.68], label="CTA", **kwargs
)

psf_hess.plot_containment_radius_vs_energy(
    ax=ax_psf, offset=offset, fraction=[0.68], label="H.E.S.S.", **kwargs
)

psf_fermi = PSFMap.read(
    "../data/fermi-ts-map/input/fermi-3fhl-gc-psf-cube.fits.gz", format="gtpsf"
)

psf_fermi.plot_containment_radius_vs_energy(ax=ax_psf, fraction=[0.68], **kwargs)
ax_psf.lines[-1].set_label("Fermi-LAT")
ax_psf.set_yticks([0, 0.1, 0.2, 0.3, 0.4])
ax_psf.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
ax_psf.set_xlim(*xlim)
ax_psf.set_xlabel("True Energy [TeV]")
ax_psf.legend()

# ax_edisp = axes[0, 1]
# ax_edisp.set_title("Energy Resolution")
# obs_cta.edisp.plot_bias(ax=ax_edisp)
# #obs_cta.edisp.plot_bias(ax=ax_edisp)
# ax_edisp.set_xlim(*xlim)

filename = "irfs.pdf"
log.info(f"Writing {filename}")
plt.savefig(filename, dpi=300)
