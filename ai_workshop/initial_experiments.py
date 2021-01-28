from pathlib import Path
import xarray as xr

data_dir = Path("data")
ndvi_dir = data_dir / "interim/OLD/ndvi_interim"

# ndvi preprocess to ERA5 grid
from src.preprocess import NDVIPreprocessor

n = NDVIPreprocessor()

regrid_path = (
    data_dir
    / "interim/reanalysis-era5-single-levels-monthly-means_preprocessed/data_kenya.nc"
)
regrid = n.load_reference_grid(regrid_path)

ds = xr.open_mfdataset((ndvi_dir / "*.nc").as_posix(), chunks={"time": 100})
ds = ds.sortby("time")

# ds = Out[31]
# ds = n.regrid(ds, regrid)

ds = n.resample_time(ds, resample_time="M")

# CHIRPS preprocess daily
import xarray as xr
from src.preprocess import CHIRPSPreprocesser

c = CHIRPSPreprocesser()

subset_str = "kenya"
resample_time = None
upsampling = False
c.merge_files(subset_str, resample_time, upsampling)

#
xr.open_dataset("data/interim/chirps_preprocessed/data_kenya.nc")
