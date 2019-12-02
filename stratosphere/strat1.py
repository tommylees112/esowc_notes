import numpy as np
import xarray as xr
from pathlib import Path
import pandas as pd

data_dir = Path('/Users/tommylees/Downloads/')

# work with the data
nc_path = Path('/Users/tommylees/Downloads/vortex_strength.nc')
ds = xr.open_dataset(nc_path)
ds = ds.isel(t=slice(0, 61000))

df = ds.to_dataframe().drop(columns=['lat', 'lon', 'p'])
df['years'] = years
df = df[df.years != '2019']
years = df.years
df = df.dropna()

times = pd.date_range(start='1851-01-01', end='1851-12-31', freq='D')[:360]
days = [f'{t.month}-{t.day}' for t in times]
df['days'] = np.tile(days, 2019-1850)
df = df.reset_index()

out = []
for i in range(len(df)):
    out.append(f"{df.years.iloc[i]}-{df.days.iloc[i]}")
df['datetime'] = pd.to_datetime(out)
df = df.set_index('datetime')

df_ = df.drop(columns=['t', 'days', 'years'])
df_.to_xarray().to_netcdf(data_dir / 'strato_clean.nc')


nc_path2 = Path('/Users/tommylees/Downloads/strat_data.nc')
d = xr.open_dataset(nc_path2)

# -------------------
#
# -------------------
# df.transform(lambda row: f"{row.years}-{row.days}", axis=1)

times = ds.t.values
years = [f"{t.year}" for t in times]
mintime = times[0].strftime()
maxtime = times[-1].strftime()
