import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

from scripts.plotting_utils import (plot_geog_location, plot_xarray_on_map)
from src.utils import get_kenya
%matplotlib
# ------------------------------------------------------------------------------
# Read the data
# ------------------------------------------------------------------------------
data_dir = Path('data')
interim_dir = data_dir / "interim"
plot_dir = Path('/soge-home/users/chri4118')
# read the preprocessed data
c_dir = interim_dir / "chirps_preprocessed.nc"
v_dir = interim_dir / "vhi_preprocessed.nc"
v_dir = interim_dir / "vhi_preprocessed" / "vhi_kenya.nc"

v2_dir = interim_dir / "vhi_preprocessed" / "vhi_preprocess_kenya.nc"

v = xr.open_dataset(v_dir)
v2 = xr.open_dataset(v2_dir)
c = xr.open_dataset(c_dir)

# select the same time slices
min_time = v.time.min()
max_time = c.time.max()

v = v.sel(time=slice(min_time, max_time))
c = c.sel(time=slice(min_time, max_time))

v2 = v2.sortby('time')
v2 = v2.sel(time=slice(min_time, max_time))
v2 = v2.rename({'latitude':'lat', 'longitude':'lon'})

colors = sns.color_palette()

kenya = get_kenya()

# ------------------------------------------------------------------------------
# Plot raw data
# ------------------------------------------------------------------------------
# Raw VHI values (timeseries)
fig, ax = plt.subplots()
times = pd.to_datetime(v.VHI.mean(dim=['lat','lon']).time.values)
v_spatialmean = v.VHI.mean(dim=['lat','lon']).values
ax.plot(times, v_spatialmean, color=colors[1])
ax.set_title('Raw Mean Monthly VHI')
fig.savefig(plot_dir/'raw_vhi_monthly.png')

# Raw CHIRPS values (timeseries)
fig, ax = plt.subplots()
times = pd.to_datetime(c.precip.mean(dim=['lat','lon']).time.values)
c_spatialmean = c.precip.mean(dim=['lat','lon']).values
ax.plot(times, c_spatialmean, color=colors[0])
ax.set_title('Raw Mean Monthly Precipitation')

# spatial plots - VHI
fig, ax = plot_geog_location(kenya, lakes=True, borders=True, rivers=True, scale=1)
da = v2.VHI.mean(dim='time')
plot_xarray_on_map(da, ax=ax)
fig.savefig(plot_dir/'raw_vhi_spatial.png')


## spatial plots - precip
fig, ax = plot_geog_location(kenya, lakes=False, borders=True, rivers=True, scale=1)
da = c.precip.mean(dim='time')
plot_xarray_on_map(da, ax=ax)

# ------------------------------------------------------------------------------
# calculate run stuff
# ------------------------------------------------------------------------------
