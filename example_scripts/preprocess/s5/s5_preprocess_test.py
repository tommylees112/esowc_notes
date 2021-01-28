"""
https://github.com/pydata/xarray/issues/3053

- Same grid (spatial)
- same time step (temporal)
- Subset ROI
- assign latitude, longitude, time
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
from pathlib import Path

data_dir = Path("/Volumes/Lees_Extend/data/ecmwf_sowc/data")
data_dir = Path("data")

ds = xr.open_dataset(data_dir / "raw" / "seasonal" / "fcmean2018.grb", engine="cfgrib")

# rename the variables to more reasonable names
ds = ds.rename(
    {"p146.172": "surface_sensible_heat_flux", "p147.172": "surface_latent_heat_flux"}
)

# rename the coords to more reasonable coords
ds = ds.rename({"time": "initialisation_date", "step": "forecast_horizon"})

# total precip rate m/s
d = ds.tprate

fig, ax = plt.subplots()
d.mean(dim=["initialisation_date", "forecast_horizon", "number"]).plot(ax=ax)

# select all forecasts of a given time (but ignore the )
# stack the `initialisation_date` and `forecast_horizon`
stacked = ds.stack(time=("initialisation_date", "forecast_horizon"))
stacked["time"] = stacked.valid_time
stacked = stacked.drop("valid_time")

# or
stacked = ds.stack(time=("initialisation_date", "forecast_horizon"))
# stacked['time'] = stacked.valid_time

# select forecasts 28days ahead
stacked.sel(forecast_horizon=np.timedelta64(28, "D"))

# select 'valid_time'
stacked.swap_dims({"time": "valid_time"}).sel(valid_time="2018-04")

# ------------------------------------------------------------------------------
# Select forecasts for a given month
# ------------------------------------------------------------------------------

# MAM forecasts
mam = stacked.sel(time=np.isin(stacked["time.month"], [3, 4, 5]))
fig, ax = plt.subplots()
mam.tprate.mean(dim=["time", "number"]).plot(ax=ax)

# SON forecasts
son = stacked.sel(time=np.isin(stacked["time.month"], [9, 10, 11]))
fig, ax = plt.subplots()
son.tprate.mean(dim=["time", "number"]).plot(ax=ax)

#
#
ds.tprate.mean(dim=["number", "time"]).isel(step=0).plot()

timedeltas = [pd.to_timedelta(val) for val in d.step.values]

# select all forecasts of a given time
d.where(d.valid_time == "2018")
valid_time = np.array([pd.to_datetime(val) for val in d.valid_time.values])

# MAM forecasts
months = ds["valid_time.month"].values

m = np.repeat(months[np.newaxis, :, :], 51, axis=0)
m = np.repeat(m[:, :, :, np.newaxis], 45, axis=3)
m = np.repeat(m[:, :, :, :, np.newaxis], 36, axis=4)
assert (
    m[0, :, :, 0, 0] == m[50, :, :, 4, 2]
).all(), f"The matrices have not been copied to the correct dimensions"

ds["month"] = (["number", "time", "step", "latitude", "longitude"], m)
