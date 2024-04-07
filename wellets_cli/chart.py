import tempfile

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from wellets_cli.config import settings


def mk_fig():
    return plt.figure(figsize=(10, 6))


def show_chart(fig, path=None):
    if not path:
        path = tempfile.mktemp(suffix=".png")

    if settings.show_charts:
        plt.show()

    if settings.save_charts:
        fig.savefig(path)
        print("Saved to", path)

    return fig


def plot_balance(fig, history, label=None):
    xs = np.array([x.timestamp for x in history])
    ys = np.array([x.balance for x in history])

    ax = fig.add_subplot(1, 1, 1)
    fig.autofmt_xdate()

    ax.plot(xs, ys, "-o", label=label)
    ax.legend()
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance")

    for i, balance in enumerate(ys):
        ax.annotate(
            f"{balance:.2f}",
            (xs[i], balance),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
        )

    return fig


def plot_allocation(fig, allocation):
    labels = np.array([x.asset.currency.acronym for x in allocation])
    values = np.array([x.allocation for x in allocation])

    ax = fig.add_subplot(1, 1, 1)
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")

    return fig


def plot_price(fig, date, price, *, label, xlabel="Date", ylabel="Price"):
    from matplotlib.dates import DateFormatter

    xs = np.array(date)
    ys = np.array(price)

    ax = fig.gca()

    ax.plot(xs, ys, label=label, linewidth=0.8)

    ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    return fig


def plot_exposition(fig, exposition: float):
    ax = fig.gca()
    ax.axhline(
        y=exposition, color="black", linestyle="--", label="Exposition", linewidth=0.8
    )

    xmin, _ = ax.get_xlim()

    ax.annotate(
        f"{exposition:.2f}",
        (xmin, exposition),
        xytext=(0, 4),
        textcoords="offset points",
        ha="left",
    )
    return fig


def plot_position(fig, date, position, size, kind):
    markersize = mpl.rcParams["lines.markersize"] ** 2

    xs = np.array(date)
    ys = np.array(position)
    color = np.array(["green" if k == "buy" else "red" for k in kind])
    size = markersize / 4 + 1.2 * np.array(size) * markersize

    ax = fig.gca()

    ax.scatter(xs, ys, s=size, color=color)

    return fig


def plot_ema(fig, x, y, window, color):
    ax = fig.gca()

    y = np.array(y)
    y = np.convolve(y, np.ones(window), "valid") / window
    x = x[window - 1 :]

    ax.plot(x, y, label=f"EMA {window}", linewidth=0.6, linestyle="--", color=color)

    return fig


def xdate_fmt(fig):
    from matplotlib.dates import DateFormatter

    date_fmt = DateFormatter(settings.date_format)

    fig.autofmt_xdate()

    ax = fig.gca()
    ax.xaxis.set_major_formatter(date_fmt)

    return fig
