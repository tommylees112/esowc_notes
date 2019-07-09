# test_zsi_local.py
from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd

%load_ext autoreload
%autoreload 2


data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')

data_path = data_dir / "interim" / "chirps_preprocessed" / "chirps_kenya.nc"
data_path = data_dir / "interim" / "chirps_preprocessed" / "chirps_kenya_.nc"

# -------------------------------------------------------------
# read data
# -------------------------------------------------------------
c = xr.open_dataset(data_path)

# convert c to mm/day
c['precip'] = c.precip / 5
c.attrs['units'] = 'mm/day'

# convert to monthly
c = c.sortby('time')
c = c.resample(time='M').mean()

c = c.sel(time=slice('2010', '2015'))

# -------------------------------------------------------------
# fit ZSI
# -------------------------------------------------------------
from src.analysis.indices.z_score import ZScoreIndex

z = ZScoreIndex(data_path)

in_variable = 'precip'
z.fit(variable=variable)







#
