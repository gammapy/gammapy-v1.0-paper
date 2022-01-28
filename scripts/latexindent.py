from pathlib import Path
import subprocess
import logging

log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

BASE_PATH = Path(__file__).parent

filenames = BASE_PATH.glob("src/text/*.tex")

for filename in filenames:
    command = ["latexindent.pl"]
    command += [f"{filename}"]
    command += ["-s", "-m", "-l", ".latexindent.yaml"]
    command += ["-o", f"{filename}"]

    log.info(f"Reformatting {filename}")
    subprocess.call(command)
