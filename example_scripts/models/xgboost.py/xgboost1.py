from pathlib import Path
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

import xgboost as xgb
# import sklearn

%matplotlib
%load_ext autoreload
%autoreload 2

from src.models import GBDT
from src.models.base import ModelBase
from src.models.data import DataLoader, train_val_mask, TrainData
from tests.utils import _make_dataset

def make_test_data(data_dir, experiment='one_month_forecast'):
    # create data (X, y)
    x, _, _ = _make_dataset(size=(5, 5), const=True)
    x_static, _, _ = _make_dataset(size=(5, 5), add_times=False)
    y = x.isel(time=[-1])

    x_add1, _, _ = _make_dataset(size=(5, 5), const=True, variable_name='precip')
    x_add2, _, _ = _make_dataset(size=(5, 5), const=True, variable_name='temp')

    x = xr.merge([x, x_add1, x_add2])

    # calculate normalising dictionaries
    norm_dict = {'VHI': {'mean': 0, 'std': 1},
                 'precip': {'mean': 0, 'std': 1},
                 'temp': {'mean': 0, 'std': 1}}
    static_norm_dict = {'VHI': {'mean': 0.0,
                        'std': 1.0}}

    # make the appropriate folders
    test_features = data_dir / f'features/{experiment}/train/hello'
    test_features.mkdir(parents=True, exist_ok=True)
    pred_features = data_dir / f'features/{experiment}/test/hello'
    pred_features.mkdir(parents=True, exist_ok=True)
    static_features = data_dir / f'features/static'
    static_features.mkdir(parents=True, exist_ok=True)

    # write the data out
    with (
        data_dir / f'features/{experiment}/normalizing_dict.pkl'
    ).open('wb') as f:
        pickle.dump(norm_dict, f)

    with (
        data_dir / f'features/static/normalizing_dict.pkl'
    ).open('wb') as f:
        pickle.dump(static_norm_dict, f)

    x.to_netcdf(test_features / 'x.nc')
    x.to_netcdf(pred_features / 'x.nc')
    y.to_netcdf(test_features / 'y.nc')
    y.to_netcdf(pred_features / 'y.nc')
    x_static.to_netcdf(static_features / 'data.nc')

data_path = data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data/')
data_path = data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/test/')

make_test_data(data_dir)

# ------------------------
# HIGH LEVEL API
# ------------------------

model = GBDT(
    data_dir, include_pred_month=False,
    experiment='one_month_forecast', include_monthly_aggs=False
)
model.train()
model.evaluate(save_preds=True)

# ------------------------
# Inside the weeds
# ------------------------

# ------------------------
# DATA LOADER
# ------------------------
len_mask = len(DataLoader._load_datasets(
    data_path, mode='train',
    shuffle_data=False, experiment='one_month_forecast'
))

# validation split = 10%
val_split = 0.1
train_mask, val_mask = train_val_mask(len_mask, val_split)

ignore_vars = []
train_dataloader = DataLoader(data_path=model.data_path,
                              batch_file_size=model.batch_size,
                              experiment=model.experiment,
                              shuffle_data=True, mode='train',
                              pred_months=model.pred_months,
                              mask=train_mask,
                              ignore_vars=model.ignore_vars,
                              monthly_aggs=model.include_monthly_aggs,
                              surrounding_pixels=model.surrounding_pixels,
                              static=model.include_static)
val_dataloader = DataLoader(data_path=model.data_path,
                            batch_file_size=model.batch_size,
                            experiment=model.experiment,
                            shuffle_data=False, mode='train',
                            pred_months=model.pred_months, mask=val_mask,
                            ignore_vars=model.ignore_vars,
                            monthly_aggs=model.include_monthly_aggs,
                            surrounding_pixels=model.surrounding_pixels,
                            static=model.include_static)

# ------------------------
# FIT
# ------------------------
xgbkwargs = {}

# set objective function
xgbkwargs['objective'] = 'reg:squarederror'
model2 = xgb.XGBRegressor(**xgbkwargs)

# collect all the data into arrays
input_train_x, input_train_y = [], []
for x, y in train_dataloader:
    input_train_x.append(model._concatenate_data(x))
    input_train_y.append(y)

input_train_x_np = np.concatenate(input_train_x, axis=0)
input_train_y_np = np.concatenate(input_train_y)

#
fit_inputs = {'X': input_train_x_np, 'y': input_train_y_np}

# early stopping criterion
early_stopping = None
if early_stopping is not None:
    input_val_x, input_val_y = [], []

    for val_x, val_y in val_dataloader:
        input_val_x.append(self._concatenate_data(val_x))
        input_val_y.append(val_y)

    input_val_x_np = np.concatenate(input_val_x, axis=0)
    input_val_y_np = np.concatenate(input_val_y)

    fit_val_inputs = {
        'eval_set': [input_val_x_np, input_val_y_np],
        'early_stopping_rounds': early_stopping,
        'eval_metric': 'rmse'
    }
    fit_inputs.update(fit_val_inputs)

model2.fit(**fit_inputs)

# ------------------------
# PREDICT
# ------------------------
test_arrays_loader = DataLoader(
    data_path=data_path, batch_file_size=model.batch_size,
    experiment=model.experiment, shuffle_data=False, mode='test',
    pred_months=model.pred_months, surrounding_pixels=model.surrounding_pixels,
    ignore_vars=model.ignore_vars, monthly_aggs=model.include_monthly_aggs,
    static=model.include_static
)

preds_dict = {}
test_arrays_dict = {}
for dict in test_arrays_loader:
    for key, val in dict.items():
        x = model._concatenate_data(val.x)
        preds = model2.predict(x)
        preds_dict[key] = preds
        test_arrays_dict[key] = {
            'y': val.y, 'latlons': val.latlons, 'time': val.target_time
        }

output_dict = {}
total_preds = []
total_true = []

for key, vals in test_arrays_dict.items():
    true = vals['y']
    preds = preds_dict[key]

    output_dict[key] = np.sqrt(mean_squared_error(true, preds)).item()

    total_preds.append(preds)
    total_true.append(true)
