# ouce_s5_test.py
from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd

from src.preprocess.seas5.ouce_s5 import OuceS5Data
%load_ext autoreload
%autoreload 2

path = '/lustre/soge1/data/incoming/seas5/1.0x1.0/6-hourly/2m_temperature/'
# -----------------------------------------------------------------
# get ouce_data
# -----------------------------------------------------------------
o = OuceS5Data()
filepaths = o.get_ouce_filepaths('2m_temperature')
filepath = filepaths[0]

o1, o2, o3 = o.read_ouce_s5_data(filepaths[0]), o.read_ouce_s5_data(filepaths[1]), o.read_ouce_s5_data(filepaths[2]),

# -----------------------------------------------------------------
# preprocess s5 data
# -----------------------------------------------------------------
from src.preprocess.seas5.s5 import S5Preprocessor
data_path = Path('data')
s = S5Preprocessor(data_path, ouce_server=True, parallel=False)

subset_str = 'kenya'
regrid = xr.open_dataset(Path('data/interim/chirps_preprocessed/chirps_kenya.nc'))
resample_time = 'M'
upsampling = False
variable = None

paths = []
variables = []
for filepath in filepaths[:3]:
    path, variable = s._preprocess(
        filepath=filepath, regrid=regrid,
    )
    paths.append(path)
    variables.append(variable)

# to join each var individually
vars_ = np.unique(variables)

# to join ALL vars
var = '_'.join(vars_)

s.merge_and_resample(
    variable=var, resample_str=resample_time,
    upsampling=upsampling, subset_str=subset_str,
)

# -----------------------------------------------------------------
# test the preprocess function
# -----------------------------------------------------------------
from shutil import rmtree
rmtree(s.interim)

from src.preprocess.seas5.s5 import S5Preprocessor
data_path = Path('data')
s = S5Preprocessor(data_path, ouce_server=True, parallel=False)

variable = '2m_temperature'
s.preprocess(
    subset_str=subset_str, regrid=regrid, resample_time=resample_time,
    upsampling=upsampling, variable=variable
)



# -----------------------------------------------------------------
# test the parallel preprocess
# -----------------------------------------------------------------
from src.preprocess.seas5.s5 import S5Preprocessor
data_path = Path('data')
s = S5Preprocessor(data_path, ouce_server=True, parallel=True)
