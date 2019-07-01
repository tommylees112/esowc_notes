# Describe the bug

I am trying to apply the SPI functions from within `python` rather than calling `process_climate_indices` from the command line. The reason being I am trying to integrate the SPI calculation code into a project looking at drought monitoring in East Africa and absolutely love your package!

# To Reproduce
```python
import xarray as xr
import pandas as pd
import numpy as np

time = pd.date_range(start='1981-01-31', end='2019-04-30', freq='M')
lat = np.linspace(-5.175003, 5.9749985, 224)
lon = np.linspace(33.524994, 42.274994, 176)
shape = (len(time), len(lat), len(lon))
precip = abs(np.random.normal(0, 1, size=shape))

dims = ['time', 'lat', 'lon']
coords = {'lat': lat,
          'lon': lon,
          'time': time}
p = xr.Dataset({'precip': (dims, precip)}, coords=coords)
p_ = p.sel(time=slice('2010', '2015'))

da_precip = p_.precip

Out[]:
<xarray.DataArray 'precip' (time: 72, lat: 224, lon: 176)>
array([[[0.353496, 1.432672, ..., 0.226953, 0.478602],
        [0.401273, 0.345513, ..., 0.164059, 0.216615],
        ...,
        [2.173777, 0.604994, ..., 0.126291, 0.725849],
        [0.180324, 0.760541, ..., 2.637146, 0.171422]],

       [[2.496804, 0.357846, ..., 0.750378, 0.075017],
        [1.714251, 0.49786 , ..., 1.034721, 0.594529],
        ...,
        [0.46032 , 0.089666, ..., 0.679843, 0.429389],
        [0.307617, 1.99291 , ..., 1.773255, 0.768199]],

       ...,

       [[0.379701, 0.451167, ..., 0.639582, 0.453396],
        [0.325368, 1.504672, ..., 0.135323, 1.102821],
        ...,
        [0.86135 , 1.520028, ..., 1.323338, 0.143189],
        [1.118784, 1.290067, ..., 1.235828, 1.140763]],

       [[0.542444, 0.635574, ..., 1.329817, 1.858417],
        [1.053195, 1.470252, ..., 0.298463, 0.642926],
        ...,
        [0.728585, 0.584189, ..., 0.059571, 0.286125],
        [1.009428, 0.02185 , ..., 0.628043, 0.446651]]])
Coordinates:
  * lat      (lat) float64 -5.175 -5.125 -5.075 -5.025 ... 5.875 5.925 5.975
  * lon      (lon) float64 33.52 33.57 33.62 33.67 ... 42.12 42.17 42.22 42.27
  * time     (time) datetime64[ns] 2010-01-31 2010-02-28 ... 2015-12-31
```

# run the spi code
```python
from climate_indices import indices

# groupby points
# https://stackoverflow.com/questions/53108606/xarray-apply-ufunc-with-groupby-unexpected-number-of-dimensions
da_precip_groupby = da_precip.stack(point=('lat', 'lon')).groupby('point')

# apply SPI to each `point`
scale = 3
distribution = 'gamma'
data_start_year = 2010
calibration_year_initial = 2010
calibration_year_final = 2015
periodicity = 'monthly'

da_spi = xr.apply_ufunc(indices.spi,
                        da_precip_groupby,
                        scale,
                        distribution,
                        data_start_year,
                        calibration_year_initial,
                        calibration_year_final,
                        periodicity)

# unstack the array back into original dimensions
da_spi = da_spi.unstack('point')

```

Gives me the following error message.
```
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
<ipython-input-105-185ebc98c80b> in <module>
     13                         calibration_year_initial,
     14                         calibration_year_final,
---> 15                         periodicity)

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/computation.py in apply_ufunc(func, input_core_dims, output_core_dims, exclude_dims, vectorize, join, dataset_join, dataset_fill_value, keep_attrs, kwargs, dask, output_dtypes, output_sizes, *args)
    953                                        keep_attrs=keep_attrs,
    954                                        dask=dask)
--> 955         return apply_groupby_func(this_apply, *args)
    956     elif any(is_dict_like(a) for a in args):
    957         return apply_dataset_vfunc(variables_vfunc, *args,

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/computation.py in apply_groupby_func(func, *args)
    434
    435     applied = (func(*zipped_args) for zipped_args in zip(*iterators))
--> 436     applied_example, applied = peek_at(applied)
    437     combine = first_groupby._combine
    438     if isinstance(applied_example, tuple):

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/utils.py in peek_at(iterable)
    137     """
    138     gen = iter(iterable)
--> 139     peek = next(gen)
    140     return peek, itertools.chain([peek], gen)
    141

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/computation.py in <genexpr>(.0)
    433         iterators.append(iterator)
    434
--> 435     applied = (func(*zipped_args) for zipped_args in zip(*iterators))
    436     applied_example, applied = peek_at(applied)
    437     combine = first_groupby._combine

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/computation.py in apply_ufunc(func, input_core_dims, output_core_dims, exclude_dims, vectorize, join, dataset_join, dataset_fill_value, keep_attrs, kwargs, dask, output_dtypes, output_sizes, *args)
    967                                      join=join,
    968                                      exclude_dims=exclude_dims,
--> 969                                      keep_attrs=keep_attrs)
    970     elif any(isinstance(a, Variable) for a in args):
    971         return variables_vfunc(*args)

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/computation.py in apply_dataarray_vfunc(func, signature, join, exclude_dims, keep_attrs, *args)
    216
    217     data_vars = [getattr(a, 'variable', a) for a in args]
--> 218     result_var = func(*data_vars)
    219
    220     if signature.num_outputs > 1:

~/miniconda3/envs/crop/lib/python3.7/site-packages/xarray/core/computation.py in apply_variable_ufunc(func, signature, exclude_dims, dask, output_dtypes, output_sizes, keep_attrs, *args)
    563             raise ValueError('unknown setting for dask array handling in '
    564                              'apply_ufunc: {}'.format(dask))
--> 565     result_data = func(*input_data)
    566
    567     if signature.num_outputs == 1:

ValueError: Invalid periodicity argument: monthly
```

# Expected behavior
Expect to produce a gridded SPI product for each pixel in the `xr.Dataset` object.

From my understanding I have the arguments to `periodicity` correct? They should be either `['daily', 'monthly']`

From the docstring:
```
:param periodicity: the periodicity of the time series represented by the input data, valid/supported values are
                    'monthly' and 'daily'
                    'monthly' indicates an array of monthly values, assumed to span full years, i.e. the first
                    value corresponds to January of the initial year and any missing final months of the final
                    year filled with NaN values, with size == # of years * 12
                    'daily' indicates an array of full years of daily values with 366 days per year, as if each
                    year were a leap year and any missing final months of the final year filled with NaN values,
                    with array size == (# years * 366)
```

# Desktop (please complete the following information):

OS: Ubuntu
Version: Ubuntu 16.04.5 LTS
