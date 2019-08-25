from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import calendar

if 'tommylees' in Path('.').absolute().parts:
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
out_dir = data_dir / 'analysis' / 'region_analysis'

from src.analysis.exploration import (
    calculate_seasonal_anomalies, create_anomaly_df,
    plot_bar_anomalies
)

%load_ext autoreload
%autoreload 2

import proplot as plot
import matplotlib.gridspec as gridspec


#

# ---------------------------------
#
# ---------------------------------


chirps = xr.open_dataset(
    data_dir / 'interim' /
    'chirps_preprocessed' / 'data_kenya.nc'
)
vci = xr.open_dataset(
    data_dir / 'interim' /
    'VCI_preprocessed' / 'data_kenya.nc'
)


# ---------------------------------
# calculate monmean / monstd
# ---------------------------------

def monmean_monstd(ds: xr.Dataset, variable: str) -> xr.DataArray:
    monmean = ds[variable].groupby('time.month').mean(dim='time').to_dataset(name=variable)
    monstd = ds[variable].groupby('time.month').std(dim='time').to_dataset(name=variable)
    return monmean, monstd

# data preprocessing for the plots
spatial_mean = vci.VCI.mean(dim='time')
temporal_mean = vci.VCI.mean(dim=['lat', 'lon'])

monmean, monstd = monmean_monstd(vci, 'VCI')
mean_df = monmean.to_dataframe().reset_index()
mean_val = mean_df.mean().VCI

# ---------------------------------
# plot violins for distribution of all
# ---------------------------------
import seaborn as sns

mean_df = monmean.to_dataframe().reset_index()
std_df = monstd.to_dataframe()

mean_val = mean_df.mean().VCI

plot.rc.small = 15
plot.rc.large = 18
fig, ax = plt.subplots(figsize=(12, 8))
sns.violinplot(x="month", y="VCI",
               data=mean_df, ax=ax,
               palette=sns.color_palette("husl", 12))
ax.set_title('Monthly Distribution of Mean VCI')
ax.set_xticklabels(
    [calendar.month_name[i] for i in range(1, 13)],
    rotation=45
)
ax.set_ylim(0, 100)
ax.axhline(mean_val, alpha=0.5, color='k', ls='--', label='Mean VCI')
plt.legend()
plt.grid(False)
fig.savefig('/Users/tommylees/Downloads/seasonal_distribution_violin.png')
plot.rc.small = 8
plot.rc.large = 9


# ---------------------------------
# spatial plot for paper
# ---------------------------------
plot.rc.small = 15
plot.rc.large = 18
fig, ax = plt.subplots(figsize=(12, 8))
spatial_mean.plot(ax=ax)
ax.set_xlabel('')
ax.set_xticklabels('')
ax.set_xticks([])
ax.set_ylabel('')
ax.set_yticklabels('')
ax.set_yticks([])
ax.set_title('Mean Spatial VCI')
fig.savefig('/Users/tommylees/Downloads/spatial_plot_vci.png')

plot.rc.small = 8
plot.rc.large = 9


# ---------------------------------
# Grid plot of 3 plots
# ---------------------------------

# plot.rc.abc = True
fig = plt.figure(figsize=(12, 8))
gs = gridspec.GridSpec(2, 3, figure=fig)
ax1 = plt.subplot(gs[:, :2])
ax2 = plt.subplot(gs[0, 2])
ax3 = plt.subplot(gs[1, 2])

# spatial plot
spatial_mean.plot(ax=ax1)
ax1.set_xlabel('')
ax1.set_xticklabels('')
ax1.set_xticks([])

ax1.set_ylabel('')
ax1.set_yticklabels('')
ax1.set_yticks([])
ax1.set_title('Mean Spatial VCI')

# temporal plot
temporal_mean.resample(time='Y').mean().plot(ax=ax2)
ax2.set_title('Mean Annual VCI')

# seasonal plot
sns.violinplot(x="month", y="VCI",
               data=mean_df, ax=ax3,
               palette=sns.color_palette("husl", 12))
ax3.set_title('Monthly Distribution of Mean VCI')
ax3.set_xticklabels(
    [calendar.month_name[i] for i in range(1, 13)],
    rotation=45
)
ax3.set_ylim(0, 100)
ax3.axhline(mean_val, alpha=0.5, color='k', ls='--', label='Mean VCI')
axs.format(grid=False)

fig.savefig('/Users/tommylees/Downloads/VCI_grid_plot.png')
plot.rc.abc = False
