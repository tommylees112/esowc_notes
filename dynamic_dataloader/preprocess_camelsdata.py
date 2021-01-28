import pandas as pd
import numpy as np
import torch

from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import os
import re
import xarray as xr
import pickle

if Path(".").absolute().parents[0].name == "runoff_uk_lstm":
    os.chdir(Path(".").absolute().parents[0])
# if Path('.').absolute().parents[0].name == 'ml_drought':
#     os.chdir(Path('.').absolute().parents[0])

# get the datasets
# data_dir = Path('data/CAMELS/CAMELS_GB_DATASET')
data_dir = Path("data/raw")
assert data_dir.exists()

print([d.name for d in data_dir.iterdir()])

attrs_dir, shp_dir, ts_dir = [data_dir / d.name for d in data_dir.iterdir()]
# shp_dir, ts_dir, attrs_dir = [data_dir / d.name for d in data_dir.iterdir()]

attrs_csvs = [d for d in attrs_dir.iterdir() if d.name.endswith(".csv")]
shp_path = [d for d in shp_dir.iterdir() if d.name.endswith(".shp")]

# timeseries
ts_csvs = [d for d in ts_dir.iterdir()]
# all the gauges
gauge_ids = [d.name.split("ies_")[-1].split("_")[0] for d in ts_dir.iterdir()]

# load one dataset
df = pd.read_csv(ts_csvs[0])

df.head()
times = np.array(df.date)
dynamic_vars = [c for c in df.columns if c != "date"]

### DYNAMIC DATA
# load all dynamic data into memory
dfs = [pd.read_csv(d) for d in ts_csvs]
print("Done")

# create dictionary of dynamic data (as a numpy array / matrix)
out = {}

for variable in dynamic_vars:
    print(f"Starting work on {variable}")

    vals = np.array([df[variable].values for df in dfs]).T
    out[variable] = vals

    print(f"FINISHED {variable}")


dims = ["time", "station_id"]
coords = {"station_id": gauge_ids, "time": times}

dynamic_ds = xr.Dataset(
    {variable_name: (dims, out[variable_name]) for variable_name in out.keys()},
    coords=coords,
)
if "station_id" in list(dynamic_ds.dims):
    dynamic_ds["station_id"] = dynamic_ds["station_id"].astype(np.dtype("int64"))
    dynamic_ds = dynamic_ds.sortby("station_id")

dynamic_ds.to_netcdf("data/dynamic_ds.nc")

with open("data/dynamic_ds.pkl", "wb") as fp:
    pickle.dump(dynamic_ds, fp)

### STATIC DATA
names = [d.name.replace(".csv", "").replace("CAMELS_GB_", "") for d in attrs_csvs]
[d.name for d in attrs_csvs]

# load all static data into memory
static_dfs = [pd.read_csv(d) for d in attrs_csvs]
print("Done")

# dict(zip(names, [list(df.columns) for df in static_dfs]))
# join into one dataframe
static_df = pd.concat(static_dfs, axis=1)

static_vars = [c for c in static_df.columns if c != "gauge_id"]
dims = ["station_id"]
coords = {"station_id": static_df.gauge_id.iloc[:, 0].values}

static_ds = xr.Dataset(
    {
        variable_name: (dims, static_df[variable_name].values)
        for variable_name in static_vars
    },
    coords=coords,
)
if "station_id" in list(static_ds.dims):
    static_ds["station_id"] = static_ds["station_id"].astype(np.dtype("int64"))
    static_ds = static_ds.sortby("station_id")

static_ds.to_netcdf("data/static_ds.nc")

with open("data/static_ds.pkl", "wb") as fp:
    pickle.dump(static_ds, fp)

### GEOGRAPHIC DATA
