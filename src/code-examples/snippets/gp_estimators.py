from astropy import units as u

from gammapy.datasets import MapDataset
from gammapy.estimators import TSMapEstimator

filename = "$GAMMAPY_DATA/cta-1dc-gc/cta-1dc-gc.fits.gz"
dataset = MapDataset.read(filename)

estimator = TSMapEstimator(
    energy_edges=[0.1, 1, 10] * u.TeV,
    n_sigma=1,
    n_sigma_ul=2,
)

maps = estimator.run(dataset)
maps["sqrt_ts"].plot_grid(add_cbar=True)
