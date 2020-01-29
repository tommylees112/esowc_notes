import seaborn as sns
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import os
import warnings
import calendar
from typing import List, Dict, Tuple

from src.analysis import read_train_data, read_test_data, read_pred_data
from src.analysis import annual_scores
from src.utils import drop_nans_and_flatten
from src.utils import get_ds_mask

%load_ext autoreload
%autoreload

# ignore warnings for now ...
warnings.filterwarnings('ignore')

if Path('.').absolute().parents[1].name == 'ml_drought':
    os.chdir(Path('.').absolute().parents[1])

# Get the data directory
data_dir = Path('data/')
data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data/')
plot_dir = Path('/Users/tommylees/Downloads/')

assert data_dir.exists()
assert plot_dir.exists()


# ------ FUNCTIONS ------
def read_experiments_pred_data(experiments: List[str] = 'one_month_forecast') -> Dict[str, Dict[str, xr.DataArray]]:
    out_dict = {}

    for experiment in experiments:
        lr_pred_ = read_pred_data(
            'linear_regression', data_dir, experiment=experiment)[-1].where(~mask)
        ln_pred_ = read_pred_data(
            'linear_network', data_dir, experiment=experiment)[-1].where(~mask)
        rnn_pred_ = read_pred_data(
            'rnn', data_dir, experiment=experiment)[-1].where(~mask)
        ealstm_pred_ = read_pred_data(
            'ealstm', data_dir, experiment=experiment)[-1].where(~mask)
        experiment_results = {
            'lr_pred': lr_pred_,
            'ln_pred': ln_pred_,
            'rnn_pred': rnn_pred_,
            'ealstm_pred': ealstm_pred_,
        }
        out_dict[experiment] = experiment_results

    return out_dict


def load_experiment_annual_scores(experiments: List[str] = ['one_month_forecast'],
                                  true_data_experiment: str = 'one_month_forecast') -> Dict[str, pd.DataFrame]:
    out_dict = {}
    for experiment in experiments:
        if experiment == 'one_month_forecast':
            models = ['previous_month', 'rnn',
                      'linear_regression', 'linear_network', 'ealstm']
        else:
            models = ['rnn', 'linear_regression',
                      'linear_network', 'ealstm']
        monthly_scores = annual_scores(
            data_path=data_dir,
            models=models,
            metrics=['rmse', 'r2'],
            pred_years=[y for y in range(2011, 2019)],
            experiment=experiment,
            true_data_experiment=true_data_experiment,
            target_var='VCI',
            verbose=False,
            to_dataframe=True
        )
        out_dict[experiment] = monthly_scores

    return out_dict


# ------ SCRIPT ------

# read in the data
X_train, y_train = read_train_data(data_dir)
X_test, y_test = read_test_data(data_dir)

# create a complete dataset of all data
ds = xr.merge([y_train, y_test]).sortby('time').sortby('lat')
d_ = xr.merge([X_train, X_test]).sortby('time').sortby('lat')
ds = xr.merge([ds, d_])

mask = get_ds_mask(X_train.VCI)

# read in predictions
bline_pred = read_pred_data('previous_month', data_dir)[-1].where(~mask)
lr_pred = read_pred_data('linear_regression', data_dir)[-1].where(~mask)
ln_pred = read_pred_data('linear_network', data_dir)[-1].where(~mask)
rnn_pred = read_pred_data('rnn', data_dir)[-1].where(~mask)
ealstm_pred = read_pred_data('ealstm', data_dir)[-1].where(~mask)

# read in other experiment predictions
experiments = [
    'one_month_forecast_VCI_YESstatic',
    'one_month_forecast_VCI_NOstatic',
    'one_month_forecast_precip_YESstatic',
    'one_month_forecast_precip_NOstatic',
    'one_month_forecast_t2m_YESstatic',
    'one_month_forecast_t2m_NOstatic',
    'one_month_forecast_pev_YESstatic',
    'one_month_forecast_pev_NOstatic',
    'one_month_forecast_E_YESstatic',
    'one_month_forecast_E_NOstatic',
    'one_month_forecast'
]

pred_dict = read_experiments_pred_data(experiments)
score_dict = load_experiment_annual_scores(experiments)
