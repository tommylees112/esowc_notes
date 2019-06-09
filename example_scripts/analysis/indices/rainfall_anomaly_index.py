import xarray as xr
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mapclassify as mc
import os
from typing import List, Dict
import ipdb

%matplotlib

if os.getcwd().split('/')[2] == "tommylees":
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
else:
    data_dir = Path('data')

era5_dir = data_dir / "interim" / "era5POS_preprocessed" / "era5POS_kenya.nc"
chirps_dir = data_dir / "interim" / "chirps_preprocessed" / "chirps_kenya.nc"
vhi_dir = data_dir / "interim" / "vhi_preprocessed" / "vhi_kenya.nc"

c = xr.open_dataset(chirps_dir)
e = xr.open_dataset(era5_dir)
v = xr.open_dataset(vhi_dir)

# convert c to mm/day
c['precip'] = c.precip / 5
c.attrs['units'] = 'mm/day'

# convert to monthly
c = c.sortby('time')
c = c.resample(time='M').mean()

c_ = c.sel(time=slice('2010', '2015'))

ts = c.mean(dim=['lat','lon']).to_dataframe()
ts2 = (
    e.precipitation_amount_1hour_Accumulation
    .mean(dim=['lat','lon'])
    .to_dataframe()
)

import salem

da = c.precip
da.mean(dim='time').salem.quick_map();

# -----------------------------------------------------------------------------
## calculate Rainfall Anomaly Index (RAI) xarray
# -----------------------------------------------------------------------------
"""
- incorporates a ranking procedure to assign magnitudes to positive and negative anomalies
- two phases, positive precipitation anomalies and negative precipitation anomalies
- easy to calculate, with a single input (precipitation) that can be analysed on monthly, seasonal and annual timescales.
- However, calculating RAI requires a serially complete dataset with estimates of missing values.
- Variations within the year need to be small compared to temporal variations.
"""


def rolling_cumsum(ds, rolling_window=3):
    ds_window = (
        ds.rolling(time=rolling_window, center=True)
        .sum()
        .dropna(dim='time', how='all')
    )
    return ds_window


def assign_magnitudes(y: xr.Dataset,
                      anom: xr.DataArray,
                      rai_plus: xr.DataArray,
                      rai_minus: xr.DataArray) -> xr.Dataset:
    # REVERSE boolean indexing
    # if anom values are NOT less than/equal than fill with PLUS values
    y_plus = y.where(~(anom >= 0), other=rai_plus)
    y_plus_mask = y.where(~(anom >= 0)).isnull()
    y_plus = y_plus.where(y_plus_mask)

    y_minus = y.where(~(anom < 0), other=rai_minus)
    y_minus_mask = y.where(~(anom < 0)).isnull()
    y_minus = y_minus.where(y_minus_mask)

    # convert to numpy masked array
    y_plus_m_np = y_plus_mask[variable].values
    y_plus_np = y_plus[variable].values
    y_plus_np = np.ma.array(y_plus_np, mask=(~y_plus_m_np))

    y_minus_m_np = y_minus_mask[variable].values
    y_minus_np = y_minus[variable].values
    y_minus_np = np.ma.array(y_minus_np, mask=(~y_minus_m_np))

    # recombine masked arrays
    rai_array = (
        np.ma.array(
            y_plus_np.filled(1) * y_minus_np.filled(1),
            mask=(y_plus_np.mask * y_minus_np.mask)
        )
    )

    rai = xr.ones_like(y)  # .to_dataset(name=variable)
    rai['RAI'] = (['time','lat','lon'], rai_array)
    rai = rai.RAI
    return rai


def RAI(da, dim: str = 'time', variable: str = 'precip', **kwargs):
    # calculations
    y  = da.copy()
    x1 = da.copy().sortby(dim, ascending=False)  # high -> low over TIME
    # sample average, max average, min average
    x_avg = x1.mean(dim=dim)  # monthly average over all time
    mx_avg = x1.isel(time=slice(0,10)).mean(dim=dim)  # max mean (top 10)
    mn_avg = x1.isel(time=slice(-11,-1)).mean(dim=dim)  # min mean (bottom 10) NB
    # anomaly = value - mean
    anom = da - x_avg

    # where anomaly is >=0, get the ratio to difference of max_avg - x_avg
    rai_plus  = 3.0 * anom.where(anom >= 0) / (mx_avg - x_avg)
    rai_minus = -3.0 * anom.where(anom < 0) / (mn_avg - x_avg)

    # assign the magnitudes for positive and negative anomalies
    # convert to numpy masked arrays and then back out to xarray
    rai = assign_magnitudes(y, anom, rai_plus, rai_minus)

    return rai


def apply_over_months(da, func, in_variable, out_variable='rank_norm', **kwargs):
    return (
        da.groupby('time.month')
        .apply(func, args=('time',in_variable,), **kwargs)
    )


def rainfall_anomaly_index(ds, rolling_window, in_variable):
    # 1. calculate a cumsum over `rolling_window` timesteps
    ds_window = rolling_cumsum(ds, rolling_window)
    # 2. calculate the normalised rank (of each month) for the variable
    out_variable = 'RAI'
    rai = apply_over_months(
        ds_window, func=RAI,
        in_variable=in_variable,
        out_variable=out_variable
    )
    rai = rai.drop('month')
    ds_window = ds_window.merge(rai.to_dataset())

    return ds_window

rolling_window = 3
variable = 'precip'
# rai = rainfall_anomaly_index(c_, rolling_window, in_variable=variable)

rolling_window = 6
rai = rainfall_anomaly_index(c, rolling_window=6, in_variable=variable)

fig, ax = plt.subplots()
rai.isel(lat=0,lon=100).RAI.plot(ax=ax)
ax.set_title(f'1981-2018 CHIRPS Rainfall Anomaly Index (RAI). {rolling_window} months cumsum')

# -----------------------------------------------------------------------------
## calculate Rainfall Anomaly Index (RAI) PANDAS
# -----------------------------------------------------------------------------

def get_test_df(ds: xr.Dataset,
                variable: str,
                min_yr: int = 2010,
                max_yr: int = 2015):
    df = (
        ds.sel(time=slice(str(min_yr), str(max_yr)))
        .isel(lat=0,lon=0)[variable]
        .to_dataframe(name=variable)
        .reset_index()
        .set_index('time')
    )

    return df


def calc_cumsum(df: pd.DataFrame,
                variable: str,
                rolling_window: int = 3):
    df_window = (
        df[variable]
        .rolling(rolling_window).sum()
        .dropna().to_frame()
    )

    return df_window


def apply_to_each_month(df_window: pd.DataFrame,
                        func,
                        variable: str,
                        **kwargs: Dict):
    for imon in np.arange(1, 13):
        sinds = df_window.index.month == imon
        x = df_window.loc[sinds, variable]
        y = func(x, **kwargs)

        df_window.loc[sinds, 'rank_norm'] = y.values

    return df_window


def RAI(x: pd.Series, variable: str):
    """ Rainfall Anomaly Index (RAI) """
    y  = x.copy()
    x1 = x.copy().sort_values(ascending=False)  # high -> low
    x_avg  = x1.mean()  # monthly average over all time
    mx_avg = x1.head(10).mean()  # max mean (top 10)
    mn_avg = x1.tail(10).mean()  # min mean (bottom 10)
    anom = x - x_avg

    rai_plus  = 3.0 * anom[anom >= 0] / (mx_avg - x_avg)
    rai_minus = -3.0 * anom[anom < 0] / (mn_avg - x_avg)
    y.loc[anom >= 0, 'RAI'] = rai_plus.values
    y.loc[anom < 0,  'RAI'] = rai_minus.values

    return y


variable = 'precip'
rolling_window = 3
droughtThreshold = 0.375


d = get_test_df(c, variable)
df_window = calc_cumsum(d, variable, rolling_window)
df_window = apply_to_each_month(
    df_window, RAI, variable, **{'variable': variable}
)
df_window.head()

#
