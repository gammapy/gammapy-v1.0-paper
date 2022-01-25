# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Provide code stats for Gammapy project"""
import argparse
import logging
import subprocess
from string import Template

import matplotlib.pyplot as plt
import pandas as pd

logging.basicConfig(level=logging.INFO)

LATEX_TEMPLATE = r"""\begin{tabular}{ccccccc}
\hline
$labels
\hline
$cells\hline
$summary
\end{tabular}

"""

CSV_TEMPLATE = r"""$labels
$cells$summary"""


# TODO: use pygount here? cloc is not easily installable via conda...
def run_cloc(args):
    result = subprocess.run(["cloc", args.src], capture_output=True)
    return result.stdout


def make_files(stats):

    latex = Template(LATEX_TEMPLATE)
    csv = Template(CSV_TEMPLATE)

    content_lat = {"labels": "", "cells": "", "summary": ""}
    content_csv = {"labels": "", "cells": "", "summary": ""}

    for idx, line in enumerate(stats.splitlines()):
        decoded = line.decode("utf-8")
        decoded = decoded.replace("Jupyter Notebook", "Notebook")
        decoded = decoded.replace("DOS Batch", "Batch")
        decoded = decoded.replace("Bourne Shell", "Shell")
        decoded = decoded.replace("SUM:", "SUM")

        latex_converted = "\t& ".join(decoded.split()) + " \\\\"
        csv_converted = ", ".join(decoded.split())

        if decoded.startswith("Language"):
            content_lat["labels"] = latex_converted
            content_csv["labels"] = csv_converted
        elif idx == len(stats.splitlines()) - 2:
            content_lat["summary"] = latex_converted
            content_csv["summary"] = csv_converted
        elif not decoded.startswith("---") and content_lat["labels"]:
            content_lat["cells"] += latex_converted + "\n"
            content_csv["cells"] += csv_converted + "\n"

    latex = latex.substitute(content_lat)
    csv = csv.substitute(content_csv)

    logging.info("LaTeX OUTPUT TABLE BELOW:\n\n")
    print(latex)
    with open("results.csv", "w") as file_csv:
        file_csv.write(csv)


def make_pie():
    file_data = pd.read_csv("results.csv", sep=", ", engine="python")

    df = file_data[:-1]
    df = df.set_index("Language")
    df = df.sort_values(by=["code"])[::-1]
    df.plot.pie(y="code", figsize=(7, 7), autopct=fix_autopct, labels=None)
    plt.ylabel("")
    plt.savefig("codestats.pdf")
    logging.info("PIECHART FILE piecode.png CREATED")

    # df = file_data[:-1]
    # df = df.set_index("Language")
    # df = df.sort_values(by=["files"])[::-1]
    # df.plot.pie(y="files", figsize=(7, 7), autopct=fix_autopct, labels=None)
    # plt.ylabel("")
    # plt.savefig("piefiles.png")
    # logging.info("PIECHART FILE piefiles.png CREATED")


def fix_autopct(pct):
    return ("%.2f" % pct) if pct > 3 else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", help="Path to Gammapy project")
    args = parser.parse_args()
    if not args.src:
        raise Exception("Please provide --src path to Gammapy project")

    result = run_cloc(args)
    make_files(result)
    make_pie()


if __name__ == "__main__":
    main()
