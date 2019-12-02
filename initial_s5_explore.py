from src.preprocess import S5Preprocessor
from pathlib import Path
import xarray as xr
import numpy as np
from pandas import Timedelta

import cfgrib

%load_ext autoreload
%autoreload 2

data_path = Path('data')
ds = xr.open_dataset(data_path / 'interim/s5_preprocessed/s5_tprate_kenya.nc', chunks={'number': 1})

d_min = xr.open_dataset(data_path / 'interim/s5_interim/tprate/Y2014_M01_12_tprate_kenya.nc')
d_raw = xr.open_dataset(
    'data/raw/seasonal-monthly-single-levels/total_precipitation/2014/Y2014_M01_12.grib', engine='cfgrib'
)

## check how we have got 51 ensemble members?
# first 25 are mostly nan, second 25 are pretty much all nan
n_nulls = ds.isnull().mean(
    dim=['lat', 'lon', 'time']
)
print("Proportion of nans in each number (ensemble member)", n_nulls.tprate.values)

# MEAN of ensemble
ds = ds.mean(dim='number')
# OR first 25 ensemble members
ds = ds.isel(number=slice(0, 25))


# --------------------------
# Oxford Server test
# --------------------------
from src.preprocess.seas5.ouce_s5 import OuceS5Data

# --------------------------
# stack the data
# --------------------------
# create the TRUE times
stacked = ds.stack(time=('initialisation_date', 'forecast_horizon'))
t = stacked.time.values
initialisation_dates = np.array(list(zip(*t))[0])
forecast_horizons = np.array(list(zip(*t))[1])
# time_2d = np.array([list(elem) for elem in t])
times = initialisation_dates + forecast_horizons

ds['valid_time'] = (
    ['initialisation_date', 'forecast_horizon'], times.reshape(312, 12)
)
ds.assign_coords(
    time=(['initialisation_date', 'forecast_horizon'], times.reshape(312, 12))
)

stacked['time'] = times
stacked = stacked.assign_coords(
    initialisation_date=('time', initialisation_dates))
stacked = stacked.assign_coords(forecast_horizon=('time', forecast_horizons))
# stacked = stacked.where(stacked['time.day'] == 1, drop=True)
stacked = stacked.dropna(dim='time', how='all')

# FROM THE MODULE
s = S5Preprocessor()
stacked = s.stack_time(ds)

# --------------------------
# map to n months ahead
# --------------------------
# map forecast horizons to months ahead
map_ = {
    pd.Timedelta('28 days 00:00:00'): 1,
    pd.Timedelta('29 days 00:00:00'): 1,
    pd.Timedelta('30 days 00:00:00'): 1,
    pd.Timedelta('31 days 00:00:00'): 1,
    pd.Timedelta('59 days 00:00:00'): 2,
    pd.Timedelta('60 days 00:00:00'): 2,
    pd.Timedelta('61 days 00:00:00'): 2,
    pd.Timedelta('62 days 00:00:00'): 2,
    pd.Timedelta('89 days 00:00:00'): 3,
    pd.Timedelta('90 days 00:00:00'): 3,
    pd.Timedelta('91 days 00:00:00'): 3,
    pd.Timedelta('92 days 00:00:00'): 3,
}

fhs = [pd.Timedelta(fh) for fh in stacked.forecast_horizon.values]
months = [map_[fh] for fh in fhs]
d = d.assign_coords(months_ahead=('time', months))

# SELECT ALL THE ONE MONTH FORECASTS
d.loc[dict(time=d.months_ahead == 1)]
d.loc[dict(time=d.months_ahead == 2)]

# select
var = 'tprate'
d1 = d.loc[dict(time=d.months_ahead == 1)].rename({var: var + '_1'})
d2 = d.loc[dict(time=d.months_ahead == 2)].rename({var: var + '_2'})
d3 = d.loc[dict(time=d.months_ahead == 3)].rename({var: var + '_3'})


# --------------------------
# stack overflow question
# --------------------------
times = [
    pd.to_datetime('2017-01-01'),
    pd.to_datetime('2017-01-31'),
    pd.to_datetime('2017-01-31'),
    pd.to_datetime('2017-02-01'),
    pd.to_datetime('2017-02-02'),
    pd.to_datetime('2017-03-01'),
    pd.to_datetime('2017-03-01'),
    pd.to_datetime('2017-03-29'),
    pd.to_datetime('2017-03-30'),
    pd.to_datetime('2017-04-01'),
    pd.to_datetime('2017-04-01'),
    pd.to_datetime('2017-04-01'),
]
data = np.ones((11, 3, 3))
data[[1, 2, 4, 5, 7, 8], :, :] = np.nan

lat = [0, 1, 2]
lon = [0, 1, 2]


ds = xr.Dataset(
    {'data': (['time', 'lat', 'lon'], data)},
    coords={
        'lon': lon,
        'lat': lat,
        'time': times,
    }
)

ds.where(ds['time.day'] == 1, drop=True)
stacked.where(stacked['time.day'] == 1, drop=True)

# ------------------------------------------------------------------------------
# Select forecasts for a given month
# ------------------------------------------------------------------------------
###
# select all forecasts of a given time (but ignore the )
# stack the `initialisation_date` and `forecast_horizon`
forecast_horizon = ds.forecast_horizon.values
initialisation_date = ds.initialisation_date.values
valid_time = initialisation_date[:, np.newaxis] + forecast_horizon

stacked = ds.stack(time=('initialisation_date', 'forecast_horizon'))
stacked['time'] = stacked.valid_time
stacked = stacked.drop('valid_time')

# or
stacked = ds.stack(time=('initialisation_date', 'forecast_horizon'))
# stacked['time'] = stacked.valid_time

# select forecasts 28days ahead
stacked.sel(forecast_horizon=np.timedelta64(28, 'D'))

# select 'valid_time'
stacked.swap_dims({'time': 'valid_time'}).sel(valid_time='2018-04')


# MAM forecasts
mam = stacked.sel(time=np.isin(stacked['time.month'], [3, 4, 5]))
fig, ax = plt.subplots()
mam.tprate.mean(dim=['time', 'number']).plot(ax=ax)

# SON forecasts
son = stacked.sel(time=np.isin(stacked['time.month'], [9, 10, 11]))
fig, ax = plt.subplots()
son.tprate.mean(dim=['time', 'number']).plot(ax=ax)

#
#
ds.tprate.mean(dim=['number', 'time']).isel(step=0).plot()

timedeltas = [pd.to_timedelta(val) for val in d.step.values]

# select all forecasts of a given time
d.where(d.valid_time == '2018')
valid_time = np.array([pd.to_datetime(val) for val in d.valid_time.values])


# ------------------------------------------------------------------------------
# Testing preprocess
# ------------------------------------------------------------------------------
#####
s = S5Preprocessor()

dir_ = Path(
    'data/raw/seasonal-monthly-single-levels/total_precipitation/2014/Y2014_M01_12.grib'
)
d = s.read_grib_file(dir_)

coords = [c for c in d.coords]
vars = [v for v in d.variables if v not in coords]
variable = '-'.join(vars)

subset_str = 'kenya'
output_path = s.create_filename(
    dir_,
    s.interim,
    variable,
    subset_name=subset_str if subset_str is not None else None
)

if 'latitude' in coords:
    d = d.rename({'latitude': 'lat'})
if 'longitude' in coords:
    d = d.rename({'longitude': 'lon'})

# 5. regrid (one variable at a time)
assert all(np.isin(['lat', 'lon'], [c for c in d.coords])), f"\
Expecting `lat` `lon` to be in d. dims : {[c for c in d.coords]}"

# regrid each variable individually
all_vars = []
for var in vars:
    time = d[var].time
    d_ = s.regrid(
        d[var].to_dataset(name=var), regrid,
        clean=False, reuse_weights=True,
    )
    d_ = d_.assign_coords(time=time)
    all_vars.append(d_)
# merge the variables into one dataset
d2 = xr.merge(all_vars).sortby('initialisation_date')

##
#
s = S5Preprocessor()

var = 'tprate'
mfd = xr.open_mfdataset((s.interim / var).as_posix() + "/*.nc")
mfd = mfd.sortby('initialisation_date')

time = mfd[var].time
d3 = s.resample_time(
    mfd, resample_length='M', upsampling=False,
    time_coord='initialisation_date'
)
d3 = mfd.assign_coords(time=time)

d3.stack(time=['initialisation_date', 'forecast_horizon']).valid_time




