# User config
configfile: "showyourwork.yml"


# Import the showyourwork module
module showyourwork:
    snakefile:
        "showyourwork/workflow/Snakefile"
    config:
        config


# Use all default rules
use rule * from showyourwork

rule minted:
    input:
        "src/code-examples/minted.py"
    output:
        "src/code-examples/generated/gp_data.tex",
        "src/code-examples/generated/gp_catalogs.tex",
        "src/code-examples/generated/gp_datasets.tex",
        "src/code-examples/generated/gp_makers.tex",
        "src/code-examples/generated/gp_maps.tex",
        "src/code-examples/generated/gp_models.tex",
        "src/code-examples/generated/gp_estimators.tex",
    conda:
        "environment.yml"
    shell:
        "cd src/code-examples && python minted.py"

# Custom rule to download Fermi dataset
rule download_fermi:
    output:
        "src/data/fermi-ts-map/input/fermi-3fhl-gc-counts-cube.fits.gz",
        "src/data/fermi-ts-map/input/fermi-3fhl-gc-background-cube.fits.gz",
        "src/data/fermi-ts-map/input/fermi-3fhl-gc-exposure-cube.fits.gz",
        "src/data/fermi-ts-map/input/fermi-3fhl-gc-psf-cube.fits.gz",
    shell:
        "cd scripts && python download.py fermi-gc"

# Custom rule to prepare Fermi dataset
rule prepare_fermi:
    input:
        "src/data/fermi-ts-map/input/fermi-3fhl-gc-counts-cube.fits.gz",
        "src/data/fermi-ts-map/input/fermi-3fhl-gc-background-cube.fits.gz",
        "src/data/fermi-ts-map/input/fermi-3fhl-gc-exposure-cube.fits.gz",
        "src/data/fermi-ts-map/input/fermi-3fhl-gc-psf-cube.fits.gz",
    output:
        "src/data/fermi-ts-map/fermi-ts-maps.fits",
        "src/data/fermi-ts-map/fermi-ts-maps.fits_model.yaml",
    shell:
        "cd src/data/fermi-ts-map && python make.py"