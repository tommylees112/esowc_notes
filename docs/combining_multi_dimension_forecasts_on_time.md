

```python
import pandas as pd
import numpy as np
import xarray as xr

def make_fcast_dataset(date_str):
    initialisation_date = pd.date_range(start=date_str, periods=1, freq='M')
    number = [i for i in range(0, 51)] # corresponds to model number (ensemble of model runs)
    lat = np.linspace(-5.175003, -5.202, 36)
    lon = np.linspace(33.5, 42.25, 45)
    forecast_horizon = np.array(
        [ 2419200000000000,  2592000000000000,  2678400000000000,
          5097600000000000,  5270400000000000,  5356800000000000,
          7689600000000000,  7776000000000000,  7862400000000000,
          7948800000000000, 10368000000000000, 10454400000000000,
          10540800000000000, 10627200000000000, 12960000000000000,
          13046400000000000, 13219200000000000, 15638400000000000,
          15724800000000000, 15811200000000000, 15897600000000000,
          18316800000000000, 18489600000000000, 18576000000000000 ],
          dtype='timedelta64[ns]'
    )
    valid_time = initialisation_date[:, np.newaxis] + forecast_horizon
    precip = np.random.normal(
        0, 1, size=(len(number), len(initialisation_date), len(forecast_horizon), len(lat), len(lon))
    )

    ds = xr.Dataset(
        {'precip': (['number', 'initialisation_date', 'forecast_horizon', 'lat', 'lon'], precip)},
        coords={
            'lon': lon,
            'lat': lat,
            'initialisation_date': initialisation_date,
            'number': number,
            'forecast_horizon': forecast_horizon,
            'valid_time': (['initialisation_date', 'step'], valid_time)
        }
    )
    return ds

ds1 = make_fcast_dataset(date_str='2000-01-01')
ds2 = make_fcast_dataset(date_str='2000-02-01')

```

I want to combine the two initialisation dates (which have the same `forecast_horizon`) into one `xr.Dataset` with the `initialisation_date` coordinate increased in size from `1` to `2`.


```python
ds = xr.concat([ds1, ds2], dim='initialisation_date')
```







<!--  -->
