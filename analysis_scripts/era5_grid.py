from pathlib import Path
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# analysis functions
from src.analysis import annual_scores
from src.analysis import plot_predictions
from src.analysis import read_pred_data, read_true_data

data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data/')
data_dir = Path('data/')

model_dir = data_dir / 'models' / 'one_month_forecast' / 'ealstm'
model_dir = data_dir / 'models' / 'one_month_forecast' / 'ealstm_ERA5_128'

test_data_dir = data_dir / 'features' / 'one_month_forecast/'

# open all predictions
pred_data = read_pred_data(model='ealstm_ERA5_128')[0]
test_data = read_true_data()

# plot all 12 months
import calendar

fig, axs = plt.subplots(3, 4, sharex=True, sharey=True)
for i in range(0, 12):
    ix = np.unravel_index(i, (3, 4))
    ax = axs[ix]
    data = test_data.isel(time=i).sortby('lat')
    data.plot(ax=ax, add_colorbar=False)
    ax.set_title(f'{calendar.month_abbr[i + 1]}')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.axis('off')
fig.suptitle('Observed VCI in 2018')

fig, axs = plt.subplots(3, 4, sharex=True, sharey=True)
for i in range(0, 12):
    ix = np.unravel_index(i, (3, 4))
    ax = axs[ix]
    data = pred_data.preds.isel(time=i).sortby('lat')
    data.plot(ax=ax, add_colorbar=False)
    ax.set_title(f'{calendar.month_abbr[i + 1]}')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.axis('off')
fig.suptitle('Predicted VCI in 2018')

fig, axs = plt.subplots(3, 4, sharex=True, sharey=True)
for i in range(0, 12):
    ix = np.unravel_index(i, (3, 4))
    ax = axs[ix]
    t_data = test_data.isel(time=i).sortby('lat')
    p_data = pred_data.preds.isel(time=i).sortby('lat')
    data = t_data - p_data
    data.plot(ax=ax, add_colorbar=False)
    ax.set_title(f'{calendar.month_abbr[i + 1]}')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.axis('off')
fig.suptitle('Predicted - Observed VCI in 2018')



# check the model performances over time
monthly_scores = annual_scores(
    data_path=data_dir,
    models=['ealstm', 'ealstm_ERA5_128', 'rnn', 'previous_month', ''],
    metrics=['rmse', 'r2'],
    verbose=False,
    to_dataframe=True,
    pred_year=2018
)

# plot the truth (in `features/../test`) against prediction (in `models/../..`)
plot_predictions(
    pred_month=4, model='ealstm',
    target_var='VCI', data_path=data_dir
)
