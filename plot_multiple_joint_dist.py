# plot_multiple_joint_dist.py
# https://github.com/amueller/dabl/issues/85
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def plot_scatter(x1, x2, ax=None):
    """pass an single axes and plot multiple things in that region """
    if ax is None:
        ax = plt.gca()

    # create gridspec
    gs = gridspec.GridSpecFromSubplotSpec(
        2,
        2,
        subplot_spec=ax.get_subplotspec(),
        width_ratios=[4, 1],
        height_ratios=[1, 4],
        hspace=0,
        wspace=0,
    )
    ax.set_subplotspec(gs[2])
    ax.update_params()
    ax.set_position(ax.figbox)
    ax.scatter(x1, x2)

    fig = ax.get_figure()
    top_ax = fig.add_subplot(gs[0])
    top_ax.hist(x1, bins=30)
    top_ax.set_axis_off()

    right_ax = fig.add_subplot(gs[3])
    right_ax.hist(x2, bins=30, orientation="horizontal")
    right_ax.set_axis_off()


if __name__ == "__main__":
    from sklearn.datasets import load_iris
    import itertools

    iris = load_iris()
    fig, axes = plt.subplots(4, 4, figsize=(10, 10))
    for i, j in itertools.product(range(4), repeat=2):
        plot_scatter(iris.data[:, i], iris.data[:, j], ax=axes[i, j])
