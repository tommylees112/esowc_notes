import xarray as xr
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import ipdb
from typing import List

%matplotlib

if os.getcwd().split('/')[2] == "tommylees":
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
else:
    data_dir = Path('data')

era5_dir = data_dir / "interim" / "era5POS_preprocessed" / "era5POS_kenya.nc"
chirps_dir = data_dir / "interim" / "chirps_preprocessed" / "chirps_kenya.nc"

c = xr.open_dataset(chirps_dir)
e = xr.open_dataset(era5_dir)

# convert c to mm/day
c['precip'] = c.precip / 5
c.attrs['units'] = 'mm/day'

# convert to monthly
c = c.sortby('time')
c = c.resample(time='M').mean()


c_ = c.sel(time=slice('2010', '2015'))

# -----------------------------------------------------------------------------
## calculate Percent of Normal Index (PNI) using xarray
# -----------------------------------------------------------------------------

rolling_window = 3
c_window = c_.rolling(time=rolling_window, center=True).sum()

mthly_climatology = c_window.groupby('time.month').mean(dim='time')
# https://stackoverflow.com/questions/34987972/expand-dimensions-xarray
# c_window['month'] = c_window['time.month']
# c_window = c_window.assign_coords(month=c_window['time.month'])

clim = create_shape_aligned_climatology(c_window, mthly_climatology, 'precip', 'month')

PNI = (c_window / clim) * 100
# drop the initial nans (e.g. window=3 the first 2 months)
PNI = PNI.dropna(dim='time', how='all')

ds = c_
variable = 'precip'
time_period = 'month'

def calculatePNI(ds: xr.Dataset,
                 variable: str,
                 time_period: str,
                 rolling_window: int = 3,
                 clim_period: Optional[List[str]] = None,
                 ) -> xr.DataArray:
    """calculate Percent of Normal Index (PNI)

        Arguments:
        ---------
        ds : xr.Dataset
            the dataset with the raw values that you are comparing to climatology

        variable: str
            name of the variable that you are comparing to the climatology

        time_period: str
            the period string used to calculate the climatology
             time_period = {'dayofyear', 'season', 'month'}

        rolling_window: int Default = 3
            the size of the cumsum window (in timesteps)

    """
    # calculate the rolling window (cumsum over time)
    ds_window = ds.rolling(time=rolling_window, center=True).sum()

    # calculate climatology based on time_period
    mthly_climatology = (
        ds_window
        .groupby(f'time.{time_period}')
        .mean(dim='time')
    )
    clim = create_shape_aligned_climatology(
        ds_window, mthly_climatology, variable, time_period
    )

    # calculate the PNI
    PNI = (ds_window / clim) * 100
    # drop the initial nans caused by the widnowed cumsum
    #  (e.g. window=3 the first 2 months)
    PNI = PNI.dropna(dim='time', how='all')

    return PNI


calculatePNI(ds, variable, time_period)
# assert that returns values correct for the given timeperiod
# assert that the different month values are ALL the same

# ==============================================================================
# CREATE CLIMATOLOGY OF SAME SHAPE
# ==============================================================================

def create_shape_aligned_climatology(ds, clim, variable, time_period):
    """match the time dimension of `clim` to the shape of `ds` so that can
    perform simple calculations / arithmetic on the values of clim
    Arguments:
    ---------
    ds : xr.Dataset
        the dataset with the raw values that you are comparing to climatology
    clim: xr.Dataset
        the climatology values for a given `time_period`
    variable: str
        name of the variable that you are comparing to the climatology
    time_period: str
        the period string used to calculate the climatology
         time_period = {'dayofyear', 'season', 'month'}
    Notes:
        1. assumes that `lat` and `lon` are the
        coord names in ds
    """
    ds[time_period] = ds[f'time.{time_period}']
    values = clim[variable].values
    keys = clim[time_period].values
    # map the `time_period` to the `values` of the climatology (threshold or mean)
    lookup_dict = dict(zip(keys, values))
    # extract an array of the `time_period` values from the `ds`
    timevals = ds[time_period].values
    # use the lat lon arrays (climatology values) in `lookup_dict` corresponding
    #  to time_period values defined in `timevals` and stack into new array
    new_clim_vals = np.stack([lookup_dict[timevals[i]] for i in range(len(timevals))])
    assert new_clim_vals.shape == ds[variable].shape, f"\
        Shapes for new_clim_vals and ds must match! \
         new_clim_vals.shape: {new_clim_vals.shape} \
         ds.shape: {ds[variable].shape}"
    # copy that forward in time
    new_clim = xr.Dataset(
        {variable: (['time', 'lat', 'lon'], new_clim_vals)},
        coords={
            'lat': clim.lat,
            'lon': clim.lon,
            'time': ds.time,
        }
    )
    return new_clim




# -----------------------------------------------------------------------------
## calculate Percent of Normal Index (PNI) using PANDAS
# -----------------------------------------------------------------------------

# convert to DataFrame
# df = c.precip.to_dataframe()
d = (
    c.sel(time=slice('2010', '2015'))
    .isel(lat=0,lon=0)
    .precip.to_dataframe()
    .reset_index()
    .set_index('time')
)

def calculatePNI(x):
    ipdb.set_trace()
    pass

d.groupby(['lat', 'lon']).apply(calculatePNI)

var_col = 'precip'
d[f'{var_col}{rolling_window}'] = d[var_col].rolling(rolling_window).sum()
# drop the initial ones (can't calculate cumsum)
df_window = d[[f'{var_col}{rolling_window}']].dropna()
df_window['PNI'] = np.nan

imon = 1
# indexes that select that month
sinds = df_window.index.month == imon
# the data for those indices (that month)
x = df_window[sinds]
# calculate Percent of Normal (climatology)
y = (
    x / x[f'{var_col}{rolling_window}'].mean()
) * 100
# assign back to the dataframe
df_window.loc[sinds, 'PNI'] = y[f'{var_col}{rolling_window}'].values


def PNI(df: pd.DataFrame, var_col: str, rolling_window: int = 3):
    """ """
    assert df.index.dtype == pd.datetime, f"expecting the index to be a timeseries"

    # aggregate by size (rolling_window) - default to 3 timesteps
    df[f'{var_col}{rolling_window}'] = df[var_col].rolling(rolling_window).sum()

    # initialise variables
    df_window = df[[f'{var_col}{rolling_window}']].dropna()
    df_window['PNI'] = np.nan

    # calculate PNI

    # loop over each month
    for imon in np.arange(1, 13):
        # select the indexes forthat month
        sinds = df_window.index.month == imon
        # the data for those indices (that month)
        x = df_window[sinds]
        # calculate Percent of Normal (climatology)
        y = (
            x / x[f'{var_col}{rolling_window}'].mean()
        ) * 100
        # assign back to the dataframe
        df_window.loc[sinds, 'PNI'] = y[f'{var_col}{rolling_window}'].values


# -----------------------------------------------------------------------------
## calculate Percent of Normal Index (PNI)
# -----------------------------------------------------------------------------




# -----------------------------------------------------------------------------
## Trying to test the broadcast functionality
# -----------------------------------------------------------------------------
xr.broadcast(c_window, mthly_climatology)

# ASSIGN DIMENSION to xarray object
min_yr = 2010
max_yr = 2015
n_yrs = max_yr - min_yr + 1
da = xr.DataArray(
    c_window['time.month'].values,
    coords=[('month', np.tile(np.arange(1, 13), n_yrs))]
)
c_window, _ = xr.broadcast(c_window, da)


# apply to each month (easier to )
mth = 1
c_window.sel(month=mth)

# create a climatology object of the same size/dimensions
_, climatology = xr.broadcast(c_window, mthly_climatology)
v = climatology.where(climatology['time.month'] == 1).dropna(dim='time', how='all')
# v.isel(time=0) == v.isel(time=1)
