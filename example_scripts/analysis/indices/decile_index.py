import xarray as xr
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mapclassify as mc
import os
from typing import List
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

times = pd.date_range('1900-01-01', freq='M', periods=1440)  # '2019-03-31',
c_lt = xr.open_dataset(
        '/Volumes/Lees_Extend/data/ecmwf_sowc/chirps_kenya.nc',
        decode_times=False
)
c_lt['time'] = times

# convert c to mm/day
c['precip'] = c.precip / 5
c.attrs['units'] = 'mm/day'

e['precip'] = e['precipitation_amount_1hour_Accumulation'] * 24
e.precip.attrs['units'] = 'mm/day'

# convert to monthly
c = c.sortby('time')
c = c.resample(time='M').mean()

c_ = c.sel(time=slice('2010', '2015'))

# -----------------------------------------------------------------------------
## calculate Decile Index xarray
# http://martin-jung.github.io/post/2018-xarrayregression/
# -----------------------------------------------------------------------------

# 1. calculate a cumsum
def rolling_cumsum(ds, rolling_window=3):
    ds_window = (
        ds.rolling(time=rolling_window, center=True)
        .sum()
        .dropna(dim='time', how='all')
    )
    return ds_window


# 2. calculate the normalised rank (of each month) for the variable
def rank_norm(ds, dim='time'):
    return (ds.rank(dim=dim) - 1) / (ds.sizes[dim] - 1) * 100

def apply_over_months(ds, func, in_variable, out_variable='rank_norm'):
    return (
        ds.groupby('time.month')
        .apply(func, args=('time',))
        .rename({in_variable: out_variable})
    )


# 3. bin the normalised rank into quintiles
def bin_to_quintiles(da: xr.DataArray,
                     new_variable_name: str = 'quintiles') -> xr.Dataset:
    """use the pandas `qcut` function to bin the
    variables to quintile labels

    Arguments:
    ---------
    da : xr.DataArray
        variable that you want to bin into quintiles

    new_variable_name: str
        the `variable_name` in the output `xr.Dataset`
         which corresponds to the quintile labels

    Returns:
    ------
    xr.Dataset

    Note:
        labels = [1, 2, 3, 4, 5] correspond to
         [(0, 20) (20,40) (40,60) (60,80) (80,100)]
    """
    # da to df
    df = da.to_dataframe()
    # calculate the quintiles using `pd.qcut`
    value_column = [c for c in df.columns][0]
    bins = pd.qcut(df[value_column], 5, labels=[1, 2, 3, 4, 5])
    # convert back to xarray
    ds = (
        bins
        .to_xarray()
        .to_dataset()
        .rename({value_column: new_variable_name})
    )
    # da = ds[new_variable_name]

    return ds

def bin_to_quintiles2(da: xr.DataArray,
                      new_variable_name: str = 'quintile') -> xr.Dataset:
    """use the numpy `np.digitize` function to bin the
    variables to quintile labels
    https://stackoverflow.com/a/56514582/9940782

    Arguments:
    ---------
    da : xr.DataArray
        variable that you want to bin into quintiles

    new_variable_name: str
        the `variable_name` in the output `xr.Dataset`
         which corresponds to the quintile labels

    Returns:
    ------
    xr.Dataset

    Note:
        labels = [1, 2, 3, 4, 5] correspond to
         [(0, 20) (20,40) (40,60) (60,80) (80,100)]
    """
    # calculate the quintiles using `np.digitize`
    bins = [0.0, 20., 40., 60., 80.]
    result = xr.apply_ufunc(np.digitize, da, bins)
    result = result.rename(new_variable_name)
    return result

# calculate cumsum
ds = c_
variable = 'precip'
rolling_window = 3
ds_window = rolling_cumsum(ds, rolling_window)

# calculate normalised rank
out_variable = 'rank_norm'
normalised_rank = apply_over_months(
    ds_window, rank_norm, 'precip', out_variable=out_variable
)
ds_window = ds_window.merge(normalised_rank.drop('month'))

# bin these into quintiles
value_column = 'rank_norm'
new_variable_name = 'quintile'
# quintile = bin_to_quintiles(ds_window[value_column], new_variable_name)
quintile2 = bin_to_quintiles2(ds_window[value_column])
ds_window = ds_window.merge(quintile.to_dataset(name='quintile'))

### Wrap all into one function
def decile_index(ds: xr.Dataset,
                 variable: str,
                 rolling_window: int = 3) -> xr.Dataset:
    # 1. calculate a cumsum over `rolling_window` timesteps
    ds_window = rolling_cumsum(ds, rolling_window)

    # 2. calculate the normalised rank (of each month) for the variable
    out_variable = 'rank_norm'
    normalised_rank = apply_over_months(
        ds_window, func=rank_norm, in_variable='precip', out_variable=out_variable
    )
    ds_window = ds_window.merge(normalised_rank.drop('month'))

    # 3. bin the normalised rank into quintiles
    new_variable_name = 'quintile'
    quintile = bin_to_quintiles2(
        ds_window[variable], new_variable_name
    )
    ds_window = ds_window.merge(quintile.to_dataset(name='quintile'))

    return ds_window

variable = 'precip'
rolling_window = 3
value_column = 'rank_norm'
new_variable_name = 'quintile'


ds = decile_index(c_, variable, rolling_window)
ds = decile_index(c, variable, rolling_window)

fig, ax = plt.subplots()
ds.isel(lat=0,lon=100).rank_norm.plot(ax=ax)
ax.axhline(80, linestyle='--', color='g')
ax.axhline(60, linestyle='--', color='lime')
ax.axhline(40, linestyle='--', color='orange')
ax.axhline(20, linestyle='--', color='r')

# -----------------------------------------------------------------------------
## calculate Decile Index PANDAS
# -----------------------------------------------------------------------------
variable = 'precip'
rolling_window = 3

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

d = get_test_df(c, variable)

# cumsum
def calc_cumsum(df: pd.DataFrame,
                variable: str,
                rolling_window: int = 3):
    df_window = (
        df[variable]
        .rolling(rolling_window).sum()
        .dropna().to_frame()
    )

    return df_window

df_window = calc_cumsum(d, variable, rolling_window)

# convert into normalised ranks for each month?
df_window['rank_norm'] = np.nan  # [np.nan for _ in range(df_window.size)]

for imon in np.arange(1, 13):
    sinds = df_window.index.month == imon
    x = df_window.loc[sinds, variable]
    y = (x.rank() - 1.0) / (len(x) - 1.0) * 100.0

    df_window.loc[sinds, 'rank_norm'] = y.values

df_window.head()

# categorise normalised_ranks within 5 bands
bins = [20., 40., 60., 80., np.Inf]
df_window['bins'] = df_window[['rank_norm']].apply(
    mc.User_Defined.make(bins=bins, rolling=False)
)

df_window.head()

# plot the result
ax = df_window['rank_norm'].plot()
ax.axhline(80, linestyle='--', color='g')
ax.axhline(60, linestyle='--', color='lime')
ax.axhline(40, linestyle='--', color='orange')
ax.axhline(20, linestyle='--', color='r')
ax.set_title('Three-Monthly Decile Index', fontsize=16)


"""
Monthly precipitation totals from a long-term record are first ranked from highest to lowest. This constructs a cumulative frequency distribution. The distribution is then split into 10 parts. The first decile is the precipitation value not exceeded by the lowest 10% of all precipitation values in a record.

 If precipitation falls into the lowest 20% (deciles 1 and 2), it is classified as ***much below normal***. Deciles 3 to 4 (20 to 40%) indicate ***below normal*** precipitation, deciles 5 to 6 (40 to 60%) indicate ***near normal*** precipitation, 7 and 8 (60 to 80%) indicate ***above normal*** precipitation and 9 and 10 (80 to 100%) indicate ***much above normal*** precipitation.

Gibbs, W.J. and J.V. Maher. 1967. Rainfall deciles as drought indicators. Bureau of Meteorology, Bulletin No. 48, Melbourne.

Hayes, M.J. 2000. Drought indices. National Drought Mitigation Center, University of Nebraska, Lincoln, Nebraska.

Smith, D.I., M.F. Hutchinson, and R.J. McArthur. 1993. Australian climatic and agricultural drought: Payments and policy. Drought Network News 5(3):11-12.

White, D.H. and B. O'Meagher. 1995. Coping with exceptional circumstances: Droughts in Australia. Drought Network News 7:13–17.
"""


# ------------------------------------------------------------------------------
# Marginalia
# ------------------------------------------------------------------------------
ds = c_
variable = 'precip'
rolling_window = 3

# cumsum
ds_window = (
    ds.rolling(time=rolling_window, center=True)
    .sum()
    .dropna(dim='time', how='all')
)

# first ranked from highest to lowest
# to construct a cumulative frequency distribution
#
# ds_window[variable].groupby('time.month').rank(dim='time')


rank_norm_list = []

# loop through all the months
for mth in range(1, 13):
    # select that month
    ds_mth = (
        ds_window
        .where(ds_window['time.month'] == mth)
        .dropna(dim='time', how='all')
    )
    # apply the function to that month (here a normalised rank (0-100))
    rank_norm_mth = (
        (ds_mth.rank(dim='time') - 1) / (ds_mth.time.size - 1.0) * 100.0
    )
    rank_norm_mth = rank_norm_mth.rename({variable: 'rank_norm'})
    rank_norm_list.append(rank_norm_mth)

# after the loop re-combine the DataArrays
rank_norm = xr.merge(rank_norm_list).sortby('time')

## NB apply function works just as well
#
def rank_norm(ds, dim='time'):
    return (ds.rank(dim=dim) - 1) / (ds.sizes[dim] - 1) * 100

result = ds_window.groupby('time.month').apply(rank_norm, args=('time',))
result = result.rename({variable:'rank_norm'}).drop('month')
test = result.isel(lon=slice(0, 10), lat=slice(0, 10))

def test(x, axis):
    ipdb.set_trace()

# assign bins to variable xarray
bins = [-0.01, 20., 40., 60., 80., np.Inf]  # bin edges
bin_labels = ['20', '40', '60', '80', '100']
decile_index_gpby = result.groupby_bins('rank_norm', bins=bins, labels=bin_labels)
output = decile_index_gpby.assign()  # assign_coords()

def return_groupby_labels(ds):
    ipdb.set_trace()

decile_index_gpby.apply(return_groupby_labels)
output = decile_index_gpby.assign()  # assign_coords()


#
# bins = pd.cut(df[variable], [-0.1, 20., 40., 60., 80., np.Inf])

df = rank_norm.to_dataframe()
bins = pd.qcut(df['rank_norm'], 5, labels=[1, 2, 3, 4, 5])
output = bins.to_xarray().to_dataset().rename({'rank_norm': 'rank_quantile'})
