from pathlib import Path
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from pandas.core.indexes.datetimes import DatetimeIndex
from typing import Tuple, Dict, List, Union, Optional

data_dir = Path("/Volumes/Lees_Extend/data/ecmwf_sowc/data/")
ealstm_dir = data_dir / "models/ealstm"
nc_files = [d for d in ealstm_dir.iterdir() if d.name[-2:] == "nc"]

test_dir = data_dir / "features/one_month_forecast/test"
true_nc_files = [f for f in test_dir.glob("*/*.nc") if f.name == "y.nc"]
true_data_paths = true_nc_files

# compare
compare_id = 0

pred_ds = xr.open_dataset(nc_files[compare_id])
true_ds = xr.open_dataset(true_nc_files[compare_id])

# spatial comparisons
fig, ax = plt.subplots()
pred_ds.preds.plot(ax=ax, vmin=0, vmax=100)
fig, ax = plt.subplots()
true_ds.VHI.plot(ax=ax, vmin=0, vmax=100)

#

# aggregate regions
region_data_path = Path("data/analysis/boundaries_preprocessed/province_l1_kenya.nc")
region_ds = xr.open_dataset(region_data_path)

fig, ax = plt.subplots()
region_ds.province_l1.plot(ax=ax)

valid_region_ids = [int(k.strip()) for k in region_ds.attrs["keys"].split(",")]

lookup = dict(
    zip(
        [int(k.strip()) for k in region_ds.attrs["keys"].split(",")],
        [v.strip() for v in region_ds.attrs["values"].split(",")],
    )
)


# ----------------------------------------------
# Compare the true / predicted values for region
# ----------------------------------------------
# init lists
region_name = []
predicted_mean_value = []
true_mean_value = []

# get DataVar names for Dataset -> DataArray
pred_var = [d for d in pred_ds.data_vars][0]
true_var = [d for d in true_ds.data_vars][0]

#
pred_da = pred_ds[pred_var]
true_da = true_ds[true_var]

for region_id in valid_region_ids:
    region_name.append(lookup[region_id])
    predicted_mean_value.append(
        pred_da.where(region_ds.province_l1 == region_id).mean().values
    )
    true_mean_value.append(
        true_da.where(region_ds.province_l1 == region_id).mean().values
    )
    assert true_da.time == pred_da.time
    datetimes.append(true_da.time)

df = pd.DataFrame(
    {
        "datetime": datetimes,
        "region_name": region_name,
        "predicted_mean_value": predicted_mean_value,
        "true_mean_value": true_mean_value,
    }
)


class TestRegionAnalysis:
    def test_init():
        return
