from gammapy.modeling.models import (
	SkyModel,
	PowerLawSpectralModel,
	PointSpatialModel,
)

pwl = PowerLawSpectralModel()
point = PointSpatialModel()

model = SkyModel(
	spectral_model=pwl,
	spatial_model=point,
	name="my-model",
)
