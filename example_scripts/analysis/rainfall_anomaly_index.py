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
