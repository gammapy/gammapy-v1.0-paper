<p align="center">
<br>
<a href="https://github.com/gammapy/gammapy-v1.0-paper/actions/workflows/showyourwork.yml">
<img src="https://github.com/gammapy/gammapy-v1.0-paper/actions/workflows/showyourwork.yml/badge.svg" alt="Article status"/>
</a>
<a href="https://github.com/gammapy/gammapy-v1.0-paper/raw/main-pdf/arxiv.tar.gz">
<img src="https://img.shields.io/badge/article-tarball-blue.svg?style=flat" alt="Article tarball"/>
</a>
<a href="https://github.com/gammapy/gammapy-v1.0-paper/raw/main-pdf/dag.pdf">
<img src="https://img.shields.io/badge/article-dag-blue.svg?style=flat" alt="Article graph"/>
</a>
<a href="https://github.com/gammapy/gammapy-v1.0-paper/raw/main-pdf/ms.pdf">
<img src="https://img.shields.io/badge/article-pdf-blue.svg?style=flat" alt="Read the article"/>
</a>
</p>

# Gammapy v1.0 Paper

This is the repository for the Gammapy v1.0 paper. The goal is to produce a paper
that accompanies the v1.0 release of Gammapy. It will describe the package design,
features and applications.

The paper will be submitted to [Astronomy and Astrophysics](https://www.aanda.org/).
We could consider jointly submitting to the [Journal of Open Source Software](https://joss.theoj.org) 
as well.

We invite you to become a co-author if you either have [contributed to the 
Gammapy core package](https://github.com/gammapy/gammapy/graphs/contributors)
or have an [official role](https://gammapy.org/team.html) in the Gammapy project.

## Getting Started
To get started with paper writing, make a fork of the repository and clone the
forked repository to your local machine:

    git clone https://github.com/yourgithub/gammapy-v1.0-paper.git

Now enter the local folder of the repository, create the corresponding `conda`
environment and activate it:

    conda env create -f environment.yml
    conda activate gammapy-v1.0-paper

To actually build the paper and paper figures locally just use:

    make

To clean up failed executions you can use:

    make clean

You can use the editor of your choice to modify the files in `src/text/*.tex`.
If you need to add a figure, please either put the corresponding `matplotlib`/ `python`
script in `src/figures` or put a pre-generated image in `src/static`. However
for reproducibility it is encouraged to submit the `python` script. The latex figure
will be linked by the label provided in the figure environment see
[showyourwork default figure generation](https://showyourwork.readthedocs.io/en/stable/custom/#default-figure-generation)
for details.

## Git pre-commit hooks
To ensure a consistent formatting of the `.tex` files and check for missing labels,
typos etc. the repository defines pre-commit hooks. Right now the setting is very 
strict such that commit is prevented if any pre-commit hook fails. If you find 
any un-reosonable behaviour of the hooks please report.
