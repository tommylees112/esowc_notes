import pandas as pd
from pathlib import Path
import xarray as xr

nino34_link = "https://www.esrl.noaa.gov/psd/data/correlation/nina34.data"
name = "nino34"
# month names
# colnames = ["year", "Jan", "Feb", "Mar", "Apr", "May",
#             "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Download data and clean the table
df = pd.read_table(nino34_link, skiprows=0, nrows=73)
# spaces to columns
df = df.iloc[:, 0].str.split(expand=True)

# wide to long format
df = df.set_index(0).stack()
df.name = name
df = df.reset_index().rename(columns={0: "year", "level_1": "month"})

# create datetime index
df["time"] = df.apply(lambda x: pd.to_datetime(f"{x.year}-{x.month}"), axis=1)
df = df.set_index("time").drop(columns=["year", "month"])

# replace missing data
df = df.astype({name: float}).replace(-99.99, np.nan)

# resample to month end (same as other data)
df = df.resample("M").first()

# -----------------
# save to xarray / .nc
# -----------------
data_dir = Path("data")
vci = xr.open_dataset(data_dir / "interim/boku_ndvi_1000_preprocessed/data_kenya.nc")[
    "boku_VCI"
]

# for each MONTH TIMESTEP multiply by the nino value
nino_xr = xr.ones_like(vci)
nino_ts = df.loc[nino_xr.time.values]
nino_xr = nino_xr * pd.DataFrame.to_xarray(nino_ts)

if not (data_dir / "analysis/sst").exists():
    (data_dir / "analysis/sst").mkdir(parents=True, exist_ok=True)

# save to netcdf
nino_xr.to_netcdf(data_dir / f"analysis/sst/data_{name}.nc")
