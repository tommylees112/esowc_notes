<!-- How to select using `.where()` on a timestamp `coordinate` -->

I am working with a multi-dimensional object (more than just time,lat,lon which is what i am used to).

It is a forecast produced from a weather model and so has the complexity of having an `initialisation_date` as well as a `forecast_horizon`.

I have a `valid_time` `coordinate` which defines the true time that the forecast refers to.

I want to be able to select these `valid_time` objects from my `xr.Dataset` object but I don't know how to select from a `coordinate` that is not also a `dimension`.

#### MCVE Code Sample

```python
import pandas as pd
import numpy as np
import xarray as xr

initialisation_date = pd.date_range('2018-01-01','2018-12-31',freq='M')
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

Out[]:
<xarray.Dataset>
Dimensions:              (forecast_horizon: 24, initialisation_date: 12, lat: 36, lon: 45, number: 51, step: 24)
Coordinates:
  * lon                  (lon) float64 33.5 33.7 33.9 34.1 ... 41.85 42.05 42.25
  * lat                  (lat) float64 -5.175 -5.176 -5.177 ... -5.201 -5.202
  * initialisation_date  (initialisation_date) datetime64[ns] 2018-01-31 ... 2018-12-31
  * number               (number) int64 0 1 2 3 4 5 6 7 ... 44 45 46 47 48 49 50
  * forecast_horizon     (forecast_horizon) timedelta64[ns] 28 days ... 215 days
    valid_time           (initialisation_date, step) datetime64[ns] 2018-02-28 ... 2019-08-03
Dimensions without coordinates: step
Data variables:
    precip               (number, initialisation_date, forecast_horizon, lat, lon) float64 1.373 ... 1.138
```

I try to select all the March, April, May months from the `valid_time` coordinate using `.sel[]`

```python
# select March April May from the valid_time
ds.sel(valid_time=np.isin(ds['valid_time.month'], [3,4,5]))
```

Error Message:
```
<ipython-input-151-132375b92854> in <module>
----> 1 ds.sel(valid_time=np.isin(ds['valid_time.month'], [3,4,5]))

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/dataset.py in sel(self, indexers, method, tolerance, drop, **indexers_kwargs)
   1729         indexers = either_dict_or_kwargs(indexers, indexers_kwargs, 'sel')
   1730         pos_indexers, new_indexes = remap_label_indexers(
-> 1731             self, indexers=indexers, method=method, tolerance=tolerance)
   1732         result = self.isel(indexers=pos_indexers, drop=drop)
   1733         return result._overwrite_indexes(new_indexes)

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/coordinates.py in remap_label_indexers(obj, indexers, method, tolerance, **indexers_kwargs)
    315
    316     pos_indexers, new_indexes = indexing.remap_label_indexers(
--> 317         obj, v_indexers, method=method, tolerance=tolerance
    318     )
    319     # attach indexer's coordinate to pos_indexers

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/indexing.py in remap_label_indexers(data_obj, indexers, method, tolerance)
    237     new_indexes = {}
    238
--> 239     dim_indexers = get_dim_indexers(data_obj, indexers)
    240     for dim, label in dim_indexers.items():
    241         try:

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/indexing.py in get_dim_indexers(data_obj, indexers)
    205     if invalid:
    206         raise ValueError("dimensions or multi-index levels %r do not exist"
--> 207                          % invalid)
    208
    209     level_indexers = defaultdict(dict)

ValueError: dimensions or multi-index levels ['valid_time'] do not exist
```

I have also tried creating a new variable of the month object from `valid_time` and copying it to the same shape as the `precip` variable
```python
# create months array of shape (51, 12, 24, 36, 45)
months = ds['valid_time.month'].values

m = np.repeat(months[np.newaxis, :, :], 51, axis=0)
m = np.repeat(m[:, :, :, np.newaxis], 36, axis=3)
m = np.repeat(m[:, :, :, :, np.newaxis], 45, axis=4)
assert (m[0, :, :, 0, 0] == m[50, :, :, 4, 2]).all(), f"The matrices have not been copied to the correct dimensions"

ds['month'] = (['number', 'initialisation_date', 'forecast_horizon', 'lat', 'lon'], m)
ds.where(np.isin(ds['month'], [3,4,5])).dropna(how='all', dim='forecast_horizon')
```

#### Problem Description
I want to be able to select all of the forecasts that correspond to the `valid_time` I select.

I think that an issue might be that the result from that query will be an irregular grid, because we will have different `initialisation_date` and `forecast_horizon` combinations that match the query. Is that the case

I want to select from a `coordinate` object that isn't a dimension. How can I go about doing this?

#### Expected Output
For example. I want to return the lat-lon arrays for the `valid_time` = `2018-04-01`.

The returning combinations should be 51 realisations of a (36 x 45) (`lat, lon`) grid of forecast values.

So 3 possible forecasts matching this criteria:
- `initialisation_date`=`2018-01-01` at a `forecast_horizon`=`3 months`
- `initialisation_date`=`2018-02-01` at a `forecast_horizon`=`2 months`
- `initialisation_date`=`2018-03-01` at a `forecast_horizon`=`1 months`


#### Output of ``xr.show_versions()``

<details>
# Paste the output here xr.show_versions() here
INSTALLED VERSIONS
------------------
commit: None
python: 3.7.0 | packaged by conda-forge | (default, Nov 12 2018, 12:34:36)
[Clang 4.0.1 (tags/RELEASE_401/final)]
python-bits: 64
OS: Darwin
OS-release: 18.2.0
machine: x86_64
processor: i386
byteorder: little
LC_ALL: en_US.UTF-8
LANG: en_US.UTF-8
LOCALE: en_US.UTF-8
libhdf5: 1.10.4
libnetcdf: 4.6.2

xarray: 0.12.1
pandas: 0.24.2
numpy: 1.16.4
scipy: 1.3.0
netCDF4: 1.5.1.2
pydap: None
h5netcdf: None
h5py: 2.9.0
Nio: None
zarr: None
cftime: 1.0.3.4
nc_time_axis: None
PseudonetCDF: None
rasterio: 1.0.17
cfgrib: 0.9.7
iris: None
bottleneck: 1.2.1
dask: 1.2.2
distributed: 1.28.1
matplotlib: 3.1.0
cartopy: 0.17.0
seaborn: 0.9.0
setuptools: 41.0.1
pip: 19.1
conda: None
pytest: 4.5.0
IPython: 7.1.1
sphinx: 2.0.1
</details>
