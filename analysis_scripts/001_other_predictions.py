import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import seaborn as sns

%load_ext autoreload
%autoreload 2
%matplotlib

data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data/')

# READ in model (maybe want to do more predictions on historical data)
from src.models import load_model, Persistence

ealstm_path = data_dir / 'models/one_month_forecast/ealstm/model.pt'
assert ealstm_path.exists(), \
    'Expected the unzipped file to have the model.pt file saved'

persistence = Persistence(data_folder=data_dir)
ealstm = load_model(model_path=ealstm_path)

# TODO: need to predict from X variables in other files
ealstm.evaluate_train_timesteps(year=np.arange(1990, 2010), month=3)
