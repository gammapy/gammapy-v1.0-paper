# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Provide code stats for Gammapy project"""
import argparse
import logging
from pathlib import Path
import subprocess
from string import Template
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

import config

logging.basicConfig(level=logging.INFO)

CODEBASE = "../../gammapy"
TEMPFILE = "results.csv"
TEXFILE = "../tables/generated/codestats.tex"
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
    result_api = subprocess.run(["cloc", "--not-match-d=test", args.src], capture_output=True).stdout
    result_test = subprocess.run(["cloc", "--match-d=test", args.src], capture_output=True).stdout

    for line in result_api.splitlines():
        decoded = line.decode("utf-8")
        if decoded.startswith("Python"):
            python_api_row = decoded
            (_, files_api, blank_api, comment_api, code_api) = python_api_row.split()
    for line in result_test.splitlines():
        decoded = line.decode("utf-8")
        if decoded.startswith("Python"):
            python_test_row = decoded
            (_, files_test, blank_test, comment_test, code_test) = python_test_row.split()

    PythonAPI  = f"PythonAPI                      {files_api}          {blank_api}          {comment_api}          {code_api}"
    PythonTests = f"PythonTests                    {files_test}           {blank_test}           {comment_test}          {code_test}"
    DocStrings = f"DocStrings                     {files_api}              0              0          {comment_api}"

    result_list = []
    for line in result_api.splitlines():
        decoded = line.decode("utf-8")
        if decoded.startswith("Python"):
            result_list.extend((PythonAPI, PythonTests, DocStrings))
        else:
            result_list.append(decoded)

    return "\n".join(result_list)


def make_files(stats):
    latex = Template(LATEX_TEMPLATE)
    csv = Template(CSV_TEMPLATE)

    content_lat = {"labels": "", "cells": "", "summary": ""}
    content_csv = {"labels": "", "cells": "", "summary": ""}

    for idx, line in enumerate(stats.splitlines()):
        line = line.replace("PythonAPI", "Python~API")
        line = line.replace("PythonTests", "Python~Tests")
        line = line.replace("Jupyter Notebook", "Notebooks")
        line = line.replace("DOS Batch", "Batch")
        line = line.replace("Bourne Shell", "Shell")
        line = line.replace("SUM:", "Total")

        latex_converted = "\t& ".join(line.split()) + " \\\\"
        csv_converted = ", ".join(line.split())

        if line.startswith("Language"):
            content_lat["labels"] = latex_converted
            content_csv["labels"] = csv_converted
        elif idx == len(stats.splitlines()) - 2:
            content_lat["summary"] = latex_converted
            content_csv["summary"] = csv_converted
        elif not line.startswith("---") and content_lat["labels"]:
            content_lat["cells"] += latex_converted + "\n"
            content_csv["cells"] += csv_converted + "\n"

    csv = csv.substitute(content_csv)
    csv = csv.replace("Python~API", "Python API")
    csv = csv.replace("Python~Tests", "Python Tests")

    tex_name = Path(TEXFILE)
    tex_name.parent.mkdir(parents=True, exist_ok=True)
    latex = latex.substitute(content_lat)
    with open(TEXFILE, "w") as file_tex:
        file_tex.write(latex)
    logging.info(f"LaTeX output file {TEXFILE} created.")

    with open(TEMPFILE, "w") as file_csv:
        file_csv.write(csv)
    logging.info(f"CSV temporary file {TEMPFILE} created.")


def make_pie():
    figsize = config.FigureSizeAA()
    fig = plt.figure(figsize=figsize.inch)

    ax = fig.add_axes([0, 0, 0.95, 0.95])

    file_data = pd.read_csv(TEMPFILE, sep=", ", engine="python")
    df = file_data[:-1]
    df = df.set_index("Language")

    # code
    df = df.sort_values(by=["code"])[::-1]
    sdf = shorthen_df(df)
    sdf.plot(
        ax=ax, kind="pie", y="code", autopct=fix_autopct, legend=False, fontsize=8
    )
    plt.ylabel("")
    plt.savefig("codestats.pdf")
    logging.info("Piecharf file codestats.pdf created.")

    # files
    # sdf = sdf.sort_values(by=["files"])[::-1]
    # sdf = shorthen_df(df)
    # sdf.plot.pie(y="files", autopct=fix_autopct, labels=None)
    # plt.ylabel("")
    # plt.savefig("filestats.pdf")
    # logging.info("Piecharf file filestats.pdf created.")


def shorthen_df(df):
    # group others
    others = defaultdict(int)
    for i in range(5, len(df)):
        others["files"] += df["files"][i]
        others["blank"] += df["blank"][i]
        others["comment"] += df["comment"][i]
        others["code"] += df["code"][i]
    odf = pd.DataFrame(data=others, index=["Others"])
    return pd.concat([df.head(5), odf], axis=0)


def fix_autopct(pct):
    return "{pct:.0f} %".format(pct=pct)


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
    Path(TEMPFILE).unlink()


if __name__ == "__main__":
    main()
