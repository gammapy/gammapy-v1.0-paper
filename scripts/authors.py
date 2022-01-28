"""Utility script to work with the CITATION.cff file"""
import logging
import subprocess
import click
from ruamel.yaml import YAML
from pathlib import Path

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

BASE_PATH = Path(__file__).parent.parent
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

    return {
        "authors": authors,
        "affiliations": affiliations,
    }


def write_author_file():
    data = get_citation_cff_authors_and_affiliations()

    author_str = "\\authorrunning{Deil, Donath, Terrier et al.}\n\n"
    author_str += "\\author{\n"

    for idx, author in enumerate(data["authors"]):
        label = f"inst:{idx}"
        author_str += f"\t{author} \\inst{{\\ref{{{label}}}}} \\and\n"

    author_str += "}\n\n"

    author_str += "\institute{\n"
    for idx, affiliation in enumerate(data["affiliations"]):
        label = f"inst:{idx}"
        affiliation = affiliation.replace("&", "\&")
        author_str += f"\t{affiliation} \\label{{{label}}} \\and\n"

    author_str += "}\n"

    authors_file = BASE_PATH / "src/text/0-authors.tex"

    log.info(f"Writing {authors_file}")

    with authors_file.open("w") as f:
        f.write(author_str)


if __name__ == "__main__":
    write_author_file()
