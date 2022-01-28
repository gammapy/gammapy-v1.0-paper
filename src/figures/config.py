"""General configuration for mpl plotting scripts"""
from pathlib import Path
from astropy import untis as u
from astropy.units import imperial

BASE_PATH = Path(__file__).parent.parent


FIGURE_WIDTH_AA = {
    "single-column": 90 * u.mm,
    "two-column": 180 * u.mm,
    "intermediate": 120 * u.mm,
}


def get_figure_size_aa(aspect_ratio=1, width_aa="single-column"):
    """Get figure size in inches"""
    width = FIGURE_WIDTH_AA[width_aa]
    height = width / aspect_ratio
    return width.to_value(imperial.inch), height.to_value(imperial.inch)


