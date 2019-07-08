# test_s5_local.py
from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd

%load_ext autoreload
%autoreload 2

data_path = Path('data')
data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data/')
s5_dir =  Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data/raw/seasonal')

s5_fpaths = [f for f in s5_dir.iterdir() if f.suffix == '.grb']

from src.preprocess.seas5.s5 import S5Preprocessor
s = S5Preprocessor(data_dir, ouce_server=False)

subset_str = 'kenya'
regrid = xr.open_dataset(data_dir / 'interim' / 'chirps_preprocessed/chirps_kenya.nc')
resample_time = 'M'
upsampling = False
parallel = False
variable = None

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

filepath = s5_fpaths[0]
ds = s.read_grib_file(filepath)

coords = [c for c in ds.coords]
vars = [v for v in ds.variables if v not in coords]
variable = '-'.join(vars)

if 'latitude' in coords:
    ds = ds.rename({'latitude': 'lat'})
if 'longitude' in coords:
    ds = ds.rename({'longitude': 'lon'})

# 2. subset ROI
if subset_str is not None:
    ds = s.chop_roi(ds, subset_str, inverse_lat=True)

t = ds.t2m.to_dataset()
# 3. regrid
if regrid is not None:
    assert all(np.isin(['lat', 'lon'], [c for c in ds.coords])), f"\
    Expecting `lat` `lon` to be in ds. dims : {[c for c in ds.coords]}"
    t_kenya = s.regrid(t, regrid)



# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------




# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
