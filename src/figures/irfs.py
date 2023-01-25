import logging

import config
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from astropy import units as u
from astropy.visualization import quantity_support

from gammapy.data import DataStore
from gammapy.irf import PSFMap, RecoPSFMap
from gammapy.maps import Map

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

fermi_livetime = 5e7 * u.s
hawc_lifetime = 56.53223 * u.day

offset = [1] * u.deg

data_store = DataStore.from_dir("../data/cta-galactic-center/input/index/gps")
obs_cta = data_store.obs(110380)

data_store = DataStore.from_dir("../data/lightcurve/input/")
obs_hess = data_store.obs(33787)

data_store = DataStore.from_dir("../data/multi-instrument/input/magic")
obs_magic = data_store.obs(5029748, required_irf=["aeff"])

figsize = config.FigureSizeAA(aspect_ratio=2.6, width_aa="two-column")

xlim = 0.008, 600

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

energy = aeff_fermi.geom.axes["energy_true"].center
data = aeff_fermi.quantity[:, 0, 0]
ax_aeff.plot(energy, data, label="Fermi-LAT", **kwargs)

aeff_magic = obs_magic.aeff.slice_by_idx({"energy_true": slice(2, 24)})
aeff_magic.plot_energy_dependence(
    ax=ax_aeff, offset=[0.4] * u.deg, label="MAGIC", **kwargs
)

aeff_hawc_max = []

for nhit_bin in range(5, 10):
    filename = (
        f"../data/hawc-dl3/irfs/EffectiveAreaMap_Crab_fHitbin{nhit_bin}GP.fits.gz"
    )
    aeff_hawc_map = Map.read(filename)
    aeff_hawc = aeff_hawc_map.to_region_nd_map(func=np.mean) / hawc_lifetime
    data = aeff_hawc.quantity[:, 0, 0]

    energy = aeff_hawc.geom.axes["energy_true"].center
    ax_aeff.plot(energy, data, alpha=0.2, color="k")
    aeff_hawc_max.append(data)

aeff_hawc_max = np.stack(aeff_hawc_max).max(axis=0)

ax_aeff.plot(
    aeff_hawc.geom.axes["energy_true"].center,
    aeff_hawc_max,
    color="k",
    label="HAWC",
    **kwargs,
)

ax_aeff.set_xlim(*xlim)
ax_aeff.set_yscale("log")
ax_aeff.set_ylim(1e-1, 8e6)
ax_aeff.legend(fontsize=8, ncol=1)

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

energy_true = psf_fermi.psf_map.geom.axes["energy_true"].center
radius = psf_fermi.containment_radius(fraction=0.68, energy_true=energy_true)
ax_psf.plot(energy_true, radius, label="Fermi-LAT", **kwargs)


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
