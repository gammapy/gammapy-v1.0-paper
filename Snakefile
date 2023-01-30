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
        "src/code-examples/snippets/gp_catalogs.py",
        "src/code-examples/snippets/gp_data.py",
        "src/code-examples/snippets/gp_datasets.py",
        "src/code-examples/snippets/gp_estimators.py",
        "src/code-examples/snippets/gp_makers.py",
        "src/code-examples/snippets/gp_models.py",
        "src/code-examples/snippets/gp_stats.py",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_023523.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_023526.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_023559.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_023592.fits.gz",
        "src/data/input/cta-1dc-gc/cta-1dc-gc.fits.gz",
        "src/data/input/catalogs/fermi/gll_psc_v28.fit.gz",
        "src/data/input/joint-crab/spectra/hess/pha_obs23523.fits",
        "src/data/input/joint-crab/spectra/hess/arf_obs23523.fits",
        "src/data/input/joint-crab/spectra/hess/rmf_obs23523.fits",
        "src/data/input/joint-crab/spectra/hess/bkg_obs23523.fits",
    output:
        "src/code-examples/generated/gp_data.tex",
        "src/code-examples/generated/gp_catalogs.tex",
        "src/code-examples/generated/gp_datasets.tex",
        "src/code-examples/generated/gp_makers.tex",
        "src/code-examples/generated/gp_maps.tex",
        "src/code-examples/generated/gp_models.tex",
        "src/code-examples/generated/gp_estimators.tex",
        "src/code-examples/generated/gp_stats.tex",
        "src/code-examples/generated-output/gp_data.tex",
        "src/code-examples/generated-output/gp_datasets.tex",
        "src/code-examples/generated-output/gp_maps.tex",
        "src/code-examples/generated-output/gp_models.tex",
        "src/code-examples/generated-output/gp_stats.tex",
    conda:
        "environment.yml"
    shell:
        "cd src/code-examples && python minted.py"

# Custom rule to download Fermi dataset
rule download_fermi:
    output:
        "src/data/input/fermi-3fhl-gc/fermi-3fhl-gc-counts-cube.fits.gz",
        "src/data/input/fermi-3fhl-gc/fermi-3fhl-gc-background-cube.fits.gz",
        "src/data/input/fermi-3fhl-gc/fermi-3fhl-gc-exposure-cube.fits.gz",
        "src/data/input/fermi-3fhl-gc/fermi-3fhl-gc-psf-cube.fits.gz",
        "src/data/input/catalogs/fermi/gll_psc_v28.fit.gz",
    conda:
        "environment.yml"
    shell:
        "cd scripts && python download.py fermi-gc"

# Custom rule to prepare Fermi dataset
rule prepare_fermi:
    input:
        "src/data/input/fermi-3fhl-gc/fermi-3fhl-gc-counts-cube.fits.gz",
        "src/data/input/fermi-3fhl-gc/fermi-3fhl-gc-background-cube.fits.gz",
        "src/data/input/fermi-3fhl-gc/fermi-3fhl-gc-exposure-cube.fits.gz",
        "src/data/input/fermi-3fhl-gc/fermi-3fhl-gc-psf-cube.fits.gz",
    output:
        "src/data/fermi-ts-map/fermi-ts-maps.fits",
        "src/data/fermi-ts-map/fermi-ts-maps.fits_model.yaml",
    conda:
        "environment.yml"
    shell:
        "cd src/data/fermi-ts-map && python make.py"

# Custom rule to download CTA dataset
rule download_cta:
    output:
        "src/data/input/cta-1dc/index/gps/hdu-index.fits.gz",
        "src/data/input/cta-1dc/index/gps/obs-index.fits.gz",
        "src/data/input/cta-1dc/data/baseline/gps/gps_baseline_110380.fits",
        "src/data/input/cta-1dc/data/baseline/gps/gps_baseline_111140.fits",
        "src/data/input/cta-1dc/data/baseline/gps/gps_baseline_111159.fits",
        "src/data/input/cta-1dc/caldb/data/cta/1dc/bcf/South_z20_50h/irf_file.fits",
        "src/data/input/cta-1dc-gc/cta-1dc-gc.fits.gz",
    conda:
        "environment.yml"
    shell:
        "cd scripts && python download.py cta-1dc"


# Custom rule to prepare CTA dataset
rule prepare_cta:
    input:
        "src/data/input/cta-1dc/index/gps/hdu-index.fits.gz",
        "src/data/input/cta-1dc/index/gps/obs-index.fits.gz",
        "src/data/input/cta-1dc/data/baseline/gps/gps_baseline_110380.fits",
        "src/data/input/cta-1dc/data/baseline/gps/gps_baseline_111140.fits",
        "src/data/input/cta-1dc/data/baseline/gps/gps_baseline_111159.fits",
        "src/data/input/cta-1dc/caldb/data/cta/1dc/bcf/South_z20_50h/irf_file.fits",
    output:
        "src/data/cta-galactic-center/datasets/datasets.yaml",
        "src/data/cta-galactic-center/datasets/pha_obsobs-110380.fits",
        "src/data/cta-galactic-center/datasets/pha_obsobs-111140.fits",
        "src/data/cta-galactic-center/datasets/pha_obsobs-111159.fits",
        "src/data/cta-galactic-center/flux-points.fits",
        "src/data/cta-galactic-center/stacked-counts.fits",
    conda:
        "environment.yml"
    shell:
        "cd src/data/cta-galactic-center && python make.py"

# Custom rule to prepare cube analysis
rule prepare_cube:
    input:
        "src/data/input/cta-1dc/index/gps/hdu-index.fits.gz",
        "src/data/input/cta-1dc/index/gps/obs-index.fits.gz",
        "src/data/input/cta-1dc/data/baseline/gps/gps_baseline_110380.fits",
        "src/data/input/cta-1dc/data/baseline/gps/gps_baseline_111140.fits",
        "src/data/input/cta-1dc/data/baseline/gps/gps_baseline_111159.fits",
        "src/data/input/cta-1dc/caldb/data/cta/1dc/bcf/South_z20_50h/irf_file.fits",
    output:
        "src/data/cube-analysis/significance_map.fits",
        "src/data/cube-analysis/best-fit-model.yaml",
        "src/data/cube-analysis/residual_map.fits",
        "src/data/cube-analysis/excess_counts.fits",
        "src/data/cube-analysis/npred_1.fits",
        "src/data/cube-analysis/npred_2.fits",
        "src/data/cube-analysis/npred_3.fits",
    conda:
        "environment.yml"
    shell:
        "cd src/data/cube-analysis && python make.py"


# Custom rule to download H.E.S.S. dataset
rule download_hess:
    output:
        "src/data/input/hess-dl3-dr1/hdu-index.fits.gz",
        "src/data/input/hess-dl3-dr1/obs-index.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033787.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033788.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033789.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033790.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033791.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033792.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033793.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033794.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033795.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033796.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033797.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033798.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033799.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033800.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033801.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_023523.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_023526.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_023559.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_023592.fits.gz",
        "src/data/input/joint-crab/spectra/hess/pha_obs23523.fits",
        "src/data/input/joint-crab/spectra/hess/arf_obs23523.fits",
        "src/data/input/joint-crab/spectra/hess/rmf_obs23523.fits",
        "src/data/input/joint-crab/spectra/hess/bkg_obs23523.fits",
    conda:
        "environment.yml"
    shell:
        "cd scripts && python download.py pks-flare"


# Custom rule to prepare H.E.S.S. dataset
rule prepare_hess:
    input:
        "src/data/input/hess-dl3-dr1/hdu-index.fits.gz",
        "src/data/input/hess-dl3-dr1/obs-index.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033787.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033788.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033789.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033790.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033791.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033792.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033793.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033794.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033795.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033796.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033797.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033798.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033799.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033800.fits.gz",
        "src/data/input/hess-dl3-dr1/data/hess_dl3_dr1_obs_id_033801.fits.gz",
    output:
        "src/data/lightcurve/pks2155_flare_lc.fits.gz",
    conda:
        "environment.yml"
    shell:
        "cd src/data/lightcurve && python make.py"


# Custom rule to download multi-instrument data, Fermi-LAT
rule download_multi_instrument:
    output:
        "src/data/input/fermi-3fhl-crab/Fermi-LAT-3FHL_data_Fermi-LAT.fits",
        "src/data/input/fermi-3fhl-crab/Fermi-LAT-3FHL_iem.fits",
        "src/data/input/fermi-3fhl-crab/Fermi-LAT-3FHL_datasets.yaml",
        "src/data/input/fermi-3fhl-crab/Fermi-LAT-3FHL_models.yaml",
        "src/data/input/magic/rad_max/data/hdu-index.fits.gz",
        "src/data/input/magic/rad_max/data/obs-index.fits.gz",
        "src/data/input/magic/rad_max/data/20131004_05029747_DL3_CrabNebula-W0.40+035.fits",
        "src/data/input/magic/rad_max/data/20131004_05029748_DL3_CrabNebula-W0.40+215.fits",
        "src/data/input/hawc_crab/HAWC19_flux_points.fits",
    conda:
        "environment.yml"
    shell:
        "cd scripts && python download.py multi-instrument"


# Custom rule to prepare multi-instrument datasets
rule prepare_multi_instrument:
    input:
        "src/data/input/fermi-3fhl-crab/Fermi-LAT-3FHL_data_Fermi-LAT.fits",
        "src/data/input/fermi-3fhl-crab/Fermi-LAT-3FHL_iem.fits",
        "src/data/input/fermi-3fhl-crab/Fermi-LAT-3FHL_datasets.yaml",
        "src/data/input/fermi-3fhl-crab/Fermi-LAT-3FHL_models.yaml",
        "src/data/input/magic/rad_max/data/hdu-index.fits.gz",
        "src/data/input/magic/rad_max/data/obs-index.fits.gz",
        "src/data/input/magic/rad_max/data/20131004_05029747_DL3_CrabNebula-W0.40+035.fits",
        "src/data/input/magic/rad_max/data/20131004_05029748_DL3_CrabNebula-W0.40+215.fits",
        "src/data/input/hawc_crab/HAWC19_flux_points.fits",
    output:
        "src/data/multi-instrument/datasets/flux_points/crab_magic_flux_points.fits",
        "src/data/multi-instrument/datasets/flux_points/crab_fermi_flux_points.fits",
        "src/data/multi-instrument/results/crab_multi_instrument_fit_lp_model.yaml",
        "src/data/multi-instrument/results/crab_multi_instrument_fit_naima_ic_model.yaml",
    conda:
        "environment.yml"
    shell:
        "cd src/data/multi-instrument && python make.py"


# Custom rule to download multi-instrument data, Fermi-LAT
rule download_hawc_dl3:
    output:
        "src/data/input/hawc/crab_events_pass4/hdu-index-table-GP-Crab.fits.gz",
        "src/data/input/hawc/crab_events_pass4/obs-index-table-GP-Crab.fits.gz",
        "src/data/input/hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin5GP.fits.gz",
        "src/data/input/hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin6GP.fits.gz",
        "src/data/input/hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin7GP.fits.gz",
        "src/data/input/hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin8GP.fits.gz",
        "src/data/input/hawc/crab_events_pass4/irfs/EffectiveAreaMap_Crab_fHitbin9GP.fits.gz",
        "src/data/input/hawc/crab_events_pass4/irfs/PSFMap_Crab_fHitbin5GP.fits.gz",
        "src/data/input/hawc/crab_events_pass4/irfs/PSFMap_Crab_fHitbin6GP.fits.gz",
        "src/data/input/hawc/crab_events_pass4/irfs/PSFMap_Crab_fHitbin7GP.fits.gz",
        "src/data/input/hawc/crab_events_pass4/irfs/PSFMap_Crab_fHitbin8GP.fits.gz",
        "src/data/input/hawc/crab_events_pass4/irfs/PSFMap_Crab_fHitbin9GP.fits.gz",
    conda:
        "environment.yml"
    shell:
        "cd scripts && python download.py hawc-dl3"

# Custom rule for the codestats
rule codestats:
    input:
        "src/figures/codestats.py"
    output:
        "src/tables/generated/codestats.tex",
    conda:
        "environment.yml"
    shell:
        "cd src/figures/ && python codestats.py"
