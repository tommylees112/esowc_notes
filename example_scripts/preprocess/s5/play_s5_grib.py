from pathlib import Path
import xarray as xr

data_dir = Path(
    "/Users/tommylees/Downloads/adaptor.mars.external-1559340756.1474853-30897-19-48cf2a73-12f1-4777-8ba0-84b1d5c68384.grib"
)

ds = xr.open_dataset(data_dir, engine="cfgrib")
