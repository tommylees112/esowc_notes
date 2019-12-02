import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

%load_ext autoreload
%autoreload 2

# data_dir = data_path = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
# sys.path.append('/Users/tommylees/github/ml_drought')

data_dir = Path('data')

# load model
from src.models import load_model

model_path = data_dir / 'models/one_month_forecast/ealstm/model.pt'
assert model_path.exists()

ealstm = load_model(model_path)

# load the dataloader
test_dl = next(iter(
    ealstm.get_dataloader(mode="test", to_tensor=True, shuffle_data=True)
))

# iterate over dataloader -> TestData
outputs = []

for key, val in test_dl.items():
    outputs.append(ealstm.get_morris_gradient(val.x))
