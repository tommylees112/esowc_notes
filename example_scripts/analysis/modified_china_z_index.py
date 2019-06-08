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
## calculate Modified China-Z Index (MCZI) xarray
# -----------------------------------------------------------------------------

"""
- CZI assumes that precipitation data follow the Pearson Type III distribution
- and is related to Wilson–Hilferty cube-root transformation

- MCZI, the median of precipitation (Med) is used instead of the mean of precipitation
"""

# -----------------------------------------------------------------------------
## calculate Modified China-Z Index (MCZI) PANDAS
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


def MCZI(x: pd.Series):
    """ Pearson Type III distribution """
    zsi = (x - x.median()) / x.std()
    cs  = np.power(zsi, 3) / len(x)
    czi = (
        6.0 / cs * np.power(
            (cs / 2.0 * zsi + 1.0), 1.0 / 3.0
        ) - 6.0 / cs + cs / 6.0
    )
    return czi


variable = 'precip'
rolling_window = 3
droughtThreshold = 0.375


d = get_test_df(c, variable)
df_window = calc_cumsum(d, variable, rolling_window)
df_window = apply_to_each_month(
    df_window, MCZI, variable
)
df_window.head()

#
