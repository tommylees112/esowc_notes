How do I calculate a `dayofyear` climatology and then subtract the value from the original data?

Let's make some data to play with
```python
import xarray as xr
import numpy as np
import pandas as pd

latitude = np.linspace(-5.175003, 5.9749985, 224)
longitude = np.linspace(33.524994, 42.274994, 176)
time = pd.date_range('2010-01-01','2015-03-01')
data = np.random.random(size=(len(time), len(latitude), len(longitude)))
d = xr.Dataset(
    {'precip': (['time','latitude','longitude'], data)},
    coords={
        'time': time,
        'latitude': latitude,
        'longitude': longitude,
    }
)

d

Out[]:
<xarray.Dataset>
Dimensions:    (latitude: 224, longitude: 176, time: 1886)
Coordinates:
  * time       (time) datetime64[ns] 2010-01-01 2010-01-02 ... 2015-03-01
  * latitude   (latitude) float64 -5.175 -5.125 -5.075 ... 5.875 5.925 5.975
  * longitude  (longitude) float64 33.52 33.57 33.62 33.67 ... 42.17 42.22 42.27
Data variables:
    precip     (time, latitude, longitude) float64 0.04193 0.3864 ... 0.9281
```

So I create the threshold and climatology values for each day. The threhsold is
one standard deviation below the mean.
```python
clim = d.groupby('time.dayofyear').mean(dim='time')
thresh = clim - d.groupby('time.dayofyear').std(dim='time')
```

I want to create a new `xr.Dataset` with the same dimensions as `d` but with
the `thresh` values copied for each day of year.

I have done it here by extracting the data as `numpy.ndarray`s and using the
`modulo` operator to index the threshold values from array `t`.

I then recreate the xarray object after the fact from the `new_t_vals`.
```python
d['dayofyear'] = d['time.dayofyear']

t = thresh.precip.values  # (365, 224, 176)
doy = thresh.dayofyear.values  # (365,)
d_doy = d.dayofyear.values  # (1886,)

new_t_vals = t[d_doy%365, :, :]  # (1886, 224, 176)

new_thresh = xr.Dataset(
    {'precip': (['time','latitude','longitude'], new_t_vals)},
    coords={
        'time': d.time,
        'latitude': latitude,
        'longitude': longitude,
    }
)

new_thresh

Out[]:
<xarray.Dataset>
Dimensions:    (latitude: 224, longitude: 176, time: 1886)
Coordinates:
  * time       (time) datetime64[ns] 2010-01-01 2010-01-02 ... 2015-03-01
  * latitude   (latitude) float64 -5.175 -5.125 -5.075 ... 5.875 5.925 5.975
  * longitude  (longitude) float64 33.52 33.57 33.62 33.67 ... 42.17 42.22 42.27
Data variables:
    precip     (time, latitude, longitude) float64 0.8928 0.5027 ... 0.5537
```

I want to calculate the difference of the data `d` from the threshold
value defined by `new_thresh`.
```python
d - new_thresh

Out[]:
<xarray.Dataset>
Dimensions:    (latitude: 224, longitude: 176, time: 1886)
Coordinates:
  * time       (time) datetime64[ns] 2010-01-01 2010-01-02 ... 2015-03-01
  * latitude   (latitude) float64 -5.175 -5.125 -5.075 ... 5.875 5.925 5.975
  * longitude  (longitude) float64 33.52 33.57 33.62 33.67 ... 42.17 42.22 42.27
Data variables:
    precip     (time, latitude, longitude) float64 -0.6518 -0.2445 ... -0.01457
```

Is there any way of doing this without resorting to numpy? Using only `xarray`.
The reason being I want to use `dask` because I will be doing this globally on
some large datasets.
