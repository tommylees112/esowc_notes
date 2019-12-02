import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

%load_ext autoreload
%autoreload 2
%matplotlib

data_dir = data_path = Path('data')
data_dir = data_path = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
sys.path.append('/Users/tommylees/github/ml_drought')


# load model
from src.models import load_model

model_path = data_dir / 'models/one_month_forecast/ealstm/model.pt'
assert model_path.exists()

ealstm = load_model(model_path)

# load X / Y data
from src.analysis import read_train_data, read_test_data
X_train, y_train = read_train_data(data_dir)
X_test, y_test = read_test_data(data_dir)

