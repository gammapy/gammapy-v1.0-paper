from gammapy.catalog import SourceCatalog4FGL

catalog = SourceCatalog4FGL()
print("Number of sources :", len(catalog.table))

source = catalog["PKS 2155-304"]
model = source.sky_model()
source.flux_points.plot()

source.lightcurve().plot()
