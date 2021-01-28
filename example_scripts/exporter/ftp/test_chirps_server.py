from pathlib import Path
import xarray as xr
from src.preprocess.preprocess_utils import select_bounding_box_xarray


project_dir = Path(".")
data_dir = Path("data")
chirps_dir = data_dir / "raw" / "chirps"

from src.preprocess.chirps import CHIRPSPreprocesser

c = CHIRPSPreprocesser()

# test that getting the filenames from the website
files = c.get_chirps_filepaths()
files.sort()
fs = [f.name for f in c.get_chirps_filepaths()]
netcdf_filepath = files[0]


# test that produce the right filename output
fnames = [c.create_filename(f, subset=True, subset_name="kenya") for f in fs]
fname = fnames[0]

# test the saving functionality works
subset_name = "kenya"
ds = xr.open_dataset(netcdf_filepath)
if subset_name == "kenya":
    kenya_region = c.get_kenya()
    kenya_ds = select_bounding_box_xarray(ds, kenya_region)

kenya_ds.to_netcdf(c.chirps_interim / fname)

# or
c.preprocess_CHIRPS_data(netcdf_filepath)


# check the preprocessing everything in parallel
c.preprocess()
