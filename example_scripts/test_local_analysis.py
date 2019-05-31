import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

from scripts.plotting_utils import (plot_geog_location, plot_xarray_on_map)
from src.utils import get_kenya
from scripts.eng_utils import get_ds_mask

%matplotlib


data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/')
plot_dir = Path('Users/tommylees/Downloads')

ds = xr.open_dataset(data_dir / "kenya_rainfall2.nc")
p_dir = data_dir / "kenya_rainfall2.nc"

chirps_dir = data_dir / "chirps_kenya.nc"

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
%load_ext autoreload
%autoreload 2

from src.analysis.event_detector import EventDetector

era = EventDetector(p_dir)
era.detect(
    variable='tp', time_period='dayofyear', hilo='low', method='std'
)

e_runs = era.calculate_runs()

chirp = EventDetector(chirps_dir)
chirp.detect(
    variable='precip', time_period='month', hilo='low', method='std'
)

c_runs = chirp.calculate_runs()

mask = get_ds_mask(chirp.ds.precip)
c_runs = c_runs.where(~mask)

kenya = get_kenya()

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
c = chirp

fig, ax = plt.subplots()
c.clim.mean(dim=['lat','lon']).precip.plot(ax=ax)
c.thresh.mean(dim=['lat','lon']).precip.plot(ax=ax)
ax.set_title('Threshold & Climatology Values for Precip (monthly) [mm day-1]')


fig, ax = plot_geog_location(kenya, lakes=False, borders=True, rivers=True, scale=0.8)
c_runs.mean(dim='time').plot(ax=ax)
ax.set_title('Mean Run Length (Consecutive Months with -1 STD)')

# explore failed seasons
c_runs['season'] = c_runs['time.season']
exceed = c.exceedences.where(~mask)

# select only the rainy seasons
exceed['season'] = exceed['time.season']
exceed = (
    exceed
    .where((exceed.season == 'MAM') | (exceed.season == 'SON'))
    .dropna(dim='time', how='all')
    .drop('season')
    .astype(bool)
)


# ------------------------------------------------------------------------------
# runs of consecutive failed months
# ------------------------------------------------------------------------------

from xclim.run_length import rle, longest_run, windowed_run_events

s_runs = rle(exceed).load()
s_runs = s_runs.where(~mask)

fig, ax = plot_geog_location(kenya, lakes=False, borders=True, rivers=True, scale=0.8)
s_runs.mean(dim='time').plot(ax=ax)
ax.set_title('Mean Run Length (Consecutive Months in rainy seasons with -1 STD)\n[1900-2019]')

# how does this vary over time (DECADAL AVERAGES)
decade_median = s_runs.resample(time='10AS').median(dim='time')
decade_median = decade_median.where(~mask)

decade_mean = s_runs.resample(time='10AS').mean(dim='time')
decade_mean = decade_mean.where(~mask)

fig, ax = plot_geog_location(kenya, lakes=False, borders=True, rivers=True, scale=0.8)
decade_mean.mean(dim='time').plot(ax=ax)
ax.set_title('Median Run Length (EACH DECADE) (Consecutive Months in rainy seasons with -1 STD)\n[1900-2019]')

fig, ax = plt.subplots()
decade_mean.count(dim=['lat','lon']).plot(ax=ax)
ax.set_title('Run length Per Decade \n[rainy season months with <1 STD precip per decade]')

# where are the max runs?
def find_the_max_runs(runs):
    max_runs = (runs
        .where(runs == runs.max())
        .dropna(dim='time', how='all')
        .dropna(dim='lat', how='all')
        .dropna(dim='lon', how='all')
    )
    return max_runs


# ------------------------------------------------------------------------------
# The longest run for each pixel
# ------------------------------------------------------------------------------

lr = longest_run(exceed).load()
lr = lr.where(~mask)

fig,ax = plt.subplots()
lr.plot(ax=ax)


# ------------------------------------------------------------------------------
# animation
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Playing with the climate_indices package
# ------------------------------------------------------------------------------

import climate_indices
# _prepare_file(netcdf_file, var_name)

# keyword arguments used for the SPI function
kwrgs = {"index": "spi",
         "netcdf_precip": netcdf_precip,
         "var_name_precip": var_name_precip,
         "input_type": input_type,
         "scale": scale,
         "distribution": dist,
         "periodicity": periodicity,
         "calibration_start_year": calibration_start_year,
         "calibration_end_year": calibration_end_year,
         "output_file_base": output_file_base}

# compute and write SPI - _compute_write_index(keyword_arguments)
_compute_write_index(kwrgs)

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
