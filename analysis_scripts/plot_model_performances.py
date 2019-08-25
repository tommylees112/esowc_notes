from pathlib import Path
import calendar

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from typing import Optional, Tuple, List, Union

if 'tommylees' in Path('.').absolute().parts:
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
out_dir = data_dir / 'analysis' / 'region_analysis'

from src.analysis import plot_shap_values, annual_r2_scores, plot_predictions

# -----------------------
# read in true and pred data
# -----------------------
def get_datetimes_from_files(files: List[Path]) -> List:
    datetimes = []
    for path in files:
        year = path.name.replace('.nc', '').split('_')[-2]
        month = path.name.replace('.nc', '').split('_')[-1]
        day = calendar.monthrange(int(year), int(month))[-1]
        dt = pd.to_datetime(f'{year}-{month}-{day}')
        datetimes.append(dt)
    return datetimes


def open_pred_data(model: str,
                   experiment: str = 'one_month_forecast'):
    import calendar

    files = [
        f for f
        in (data_dir / 'models' / 'one_month_forecast' / model).glob('*.nc')
    ]
    files.sort(key=lambda path: int(path.name.split('_')[-1][:-3]))
    times = get_datetimes_from_files(files)

    pred_ds = xr.merge([
        xr.open_dataset(f).assign_coords(time=times[i]).expand_dims('time')
        for i, f in enumerate(files)
    ])

    return pred_ds

def read_pred_data(model: str):
    model_pred_dir = (data_dir / 'models' / 'one_month_forecast' / model)
    pred_ds = xr.open_mfdataset((model_pred_dir / '*.nc').as_posix())
    pred_ds.sortby('time')
    pred_da = pred_ds.preds
    pred_da = pred_da.transpose('time', 'lat', 'lon')

    return pred_ds, pred_da


# read pred data
ealstm_pred_ds, ealstm_pred_da = read_pred_data('ealstm')
persistence_pred_ds, persistence_pred_da = read_pred_data('previous_month')
# lr_pred_ds, lr_pred_da = read_pred_data('linear_regression')
# rnn_0surrounding_pred_ds, rnn_0surrounding_pred_da = read_pred_data('rnn_surrounding_0')
# ealstm_0surrounding_pred_ds, ealstm_0surrounding_pred_da = read_pred_data('ealstm_surrounding_0')
# rnn_pred_ds, rnn_pred_da = read_pred_data('rnn')

# read true data
true_paths = [f for f in (data_dir / 'features' / 'one_month_forecast' / 'test').glob('*/y.nc')]
true_ds = xr.open_mfdataset(true_paths).sortby('time').compute()
# true_ds.to_netcdf(out_dir / 'true_VHI_data.nc')
true_da = true_ds.VCI.transpose('time', 'lat', 'lon')

# --------------------------
# plot spatial error metrics
# --------------------------
from src.analysis import spatial_rmse
from src.analysis.evaluation import spatial_r2
from src.analysis.plot_regions import get_vrange
from src.utils import drop_nans_and_flatten
import seaborn as sns

# persistence_rmse_da = spatial_rmse(true_da.isel(time=slice(0,5)), persistence_pred_da)
# ealstm0_rmse_da = spatial_rmse(true_da, ealstm_0surrounding_pred_da)
ealstm_rmse_da = spatial_rmse(true_da, ealstm_pred_da)
persistence_rmse_da = spatial_rmse(true_da, persistence_pred_da)
ealstm_r2_da = spatial_r2(true_da, ealstm_pred_da)
persistence_r2_da = spatial_r2(true_da, persistence_pred_da)

# rnn0_rmse_da = spatial_rmse(true_da, rnn_0surrounding_pred_da)
# ln_rmse_da = spatial_rmse(true_da, ln_pred_da)

# including surrounding pixels
# ealstm_rmse_da = spatial_rmse(true_da.isel(lat=slice(1, -1), lon=slice(1, -1)), ealstm_pred_da)
# rnn_rmse_da = spatial_rmse(true_da.isel(lat=slice(1, -1), lon=slice(1, -1)), rnn_pred_da)
# lr_rmse_da = spatial_rmse(true_da.isel(lat=slice(1, -1), lon=slice(1, -1)), lr_pred_da)


ealstm_rmse_da.name = 'rmse'
ealstm_r2_da.name = 'r2'
# ealstm0_rmse_da.name = 'rmse'
# rnn0_rmse_da.name = 'rmse'
# rnn_rmse_da.name = 'rmse'
persistence_rmse_da.name = 'rmse'
persistence_r2_da.name = 'r2'
# lr_rmse_da.name = 'rmse'


vmin, vmax = get_vrange(
    drop_nans_and_flatten(ealstm_rmse_da), drop_nans_and_flatten(persistence_rmse_da)
)
# vmax = 30

def plot_model_spatial_rmse(model: str,
                            model_rmse: xr.DataArray,
                            vmin: Optional[float] = None,
                            vmax: Optional[float] = None,
                            cmap: str = 'viridis'):
    fig, ax = plt.subplots()
    model_rmse.plot.contourf(ax=ax, vmin=vmin, vmax=vmax, cmap=cmap)
    ax.set_title(f'RMSE for {model} (test vs. preds) 2018')
    fig.savefig(out_dir / f'{model}_VHI_2018_RMSE_pixel.png')
    fig.savefig(Path('/Users/tommylees/Downloads') / f'{model}_VHI_2018_RMSE_pixel.png')

# plot_model_spatial_rmse(
#     model='ealstm_surrounding_1', model_rmse=ealstm_rmse_da,
#     vmin=vmin, vmax=vmax
# )
plot_model_spatial_rmse(
    model='persistence', model_rmse=persistence_rmse_da,
    vmin=vmin, vmax=vmax
)
# plot_model_spatial_rmse(
#     model='rnn_surrounding_1', model_rmse=rnn_rmse_da,
#     vmin=vmin, vmax=vmax
# )
# plot_model_spatial_rmse(
#     model='ealstm_surrounding_0', model_rmse=ealstm0_rmse_da,
#     vmin=vmin, vmax=vmax
# )
plot_model_spatial_rmse(
    model='ealstm', model_rmse=ealstm_rmse_da,
    vmin=vmin, vmax=vmax
)

vmin, vmax = get_vrange(
    drop_nans_and_flatten(ealstm_rmse_da-persistence_rmse_da), drop_nans_and_flatten(ealstm_rmse_da-persistence_rmse_da)
)
plot_model_spatial_rmse(
    model='ealstm', model_rmse=ealstm_rmse_da-persistence_rmse_da,
    vmin=vmin, vmax=vmax
)

# plot_model_spatial_rmse(
#     model='rnn_surrounding_0', model_rmse=rnn0_rmse_da,
#     vmin=vmin, vmax=vmax
# )
# plot_model_spatial_rmse(
#     model='linear_regression_surrounding_1', model_rmse=lr_rmse_da,
#     vmin=vmin, vmax=vmax
# )
# plot_model_spatial_rmse(model='linear_network', model_rmse=ln_rmse_da)
# plot_model_spatial_rmse(model='linear_regression', model_rmse=lr_rmse_da)


#

vmin, vmax = get_vrange(
    drop_nans_and_flatten(ealstm_r2_da), drop_nans_and_flatten(persistence_r2_da)
)


def plot_model_spatial_r2(model: str,
                          model_r2: xr.DataArray,
                          vmin: Optional[float] = None,
                          vmax: Optional[float] = None,
                          cmap: str = 'viridis'):
    fig, ax = plt.subplots()
    model_r2.plot.contourf(ax=ax, vmin=vmin, vmax=vmax, cmap=cmap)
    ax.set_title(f'R2 for {model} (test vs. preds) 2018')
    fig.savefig(out_dir / f'{model}_VHI_2018_r2_pixel.png')
    fig.savefig(Path('/Users/tommylees/Downloads') / f'{model}_VHI_2018_r2_pixel.png')

vmin = -0.1
vmax = 0.7
plot_model_spatial_r2(
    model='ealstm', model_r2=ealstm_r2_da,
    vmin=vmin, vmax=vmax
)
plot_model_spatial_r2(
    model='persistence', model_r2=persistence_r2_da,
    vmin=vmin, vmax=vmax
)

# plot teh difference
vmin, vmax = get_vrange(
    drop_nans_and_flatten(ealstm_r2_da-persistence_r2_da), drop_nans_and_flatten(ealstm_r2_da-persistence_r2_da)
)
vmax = max(abs(vmin), vmax)
vmin = -max(abs(vmin), vmax)

plot_model_spatial_r2(
    model='ealstm - persistence', model_r2=ealstm_r2_da-persistence_r2_da,
    vmin=vmin, vmax=vmax, cmap='RdBu'
)

fig, ax = plt.subplots()
sns.distplot(drop_nans_and_flatten(ealstm_rmse_da), ax=ax, label='ealstm')
sns.distplot(drop_nans_and_flatten(persistence_rmse_da), ax=ax, label='persistence')
plt.legend()
ax.set_title('Comparison of RMSE Scores for the models')
ax.set_xlabel('RMSE')
ax.set_ylabel('Density')
fig.savefig(Path('/Users/tommylees/Downloads') /'model_intercomparison_histograms.png')
fig.savefig(out_dir / 'model_intercomparison_histograms_LATEST.png')

lstm_r2=drop_nans_and_flatten(ealstm_r2_da)
base_r2=drop_nans_and_flatten(persistence_r2_da)
base_r2 = base_r2[base_r2 > -3.0]
lstm_r2 = lstm_r2[lstm_r2 > -3.0]

fig, ax = plt.subplots()
sns.distplot(lstm_r2, ax=ax, label='ealstm')
sns.distplot(base_r2, ax=ax, label='persistence')
plt.legend()
ax.set_title('Comparison of r2 Scores for the models')
ax.set_xlabel('r2')
ax.set_ylabel('Density')
fig.savefig(Path('/Users/tommylees/Downloads') /'model_intercomparison_histograms_r2.png')
fig.savefig(out_dir / 'model_intercomparison_histograms_LATEST_r2.png')


# -------------------------
# histogram
# -------------------------
fig, ax = plt.subplots()
sns.distplot(drop_nans_and_flatten(ealstm_rmse_da), ax=ax, label='ealstm_surrounding_1')
sns.distplot(drop_nans_and_flatten(persistence_rmse_da), ax=ax, label='persistence')
sns.distplot(drop_nans_and_flatten(rnn_rmse_da), ax=ax, label='rnn_surrounding_1')
sns.distplot(drop_nans_and_flatten(ealstm0_rmse_da), ax=ax, label='ealstm_surrounding_0')
sns.distplot(drop_nans_and_flatten(rnn0_rmse_da), ax=ax, label='rnn_surrounding_0')
# sns.distplot(drop_nans_and_flatten(lr_rmse_da), ax=ax, label='linear_regression_surrounding_1')
# sns.distplot(drop_nans_and_flatten(ln_rmse_da), ax=ax, label='Linear Neural Network')
# sns.distplot(drop_nans_and_flatten(lr_rmse_da), ax=ax, label='Linear Regression')
plt.legend()
ax.set_title('Comparison of RMSE Scores for the models')
ax.set_xlabel('RMSE')
ax.set_ylabel('Density')
fig.savefig(Path('/Users/tommylees/Downloads') /'model_intercomparison_histograms.png')
fig.savefig(out_dir / 'model_intercomparison_histograms_LATEST.png')


# --------------------------
# plotting the VDI
# --------------------------



# --------------------------
# functions
# --------------------------

def stack_pixels(da: xr.DataArray) -> xr.DataArray:
    return da.stack(point=('lat', 'lon')).groupby('point')


# stack
pred_stacked = stack_pixels(ealstm_pred_da).first()
true_stacked = stack_pixels(true_da).first()

# unstack
true_stacked.unstack('point').to_dataset(name=f'SPI{scale}')
pred_stacked.unstack('point').to_dataset(name=f'SPI{scale}')


# test mse
# impute missing values?
# https://scikit-learn.org/stable/modules/impute.html#impute
pred_stacked = stack_pixels(ealstm_pred_da).first()
true_stacked = stack_pixels(true_da).first()

pred_2d = pred_stacked.values.T
true_2d = true_stacked.values.T

(np.isnan(pred_2d) | np.isnan(true_2d)).mean()
np.where(np.isnan(pred_2d) | np.isnan(true_2d))

#
from sklearn.impute import SimpleImputer
imp = SimpleImputer(missing_values=np.nan, strategy='mean')
imp.fit(pred_2d)
pred_2d = imp.transform(pred_2d)

imp = SimpleImputer(missing_values=np.nan, strategy='mean')
imp.fit(true_2d)
true_2d = imp.transform(true_2d)

np.sqrt(mean_squared_error(true_2d, pred_2d))
