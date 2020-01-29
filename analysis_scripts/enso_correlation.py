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
import pickle

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

with open(data_dir.parents[0] / 'one_month_forecast_ALL_ds.pkl', 'rb') as fp:
    ds = pickle.load(fp)

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
# correlate with each pixel (SPATIAL CORRELATION)
# ---------------------------
from scipy.stats.stats import pearsonr
from datetime import datetime


def stack_pixels(da: xr.DataArray) -> xr.DataArray:
    return da.stack(pixel=('lat', 'lon')).groupby('pixel')



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
    # stacked = stack_pixels(da).first()
    stacked = da.stack(pixel=('lat', 'lon'))
    # drop the missing pixels (all missing)
    stacked = stacked.dropna(dim='pixel', how='all')
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
    pixel_rs = []
    for pixel in range(len(final_stacked.pixel)):
        if pixel % 1000 == 0:
            pct = f'{(pixel / len(final_stacked.pixel)) * 100 :.1f}%'
            print(pct)
        x1 = final_stacked.isel(pixel=pixel).values
        x2 = series.loc[np.isin(series.index, pd.to_datetime(final_times))].values
        r = _calculate_pearsonr(x1, x2)
        pixel_rs.append(r)

    # create final dataset
    out = xr.ones_like(final_stacked).isel(time=0)
    out.values = pixel_rs
    return out.unstack('pixel').to_dataset(name=f'correlation')


chirps_nino_corr_ds = calculate_slow_pearsonr(chirps_norm_seas['precip'], shifted_nino)
# vci_nino_corr_ds = calculate_slow_pearsonr(vci_norm_seas['VCI'], shifted_nino)




def plot_correlation_ds(correlation_ds: xr.Dataset, variable: str):
    fig, ax = plt.subplots(figsize=(12, 8))
    correlation_ds.correlation.plot(ax=ax)
    ax.set_title(f'{variable} Correlation with ENSO at Seasonal Timesteps: Lag 1')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_yticklabels('')
    ax.set_xticklabels('')
    ax.set_xticks([])
    ax.set_yticks([])
    fig.savefig(f'/Users/tommylees/Downloads/{variable}_ENSO_lag1_correlation.png')


variable='precipitation'
plot_correlation_ds(chirps_nino_corr_ds, variable=variable)
# title = 'VCI Correlation with ENSO at Seasonal Timesteps: Lag 1'


# VECTORIZE this shit ...
# xr.apply_ufunc(

# )


pearsonr(stacked.isel(pixel=1).values, nino_seas['NINO34'].values)

# unstack
stacked.unstack('pixel').to_dataset(name=f'corrcoef')

# ---------------------------
# correlate with each time (TEMPORAL CORRELATION)
# ---------------------------
da = chirps_norm_seas['precip']

stacked = stack_pixels(da).first()
# da.stack(pixel=('time')).groupby('time').all()


# --------------------
# calculate a Kendall RANK correlation
# --------------------
# http://martin-jung.github.io/post/2018-xarrayregression/

if False:

    def k_cor(x, y, pthres: float = 0.05, direction: bool = True):
        """
        Uses the scipy stats module to calculate a Kendall correlation test
        :x vector: Input pixel vector to run tests on
        :y vector: The date input vector
        :pthres: Significance of the underlying test
        :direction: output only direction as output (-1 & 1)
        """
        assert False
        # Check NA values
        co = np.count_nonzero(~np.isnan(x))
        if co < 4:  # If fewer than 4 observations return -9999
            return -9999
        # Run the kendalltau test
        tau, p_value = stats.kendalltau(x, y)

        # Criterium to return results in case of Significance
        if p_value < pthres:
            # Check direction
            if direction:
                if tau < 0:
                    return -1
                elif tau > 0:
                    return 1
            else:
                return tau
        else:
        return 0


    # The function we are going to use for applying our kendal test per pixel
    def kendall_correlation(x: xr.DataArray, y: xr.DataArray, dim: str = 'year'):
        # x = Pixel value, y = a vector containing the date, dim == dimension
        return xr.apply_ufunc(
            k_cor, x, y,
            input_core_dims=[[dim], [dim]],
            vectorize=True,  # !Important!
            output_dtypes=[int]
        )


    time = xr.DataArray(np.arange(len(vci['time']))+1, dims='time',
                    coords={'time': vci['time']})
    r = kendall_correlation(vci.unstack(), time, 'time')


# ------------------
# xarray covariance
# ------------------
# https://github.com/pydata/xarray/issues/1115
# https://github.com/pydata/xarray/pull/3550
# mvstats = https://github.com/hrishikeshac/mvstats/blob/master/mvstats/mvstats.py

import mvstats.mvstats as mv


other_vars = [v for v in ds.data_vars if v != 'VCI']
all_ds = []
lags = np.array([0, 1, 2, 3])
for var_ in other_vars:
    v_str = f"VCI_{var_}"
    all_ = []
    for lag in lags:
        print(f"Variable: {var_} Lag {lag}")
        var_name = f"cov_{var_}_lag{lag}"
        # covs.append(
        #     mv.cov(ds.VCI, ds[var_], lagy=lag).rename(var_name)
        # )
        # d_ = xr.merge(covs)
        all_.append(
            mv.cor(ds.VCI, ds[var_], lagy=lag).rename(var_name).values
        )

        cor_data = np.array(all_)  # lag, lat, lon

    # create xarray object
    d = xr.Dataset(
        {
            v_str: (
                ["lag", "lat", "lon"],
                cor_data,
            )
        },
        coords={
            "lag": lags,
            "lon": ds.lon,
            "lat": ds.lat,
        },
    )
    all_ds.append(d)

corrs = xr.auto_combine(all_ds)

# Plot the correlation maps
other_vars = [v for v in ds.data_vars if v != 'VCI']
kwargs = dict(vmin=-0.4, vmax=0.4, cmap='RdBu_r')
fig, axes = plt.subplots(len(other_vars), len(lags), figsize=(10, 12))

for i, (var_, lag) in enumerate([v for v in itertools.product(other_vars, lags)]):
    ax_ix = np.unravel_index(i, (len(other_vars), len(lags)))
    ax = axes[ax_ix]
    corrs[f'VCI_{var_}'].sel(lag=lag).plot(ax=ax, add_colorbar=False, **kwargs)

    ax.set_title(f'{var_} Lag: {lag}')

    # Turn off tick labels
    ax.set_axis_off()

plt.tight_layout()
fig.savefig('/Users/tommylees/Downloads/pixel_wise_correlation_maps.png')


# -------------------
# plot the variables
# -------------------

stacked = ds.stack(pixel=('lat', 'lon'))
