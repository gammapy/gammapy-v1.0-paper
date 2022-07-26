from gammapy.catalog import SOURCE_CATALOGS

catalog = SOURCE_CATALOGS.get_cls("4fgl")()
print("Number of sources :", len(catalog.table))

source = catalog["PKS 2155-304"]
model = source.sky_model()
source.flux_points.plot()

source.lightcurve().plot()
