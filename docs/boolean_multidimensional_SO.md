
I need to assign the values of one `xr.DataArray` (`gt`) if a certain condition is met. And the values of another `xr.DataArray` (`lt`) if a different condition is met. I want it to scale (there might be more than 2 conditions that might not cover all possibilities).

Ideally i would also like to do it all in `xarray`.

I currently have a solution that writes out to `numpy` and uses the masked array functionality built there.

# Here is a minimal reproducible example

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

# DUMMY DataArray's for filling in gt / lt values
lt = xr.full_like(da, -100)
gt = xr.full_like(da, 100)

```

# what I want
I want a `DataArray` with the values from `lt` when `da.values` are LESS THAN 1 ('-100'), and the values from `gt` (`100`) when `da.values` are GREATER THAN 1.

```python
<xarray.Dataset>
Dimensions:  (lat: 10, lon: 10, time: 24)
Coordinates:
  * lon      (lon) float64 33.52 33.57 33.62 33.67 ... 33.82 33.87 33.92 33.97
  * lat      (lat) float64 -5.175 -5.125 -5.075 -5.025 ... -4.825 -4.775 -4.725
  * time     (time) datetime64[ns] 2010-01-31 2010-02-28 ... 2011-12-31
Data variables:
    out      (time, lat, lon) float64 -100.0 -100.0 -100.0 ... -100.0 -100.0
```


# What I have tried:

- using the `.where` syntax to select from another (same `size` `xr.Dataset`) object
- convert to `np.ma.array`
- recombine using `np.ma.array` syntax
- read back into a `xr.Dataset`
```python
da = ds.precip

# get the overall mask (e.g. land-sea mask)
overall_mask = da.isnull()


# create masked `xr.DataArray` with values from `lt` or `gt`
lt1 = da.where(~(da < 1), other=lt)
lt_mask = lt1.where(~(da < 1)).isnull()
lt1 = lt1.where(lt_mask).where(~overall_mask)

gt1 = da.where(~(da >= 1), other=gt)
gt_mask = gt1.where(~(da >= 1)).isnull()
gt1 = gt1.where(gt_mask).where(~overall_mask)

# convert to numpy masked array
gtm_np = gt_mask.values
gt1_np = gt1.values
gt1_np = np.ma.array(gt1_np, mask=(~gtm_np))

ltm_np = lt_mask.values
lt1_np = lt1.values
lt1_np = np.ma.array(lt1_np, mask=(~ltm_np))

# recombine masked arrays
out_array = (
    np.ma.array(
        gt1_np.filled(1) * lt1_np.filled(1),
        mask=(gt1_np.mask * lt1_np.mask)
    )
)

# assign back to xarray
new = xr.ones_like(da).to_dataset()
new['out'] = (['time','lat','lon'], out_array)
new = new.drop('precip')
new
```

I want a way to do this efficiently /natively in xarray if it's possible.
