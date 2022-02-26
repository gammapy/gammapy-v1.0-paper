# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Provide code stats for Gammapy project"""
import argparse
import logging
import pathlib
import subprocess
from string import Template
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

import config

logging.basicConfig(level=logging.INFO)

CODEBASE = "../../gammapy" 
TEMPFILE = "results.csv"
TEXFILE = "../text/tables/codestats.tex"
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

    with open(TEXFILE, "w") as file_tex:
        file_tex.write(latex)
    logging.info(f"LaTeX output file {TEXFILE} created.")

    with open(TEMPFILE, "w") as file_csv:
        file_csv.write(csv)
    logging.info(f"CSV temporary file {TEMPFILE} created.")    

def make_pie():

    figsize = config.FigureSizeAA()
    plt.figure(figsize=figsize.inch)

    file_data = pd.read_csv(TEMPFILE, sep=", ", engine="python")
    df = file_data[:-1]
    df = df.set_index("Language")

    # code
    df = df.sort_values(by=["code"])[::-1]
    sdf = shorthen_df(df)
    sdf.plot.pie(y="code", autopct=fix_autopct, labels=None)
    plt.ylabel("")
    plt.savefig("codestats.pdf")
    logging.info("Piecharf file codestats.pdf created.")

    # files
    sdf = sdf.sort_values(by=["files"])[::-1]
    sdf = shorthen_df(df)
    sdf.plot.pie(y="files", autopct=fix_autopct, labels=None)
    plt.ylabel("")
    plt.savefig("filestats.pdf")
    logging.info("Piecharf file filestats.pdf created.")

def shorthen_df(df):
    # group others
    others = defaultdict(int)
    for i in range(4, len(df)):
        others["files"] += df["files"][i]
        others["blank"] += df["blank"][i]
        others["comment"] += df["comment"][i]
        others["code"] += df["code"][i]
    odf = pd.DataFrame(data=others, index=["Others"])
    return pd.concat([df.head(4), odf], axis=0)

def fix_autopct(pct):
    return ("%.2f" % pct) if pct > 3 else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", help="Path to Gammapy project")
    args = parser.parse_args()
    if not args.src:
        # raise Exception("Please provide --src path to Gammapy project")
        args.src = CODEBASE

    result = run_cloc(args)
    make_files(result)
    make_pie()

    # remove not needed intermediate file
    pathlib.Path(TEMPFILE).unlink()


if __name__ == "__main__":
    main()
