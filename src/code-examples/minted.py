import logging
import os
import subprocess
from pathlib import Path

os.environ["GAMMAPY_DATA"] = "../../data/input"

log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

PATH = Path(__file__).parent

SNIPPETS = PATH / "snippets"
GENERATED = PATH / "generated"
GENERATED_OUTPUT = PATH / "generated-output"

EXCLUDE_OUTPUT = [
    "gp_catalogs.py",
    "gp_estimators.py",
    "gp_makers.py",
]

# for example 'frame=single' to frame the code
OPTIONS = "frame=lines,style=friendly,linenos=0"
OPTIONS_OUTPUT = "frame=lines,style=nord,linenos=0"

if __name__ == "__main__":
    GENERATED.mkdir(exist_ok=True)

    filenames = SNIPPETS.glob("*.py")
    for filename in filenames:
        command = ["pygmentize"]
        command += ["-O", f"verboptions={OPTIONS}"]
        command += ["-f", "tex"]

        filename_out = GENERATED / filename.name.replace(".py", ".tex")
        command += ["-o", f"{filename_out}"]
        command += [f"{filename}"]
        log.info(f"Executing {' '.join(command)}")
        subprocess.call(command)

    filenames = SNIPPETS.glob("*.py")
    GENERATED_OUTPUT.mkdir(exist_ok=True)

    for filename in filenames:
        if filename.name in EXCLUDE_OUTPUT:
            continue

        command = ["pygmentize"]
        command += ["-O", f"verboptions={OPTIONS_OUTPUT}"]
        command += ["-f", "tex"]

        filename_out = GENERATED_OUTPUT / filename.name.replace(".py", ".tex")
        command += ["-o", f"{filename_out}"]
        log.info(f"Executing {' '.join(command)}")

        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        proc = subprocess.Popen(["python", str(filename)], stdout=subprocess.PIPE)
        out = proc.communicate()[0]

        if out == "":
            raise ValueError(f"No output from script {filename.name}")

        stdout_data = p.communicate(input=out)[0]
