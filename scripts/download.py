from fileinput import filename
import logging
import click
from pathlib import Path
from gammapy.scripts.download import progress_download

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://github.com/gammapy/gammapy-data/raw/master/"
PATH = Path(__file__).parent.parent
PATH_DATA = PATH / "src/data"


FILENAMES_FERMI = [
    "fermi-3fhl-gc-counts-cube.fits.gz",
    "fermi-3fhl-gc-background-cube.fits.gz",
    "fermi-3fhl-gc-exposure-cube.fits.gz",
    "fermi-3fhl-gc-psf-cube.fits.gz",
]

FILENAMES_FERMI_3FHL = [
    "Fermi-LAT-3FHL_data_Fermi-LAT.fits",
    "Fermi-LAT-3FHL_iem.fits",
    "Fermi-LAT-3FHL_datasets.yaml",
    "Fermi-LAT-3FHL_models.yaml",
]

FILENAMES_MAGIC = [
    "hdu-index.fits.gz",
    "obs-index.fits.gz",
    "20131004_05029747_DL3_CrabNebula-W0.40+035.fits",
    "20131004_05029748_DL3_CrabNebula-W0.40+215.fits",
]

FILENAMES_HAWC = [
    "HAWC19_flux_points.fits",
]

FILENAMES_CTA = [
    "index/gps/hdu-index.fits.gz",
    "index/gps/obs-index.fits.gz",
    "data/baseline/gps/gps_baseline_110380.fits",
    "data/baseline/gps/gps_baseline_111140.fits",
    "data/baseline/gps/gps_baseline_111159.fits",
    "caldb/data/cta/1dc/bcf/South_z20_50h/irf_file.fits",
]

OBS_IDS_PKS2155 = [
    "33787",
    "33788",
    "33789",
    "33790",
    "33791",
    "33792",
    "33793",
    "33794",
    "33795",
    "33796",
    "33797",
    "33798",
    "33799",
    "33800",
    "33801",
]

FILENAMES_PKS2155 = ["obs-index.fits.gz", "hdu-index.fits.gz"]


def download_cta_data():
    cta_path = PATH_DATA / f"cta-galactic-center/input"
    cta_path.mkdir(exist_ok=True, parents=True)

    for filename in FILENAMES_CTA:
        destination = cta_path / filename
        destination.parent.mkdir(exist_ok=True, parents=True)
        source = BASE_URL + "cta-1dc/" + filename
        log.info(f"Downloading {source}")
        progress_download(source, destination)


def download_fermi_data():
    fermi_path = PATH_DATA / f"fermi-ts-map/input"
    fermi_path.mkdir(exist_ok=True, parents=True)

    for filename in FILENAMES_FERMI:
        destination = fermi_path / filename
        source = BASE_URL + "fermi-3fhl-gc/" + filename
        log.info(f"Downloading {source}")
        progress_download(source, destination)


def download_fermi_crab_3fhl():
    fermi_path = PATH_DATA / f"multi-instrument/input/data/fermi"
    fermi_path.mkdir(exist_ok=True, parents=True)

    for filename in FILENAMES_FERMI_3FHL:
        destination = fermi_path / filename
        source = BASE_URL + "fermi-3fhl-crab/" + filename
        log.info(f"Downloading {source}")
        progress_download(source, destination)


def download_magic_data():
    magic_path = PATH_DATA / f"multi-instrument/input/data/magic"
    magic_path.mkdir(exist_ok=True, parents=True)

    for filename in FILENAMES_MAGIC:
        destination = magic_path / filename
        destination.parent.mkdir(exist_ok=True, parents=True)
        source = BASE_URL + "magic/rad_max/data/" + filename
        log.info(f"Downloading {source}")
        progress_download(source, destination)


def download_hawc_data():
    hawc_path = PATH_DATA / f"multi-instrument/input/data/hawc"
    hawc_path.mkdir(exist_ok=True, parents=True)

    for filename in FILENAMES_HAWC:
        destination = hawc_path / filename
        destination.parent.mkdir(exist_ok=True, parents=True)
        source = BASE_URL + "hawc_crab/" + filename
        log.info(f"Downloading {source}")
        progress_download(source, destination)


def download_hess_pks2155_data():
    pks_path = PATH_DATA / f"lightcurve/input"
    pks_path.mkdir(exist_ok=True, parents=True)

    for obs_id in OBS_IDS_PKS2155:
        filename = "data/hess_dl3_dr1_obs_id_0" + obs_id + ".fits.gz"
        FILENAMES_PKS2155.append(filename)

    for filename in FILENAMES_PKS2155:
        destination = pks_path / filename
        destination.parent.mkdir(exist_ok=True, parents=True)
        source = BASE_URL + "hess-dl3-dr1/" + filename
        log.info(f"Downloading {source}")
        progress_download(source, destination)


DATASETS_REGISTRY = {
    "fermi-gc": download_fermi_data,
    "cta-1dc": download_cta_data,
    "pks-flare": download_hess_pks2155_data,
    "multi-instrument-fermi": download_fermi_crab_3fhl,
    "multi-instrument-magic": download_magic_data,
    "multi-instrument-hawc": download_hawc_data
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
