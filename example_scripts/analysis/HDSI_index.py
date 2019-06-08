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
## calculate Hutchinson Drought Severity Index (HDSI) xarray
## Drought Severity Index
# -----------------------------------------------------------------------------

"""
- raw monthly rainfall totals are integrated to rolling 6-monthly totals
- then ranked into percentiles by month
- rescaled to range between -4 and +4 in keeping with the range of the Palmer Index
- default threshold at -1 which is at 3/8ths or the 37.5th percentile
"""


# -----------------------------------------------------------------------------
## calculate Hutchinson Drought Severity Index (HDSI) PANDAS
## Drought Severity Index
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


def DSI(x: pd.Series,
        droughtThreshold: float = 0.375):
    y = (x.rank() - 1.0) / (len(x) - 1.0)  # normalised rank (0-1)
    z = 8.0 * (y - 0.5)  # scaled between -4, 4
    return z


variable = 'precip'
rolling_window = 3
droughtThreshold = 0.375

d = get_test_df(c, variable)
df_window = calc_cumsum(d, variable, rolling_window)
df_window = apply_to_each_month(
    df_window, DSI, variable, **{'droughtThreshold': droughtThreshold}
)
df_window.head()



#
