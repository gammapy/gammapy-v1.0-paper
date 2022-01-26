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
        "src/snippets/minted.py"
    output:
        "src/snippets/generated/gp_data.tex"
    conda:
        "environment.yml"
    shell:
        "cd src/snippets && python minted.py"

