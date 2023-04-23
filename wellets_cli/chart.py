import tempfile

import matplotlib.pyplot as plt
import numpy as np

from wellets_cli.config import settings


def mk_fig():
    return plt.figure(figsize=(10, 6))


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


def show_chart(fig, path=None):
    if not path:
        path = tempfile.mktemp(suffix=".png")

    if settings.app.show_charts:
        plt.show()

    if settings.app.save_charts:
        fig.savefig(path)
        print("Saved to", path)

    return fig
