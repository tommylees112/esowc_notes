import numpy as np
from collections import defaultdict
import calendar
from datetime import datetime, date
from pathlib import Path
import xarray as xr

from typing import cast, Dict, List, Optional, Union, Tuple
from typing import DefaultDict as DDict

from src.engineer import NowcastEngineer, OneMonthForecastEngineer
from src.preprocess.base import BasePreProcessor
from src.utils import minus_months
from tests.utils import _make_dataset

%load_ext autoreload
%autoreload 2

# variables
years = [1990]
test_year = [years[0]]
year = years[0]
target_variable='VHI'
target_month=7
pred_months=3
expected_length=pred_months

data_dir = data_path = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')

n = NowcastEngineer(data_dir)
o = OneMonthForecast(data_dir)
engineer = Engineer(data_dir)


n.engineer(
    test_year=test_year, target_variable=target_variable,
    pred_months=pred_months, expected_length=expected_length,
)


# ------------------------------------------------------------------------------
# Play with the class functions
# ------------------------------------------------------------------------------
data = engineer._make_dataset()

# get the test datetime
max_date = date(year, target_month, calendar.monthrange(year, target_month)[-1])
mx_year, mx_month, max_train_date = minus_months(year, target_month, diff_months=1)
_, _, min_date = minus_months(mx_year, mx_month, diff_months=pred_months)
# convert to numpy datetime
min_date_np = np.datetime64(str(min_date))
max_date_np = np.datetime64(str(max_date))
max_train_date_np = np.datetime64(str(max_train_date))

ds = data
# boolean array indexing the TARGET variable timesteps
x_target = (
    (ds.time.values > min_date_np) & (ds.time.values <= max_train_date_np)
)
y_target = (
    (ds.time.values > max_train_date_np) & (ds.time.values <= max_date_np)
)
# boolean array indexing the NON-TARGET variables timesteps
x_non_target = (
    (ds.time.values > min_date_np) & (ds.time.values <= max_date_np)
)

train_ds = n._train_test_split(
    data, cast(List, test_year), target_variable,
    pred_months
)

min_date = n.get_datetime(train_ds.time.values.min())
max_date = n.get_datetime(train_ds.time.values.max())
cur_min_date = max_date
cur_pred_year, cur_pred_month = max_date.year, max_date.month
cur_min_date = max_date

arrays, cur_min_date = n.stratify_xy(
    ds=train_ds, year=cur_pred_year,
    target_variable=target_variable, target_month=cur_pred_month,
    pred_months=pred_months,
)
if arrays is not None:
    n.calculate_normalization_values(arrays['x'])
    n._save(
        arrays, year=cur_pred_year, month=cur_pred_month,
        dataset_type='train'
    )
cur_pred_year, cur_pred_month = cur_min_date.year, cur_min_date.month
