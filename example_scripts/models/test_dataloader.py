import numpy as np
from collections import defaultdict
import calendar
from datetime import datetime, date
from pathlib import Path
import xarray as xr

from typing import cast, Dict, List, Optional, Union, Tuple
from typing import DefaultDict as DDict

from src.engineer import Engineer
from src.preprocess.base import BasePreProcessor


data_path = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
engineer = Engineer(data_path)
engineer.engineer(
    test_year=1990, target_variable='VHI', pred_months=3,
    expected_length=3
)

# wrong shapes!
datasets = engineer._get_preprocessed_files()
ds_list = [xr.open_dataset(ds) for ds in datasets]
dims_list = [
    [dim for dim in ds.dims]
    for ds in ds_list
]
variable_list = [
    [var for var in ds.variables if var not in dims_list[i]][0]
    for i, ds in enumerate(ds_list)
]
da_list = [
    ds[variable_list[i]]
    for i, ds in enumerate(ds_list)
]

#
ds = engineer._make_dataset()
years = [1990]
train_ds, test_dict
train_ds = engineer._train_test_split(
    ds, years, target_variable='VHI',
    pred_months=3, expected_length=3,
)
xy_test, min_test_date = engineer.stratify_xy(
    ds, years[0], target_variable='VHI', target_month=7,
    pred_months=3, expected_length=3
)
train_dict = engineer._stratify_training_data(
    train_ds, target_variable,
    pred_months, expected_length
)







#
years = [1990]
test_year = [years[0]]
year = years[0]
target_variable='VHI'
target_month=7
pred_months=11
expected_length=11

data = engineer._make_dataset()
train_ds = engineer._train_test_split(
    data, cast(List, test_year), target_variable,
    pred_months, expected_length
)

for var in engineer.normalization_values.keys():
    engineer.normalization_values[var]['mean'] /= engineer.num_normalization_values
    engineer.normalization_values[var]['std'] /= engineer.num_normalization_values




xy_test, min_test_date = engineer.stratify_xy(
    ds, years[0], target_variable='VHI', target_month=7,
    pred_months=3, expected_length=3
)

train_dates = ds.time.values <= np.datetime64(str(min_test_date))

output_test_arrays: DDict[int, DDict[int, Dict[str, xr.Dataset]]] = \
    defaultdict(lambda: defaultdict(dict))

for year in years:
    for month in range(1, 13):
        if year > years[0] or month > 1:
            # prevents the initial test set from being recalculated
            xy_test, _ = engineer.stratify_xy(ds, year, target_variable, month,
                                          pred_months, expected_length)
            if xy_test is not None:
                output_test_arrays[year][month] = xy_test

#
x = xr.open_dataset('/Volumes/Lees_Extend/data/ecmwf_sowc/data/features/train/1985_12/x.nc')
y = xr.open_dataset('/Volumes/Lees_Extend/data/ecmwf_sowc/data/features/train/1985_12/y.nc')
