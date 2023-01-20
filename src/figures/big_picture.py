import logging

import click
import config
import matplotlib
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import numpy as np
from astropy import units as u
from astropy.table import Table
from matplotlib.patches import FancyArrow, FancyArrowPatch, PathPatch, Polygon
from matplotlib.text import TextPath
from matplotlib.ticker import MultipleLocator

from gammapy.estimators import FluxPoints
from gammapy.maps import Map

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

plt.rcParams["mathtext.fontset"] = "cm"

FIGSIZE = config.FigureSizeAA(aspect_ratio=1.8, width_aa="two-column")


GRAY = (0.7, 0.7, 0.7)
LIGHT_GRAY = "#ECECEC"
GP_GRAY = "#3D3D3D"
GP_ORANGE = "#FC3617"

DOC_ICON = np.array([(0, 0), (0, 0.85), (0.15, 1), (0.75, 1), (0.75, 0)])


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


def plot_lightcurve(ax):
    filename = config.BASE_PATH / "data/data-flow/light_curve.fits"
    log.info(f"Reading: {filename}")

    lc = FluxPoints.read(filename, format="lightcurve")
    lc.plot(ax=ax, sed_type="dnde", marker="None", label="1 TeV")
    ax.set_yscale("linear")
    format_dl5_ax(ax=ax)
    # ax.set_ylim(3e-11, 4e-10)
    # ax.set_xlim(53945.85, 53946.09)
    ax.legend(fontsize=8, labelspacing=0.1)
    ax.set_title("Lightcurves", color=GP_GRAY, pad=4)


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
    ax.set_title("SEDs", color=GP_GRAY, pad=4)


def plot_image(ax):
    filename = config.BASE_PATH / "data/data-flow/flux_image.fits"
    log.info(f"Reading: {filename}")
    m = Map.read(filename)
    m.plot(ax=ax, cmap="inferno", stretch="sqrt")
    ax.set_title("Images", color=GP_GRAY, pad=4)
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
    ax.set_xticks([1 / 3, 2 / 3])
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.grid(lw=1, color=GP_GRAY)
    ax.axvspan(0, 1 / 3, fc="lightgray", ec="None")
    ax.axhspan(0.75, 1, fc="lightgray", ec="None")
    ax.tick_params(axis="both", direction="in", color=GP_GRAY)

    for idx, xpos in enumerate([1 / 6, 3 / 6, 5 / 6]):
        for jdx, ypos in enumerate([7 / 8, 5 / 8, 3 / 8, 1 / 8]):
            plt.text(
                xpos,
                ypos,
                s=cell_text[jdx][idx],
                color=GP_GRAY,
                va="center",
                ha="center",
                size=8,
            )


def plot_gp_logo(ax, offset, fontsize=32, sub_title="", sub_title_shift=10):
    scale = fontsize / 32.0
    ax.text(
        offset[0] + scale,
        offset[1],
        s="$\gamma$",
        size=fontsize,
        va="bottom",
        color=GP_ORANGE,
    )

    ax.text(offset[0] + 6 * scale, offset[1], s="$\pi$", size=fontsize, color=GP_GRAY)
    ax.text(
        offset[0] + 6 * scale - 10,
        offset[1] - sub_title_shift,
        s=sub_title,
        size=12,
        color=GP_GRAY,
    )


def plot_instrument_logo(filename, fig, position, size=0.18, alpha=1.0):
    logo = plt.imread(filename)
    rect = [position[0], position[1], size, size]
    ax = fig.add_axes(rect)
    ax.axis("off")
    ax.imshow(logo, zorder=0, alpha=alpha)


def plot_gadf_icon(ax, offset, size=14, text=""):
    p = Polygon(
        offset + size * DOC_ICON,
        fc=LIGHT_GRAY,
        ec=GP_GRAY,
        lw=1.5,
        transform=ax.transData,
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
        size=12,
    )


def plot_instrument_logos(fig):
    left, offset = 0, 0
    left_cta_hess = 0
    plot_instrument_logo(
        "logos/cta.png", fig=fig, position=(-0.03, offset + 0.7), size=0.35
    )
    plot_instrument_logo(
        "logos/hess.jpg",
        fig=fig,
        position=(left_cta_hess - 0.02, offset + 0.56),
        size=0.20,
    )
    plot_instrument_logo(
        "logos/veritas.png", fig=fig, position=(left_cta_hess + 0.1, offset + 0.58)
    )
    plot_instrument_logo(
        "logos/fermi.png", fig=fig, position=(left + 0.15, offset + 0.1)
    )
    plot_instrument_logo("logos/hawc.png", fig=fig, position=(left, offset + 0.1))


def plot_package_logos(fig):
    plot_instrument_logo(
        "logos/numpy.png", fig=fig, position=(0.45, 0.15), size=0.15, alpha=0.5
    )
    plot_instrument_logo(
        "logos/scipy.png", fig=fig, position=(0.6, 0.15), size=0.15, alpha=0.5
    )
    plot_instrument_logo(
        "logos/astropy.png", fig=fig, position=(0.55, 0), size=0.15, alpha=0.5
    )


@click.command()
@click.option("--draft", is_flag=True)
def main(draft=True):
    fig = plt.figure(figsize=FIGSIZE.inch)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FIGSIZE.mm[0])
    ax.set_ylim(0, FIGSIZE.mm[1])

    ypos = 40
    plot_gp_logo(ax=ax, offset=(80, ypos), fontsize=120, sub_title="")
    plot_gadf_icon(ax=ax, offset=(68, ypos), text="DL3\nGADF", size=20)

    ax.tick_params(axis="both", direction="in", pad=-20)
    ax.xaxis.set_minor_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(10))

    plot_instrument_logos(fig=fig)
    plot_package_logos(fig=fig)

    # ax.text(s="Other IACTS")

    kwargs = {}
    kwargs["head_width"] = 7
    kwargs["head_length"] = 3

    # xpos = 130
    # width = 7
    # plot_arrow(ax, offset=(xpos, 15), dx=14, width=width, fc=LIGHT_GRAY, **kwargs)
    # plot_arrow(ax, offset=(xpos - 5, 35), dx=19, width=width, fc=LIGHT_GRAY, **kwargs)
    # plot_arrow(ax, offset=(xpos, 64), dx=14, width=width, fc=LIGHT_GRAY, **kwargs)
    # plot_arrow(ax, offset=(xpos, 96), dx=14, width=width, fc=LIGHT_GRAY, **kwargs)

    # ax.text(
    #     x=48,
    #     y=98,
    #     s="Events\n&\nIRFs",
    #     va="center",
    #     ha="center",
    #     color=GRAY,
    #     fontweight="black",
    #     size=10,
    # )

    if draft:
        plt.grid(alpha=0.2, lw=0.5)
    else:
        ax.set_axis_off()

    width, height = 25, 20.0 / 6 * 5
    left = 153
    ax_image = add_sub_axes(ax, [left, 72, width, height])
    plot_image(ax=ax_image)

    ax_fp = add_sub_axes(ax, [left, 40, width, height])
    plot_sed(ax=ax_fp)

    ax_lc = add_sub_axes(ax, [left, 8, width, height])
    plot_lightcurve(ax=ax_lc)

    filename = "big-picture.pdf"
    log.info(f"Writing {filename}")
    plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    main()
