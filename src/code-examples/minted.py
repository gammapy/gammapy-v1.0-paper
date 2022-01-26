from pathlib import Path
import subprocess

PATH = Path(__file__).parent

SNIPPETS = PATH / "snippets"
GENERATED = PATH / "generated"

# for example 'frame=single' to frame the code
OPTIONS = 'frame=single,style=friendly,linenos=1'

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
        subprocess.call(command)
