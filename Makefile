# Snakemake options. Override by calling, e.g., `make ms.pdf OPTIONS="..."`
OPTIONS ?= -c1


# Settings
export OPTIONS
.PHONY: Makefile
SHOWYOURWORK := $(shell test -f showyourwork/LICENSE && echo 1 || echo 0)
GAMMAPY := $(shell test -f gammapy/LICENSE.rst && echo 1 || echo 0)


# Default target: generate the article
ms.pdf: showyourwork_setup
	@$(MAKE) -C showyourwork ms.pdf


# Ensure we've cloned the showyourwork submodule
showyourwork_setup:
	@if [ "$(SHOWYOURWORK)" = "0" ]; then \
		echo "Setting up the showyourwork submodule...";\
		git submodule init;\
		git submodule update;\
	fi

# Ensure we've cloned the gammapy submodule
gammapy_setup:
	@if [ "$(GAMMAPY)" = "0" ]; then \
		echo "Setting up the gammapy submodule...";\
		git submodule init;\
		git submodule update;\
	fi

# Route all targets to showyourwork/Makefile
%: Makefile showyourwork_setup gammapy_setup
	@$(MAKE) -C showyourwork $@
