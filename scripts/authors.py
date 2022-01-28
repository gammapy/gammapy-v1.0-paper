"""Utility script to work with the CITATION.cff file"""
import logging
import subprocess
import click
from ruamel.yaml import YAML
from pathlib import Path
from astropy.table import Table, vstack

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

BASE_PATH = Path(__file__).parent.parent

# TODO: get rid of the hard coded path, either download the file or
#  introduce gammapy as sub-module to the paper repo
PATH = Path("/Users/adonath/github/adonath/gammapy")
CITATION_CFF = PATH / "CITATION.cff"

AUTHOR_TEMPLATE = "{author_name} \inst{\ref{{affiliation_label}}}"


def get_full_name(author_data):
    """Get full name from CITATION.cff parts"""
    parts = []
    parts.append(author_data["given-names"])

    name_particle = author_data.get("name-particle", None)

    if name_particle:
        parts.append(name_particle)

    parts.append(author_data["family-names"])
    return " ".join(parts)


def get_citation_cff_authors_and_affiliations():
    """Get list of authors from CITATION.cff"""
    authors, affiliations = [], []

    yaml = YAML()

    with CITATION_CFF.open("r") as stream:
        data = yaml.load(stream)

    for author_data in data["authors"]:
        full_name = get_full_name(author_data)
        authors.append(full_name)

        affiliation = author_data.get("affiliation", "unknown")
        affiliations.append(affiliation)

    table = Table()
    table["author"] = authors
    table["affiliation"] = affiliations
    table["label"] = "inst:unknown"

    table_grouped = table.group_by("affiliation")

    for idx, group in enumerate(table_grouped.groups):
        affiliation = group[0]["affiliation"]

        if affiliation == "unknown":
            continue

        mask = table["affiliation"] == affiliation
        table["label"][mask] = f"inst:{idx}"

    return table


def write_author_file():
    table = get_citation_cff_authors_and_affiliations()

    author_str = "\\authorrunning{Deil, Donath, Terrier et al.}\n\n"
    author_str += "\\author{\n"

    for idx, row in enumerate(table):
        author, label = row["author"], row["label"]
        author_str += f"\t{author} \\inst{{\\ref{{{label}}}}}"
        if idx < len(table) - 1:
            author_str += " \\and\n"

    author_str += "\n}\n\n"

    author_str += "\institute{\n"

    table = table.group_by("affiliation")

    for idx, group in enumerate(table.groups):
        affiliation, label = group[0]["affiliation"], group[0]["label"]
        affiliation = affiliation.replace("&", "\&")
        author_str += f"\t{affiliation} \\label{{{label}}}"
        if idx < len(table.groups) - 1:
            author_str += " \\and\n"

    author_str += "\n}\n"

    authors_file = BASE_PATH / "src/text/0-authors.tex"

    log.info(f"Writing {authors_file}")

    with authors_file.open("w") as f:
        f.write(author_str)


if __name__ == "__main__":
    write_author_file()
