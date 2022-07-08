from gammapy.datasets import (
    MapDataset, FluxPointsDataset, Datasets
)

dataset1 = MapDataset.read(
    "$GAMMAPY_DATA/cta-1dc-gc/cta-1dc-gc.fits.gz",
    name="map-dataset"
)

dataset2 = FluxPointsDataset.read(
    "$GAMMAPY_DATA/tests/spectrum/flux_points/diff_flux_points.fits",
    name="flux-points-dataset",
)

datasets = Datasets([dataset1, dataset2])
print(datasets)
