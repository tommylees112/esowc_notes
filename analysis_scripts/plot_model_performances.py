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

#
# ealstm_pred_ds = open_pred_data('ealstm')
ealstm_pred_ds = xr.open_mfdataset((data_dir / 'models' / 'one_month_forecast' / 'ealstm' / '*.nc').as_posix())
ealstm_pred_ds = ealstm_pred_ds.sortby('time')
# ealstm_pred_ds.to_netcdf(out_dir / f'{model}_prediction_VHI.nc')
ealstm_pred_da = ealstm_pred_ds.preds
ealstm_pred_da = ealstm_pred_da.transpose('time', 'lat', 'lon')

#
# lr_pred_ds = open_pred_data('linear_regression')
lr_pred_ds = xr.open_mfdataset((data_dir / 'models' / 'one_month_forecast' / 'linear_regression' / '*.nc').as_posix())
lr_pred_ds = lr_pred_ds.sortby('time')
# lr_pred_ds.to_netcdf(out_dir / f'{model}_prediction_VHI.nc')
lr_pred_da = lr_pred_ds.preds
lr_pred_da = lr_pred_da.transpose('time', 'lat', 'lon')


#
# persistence_pred_ds = open_pred_data('previous_month')
persistence_pred_ds = xr.open_mfdataset((data_dir / 'models' / 'one_month_forecast' / 'previous_month' / '*.nc').as_posix())
persistence_pred_ds = persistence_pred_ds.sortby('time')
# persistence_pred_ds.to_netcdf(out_dir / f'{model}_prediction_VHI.nc')
persistence_pred_da = persistence_pred_ds.preds
persistence_pred_da = persistence_pred_da.transpose('time', 'lat', 'lon')

#
# ln_pred_ds = open_pred_data('linear_network')
# ln_pred_ds = xr.open_mfdataset((data_dir / 'models' / 'one_month_forecast' / 'linear_network' / '*.nc').as_posix())
# ln_pred_ds = ln_pred_ds.sortby('time')
# # ln_pred_ds.to_netcdf(out_dir / f'{model}_prediction_VHI.nc')
# ln_pred_da = ln_pred_ds.preds

rnn_pred_ds = xr.open_mfdataset((data_dir / 'models' / 'one_month_forecast' / 'rnn' / '*.nc').as_posix())
rnn_pred_ds = rnn_pred_ds.sortby('time')
# rnn_pred_ds.to_netcdf(out_dir / f'{model}_prediction_VHI.nc')
rnn_pred_da = rnn_pred_ds.preds
rnn_pred_da = rnn_pred_da.transpose('time', 'lat', 'lon')

#
true_paths = [f for f in (data_dir / 'features' / 'one_month_forecast' / 'test').glob('*/y.nc')]
true_ds = xr.open_mfdataset(true_paths).sortby('time').compute()
# true_ds.to_netcdf(out_dir / 'true_VHI_data.nc')
true_da = true_ds.VCI

# --------------------------
# plot spatial error metrics
# --------------------------
from src.analysis import spatial_rmse
from src.analysis.plot_regions import get_vrange
from src.utils import drop_nans_and_flatten
import seaborn as sns

ealstm_rmse_da = spatial_rmse(true_da, ealstm_pred_da)
persistence_rmse_da = spatial_rmse(true_da, persistence_pred_da)
# persistence_rmse_da = spatial_rmse(true_da.isel(time=slice(0,5)), persistence_pred_da)
# ln_rmse_da = spatial_rmse(true_da.isel(time=slice(0,5)), ln_pred_da)
# lr_rmse_da = spatial_rmse(true_da.isel(time=slice(0,5)), lr_pred_da)
# lr_rmse_da = spatial_rmse(true_da, lr_pred_da)
rnn_rmse_da = spatial_rmse(true_da, rnn_pred_da)

ealstm_rmse_da.name = 'rmse'
persistence_rmse_da.name = 'rmse'
rnn_rmse_da.name = 'rmse'
# ln_rmse_da.name = 'rmse'
# lr_rmse_da.name = 'rmse'

vmin, _ = get_vrange(
    drop_nans_and_flatten(ealstm_rmse_da), drop_nans_and_flatten(ealstm_rmse_da)
)
vmax = 30

def plot_model_spatial_rmse(model: str,
                            model_rmse: xr.DataArray,
                            vmin: Optional[float] = None,
                            vmax: Optional[float] = None):
    fig, ax = plt.subplots()
    model_rmse.plot.contourf(ax=ax, vmin=vmin, vmax=vmax)
    ax.set_title(f'RMSE for {model} (test vs. preds) 2018')
    fig.savefig(out_dir / f'{model}_VHI_2018_RMSE_pixel.png')
    fig.savefig(Path('/Users/tommylees/Downloads') / f'{model}_VHI_2018_RMSE_pixel.png')

plot_model_spatial_rmse(
    model='ealstm', model_rmse=ealstm_rmse_da,
    vmin=vmin, vmax=vmax
)
plot_model_spatial_rmse(
    model='persistence', model_rmse=persistence_rmse_da,
    vmin=vmin, vmax=vmax
)
plot_model_spatial_rmse(
    model='persistence', model_rmse=rnn_rmse_da,
    vmin=vmin, vmax=vmax
)
# plot_model_spatial_rmse(model='linear_network', model_rmse=ln_rmse_da)
# plot_model_spatial_rmse(model='linear_regression', model_rmse=lr_rmse_da)

# histogram
fig, ax = plt.subplots()
sns.distplot(drop_nans_and_flatten(ealstm_rmse_da), ax=ax, label='EALSTM')
sns.distplot(drop_nans_and_flatten(persistence_rmse_da), ax=ax, label='Persistence')
# sns.distplot(drop_nans_and_flatten(ln_rmse_da), ax=ax, label='Linear Neural Network')
# sns.distplot(drop_nans_and_flatten(lr_rmse_da), ax=ax, label='Linear Regression')
plt.legend()
ax.set_title('Comparison of RMSE Scores for the models')
ax.set_xlabel('RMSE')
ax.set_ylabel('Density')
fig.savefig(Path('/Users/tommylees/Downloads') /'model_intercomparison_histograms.png')
fig.savefig(out_dir / 'model_intercomparison_histograms.png')


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
