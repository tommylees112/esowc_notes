from pathlib import Path
from xarray import xr

era_5_precip_path = Path(
    "data/interim/reanalysis-era5-land_preprocessed/reanalysis-era5-land_kenya.nc"
)
ds = xr.open_dataset(era_5_precip_path)


#
