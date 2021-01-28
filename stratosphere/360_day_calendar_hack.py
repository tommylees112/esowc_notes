import numpy as np
import xarray as xr
from pathlib import Path
import pandas as pd

data_dir = Path("/Users/tommylees/Downloads/")

# work with the data
nc_path = Path("/Users/tommylees/Downloads/vortex_strength.nc")
ds = xr.open_dataset(nc_path)
ds = ds.isel(t=slice(0, 61000))

df = ds.to_dataframe().drop(columns=["lat", "lon"])

years = [t.year for t in ds.t.values]
df["years"] = years
df = df[df.years != 2019]
years = df.years
df = df.dropna()

times = pd.date_range(start="1851-01-01", end="1851-12-31", freq="D")[:360]
days = [f"{t.month}-{t.day}" for t in times]
df["days"] = np.tile(days, 2019 - 1850)
df = df.reset_index()

out = []
for i in range(len(df)):
    out.append(f"{df.years.iloc[i]}-{df.days.iloc[i]}")
df["time"] = pd.to_datetime(out)
df = df.set_index("time")

df_ = df.drop(columns=["t", "days", "years"])
ds_clean = df_.to_xarray()
ds_clean.to_netcdf(data_dir / "strato_clean_ALL.nc")
# ds_clean['month'] = ds_clean['time.month']

vars_ = [v for v in ds.data_vars]

df_rolling = (
    ds_clean.sel(time=slice("2010", "2018")).rolling(time=90).mean().to_dataframe()
)
df_rolling[vars_].plot()


def is_winter(month):
    return [m in [1, 2, 3, 10, 11, 12] for m in month.values]


winter_data = ds_clean.sel(time=is_winter(ds_clean["time.month"]))
winter_data.sel(time=slice("2010", "2018")).u.plot()

# -------------------
#
# -------------------
nc_path2 = Path("/Users/tommylees/Downloads/strat_data.nc")
d = xr.open_dataset(nc_path2)
