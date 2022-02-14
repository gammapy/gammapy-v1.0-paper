from pathlib import Path
from ruamel.yaml import YAML
from gammapy.scripts.download import progress_download

BASE_URL = "https://github.com/gammapy/gammapy-data/raw/master/"
PATH = Path(__file__).parent.parent
PATH_DATA = PATH / "src/data"


def download_fermi_data():
    fermi_path = PATH_DATA / f"fermi-ts-map/input"
    fermi_path.mkdir(exist_ok=True, parents=True)

    yaml = YAML()

    config_file = PATH / "showyourwork.yml"
    with config_file.open("r") as stream:
        data = yaml.load(stream)

    filenames = data["dependencies"]["src/figures/fermi_ts_map.py"]
    filenames = [Path(_) for _ in filenames]

    for filename in filenames:
        destination = fermi_path / filename.name
        source = BASE_URL + "fermi-3fhl-gc/" + filename.name
        print(source)
        progress_download(source, destination)


if __name__ == "__main__":
    download_fermi_data()