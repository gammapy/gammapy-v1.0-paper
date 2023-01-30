import logging
from fileinput import filename
from pathlib import Path

import click

from gammapy.scripts.download import progress_download

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://github.com/gammapy/gammapy-data/raw/v1.0/"
PATH = Path(__file__).parent.parent
PATH_DATA = PATH / "src/data/input"


FILENAMES_FERMI = [
    "fermi-3fhl-gc/fermi-3fhl-gc-counts-cube.fits.gz",
    "fermi-3fhl-gc/fermi-3fhl-gc-background-cube.fits.gz",
    "fermi-3fhl-gc/fermi-3fhl-gc-exposure-cube.fits.gz",
    "fermi-3fhl-gc/fermi-3fhl-gc-psf-cube.fits.gz",
]

FILENAMES_FERMI_CATALOG = ["catalogs/fermi/gll_psc_v28.fit.gz"]

FILENAMES_FERMI_3FHL = [
    "fermi-3fhl-crab/Fermi-LAT-3FHL_data_Fermi-LAT.fits",
    "fermi-3fhl-crab/Fermi-LAT-3FHL_iem.fits",
    "fermi-3fhl-crab/Fermi-LAT-3FHL_datasets.yaml",
    "fermi-3fhl-crab/Fermi-LAT-3FHL_models.yaml",
]

FILENAMES_MAGIC = [
    "magic/rad_max/data/hdu-index.fits.gz",
    "magic/rad_max/data/obs-index.fits.gz",
    "magic/rad_max/data/20131004_05029747_DL3_CrabNebula-W0.40+035.fits",
    "magic/rad_max/data/20131004_05029748_DL3_CrabNebula-W0.40+215.fits",
]

FILENAMES_HAWC = [
    "hawc_crab/HAWC19_flux_points.fits",
]

FILENAMES_HAWC_DL3 = [
    "hawc/crab_events_pass4/hdu-index-table-GP-Crab.fits.gz",
    "hawc/crab_events_pass4/obs-index-table-GP-Crab.fits.gz",
    "hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin5GP.fits.gz",
    "hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin6GP.fits.gz",
    "hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin7GP.fits.gz",
    "hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin8GP.fits.gz",
    "hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin9GP.fits.gz",
    "hawc/crab_events_pass4/irfs/PSFMap_Crab_fHitbin5GP.fits.gz",
    "hawc/crab_events_pass4/irfs/PSFMap_Crab_fHitbin6GP.fits.gz",
    "hawc/crab_events_pass4/irfs/PSFMap_Crab_fHitbin7GP.fits.gz",
    "hawc/crab_events_pass4/irfs/PSFMap_Crab_fHitbin8GP.fits.gz",
    "hawc/crab_events_pass4/irfs/PSFMap_Crab_fHitbin9GP.fits.gz",
]


FILENAMES_CTA = [
    "cta-1dc/index/gps/hdu-index.fits.gz",
    "cta-1dc/index/gps/obs-index.fits.gz",
    "cta-1dc/data/baseline/gps/gps_baseline_110380.fits",
    "cta-1dc/data/baseline/gps/gps_baseline_111140.fits",
    "cta-1dc/data/baseline/gps/gps_baseline_111159.fits",
    "cta-1dc/caldb/data/cta/1dc/bcf/South_z20_50h/irf_file.fits",
]

OBS_IDS_HESS_DR1 = [
    33787,
    33788,
    33789,
    33790,
    33791,
    33792,
    33793,
    33794,
    33795,
    33796,
    33797,
    33798,
    33799,
    33800,
    33801,
    23523,
    23526,
    23559,
    23592,
]

FILENAMES_HESS_DR1 = [
    "hess-dl3-dr1/obs-index.fits.gz",
    "hess-dl3-dr1/hdu-index.fits.gz",
]

for obs_id in OBS_IDS_HESS_DR1:
    filename = f"hess-dl3-dr1/data/hess_dl3_dr1_obs_id_0{obs_id}.fits.gz"
    FILENAMES_HESS_DR1.append(filename)


def download_data_files(filenames):
    for filename in filenames:
        destination = PATH_DATA / filename
        destination.parent.mkdir(exist_ok=True, parents=True)
        source = BASE_URL + filename
        log.info(f"Downloading {source}")
        progress_download(source, destination)


def download_cta_data():
    """Download CTA data."""
    download_data_files(FILENAMES_CTA)


def download_fermi_data():
    """Download Fermi data."""
    download_data_files(FILENAMES_FERMI_CATALOG)
    download_fermi_crab_3fhl()


def download_fermi_crab_3fhl():
    """Download Fermi 3FHL Crab data."""
    download_data_files(FILENAMES_FERMI_3FHL)


def download_magic_data():
    """Download MAGIC data."""
    download_data_files(FILENAMES_MAGIC)


def download_hawc_data():
    """Download HAWC data."""
    download_data_files(FILENAMES_HAWC)


def download_hawc_dl3_data():
    """Download HAWC data."""
    download_data_files(FILENAMES_HAWC_DL3)


def download_hess_pks2155_data():
    """Download HESS PKS2155 data."""
    download_data_files(FILENAMES_HESS_DR1)


def download_multi_instrument():
    download_fermi_crab_3fhl()
    download_magic_data()
    download_hawc_data()


DATASETS_REGISTRY = {
    "fermi-gc": download_fermi_data,
    "cta-1dc": download_cta_data,
    "pks-flare": download_hess_pks2155_data,
    "multi-instrument": download_multi_instrument,
    "hawc-dl3": download_hawc_dl3_data,
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
