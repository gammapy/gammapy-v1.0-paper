"""General configuration for mpl plotting scripts"""
from pathlib import Path
from astropy import units as u
from astropy.units import imperial
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 8})

BASE_PATH = Path(__file__).parent.parent


FIGURE_WIDTH_AA = {
    "single-column": 90 * u.mm,
    "two-column": 180 * u.mm,
    "intermediate": 120 * u.mm,
}


class FigureSizeAA:
    """Figure size A&A"""
    def __init__(self, aspect_ratio=1, width_aa="single-column"):
        self.width = FIGURE_WIDTH_AA[width_aa]
        self.height = self.width / aspect_ratio

    @property
    def inch(self):
        """Figure size in inch"""
        return self.width.to_value(imperial.inch), self.height.to_value(imperial.inch)

    @property
    def mm(self):
        """Figure size in mm"""
        return self.width.value, self.height.value

