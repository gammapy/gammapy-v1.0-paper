import click
from pathlib import Path
from gammapy.scripts.download import progress_download

BASE_URL = "https://github.com/gammapy/gammapy-data/raw/master/"
PATH = Path(__file__).parent.parent
PATH_DATA = PATH / "src/data"


FILENAMES = [
    "fermi-3fhl-gc-counts-cube.fits.gz",
    "fermi-3fhl-gc-background-cube.fits.gz",
    "fermi-3fhl-gc-exposure-cube.fits.gz",
    "fermi-3fhl-gc-psf-cube.fits.gz",
]


def download_fermi_data():
    fermi_path = PATH_DATA / f"fermi-ts-map/input"
    fermi_path.mkdir(exist_ok=True, parents=True)

    for filename in FILENAMES:
        destination = fermi_path / filename
        source = BASE_URL + "fermi-3fhl-gc/" + filename
        progress_download(source, destination)


DATASETS_REGISTRY = {
    "fermi-gc": download_fermi_data,
}


@click.command()
@click.argument(
    "dataset", type=click.Choice(list(DATASETS_REGISTRY), case_sensitive=False)
)
def cli(dataset):
    download_method = DATASETS_REGISTRY[dataset]
    download_method()


if __name__ == "__main__":
    cli()
