# test_get_current.py
from pathlib import Path
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tests.utils import _make_dataset
from src.models.data import DataLoader, _BaseIter, TrainData


def make_test_datasets(tmp_dir):
    x_pred, _, _ = _make_dataset(size=(5, 5))
    x_coeff, _, _ = _make_dataset(size=(5, 5), variable_name="precip")

    x = xr.merge([x_pred, x_coeff])
    y = x_pred.isel(time=[0])

    data_dir = tmp_path / experiment
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)

    # save netcdf
    x_file = data_dir / "x.nc"
    y_file = data_dir / "y.nc"
    if not x_file.exists():
        x.to_netcdf(x_file)
    if not y_file.exists():
        y.to_netcdf(y_file)

    # make normalising dictionary
    norm_dict = {}
    for var in x.data_vars:
        norm_dict[var] = {
            "mean": x[var].mean(dim=["lat", "lon"], skipna=True).values,
            "std": x[var].std(dim=["lat", "lon"], skipna=True).values,
        }

    return data_dir


tmp_dir = Path("~/Desktop")
data_dir = make_test_datasets(tmp_dir)


class MockLoader:
    def __init__(self):
        self.batch_file_size = None
        self.mode = None
        self.shuffle = None
        self.clear_nans = None
        self.data_files = []
        self.normalizing_dict = norm_dict if normalize else None
        self.to_tensor = None
        self.experiment = experiment


base_iterator = _BaseIter(MockLoader())

arrays = base_iterator.ds_folder_to_np(
    data_dir, return_latlons=True, to_tensor=to_tensor
)


#
