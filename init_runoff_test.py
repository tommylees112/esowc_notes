%load_ext autoreload
%autoreload 2

from pathlib import Path
from tests.utils import _create_runoff_features_dir, _make_runoff_data
from src.utils import minus_timesteps
from pandas.tseries.offsets import Day

import numpy as np
import calendar
from datetime import date
import xarray as xr
import warnings
import pandas as pd
from pandas.tseries.offsets import Day
from collections import defaultdict
import pickle

from typing import cast, DefaultDict, Dict, List, Optional, Union, Tuple
from src.utils import minus_timesteps
from src.engineer.base import _EngineerBase

path = Path('data')

if True:
    # X, y, static = _create_runoff_features_dir(path)
    ds, static = _make_runoff_data(
        start_date='1998-01',
        end_date='2002-01'
    )
    ds.to_netcdf(path/'interim/camels_preprocessed/data.nc')
    static.to_netcdf(path/'interim/static/data.nc')

from src.engineer.one_timestep_forecast import _OneTimestepForecastEngineer
E = _OneTimestepForecastEngineer(path)

E._process_dynamic('2013', target_variable='discharge_vol')


# use the dataloader
dl = DataLoader()


x_vars = ['precip', 'pet']
target_var = 'discharge'
seq_length = 365

# 1. train test data

min_test_date_str = '2000'
min_test_date = pd.to_datetime(min_test_date_str)
max_test_date = pd.to_datetime(ds.time.max().values) + Day(1)
max_train_date = min_test_date - Day(1)
min_ds_date = pd.to_datetime(ds.time.min().values)

print(
    f'Generating data.\nTrain: {min_ds_date}-{max_train_date}'
    f'\nTest:  {min_test_date}-{max_test_date} '
)
test_ds = ds.sel(time=slice(min_test_date, max_test_date))
train_ds = ds.sel(time=slice(min_ds_date, max_train_date))

# check no model leakage train-test
assert train_ds.time.min().values < test_ds.time.min().values

# 1. split into x,y pairs

# TEST DATA
self.stratify_xy(
    ds=ds,
    target_times=test_ds.time.values,
    train=False,
    resolution='D'
)

# TRAIN DATA
self.stratify_xy(
    ds=ds,
    target_times=train_ds.time.values,
    train=True,
    resolution='D'
)



print("\n** Generating Test Data **\n")
for target_time in test_ds.time.values:
    print(f"Generating data for target time: {target_time}")
    max_X_date = minus_timesteps(target_time, 1, 'D')
    min_X_date = minus_timesteps(target_time, seq_length, 'D')

    # select from the ORIGINAL dataset (ds)
    # because X data can be already seen by the
    # model in the train data just not the y data.

    # split into x, y
    X_dataset = ds[x_vars].sel(time=slice(min_X_date, max_X_date))
    y_dataset = ds[target_var].sel(time=target_time)

    ds_dict = {"x": X_dataset, "y": y_dataset}

    # save to netcdf
    # self._save(ds_dict, target_time, dataset_type='test', resolution='D')

    break


# TRAIN DATA
# only for the months AFTER `seq_length` otherwise not
# enough X input timesteps
print("\n** Generating Training Data **\n")
for target_time in train_ds.time.values:
    max_X_date = minus_timesteps(target_time, 1, 'D')
    min_X_date = minus_timesteps(target_time, seq_length, 'D')
    print(f"Min: {min_X_date} Max: {max_X_date}")

    if min_X_date < min_ds_date:
        print(f"Not enough input timesteps for {target_time}")
        # return

    print(f"Generating data for target time: {target_time}")
    # split into x, y
    X_dataset = ds[x_vars].sel(time=slice(min_X_date, max_X_date))
    y_dataset = ds[target_var].sel(time=target_time)

    ds_dict = {"x": X_dataset, "y": y_dataset}
    # self._save(ds_dict, target_time, dataset_type='train', resolution='D')

