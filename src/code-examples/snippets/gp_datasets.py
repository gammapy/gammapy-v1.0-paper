from pathlib import Path

from gammapy.datasets import (
    Datasets,
    FluxPointsDataset,
    MapDataset,
    SpectrumDatasetOnOff,
)

path = Path("$GAMMAPY_DATA")

map_dataset = MapDataset.read(
    path / "cta-1dc-gc/cta-1dc-gc.fits.gz",
    name="map-dataset",
)

spectrum_dataset = SpectrumDatasetOnOff.read(
    path / "joint-crab/spectra/hess/pha_obs23523.fits",
    name="spectrum-datasets",
)

flux_points_dataset = FluxPointsDataset.read(
    path / "hawc_crab/HAWC19_flux_points.fits",
    name="flux-points-dataset",
)


datasets = Datasets([
    map_dataset,
    spectrum_dataset,
    flux_points_dataset
])

print(datasets["map-dataset"])
