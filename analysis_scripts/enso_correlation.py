"""
Correlate VCI / Precip with ENSO time series

http://martin-jung.github.io/post/2018-xarrayregression/

https://github.com/pydata/xarray/issues/1115#issuecomment-451052107
"""

from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from typing import List

if 'tommylees' in Path('.').absolute().parts:
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
out_dir = data_dir / 'analysis' / 'region_analysis'

chirps = xr.open_dataset(
    data_dir / 'interim' /
    'chirps_preprocessed' / 'data_kenya.nc'
)

vci = xr.open_dataset(
    data_dir / 'interim' /
    'VCI_preprocessed' / 'data_kenya.nc'
)

from src.analysis.exploration import (
    calculate_seasonal_anomalies, create_anomaly_df,
    plot_bar_anomalies
)
from sklearn.preprocessing import scale

# ---------------------------
# Get and clean ENSO index
# ---------------------------

indices_df = pd.read_csv('data/flow_and_indices.csv').drop(columns=['flow', 'flow_std'])
indices_df = indices_df.astype({'date': 'datetime64[ns]'}).set_index('date')
nino = indices_df.NINO34.to_frame()

# ---------------------------
# get matching time series
# ---------------------------
#
# min_time = pd.to_datetime(max(vci_norm.time.min().values, nino.index.min()))
# max_time = pd.to_datetime(min(vci_norm.time.max().values, nino.index.max()))
#
# min_time = pd.Series([0], index=[min_time]).resample('M').first().index[0]
# max_time = pd.Series([0], index=[max_time]).resample('M').first().index[0]
#
# nino = nino.resample('M').first()[min_time: max_time]
# vci_norm = vci_norm.sel(time=slice(min_time, max_time))
#
# assert vci_norm.time.min().values == nino.index.min()
# assert len(vci_norm.time) == len(nino.index)

# ---------------------------
# get seasonal vals
# ---------------------------

nino_seas = nino.resample('Q-DEC').mean()
# vci_norm_seas = vci.resample(time='Q-DEC').mean(dim='time')
chirps_norm_seas = chirps.resample(time='Q-DEC').mean(dim='time')

# calculate shifted nino index
shift = 1
shifted_nino = nino_seas['NINO34'].shift(shift).dropna()

# ---------------------------
# standardize data
# ---------------------------

# da data
from src.utils import create_shape_aligned_climatology

def normalise_dataset(ds: xr.Dataset, variable: str) -> xr.DataArray:
    monmean = ds[variable].groupby('time.month').mean(dim='time').to_dataset(name=variable)
    monstd = ds[variable].groupby('time.month').std(dim='time').to_dataset(name=variable)
    monmean = create_shape_aligned_climatology(
        ds=ds, variable=variable, clim=monmean, time_period='month'
    )
    monstd = create_shape_aligned_climatology(
        ds=ds, variable=variable, clim=monstd, time_period='month'
    )

    norm = (ds[variable] - monmean[variable]) / monstd[variable]
    return norm

chirps_norm = normalise_dataset(chirps, 'precip')
# vci_norm = normalise_dataset(vci, 'VHI')

# normalize ocean index timeseries data
nino['NINO34'] = scale(nino['NINO34'])


# ---------------------------
# correlate with each pixel
# ---------------------------
from scipy.stats.stats import pearsonr
from datetime import datetime


def stack_pixels(da: xr.DataArray) -> xr.DataArray:
    return da.stack(point=('lat', 'lon')).groupby('point')



# def matching_timesteps(array1: List[np.datetime64],
#                        array2: List[np.datetime64]
#                        ) -> List[np.datetime64]:

def matching_timesteps(array1: List[datetime],
                       array2: List[datetime]
                       ) -> List[datetime]:
    # assert np.unique([str(type(v)) for v in array1]) == np.unique([str(type(v)) for v in array2]),\
    #     'Expect the types to be matching in both arrays'

    final_array1 = np.array(array1)[np.isin(array1, array2)]
    final_array2 = np.array(array2)[np.isin(array2, array1)]

    assert np.isin(final_array1, final_array2).all(), \
        f'{final_array1[~np.isin(final_array1, final_array2)]}' \
        f'{final_array2[np.isin(final_array2, final_array1)]}'

    return final_array1


def _calculate_pearsonr(x1: np.array, x2: np.array) -> float:
    try:
        r, _ = pearsonr(x1, x2)
    except ValueError:
        r = np.nan
    return r


def calculate_slow_pearsonr(da: xr.DataArray, series: pd.Series) -> xr.Dataset:
    # stack the pixels
    stacked = stack_pixels(da).first()
    # drop the missing pixels (all missing)
    stacked = stacked.dropna(dim='point', how='all')
    stacked = stacked.dropna(dim='time', how='all')
    print('* Stacked the pixels (3D -> 2D)*')

    # match timesteps
    series_times = [pd.to_datetime(time).to_pydatetime() for time in series.index.values]
    da_times = [pd.to_datetime(time).to_pydatetime() for time in stacked.time.values]
    final_times = matching_timesteps(series_times, da_times)
    final_stacked = stacked.sel(time=final_times)
    print('* Matching timesteps calculated *')

    # calculate correlations
    print('* Starting the Correlation Calculations *')
    point_rs = []
    for point in range(len(final_stacked.point)):
        if point % 1000 == 0:
            pct = f'{(point / len(final_stacked.point)) * 100}%'
            print(pct)
        x1 = final_stacked.isel(point=point).values
        x2 = series.loc[np.isin(series.index, pd.to_datetime(final_times))].values
        r = _calculate_pearsonr(x1, x2)
        point_rs.append(r)

    # create final dataset
    out = xr.ones_like(final_stacked).isel(time=0)
    out.values = point_rs
    return out.unstack('point').to_dataset(name=f'correlation')


chirps_nino_corr_ds = calculate_slow_pearsonr(chirps_norm_seas['precip'], shifted_nino)



# stack
stacked = stack_pixels(vci_norm_seas).first()
# drop the missing pixels (all missing)
stacked = stacked.dropna(dim='point', how='all')
stacked = stacked.dropna(dim='time', how='all')

# match all timesteps

final_times = matching_timesteps(shifted_nino.index.values, stacked.time.values)
final_stacked = stacked.sel(time=final_times)

point = 1

point_rs = []
for point in range(len(final_stacked.point)):
    if point % 1000 == 0:
        pct = f'{point / len(final_stacked.point)}%'
        print(pct)
    x1 = final_stacked.isel(point=point).values
    x2 = shifted_nino.loc[np.isin(shifted_nino.index, final_times)].values
    try:
        r, _ = pearsonr(x1, x2)
    except ValueError:
        r = np.nan
    point_rs.append(r)

out = xr.ones_like(final_stacked).isel(time=0)
out.values = point_rs
correlation_ds = out.unstack('point').to_dataset(name=f'correlation')

fig, ax = plt.subplots(figsize=(12, 8))
correlation_ds.correlation.plot(ax=ax)
ax.set_title('VCI Correlation with ENSO at Seasonal Timesteps: Lag 1')
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_yticklabels('')
ax.set_xticklabels('')
ax.set_xticks([])
ax.set_yticks([])
fig.savefig('/Users/tommylees/Downloads/VCI_ENSO_lag1_correlation.png')

# VECTORIZE this shit ...
xr.apply_ufunc(

)


pearsonr(stacked.isel(point=1).values, nino_seas['NINO34'].values)

# unstack
stacked.unstack('point').to_dataset(name=f'corrcoef')


# --------------------
#
# --------------------
