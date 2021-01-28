from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import cfgrib


def make_dummy_seas5_data(date_str: str) -> xr.Dataset:
    initialisation_date = pd.date_range(start=date_str, periods=1, freq="M")
    number = [i for i in range(0, 26)]  # corresponds to ensemble number (51)
    lat = np.linspace(-5.175003, -5.202, 36)
    lon = np.linspace(33.5, 42.25, 45)
    forecast_horizon = np.array(
        [
            2419200000000000,
            2592000000000000,
            2678400000000000,
            5097600000000000,
            5270400000000000,
            5356800000000000,
            7689600000000000,
            7776000000000000,
            7862400000000000,
            7948800000000000,
            10368000000000000,
            10454400000000000,
            10540800000000000,
            10627200000000000,
            12960000000000000,
            13046400000000000,
            13219200000000000,
            15638400000000000,
            15724800000000000,
            15811200000000000,
            15897600000000000,
            18316800000000000,
            18489600000000000,
            18576000000000000,
        ],
        dtype="timedelta64[ns]",
    )
    valid_time = initialisation_date[:, np.newaxis] + forecast_horizon
    precip = np.ones(
        shape=(
            len(number),
            len(initialisation_date),
            len(forecast_horizon),
            len(lat),
            len(lon),
        )
    )

    ds = xr.Dataset(
        {
            "precip": (
                ["number", "initialisation_date", "forecast_horizon", "lat", "lon"],
                precip,
            )
        },
        coords={
            "lon": lon,
            "lat": lat,
            "initialisation_date": initialisation_date,
            "number": number,
            "forecast_horizon": forecast_horizon,
            "valid_time": (["initialisation_date", "step"], valid_time),
        },
    )
    return ds


def save_dummy_seas5(
    tmp_path,
    date_str,
    to_grib=False,
    dataset="seasonal-monthly-pressure-levels",
    variable="temperature",
) -> Path:
    """
    filename structure:
     data/raw/seasonal-monthly-pressure-levels/temperature/2017/01.grib
    """
    year = pd.to_datetime(date_str).year
    month = pd.to_datetime(date_str).month
    out_dir = tmp_path / "data" / "raw" / "s5" / dataset / variable / str(year)
    if not out_dir.exists():
        out_dir.mkdir(exist_ok=True, parents=True)

    ds = make_dummy_seas5_data(date_str)
    if to_grib:
        cfgrib.to_grib(
            ds,
            out_dir / f"{month:02}.grib",
            grib_keys={"edition": 2, "gridType": "regular_ll"},
        )
    else:
        ds.to_netcdf(out_dir / f"{month:02}.nc")

    return out_dir


data_path = save_dummy_seas5(
    tmp_path,
    "2018-01-01",
    to_grib=True,
    dataset="seasonal-monthly-pressure-levels",
    variable="temperature",
)

xr.open_dataset(out_dir / "01.grib", engine="cfgrib")
