import matplotlib.pyplot as plt

from gammapy.catalog import CATALOG_REGISTRY

catalog = CATALOG_REGISTRY.get_cls("4fgl")()
print("Number of sources :", len(catalog.table))

source = catalog["PKS 2155-304"]

_, axes = plt.subplots(ncols=2)
source.flux_points.plot(ax=axes[0], sed_type="e2dnde")

source.lightcurve().plot(ax=axes[1])
