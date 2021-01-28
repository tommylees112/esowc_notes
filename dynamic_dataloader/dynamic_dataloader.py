from pandas.tseries.offsets import Day
import pandas as pd
import pickle
from collections import defaultdict
import numpy as np
import xarray as xr
from pathlib import Path
from datetime import datetime
from typing import DefaultDict, Dict, Tuple, Optional, Union, List, Any, cast

from src.models.data import DataLoader, ModelArrays, TrainData, _TrainIter, _TestIter
from src.utils import minus_timesteps


class DynamicDataLoader(DataLoader):
    """
    New arguments:
    ---------------
    self.dynamic_ds: xr.Dataset
        load the data once into memory and then sample from it using the Iterators
    self.train_dynamic: xr.Dataset
    self.static_ds: xr.Dataset
        load the data once into memory and then sample from it using the Iterators

    self.legit_target_times: List[np.dtype('datetime64[ns]')]
    self.valid_train_times: List[np.dtype('datetime64[ns]')]
    self.valid_test_times: List[np.dtype('datetime64[ns]')]
    """

    dynamic: bool = True

    def __init__(
        self,
        target_var: str,
        test_years: Union[List[str], str],
        seq_length: int = 365,  # changed this default arg
        forecast_horizon: int = 1,
        data_path: Path = Path("data"),
        batch_file_size: int = 1,
        mode: str = "train",
        shuffle_data: bool = True,
        clear_nans: bool = True,
        normalize: bool = True,
        predict_delta: bool = False,
        experiment: str = "one_timestep_forecast",  # changed this default arg
        mask: Optional[List[bool]] = None,
        pred_months: Optional[List[int]] = None,
        to_tensor: bool = False,
        surrounding_pixels: Optional[int] = None,
        dynamic_ignore_vars: Optional[List[str]] = None,
        static_ignore_vars: Optional[List[str]] = None,
        timestep_aggs: bool = False,  # changed this default arg
        static: Optional[str] = "features",
        device: str = "cpu",
        spatial_mask: Optional[xr.DataArray] = None,
        normalize_y: bool = False,
        reducing_dims: Optional[List[str]] = None,
        calculate_latlons: bool = False,  # changed this default arg
        use_prev_y_var: bool = False,
        resolution: str = "D",
    ) -> None:
        self.data_path = data_path
        self.forecast_horizon = forecast_horizon
        self.target_var = target_var

        self.dynamic_ignore_vars = dynamic_ignore_vars
        self.static_ignore_vars = static_ignore_vars
        # load engineered data into memory for sampling dynamically
        # TODO: split train/test sets HERE
        self.load_data(
            experiment=experiment,
            static=True if static is not None else False,
            test_years=test_years,
        )

        # init the super class
        super().__init__(
            data_path=data_path,
            batch_file_size=batch_file_size,
            mode=mode,
            shuffle_data=shuffle_data,
            clear_nans=clear_nans,
            normalize=normalize,
            predict_delta=predict_delta,
            experiment=experiment,
            mask=mask,
            seq_length=seq_length,
            pred_months=pred_months,
            to_tensor=to_tensor,
            surrounding_pixels=surrounding_pixels,
            ignore_vars=dynamic_ignore_vars,  # basically ignored
            timestep_aggs=timestep_aggs,
            static=static,
            device=device,
            spatial_mask=spatial_mask,
            normalize_y=normalize_y,
            reducing_dims=reducing_dims,
            calculate_latlons=calculate_latlons,
            use_prev_y_var=use_prev_y_var,
        )

        # get the legitimate target_timesteps
        assert self.seq_length is not None, "Must provide a sequence length. Try 365"
        self.resolution = resolution
        data_times = [pd.to_datetime(t) for t in self.dynamic_ds.time.values]

        self.legit_target_times = self.calculate_legitimate_target_times(
            seq_length=self.seq_length,
            data_times=data_times,
            resolution=self.resolution,
        )

    def __iter__(self):
        if self.mode == "train":
            return _TrainDynamicIter(self, mode="train")
        else:
            return _TestDynamicIter(self, mode="test")

    def __len__(self) -> int:
        return len(self.legit_target_times) // self.batch_file_size

    def get_train_test_times(
        self, test_years: Union[List[str], str]
    ) -> Tuple[List[datetime]]:
        """Get a list of the test timestamps, train_timestamps"""
        min_test_date, max_train_date, _ = self.get_max_train_date(
            self.dynamic_ds, test_year=test_years
        )

        # use pandas .loc functionality with timeseries to get train_test periods
        ds_times = pd.DataFrame(index=pd.DatetimeIndex(self.dynamic_ds.time.values))
        valid_train_times = ds_times.loc[:max_train_date].index.values
        valid_test_times = ds_times.loc[min_test_date:].index.values

        return valid_train_times, valid_test_times

    @staticmethod
    def get_max_train_date(ds, test_year: Union[str, List[str]]) -> Tuple[pd.Timestamp]:
        """"""
        # get the minimum test_year
        if isinstance(test_year, Iterable):
            test_year = min([int(y) for y in test_year])

        # because of time-series nature of data
        # ASSUMPTION: only train on timesteps before the minimum test-date
        ds = ds.sortby("time")
        min_test_date = pd.to_datetime(f"{test_year}-01-01")
        max_train_date = min_test_date - Day(1)
        min_ds_date = pd.to_datetime(ds.time.min().values)

        return min_test_date, max_train_date, min_ds_date

    def get_reducing_dims(self, reducing_dims: Optional[List[str]] = None) -> List[str]:
        return [c for c in self.dynamic_ds.coords if c != "time"]

    def load_data(
        self, experiment: str, static: bool, test_years: Union[List[str], str]
    ) -> None:
        """load static and dynamic data into memory for
        dynamic sampling!

        Get the train_ds vs. the whole dynamic_ds
        """
        data_folder = self.data_path / f"features/{experiment}"
        dynamic_path = data_folder / "data.nc"
        static_path = self.data_path / "features/static/data.nc"

        self.dynamic_ds: xr.Dataset = xr.open_dataset(dynamic_path)

        # split into TRAIN/TEST data
        self.valid_train_times, self.valid_test_times = self.get_train_test_times(
            test_years
        )
        self.train_dynamic = self.dynamic_ds.sel(time=self.valid_train_times)

        self.normalizing_dict: Dict = pickle.load(
            open(data_folder / "normalizing_dict.pkl", "rb")
        )

        # calculate the normalizing_array in the loader too
        # ignore_vars = only include the vars being used in X!
        data_vars: List[str] = [
            v for v in self.normalizing_dict.keys() if v not in self.dynamic_ignore_vars
        ]
        self.normalizing_array: Optional[
            Dict[str, np.ndarray]
        ] = self.calculate_normalizing_array(data_vars, static=False)

        if static:
            self.static_ds = xr.open_dataset(static_path)
            self.static_normalizing_dict: Dict = pickle.load(
                open(self.data_path / "features/static/normalizing_dict.pkl", "rb")
            )
            # calculate the normalizing_array in the loader too
            data_vars: List[str] = [
                v
                for v in self.static_normalizing_dict.keys()
                if v not in self.static_ignore_vars
            ]
            self.normalizing_array_static: Optional[
                Dict[str, np.ndarray]
            ] = self.calculate_normalizing_array(data_vars, static=True)
        else:
            assert False, "Should provide static data for this loader ..."
            self.static_ds = None
            self.static_normalizing_dict = None

    @staticmethod
    def calculate_legitimate_target_times(
        data_times: List[pd.Timestamp], seq_length: int, resolution: str = "D"
    ) -> List[pd.Timestamp]:
        """return a list of the target times that we have enough data for"""
        min_data_date = min(data_times)

        # if the minimum required data is greater than the minimum date
        # then it is a valid time
        legitimate_times = []
        for target_time in data_times:
            min_X_date = minus_timesteps(target_time, seq_length, resolution)
            if min_X_date > min_data_date:
                legitimate_times.append(target_time)

        return legitimate_times

    def calculate_normalizing_array(
        self, data_vars: List[str], static: bool
    ) -> Dict[str, np.ndarray]:
        """Use dictionary created by the engineers -> numpy arrays
        for normalisation of the numpy arrays for use
        at a later time (by the iterators)
        """
        # If we've made it here, normalizing_dict is definitely not None
        if static:
            self.static_normalizing_dict = cast(
                Dict[str, Dict[str, float]], self.static_normalizing_dict
            )
        else:
            self.normalizing_dict = cast(
                Dict[str, Dict[str, float]], self.normalizing_dict
            )

        mean, std = [], []
        normalizing_dict_keys = (
            self.static_normalizing_dict.keys()
            if static
            else self.normalizing_dict.keys()
        )
        for var in data_vars:
            for norm_var in normalizing_dict_keys:
                if var.endswith(norm_var):
                    mean_val = (
                        self.static_normalizing_dict[norm_var]["mean"]
                        if static
                        else self.normalizing_dict[norm_var]["mean"]
                    )
                    std_val = (
                        self.static_normalizing_dict[norm_var]["std"]
                        if static
                        else self.normalizing_dict[norm_var]["std"]
                    )
                    mean.append(mean_val)
                    std.append(std_val)
                    break

        mean_np, std_np = np.asarray(mean), np.asarray(std)

        normalizing_array = cast(
            Dict[str, np.ndarray], {"mean": mean_np, "std": std_np}
        )
        return normalizing_array
