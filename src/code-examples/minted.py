from pathlib import Path
import subprocess
import logging

log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

PATH = Path(__file__).parent

SNIPPETS = PATH / "snippets"
GENERATED = PATH / "generated"

# for example 'frame=single' to frame the code
OPTIONS = 'frame=lines,style=friendly,linenos=1'

if __name__ == '__main__':
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
