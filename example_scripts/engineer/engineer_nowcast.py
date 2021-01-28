"""
Functions:
---------
engineer.engineer
    test_year
    target_variable
    pred_months
    expected_length
    experiment
engineer._get_preprocessed_files
engineer._make_dataset
engineer._stratify_training_data
engineer._train_test_split
engineer.stratify_xy
engineer.get_datetime
engineer._save
"""

import xarray as xr
import numpy as np
from pathlib import Path
from src.preprocess.base import BasePreProcessor

from src.engineer import Engineer

data_path = Path("/Volumes/Lees_Extend/data/ecmwf_sowc/data")
engineer = Engineer(data_path)
# engineer.engineer(test_year=1994, target_variable='VHI')

# wrong shapes!
datasets = engineer._get_preprocessed_files()
ds_list = [xr.open_dataset(ds) for ds in datasets]
dims_list = [[dim for dim in ds.dims] for ds in ds_list]
variable_list = [
    [var for var in ds.variables if var not in dims_list[i]][0]
    for i, ds in enumerate(ds_list)
]
da_list = [ds[variable_list[i]] for i, ds in enumerate(ds_list)]

pp = BasePreProcessor(data_path)
c_ds = ds_list[0]
e_ds = ds_list[1]
v_ds = ds_list[2]

v_ds = pp.resample_time(v_ds)

c_ds = pp.regrid(c_ds, v_ds)
c_ds = pp.resample_time(c_ds)


v_ds.to_netcdf(vhi_path.home() / vhi_path.parent / "vhi_kenya_regrid.nc")
v_ds.to_netcdf(chirps_path.home() / chirps_path.parent / "chirps_kenya_regrid.nc")

# engineer process
engineer._get_preprocessed_files
engineer._make_dataset
engineer.stratify_xy
engineer.stratify_xy
engineer._train_test_split
engineer.stratify_xy
engineer._stratify_training_data
engineer._save
