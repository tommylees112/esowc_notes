import xarray as xr
import pickle
from pathlib import Path
import pandas as pd
import numpy as np

data_dir = Path("camels_gb_only_global_basin_subset_input_subset_1805_1040")

val_results = pickle.load(
    open(data_dir / "validation/model_epoch030/validation_results.p", 'rb')
)
train_data = pickle.load(
    open(data_dir / "train_data/train_data.p", 'rb')
)

# CREATE TRAINING dataset
basins = train_data['coords']['basin']['data']
time = train_data['coords']['date']['data']

coords = {'station_id': basins, 'time': time}
dims = ('station_id', 'time')

data = {
    variable: (dims, train_data['data_vars'][variable]['data'])
    for variable in [v for v in train_data['data_vars'].keys()]
}
train_ds = xr.Dataset(data, coords=coords)

# create VALIDATION dataset
[stn for stn in val_results.keys()]

station_ids = [stn for stn in val_results.keys()]

discharge_spec_obs_ALL = []
discharge_spec_sim_ALL = []

for stn in station_ids:
    discharge_spec_obs_ALL.append(
        val_results[stn]['xr']['discharge_spec_obs'].values.flatten()
    )
    discharge_spec_sim_ALL.append(
        val_results[stn]['xr']['discharge_spec_sim'].values.flatten()
    )

times = val_results[stn]['xr']['date'].values
obs = np.vstack(discharge_spec_obs_ALL)
sim = np.vstack(discharge_spec_sim_ALL)

assert obs.shape == sim.shape

coords = {"time": times, "station_id": station_ids}
data = {
    "obs": (["station_id", "time"], obs),
    "sim": (["station_id", "time"], sim),
}
valid_ds = xr.Dataset(data, coords=coords)


valid_ds.to_netcdf('valid_ds.nc')
train_ds.to_netcdf('train_ds.nc')


valid_ds = xr.open_dataset('valid_ds.nc')
valid_ds.to_dataframe()