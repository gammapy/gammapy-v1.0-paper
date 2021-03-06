import logging
import click
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.lines as mlines
import matplotlib.transforms as mtrans
from matplotlib.patches import Polygon, FancyArrow, PathPatch, FancyArrowPatch
from matplotlib.text import TextPath
from matplotlib.ticker import MultipleLocator
from astropy import units as u
from astropy.table import Table
from gammapy.estimators import FluxPoints
from gammapy.maps import Map
import config


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

plt.rcParams["mathtext.fontset"] = "cm"

FIGSIZE = config.FigureSizeAA(aspect_ratio=1.3740, width_aa="two-column")


GRAY = (0.7, 0.7, 0.7)
LIGHT_GRAY = "#ECECEC"
GP_GRAY = "#3D3D3D"
GP_ORANGE = "#FC3617"

DOC_ICON = np.array(
    [(0, 0), (0, 0.85), (0.15, 1), (0.75, 1), (0.75, 0)]
)

def axis_to_fig(axis):
    fig = axis.figure

    def transform(coord):
        return fig.transFigure.inverted().transform(axis.transData.transform(coord))

    return transform


def add_sub_axes(axis, rect):
    fig = axis.figure
    left, bottom, width, height = rect
    trans = axis_to_fig(axis)
    figleft, figbottom = trans((left, bottom))
    figwidth, figheight = trans([width, height]) - trans([0, 0])
    return fig.add_axes([figleft, figbottom, figwidth, figheight])



def plot_arrow(ax, offset, dx=10, dy=0, **kwargs):
    kwargs.setdefault("fc", GP_GRAY)
    kwargs.setdefault("ec", "None")
    kwargs.setdefault("head_width", 3)
    kwargs.setdefault("head_length", 3)
    kwargs.setdefault("length_includes_head", True)
    kwargs.setdefault("width", 1)

    arrow = FancyArrow(
        offset[0], offset[1], dx=dx, dy=dy, transform=ax.transData, **kwargs
    )
    ax.add_artist(arrow)


def plot_curved_arrow(ax, posA, posB, **kwargs):
    kwargs.setdefault("connectionstyle", "bar,angle=90,fraction=-0.25")
    kwargs.setdefault("fc", GP_GRAY)
    kwargs.setdefault("ec", GRAY)
    kwargs.setdefault("lw", 3)
    kwargs.setdefault("arrowstyle", "-|>, head_length=3.5, head_width=2")
    kwargs.setdefault("capstyle", "butt")
    kwargs.setdefault("joinstyle", "miter")

    arrow = FancyArrowPatch(posA=posA, posB=posB, transform=ax.transData, **kwargs)
    ax.add_artist(arrow)


def format_dl5_ax(ax):
    for key, spine in ax.spines.items():
        spine.set_color(GP_GRAY)
        spine.set_lw(1)

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.patch.set_alpha(0)

    ax.tick_params(axis="both", direction="in", which="both")

    ax.set_xticklabels([])
    ax.set_yticklabels([])


def plot_catalog(ax):
    ax.set_title("Source Catalogs", color=GP_GRAY, pad=4)
    cell_text = [
        ["Name", "Flux", "Size"],
        ["SNR", 1e-12, "1 deg"],
        ["PWN", 1e-11, "0.2 deg"],
        ["GRB", 1e-10, "0 deg"],
    ]

    format_dl5_ax(ax=ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([1/3, 2/3])
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.grid(lw=1, color=GP_GRAY)
    ax.axvspan(0, 1/3, fc="lightgray", ec="None")
    ax.axhspan(0.75, 1, fc="lightgray", ec="None")
    ax.tick_params(axis="both", direction="in", color=GP_GRAY)

    for idx, xpos in enumerate([1/6, 3/6, 5/6]):
        for jdx, ypos in enumerate([7/8, 5/8, 3/8, 1/8]):
            plt.text(xpos, ypos, s=cell_text[jdx][idx], color=GP_GRAY, va="center", ha="center", size=8)


def plot_lightcurve(ax):
    filename = config.BASE_PATH / "data/data-flow/light_curve.fits"
    log.info(f"Reading: {filename}")

    lc = FluxPoints.read(filename, format="lightcurve")
    lc.plot(ax=ax, sed_type="dnde", marker="None", label="1 TeV")
    ax.set_yscale("linear")
    format_dl5_ax(ax=ax)
    #ax.set_ylim(3e-11, 4e-10)
    #ax.set_xlim(53945.85, 53946.09)
    ax.legend(fontsize=8, labelspacing=0.1)


def plot_sed(ax):
    filename = config.BASE_PATH / "data/data-flow/flux_points.fits"
    log.info(f"Reading: {filename}")

    flux_points = FluxPoints.read(filename, sed_type="likelihood")
    ax.yaxis.set_units(u.Unit("erg cm-2 s-1"))
    flux_points.plot(
        ax=ax,
        sed_type="e2dnde",
        color="darkorange",
        elinewidth=1,
        markeredgewidth=1,
    )

    flux_points.plot_ts_profiles(ax=ax, sed_type="e2dnde", add_cbar=False)
    format_dl5_ax(ax=ax)
    ax.set_title("SEDs & Lightcurves", color=GP_GRAY, pad=4)


def plot_image(ax):
    filename = config.BASE_PATH / "data/data-flow/flux_image.fits"
    log.info(f"Reading: {filename}")
    m = Map.read(filename)
    m.plot(ax=ax, cmap="inferno", stretch="sqrt")
    ax.set_title("Flux & TS Maps", color=GP_GRAY, pad=4)
    format_dl5_ax(ax=ax)


def plot_event_list(ax):
    ax.set_title("Event list", color=GP_GRAY, pad=4)
    cell_text = [
        ["Lon", "Lat", "Energy"],
        [0.1, 0.1, "1 TeV"],
        [0.2, 0.2, "3 TeV"],
        [0.3, 0.3, "5 TeV"],
    ]

    format_dl5_ax(ax=ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([1/3, 2/3])
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.grid(lw=1, color=GP_GRAY)
    ax.axvspan(0, 1/3, fc="lightgray", ec="None")
    ax.axhspan(0.75, 1, fc="lightgray", ec="None")
    ax.tick_params(axis="both", direction="in", color=GP_GRAY)

    for idx, xpos in enumerate([1/6, 3/6, 5/6]):
        for jdx, ypos in enumerate([7/8, 5/8, 3/8, 1/8]):
            plt.text(xpos, ypos, s=cell_text[jdx][idx], color=GP_GRAY, va="center", ha="center", size=8)


def plot_data_levels(ax, ypos=123):
    # data levels
    kwargs = {}
    kwargs["va"] = "center"
    kwargs["ha"] = "center"
    kwargs["transform"] = ax.transData
    kwargs["color"] = GP_GRAY
    kwargs["size"] = 24

    #ax.text(20, ypos, "DL<3", **kwargs, alpha=0.3)
    #ax.text(72, ypos, "DL3", **kwargs)
    #ax.text(72, 12, "DL4", **kwargs)
    ax.text(160, ypos, "DL5/6", **kwargs)

    kwargs["size"] = 12
    #ax.text(20, ypos - 7, "Inst. level data", **kwargs, alpha=0.3)
    #ax.text(72, ypos - 7, "$\mathsf{\gamma}$-like events & IRFs", **kwargs)
    #ax.text(72, 12 - 7, "Binned data", **kwargs)
    ax.text(160, ypos - 7, "Science products", **kwargs)

    # Arrows
    #plot_arrow(ax, offset=(35.5, ypos), dx=15, fc=GRAY, alpha=0.3)
    #plot_arrow(ax, offset=(72.5, ypos), dx=25, fc=GRAY)
    #plot_arrow(ax, offset=(122.5, ypos), dx=20, fc=GRAY)

    kwargs["color"] = GRAY
    #ax.text(47.5, ypos - 15, "Data reduction", **kwargs)
    #ax.text(123, ypos - 20, "Likelihood \n fitting", **kwargs)


def plot_gp_logo(ax, offset, fontsize=32, sub_title="", sub_title_shift=10):
    scale = fontsize / 32.
    ax.text(
        offset[0] + scale,
        offset[1],
        s="$\gamma$",
        size=fontsize,
        va="bottom",
        color=GP_ORANGE,
    )

    ax.text(offset[0] + 6 * scale, offset[1], s="$\pi$", size=fontsize, color=GP_GRAY)
    ax.text(offset[0] + 6 * scale - 10, offset[1] - sub_title_shift, s=sub_title, size=12, color=GP_GRAY)


def plot_instrument_logo(filename, fig, position, size=0.18):
    logo = plt.imread(filename)
    rect = [position[0], position[1], size, size]
    ax = fig.add_axes(rect)
    ax.axis("off")
    ax.imshow(logo, zorder=0)



def plot_gadf_icon(ax, offset, size=14, text=""):
    p = Polygon(
        offset + size * DOC_ICON, fc=LIGHT_GRAY, ec=GP_GRAY, lw=1.5, transform=ax.transData
    )
    ax.add_artist(p)

    ax.text(
        offset[0] + size * 0.75 / 2,
        offset[1] + size / 2,
        s=text,
        va="center",
        ha="center",
        color=GP_GRAY,
        fontweight="black",
        size=12
    )


def plot_dl3_block(ax):
    xpos = 27
    ymax = 0.84
    ax.axvspan(xpos + 8, xpos + 28, fc=LIGHT_GRAY, ec="None", ymin=0.5, ymax=ymax)

    kwargs = {}
    kwargs["head_width"] = 10
    kwargs["head_length"] = 3
    plot_arrow(ax, offset=(xpos, 102), dx=11, width=13, fc=LIGHT_GRAY, **kwargs)
    plot_arrow(ax, offset=(xpos, 76), dx=11, width=13, fc=LIGHT_GRAY, **kwargs)
    #plot_arrow(ax, offset=(xpos, 89), dx=41, width=13, fc=LIGHT_GRAY, **kwargs)


def plot_instrument_logos(fig):
    left, offset = 0.01, 0
    left_cta_hess = 0.01
    plot_instrument_logo("logos/cta.png", fig=fig, position=(-0.03, offset + 0.73), size=0.3)
    plot_instrument_logo("logos/hess.jpg", fig=fig, position=(left_cta_hess, offset + 0.6))
    plot_instrument_logo("logos/fermi.png", fig=fig, position=(left + 0.01, offset + 0.28))
    plot_instrument_logo("logos/hawc.png", fig=fig, position=(left, offset + 0.1))


@click.command()
@click.option("--draft", is_flag=True)
def main(draft=True):
    fig = plt.figure(figsize=FIGSIZE.inch)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FIGSIZE.mm[0])
    ax.set_ylim(0, FIGSIZE.mm[1])

    plot_gp_logo(ax=ax, offset=(86, 28), fontsize=100, sub_title="Modeling & \nFitting")

    ax.tick_params(axis="both", direction="in", pad=-20)
    ax.xaxis.set_minor_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(10))

    plot_data_levels(ax=ax)

    plot_instrument_logos(fig=fig)
    #ax.text(s="Other IACTS")

    plot_gadf_icon(ax=ax, offset=(63, 85), text="DL3\nGADF", size=24)
    plot_gadf_icon(ax=ax, offset=(63, 20), text="DL4\nGADF", size=24)
    plot_gp_logo(
        ax=ax, offset=(59, 62), fontsize=48, sub_title="Data Reduction", sub_title_shift=4,
    )

    ymax = 0.76
    ax.axvspan(130, 137, fc=LIGHT_GRAY, ec="None", ymin=0.09, ymax=ymax)
    #
    # ymax = 0.84
    # ax.axvspan(65, 75, fc=LIGHT_GRAY, ec="None", ymin=0.08, ymax=ymax)
    # ax.axvspan(65, 75, fc=LIGHT_GRAY, ec="None", ymin=0.08, ymax=ymax)

    kwargs = {}
    kwargs["head_width"] = 7
    kwargs["head_length"] = 3

    plot_arrow(ax, offset=(72, 83), dy=-9, dx=0, width=7, fc=LIGHT_GRAY, **kwargs)
    plot_arrow(ax, offset=(72, 55), dy=-9, dx=0, width=7, fc=LIGHT_GRAY, **kwargs)

    plot_arrow(ax, offset=(84, 35), dx=10, width=7, fc=LIGHT_GRAY, **kwargs)
    plot_arrow(ax, offset=(37, 98), dx=24, width=14, fc=LIGHT_GRAY, head_width=14)

    xpos = 130
    width = 7
    plot_arrow(ax, offset=(xpos, 15), dx=14, width=width, fc=LIGHT_GRAY, **kwargs)
    plot_arrow(ax, offset=(xpos - 5, 35), dx=19, width=width, fc=LIGHT_GRAY, **kwargs)
    plot_arrow(ax, offset=(xpos, 64), dx=14, width=width, fc=LIGHT_GRAY, **kwargs)
    plot_arrow(ax, offset=(xpos, 96), dx=14, width=width, fc=LIGHT_GRAY, **kwargs)

    # thin arrows
    kwargs["head_width"] = 5
    kwargs["head_length"] = 3
    plot_arrow(ax, offset=(37, 33), dx=24, width=5, fc=LIGHT_GRAY, **kwargs)
    plot_arrow(ax, offset=(37, 39), dx=8, width=5, fc=LIGHT_GRAY, head_length=0)
    plot_arrow(ax, offset=(46, 36.5), dx=0, dy=53.5, width=5, fc=LIGHT_GRAY, head_length=0)
    plot_arrow(ax, offset=(45, 87.5), dx=16, width=5, fc=LIGHT_GRAY, **kwargs)


    ax.text(
        x=48,
        y=98,
        s="Events\n&\nIRFs",
        va="center",
        ha="center",
        color=GRAY,
        fontweight="black",
        size=10
    )

    ax.text(
        x=46,
        y=33,
        s="IRFs",
        va="center",
        ha="center",
        color=GRAY,
        fontweight="black",
        size=10
    )

    ax.text(
        x=46,
        y=60,
        s="Events",
        va="center",
        ha="center",
        color=GRAY,
        fontweight="black",
        size=10,
        rotation=90
    )

    if draft:
        plt.grid(alpha=0.2, lw=0.5)
    else:
        ax.set_axis_off()

    ax_image = add_sub_axes(ax, [145, 54, 30, 20])
    plot_image(ax=ax_image)

    ax_fp = add_sub_axes(ax, [145, 25, 30, 20])
    plot_sed(ax=ax_fp)

    ax_lc = add_sub_axes(ax, [145, 4, 30, 20])
    plot_lightcurve(ax=ax_lc)

    ax_cat = add_sub_axes(ax, [145, 86, 30, 20])
    plot_catalog(ax=ax_cat)

    filename = "big-picture.pdf"
    log.info(f"Writing {filename}")
    plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    main()
