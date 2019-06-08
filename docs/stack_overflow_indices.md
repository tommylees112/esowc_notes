# assign values from `xr.groupby_bins`

I want to calculate the [Decile Index](https://github.com/royalosyin/Calculate-Precipitation-based-Agricultural-Drought-Indices-with-Python/blob/master/) - see the `ex1-Calculate Decile Index (DI) with Python.ipynb`.

The `pandas` implementation is simple enough but I need help with applying the bin labels to a new `variable` / `coordinate`.

```Python
import pandas as pd
import numpy as np
import xarray as xr

time = pd.date_range('2010-01-01','2011-12-31',freq='M')
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
```

```
Out[]:
<xarray.Dataset>
Dimensions:  (lat: 10, lon: 10, time: 24)
Coordinates:
  * lon      (lon) float64 33.52 33.57 33.62 33.67 ... 33.82 33.87 33.92 33.97
  * lat      (lat) float64 -5.175 -5.125 -5.075 -5.025 ... -4.825 -4.775 -4.725
  * time     (time) datetime64[ns] 2010-01-31 2010-02-28 ... 2011-12-31
Data variables:
    precip   (time, lat, lon) float64 0.1638 -1.031 0.2087 ... -0.1147 -0.6863
```


```python
# calculate a cumsum over some window size
rolling_window = 3
ds_window = (
    ds.rolling(time=rolling_window, center=True)
    .sum()
    .dropna(dim='time', how='all')

# construct a cumulative frequency distribution ranking the precip values
# per month
rank_norm_list = []
for mth in range(1, 13):
    ds_mth = (
        ds_window
        .where(ds_window['time.month'] == mth)
        .dropna(dim='time', how='all')
    )
    rank_norm_mth = (
        (ds_mth.rank(dim='time') - 1) / (ds_mth.time.size - 1.0) * 100.0
    )
    rank_norm_mth = rank_norm_mth.rename({variable: 'rank_norm'})
    rank_norm_list.append(rank_norm_mth)

rank_norm = xr.merge(rank_norm_list).sortby('time')
```

I want to create a variable which will create a new `variable` or `coordinate`
in `ds` that will have the the integers corresponding to the bins from the `bins = [20., 40., 60., 80., np.Inf]`.

i.e.:
```
<xarray.Dataset>
Dimensions:   (lat: 10, lon: 10, time: 24)
Coordinates:
  * time      (time) datetime64[ns] 2010-01-31 2010-02-28 ... 2011-12-31
  * lat       (lat) float32 -5.175003 -5.125 -5.075001 ... -4.7750015 -4.7250023
  * lon       (lon) float32 33.524994 33.574997 33.625 ... 33.925003 33.97499
Data variables:
    precip    (time, lat, lon) float32 4.6461554 4.790813 ... 7.3063064 7.535994
    rank_bin  (lat, lon, time) int64 1 3 3 0 1 4 2 3 0 1 ... 0 4 0 1 3 1 2 2 3 1
```

## the way that I tried

```python
# assign bins to variable xarray
bins = [20., 40., 60., 80., np.Inf]
decile_index_gpby = rank_norm.groupby_bins('rank_norm', bins=bins)
out = decile_index_gpby.assign()  # assign_coords()
```

The error message I get is as follows:
```
---------------------------------------------------------------------------
IndexError                                Traceback (most recent call last)
<ipython-input-166-8d48b9fc1d56> in <module>
      1 bins = [20., 40., 60., 80., np.Inf]
      2 decile_index_gpby = rank_norm.groupby_bins('rank_norm', bins=bins)
----> 3 out = decile_index_gpby.assign()  # assign_coords()

~/miniconda3/lib/python3.7/site-packages/xarray/core/groupby.py in assign(self, **kwargs)
    772         Dataset.assign
    773         """
--> 774         return self.apply(lambda ds: ds.assign(**kwargs))
    775
    776

~/miniconda3/lib/python3.7/site-packages/xarray/core/groupby.py in apply(self, func, args, **kwargs)
    684         kwargs.pop('shortcut', None)  # ignore shortcut if set (for now)
    685         applied = (func(ds, *args, **kwargs) for ds in self._iter_grouped())
--> 686         return self._combine(applied)
    687
    688     def _combine(self, applied):

~/miniconda3/lib/python3.7/site-packages/xarray/core/groupby.py in _combine(self, applied)
    691         coord, dim, positions = self._infer_concat_args(applied_example)
    692         combined = concat(applied, dim)
--> 693         combined = _maybe_reorder(combined, dim, positions)
    694         if coord is not None:
    695             combined[coord.name] = coord

~/miniconda3/lib/python3.7/site-packages/xarray/core/groupby.py in _maybe_reorder(xarray_obj, dim, positions)
    468
    469 def _maybe_reorder(xarray_obj, dim, positions):
--> 470     order = _inverse_permutation_indices(positions)
    471
    472     if order is None:

~/miniconda3/lib/python3.7/site-packages/xarray/core/groupby.py in _inverse_permutation_indices(positions)
    110         positions = [np.arange(sl.start, sl.stop, sl.step) for sl in positions]
    111
--> 112     indices = nputils.inverse_permutation(np.concatenate(positions))
    113     return indices
    114

~/miniconda3/lib/python3.7/site-packages/xarray/core/nputils.py in inverse_permutation(indices)
     58     # use intp instead of int64 because of windows :(
     59     inverse_permutation = np.empty(len(indices), dtype=np.intp)
---> 60     inverse_permutation[indices] = np.arange(len(indices), dtype=np.intp)
     61     return inverse_permutation
     62

IndexError: index 1304 is out of bounds for axis 0 with size 1000
```
