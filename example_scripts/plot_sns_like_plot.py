# https://github.com/amueller/dabl/issues/85

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

rs = np.random.RandomState(42)
x1, x2, = rs.multivariate_normal([0, 0], [(1, 0.5), (0.5, 1)], 500).T

fig = plt.figure(figsize=(6, 6))
gs = GridSpec(2, 2, width_ratios=[4, 1], height_ratios=[1, 4], hspace=0, wspace=0)
top_ax = fig.add_subplot(gs[0])
top_ax.set_axis_off()
left_ax = fig.add_subplot(gs[3])
left_ax.set_axis_off()
main_ax = fig.add_subplot(gs[2])

top_ax.hist(x1, bins=30)
left_ax.hist(x2, bins=30, orientation='horizontal')
main_ax.scatter(x1, x2, alpha=0.6)
