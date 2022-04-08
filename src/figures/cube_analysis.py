import logging
from pathlib import Path
import matplotlib.pyplot as plt
from gammapy.datasets import Datasets
from gammapy.maps import Map
from gammapy.modeling.models import Models
import config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

path = Path("../data/cube-analysis/")
significance = Map.read(path / "significance_map.fits")
residual = Map.read(path / "residual_map.fits")
excess =Map.read(path / "excess_counts.fits", format="ogip")
npred_1 =Map.read(path / "npred_1.fits", format="ogip")
npred_2 =Map.read(path / "npred_2.fits", format="ogip")
npred_3 =Map.read(path / "npred_3.fits", format="ogip")

models = Models.read(path / "best-fit-model.yaml")

figsize = config.FigureSizeAA(aspect_ratio=2.8, width_aa="two-column")
fig = plt.figure(figsize=figsize.inch)

wcs = significance.geom.wcs
region = excess.geom.region

# rect = (0.05, 0.2, 0.28, 0.75)
rect = (0.05, 0.2, 0.4, 0.75)
ax = fig.add_axes(rect=rect, projection=wcs)
significance.plot(ax=ax, stretch='sqrt', add_cbar=True)
ax.images[-1].colorbar.set_label('Significance ($\sigma$)', rotation=270, labelpad=25, fontsize=12)
region.to_pixel(wcs).plot(ax=ax, fill=False, lw=1, color='blue', ls='--')

# rect = (0.40, 0.2, 0.28, 0.75)
rect = (0.55, 0.2, 0.4, 0.75)

ax = fig.add_axes(rect=rect, projection=wcs)
residual.plot(ax=ax,cmap='coolwarm', vmin=-5, vmax=5, add_cbar=True)
ax.images[-1].colorbar.set_label('Significance ($\sigma$)', rotation=270, labelpad=25, fontsize=12)

ax.scatter(models[0].spatial_model.to_region().to_pixel(wcs).center.x,
            models[0].spatial_model.to_region().to_pixel(wcs).center.y,
            color='k', marker='x')
models[1].spatial_model.to_region().to_pixel(wcs).plot(ax=ax, fill=False, lw=1, color='k')
models[2].spatial_model.to_region().to_pixel(wcs).plot(ax=ax, fill=False, lw=1, color='k')

filename = "cube_analysis_fig1.pdf"
log.info(f"Writing {filename}")
plt.savefig(filename, dpi=300)

# rect = (0.72, 0.2, 0.28, 0.75)
# ax = fig.add_axes(rect=rect)

figsize = config.FigureSizeAA(aspect_ratio=1.2, width_aa="single-column")
fig = plt.figure(figsize=figsize.inch)
rect = (0.16, 0.15, 0.75, 0.8)
ax = fig.add_axes(rect=rect)
excess.plot(ax=ax, color='blue', label='excess counts')
npred_1.plot_hist(ax=ax, label='source 1', lw=1, color='C0')
npred_2.plot_hist(ax=ax, label='source 2', lw=1, color='C1')
npred_3.plot_hist(ax=ax, label='source 3', lw=1, color='C2')
(npred_1 + npred_2 + npred_3).plot_hist(ax=ax, label='total', lw=1, color='k')
ax.legend(fontsize=6)
ax.set_ylabel('Counts')

filename = "cube_analysis_fig2.pdf"
log.info(f"Writing {filename}")
plt.savefig(filename, dpi=300)
