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
from typing import List

from src.analysis import read_train_data, read_test_data, read_pred_data
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
