from gammapy.datasets import MapDataset
from gammapy.modeling.models import SkyModel, PowerLawSpectralModel, PointSpatialModel
from gammapy.modeling import Fit
dataset = MapDataset.read("$GAMMAPY_DATA/cta-1dc-gc/cta-1dc-gc.fits.gz", name="cta_dataset")
pwl = PowerLawSpectralModel()
point = PointSpatialModel()
model = SkyModel( spectral_model=pwl,spatial_model=point,name=”my-model”)
fit = Fit()
result = fit.run(datasets=[datasets])

