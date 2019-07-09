# test_zsi_local.py
from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

%load_ext autoreload
%autoreload 2


data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')

data_path = data_dir / "interim" / "chirps_preprocessed" / "chirps_kenya.nc"
data_path = data_dir / "interim" / "chirps_preprocessed" / "chirps_kenya_.nc"

# -------------------------------------------------------------
# read data
# -------------------------------------------------------------
c = xr.open_dataset(data_path)


from ..utils import _make_dataset

data_dir = tmp_dir / "data" / "raw"
if not data_dir.exists():
    data_dir.mkdir(exist_ok=True, parents=True)

data_path = data_dir / "tmp_file.nc"
ds = _make_dataset(size=(30, 30))
ds.to_netcdf(data_path)

# -------------------------------------------------------------
# fit ZSI
# -------------------------------------------------------------
from src.analysis.indices.z_score import ZScoreIndex

z = ZScoreIndex(data_path)

variable = 'precip'
z.fit(variable=variable)

# -------------------------------------------------------------
# fit PDI
# -------------------------------------------------------------
from src.analysis.indices.percent_normal_index import PercentNormalIndex

p = PercentNormalIndex(data_path)
variable = 'precip'
p.fit(variable=variable)

# -------------------------------------------------------------
# fit HDSI
# -------------------------------------------------------------
from src.analysis.indices.drought_severity_index import DroughtSeverityIndex

h = DroughtSeverityIndex(data_path)
variable = 'precip'
h.fit(variable=variable)

# -------------------------------------------------------------
# fit China Z index
# -------------------------------------------------------------
from src.analysis.indices.china_z_index import ChinaZIndex

c = ChinaZIndex(data_path)
variable = 'precip'
c.fit(variable=variable)

# -------------------------------------------------------------
# fit Decile Index
# -------------------------------------------------------------
from src.analysis.indices.decile_index import DecileIndex
d= DecileIndex(data_path)
variable = 'precip'
d.fit(variable=variable)

# -------------------------------------------------------------
# fit AnomalyIndex
# -------------------------------------------------------------
from src.analysis.indices.anomaly_index import AnomalyIndex

a= AnomalyIndex(data_path)
variable = 'precip'
a.fit(variable=variable)



#
