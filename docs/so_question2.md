# Efficiently apply a function over the month of interest xarray

```python
import pandas as pd
import numpy as np
import xarray as xr

time = pd.date_range('2010-01-01','2018-12-31',freq='M')
lat = np.linspace(-5.175003, -4.7250023, 10)
lon = np.linspace(33.524994, 33.97499, 10)
precip = np.random.normal(0, 1, size=(len(time), len(lat), len(lon)))

ds = xr.Dataset(
    {'precip': (['time', 'lat', 'lon'], precip)},
    coords={
        'lon': lon,
        'lat': lat,
        'time': time,
    }
)

Out[]:
<xarray.Dataset>
Dimensions:  (lat: 10, lon: 10, time: 108)
Coordinates:
  * lon      (lon) float64 33.52 33.57 33.62 33.67 ... 33.82 33.87 33.92 33.97
  * lat      (lat) float64 -5.175 -5.125 -5.075 -5.025 ... -4.825 -4.775 -4.725
  * time     (time) datetime64[ns] 2010-01-31 2010-02-28 ... 2018-12-31
Data variables:
    precip   (time, lat, lon) float64 -0.7862 -0.28 1.236 ... 0.6622 -0.7682
```

# My current approach
I currently apply a function by:
- looping through all of the months
- selecting all timesteps in the original dataset with that month
- apply a function to those months (here the normalised rank)
- re-combine the list of monthly `DataArray`s into a `Dataset` with all timesteps

The function might be a difference from climatology, but here it is the normalised rank.
- get the rank of the variable value compared to all other values for that `month` in the dataset
- set it on a range from `0-100`
```python
variable = 'precip'
rank_norm_list = []

# loop through all the months
for mth in range(1, 13):
    # select that month
    ds_mth = (
        ds
        .where(ds['time.month'] == mth)
        .dropna(dim='time', how='all')
    )
    # apply the function to that month (here a normalised rank (0-100))
    rank_norm_mth = (
        (ds_mth.rank(dim='time') - 1) / (ds_mth.time.size - 1.0) * 100.0
    )
    rank_norm_mth = rank_norm_mth.rename({variable: 'rank_norm'})
    rank_norm_list.append(rank_norm_mth)

# after the loop re-combine the DataArrays
rank_norm = xr.merge(rank_norm_list).sortby('time')

Out[]:

```

Is there a clever/more efficient way that doesn't involve looping and selecting?
