import xarray as xr
import pandas as pd
import numpy as np


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


def _make_dataset(
    size,
    variable_name="VHI",
    lonmin=-180.0,
    lonmax=180.0,
    latmin=-55.152,
    latmax=75.024,
    add_times=True,
    const=False,
    start_date="1999-01-01",
    end_date="2001-12-31",
):

    lat_len, lon_len = size
    # create the vector
    longitudes = np.linspace(lonmin, lonmax, lon_len)
    latitudes = np.linspace(latmin, latmax, lat_len)

    dims = ["lat", "lon"]
    coords = {"lat": latitudes, "lon": longitudes}

    if add_times:
        times = pd.date_range(start_date, end_date, name="time", freq="M")
        size = (len(times), size[0], size[1])
        dims.insert(0, "time")
        coords["time"] = times
    var = np.random.randint(100, size=size)
    if const:
        var *= 0
        var += 1

    ds = xr.Dataset({variable_name: (dims, var)}, coords=coords)

    return ds, (lonmin, lonmax), (latmin, latmax)
