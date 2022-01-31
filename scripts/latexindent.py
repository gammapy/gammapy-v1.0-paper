from pathlib import Path
import subprocess
import logging

EXCLUDE_FILES = ["0-authors.tex"]

log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

BASE_PATH = Path(__file__).parent.parent

filenames = (BASE_PATH / "src/text").glob("**/*.tex")

for filename in filenames:
    if filename.name in EXCLUDE_FILES:
        continue

    command = ["latexindent.pl"]
    command += [f"{filename}"]
    command += ["-s", "-m", "-l", ".latexindent.yaml"]
    command += ["-o", f"{filename}"]

    log.info(f"Reformatting {filename}")
    subprocess.call(command)
